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
import sha

NS_AUTH="jabber:iq:auth"

DBG_AUTH='auth'
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
            return 1
        owner.DEBUG(DBG_AUTH,'Authentication failed!','error')
