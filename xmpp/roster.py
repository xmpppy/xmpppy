##   roster.py
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

import protocol
from client import PlugIn

NS_ROSTER     = "jabber:iq:roster"

class Roster(PlugIn):
    def __init__(self):
        PlugIn.__init__(self)
        self.DBG_LINE='roster'
        self._data = {}

    def plugin(self,owner,request=1):
        self._owner.RegisterHandler('iq',self.RosterIqHandler,'result',NS_ROSTER)
        self._owner.RegisterHandler('iq',self.RosterIqHandler,'set',NS_ROSTER)
        self._owner.RegisterHandler('presence',self.PresenceHandler)
        if request: self.Request()

    def Request(self):
        self._owner.send(protocol.Iq('get',NS_ROSTER))
        self.DEBUG('Roster requested from server','start')

    def RosterIqHandler(self,dis,stanza):
        for item in stanza.getTag('query').getTags('item'):
            jid=item.getAttr('jid')
            self.DEBUG('Setting roster item %s...'%jid,'ok')
            if not self._data.has_key(jid): self._data[jid]={}
            self._data[jid]['name']=item.getAttr('name')
            self._data[jid]['ask']=item.getAttr('ask')
            self._data[jid]['subscription']=item.getAttr('subscription')
            self._data[jid]['groups']=[]
            if not self._data[jid].has_key('resources'): self._data[jid]['resources']={}
            for group in item.getTags('group'): self._data[jid]['groups'].append(group.getData())
        self._data[self._owner.User+'@'+self._owner.Server]={'resources':{}}

    def PresenceHandler(self,dis,pres):
        JID=protocol.JID(pres.getFrom())
        if not self._data.has_key(JID.getStripped()): self._data[JID.getStripped()]={'name':None,'ask':None,'subscription':'none','groups':['Not in roster'],'resources':{}}

        item=self._data[JID.getStripped()]
        typ=pres.getType()

        if not typ:
            if not item['resources'].has_key(JID.getResource()): item['resources'][JID.getResource()]={'show':None,'status':None,'priority':'0','timestamp':None}
            self.DEBUG('Setting roster item %s for resource %s...'%(JID.getStripped(),JID.getResource()),'ok')
            res=item['resources'][JID.getResource()]
            if pres.getTag('show'): res['show']=pres.getShow()
            if pres.getTag('status'): res['status']=pres.getStatus()
            if pres.getTag('priority'): res['priority']=pres.getPriority()
            if not pres.getTimestamp(): pres.setTimestamp()
            res['timestamp']=pres.getTimestamp()

        elif typ=='unavailable' and item['resources'].has_key(JID.getResource()): del item['resources'][JID.getResource()]
# Надо ещё обработать type='error'
    def _getItemData(self,jid,dataname):
        jid=jid[:(jid+'/').find('/')]
        return self._data[jid][dataname]
    def _getResourceData(self,jid,dataname):
        if jid.find('/')+1:
            jid,resource=jid.split('/')
            if self._data[jid]['resources'].has_key(resource): return self._data[jid]['resources'][resource][dataname]
        elif self._data[jid]['resources'].keys():
            lastpri=-129
            for r in self._data[jid]['resources'].keys():
                if int(self._data[jid]['resources'][r]['priority'])>lastpri: resource,lastpri=r,int(self._data[jid]['resources'][r]['priority'])
            return self._data[jid]['resources'][resource][dataname]
    def delItem(self,jid): self._owner.send(protocol.Iq('set',NS_ROSTER,payload=[Node('item',{'jid':jid,'subscription':'remove'})]))
    def getAsk(self,jid): return self._getItemData(jid,'ask')
    def getGroups(self,jid): return self._getItemData(jid,'groups')
    def getName(self,jid): return self._getItemData(jid,'name')
    def getPriority(self,jid): return self._getResourceData(jid,'priority')
    def getRawRoster(self): return self._data
    def getRawItem(self,jid): return self._data[jid[:(jid+'/').find('/')]]
    def getShow(self, jid): return self._getResourceData(jid,'show')
    def getStatus(self, jid): return self._getResourceData(jid,'status')
    def getSubscription(self,jid): return self._getItemData(jid,'subscription')
    def getResources(self,jid): return self._data[jid[:(jid+'/').find('/')]]['resources'].keys()
    def setItem(self,jid,name=None,groups=None):
        iq=protocol.Iq('set',NS_ROSTER)
        attrs={'jid':jid}
        if name: attrs['name']=name
        iq.setTag('item',attrs)
        for group in groups: iq.addChild(node=Node('group',payload=[group]))
        self._owner.send(iq)
    def Subscribe(self,jid): self._owner.send(protocol.Presence(jid,'subscribe'))
    def Unsubscribe(self,jid): self._owner.send(protocol.Presence(jid,'unsubscribe'))
    def Authorize(self,jid): self._owner.send(protocol.Presence(jid,'subscribed'))
    def Unauthorize(self,jid): self._owner.send(protocol.Presence(jid,'unsubscribed'))
