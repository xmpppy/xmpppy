##   auth.py
##
##   Copyright (C) 2003-2005 Alexey "Snake" Nezhdanov
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
Provides library with all Non-SASL and SASL authentication mechanisms.
Can be used both for client and transport authentication.
"""

from .protocol import *
from .client import PlugIn
import base64,random,re
from . import dispatcher
import hmac
from hashlib import md5,sha1,sha256,pbkdf2_hmac
from six import ensure_str,ensure_binary

CHARSET_ENCODING='utf-8'

def HH(some):
    return md5(ensure_binary(some, CHARSET_ENCODING)).hexdigest()
def H(some):
    return md5(ensure_binary(some, CHARSET_ENCODING)).digest()
def C(some):
    some = [ensure_binary(x, CHARSET_ENCODING) for x in some]
    return b':'.join(some)

def HHSHA1(some):
    return sha1(ensure_binary(some, CHARSET_ENCODING)).hexdigest()
def B64(some):
    return ensure_str(base64.b64encode(ensure_binary(some,CHARSET_ENCODING)),CHARSET_ENCODING)

class NonSASL(PlugIn):
    """ Implements old Non-SASL (XEP-0078) authentication used in jabberd1.4 and transport authentication."""
    def __init__(self,user,password,resource):
        """ Caches username, password and resource for auth. """
        PlugIn.__init__(self)
        self.DBG_LINE='gen_auth'
        self.user=user
        self.password=password
        self.resource=resource

    def plugin(self,owner):
        """ Determine the best auth method (digest/0k/plain) and use it for auth.
            Returns used method name on success. Used internally. """
        if not self.resource: return self.authComponent(owner)
        self.DEBUG('Querying server about possible auth methods','start')
        resp=owner.Dispatcher.SendAndWaitForResponse(Iq('get',NS_AUTH,payload=[Node('username',payload=[self.user])]))
        if not isResultNode(resp):
            self.DEBUG('No result node arrived! Aborting...','error')
            return
        iq=Iq(typ='set',node=resp)
        query=iq.getTag('query')
        query.setTagData('username',self.user)
        query.setTagData('resource',self.resource)

        if query.getTag('digest'):
            self.DEBUG("Performing digest authentication",'ok')
            query.setTagData('digest',HHSHA1(owner.Dispatcher.Stream._document_attrs['id']+self.password))
            if query.getTag('password'): query.delChild('password')
            method='digest'
        elif query.getTag('token'):
            token=query.getTagData('token')
            seq=query.getTagData('sequence')
            self.DEBUG("Performing zero-k authentication",'ok')
            hash = HHSHA1(HHSHA1(self.password)+token)
            for foo in range(int(seq)): hash = HHSHA1(hash)
            query.setTagData('hash',hash)
            method='0k'
        else:
            self.DEBUG("Sequre methods unsupported, performing plain text authentication",'warn')
            query.setTagData('password',self.password)
            method='plain'
        resp=owner.Dispatcher.SendAndWaitForResponse(iq)
        if isResultNode(resp):
            self.DEBUG('Sucessfully authenticated with remove host.','ok')
            owner.User=self.user
            owner.Resource=self.resource
            owner._registered_name=owner.User+'@'+owner.Server+'/'+owner.Resource
            return method
        self.DEBUG('Authentication failed!','error')

    def authComponent(self,owner):
        """ Authenticate component. Send handshake stanza and wait for result. Returns "ok" on success. """
        self.handshake=0
        owner.send(Node(NS_COMPONENT_ACCEPT+' handshake',payload=[HHSHA1(owner.Dispatcher.Stream._document_attrs['id']+self.password)]))
        owner.RegisterHandler('handshake',self.handshakeHandler,xmlns=NS_COMPONENT_ACCEPT)
        while not self.handshake:
            self.DEBUG("waiting on handshake",'notify')
            owner.Process(1)
        owner._registered_name=self.user
        if self.handshake+1: return 'ok'

    def handshakeHandler(self,disp,stanza):
        """ Handler for registering in dispatcher for accepting transport authentication. """
        if stanza.getName()=='handshake': self.handshake=1
        else: self.handshake=-1

class SASL(PlugIn):
    """ Implements SASL authentication. """
    def __init__(self,username,password):
        PlugIn.__init__(self)
        self.username=username
        self.password=password
        self.mechanism=None
        self.scram_state={}

    def plugin(self,owner):
        if 'version' not in self._owner.Dispatcher.Stream._document_attrs: self.startsasl='not-supported'
        elif self._owner.Dispatcher.Stream.features:
            try: self.FeaturesHandler(self._owner.Dispatcher,self._owner.Dispatcher.Stream.features)
            except NodeProcessed: pass
        else: self.startsasl=None

    def auth(self):
        """ Start authentication. Result can be obtained via "SASL.startsasl" attribute and will be
            either "success" or "failure". Note that successfull auth will take at least
            two Dispatcher.Process() calls. """
        if self.startsasl: pass
        elif self._owner.Dispatcher.Stream.features:
            try: self.FeaturesHandler(self._owner.Dispatcher,self._owner.Dispatcher.Stream.features)
            except NodeProcessed: pass
        else: self._owner.RegisterHandler('features',self.FeaturesHandler,xmlns=NS_STREAMS)

    def plugout(self):
        """ Remove SASL handlers from owner's dispatcher. Used internally. """
        if 'features' in self._owner.__dict__: self._owner.UnregisterHandler('features',self.FeaturesHandler,xmlns=NS_STREAMS)
        if 'challenge' in self._owner.__dict__: self._owner.UnregisterHandler('challenge',self.SASLHandler,xmlns=NS_SASL)
        if 'failure' in self._owner.__dict__: self._owner.UnregisterHandler('failure',self.SASLHandler,xmlns=NS_SASL)
        if 'success' in self._owner.__dict__: self._owner.UnregisterHandler('success',self.SASLHandler,xmlns=NS_SASL)

    def FeaturesHandler(self,conn,feats):
        """ Used to determine if server supports SASL auth. Used internally. """
        if not feats.getTag('mechanisms',namespace=NS_SASL):
            self.startsasl='not-supported'
            self.DEBUG('SASL not supported by server','error')
            return
        mecs=[]
        for mec in feats.getTag('mechanisms',namespace=NS_SASL).getTags('mechanism'):
            mecs.append(mec.getData())
        self._owner.RegisterHandler('challenge',self.SASLHandler,xmlns=NS_SASL)
        self._owner.RegisterHandler('failure',self.SASLHandler,xmlns=NS_SASL)
        self._owner.RegisterHandler('success',self.SASLHandler,xmlns=NS_SASL)
        node=None
        use_plus=False
        cb_type, cb_data = self._tls_channel_binding()
        if "SCRAM-SHA-256-PLUS" in mecs and cb_data:
            use_plus=True
            node=self._build_scram_auth('SCRAM-SHA-256-PLUS', cb_type, cb_data)
        elif "SCRAM-SHA-256" in mecs:
            node=self._build_scram_auth('SCRAM-SHA-256')
        elif "SCRAM-SHA-1-PLUS" in mecs and cb_data:
            use_plus=True
            node=self._build_scram_auth('SCRAM-SHA-1-PLUS', cb_type, cb_data)
        elif "SCRAM-SHA-1" in mecs:
            node=self._build_scram_auth('SCRAM-SHA-1')
        elif "ANONYMOUS" in mecs and self.username == None:
            self.mechanism='ANONYMOUS'
            node=Node('auth',attrs={'xmlns':NS_SASL,'mechanism':'ANONYMOUS'})
        elif "DIGEST-MD5" in mecs:
            self.mechanism='DIGEST-MD5'
            node=Node('auth',attrs={'xmlns':NS_SASL,'mechanism':'DIGEST-MD5'})
        elif "PLAIN" in mecs:
            self.mechanism='PLAIN'
            sasl_data='%s\x00%s\x00%s'%(self.username+'@'+self._owner.Server,self.username,self.password)
            node=Node('auth',attrs={'xmlns':NS_SASL,'mechanism':'PLAIN'},payload=[B64(sasl_data)])
        else:
            self.startsasl='failure'
            self.DEBUG('I can only use SCRAM-SHA-256(+)/SCRAM-SHA-1(+), DIGEST-MD5 and PLAIN mechanisms.','error')
            return
        if node:
            try:
                self.mechanism = node.getAttr('mechanism')
            except Exception:
                pass
        self.startsasl='in-process'
        self._owner.send(node.__str__())
        raise NodeProcessed

    def SASLHandler(self,conn,challenge):
        """ Perform next SASL auth step. Used internally. """
        if challenge.getNamespace()!=NS_SASL: return
        if challenge.getName()=='failure':
            try:
                reason_node = challenge.getChildren()[0]
            except:
                reason_node = challenge
            reason_text = ''
            try:
                for c in challenge.getChildren():
                    if c.getName() == 'text':
                        reason_text = c.getData() or ''
                        break
            except Exception:
                pass
            if self.mechanism and self.mechanism.endswith('-PLUS') and ('channel binding' in reason_text.lower() or 'binding' in reason_text.lower()):
                mech = self.mechanism.replace('-PLUS', '')
                self.DEBUG('Server rejected channel binding, falling back to %s' % mech, 'warn')
                self.mechanism = mech
                node = self._build_scram_auth(mech)
                self.startsasl = 'in-process'
                self._owner.send(node.__str__())
                raise NodeProcessed
            self.startsasl='failure'
            self.DEBUG('Failed SASL authentification: %s'%reason_node,'error')
            raise NodeProcessed
        elif challenge.getName()=='success':
            if self.mechanism and self.mechanism.startswith('SCRAM-SHA-256') and challenge.getData():
                data=ensure_str(base64.b64decode(challenge.getData()),CHARSET_ENCODING)
                attrs=self._scram_parse(data)
                expected=self.scram_state.get('server_signature')
                if expected and attrs.get('v')!=expected:
                    self.startsasl='failure'
                    self.DEBUG('SCRAM server signature mismatch','error')
                    raise NodeProcessed
            self.startsasl='success'
            self.DEBUG('Successfully authenticated with remote server.','ok')
            handlers=self._owner.Dispatcher.dumpHandlers()
            self._owner.Dispatcher.PlugOut()
            dispatcher.Dispatcher().PlugIn(self._owner)
            self._owner.Dispatcher.restoreHandlers(handlers)
            self._owner.User=self.username
            raise NodeProcessed
########################################3333
        if self.mechanism and self.mechanism.startswith('SCRAM-SHA-'):
            self._handle_scram_challenge(challenge)
            raise NodeProcessed

        incoming_data=challenge.getData()
        chal={}
        data=base64.b64decode(incoming_data)
        data=ensure_str(data,CHARSET_ENCODING)
        self.DEBUG('Got challenge: '+data,'ok')
        for pair in re.findall(r'(\w+\s*=\s*(?:(?:"[^"]+")|(?:[^,]+)))',data):
            key,value=[x.strip() for x in pair.split('=', 1)]
            if value[:1]=='"' and value[-1:]=='"': value=value[1:-1]
            chal[key]=value
        if 'qop' in chal and 'auth' in [x.strip() for x in chal['qop'].split(',')]:
            resp={}
            resp['username']=self.username
            resp['realm']=self._owner.Server
            resp['nonce']=chal['nonce']
            cnonce=''
            for i in range(7):
                cnonce+=hex(int(random.random()*65536*4096))[2:]
            resp['cnonce']=cnonce
            resp['nc']=('00000001')
            resp['qop']='auth'
            resp['digest-uri']='xmpp/'+self._owner.Server
            A1=C([H(C([resp['username'],resp['realm'],self.password])),resp['nonce'],resp['cnonce']])
            A2=C(['AUTHENTICATE',resp['digest-uri']])
            response= HH(C([HH(A1),resp['nonce'],resp['nc'],resp['cnonce'],resp['qop'],HH(A2)]))
            resp['response']=response
            resp['charset']=CHARSET_ENCODING
            sasl_data=''
            for key in ['charset','username','realm','nonce','nc','cnonce','digest-uri','response','qop']:
                if key in ['nc','qop','response','charset']: sasl_data+="%s=%s,"%(key,resp[key])
                else: sasl_data+='%s="%s",'%(key,resp[key])
########################################3333
            node=Node('response',attrs={'xmlns':NS_SASL},payload=[B64(sasl_data[:-1])])
            self._owner.send(node.__str__())
        elif 'rspauth' in chal: self._owner.send(Node('response',attrs={'xmlns':NS_SASL}).__str__())
        else:
            self.startsasl='failure'
            self.DEBUG('Failed SASL authentification: unknown challenge','error')
        raise NodeProcessed

    # ---- SCRAM-SHA-256 helpers ----
    def _tls_channel_binding(self):
        """Return (cb_type, cb_data) if TLS channel binding data is available."""
        try:
            conn = getattr(self._owner, 'Connection', None)
            sslobj = getattr(conn, '_sslObj', None)
            if not sslobj:
                return (None, None)
            if hasattr(sslobj, 'version') and sslobj.version() and 'TLSv1.3' in sslobj.version():
                if hasattr(sslobj, 'export_keying_material'):
                    data = sslobj.export_keying_material(b"EXPORTER-Channel-Binding", 32, b"")
                    return ('tls-exporter', data)
            if hasattr(sslobj, 'get_channel_binding'):
                data = sslobj.get_channel_binding('tls-unique')
                if data:
                    return ('tls-unique', data)
        except Exception as exc:
            self.DEBUG('Channel binding unavailable: %s'%exc,'warn')
        return (None, None)

    def _scram_escape(self,value):
        return value.replace('=','=3D').replace(',','=2C')

    def _scram_build_gs2(self,cb_type=None):
        if cb_type:
            return 'p=%s,,'%(cb_type)
        return 'n,,'

    def _build_scram_auth(self, mechanism, cb_type=None, cb_data=b''):
        self.mechanism=mechanism
        nonce_bytes=random.randbytes(18) if hasattr(random,'randbytes') else bytes([random.randint(0,255) for _ in range(18)])
        nonce=base64.b64encode(nonce_bytes).decode('ascii')
        gs2_header=self._scram_build_gs2(cb_type if mechanism.endswith('PLUS') else None)
        client_first_bare='n=%s,r=%s'%(self._scram_escape(self.username),nonce)
        client_first_message=gs2_header+client_first_bare
        self.scram_state={
            'gs2':gs2_header,
            'nonce':nonce,
            'client_first_bare':client_first_bare,
            'server_first':None,
            'cb_data':cb_data if mechanism.endswith('PLUS') else b'',
        }
        return Node('auth',attrs={'xmlns':NS_SASL,'mechanism':mechanism},payload=[B64(client_first_message)])

    def _scram_parse(self, data):
        attrs={}
        for item in data.split(','):
            if '=' in item:
                k,v=item.split('=',1)
                attrs[k]=v
        return attrs

    def _handle_scram_challenge(self,challenge):
        incoming_data=challenge.getData()
        data=ensure_str(base64.b64decode(incoming_data),CHARSET_ENCODING)
        attrs=self._scram_parse(data)
        self.DEBUG('Got SCRAM challenge: '+data,'ok')
        if 'e' in attrs:
            self.startsasl='failure'
            self.DEBUG('SCRAM error: %s'%attrs.get('e'),'error')
            return
        state=self.scram_state
        if state.get('server_first') is None:
            # server-first message
            combined_nonce=attrs.get('r','')
            if not combined_nonce.startswith(state['nonce']):
                self.startsasl='failure'
                self.DEBUG('SCRAM nonce mismatch','error')
                return
            salt=base64.b64decode(attrs.get('s',''))
            iterations=int(attrs.get('i','0'))
            if iterations<=0:
                self.startsasl='failure'
                self.DEBUG('SCRAM invalid iteration count','error')
                return
            gs2header=state['gs2']
            cb_data=state.get('cb_data',b'')
            cbind=B64(gs2header.encode(CHARSET_ENCODING)+cb_data)
            if self.mechanism and 'SHA-256' in self.mechanism:
                hash_name = 'sha256'
                hash_mod = sha256
            else:
                hash_name = 'sha1'
                hash_mod = sha1
            salted=pbkdf2_hmac(hash_name,ensure_binary(self.password,CHARSET_ENCODING),salt,iterations)
            client_key=hmac.new(salted,b"Client Key",hash_mod).digest()
            stored_key=hash_mod(client_key).digest()
            client_final_no_proof='c=%s,r=%s'%(cbind,combined_nonce)
            auth_message=','.join([state['client_first_bare'],data,client_final_no_proof])
            client_signature=hmac.new(stored_key,ensure_binary(auth_message,CHARSET_ENCODING),hash_mod).digest()
            proof=bytes([a ^ b for a,b in zip(client_key,client_signature)])
            server_key=hmac.new(salted,b"Server Key",hash_mod).digest()
            server_signature=hmac.new(server_key,ensure_binary(auth_message,CHARSET_ENCODING),hash_mod).digest()
            state['server_signature']=base64.b64encode(server_signature).decode('ascii')
            state['server_first']=data
            resp='%s,p=%s'%(client_final_no_proof,base64.b64encode(proof).decode('ascii'))
            node=Node('response',attrs={'xmlns':NS_SASL},payload=[B64(resp)])
            self._owner.send(node.__str__())
        else:
            # Should not reach here because success handled separately
            self.DEBUG('Unexpected SCRAM challenge state','warn')

class Bind(PlugIn):
    """ Bind some JID to the current connection to allow router know of our location."""
    def __init__(self):
        PlugIn.__init__(self)
        self.DBG_LINE='bind'
        self.bound=None

    def plugin(self,owner):
        """ Start resource binding, if allowed at this time. Used internally. """
        if self._owner.Dispatcher.Stream.features:
            try: self.FeaturesHandler(self._owner.Dispatcher,self._owner.Dispatcher.Stream.features)
            except NodeProcessed: pass
        else: self._owner.RegisterHandler('features',self.FeaturesHandler,xmlns=NS_STREAMS)

    def plugout(self):
        """ Remove Bind handler from owner's dispatcher. Used internally. """
        self._owner.UnregisterHandler('features',self.FeaturesHandler,xmlns=NS_STREAMS)

    def FeaturesHandler(self,conn,feats):
        """ Determine if server supports resource binding and set some internal attributes accordingly. """
        if not feats.getTag('bind',namespace=NS_BIND):
            self.bound='failure'
            self.DEBUG('Server does not requested binding.','error')
            return
        if feats.getTag('session',namespace=NS_SESSION): self.session=1
        else: self.session=-1
        self.bound=[]

    def Bind(self,resource=None):
        """ Perform binding. Use provided resource name or random (if not provided). """
        while self.bound is None and self._owner.Process(1): pass
        if resource: resource=[Node('resource',payload=[resource])]
        else: resource=[]
        resp=self._owner.SendAndWaitForResponse(Protocol('iq',typ='set',payload=[Node('bind',attrs={'xmlns':NS_BIND},payload=resource)]))
        if isResultNode(resp):
            self.bound.append(resp.getTag('bind').getTagData('jid'))
            self.DEBUG('Successfully bound %s.'%self.bound[-1],'ok')
            jid=JID(resp.getTag('bind').getTagData('jid'))
            self._owner.User=jid.getNode()
            self._owner.Resource=jid.getResource()
            resp=self._owner.SendAndWaitForResponse(Protocol('iq',typ='set',payload=[Node('session',attrs={'xmlns':NS_SESSION})]))
            if isResultNode(resp):
                self.DEBUG('Successfully opened session.','ok')
                self.session=1
                return 'ok'
            else:
                self.DEBUG('Session open failed.','error')
                self.session=0
        elif resp: self.DEBUG('Binding failed: %s.'%resp.getTag('error'),'error')
        else:
            self.DEBUG('Binding failed: timeout expired.','error')
            return ''

class ComponentBind(PlugIn):
    """ ComponentBind some JID to the current connection to allow router know of our location."""
    def __init__(self, sasl):
        PlugIn.__init__(self)
        self.DBG_LINE='bind'
        self.bound=None
        self.needsUnregister=None
        self.sasl = sasl

    def plugin(self,owner):
        """ Start resource binding, if allowed at this time. Used internally. """
        if not self.sasl:
            self.bound=[]
            return
        if self._owner.Dispatcher.Stream.features:
            try: self.FeaturesHandler(self._owner.Dispatcher,self._owner.Dispatcher.Stream.features)
            except NodeProcessed: pass
        else:
            self._owner.RegisterHandler('features',self.FeaturesHandler,xmlns=NS_STREAMS)
            self.needsUnregister=1

    def plugout(self):
        """ Remove ComponentBind handler from owner's dispatcher. Used internally. """
        if self.needsUnregister:
            self._owner.UnregisterHandler('features',self.FeaturesHandler,xmlns=NS_STREAMS)

    def FeaturesHandler(self,conn,feats):
        """ Determine if server supports resource binding and set some internal attributes accordingly. """
        if not feats.getTag('bind',namespace=NS_BIND):
            self.bound='failure'
            self.DEBUG('Server does not requested binding.','error')
            return
        if feats.getTag('session',namespace=NS_SESSION): self.session=1
        else: self.session=-1
        self.bound=[]

    def Bind(self,domain=None):
        """ Perform binding. Use provided domain name (if not provided). """
        while self.bound is None and self._owner.Process(1): pass
        if self.sasl:
            xmlns = NS_COMPONENT_1
        else:
            xmlns = None
        self.bindresponse = None
        ttl = dispatcher.DefaultTimeout
        self._owner.RegisterHandler('bind',self.BindHandler,xmlns=xmlns)
        self._owner.send(Protocol('bind',attrs={'name':domain},xmlns=NS_COMPONENT_1))
        while self.bindresponse is None and self._owner.Process(1) and ttl > 0: ttl-=1
        self._owner.UnregisterHandler('bind',self.BindHandler,xmlns=xmlns)
        resp=self.bindresponse
        if resp and resp.getAttr('error'):
            self.DEBUG('Binding failed: %s.'%resp.getAttr('error'),'error')
        elif resp:
            self.DEBUG('Successfully bound.','ok')
            return 'ok'
        else:
            self.DEBUG('Binding failed: timeout expired.','error')
            return ''

    def BindHandler(self,conn,bind):
        self.bindresponse = bind
        pass
