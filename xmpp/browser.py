##   browser.py
##
##   Copyright (C) 2004 Alexey "Snake" Nezhdanov
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

from dispatcher import *
from client import PlugIn

class Browser(PlugIn):
    def __init__(self):
        PlugIn.__init__(self)
        DBG_LINE='browser'
        self._exported_methods=[]
        self._handlers={}

    def plugin(self, owner):
        owner.RegisterHandler('iq',self._DiscoveryHandler,ns=NS_DISCO_INFO)
        owner.RegisterHandler('iq',self._DiscoveryHandler,ns=NS_DISCO_ITEMS)

    def plugout(self):
        self._owner.UnregisterHandler('iq',self._DiscoveryHandler,ns=NS_DISCO_INFO)
        self._owner.UnregisterHandler('iq',self._DiscoveryHandler,ns=NS_DISCO_ITEMS)

    def _traversePath(self,node,set=0):
        "Returns dictionary and key or None,None"
        "/a/b/c - node"
        "/a/b/  - branch"
        """ '' - handler for this branch
            1  - handler for this node
        """
        {'a':{1:handlerA,'':HandlerAdef},None:{1:handlerRoot}}
        "Set returns '' or None as the key "
        "get returns '' or None as the key or None as the dict"

        """
            1. set None   (root)
            2. set a      (node)
            3. set a/     (default)
            4. set a//    (illegal - case 3)
            5. set /      ([il]legal - like 3)

            6. get None   (root)
            7. get None   (non-existent)
            8. get a      (node)
            9. get a/b    (default)
           10. get c      (non-existent)
           11. get /      (illegal)
           12. get a/     (illegal)
           13. get a//    (illegal)
                """
        {None:{1:handlerRoot},'a':{1:handlerA, '':handlerAdef}}
        cur=self._handlers
        if not node: node=[None]
        else: node=node.split('/')
        for i in node:
            if i<>'' and cur.has_key[i]: cur=cur[i]     # CYCLE: 1e,2e,3e,6,8,9,12,13
            elif set and i<>'': cur[i]={}; cur=cur[i]   # CYCLE: 1n,2n,3n
            elif set or cur.has_key(''): return cur,''  # 3e,3n,7d,9,11,12,13
            else: return None,None                      # 7n,10
        if cur.has_key(1) or set: return cur,1          # 1e,1n,2e,2n,6,8
        raise "Corrupted data"

    def setDiscoHandler(self,Handler,node=''):
        node,key=self._traversePath(node,1)
        node[key]=Handler

    def getDiscoHandler(self,node=''):
        node,key=self._traversePath(node)
        if node: return node[key]

    def delDiscoHandler(self,node=''):
        node,key=self._traversePath(node)
        if node:
            handler=node[key]
            del node[key]
            return handler

    def _DiscoveryHandler(self,conn,request):
        node,key=self._traversePath(request.getQuerynode())
        if not node or not node[key]:
            return conn.send(Error(request,ERR_ITEM_NOT_FOUND))
        rep=request.buildReply('result')
        q=rep.getTag('query')
        if request.getQueryNS()==NS_DISCO_ITEMS:
            list=node[key]['items']
            # handler must return list: [{jid,action,node,name}]
            if type(list)<>type([]): list=list(conn,request,'items')
            for item in list: q.addChild('item',item)
        elif request.getQueryNS()==NS_DISCO_INFO:
            dict=node[key]['info']
            # handler must return dictionary:
            # {'ids':[{},{},{},{}], 'features':[fe,at,ur,es], 'xdata':DataForm}
            if type(dict)<>type({}): dict=dict(conn,request,'info')
            for id in dict['ids']: q.addChild('identity',id)
            for feature in dict['features']: q.addChild('feature',{'var':feature})
            if dict.has_key('xdata'): q.addChild(node=dict['xdata'])
        conn.send(rep)
        raise NodeProcessed
