MODULE=pylama
SPHINXBUILD=sphinx-build
ALLSPHINXOPTS= -d $(BUILDDIR)/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .
BUILDDIR=_build
VIRTUAL_ENV 	?= env

LIBSDIR=$(CURDIR)/libs

.PHONY: help
# target: help - Display callable targets
help:
	@egrep "^# target:" [Mm]akefile

$(VIRTUAL_ENV): setup.cfg requirements/requirements.txt requirements/requirements-tests.txt
	@[ -d $(VIRTUAL_ENV) ] || python -m venv $(VIRTUAL_ENV)
	@$(VIRTUAL_ENV)/bin/pip install -e .[tests]
	@touch $(VIRTUAL_ENV)

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
release minor:
	@pip install bumpversion
	@bumpversion $(VERSION)
	@git checkout master
	@git merge develop
	@git checkout develop
	@git push --all
	@git push --tags

.PHONY: major
major:
	make release VERSION=major

.PHONY: patch
patch:
	make release VERSION=patch

# ===============
#  Build package
# ===============

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
t test: $(VIRTUAL_ENV)
	@pytest --pylama pylama
	@pytest tests

mypy: $(VIRTUAL_ENV)
	mypy pylama

.PHONY: audit
audit:
	@python -m "pylama.main"

.PHONY: docs
docs: docs
	@python setup.py build_sphinx --source-dir=docs/ --build-dir=docs/_build --all-files

docker:
	docker build -t pylama .

docker-sh:
	docker run --rm -it pylama sh

docker-test:
	docker run --rm -it pylama pytest --pylama pylama
