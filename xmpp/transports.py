##   transports.py
##
##   Copyright (C) 2003-2004 Alexey "Snake" Nezhdanov
##
##   This program is free software; you can redistribute it and/or modify
##   it under the terms of the GNU General Public License as published by
##   the Free Software Foundation; either version 2, or (at your option)
##   any later version.
##
##   This program is distributed in the hope that it will be useful,
##   but WITHOUT ANY WARRANTY; without even the implied warranty of
##   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##   GNU General Public License for more details.

# $Id$

"""
This module contains the low-level implementations of xmpppy connect methods or
(in other words) transports for xmpp-stanzas.
Currently here is three transports:
direct TCP connect - TCPsocket class
proxied TCP connect - HTTPPROXYsocket class (CONNECT proxies)
TLS connection - TLS class. Can be used for SSL connections also.

Transports are stackable so you - f.e. TLS use HTPPROXYsocket or TCPsocket as more low-level transport.

Also exception 'error' is defined to allow capture of this module specific exceptions.
"""

import socket,ssl,select,base64,sys
from . import dispatcher
from .simplexml import ustr
from .client import PlugIn
from .protocol import *
try:
    from httplib import HTTPConnection, HTTPSConnection, _CS_IDLE, BadStatusLine
except ImportError:
    from http.client import HTTPConnection, HTTPSConnection, _CS_IDLE, BadStatusLine
from errno import ECONNREFUSED
import random
import gzip
from io import StringIO
try:
    from urllib2 import urlparse
    urlparse = urlparse.urlparse
except ImportError:
    from urllib import parse
    urlparse = parse.urlparse

if not hasattr(sys, 'exc_clear'):
    def exc_clear(): pass
    setattr(sys, 'exc_clear', exc_clear)


# determine which DNS resolution library is available
HAVE_DNSPYTHON = False
HAVE_PYDNS = False
try:
    import dns.resolver # http://dnspython.org/
    HAVE_DNSPYTHON = True
except ImportError:
    try:
        import DNS # http://pydns.sf.net/
        HAVE_PYDNS = True
    except ImportError:
        pass

DATA_RECEIVED='DATA RECEIVED'
DATA_SENT='DATA SENT'

class error:
    """An exception to be raised in case of low-level errors in methods of 'transports' module."""
    def __init__(self,comment):
        """Cache the descriptive string"""
        self._comment=comment

    def __str__(self):
        """Serialise exception into pre-cached descriptive string."""
        return self._comment

BUFLEN=1024
class TCPsocket(PlugIn):
    """ This class defines direct TCP connection method. """
    def __init__(self, server=None, use_srv=True):
        """ Cache connection point 'server'. 'server' is the tuple of (host, port)
            absolutely the same as standard tcp socket uses. However library will lookup for
            ('_xmpp-client._tcp.' + host) SRV record in DNS and connect to the found (if it is)
            server instead
        """
        PlugIn.__init__(self)
        self.DBG_LINE='socket'
        self._exported_methods=[self.send,self.disconnect]
        self._server, self.use_srv = server, use_srv

    def srv_lookup(self, server):
        " SRV resolver. Takes server=(host, port) as argument. Returns new (host, port) pair "
        if HAVE_DNSPYTHON or HAVE_PYDNS:
            host, port = server
            possible_queries = ['_xmpp-client._tcp.' + host]

            for query in possible_queries:
                try:
                    if HAVE_DNSPYTHON:
                        answers = [x for x in dns.resolver.query(query, 'SRV')]
                        # Sort by priority, according to RFC 2782.
                        answers.sort(key=lambda a: a.priority)
                        if answers:
                            host = str(answers[0].target)
                            port = int(answers[0].port)
                            break
                    elif HAVE_PYDNS:
                        # ensure we haven't cached an old configuration
                        DNS.DiscoverNameServers()
                        response = DNS.Request().req(query, qtype='SRV')
                        # Sort by priority, according to RFC 2782.
                        answers = sorted(response.answers, key=lambda a: a['data'][0])
                        if len(answers) > 0:
                            # ignore the priority and weight for now
                            _, _, port, host = answers[0]['data']
                            del _
                            port = int(port)
                            break
                except:
                    self.DEBUG('An error occurred while looking up %s' % query, 'warn')
            server = (host, port)
        else:
            self.DEBUG("Could not load one of the supported DNS libraries (dnspython or pydns). SRV records will not be queried and you may need to set custom hostname/port for some servers to be accessible.\n",'warn')
        # end of SRV resolver
        return server

    def plugin(self, owner):
        """ Fire up connection. Return non-empty string on success.
            Also registers self.disconnected method in the owner's dispatcher.
            Called internally. """
        if not self._server: self._server=(self._owner.Server,5222)
        if self.use_srv: server=self.srv_lookup(self._server)
        else: server=self._server
        if not self.connect(server): return
        self._owner.Connection=self
        self._owner.RegisterDisconnectHandler(self.disconnected)
        return 'ok'

    def getHost(self):
        """ Return the 'host' value that is connection is [will be] made to."""
        return self._server[0]
    def getPort(self):
        """ Return the 'port' value that is connection is [will be] made to."""
        return self._server[1]

    def connect(self,server=None):
        """ Try to connect to the given host/port. Does not lookup for SRV record.
            Returns non-empty string on success. """
        if not server: server=self._server
        try:
            for res in socket.getaddrinfo(server[0], int(server[1]), 0, socket.SOCK_STREAM):
                af, socktype, proto, canonname, sa = res
                try:
                    self._sock = socket.socket(af, socktype, proto)
                    self._sock.connect(sa)
                    self._send=self._sock.sendall
                    self._recv=self._sock.recv
                    self.DEBUG("Successfully connected to remote host %s"%repr(server),'start')
                    return 'ok'
                except socket.error as xxx_todo_changeme:
                    errno = xxx_todo_changeme.args[0]
                    strerror = xxx_todo_changeme.args[1]
                    if self._sock is not None: self._sock.close()
            self.DEBUG("Failed to connect to remote host %s: %s (%s)"%(repr(server), strerror, errno),'error')
        except socket.gaierror as xxx_todo_changeme1:
            errno = xxx_todo_changeme1.args[0]
            strerror = xxx_todo_changeme1.args[1]
            self.DEBUG("Failed to lookup remote host %s: %s (%s)"%(repr(server), strerror, errno),'error')

    def plugout(self):
        """ Disconnect from the remote server and unregister self.disconnected method from
            the owner's dispatcher. """
        self._sock.close()
        if 'Connection' in self._owner.__dict__:
            del self._owner.Connection
            self._owner.UnregisterDisconnectHandler(self.disconnected)

    def receive(self):
        """ Reads all pending incoming data.
            In case of disconnection calls owner's disconnected() method and then raises IOError exception."""
        try: received = self._recv(BUFLEN)
        except socket.error as e:
            self._seen_data=0
            if self.check_pending(e, 'receiving', 'asking for a retry'):
                return ''
            self.DEBUG('Socket error while receiving data','error')
            sys.exc_clear()
            self._owner.disconnected()
            raise IOError("Disconnected from server")
        except: received = ''

        while self.pending_data(0):
            try: add = self._recv(BUFLEN)
            except socket.error as e:
                self._seen_data=0
                if self.check_pending(e, 'receiving', 'ignoring'):
                    break
                self.DEBUG('Socket error while receiving data','error')
                sys.exc_clear()
                self._owner.disconnected()
                raise IOError("Disconnected from server")
            except: add=''
            received +=add
            if not add: break

        if len(received): # length of 0 means disconnect
            self._seen_data=1
            self.DEBUG(received,'got')
            if hasattr(self._owner, 'Dispatcher'):
                self._owner.Dispatcher.Event('', DATA_RECEIVED, received)
        else:
            self.DEBUG('Socket error while receiving data','error')
            self._owner.disconnected()
            raise IOError("Disconnected from server")
        return received

    def send(self,raw_data,retry_timeout=1):
        """ Writes raw outgoing data. Blocks until done.
            If supplied data is unicode string, encodes it to utf-8 before send."""
        #print('type:', type(raw_data))
        if type(raw_data)==type(''): raw_data = raw_data
        elif type(raw_data)!=type(''): raw_data = ustr(raw_data)
        if sys.version_info.major >= 3:
            raw_data = raw_data.encode('utf-8')
        try:
            sent = 0
            while not sent:
                try:
                    self._send(raw_data)
                    sent = 1
                except socket.error as e:
                    if self.check_pending(e, 'sending', 'waiting to retry'):
                        continue
                    raise
            # Avoid printing messages that are empty keepalive packets.
            if raw_data.strip():
                self.DEBUG(raw_data,'sent')
                if hasattr(self._owner, 'Dispatcher'): # HTTPPROXYsocket will send data before we have a Dispatcher
                    self._owner.Dispatcher.Event('', DATA_SENT, raw_data)
        except:
            self.DEBUG("Socket error while sending data",'error')
            self._owner.disconnected()

    def pending_data(self,timeout=0):
        """ Returns true if there is a data ready to be read. """
        return select.select([self._sock],[],[],timeout)[0]

    def check_pending(self, ex, direction, action):
        if hasattr(socket, 'sslerror'):
            if ex[0] == socket.SSL_ERROR_WANT_READ:
                sys.exc_clear()
                self.DEBUG("SSL_WANT_READ while {direction} data, {action}".format(**locals()), 'warn')
                return True
            if ex[0] == socket.SSL_ERROR_WANT_WRITE:
                sys.exc_clear()
                self.DEBUG("SSL_WANT_WRITE while {direction} data, {action}".format(**locals()), 'warn')
                return True
        else:
            if isinstance(ex, ssl.SSLWantReadError):
                sys.exc_clear()
                self.DEBUG("SSL_WANT_READ while {direction} data, {action}".format(**locals()), 'warn')
                return True
            if isinstance(ex, ssl.SSLWantWriteError):
                sys.exc_clear()
                self.DEBUG("SSL_WANT_WRITE while {direction} data, {action}".format(**locals()), 'warn')
                return True

    def disconnect(self):
        """ Closes the socket. """
        self.DEBUG("Closing socket",'stop')
        self._sock.close()

    def disconnected(self):
        """ Called when a Network Error or disconnection occurs.
            Designed to be overidden. """
        self.DEBUG("Socket operation failed",'error')

DBG_CONNECT_PROXY='CONNECTproxy'
class HTTPPROXYsocket(TCPsocket):
    """ HTTP (CONNECT) proxy connection class. Uses TCPsocket as the base class
        redefines only connect method. Allows to use HTTP proxies like squid with
        (optionally) simple authentication (using login and password). """
    def __init__(self,proxy,server,use_srv=True):
        """ Caches proxy and target addresses.
            'proxy' argument is a dictionary with mandatory keys 'host' and 'port' (proxy address)
            and optional keys 'user' and 'password' to use for authentication.
            'server' argument is a tuple of host and port - just like TCPsocket uses. """
        TCPsocket.__init__(self,server,use_srv)
        self.DBG_LINE=DBG_CONNECT_PROXY
        self._proxy=proxy

    def plugin(self, owner):
        """ Starts connection. Used interally. Returns non-empty string on success."""
        owner.debug_flags.append(DBG_CONNECT_PROXY)
        return TCPsocket.plugin(self,owner)

    def connect(self,server=None):
        """ Starts connection. Connects to proxy, supplies login and password to it
            (if were specified while creating instance). Instructs proxy to make
            connection to the target server. Returns non-empty sting on success. """
        if not TCPsocket.connect(self,(self._proxy['host'],self._proxy['port'])): return
        self.DEBUG("Proxy server contacted, performing authentification",'start')
        if not server: server=self._server
        connector = ['CONNECT %s:%s HTTP/1.0'%server,
            'Proxy-Connection: Keep-Alive',
            'Pragma: no-cache',
            'Host: %s:%s'%server,
            'User-Agent: HTTPPROXYsocket/v0.1']
        if 'user' in self._proxy and 'password' in self._proxy:
            credentials = '%s:%s'%(self._proxy['user'],self._proxy['password'])
            credentials = base64.encodestring(credentials).strip()
            connector.append('Proxy-Authorization: Basic '+credentials)
        connector.append('\r\n')
        self.send('\r\n'.join(connector))
        try: reply = self.receive().replace('\r','')
        except IOError:
            self.DEBUG('Proxy suddenly disconnected','error')
            self._owner.disconnected()
            return
        try: proto,code,desc=reply.split('\n')[0].split(' ',2)
        except: raise error('Invalid proxy reply')
        if code!='200':
            self.DEBUG('Invalid proxy reply: %s %s %s'%(proto,code,desc),'error')
            self._owner.disconnected()
            return
        while reply.find('\n\n') == -1:
            try: reply += self.receive().replace('\r','')
            except IOError:
                self.DEBUG('Proxy suddenly disconnected','error')
                self._owner.disconnected()
                return
        self.DEBUG("Authentification successfull. XMPP server contacted.",'ok')
        return 'ok'

    def DEBUG(self,text,severity):
        """Overwrites DEBUG tag to allow debug output be presented as "CONNECTproxy"."""
        return self._owner.DEBUG(DBG_CONNECT_PROXY,text,severity)

class TLS(PlugIn):
    """ TLS connection used to encrypts already estabilished tcp connection."""
    def PlugIn(self,owner,now=0):
        """ If the 'now' argument is true then starts using encryption immidiatedly.
            If 'now' in false then starts encryption as soon as TLS feature is
            declared by the server (if it were already declared - it is ok).
        """
        if 'TLS' in owner.__dict__: return  # Already enabled.
        PlugIn.PlugIn(self,owner)
        DBG_LINE='TLS'
        if now: return self._startSSL()
        if self._owner.Dispatcher.Stream.features:
            try: self.FeaturesHandler(self._owner.Dispatcher,self._owner.Dispatcher.Stream.features)
            except NodeProcessed: pass
        else: self._owner.RegisterHandlerOnce('features',self.FeaturesHandler,xmlns=NS_STREAMS)
        self.starttls=None

    def plugout(self,now=0):
        """ Unregisters TLS handler's from owner's dispatcher. Take note that encription
            can not be stopped once started. You can only break the connection and start over."""
        self._owner.UnregisterHandler('features',self.FeaturesHandler,xmlns=NS_STREAMS)
        self._owner.UnregisterHandler('proceed',self.StartTLSHandler,xmlns=NS_TLS)
        self._owner.UnregisterHandler('failure',self.StartTLSHandler,xmlns=NS_TLS)

    def FeaturesHandler(self, conn, feats):
        """ Used to analyse server <features/> tag for TLS support.
            If TLS is supported starts the encryption negotiation. Used internally"""
        if not feats.getTag('starttls',namespace=NS_TLS):
            self.DEBUG("TLS unsupported by remote server.",'warn')
            return
        self.DEBUG("TLS supported by remote server. Requesting TLS start.",'ok')
        self._owner.RegisterHandlerOnce('proceed',self.StartTLSHandler,xmlns=NS_TLS)
        self._owner.RegisterHandlerOnce('failure',self.StartTLSHandler,xmlns=NS_TLS)
        self._owner.Connection.send('<starttls xmlns="%s"/>'%NS_TLS)
        raise NodeProcessed

    def pending_data(self,timeout=0):
        """ Returns true if there possible is a data ready to be read. """
        return self._tcpsock._seen_data or select.select([self._tcpsock._sslObj],[],[],timeout)[0]

    def _startSSL(self):
        """ Immidiatedly switch socket to TLS mode. Used internally."""
        """ Here we should switch pending_data to hint mode."""
        tcpsock=self._owner.Connection
        tcpsock._sslObj    = ssl.wrap_socket(tcpsock._sock, None, None)
        tcpsock._sslIssuer = tcpsock._sslObj.getpeercert().get('issuer')
        tcpsock._sslServer = tcpsock._sslObj.getpeercert().get('server')
        tcpsock._recv = tcpsock._sslObj.read
        tcpsock._send = tcpsock._sslObj.write

        tcpsock._seen_data=1
        self._tcpsock=tcpsock
        tcpsock.pending_data=self.pending_data
        tcpsock._sslObj.setblocking(False)

        self.starttls='success'

    def StartTLSHandler(self, conn, starttls):
        """ Handle server reply if TLS is allowed to process. Behaves accordingly.
            Used internally."""
        if starttls.getNamespace()!=NS_TLS: return
        self.starttls=starttls.getName()
        if self.starttls=='failure':
            self.DEBUG("Got starttls response: "+self.starttls,'error')
            return
        self.DEBUG("Got starttls proceed response. Switching to TLS/SSL...",'ok')
        self._startSSL()
        self._owner.Dispatcher.PlugOut()
        dispatcher.Dispatcher().PlugIn(self._owner)

POST='POST'
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
class Bosh(PlugIn):

    connection_cls = {
        'http': HTTPConnection,
        'https': HTTPSConnection,
    }

    default_headers = {
        'Content-Type': 'text/xml; charset=utf-8',
        'Connection': 'Keep-Alive',
    }

    def __init__(self, endpoint, server=None, port=None, use_srv=True, wait=80,
            hold=4, requests=5, headers=None, PIPELINE=True, GZIP=True):
        PlugIn.__init__(self)
        self.DBG_LINE = 'bosh'
        self._exported_methods = [
            self.send, self.receive, self.disconnect,
        ]
        url = urlparse(endpoint)
        self._http_host = url.hostname
        self._http_path = url.path
        if url.port:
            self._http_port = url.port
        elif url.scheme == 'https':
            self._http_port = 443
        else:
            self._http_port = 80
        self._http_proto = url.scheme
        self._server = server
        self._port = port
        self.use_srv = use_srv
        self.Sid = None
        self._rid = 0
        self.wait = 80
        self.hold = hold
        self.requests = requests
        self._pipeline = None
        self.PIPELINE = PIPELINE
        if self.PIPELINE:
            self._respobjs = []
        else:
            self._respobjs = {}
        self.headers = headers or self.default_headers
        self.GZIP = GZIP

    def srv_lookup(self, server):
        # XXX Lookup TXT records to determine BOSH endpoint:
        # _xmppconnect IN TXT "_xmpp-client-xbosh=https://bosh.jabber.org:5280/bind"
        pass

    def plugin(self, owner):
        # XXX Provide resonable defaults if non were given, lookup service
        # records from DNS TXT records (see srv_lookup)
        if not self.connect(self._http_host, self._http_port):
            return
        self._owner.Connection=self
        self._owner.RegisterDisconnectHandler(self.disconnect)
        return 'ok'

    def connect(self, server=None, port=None, timeout=3, conopts={}):
        conn = self._connect(server, port, timeout, conopts)
        if conn:
            if self.PIPELINE:
                self._pipeline == conn
            else:
                conn.close()
            return 'ok'

    def _connect(self, server=None, port=None, timeout=3, conopts={}):
        endat = time.time() + timeout
        while True:
            cls = self.connection_cls[self._http_proto]
            conn = cls(server, port, **conopts)
            try:
                conn.connect()
            except socket.error as e:
                if e.errno == ECONNREFUSED: # Connection refused
                    if time.time() > endat:
                        msg = "Failed to connect to remote host %s: %s (%s)" % (
                            'server', e.strerror, e.errno,
                        )
                        self.DEBUG(msg, 'error')
                        raise
                else:
                    conn.close()
                    raise
                time.sleep(.5)
            else:
                break
        return conn

    def Connection(self, reset=False):
        if self.PIPELINE:
            if not self._pipeline or not self._pipeline.sock:
                self._pipeline = self._connect(
                    self._http_host, self._http_port
                )
            return self._pipeline
        conn = self._connect(self._http_host, self._http_port)
        conn.connect()
        return conn

    def refreshpipeline(I):
        if self._pipeline and self._pipeline.sock:
            self._pipeline.sock.shutdown()
            self._pipeline.sock.close()
        self._pipeline = None
        self.Connect()

    def plugout(self):
        for soc in self._respobjs:
            soc.close()
        if 'Connection' in self._owner.__dict__:
            del(self._owner.Connection)
            self._owner.UnregisterDisconnectHandler(self.disconnected)

    def receive(self):
        resp = ''
        if self.PIPELINE:
            res, data = self._respobjs.pop(0)
        else:
            res, data = self._respobjs.pop(sock)
        try:
            res.begin()
        except BadStatusLine:
            resp = sock.recv(1024)
            if len(resp) == 0:
                # The TCP Connection has been dropped, Resend the
                # request.
                self.refreshpipeline()
                node = Node(node=data)
                self.Rid = node.getAttr('rid')
                self.send(data)
                return resp
            else:
                # The server sent some data but it was a legit bad
                # status line.
                raise
        if res.status == OK:
            # Response to valid client request.
            headers = dict(res.getheaders())
            if headers.get('content-encoding', None) == 'gzip':
                a = StringIO()
                a.write(res.read())
                a.seek(0)
                gz = gzip.GzipFile(fileobj=a)
                data = gz.read()
            else:
                data = res.read()
            self.DEBUG(data, 'got')
        elif res.status == BAD_REQUEST:
            # Inform client that the format of an HTTP header or binding
            # element is unacceptable.
            self.DEBUG("The server did not undertand the request")
            raise Exception("Disconnected from server", 'error')
        elif res.status == FORBIDDEN:
            # Inform the client that it bas borken the session rules
            # (polling too frequently, requesting too frequently, too
            # many simultanious requests.
            self.DEBUG("Forbidden due to policy-violation", 'error')
            raise Exception("Disconnected from server")
        elif res.status == NOTFOUND:
            # Inform the client that (1) 'sid' is not valide, (2) 'stream' is
            # not valid, (3) 'rid' is larger than the upper limit of the
            # expected window, (4) connection manager is unable to resend
            # respons (5) 'key' sequence if invalid.
            self.DEBUG("Invalid/Corrupt Stream", 'error')
            raise Exception("Disconnected from server")
        else:
            msg = "Recieved status not defined in XEP-1204: %s" % res.status
            self.DEBUG(msg, 'error')
            raise Exception("Disconnected from server")
        node = Node(node=data)
        if  node.getName() != 'body':
            self.DEBUG("The server sent an invalid BOSH payload", 'error')
            raise IOError("Disconnected from server")
        if node.getAttr('type') == 'terminate':
            msg = "Connection manager terminated stream: %s" % (
                node.getAttr('condition')
            )
            self.DEBUG(msg, 'info')
            raise IOError("Disconnected from server")
        resp = self.bosh_to_xmlstream(node)
        if resp:
            self._owner.Dispatcher.Event('', DATA_RECEIVED, resp)
        else:
            self.send(data)
        return resp

    def bosh_to_xmlstream(self, node):
        if not self.Sid or self.restart:
            # Expect a stream features elemnt that needs to be opened by a
            # stream element.
            if self.restart:
                self.restart = False
            else:
                self.Sid = node.getAttr('sid')
                self.AuthId = node.getAttr('authid')
                self.wait = int(node.getAttr('wait') or self.wait)
                self.hold = int(node.getAttr('hold') or self.hold)
                self.requests = int(node.getAttr('requests') or self.requests)
            stream=Node('stream:stream', payload=node.getChildren())
            stream.setNamespace(self._owner.Namespace)
            stream.setAttr('version','1.0')
            stream.setAttr('xmlns:stream', NS_STREAMS)
            stream.setAttr('from', self._owner.Server)
            data = str(stream)[:-len('</stream:stream>')]
            resp = "<?xml version='1.0'?>%s"%str(data)
        elif node.getChildren():
            resp = ''.join(str(i) for i in node.getChildren())
        else:
            resp = ''
        return resp

    def xmlstream_to_bosh(self, stream):
        if stream.startswith("<?xml version='1.0'?><stream"):
            # The begining of an xml stream. This is expected to
            # happen two times through out the lifetime of the bosh
            # session. When we first open the session and once
            # after authentication.

            # Sanitize stream tag so that it is suitable for parsing.
            stream = stream.split('>',1)[1]
            stream = '%s/>'%str(stream)[:-1]
            stream = Node(node=stream)
            # XXX This hasn't been tested with old-style auth. Will
            # probably need to detec that and handle similarly.
            SASL = getattr(self._owner, 'SASL',  None)
            if SASL and SASL.startsasl == 'success':
                # Send restart after authentication.
                body = Node('body')
                body.setAttr('xmpp:restart', 'true')
                body.setAttr('xmlns:xmpp', 'urn:xmpp:xbosh')
                self.restart = True
            else:
                # Opening a new BOSH session.
                self.restart = False
                body=Node('body')
                body.setNamespace(NS_HTTP_BIND)
                body.setAttr('hold', self.hold)
                body.setAttr('wait', self.wait)
                body.setAttr('ver', '1.6')
                body.setAttr('xmpp:version', stream.getAttr('version'))
                body.setAttr('to', stream.getAttr('to'))
                body.setAttr('xmlns:xmpp', 'urn:xmpp:xbosh')
                # XXX Ack support for request acknowledgements.
                if self._server != self._http_host:
                    if self._port:
                        route = '%s:%s' % self._server, self._port
                    else:
                        route = self._server
                    body.setAttr('route', route)
        else:
            # Mid stream, wrap the xml stanza in a BOSH body wrapper
            if stream:
                if type(stream) == type('') or type(stream) == type(''):
                    stream = Node(node=stream)
                stream = [stream]
            else:
                stream = []
            body = Node('body', payload=stream)
        body.setNamespace('http://jabber.org/protocol/httpbind')
        body.setAttr('content', 'text/xml; charset=utf-8')
        body.setAttr('xml:lang', 'en')
        body.setAttr('rid', self.Rid)
        if self.Sid:
            body.setAttr('sid', self.Sid)
        return str(body)

    def send(self, raw_data, headers={}):
        if type(raw_data) != type('') or type(raw_data) != type(''):
            raw_data = str(raw_data)
        bosh_data = self.xmlstream_to_bosh(raw_data)
        default = dict(self.headers)
        default['Host'] = self._http_host
        default['Content-Length'] = len(bosh_data)
        if self.GZIP:
            default['Accept-Encoding'] = 'gzip, deflate'
        headers = dict(default, **headers) 
        conn = self.Connection()
        if self.PIPELINE:
            conn._HTTPConnection__state = _CS_IDLE
        self.DEBUG(bosh_data, 'sent')
        conn.request(POST, self._http_path, bosh_data, headers)
        respobj = conn.response_class(
                conn.sock, strict=conn.strict, method=conn._method,
        )
        if self.PIPELINE:
            self._respobjs.append(
                (respobj, bosh_data)
            )
        else:
            self._respobjs[conn.sock] = (respobj, bosh_data)
        if hasattr(self._owner, 'Dispatcher') and bosh_data.strip():
            self._owner.Dispatcher.Event('', DATA_SENT, bosh_data)
        return True

    def disconnect(self):
        self.DEBUG("Closing socket", 'stop')
        if self.PIPELINE:
            if self._pipeline and self._pipeline.sock:
                self._pipeline.sock.shutdown()
                self._pipeline.close()
        else:
            for sock in self._respobjs:
                sock.shutdown()
                sock.close()

    def disconnected(self):
        self.DEBUG("BOSH transport operation failed", 'error')

    def pending_data(self, timeout=0):
        pending = False
        if self.PIPELINE:
            if not self._pipeline or not self._pipeline.sock:
                return
            pending = select.select([self._pipeline.sock], [], [], timeout)[0]
        else:
            pending = select.select(list(self._respobjs.keys()), [], [], timeout,)[0]
        if not pending and self.accepts_more_requests():
            self.send('')
        return pending

    def accepts_more_requests(self):
        if not self.authenticated():
            return False
        if self.PIPELINE:
            return len(self._respobjs) < self.hold
        if len(self._respobjs) >= self.requests - 1:
            return False
        return len(self._respobjs) < self.hold

    def authenticated(self):
        return self._owner and '+' in self._owner.connected

    @property
    def Rid(self):
        """
        An auto incrementing response id.
        """
        if not self._rid:
            self._rid = random.randint(0, 10000000)
        else:
            self._rid += 1
        return str(self._rid)

    @Rid.setter
    def Rid(self, i):
        """
        Set the Rid's next value
        """
        self._rid = int(i) - 1

    def getPort(self):
        """
        Return the port of the backend server (behind the endpoint).
        """
        return self._port

