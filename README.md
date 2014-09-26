### Introduction to xmpppy

This is my work to fork http://xmpppy.sf.net/ with the current and maintained project.

This library has been written to be [RFC3920](https://datatracker.ietf.org/doc/rfc3920/) and [RFC3921](https://datatracker.ietf.org/doc/rfc3921/) compliant.

### Documentation

Documentation exists in three formats.
* The first is the examples that written to show xmpppy in action you can find in the wiki
* The second is the wiki pages where describing the idea of library and the ways the goals are achieved.
* Third is the docstrings. Using epydoc (epydoc -o doc/api --name xmpppy --inheritance listed --graph all xmpp) and located here: http://archipelproject.github.io/xmpppy/

### Installation

Here you have several options:
  * run pip install git+https://github.com/ArchipelProject/xmpppy
  * run 'python setup.py install' from xmpppy distribution as root.
  * if you don't like python installator - just copy xmpp directory into python's site-packages directory (this is what setup.py does).
  * If you have no intention to install library system-wide (or just have no privileges to do it) you can copy xmpp directory just in your application's directory. Example:

```
 myxmpppytry/
            xmpp/
                ...xmpppy modules
            test.py
```

If you have any questions about xmpppy usage or you have find a bug or want
to share some ideas - you are welcome on github

2014.09.21                  Cyril Peponnet
