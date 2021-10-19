# -*- coding: utf-8 -*-
import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

# Set proper release version in source code also!!!
setup(name='xmpppy',
      version='0.6.4',
      author='Alexey Nezhdanov',
      author_email='snakeru@users.sourceforge.net',
      url='http://xmpppy.sourceforge.net/',
      description='XMPP implementation in Python',
      long_description=README,
      download_url='https://pypi.org/project/xmpppy/',
      packages=['xmpp'],
      license="GPL",
      platforms="All",
      keywords=['jabber', 'xmpp', 'RFC3920', 'RFC3921'],
      classifiers = [
          "Programming Language :: Python",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Development Status :: 4 - Beta",
          "Operating System :: OS Independent",
          "Natural Language :: English",
          "Intended Audience :: Developers",
          "Intended Audience :: Education",
          "Intended Audience :: Information Technology",
          "Intended Audience :: System Administrators",
          "Intended Audience :: Telecommunications Industry",
          "Topic :: Communications",
          "Topic :: Communications :: Chat",
          "Topic :: Database",
          "Topic :: Internet",
          "Topic :: Software Development :: Libraries",
          "Topic :: System :: Networking",
          "Topic :: Text Processing",
          "Topic :: Utilities",
        ],
      entry_points={
          'console_scripts': [
              'xmpp-message = xmpp.cli:simple_message',
          ],
      },
  )
