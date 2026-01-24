.PHONY: apidocs install release

apidocs:
	epydoc -q -o doc/apidocs xmpp/

install:
	# Add here commands to install the package into debian/python-xmpp
	[ -d $(MODULESDIR)/xmpp ] || mkdir $(MODULESDIR)/xmpp
	install -m 0644 xmpp/*py $(MODULESDIR)/xmpp

release: push build pypi-upload


# ===============
# Utility targets
# ===============
push:
	git push && git push --tags

build:
	uvx --with=build python -m build

pypi-upload:
	uvx twine upload --skip-existing --verbose dist/*.tar.gz
