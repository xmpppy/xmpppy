##   simplexml.py based on Mattew Allum's xmlstream.py
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

import xml.parsers.expat

def XMLescape(txt):
    "Escape XML entities"
    txt = txt.replace("&", "&amp;")
    txt = txt.replace("<", "&lt;")
    txt = txt.replace(">", "&gt;")
    return txt

def XMLunescape(txt):
    "Unescape XML entities"
    txt = txt.replace("&gt;", ">")
    txt = txt.replace("&lt;", "<")
    txt = txt.replace("&amp;", "&")
    return txt

ENCODING='utf-8'
def ustr(what):
    if type(what) == type(u''): return what
    try: r=what.__str__()
    except AttributeError: r=str(what)
    if type(r)<>type(u''): return unicode(r,ENCODING)
    return r
    
class Node:
    def __init__(self, tag=None, attrs={}, payload=[], parent=None, node=None):
        if node:
            if type(node)<>type(self): node=NodeBuilder(node).getDom()
            self.name,self.namespace,self.attrs,self.data,self.kids,self.parent = node.name,node.namespace,node.attrs,node.data,node.kids,node.parent
        else: self.name,self.namespace,self.attrs,self.data,self.kids,self.parent = 'tag','',{},[],[],None

        if tag: self.namespace, self.name = (['']+tag.split())[-2:]
        if parent: self.parent = parent
        if self.parent and not self.namespace: self.namespace=self.parent.namespace
        for attr in attrs.keys():
            self.attrs[attr]=attrs[attr]
        for i in payload:
            if type(i)==type(self): self.addChild(node=i)
            else: self.data.append(i)
    def __str__(self,parent=None):
        s = "<" + self.name  
        if self.namespace:
            if parent and parent.namespace!=self.namespace:
                s = s + " xmlns='%s'"%self.namespace
        for key in self.attrs.keys():
            val = ustr(self.attrs[key])
            s = s + " %s='%s'" % ( key, XMLescape(val) )
        s = s + ">"
        cnt = 0 
        if self.kids != None:
            for a in self.kids:
                if (len(self.data)-1) >= cnt: s = s + XMLescape(self.data[cnt])
                s = s + a.__str__(self)
                cnt=cnt+1
        if (len(self.data)-1) >= cnt: s = s + XMLescape(self.data[cnt])
        if not self.kids and s[-1:]=='>':
            s=s[:-1]+' />'
        else:
            s = s + "</" + self.name + ">"
        return s
    def addChild(self, name=None, attrs={}, payload=[], namespace=None, node=None):
        if namespace: name=namespace+' '+name
        newnode = Node(tag=name, parent=self, attrs=attrs, payload=payload, node=node)
        self.kids.append(newnode)
        return newnode
    def addData(self, data): self.data.append(data)
    def clearData(self): self.data=[]
    def delAttr(self, key): del self.attrs[key]
    def delChild(self, node, attrs={}):
        if type(node)<>type(self): node=self.getTag(node,attrs)
        self.kids.remove(node)
        return node
    def getAttrs(self): return self.attrs
    def getAttr(self, key):
        try: return self.attrs[key]
        except: return None
    def getChildren(self): return self.kids
    def getData(self): return ''.join(self.data)
    def getName(self): return self.name
    def getNamespace(self): return self.namespace
    def getParent(self): return self.parent
    def getPayload(self): return self.kids
    def getTag(self, name, attrs={}, namespace=None): return self.getTags(name, attrs, namespace, one=1)
    def getTagAttr(self,tag,attr):
        try: return self.getTag(tag).attrs[attr]
        except: return None
    def getTagData(self,tag):
        try: return self.getTag(tag).getData()
        except: return None
    def getTags(self, name, attrs={}, namespace=None, one=0):
        nodes=[]
        for node in self.kids:
            if namespace and namespace<>node.getNamespace(): continue
            if node.getName() == name:
                for key in attrs.keys():
                   if not node.attrs.has_key(key) or node.attrs[key]<>attrs[key]: break
                else: nodes.append(node)
            if one and nodes: return nodes[0]
        if not one: return nodes
    def setAttr(self, key, val): self.attrs[key]=val
    def setData(self, data): self.data=[data]
    def setName(self,val): self.name = val
    def setNamespace(self, namespace): self.namespace=namespace
    def setParent(self, node): self.parent = node
    def setPayload(self,payload,add=0):
        if add: self.kids+=payload
        else: self.kids=payload
    def setTag(self, name, attrs={}, namespace=None):
        node=self.getTags(name, attrs, namespace=namespace, one=1)
        if node: return node
        else: return self.addChild(name, attrs, namespace=namespace)
    def setTagAttr(self,tag,attr,val):
        try: self.getTag(tag).attrs[attr]=val
        except: self.addChild(tag,attrs={attr:val})
    def setTagData(self,tag,val,attrs={}):
        try: self.getTag(tag,attrs).setData(val)
        except: self.addChild(tag,attrs,payload=[val])

DBG_NODEBUILDER = 'nodebuilder'
class NodeBuilder:
    """builds a 'minidom' from data parsed to it. Primarily for insertXML
       method of Node"""
    def __init__(self,data=None):
        self.DEBUG(DBG_NODEBUILDER, "Preparing to handle incoming XML stream.", 'start')
        self._parser = xml.parsers.expat.ParserCreate(namespace_separator=' ')
        self._parser.StartElementHandler  = self.starttag
        self._parser.EndElementHandler    = self.endtag
        self._parser.CharacterDataHandler = self.handle_data
        self.Parse = self._parser.Parse

        self.__depth = 0
        self._dispatch_depth = 1
        self._document_attrs = None
        
        if data: self._parser.Parse(data,1)

    def starttag(self, tag, attrs):
        """XML Parser callback"""
        self.__depth += 1
        self.DEBUG(DBG_NODEBUILDER, "DEPTH -> %i , tag -> %s, attrs -> %s" % (self.__depth, tag, `attrs`), 'down')
        if self.__depth == self._dispatch_depth:
            self._mini_dom = Node(tag=tag, attrs=attrs)
            self._ptr = self._mini_dom
        elif self.__depth > self._dispatch_depth:
            self._ptr.kids.append(Node(tag=tag,parent=self._ptr,attrs=attrs))
            self._ptr = self._ptr.kids[-1]
        if self.__depth == 1:
            self._document_attrs = attrs
        self.last_is_data = 0

    def endtag(self, tag ):
        """XML Parser callback"""
        self.DEBUG(DBG_NODEBUILDER, "DEPTH -> %i , tag -> %s" % (self.__depth, tag), 'up')
        if self.__depth == self._dispatch_depth:
            self.dispatch(self._mini_dom)
        elif self.__depth > self._dispatch_depth:
            self._ptr = self._ptr.parent
        else:
            self.DEBUG(DBG_NODEBUILDER, "Got higher than dispatch level. Stream terminated?", 'stop')
        self.__depth -= 1
        self.last_is_data = 0

    def handle_data(self, data):
        """XML Parser callback"""
        self.DEBUG(DBG_NODEBUILDER, data, 'data')
        if self.last_is_data:
            self._ptr.data[-1] += data
        else:
            self._ptr.data.append(data)
            self.last_is_data = 1

    def DEBUG(self, level, text, comment=None): pass
    def getDom(self): return self._mini_dom
    def dispatch(self,stanza): pass

def XML2Node(xml): return NodeBuilder(xml).getDom()
