# $Id$

"""
All features of xmpppy library contained within separate modules.
At present there are modules:
simplexml - XML handling routines
protocol - jabber-objects (I.e. JID and different stanzas and sub-stanzas) handling routines.
debug - Jacob Lundquist's debugging module. Very handy if you like colored debug.
auth - Non-SASL and SASL stuff. You will need it to auth as a client or transport.
transports - low level connection handling. TCP and TLS currently. HTTP support planned.
roster - simple roster for use in clients.
dispatcher - decision-making logic. Handles all hooks. The first who takes control over fresh stanzas.
features - different stuff that didn't worths separating into modules
browser - DISCO server framework. Allows to build dynamic disco tree.
filetransfer - Currently contains only IBB stuff. Can be used for bot-to-bot transfers.
"""

import simplexml,protocol,debug,auth,transports,roster,dispatcher,features,browser,filetransfer
from client import *
from protocol import *
