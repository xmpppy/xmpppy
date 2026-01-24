######
xmpppy
######

.. image:: https://img.shields.io/pypi/pyversions/xmpppy.svg
    :target: https://pypi.org/project/xmpppy/

.. image:: https://img.shields.io/pypi/v/xmpppy.svg
    :target: https://pypi.org/project/xmpppy/

.. image:: https://img.shields.io/pypi/l/xmpppy.svg
    :target: https://pypi.org/project/xmpppy/

.. image:: https://img.shields.io/pypi/dm/xmpppy.svg
    :target: https://pypi.org/project/xmpppy/

.. image:: https://img.shields.io/pypi/status/xmpppy.svg
    :target: https://pypi.org/project/xmpppy/

.. image:: https://github.com/xmpppy/xmpppy/actions/workflows/tests.yml/badge.svg
    :target: https://github.com/xmpppy/xmpppy/actions/workflows/tests.yml

.. image:: https://img.shields.io/codecov/c/gh/xmpppy/xmpppy.svg
    :target: https://codecov.io/gh/xmpppy/xmpppy/

|

:About: Python 2/3 implementation of XMPP
:Standards: `RFC3920`_, `RFC3921`_
:Documentation: https://xmpppy.sourceforge.net/
:Source Code: https://github.com/xmpppy/xmpppy


************
Installation
************

Using ``pip``, you can install the package with::

    pip install --upgrade xmpppy


*****
Usage
*****

As a library
============

Regularly, the module is used as a library, like::

    import xmpp

    jabberid = "foobar@xmpp.domain.tld"
    password = "secret"
    receiver = "bazqux@xmpp.domain.tld"
    message  = "hello world"

    def main():
        jid = xmpp.protocol.JID(jabberid)
        connection = xmpp.Client(server=jid.getDomain(), debug=True)
        connection.connect()
        connection.auth(user=jid.getNode(), password=password, resource=jid.getResource())
        connection.send(xmpp.protocol.Message(to=receiver, body=message))

    if __name__ == "__main__":
        main()


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

- The ``xmpp-message`` program, located at ``xmpp/cli.py``, for sending a single XMPP message.
- The other programs within the ``doc/examples`` directory.
- The docstrings within the library itself.


***********
Development
***********

::

    git clone https://github.com/xmpppy/xmpppy
    cd xmpppy
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --editable='.[test]' --upgrade


**************
Software tests
**************

::

    pip install -r requirements-test.txt
    docker compose --file tests/compose.yml up
    pytest


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


.. _RFC3920: https://datatracker.ietf.org/doc/rfc3920/
.. _RFC3921: https://datatracker.ietf.org/doc/rfc3921/
