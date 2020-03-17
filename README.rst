######
xmpppy
######

    *Python 2/3 implementation of XMPP.*

----

**Documentation**: http://xmpppy.sf.net/

**Source Code**: https://github.com/xmpppy/xmpppy

**Status**:

.. image:: https://img.shields.io/badge/Python-2.7,%203.8-green.svg
    :target: https://github.com/xmpppy/xmpppy

.. image:: https://img.shields.io/pypi/v/xmpppy.svg
    :target: https://pypi.org/project/xmpppy/

.. image:: https://img.shields.io/github/tag/xmpppy/xmpppy.svg
    :target: https://github.com/xmpppy/xmpppy


----


************
Installation
************
If you are using Debian, you can simply run::

    apt-get install python-xmpp

Otherwise, you might want to use pip::

    pip install xmpppy


*****
Usage
*****
The module installs a basic example program called ``xmpp-message``.
The synopsis is::

    xmpp-message --debug \
        --jabberid foobar@jabber.example.org --password secret \
        --receiver bazqux@jabber.example.org --message '☠☠☠ hello world ☠☠☠'


*************
Documentation
*************
For learning about how to use this module, please have a look at these spots.

- The ``xmpp/cli.py`` example program.
- The ``doc/examples`` directory.
  The two most basic programs are ``README.py`` and ``xsend.py``.
- The HTML pages on http://xmpppy.sf.net/.
- The docstrings.


*******
Support
*******
If you have any questions about xmpppy usage or you have found a bug or want
to share some ideas - you are welcome to join us on the
`issue tracker <https://github.com/xmpppy/xmpppy/issues>`_
or on the
`xmpppy-devel mailing list <http://lists.sourceforge.net/lists/listinfo/xmpppy-devel>`_.
