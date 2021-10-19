################
xmpppy changelog
################


in progress
===========


2021-10-19 0.6.4
================
- Python 3: Fix handling of ``socket.error``/``OSError`` exceptions


2021-09-14 0.6.3
================
- Improve compatibility with Python 3 within authentication subsystem
- Improve exception handling
- Remove special characters from README.rst to make installation on Windows easier


2020-11-12 0.6.2
================
- Use modern base64 interface (base64.b64encode/decode). Thanks, @rogue73!
  This adds compatibility with Python 3.9,
  but still retains compatibility with Python 2.7.


2020-03-28 0.6.1
================
- Add library usage example to README
- Retroactively add changelog
- Improve documentation
- Remove print statement. Thanks, @clarkspark!


2020-03-17 0.6.0
================
- Use setuptools instead of distutils like a modern python library
- Move "ietf-docs" to "doc" directory
- Adjust .gitignore
- Move TODO file to doc/backlog.txt
- Fix TLS with newer Python.
- Add program "xmpp-message" for sending a basic XMPP message
- Attempt to convert to python3
- Backwards compatibility for Python2
- More Python 3
- Improve documentation
- Add LICENSE file


2015-08-28 0.5.x
================
- Remove unused calls.
- Bump revision no
- transport.py: remove obsolete issuer()/server()
- http proxy server resolve bug
- http proxy server bug using srv lookup
- Merge pull request #22 from destroy/master
- Merge pull request #20 from Mic92/patch-1
- Merge pull request #15 from mpasternak/master
- Merge pull request #14 from dwoz/bosh


2013-12-20 0.5.x
================
- Add Bosh transport
- Adding a BoshClient class
- Patches to SASL and Dispatcher for BOSH support
- Different bug fixes
- Much less intrusive BOSH transport implimentation
- Less intrusive diff to main branch
- Clean cruft form pipelining attempt
- Add comment about possible breakage
- Distinguish host/port of endpoint and server
- Cleanup TODOs, fix typos.
- Add a simple BOSH client example
- Document the only useful stuff
- No longer storing a single class level connection
- Add HTTP pipelining support
- Clean up some minor annoyances
- Add gzip support to BOSH transport
- Connections are tracked in the trasport now
- Referencing BOSH session not a connection
- Better handling of invalid responses


2013-09-26 0.5.x
================
- Corrected a little typo
- Merge pull request #13 from iamsudip/typo
- Merge pull request #10 from ivucica/FixCommandsForUnicodeJids


2013-04-11 0.5.x
================
- Crashfix: 'From' jid w/ non-ASCII char sending cmd


2012-10-12 0.5.x
================
- Fixed sorting records (DNSPYTHON)
- Merge pull request #9 from provonet/master


2011-06-04 0.5.x
================
- Log all SSL_ERROR_WANT's and handle them during write.
- Turn string exceptions into Exceptions
- Fix up multiple receives
- Remove trailing spaces and convert tabs to 4 spaces
- Remove bashism from debian/rules.
- Make apidocs when building a debian package.
- Don't install ChangeLog in debian package.
- Add .gitignore.
- Debian package: Recommend python-dnspython.
- Bump version for the debian package.
- Support connections to IPv6 servers.


2011-05-03 0.5.0
================
- Move jep0106 test code into it's module
- HTTPPROXYsocket will send data before we have a Dispatcher
- Handle missing body, thanks to Brendan Sleight
- Handle spaces in SASL DIGEST-MD5 responses correctly
- Fix for incorrect-encoding during SASL PLAIN auth
- Allow anonymous auth if username is None
- Add extra XEP refs (this has been sitting in my working copy for about a year)
- Import simplexml updates from gajim, thanks mainly to asterix, thorstenp and dwd
- Replaced couple of 'print' statements with proper use of self.DEBUG
- Fix for fresh bug: self.server => self._server
- Fixed documentation bug in Component.__init__
- Fixed crash on whitespace-containing disco <iq/> reply
- Merged a fix for DNS SRV lookup on win32
- Merged XEP-0004.Multiple.Items.Form.Results patch. Thanks to Iván Lloro
- replaced deprecated code
- Sort SRV records by priority.
- Merge branch 'master' of https://github.com/umonkey/xmpppy
- Don't assume IQ child node is called 'query'
- An 'error' child is not a query node
- message.buildReply() preserves message type
- Import 0.5.0rc1 setup changes
- Merge branch 'setup' and update setup to be next alpha version


2007-09-15 0.4.1
================
- Fixing auth splits
- Ignore comment lines in config file
- tweaked login code to fail with reasons
- add some missing protocol namespaces
- Debian updates for version 0.4
- updating documentation links
- missed a few links
- allow the bot to set a connection resource
- Handle XCP component:accept namespace
- Fixed node attribute deletion with "del node[attr]" syntax.
- add support for setting the DataField label in it's constructor
- updating namespace constants
- moving admin namespace constants from jep0133 to to protocol
- Fix for non-ascii data in debug message
- change jep references into xep
- Ordering fix for when addChild and addData are used on the same node (may increase memory usage, might need to watch for that)
- Fix PlugOut and reconnectAndReauth code execution order
- More fixes - reconnectAndReauth now works for Client too
- Fix socket namespace conflict
- [ 1729857 ] typo in commands.py
- [ 1529650 ] Bug in auth, can't retry
- Fixes for children node fetching, still not perfect, but much better
- Clean up SSL errors a little bit


2006-10-06 0.4.0
================
- minor typos
- moved XEP-0106 into xmpp
- Added CDATA extracting method to xml node.
- Fix for non-int ports
- General cleanups
- fixed command namespaces
- added xmlns safety check
- fixes from Liorithiel
- added example command bot from Liorithiel
- fixed command namespaces and basic circle area math
- added support for wildfire component binding


2006-03-25 0.3.1
================
- Fixed bug in disco items discovery (thanks Soren Roug).
- Updated version stuff for xmpppy module.
- Updated debian/ directory to match actual debian package.
- Added dependency to python-dns package.
- Re-enabled debugging.


2006-03-13 0.3.0
================
- Added parameter to auth() to disable SASL
- Removed early FeaturesHandler call to not start auth before credentials got passed.
- Another SASL case was broken. Fix applied, tested against variety of servers.
- Lots of bugfixes -- thanks Norman
- List of default ssl ports is now [5223,443].
- Changed cl.connected from 'tls' to 'ssl' in case of port 5223/443.
- Commands now work.  Errors are also returned if continuing an invalid session.
- Docstring fix
- The setPrivacyList function used a nonexistent payload variable where it
- WARNING! Incompatible change! Now newtag=n.T.newtag do not creates new tag
- Fixed usage of .T. and .NT. notation according to recent change.
- Added support for non-fatal exception handling, exceptions can also be logged to file.
- fixes for error constants
- Added SRV record resolution for new client connections. This is using gajim changesets (2036 2037 2039 2040 3184 3407 3408 3409 3410 3411 3412 3413)
- Added help message to sample config file.
- Added keepalive feature in TODO list.
- Added another todo line about input chunking.
- Added TODO line about roster parsing traceback.
- fix for items being returned on non-items disco
- tidied disco and muc namespaces
- some todo items
- Fixes to make commands work, when you're working with multiple jids and nodes.
- Docstring fixes.
- Bumper pack of namespace definitions. Including gajim #2637.
- Asynchronous In-band Registration. Gajim patches #2035 #2318
- Enable SSL on non-standard port. Gajim #2065
- SASL Timeout, Gajim #2066
- Fixed first timestamp detection
- Fixed binding process. Formatiing fixes.
- Added several lines to TODO.
- Added method for retrieve nick value in MUC (Gajim patch 2089).
- Typo and debug line text fixes (Gajim patch 2113).
- Removed useless #!/usr/bin/python header (Gajim patch 2115)
- Added events for sent/received bytes (Gajim patches 2789, 2979, 3254).
- Added catchment for exception while tls handshake (Gajim patch 3323).
- Made SRV resolution disableable (Gajim patch 3658).
- fixes for discovery replies that gajim exposed
- fixed whitespace
- [gajim]it is standarD not with T; thanks dkm
- Fixed SASL bug on win32 platform. (Thanks to Martin Thomas)
- Fixed timstamp detecting bug (thanks to Daryl Herzmann).
- Fixed digest-uri parameter in SASL auth.
- command nodes now return correct disco#info values
- http://trac.gajim.org/ticket/1188 - fix for base64 encoded strings ending with an equals sign
- made failed connections slightly more robust.
- Disabled color output on non-un*x-like platforms.
- Enhanced debug output
- Jabberd2 component protocol support
- Added message events, and minor DataForm fix
- Message.buildReply fix for Gerard
- Namespace fixes
- xmlns fixes, and minor tweaks for speed and safety
- Made xmpppy to print warnings to stdout instead of stderr
- Bugfix for previous commit
- Fixed features.register
- Fixed resources consumation in many places
- Made NoDebug class usable


2005-05-12 0.2.0
================
- Bugfix: don't traceback if DISCO/Browse timed out.
- Now stanza properties stored in it's attribute "props".
- Ensure that username and resourcename got from server's responce.
- Bugfix: auth details should go into self._owner
- "chained" handlers killed
- NS_DIALBACK added
- Bugfix: typo in _DiscoveryHandler (thanks 2 Mike Albon)
- Fixed component auth that was brocken by dispatcher's changes.
- Added some wisdom to determining of default handler's namespace.
- More wisdom for default handler's namespace determining
- Bugfix: complete autodetection of default handler's namespace
- Docstrings merged. Most of them were ready already in (shame!) july.
- Pydoc strings added
- Added and/or modifyed docstrings. Now every method in library is documented\! Hurray\!
- Removed since api documentation is maintained via docstrings.
- Documentation updated: expert docs written, advanced started.
- README rewrited
- python distutils install tool
- Session class added
- Old servers compatibility stuff added. Tnx google, randomthoughts.
- Xmpppy-based bot example
- Initial version of commands processor
- Modified the handlers used. Result messages are not required for command processor use.
- BugFix: Roster.PresenceHandler should not raise NodeProcessed exception.
- Bugfix: (NonSASL) Added removal of empty <password/> node to achieve JiveMessenger compatibility (Tnx Brian Tipton)
- Bugfix: UNbroke accidentally brocken code. Shame on me.
- Bugfix: presences should not really inherit meta-info (like <show/> etc)
- Added etherx namespace to the default set to allow stream errors handling.
- "raise NodeProcessed" removed to allow userspace catch roster changes too
- Fixed Iq callback brocken last commit
- Changed (c) date range
- Preserved handlers during auth process to allow early handlers registration.
- Added commands module import
- Some tweaks about determining if node needs 'xmlns' attribute.
- Tweaked library to make it play nice as jabberd2 legacy component.
- Tuned "import"s stuff to be more in-line with library
- Installer Makefile
- Conference logging bot example
- Add index.html
- Bugfix: proxy was specified incorrectly
- Added presences tracking
- Replaced manual server type specification with autodetect
- Added back possibility of manual specification of server type (for Component)
- Reduced overload caused by extensive usage of T/NT classes.
- TODO for 0.2 release
- Fixed plugout methods to not take parameter
- Fixed RegisterHandler calls to catch only 'get' iqs.
- Added NS_COMMANDS, NS_ENCRYPTED, NS_SIGNED namespaces.
- Adjust docstrings
- Fixed getRegInfo to not crash on query's CDATA
- Minor changes in receive() code in preparation to fix TLS bug.
- Fixed auth logic: if SASL failed - then auth definitely failed too.
- Bugfix: TLS mode was unable to handle big (>1024 bytes) chunks of data.
- Fixed Non-SASL auth brocken with one of today's commits.
- Added stream errors classes along with default handler
- Added missing MUC attributes helper.
- Auth was failing when server declares XMPP stream (version="1.0") but
- Added non-locking SendAndCallForResponse method to ease life of realtime clients.
- Fixed stupid typo in DataForm
- Fixed traceback while connecting via proxy
- Added possibility to detect broken servers that didn't restart stream after
- Add reminder to fix source code release version string while making release
- Changed download url from whole project to xmpppy module
- Bugfix: RegisterHandler(...,makefirst=1) didn't work.
- New design. Big thanks to Marek Kubica for it.
- Made <a/> tags to not open new windows.
- Roster Iq handler must raise NodeProcessed. Otherwise, iq's will hit default
- Added comment about roster's NodeProcessed behaivoir.
- Fixed TLS-not-disconnects bug
- Added return value description to connect() docstring.
- Added note about TLS issue


2004-09-25 0.1.1
================
- Location changed to site-packages/xmpp
- Installation directory changes
- Web page xmpppy.sf.net
- All character data is now *STORED* in utf-8 not only printed.
- Cleanup: import of features no more needed.
- Changed dispatching policy: check for ALL child namespaces - not for only first <query/> in Iq stanza.
- Function "resultNode" replaced by "isResultNode".
- XMPP-Core stanza and stream level errors support added.
- Added translation of error codes to error conditions.
- returnStanzaHandler added.
- Added "default handler" mechanism.
- Date extended in license text.
- Update to current upstream version.
- 'jid' replaced by 'host' in registration methods.
- DataForm now can use prototype node for initialisation (as other protocol elements).
- Default resource name "xmpppy" now used only when auth with non-xmpp compliant
- Events introduced.
- Message.buildReply and Iq.buildReply introduced.
- Node cloning improved. Full cloning mode introduced.
- Implemented common plugins framework.
- Bugfix: preserve namespace when cloning node.
- Python 2.1 compatibility in Protocol.__init__.
- Error nodes creating and setting made more (I hope) intuitive. WARNING: uncompatible changes.
- Protocol.Error syntax changed. WARNING: incompatible changes.
- Very preliminary. It worked recently but poorly and may be broken already.
- Updated to 0.1-pre6.
- Fix: next version will be -rc1 not -pre6.
- Changed all "type" in functions arguments to "typ" .
- Changed debian-policy version to please the lintian.
- Removed "#!/usr/bin/python" headers to please lintian.
- Added getItems, keys and __getitem__ methods (limited mapping interface).
- Added NS_XXX importing into module's namespace.
- DeregisterDisconnectHandler renamed to UnregisterDisconnectHandler.
- JID.__ne__ method added.
- Bugfix: debug_flags was in "debug" module namespace instead of being Debug class attribute.
- Fixed backtrace on unhandled condition case.
- getRoster method added.
- getRoster , getItem methods added
- Sync with Debian's versions.
- Added README.
- Bugfix: addChild now set's child.parent properly.
- Fixed bug with "@" and "/" characters in the resource string.
- Bugfix: bits like xml:lang='en' was processed incorrectly.
- Bugfix: tag.getError() will not issue a traceback anymore if there is no error (thanks to sneakin).
- Add first pieces of documentation.
- Example script that is used in "simple" doc.
- Bugfix: use &quot; to not corrupt XML on some attribute values.
- Added links to documentation and Mike Albon's IRC transport.
- Added getQuerynode and setQuerynode methods.
- Synced with rc2-2 Debian version.
- Sync with rc3-1.proposed version.
- Added direct import from protocol module.
- All namespaces declarations moved to protocol module.
- Namespace declarations moved to protocol module.
- Bugfix: TLS failed to restart after disconnect.
- Bugfix: already dispatched node must not be changed anymore by NodeBuilder.
- Iq.buildReply made to appropriate set the queryNS value.
- Hand-crafted and logically debugged the heart - _traversePath. Now need to check other methods.
- Browser module tested, fixed and included into library structure.
- Bugfix: the returnStanzaHandler must not return error stanzas.
- Added Node.has_attr
- Added raising NodeProcessed exception to mark already processed iq and presences.
- Added DataField class in preparation to DataForm rewrite.
- Added support for nodes like "http://jabber.org/protocol/commands".
- Added support for several hosts on one connection.
- Added import of ustr function from simplexml module.
- Added support for multiple values.
- DataForm class re-implemented to conform XEP-0004 more closely.
- Fixed bug in CDATA handling code. The data will not be shifted between tags anymore.
- Made getPayload to return both CDATA and child nodes just like setPayload uses.
- Added getQueryChildren method. WARNING: it behaves gust like getQueryPayload before. And the getQueryPayload is now different!
- Bugfix: nodebuilder was tracing on the first node.
- Corrections to text donated by Mike Albon.
- Bugfix: typeless stanzas were processed several times sometimes.
- Fixed and tested IBB. Added usual debugging stuff to it.
- IBB stuff is fixed and worth inclusion.
- Fixed typo: SendInitialPresence => SendInitPresence.
- Update to revision 24.
- Added sessions support.
- Comments translated to english.
- Added 'jabber:client' and 'jabber:server' namespaces.
- Bugfix: handle roster item deletion properly.
- Bugfix: more delicate namespaces processing. Slow (again) but sure.
- XML namespaces vocabulary introduced.
- Added xmpp streams namespace.
- Added stanzas namespace support in dispatcher.
- SASL.auth method added. Removed credentials passing from PlugIn.
- Added SASL error conditions
- Added plugout method to TLS class for unregistering handlers.
- added destroy method to NodeBuilder to prevent memory leak
- Added plugout method for proper destuction of Stream instance.
- Plugging in now available only once.
- Namespace handler now comes under the name "default".
- XMPP streams namespace added.
- Allowed attribute values to be objects
- Rolled back ns vocabularies. They were potentially messing namespaces.


2004-02-28 0.1.0
================
- Added and tested SASL PLAIN.
- Service/agents discovery, [un]registration and password change, privacy lists handling.
- Tuned SASL (though it still not working), maked it to restart Dispatcher after auth.
- Fixed incompatibilities with jabberd2 in MD5-DIGEST algorithm.
- Bugfix: tag.getTags were broken.
- Syntactic changes and bugfixes in protocol.DataForm.
- payload again can be of non-[] non-() type.
- Two conditional service functions added: errorNode and resultNode.
- Make use of errorNode and resultNode conditional functions.
- Changed WaitForResponse to always return received Node if it were really received.
- Bugfixes: replaced "m" with "self" in many cases in Client code.
- Make use of resultNode and errorNode service functions.
- Added comparison methods.
- Fix case-handling in JIDs comparisons
- Make dispatcher to cache features tag.
- Make use of Dispatcher's features tag caching.
- Add fancy XML formatting (indents and newlines).
- Add "any time" SASL auth status.
- Made TLS and SASL use more flexible to work with ejabberd server.
- Bugfix: SASL authentication must be completed before resource binding.
- Maked early start of TLS when connecting to port 5223 possible.
- Bugfixes in privacy lists mangling stuff.
- Added (again) default port for component class.
- JID.getStripped now returns lower case JID (questionable change).
- Bugfix: non-sasl auth was not recognized.
- Simple import of all modules.
- Changes in "fancy" node output. Even more CDATA corruption ;)
- PlugIn methods now returns results of connection.
- connect() and auth() methods now returns result of operation.
- Fixed error text saying that we can do only PLAIN authentication.
- Bugfix: Component used 'client' string in debug output.
- Fix: Previous client.py commit broke jabberd2-compatible mechanisms.
- Added isConnected method.
- Made isConnected return more meaningful result (tcp | tls+old_auth | sasl)
- Made tests like isConnected()[4:] possible.
- Bugfix: Client.connect doesn't always returned true when connection estabilished.
- Added experimental support for live reconnection.
- Added revision control comment line.
- Added "NodeProcessed" mechanism to allow handlers stop further stanza processing.
- Initial Release.


2003-12-12 0.0.0
================
- Initial revision.
