#!/usr/bin/python
##   auth.py
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

from protocol import *
import sha,base64,random,dispatcher

import md5
def HH(some): return md5.new(some).hexdigest()
def H(some): return md5.new(some).digest()
def C(some): return ':'.join(some)

NS_AUTH="jabber:iq:auth"

DBG_AUTH='gen_auth'
class NonSASL:
    def __init__(self,user,password,resource):
        self.user=user
        self.password=password
        self.resource=resource

    def PlugOut(self): pass
    def PlugIn(self,owner):
        owner.debug_flags.append(DBG_AUTH)
        owner.DEBUG(DBG_AUTH,'Querying server about possible auth methods','start')
        resp=owner.Dispatcher.SendAndWaitForResponse(Iq('get',NS_AUTH,payload=[Node('username',payload=[self.user])]))
        if not resp or resp.getType()<>'result':
            owner.DEBUG(DBG_AUTH,'No result node arrived! Aborting...','error')
            return
        iq=Iq(type='set',node=resp)
        query=iq.getTag('query')
        query.setTagData('username',self.user)
        query.setTagData('resource',self.resource)

        if query.getTag('token'):
            token=query.getTagData('token')
            seq=query.getTagData('sequence')
            owner.DEBUG(DBG_AUTH,"Performing zero-k authentication",'ok')
            hash = sha.new(sha.new(self.password).hexdigest()+token).hexdigest()
            for foo in xrange(int(seq)): hash = sha.new(hash).hexdigest()
            query.setTagData('hash',hash)
        elif query.getTag('digest'):
            owner.DEBUG(DBG_AUTH,"Performing digest authentication",'ok')
            query.setTagData('digest',sha.new(owner.Dispatcher.Stream._document_attrs['id']+self.password).hexdigest())
        else:
            owner.DEBUG(DBG_AUTH,"Sequre methods unsupported, performing plain text authentication",'warn')
            query.setTagData('password',self.password)
        resp=owner.Dispatcher.SendAndWaitForResponse(iq)
        if resp and not resp.getError():
            owner.DEBUG(DBG_AUTH,'Sucessfully authenticated with remove host.','ok')
            owner.User=self.user
            owner.Resource=self.resource
            return 1
        owner.DEBUG(DBG_AUTH,'Authentication failed!','error')

DBG_SASL='SASL_auth'
NS_SASL='urn:ietf:params:xml:ns:xmpp-sasl'
class SASL:
    def __init__(self,username,password):
        self.username=username
        self.password=password
        self.startsasl=None
        self.nc=0
        self.uri='xmpp'

    def PlugIn(self,owner):
        self._owner=owner
        owner.debug_flags.append(DBG_SASL)
        owner.DEBUG(DBG_SASL,'Plugging into %s'%owner,'start')
        self._owner.SASL=self
        self._owner.RegisterHandler('features',self.FeaturesHandler)

    def FeaturesHandler(self,conn,feats):
        if not feats.getTag('mechanisms',namespace=NS_SASL):
            self.startsasl='failure'
            self._owner.DEBUG(DBG_SASL,'SASL not supported by server','error')
            return
        mecs=[]
        for mec in feats.getTag('mechanisms',namespace=NS_SASL).getTags('mechanism'):
            mecs.append(mec.getData())
        self._owner.RegisterHandler('challenge',self.SASLHandler)
        self._owner.RegisterHandler('failure',self.SASLHandler)
        self._owner.RegisterHandler('success',self.SASLHandler)
        if "DIGEST-MD5" in mecs:
            node=Node('auth',attrs={'xmlns':NS_SASL,'mechanism':'DIGEST-MD5'})
        elif "PLAIN" in mecs:
            sasl_data='%s\x00%s\x00%s'%(self._owner.Server,self.username,self.password)
            node=Node('auth',attrs={'xmlns':NS_SASL,'mechanism':'PLAIN'},payload=[base64.encodestring(sasl_data)])
        else:
            self.startsasl='failure'
            self._owner.DEBUG(DBG_SASL,'I can only use PLAIN mecanism for now.','error')
            return
        self._owner.send(node.__str__())

    def SASLHandler(self,conn,challenge):
        if challenge.getNamespace()<>NS_SASL: return
        if challenge.getName()=='failure':
            self.startsasl='failure'
            try: reason=challenge.getChildren()[0]
            except: reason=challenge
            self._owner.DEBUG(DBG_SASL,'Failed SASL authentification: %s'%reason,'error')
            return
        elif challenge.getName()=='success':
            self.startsasl='success'
            self._owner.DEBUG(DBG_SASL,'Successfully authenticated with remote server.','ok')
            self._owner.Dispatcher.PlugOut()
            dispatcher.Dispatcher().PlugIn(self._owner)
            self._owner.send_header()
            self._owner.User=self.username
            return
########################################3333
        incoming_data=challenge.getData()       # может быть потребуется str
        chal={}
        for pair in base64.decodestring(incoming_data).split(','):
            key,value=pair.split('=')
            if key in ['realm','nonce','qop','cipher']: value=value[1:-1]
            chal[key]=value
        if chal.has_key('realm'):       # может быть потребуется str
            resp={}
            resp['username']=self.username       # может быть потребуется str
            resp['realm']=chal['realm']       # может быть потребуется str
            resp['nonce']=chal['nonce']       # может быть потребуется str
            cnonce='OA6MHXh6VqTrRk'
#            for i in range(7):
#                cnonce+=hex(int(random.random()*65536*4096))[2:]
            resp['cnonce']=cnonce
            self.nc+=1
            resp['nc']=('0000000%i'%self.nc)[-8:]
            resp['qop']='auth'
            resp['digest-uri']=self.uri+'/'+self._owner.Server       # может быть потребуется str
            _A1=C([resp['username'],resp['realm'],self.password])
            A1=C([H(_A1),resp['nonce'],resp['cnonce']])
            A2=C(['AUTHENTICATE',resp['digest-uri']])
            response= HH(C([HH(A1),resp['nonce'],resp['nc'],resp['cnonce'],resp['qop'],HH(A2)]))
            resp['response']=response
            resp['charset']='utf-8'
            sasl_data=''
            for key in ['charset','username','realm','nonce','nc','cnonce','digest-uri','response','qop']:
                if key in ['nc','qop','response','charset']: sasl_data+="%s=%s,"%(key,resp[key])
                else: sasl_data+='%s="%s",'%(key,resp[key])
########################################3333
            print "sasl_data",sasl_data[:-1]
            node=Node('response',attrs={'xmlns':NS_SASL},payload=[base64.encodestring(sasl_data[:-1])])
            self._owner.send(node.__str__())
        elif chal.has_key('rspauth'): self._owner.send(Node('response',attrs={'xmlns':NS_SASL}).__str__())
        else: 
            self.startsasl='failure'
            self._owner.DEBUG(DBG_SASL,'Failed SASL authentification: unknown challenge','error')
            return

DBG_BIND='bind'
NS_BIND='urn:ietf:params:xml:ns:xmpp-bind'
class Bind:
    def __init__(self):
        self.bound=None

    def PlugIn(self,owner):
        self._owner=owner
        owner.debug_flags.append(DBG_BIND)
        owner.DEBUG(DBG_BIND,'Plugging into %s'%owner,'start')
        self._owner.Bind=self
        self._owner.RegisterHandler('features',self.FeaturesHandler)

    def FeaturesHandler(self,conn,feats):
        if not feats.getTag('bind',namespace=NS_BIND):
            self.bound='failure'
            self._owner.DEBUG(DBG_BIND,'Server does not requested binding.','error')
            return
        self.bound=[]

    def Bind(self,resource):
        while self.bound is None and self._owner.Process(1): pass
#        resp=self._owner.SendAndWaitForResponse(Protocol('iq',type='set',payload=[Node('bind',attrs={'xmlns':NS_BIND},payload=[Node('resource',payload=[resource])])]))
        resp=self._owner.SendAndWaitForResponse(Protocol('iq',type='set',payload=[Node('bind',attrs={'xmlns':NS_BIND})]))
        if resp and resp.getType()=='result':
            self.bound.append(resp.getTag('bind').getTagData('jid'))
            self._owner.DEBUG(DBG_BIND,'Successfully bound %s.'%self.bound[-1],'ok')
        elif resp: self._owner.DEBUG(DBG_BIND,'Binding failed: %s.'%resp.getTag('error'),'error')
        else: self._owner.DEBUG(DBG_BIND,'Binding failed: timeout expired.','error')
