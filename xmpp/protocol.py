##   protocol.py 
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

from simplexml import Node
import time

NS_DELAY   = 'jabber:x:delay'
NS_DATA    = 'jabber:x:data'
NS_STANZAS = 'urn:ietf:params:xml:ns:xmpp-stanzas'

xmpp_stream_error_conditions="""
bad-format --  --  -- The entity has sent XML that cannot be processed.
bad-namespace-prefix --  --  -- The entity has sent a namespace prefix that is unsupported, or has sent no namespace prefix on an element that requires such a prefix.
conflict --  --  -- The server is closing the active stream for this entity because a new stream has been initiated that conflicts with the existing stream.
connection-timeout --  --  -- The entity has not generated any traffic over the stream for some period of time.
host-gone --  --  -- The value of the 'to' attribute provided by the initiating entity in the stream header corresponds to a hostname that is no longer hosted by the server.
host-unknown --  --  -- The value of the 'to' attribute provided by the initiating entity in the stream header does not correspond to a hostname that is hosted by the server.
improper-addressing --  --  -- A stanza sent between two servers lacks a 'to' or 'from' attribute (or the attribute has no value).
internal-server-error --  --  -- The server has experienced a misconfiguration or an otherwise-undefined internal error that prevents it from servicing the stream.
invalid-from -- cancel --  -- The JID or hostname provided in a 'from' address does not match an authorized JID or validated domain negotiated between servers via SASL or dialback, or between a client and a server via authentication and resource authorization.
invalid-id --  --  -- The stream ID or dialback ID is invalid or does not match an ID previously provided.
invalid-namespace --  --  -- The streams namespace name is something other than "http://etherx.jabber.org/streams" or the dialback namespace name is something other than "jabber:server:dialback".
invalid-xml --  --  -- The entity has sent invalid XML over the stream to a server that performs validation.
not-authorized --  --  -- The entity has attempted to send data before the stream has been authenticated, or otherwise is not authorized to perform an action related to stream negotiation.
policy-violation --  --  -- The entity has violated some local service policy.
remote-connection-failed --  --  -- The server is unable to properly connect to a remote resource that is required for authentication or authorization.
resource-constraint --  --  -- The server lacks the system resources necessary to service the stream.
restricted-xml --  --  -- The entity has attempted to send restricted XML features such as a comment, processing instruction, DTD, entity reference, or unescaped character.
see-other-host --  --  -- The server will not provide service to the initiating entity but is redirecting traffic to another host.
system-shutdown --  --  -- The server is being shut down and all active streams are being closed.
undefined-condition --  --  -- The error condition is not one of those defined by the other conditions in this list.
unsupported-encoding --  --  -- The initiating entity has encoded the stream in an encoding that is not supported by the server.
unsupported-stanza-type --  --  -- The initiating entity has sent a first-level child of the stream that is not supported by the server.
unsupported-version --  --  -- The value of the 'version' attribute provided by the initiating entity in the stream header specifies a version of XMPP that is not supported by the server.
xml-not-well-formed --  --  -- The initiating entity has sent XML that is not well-formed."""
xmpp_stanza_error_conditions="""
bad-request -- 400 -- modify -- The sender has sent XML that is malformed or that cannot be processed.
conflict -- 409 -- cancel -- Access cannot be granted because an existing resource or session exists with the same name or address.
feature-not-implemented -- 501 -- cancel -- The feature requested is not implemented by the recipient or server and therefore cannot be processed.
forbidden -- 403 -- auth -- The requesting entity does not possess the required permissions to perform the action.
gone -- 302 -- modify -- The recipient or server can no longer be contacted at this address.
internal-server-error -- 500 -- wait -- The server could not process the stanza because of a misconfiguration or an otherwise-undefined internal server error.
item-not-found -- 404 -- cancel -- The addressed JID or item requested cannot be found.
jid-malformed -- 400 -- modify -- The value of the 'to' attribute in the sender's stanza does not adhere to the syntax defined in Addressing Scheme.
not-acceptable -- 406 -- cancel -- The recipient or server understands the request but is refusing to process it because it does not meet criteria defined by the recipient or server.
not-allowed -- 405 -- cancel -- The recipient or server does not allow any entity to perform the action.
payment-required -- 402 -- auth -- The requesting entity is not authorized to access the requested service because payment is required.
recipient-unavailable -- 404 -- wait -- The intended recipient is temporarily unavailable.
redirect -- 302 -- modify -- The recipient or server is redirecting requests for this information to another entity.
registration-required -- 407 -- auth -- The requesting entity is not authorized to access the requested service because registration is required.
remote-server-not-found -- 404 -- cancel -- A remote server or service specified as part or all of the JID of the intended recipient does not exist.
remote-server-timeout -- 504 -- wait -- A remote server or service specified as part or all of the JID of the intended recipient could not be contacted within a reasonable amount of time.
resource-constraint -- 500 -- wait -- The server or recipient lacks the system resources necessary to service the request.
service-unavailable -- 503 -- cancel -- The server or recipient does not currently provide the requested service.
subscription-required -- 407 -- auth -- The requesting entity is not authorized to access the requested service because a subscription is required.
undefined-condition -- 500 --  -- 
unexpected-request -- 400 -- wait -- The recipient or server understood the request but was not expecting it at this time (e.g., the request was out of order)."""

ERRORS,_errorcodes={},{}
for err in (xmpp_stream_error_conditions+xmpp_stanza_error_conditions)[1:].split('\n'):
    cond,code,typ,text=err.split(' -- ')
    name='ERR_'+cond.upper().replace('-','_')
    locals()[name]=cond
    ERRORS[cond]=[code,typ,text]
    _errorcodes[code]=cond
del err,cond,code,typ,text

def isResultNode(node): return node and node.getType()=='result'
def isErrorNode(node): return node and node.getType()=='error'

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

gen_type=type
class Protocol(Node):
    def __init__(self, name=None, to=None, type=None, frm=None, attrs={}, payload=[], timestamp=None, node=None):
        if not attrs: attrs={}
        if to: attrs['to']=to
        if frm: attrs['from']=frm
        if type: attrs['type']=type
        Node.__init__(self, tag=name, attrs=attrs, payload=payload, node=node)
        if node and gen_type(self)==gen_type(node) and self.__class__==node.__class__ and self.attrs.has_key('id'): del self.attrs['id']
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
    def getError(self):
        for tag in self.getTag('error').getChildren():
            if tag.getName()<>'text': return tag.getName()
        return self.getTagData('error')
    def getErrorCode(self): return self.getTagAttr('error','code')
    def setError(self,error,code=None):
        if code:
            if str(code) in _errorcodes.keys(): error=ErrorNode(_errorcodes[str(code)],text=error)
            else: error=ErrorNode(ERR_UNDEFINED_CONDITION,code=code,type='cancel',text=error)
        elif type(error) in [type(''),type(u'')]: error=ErrorNode(error)
        self.setType('error')
        self.addChild(node=error)
    def setTimestamp(self,val=None):
        if not val: val=time.strftime('%Y%m%dT%H:%M:%S', time.gmtime())
        self.timestamp=val
        self.setTag('x',{'stamp':self.timestamp},namespace=NS_DELAY)
    def getProperties(self):
        props=[]
        for child in self.getChildren():
            prop=child.getNamespace()
            if prop not in props: props.append(prop)
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
    def buildReply(self,text=None): return Message(to=self.getFrom(),frm=self.getTo(),body=text,node=self)

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
    def buildReply(self,type): return Iq(type,to=self.getFrom(),frm=self.getTo(),attrs={'id':self.getID()})

class DataForm(Node):
    def __init__(self,data=None,node=None):
        Node.__init__(self,'x',node=node)
        self.setNamespace(NS_DATA)
        if type(data) in [type(()),type([])]:
            dict={}
            for i in data: dict[i]=''
        elif data: dict=data
        for key in dict.keys():
            self.setField(key,dict[key])
    def asDict(self):
        ret={}
        for i in self.getTags('field'):
            key,val=i.getAttr('var'),i.getTagData('value')
            if not ret.has_key(key) or val: ret[key]=val # Workaround for broken jabberd1.4 registration form reply
        return ret
    def getField(self,name):
        tag=self.getTag('field',attrs={'var':name})
        if tag: return tag.getTagData('value')
    def __getitem__(self,name):
        tag=self.getTag('field',attrs={'var':name})
        if tag: return tag.getTagData('value')
        else: raise IndexError('No such field')
    def setField(self,name,val): self.setTag('field',attrs={'var':name}).setTagData('value',val)
    __setitem__=setField
    def setFromDict(self,dict):
        for i in dict.keys(): self.setField(i,dict[i])

class ErrorNode(Node):
    def __init__(self,name,code=None,typ=None,text=None):
        """ Mandatory parameter: name
            Optional parameters: code, typ, text."""
        if ERRORS.has_key(name): cod,type,txt=ERRORS[name]
        else: cod,type,txt='','cancel',''
        if typ: type=typ
        if code: cod=code
        if text: txt=text
        Node.__init__(self,'error',{'type':type},[Node(NS_STANZAS+' '+name)])
        if txt: self.addChild(node=Node(NS_STANZAS+' text',{},[txt]))
        if cod: self.setAttr('code',cod)

class Error(Protocol):
    def __init__(self,error,node,reply=0):
        if reply: Protocol.__init__(self,to=node.getFrom(),frm=node.getTo(),node=node)
        else: Protocol.__init__(self,node=node)
        self.setError(error)
