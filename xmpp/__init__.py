# $Id$

for m in ['simplexml','protocol','debug','auth','transports','roster','dispatcher','features']:
    exec 'import '+m
    md=locals()[m].__dict__
    for var in md.keys():
        if var[:3]=='NS_': locals()[var]=md[var]

from client import *
