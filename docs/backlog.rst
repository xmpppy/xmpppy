#####
About
#####

************
Introduction
************
This is my work to replace the jabberpy with the current and maintained
project.

Now, the project nears feature freeze of 0.2 branch. Almost all goals are
achieved already. Though the main goal was to write a documentation - at least
a line for every feature of library. Yesterday I have checked in last docstrings
for all yet undocumented modules and now I can say that this issue is resolved
(at least for 0.2 release level).

Documentation exists in three formats.

- The first is the examples that I wrote to show xmpppy in action. This is
  two simple scripts - ``README.py`` and ``xsend.py``.
- The second is the html pages where I try to describe the idea of library
  and the ways the goals are achieved.
- Third is the docstrings. I am currently using epydoc but other tools
  should work too (at least the pydoc works)

************
Installation
************
If you are using Debian (sarge or above) you can simply run::

    apt-get install python-xmpp

and you will get the current stable release of xmpppy installed. After installation,
you can do 'import xmpp'. Though currently debian contains 0.1 release of xmpppy so
if you want to use 0.2 branch you should install it manually (python2.3 required).
Here you have several options:

- run 'python setup.py install' from xmpppy distribution as root.
  All should work nice.
- if you don't like python installator - just copy xmpp directory into python's
  site-packages directory (this is what setup.py does).
- If you have no intention to install library system-wide (or just have no
  privileges to do it) you can copy xmpp directory just in your application's
  directory. Example::

        myxmpppytry/
            xmpp/
                ...xmpppy modules
            test.py


-- 2004.12.26, Alexey Nezhdanov



#####
Notes
#####

Before 0.2 release:

- Adapt and integrate Commands module.
- Ensure that all docstrings are in place.
- Add SI to filetransfer
- Evaluate about namespace separation in dispatcher.
- S&D memory leak (cvs diff -r 1.26 -r 1.25 simplexml.py | patch && apt-get install python2.2 && /usr/sbin/jabber-irc)
- Regenerate documentation
- Add client mode detection to Browser class.
- Commands: auto-add commands item
- Fix TLS/TCP issue by deleting transports.receive and staring over.
- Add keepalive mechanism.
- Decide if gajim changeset 2659 (input chunking) can go in or not. They notices that is slows things but it really should not...
- Investigate http://trac.gajim.org/ticket/676 problem. We should fix - but not workaround it.
- If auth fails because connection was not connected, unplug correctly and/or return gracefully
- If IOException during dispatcher.process then return 0 instead of None

After 0.6.0 release:

- [x] Retroactively add changelog.
- [o] Integrate documentation about alternative installation variants. Add note about virtualenv and pipx.
- [o] Add more example programs as command line entrypoints.
- [o] Update documentation files ``doc/*.html``
- [o] Documentation: Add note about installing DNS libraries (dnspython or pydns) for querying SRV records.
