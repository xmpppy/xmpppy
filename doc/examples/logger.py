#!/usr/bin/python
from xmpp import *
import time,os

#BOT=(botjid,password)
BOT=('test@penza-gsm.ru','test')
#CONF=(confjid,password)
CONF=('talks@conference.jabber.ru','')
LOGDIR='./'
PROXY={}
#PROXY={'host':'192.168.0.1','port':3128,'username':'luchs','password':'secret'}
#######################################

def LOG(fold,day,tm,nick,text):
    try: os.mkdir(LOGDIR+fold)
    except: pass
    fName='%s%s/%s.%s.html'%(LOGDIR,fold,fold,day)
    try: open(fName)
    except:
        open(fName,'w').write("""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xml:lang="ru-RU" lang="ru-RU" xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <meta content="text/html; charset=utf-8" http-equiv="content-type" />
        <title>%s logs for %s.%s.</title>
    </head>
    <body>
<table border="1"><tr><th>time</th><th>who</th><th>text</th></tr>
"""%(CONF[0],fold,day))
    open(fName,'a').write((u"<tr><td>%s</td><td>%s</td><td>%s</td></tr>\n"%(tm,nick,text)).encode('utf-8'))
    print u"<tr><td>%s</td><td>%s</td><td>%s</td></tr>\n"%(tm,nick,text)
#    print time.localtime(tp),nick,text

def messageCB(sess,mess):
    nick=mess.getFrom().getResource()
    text=mess.getBody()
    ts=mess.getTimestamp()
    if not ts:
        ts=mess.setTimestamp()
        ts=mess.getTimestamp()
    tp=time.mktime(time.strptime(ts,'%Y%m%dT%H:%M:%S %Z'))+3600*3
    if time.localtime()[-1]: tp+=3600
    tp=time.localtime(tp)
    fold=time.strftime("%Y.%m",tp)
    day=time.strftime("%d",tp)
    tm=time.strftime("%H:%M:%S",tp)
    line="<tr><td>%s</td><td>%s<td>"%(tm,text)
    LOG(fold,day,tm,nick,text)

if 1:
    cl=Client(JID(BOT[0]).getDomain(),debug=[])
    cl.connect(PROXY)
    cl.RegisterHandler('message',messageCB)
    cl.auth(JID(BOT[0]).getNode(),BOT[1])
    p=Presence(to='%s/logger'%CONF[0])
    p.setTag('x',namespace=NS_MUC).setTagData('password',CONF[1])
    p.getTag('x').addChild('history',{'maxchars':'0','maxstanzas':'0'})
    cl.send(p)
    while 1:
        cl.Process(1)
