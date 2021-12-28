# -*- coding: utf-8 -*-
import os
import sys
from collections import OrderedDict

import xmpp
import argparse
"""
Synopsis::

    xmpp-message --debug \
        --jabberid foobar@xmpp.domain.tld --password secret \
        --receiver bazqux@xmpp.domain.tld --message '☠☠☠ hello world ☠☠☠'
"""


def send_message(jabberid, password, receiver, message, debug=False):
    """
    Connect to XMPP server and send message.
    """
    if debug:
        debug = ['always']

    jid = xmpp.protocol.JID(jabberid)
    connection = xmpp.Client(server=jid.getDomain(), debug=debug)
    connection.connect()
    retval = connection.auth(user=jid.getNode(), password=password, resource=jid.getResource())
    if retval is None:
        sys.stderr.write("ERROR: Authentication failed\n")
        sys.exit(1)
    connection.send(xmpp.protocol.Message(to=receiver, body=message))


def read_xsend():
    """
    Read credentials from `~/.xsend` file.
    """
    params = OrderedDict()
    xsendfile = os.path.join(os.environ['HOME'], '.xsend')
    with open(xsendfile, "r") as f:
        for ln in f.readlines():
            ln = ln.strip()
            if not ln:
                continue
            if ln[0] not in ('#', ';'):
                key, val = ln.split('=', 1)
                params[key.lower()] = val
    return params


def simple_message():
    """
    Send an XMPP message from the command line.
    """
    parser = argparse.ArgumentParser(description='Authenticate with XMPP server and send simple message')
    parser.add_argument('--jabberid', required=False, help='Jabber Identifier (JID) aka. username')
    parser.add_argument('--password', required=False, help='Password for Jabber Identifier (JID)')
    parser.add_argument('--receiver', required=True, help='Receiver address')
    parser.add_argument('--message', required=True, help='Message content')
    parser.add_argument('--debug', action='store_true', default=False, help='Enable debug messages')

    options = parser.parse_args()

    # Optionally, read credentials from `~/.xsend` file.
    if options.jabberid is None:
        try:
            params = read_xsend()
        except Exception as ex:
            sys.stderr.write("ERROR: Unable to read credentials from ~/.xsend file: %s\n" % ex)
            sys.exit(1)
        options.jabberid = params["jid"]
        options.password = params["password"]

    send_message(options.jabberid, options.password, options.receiver, options.message, debug=options.debug)
