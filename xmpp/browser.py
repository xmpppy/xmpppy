#!/usr/bin/python
##
##   browser.py
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

"""
Нам нужно обеспечить браузинг и регистрацию.
################# info #############################
<query node=''> # node optional
    <identity category='' name='' type='' />    # type optional
    <feature var='' />
</query>
################## items ######################
<query node=''> # node optional
    <item jid='' name='' node='' action='remove/update'/>       # только jid обязателен
</query>    
"""

NS_DISCO_INFO='http://jabber.org/protocol/disco#info'
NS_DISCO_ITEMS='http://jabber.org/protocol/disco#items'

class Browser:
    def __init__(self,host):
        pass
    def PlugIn(self,host):
        pass
    def requestInfo(self,host)