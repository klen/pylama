MODULE=pylama
SPHINXBUILD=sphinx-build
ALLSPHINXOPTS= -d $(BUILDDIR)/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .
BUILDDIR=_build

LIBSDIR=$(CURDIR)/libs


.PHONY: clean
clean:
	@rm -rf build dist docs/_build
	@find . -name "*.pyc" -delete
	@find . -name "*.orig" -delete
	@rm -rf $(CURDIR)/libs

.PHONY: register
	python setup.py register

.PHONY: upload
upload:
	python setup.py sdist upload || echo 'Upload already'

.PHONY: t
t: audit
	python setup.py test

.PHONY: audit
audit:
	python -m "pylama.main"

.PHONY: docs
docs: docs
	python setup.py build_sphinx --source-dir=docs/ --build-dir=docs/_build --all-files

.PHONY: libs
libs: pep257 pep8 pyflakes

$(LIBSDIR)/pep8:
	mkdir -p $(LIBSDIR)
	@git clone https://github.com/jcrocholl/pep8 $(LIBSDIR)/pep8

$(LIBSDIR)/pyflakes:
	mkdir -p $(LIBSDIR)
	@git clone https://github.com/kevinw/pyflakes $(LIBSDIR)/pyflakes

$(LIBSDIR)/pep257:
	mkdir -p $(LIBSDIR)
	@git clone https://github.com/GreenSteam/pep257 $(LIBSDIR)/pep257

$(LIBSDIR)/pies:
	mkdir -p $(LIBSDIR)
	@git clone https://github.com/timothycrosley/pies $(LIBSDIR)/pies

.PHONY: pep257
pep257: $(LIBSDIR)/pep257
	cd $(LIBSDIR)/pep257 && git pull --rebase
	cp -f $(LIBSDIR)/pep257/pep257.py $(CURDIR)/pylama/lint/pylama_pep257/.

.PHONY: pep8
pep8: $(LIBSDIR)/pep8
	cd $(LIBSDIR)/pep8 && git pull --rebase
	cp -f $(LIBSDIR)/pep8/pep8.py $(CURDIR)/pylama/lint/pylama_pep8/.

.PHONY: pyflakes
pyflakes: $(LIBSDIR)/pyflakes
	cd $(LIBSDIR)/pyflakes && git pull --rebase
	cp -f $(LIBSDIR)/pyflakes/pyflakes/__init__.py $(CURDIR)/pylama/lint/pylama_pyflakes/pyflakes/.
	cp -f $(LIBSDIR)/pyflakes/pyflakes/messages.py $(CURDIR)/pylama/lint/pylama_pyflakes/pyflakes/.
	cp -f $(LIBSDIR)/pyflakes/pyflakes/checker.py $(CURDIR)/pylama/lint/pylama_pyflakes/pyflakes/.

# $(LIBSDIR)/frosted:
	# mkdir -p $(LIBSDIR)
	# @git clone https://github.com/timothycrosley/frosted $(LIBSDIR)/frosted

# .PHONY: frosted
# frosted: $(LIBSDIR)/frosted
	cd $(LIBSDIR)/frosted && git pull --rebase
