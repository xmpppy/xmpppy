import pytest
from xmpp.protocol import *


class Test_JID():
    
    def test_equality(self):
        assert 'me@myserver/res' == JID('me@myserver/res')
    def test_1(self):
        jid = JID('audiod/Jcop')
        assert jid.getDomain() == ''
        assert jid.getNode() == 'audiod'
        assert jid.getResource() == 'Jcop'

    def test_2(self):
        jid = JID('audiod@ics/Jcop')
        assert jid.getDomain() == 'ics'
        assert jid.getNode() == 'audiod'
        assert jid.getResource() == 'Jcop'

    def test_3(self):
        jid = JID('audiod')
        assert jid.getDomain() == ''
        assert jid.getNode() == 'audiod'
        assert jid.getResource() == ''

    def test_4(self):
        jid = JID('audiod@ics')
        assert jid.getDomain() == 'ics'
        assert jid.getNode() == 'audiod'
        assert jid.getResource() == ''


t = Test_JID()
t.test_equality()
