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
	@pip install twine wheel
	@python setup.py sdist bdist_wheel
	@twine upload dist/*.tar.gz || true
	@twine upload dist/*.whl || true

# =============
#  Development
# =============

.PHONY: t
t test:
	@py.test --pylama pylama
	@py.test -sx tests

.PHONY: audit
audit:
	@python -m "pylama.main"

.PHONY: docs
docs: docs
	@python setup.py build_sphinx --source-dir=docs/ --build-dir=docs/_build --all-files
