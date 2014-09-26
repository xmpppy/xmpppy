#!/usr/bin/python
# -*- coding: koi8-r -*-
from distutils.core import setup,sys
import os

if sys.version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

# Set proper release version in source code also!!!
setup(name='xmpppy',
      version='0.5.2',
      author='Cyril Peponnet',
      author_email='cyril@peponnet.fr',
      url='https://github.com/ArchipelProject/xmpppy',
      description='XMPP-IM-compliant library for jabber instant messenging.',
      long_description="""This library provides functionality for writing xmpp-compliant
clients, servers and/or components/transports.

It was initially designed as a \"rework\" of the jabberpy library but
has become a separate product no longer maintened by the previous author.
This is distributed under the terms of GPL.""",
      download_url='https://github.com/ArchipelProject/xmpppy/releases',
      package_dir={'xmpp': ''},
      packages=['xmpp'],
      license="GPL",
      platforms="All",
      keywords=['jabber','xmpp'],
      classifiers = [
          'Topic :: Communications :: Chat',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Natural Language :: English',
          'Development Status :: 5 - Production/Stable ',
          'Intended Audience :: Developers',
        ],
     )
