##   transports.py
##
##   Copyright (C) 2003 Alexey "Snake" Nezhdanov
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

import socket,select,base64,dispatcher
from simplexml import ustr

class error:
    def __init__(self,comment):
        self._comment=comment

    def __str__(self):
        return self._comment

DBG_SOCKET='socket'
class TCPsocket:
    """Must be plugged into some object to work properly"""
    def __init__(self, server=None):
        self._server = server

    def PlugIn(self, owner):
        self._owner=owner
        self._owner.debug_flags.append(DBG_SOCKET)
        self._owner.DEBUG(DBG_SOCKET,"Plugging into %s"%(owner),'start')
        if not self._server: self._server=(self._owner.Server,5222)
        if not self.connect(self._server): return
        self._owner.Connection=self
        self._owner.send=self.send
        self._owner.disconnect=self.shutdown
        self._owner.RegisterDisconnectHandler(self.disconnected)
        return 'ok'

    def getHost(self): return self._server[0]
    def getPort(self): return self._server[1]

    def connect(self,server=None):
        try:
            if not server: server=self._server
            self._sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.connect(server)
            self._send=self._sock.sendall
            self._recv=self._sock.recv
            self._owner.DEBUG(DBG_SOCKET,"Successfully connected to remote host %s"%`server`,'start')
            return 'ok'
        except: pass

    def PlugOut(self):
        self._owner.DEBUG(DBG_SOCKET,"Plugging out.",'stop')
        self._owner.DeregisterDisconnectHandler(self.disconnected)
        self.shutdown()
        del self._owner.connection
        del self._owner.send
        del self._owner.disconnect

    def receive(self):
        """Reads incoming data. Blocks until done. Calls self.disconnected(self) if appropriate."""
        try: received = self._recv(1024)
        except: received = ''

        while select.select([self._sock],[],[],0)[0]:
            try: add = self._recv(1024)
            except: add=''
            received +=add
            if not add: break

        if len(received): # length of 0 means disconnect
            self._owner.DEBUG(DBG_SOCKET,received,'got')
        else:
            self._owner.DEBUG(DBG_SOCKET,'Socket error while receiving data','error')
            self._owner.disconnected()
        return received

    def send(self,raw_data):
        """Writes raw outgoing data. Blocks until done.
           If supplied data is unicode string, treating it as utf-8 encoded."""
        if type(raw_data)==type(u''): raw_data = raw_data.encode('utf-8')
        elif type(raw_data)<>type(''): raw_data = ustr(raw_data).encode('utf-8')
        try:
            self._send(raw_data)
            self._owner.DEBUG(DBG_SOCKET,raw_data,'sent')
        except:
            self._owner.DEBUG(DBG_SOCKET,"Socket error while sending data",'error')
            self._owner.disconnected()

    def pending_data(self,timeout=0):
        return select.select([self._sock],[],[],timeout)[0]

    def shutdown(self):
        """Close the socket"""
        self._owner.DEBUG(DBG_SOCKET,"Closing socket",'stop')
        self._sock.close()

    def disconnected(self):
        """Called when a Network Error or disconnection occurs.
        Designed to be overidden"""
        self._owner.DEBUG(DBG_SOCKET,"Socket operation failed",'error')

DBG_CONNECT_PROXY='CONNECTproxy'
class HTTPPROXYsocket(TCPsocket):
    def __init__(self,proxy,server=None):
        TCPsocket.__init__(self,server)
        self._proxy=proxy

    def PlugIn(self, owner):
        owner.debug_flags.append(DBG_CONNECT_PROXY)
        return TCPsocket.PlugIn(self,owner)

    def connect(self,dupe=None):
        if not TCPsocket.connect(self,(self._proxy['host'],self._proxy['port'])): return
        self._owner.DEBUG(DBG_CONNECT_PROXY,"Proxy server contacted, performing authentification",'start')
        connector = ['CONNECT %s:%s HTTP/1.0'%self._server,
            'Proxy-Connection: Keep-Alive',
            'Pragma: no-cache',
            'Host: %s:%s'%self._server,
            'User-Agent: HTTPPROXYsocket/v0.1']
        if self._proxy.has_key('user') and self._proxy.has_key('password'):
            credentials = '%s:%s'%(self._proxy['user'],self._proxy['password'])
            credentials = base64.encodestring(credentials).strip()
            connector.append('Proxy-Authorization: Basic '+credentials)
        connector.append('\r\n')
        self.send('\r\n'.join(connector))
        reply = self.receive().replace('\r','')
        try: proto,code,desc=reply.split('\n')[0].split(' ',2)
        except: raise error('Invalid proxy reply')
        if code<>'200':
            self._owner.DEBUG(DBG_CONNECT_PROXY,'Invalid proxy reply: %s %s %s'%(proto,code,desc),'error')
            self._owner.disconnected()
            return
        while reply.find('\n\n') == -1: reply += self.receive().replace('\r','')
        self._owner.DEBUG(DBG_CONNECT_PROXY,"Authentification successfull. Jabber server contacted.",'ok')
        return 'ok'

DBG_TLS='TLS'
NS_TLS='urn:ietf:params:xml:ns:xmpp-tls'
class TLS:
    def PlugIn(self,owner,now=0):
        if owner.__dict__.has_key('TLS'): return  # Already enabled.
        self._owner=owner
        self._owner.debug_flags.append(DBG_TLS)
        self._owner.DEBUG(DBG_TLS,"Plugging into %s"%`owner`,'start')
        self._owner.TLS=self
        if now: return self._startSSL()
        if self._owner.Dispatcher.Stream.features: self.FeaturesHandler(self._owner.Dispatcher,self._owner.Dispatcher.Stream.features)
        else: self._owner.RegisterHandlerOnce('features',self.FeaturesHandler)
        self.starttls=None

    def FeaturesHandler(self, conn, feats):
        if not feats.getTag('starttls',namespace=NS_TLS):
            self._owner.DEBUG(DBG_TLS,"TLS unsupported by remote server.",'warn')
            return
        self._owner.DEBUG(DBG_TLS,"TLS supported by remote server. Requesting TLS start.",'ok')
        self._owner.RegisterHandlerOnce('proceed',self.StartTLSHandler)
        self._owner.RegisterHandlerOnce('failure',self.StartTLSHandler)
        self._owner.Connection.send('<starttls xmlns="%s"/>'%NS_TLS)

    def _startSSL(self):
        tcpsock=self._owner.Connection
        tcpsock._sslObj    = socket.ssl(tcpsock._sock, None, None)
        tcpsock._sslIssuer = tcpsock._sslObj.issuer()
        tcpsock._sslServer = tcpsock._sslObj.server()
        tcpsock._recv = tcpsock._sslObj.read
        tcpsock._send = tcpsock._sslObj.write
        self.starttls='success'

    def StartTLSHandler(self, conn, starttls):
        if starttls.getNamespace()<>NS_TLS: return
        self.starttls=starttls.getName()
        if self.starttls=='failure':
            self._owner.DEBUG(DBG_TLS,"Got starttls responce: "+self.starttls,'error')
            return
        self._owner.DEBUG(DBG_TLS,"Got starttls proceed responce. Switching to SSL...",'ok')
        self._startSSL()
        self._owner.Dispatcher.PlugOut()
        dispatcher.Dispatcher().PlugIn(self._owner)
