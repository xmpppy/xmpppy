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

import simplexml,time
from protocol import Protocol,Iq,Presence,Message
from client import PlugIn

DefaultTimeout=25
ID=0

class NodeProcessed(Exception): pass

class Dispatcher(PlugIn):
    def __init__(self):
        PlugIn.__init__(self)
        DBG_LINE='dispatcher'
        self.handlers={}
        self._expected={}
        self._defaultHandler=None
        self._eventHandler=None
        self._cycleHandlers=[]
        self._exported_methods=[self.Process,self.RegisterHandler,self.RegisterDefaultHandler,\
        self.RegisterEventHandler,self.UnregisterCycleHandler,self.RegisterCycleHandler,\
        self.RegisterHandlerOnce,self.UnregisterHandler,self.RegisterProtocol,\
        self.WaitForResponse,self.SendAndWaitForResponse,self.send,self.disconnect]

    def dumpHandlers(self): return self.handlers
    def restoreHandlers(self,handlers): self.handlers=handlers

    def plugin(self, owner):
        self.RegisterProtocol('unknown',Protocol)
        self.RegisterProtocol('iq',Iq)
        self.RegisterProtocol('presence',Presence)
        self.RegisterProtocol('message',Message)
        for method in self._old_owners_methods:
            if method.__name__=='send': self._owner_send=method; break
        self._owner.lastErrNode=None
        self._owner.lastErr=None
        self._owner.lastErrCode=None
        self.StreamInit()

    def StreamInit(self):
        self.Stream=simplexml.NodeBuilder()
        self.Stream._dispatch_depth=2
        self.Stream.dispatch=self.dispatch
        self._owner.debug_flags.append(simplexml.DBG_NODEBUILDER)
        self.Stream.DEBUG=self._owner.DEBUG
        self.Stream.features=None
        self._owner.send("<?xml version='1.0'?><stream:stream version='1.0' xmlns:stream='http://etherx.jabber.org/streams' to='%s' xmlns='%s'>"%(self._owner.Server,self._owner.Namespace))

    def Process(self, timeout=0):
        """Returns:
            1) length of processed data if some data were processed;
            2) '0' string if no data were processed but link is alive;
            3) 0 (zero) if underlying connection is closed."""
        for handler in self._cycleHandlers: handler(self)
        if self._owner.Connection.pending_data(timeout):
            data=self._owner.Connection.receive()
            self.Stream.Parse(data)
            return len(data)
        return '0'	# It means that nothing is received but link is alive.
        
    def RegisterProtocol(self,tag_name,Proto,order='info'):
        self.DEBUG('Registering protocol "%s" as %s'%(tag_name,Proto), order)
        self.handlers[tag_name]={type:Proto, 'default':[]}

    def RegisterHandler(self,name,handler,typ='',ns='',chained=0, makefirst=0, system=0):
        self.DEBUG('Registering handler %s for "%s" type->%s ns->%s'%(handler,name,typ,ns), 'info')
        if not typ and not ns: typ='default'
        if not self.handlers.has_key(name): self.RegisterProtocol(name,Protocol,'warn')
        if not self.handlers[name].has_key(typ+ns): self.handlers[name][typ+ns]=[]
        if makefirst: self.handlers[name][typ+ns].insert({'chain':chained,'func':handler,'system':system})
        else: self.handlers[name][typ+ns].append({'chain':chained,'func':handler,'system':system})

    def RegisterHandlerOnce(self,name,handler,typ='',ns='',chained=0, makefirst=0, system=0):
        self.RegisterHandler(name,handler,typ,ns,chained, makefirst, system)

    def UnregisterHandler(self,name,handler=None,typ='',ns=''):
        if not typ and not ns: typ='default'
        self.handlers[name][typ+ns].remove({'chain':chained,'func':handler,'system':system})

    def RegisterDefaultHandler(self,handler): self._defaultHandler=handler
    def RegisterEventHandler(self,handler): self._eventHandler=handler

    def RegisterCycleHandler(self,handler):
        if handler not in self._cycleHandlers: self._cycleHandlers.append(handler)

    def UnregisterCycleHandler(self,handler):
        if handler in self._cycleHandlers: self._cycleHandlers.remove(handler)

    def Event(self,realm,event,data):
        if self._eventHandler: self._eventHandler(realm,event,data)

    def dispatch(self,stanza):
        self.Stream._mini_dom=None
        name=stanza.getName()

        if name=='features': self.Stream.features=stanza

        if not self.handlers.has_key(name):
            self.DEBUG("Unknown stanza: " + name,'warn')
            name='unknown'
        else:
            self.DEBUG("Got %s stanza"%name, 'ok')

        stanza=self.handlers[name][type](node=stanza)

        typ=stanza.getType()
        if not typ: typ=''
        props=stanza.getProperties()
        ID=stanza.getID()

        self.DEBUG("Dispatching %s stanza with type->%s props->%s id->%s"%(name,typ,props,ID),'ok')

        list=['default']                                                     # we will use all handlers:
        if self.handlers[name].has_key(typ): list.append(typ)                # from very common...
        for prop in props:
            if self.handlers[name].has_key(prop): list.append(prop)
            if self.handlers[name].has_key(typ+prop): list.append(typ+prop)  # ...to very particular

        chain=[]
        for key in list:
            if key: chain += self.handlers[name][key]

        output=''
        if self._expected.has_key(ID):
            self._expected[ID]=stanza
            user=0
            self.DEBUG("Expected stanza arrived!",'ok')
        else: user=1
        for handler in chain:
            if user or handler['system']:
                try:
                    if handler['chain']: output=handler['func'](self,stanza,output)
                    else: handler['func'](self,stanza)
                except NodeProcessed: user=0
        if user and self._defaultHandler: self._defaultHandler(stanza)

    def WaitForResponse(self, ID, timeout=DefaultTimeout):
        self._expected[ID]=None
        has_timed_out=0
        abort_time=time.time() + timeout
        self.DEBUG("Waiting for ID:%s with timeout %s..." % (ID,timeout),'wait')
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
