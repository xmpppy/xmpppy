# -*- coding: utf-8 -*-
import xmpp
import argparse
"""
Synopsis::

    xmpp-message --debug \
        --jabberid foobar@xmpp.domain.tld --password secret \
        --receiver bazqux@xmpp.domain.tld --message '☠☠☠ hello world ☠☠☠'
"""


def send_message(jabberid, password, receiver, message, debug=False):

    if debug:
        debug = ['always']

    jid = xmpp.protocol.JID(jabberid)
    connection = xmpp.Client(server=jid.getDomain(), debug=debug)
    connection.connect()
    connection.auth(user=jid.getNode(), password=password, resource=jid.getResource())
    connection.send(xmpp.protocol.Message(to=receiver, body=message))


def simple_message():
    parser = argparse.ArgumentParser(description='Authenticate with XMPP server and send simple message')
    parser.add_argument('--jabberid', required=True, help='Jabber Identifier (JID) aka. username')
    parser.add_argument('--password', required=True, help='Password for Jabber Identifier (JID)')
    parser.add_argument('--receiver', required=True, help='Receiver address')
    parser.add_argument('--message', required=True, help='Message content')
    parser.add_argument('--debug', action='store_true', default=False, help='Enable debug messages')

    options = parser.parse_args()

    send_message(options.jabberid, options.password, options.receiver, options.message, debug=options.debug)
