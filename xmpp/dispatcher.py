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

import protocol,simplexml,time

DBG_DISPATCHER='dispatcher'

DefaultTimeout=25
ID=0

class Dispatcher:
    def __init__(self):
        self.handlers={}
        self._expected={}
        
    def PlugIn(self, owner):
        self._owner=owner
        self._owner.debug_flags.append(DBG_DISPATCHER)
        self._owner.DEBUG(DBG_DISPATCHER,"Plugging into %s"%(owner),'start')
        self.RegisterProtocol('unknown',protocol.Protocol)
        self.RegisterProtocol('iq',protocol.Iq)
        self.RegisterProtocol('presence',protocol.Presence)
        self.RegisterProtocol('message',protocol.Message)
        self._owner.Dispatcher=self
        self._owner.Process=self.Process
        self._owner.RegisterHandler=self.RegisterHandler
        self._owner.RegisterHandlerOnce=self.RegisterHandlerOnce
        self._owner.UnregisterHandler=self.UnregisterHandler
        self._owner.RegisterProtocol=self.RegisterProtocol
        self._owner.WaitForResponse=self.WaitForResponse
        self._owner.SendAndWaitForResponse=self.SendAndWaitForResponse
        self._owner.lastErrNode=None
        self._owner.lastErr=None
        self._owner.lastErrCode=None
        self._owner_send=self._owner.send
        self._owner.send=self.send
        self._owner.disconnect=self.disconnect
        self.StreamInit()

    def PlugOut(self):
        self._owner.DEBUG(DBG_DISPATCHER,"Plugging out.",'stop')
        del self._owner.disconnect
        self._owner.send=self._owner_send
        del self._owner.SendAndWaitForResponse
        del self._owner.WaitForResponse
        del self._owner.lastErrCode
        del self._owner.lastErr
        del self._owner.lastErrNode
        del self._owner.RegisterProtocol
        del self._owner.UnregisterHandler
        del self._owner.RegisterHandlerOnce
        del self._owner.RegisterHandler
        del self._owner.Process
        del self._owner.Dispatcher
        self._owner.debug_flags.remove(DBG_DISPATCHER)

    def StreamInit(self):
        self.Stream=simplexml.NodeBuilder()
        self.Stream._dispatch_depth=2
        self.Stream.dispatch=self.dispatch
        self._owner.debug_flags.append(simplexml.DBG_NODEBUILDER)
        self.Stream.DEBUG=self._owner.DEBUG
        self.Stream.features=None
        self._owner.send("<?xml version='1.0'?><stream:stream version='1.0' xmlns:stream='http://etherx.jabber.org/streams' to='%s' xmlns='%s'>"%(self._owner.Server,self._owner.Namespace))

    def Process(self, timeout=0):
        if self._owner.Connection.pending_data(timeout):
            data=self._owner.Connection.receive()
            self.Stream.Parse(data)
            return len(data)
        return '0'	# It means that nothing is received but link is alive.
        
    def RegisterProtocol(self,tag_name,Proto,order='info'):
        self._owner.DEBUG(DBG_DISPATCHER,'Registering protocol "%s" as %s'%(tag_name,Proto), order)
        self.handlers[tag_name]={type:Proto, 'default':[]}

    def RegisterHandler(self,name,handler,type='',ns='',chained=0, makefirst=0, system=0):
        self._owner.DEBUG(DBG_DISPATCHER,'Registering handler %s for "%s" type->%s ns->%s'%(handler,name,type,ns), 'info')
        if not type and not ns: type='default'
        if not self.handlers.has_key(name): self.RegisterProtocol(name,protocol.Protocol,'warn')
        if not self.handlers[name].has_key(type+ns): self.handlers[name][type+ns]=[]
        if makefirst: self.handlers[name][type+ns].insert({'chain':chained,'func':handler,'system':system})
        else: self.handlers[name][type+ns].append({'chain':chained,'func':handler,'system':system})

    def RegisterHandlerOnce(self,name,handler,type='',ns='',chained=0, makefirst=0, system=0):
        self.RegisterHandler(name,handler,type,ns,chained, makefirst, system)

    def UnregisterHandler(self,name,handler=None,type='',ns=''):
        if not type and not ns: type='default'
        self.handlers[name][type+ns].remove({'chain':chained,'func':handler,'system':system})

    def dispatch(self,stanza):
        name=stanza.getName()

        if name=='features': self.Stream.features=stanza

        if not self.handlers.has_key(name):
            self._owner.DEBUG(DBG_DISPATCHER, "Unknown stanza: " + name,'warn')
            name='unknown'
        else:
            self._owner.DEBUG(DBG_DISPATCHER,"Got %s stanza"%name, 'ok')

        stanza=self.handlers[name][type](node=stanza)

        typ=stanza.getType()
        if not typ: typ=''
        try: ns=stanza.getQueryNS()
        except: ns=''
        if not ns: ns=''
        typns=typ+ns
        ID=stanza.getID()

        self._owner.DEBUG(DBG_DISPATCHER,"Dispatching %s stanza with type->%s ns->%s id->%s"%(name,typ,ns,ID),'ok')

        if not self.handlers[name].has_key(ns): ns=''
        if not self.handlers[name].has_key(typ): typ=''
        if not self.handlers[name].has_key(typns): typns=''
        chain=[]
        for key in ['default',typ,ns,typns]: # we will use all handlers: from very common to very particular
            if key: chain += self.handlers[name][key]

        output=''
        if self._expected.has_key(ID):
            self._expected[ID]=stanza
            user=0
            self._owner.DEBUG(DBG_DISPATCHER,"Expected stanza arrived!",'ok')
        else: user=1
        for handler in chain:
            if user or handler['system']:
                if handler['chain']: output=handler['func'](self,stanza,output)
                else: handler['func'](self,stanza)

    def WaitForResponse(self, ID, timeout=DefaultTimeout):
        self._expected[ID]=None
        has_timed_out=0
        abort_time=time.time() + timeout
        self._owner.DEBUG(DBG_DISPATCHER,"Waiting for ID:%s with timeout %s..." % (ID,timeout),'wait')
        while not self._expected[ID]:
            if not self.Process(0.04):
                self._owner.lastErr="Disconnect"
                return None
            if time.time() > abort_time:
                self._owner.lastErr="Timeout"
                return None
        response=self._expected[ID]
        del self._expected[ID]
        if response.getErrorCode():
            self._owner.lastErrNode=response
            self._owner.lastErr=response.getError()
            self._owner.lastErrCode=response.getErrorCode()
        return response

    def SendAndWaitForResponse(self, stanza, timeout=DefaultTimeout):
        return self.WaitForResponse(self.send(stanza),timeout)

    def send(self,stanza):
        if type(stanza) in [type(''), type(u'')]: return self._owner_send(stanza)
        _ID=stanza.getID()
        if not _ID:
            global ID
            ID+=1
            _ID=`ID`
            stanza.setID(_ID)
        if self._owner._registered_name and not stanza.getAttr('from'): stanza.setAttr('from',self._owner._registered_name)
        self._owner_send(stanza)
        return _ID

    def disconnect(self):
        self._owner_send('</stream:stream>')
        while self.Process(1): pass
