MODULE=pylama
SPHINXBUILD=sphinx-build
ALLSPHINXOPTS= -d $(BUILDDIR)/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .
BUILDDIR=_build

LIBSDIR=$(CURDIR)/libs

.PHONY: help
# target: help - Display callable targets
help:
	@egrep "^# target:" [Mm]akefile

.PHONY: clean
# target: clean - Clean repo
clean:
	@rm -rf build dist docs/_build *.egg
	@find . -name "*.pyc" -delete
	@find . -name "*.orig" -delete
	@rm -rf $(CURDIR)/libs

# ==============
#  Bump version
# ==============

.PHONY: release
VERSION?=minor
# target: release - Bump version
release:
	@pip install bumpversion
	@bumpversion $(VERSION)
	@git checkout master
	@git merge develop
	@git checkout develop
	@git push --all
	@git push --tags

.PHONY: minor
minor: release

.PHONY: patch
patch:
	make release VERSION=patch

# ===============
#  Build package
# ===============

.PHONY: register
# target: register - Register module on PyPi
register:
	python setup.py register

.PHONY: upload
# target: upload - Upload module on PyPi
upload: clean
	@git push --all
	@git push --tags
	@pip install wheel
	@python setup.py sdist upload || echo 'Already uploaded'
	@python setup.py bdist_wheel upload || echo 'Already uploaded'

# =============
#  Development
# =============

.PHONY: t
t:
	@py.test -sx tests.py

.PHONY: audit
audit:
	python -m "pylama.main"

.PHONY: docs
docs: docs
	python setup.py build_sphinx --source-dir=docs/ --build-dir=docs/_build --all-files
