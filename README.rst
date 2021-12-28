######
xmpppy
######

    *Python 2/3 implementation of XMPP (RFC3920, RFC3921).*

----

**Documentation**: http://xmpppy.sf.net/

**Source Code**: https://github.com/xmpppy/xmpppy

**Status**:

.. image:: https://img.shields.io/pypi/pyversions/xmpppy.svg
    :target: https://pypi.org/project/xmpppy/

.. image:: https://img.shields.io/pypi/v/xmpppy.svg
    :target: https://pypi.org/project/xmpppy/

.. image:: https://img.shields.io/pypi/l/xmpppy.svg
    :target: https://pypi.org/project/xmpppy/

.. image:: https://img.shields.io/pypi/dm/xmpppy.svg
    :target: https://pypi.org/project/xmpppy/


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

Using ``pip``, you can install the package with::

    pip install xmpppy --upgrade


*****
Usage
*****

As a library
============

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


Command line interface
======================

The package also installs a command line program called ``xmpp-message``.
Its synopsis is::

    xmpp-message --debug \
        --jabberid foobar@xmpp.domain.tld --password secret \
        --receiver bazqux@xmpp.domain.tld --message 'hello world'

You can also put your credentials into an ``~/.xsend`` file, like::

    JID=foobar@xmpp.domain.tld
    PASSWORD=secret

and then invoke ``xmpp-message`` omitting the ``--jabberid`` and ``--password`` options, like::

    xmpp-message --receiver bazqux@xmpp.domain.tld --message 'hello world'


*************
Documentation
*************

The canonical documentation is hosted at https://xmpppy.github.io/ and
http://xmpppy.sourceforge.net/.

For learning about how to use this module, please have a look at these spots
within the code base.

- The ``xmpp/cli.py`` example program.
- The ``doc/examples`` directory.
  You might want to look at ``basic.py`` and ``demo.py`` first
  before investigating the other examples.
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
- https://github.com/poezio/slixmpp
- https://github.com/horazont/aioxmpp
- https://github.com/Jajcus/pyxmpp2
- https://github.com/fritzy/SleekXMPP
- https://dev.gajim.org/gajim/python-nbxmpp
- https://github.com/xmpppy/xmpppy/files/4346179/xmpp_libs.xlsx
