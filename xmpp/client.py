#!/usr/bin/python
##
##   client.py
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

import transports,dispatcher,debug,auth,roster
from features import *

Debug=debug
Debug.DEBUGGING_IS_ON=1
Debug.Debug.colors['socket']=debug.color_dark_gray
Debug.Debug.colors['CONNECTproxy']=debug.color_dark_gray
Debug.Debug.colors['nodebuilder']=debug.color_brown
Debug.Debug.colors['client']=debug.color_cyan
Debug.Debug.colors['component']=debug.color_cyan
Debug.Debug.colors['dispatcher']=debug.color_green
Debug.Debug.colors['auth']=debug.color_yellow
Debug.Debug.colors['roster']=debug.color_magenta

Debug.Debug.colors['down']=debug.color_brown
Debug.Debug.colors['up']=debug.color_brown
Debug.Debug.colors['data']=debug.color_brown
Debug.Debug.colors['ok']=debug.color_green
Debug.Debug.colors['warn']=debug.color_yellow
Debug.Debug.colors['error']=debug.color_red
Debug.Debug.colors['start']=debug.color_dark_gray
Debug.Debug.colors['stop']=debug.color_dark_gray
Debug.Debug.colors['sent']=debug.color_blue
Debug.Debug.colors['got']=debug.color_bright_cyan

DBG_CLIENT='client'
DBG_COMPONENT='component'

class CommonClient:
    def __init__(self,server,port=5222,debug=['always', 'nodebuilder']):
        if self.__class__.__name__=='Client': self.Namespace,self.DBG='jabber:client',DBG_CLIENT
        elif self.__class__.__name__=='Component': self.Namespace,self.DBG='jabber:component:accept',DBG_COMPONENT
        self.disconnect_handlers=[]
        self.Server=server
        self.Port=port
        self._DEBUG=Debug.Debug(debug)
        self.DEBUG=self._DEBUG.Show
        self.debug_flags=Debug.debug_flags
        self.debug_flags.append(self.DBG)
        self._owner=self
        self._registered_name=None
        self.RegisterDisconnectHandler(self.DisconnectHandler)

    def RegisterDisconnectHandler(self,handler):
        self.disconnect_handlers.append(handler)

    def DeregisterDisconnectHandler(self,handler):
        self.disconnect_handlers.remove(handler)

    def disconnected(self):
        self.DEBUG(self.DBG,'Disconnect detected','stop')
        self.disconnect_handlers.reverse()
        for i in self.disconnect_handlers: i()
        self.disconnect_handlers.reverse()

    def DisconnectHandler(self):        # default stuff. To be overriden or unregistered.
        raise IOError('Disconnected from server.')

    def event(self,eventName,args={}):
        print "Event: ",(eventName,args)

    def connect(self,server=None,proxy=None):
        if not server: server=(self.Server,self.Port)
        if proxy: connected=transports.HTTPPROXYsocket(proxy,server).PlugIn(self)
        else: connected=transports.TCPsocket(server).PlugIn(self)
        if not connected: return
        if self.Connection.getPort()==5223: transports.TLS().PlugIn(self,now=1)
        dispatcher.Dispatcher().PlugIn(self)
        while self.Dispatcher.Stream._document_attrs is None: self.Process(1)
        return 'ok'

class Client(CommonClient):
    def connect(self,server=None,proxy=None):
        if not CommonClient.connect(self,server,proxy): return
        transports.TLS().PlugIn(self)
        if not self.Dispatcher.Stream._document_attrs.has_key('version') or not self.Dispatcher.Stream._document_attrs['version']=='1.0': return
        while not self.Dispatcher.Stream.features and self.Process(): pass      # If we get version 1.0 stream the features tag MUST BE presented
        if not self.Dispatcher.Stream.features.getTag('starttls'): return       # TLS not supported by server
        while not self.TLS.starttls and self.Process(): pass
        if self.TLS.starttls<>'proceed': self.event('tls_failed'); return 'tls failed'
        return 'ok'

    def auth(self,user,password,resource='xmpppy'):
        auth.SASL(user,password).PlugIn(self)
        while not self.Dispatcher.Stream._document_attrs and self.Process(): pass
        if self.Dispatcher.Stream._document_attrs.has_key('version') and self.Dispatcher.Stream._document_attrs['version']=='1.0':
            while not self.Dispatcher.Stream.features and self.Process(): pass      # If we get version 1.0 stream the features tag MUST BE presented
            while self.SASL.startsasl=='in-process' and self.Process(): pass
        else: self.SASL.startsasl='failure'
        if self.SASL.startsasl=='failure': return auth.NonSASL(user,password,resource).PlugIn(self)
        else:
            auth.Bind().PlugIn(self)
            while self.Bind.bound is None: self.Process()
            return self.Bind.Bind(resource)

    def sendInitPresence(self,requestRoster=1):
        self.sendPresence(requestRoster=requestRoster)

    def sendPresence(self,jid=None,type=None,requestRoster=0):
        if requestRoster: roster.Roster().PlugIn(self)
        self.send(dispatcher.protocol.Presence(to=jid, type=type))

class Component(CommonClient):
    def auth(self,name,password):
        return auth.NonSASL(name,password,'').PlugIn(self)
