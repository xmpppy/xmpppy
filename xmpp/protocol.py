##   protocol.py 
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

from simplexml import Node
import time

NS_DELAY='jabber:x:delay'
NS_DATA ='jabber:x:data'

def resultNode(node): return node and node.getType()=='result'
def errorNode(node): return node and node.getType()=='error'

class JID:
    def __init__(self, jid, node='', domain='', resource=''):
        if not jid: raise ValueError('JID must contain at least domain name')
        elif type(jid)==type(self): self.node,self.domain,self.resource=jid.node,jid.domain,jid.resource
        elif domain: self.node,self.domain,self.resource=node,domain,resource
        else:
            if jid.find('@')+1: self.node,jid=jid.split('@')
            else: self.node=''
            if jid.find('/')+1: self.domain,self.resource=jid.split('/')
            else: self.domain,self.resource=jid,''
    def getNode(self): return self.node
    def setNode(self,node): self.node=node
    def getDomain(self): return self.domain
    def setDomain(self,domain): self.domain=domain
    def getResource(self): return self.resource
    def setResource(self,resource): self.resource=resource
    def getStripped(self): return self.__str__(0)
    def __eq__(self, other):
        other=JID(other)
        return self.resource==other.resource and self.__str__(0) == other.__str__(0)
    def bareMatch(self, other): return self.__str__(0) == JID(other).__str__(0)
    def __str__(self,wresource=1):
        if self.node: jid=self.node+'@'+self.domain
        else: jid=self.domain
        if wresource and self.resource: return jid+'/'+self.resource
        return jid.lower()

class Protocol(Node):
    def __init__(self, name=None, to=None, type=None, frm=None, attrs={}, payload=[], timestamp=None, node=None):
        if not attrs: attrs={}
        if to: attrs['to']=to
        if frm: attrs['from']=frm
        if type: attrs['type']=type
        Node.__init__(self, tag=name, attrs=attrs, payload=payload, node=node)
        if node and self.__class__==node.__class__ and self.attrs.has_key('id'): del self.attrs['id']
        self.timestamp=None
        for x in self.getTags('x',namespace=NS_DELAY):
            try:
                if x.getAttr('stamp')>self.getTimestamp(): self.setTimestamp(x.getAttr('stamp'))
            except: pass
        if timestamp is not None: self.setTimestamp(timestamp)  # To auto-timestamp stanza just pass timestamp=''
    def getTo(self):
        try: return JID(self.getAttr('to'))
        except: return None
    def getFrom(self):
        try: return JID(self.getAttr('from'))
        except: return None
    def getTimestamp(self): return self.timestamp
    def getID(self): return self.getAttr('id')
    def setTo(self,val): self.setAttr('to', val)
    def getType(self): return self.getAttr('type')
    def setFrom(self,val): self.setAttr('from', val)
    def setType(self,val): self.setAttr('type', val)
    def setID(self,val): self.setAttr('id', val)
    def getError(self): return self.getTagData('error')
    def getErrorCode(self): return self.getTagAttr('error','code')
    def setError(self,code,comment):
        self.setTagData('error',comment)
        self.setTagAttr('error','code',code)
    def setTimestamp(self,val=None):
        if not val: val=time.strftime('%Y%m%dT%H:%M:%S', time.gmtime())
        self.timestamp=val
        self.setTag('x',{'stamp':self.timestamp},namespace=NS_DELAY)
    def getProperties(self):
        props=[]
        for child in self.getChildren():
            if child.getNamespace()<>self.getNamespace(): props.append(child.getNamespace())
        return props

class Message(Protocol):
    def __init__(self, to=None, body=None, type=None, subject=None, attrs={}, frm=None, payload=[], timestamp=None, node=None):
        Protocol.__init__(self, 'message', to=to, type=type, attrs=attrs, frm=frm, payload=payload, timestamp=timestamp, node=node)
        if body: self.setBody(body)
        if subject: self.setSubject(subject)
    def getBody(self): return self.getTagData('body')
    def getSubject(self): return self.getTagData('subject')
    def getThread(self): return self.getTagData('thread')
    def setBody(self,val): self.setTagData('body',val)
    def setSubject(self,val): self.setTagData('subject',val)
    def setThread(self,val): self.setTagData('thread',val)

class Presence(Protocol):
    def __init__(self, to=None, type=None, priority=None, show=None, status=None, attrs={}, frm=None, timestamp=None, payload=[], node=None):
        Protocol.__init__(self, 'presence', to=to, type=type, attrs=attrs, frm=frm, payload=payload, timestamp=timestamp, node=node)
        if priority: self.setPriority(priority)
        if show: self.setShow(show)
        if status: self.setStatus(status)
    def getPriority(self): return self.getTagData('priority')
    def getShow(self): return self.getTagData('show')
    def getStatus(self): return self.getTagData('status')
    def setPriority(self,val): self.setTagData('priority',val)
    def setShow(self,val): self.setTagData('show',val)
    def setStatus(self,val): self.setTagData('status',val)

class Iq(Protocol): 
    def __init__(self, type=None, queryNS=None, attrs={}, to=None, frm=None, payload=[], node=None):
        Protocol.__init__(self, 'iq', to=to, type=type, attrs=attrs, frm=frm, node=node)
        if payload: self.setQueryPayload(payload)
        if queryNS: self.setQueryNS(queryNS)
    def getQueryNS(self):
        tag=self.getTag('query')
        if tag: return tag.getNamespace()
    def getQueryPayload(self):
        tag=self.getTag('query')
        if tag: return tag.getPayload()
    def setQueryNS(self,namespace): self.setTag('query').setNamespace(namespace)
    def setQueryPayload(self,payload): self.setTag('query').setPayload(payload)

class DataForm(Node):
    def __init__(self,data):
        Node.__init__(self,'x')
        self.setNamespace(NS_DATA)
        if type(data) in [type(()),type([])]:
            dict={}
            for i in data: dict[i]=''
        else: dict=data
        for key in dict.keys():
            self.setField(key,dict[key])
    def asDict(self):
        ret={}
        for i in self.getTags('field'):
            ret[i.getAttr('var')]=i.getTagData('value')
        return ret
    def getField(self,name):
        tag=self.getTag('field',attrs={'var':name})
        if tag: return tag.getTagData('value')
    def setField(self,name, val): self.setTag('field',attrs={'var':name}).setTagData('value',val)
    def setFromDict(self,dict):
        for i in dict.keys(): self.setField(i,dict[i])
