######
xmpppy
######

    *Python 2/3 implementation of XMPP (RFC3920, RFC3921).*

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

*****
About
*****
This library has been written to be compliant with
`RFC3920 <https://datatracker.ietf.org/doc/rfc3920/>`_
and
`RFC3921 <https://datatracker.ietf.org/doc/rfc3921/>`_.


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
Regularly, the module is used as a library, like::

    jabberid = "foobar@xmpp.domain.tld"
    password = "secret"
    receiver = "bazqux@xmpp.domain.tld"
    message  = "hello world"

    jid = xmpp.protocol.JID(jabberid)
    connection = xmpp.Client(server=jid.getDomain(), debug=debug)
    connection.connect()
    connection.auth(user=jid.getNode(), password=password, resource=jid.getResource())
    connection.send(xmpp.protocol.Message(to=receiver, body=message))

However, the module also installs a basic example program called ``xmpp-message``,
which can be invoked from the command line. Its synopsis is::

    xmpp-message --debug \
        --jabberid foobar@xmpp.domain.tld --password secret \
        --receiver bazqux@xmpp.domain.tld --message 'hello world'


*************
Documentation
*************
For learning about how to use this module, please have a look at these spots.

- The ``xmpp/cli.py`` example program.
- The ``doc/examples`` directory.
  You might want to look at ``basic.py`` and ``demo.py`` first
  before investigating the other examples.
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



**************
Other projects
**************
- https://github.com/Jajcus/pyxmpp2
- https://github.com/fritzy/SleekXMPP
- https://dev.gajim.org/gajim/python-nbxmpp
