
#MODULESDIR=/usr/lib/($PYTHONVERSION)/site-packages

.PHONY: apidocs install

apidocs:
	epydoc -q -o doc/apidocs xmpp/

install:
	# Add here commands to install the package into debian/python-xmpp
	[ -d $(MODULESDIR)/xmpp ] || mkdir $(MODULESDIR)/xmpp
	install -m 0644 xmpp/*py $(MODULESDIR)/xmpp

#release: bumpversion push sdist pypi-upload
release: push build pypi-upload


# ===============
# Utility targets
# ===============
bumpversion: install-releasetools check-bump-options
	$(bumpversion) $(bump)

push:
	git push && git push --tags

build:
	uvx --with=build python -m build

pypi-upload:
	uvx twine upload --skip-existing --verbose dist/*.tar.gz

install-releasetools: setup-virtualenv2
	@$(pip) install --quiet --requirement requirements-release.txt --upgrade

check-bump-options:
	@if test "$(bump)" = ""; then \
		echo "ERROR: 'bump' not set, try 'make release bump={patch,minor,major}'"; \
		exit 1; \
	fi
