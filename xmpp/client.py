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
class Client:
    def __init__(self,server,debug=['socket']):#['always', 'nodebuilder']):
        self.disconnect_handlers=[]
        self.Namespace='jabber:client'
        self.Server=server
        self._DEBUG=Debug.Debug(debug)
        self.DEBUG=self._DEBUG.Show
        self.debug_flags=Debug.debug_flags
        self.debug_flags.append(DBG_CLIENT)
        self._owner=self

    def RegisterDisconnectHandler(self,handler):
        self.disconnect_handlers.append(handler)

    def DeregisterDisconnectHandler(self,handler):
        self.disconnect_handlers.remove(handler)

    def disconnected(self):
        self.DEBUG(DBG_CLIENT,'Disconnect detected','stop')
        self.disconnect_handlers.reverse()
        for i in self.disconnect_handlers: i()
        self.disconnect_handlers.reverse()

    def send_header(self):
        self.send("<?xml version='1.0'?><stream:stream version='1.0' xmlns:stream='http://etherx.jabber.org/streams' to='%s' xmlns='%s'>"%(self.Server,self.Namespace))

    def connect(self,proxy=None):
        if proxy: transports.HTTPPROXYsocket(proxy).PlugIn(self)
        else: transports.TCPsocket().PlugIn(self)
        dispatcher.Dispatcher().PlugIn(m)
        self.send_header()
        transports.TLS().PlugIn(self)
        while self.Process() and not self.Dispatcher.Stream._document_attrs: pass
        if self.Dispatcher.Stream._document_attrs.has_key('version') and self.Dispatcher.Stream._document_attrs['version']=='1.0':
            while self.Process() and not self.TLS.starttls: pass
        if self.TLS.starttls<>'proceed': self.disconnected()

    def auth(self,user,password,resource):
        auth.SASL(user,password).PlugIn(self)
        while self.Process() and not self.Dispatcher.Stream._document_attrs: pass
        if self.Dispatcher.Stream._document_attrs.has_key('version') and self.Dispatcher.Stream._document_attrs['version']=='1.0':
            while self.Process() and not self.SASL.startsasl: pass
        if self.SASL.startsasl<>'success': auth.NonSASL(user,password,resource).PlugIn(m)
        else:
            auth.Bind().PlugIn(self)
            self.Bind.Bind(resource)

    def sendInitPresence(self,requestRoster=1):
        self.sendPresence(requestRoster=requestRoster)

    def sendPresence(self,jid=None,type=None,requestRoster=0):
        if requestRoster: roster.Roster().PlugIn(m)
        self.send(dispatcher.protocol.Presence(to=jid, type=type))

test_client=1
if test_client:
    proxy={}
    proxy['host']='localhost'
    proxy['port']=8080
    proxy['user']='3128'
    proxy['password']='3128'
    m=Client('woody8.penza-gsm.ru')
    m.connect()
    #raise
    m.auth('test','test','test')
    m.sendInitPresence()
    if 1:
        m.Process(5)
        print m.Roster._data
    print discoverItems(m,'woody8.penza-gsm.ru')
    print discoverInfo(m,'woody8.penza-gsm.ru')
print getPrivacyLists(m)
print getPrivacyList(m,'a')
