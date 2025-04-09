#!/usr/bin/python3

import os, xmpp, sys

server = os.environ['XMPP_SERVER']
username = os.environ['XMPP_USER']
fullname = f'{username}@{server}'
password = os.environ['XMPP_PW']
chatroom = os.environ['XMPP_CHATROOM']  # must be channel@conferenceserver.example.com


jid = xmpp.protocol.JID(fullname)
cl = xmpp.Client(jid.getDomain(),debug=[])
con = cl.connect()
if not con:
    print('could not connect!')

auth = cl.auth(jid.getNode(), password, resource=jid.getResource())
if not auth:
    print('could not authenticate!')

def handler(session, message):
    if message.getType() == 'error':
        print(f'{message!s}', file=sys.stderr)

cl.RegisterHandler('default', handler)

# https://xmpp.org/extensions/xep-0045.html#enter-muc
sent = cl.send(xmpp.protocol.Presence(to=f'{chatroom}/{username}', payload=[xmpp.Protocol(name='x', xmlns='http://jabber.org/protocol/muc')]))
print('sent presence with id', sent)
cl.Process(1) # process answer from server

# https://xmpp.org/extensions/xep-0045.html#message
sent = cl.send(xmpp.protocol.Message('{chatroom}', 'test', typ='groupchat', xmlns=None, attrs={'from':f'{fullname}/xmpppy'}))
print('sent message with id', sent)
cl.Process(1)
