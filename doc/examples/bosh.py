#!/usr/bin/env python
"""
Simple BOSH Bot Example
"""
import sys
import xmpp
from xmpp.transports import Bosh
from urllib2 import urlparse

def showhelp(*args):
    tpl = """
 Simple BOSH Bot Example

   bosh.py USERNAME PASSWORD ENDPOINT [Options] -r|--resource RESOURCE

 Required Arguments:

   USERNAME    A Username to authenticate with.

               Current: {0}

   PASSWORD    A passowd to authenticate with.

               Current: {1}

   ENDPOINT    The BOSH endpoint Url.

               Current: {2}

 Options:

  -r|--resource RESOURCE  Set the resource name that will be used

                   Current: {3}

  -h|--help Show Help

"""
    print tpl.format(*args)

def connect(username, password, resource,  server='', port='', bosh='', use_srv=False):
    """
    The only thing of much substance here, this connect method demonstrates how
    to create an xmpp client using the BOSH transport.
    """
    transport = None
    url = urlparse.urlparse(bosh)
    if bosh:
        transport = Bosh(bosh, server=server, port=port, use_srv=use_srv)
    server = server or url.hostname
    port = port or 5522
    con = xmpp.Client(server, port)
    con.connect(transport=transport)
    con.auth(username, password, resource)
    return con

def message(con, stanze):
    print stanze
    return stanze

def step(conn):
    try:
        i = conn.Process(1)
        if not i:
            return 1
    except KeyboardInterrupt:
        return 0
    return 1

def main(conn):
    while step(conn): pass

if __name__ == '__main__':
    args = sys.argv[1:]
    resource = 'simplebot'
    help = False
    username = ''
    password = ''
    endpoint = ''
    positionals = []
    while args:
        arg = args.pop(0)
        if arg in ['-r', '--resource']:
            resource = args.pop(0)
            continue
        if arg in ['-h', '--help']:
            help = True
            continue
        if not arg.startswith('-'):
            if len(positionals) == 0:
                username = arg
            elif len(positionals) == 1:
                password = arg
            elif len(positionals) == 2:
                endpoint = arg
            positionals.append(arg)
            continue
    if help:
        showhelp(username, password, endpoint, resource)
        sys.exit(0)
    assert username and password and endpoint, \
        'username, password, and endpoint required'
    c = connect(username, password, resource, bosh=endpoint)
    c.RegisterHandler('message', message)
    c.sendInitPresence()
    main(c)
