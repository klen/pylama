MODULE=pylama
SPHINXBUILD=sphinx-build
ALLSPHINXOPTS= -d $(BUILDDIR)/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .
BUILDDIR=_build


.PHONY: clean
clean:
	sudo rm -rf build dist docs/_build
	find . -name "*.pyc" -delete
	find . -name "*.orig" -delete

.PHONY: register
	python setup.py register

.PHONY: upload
upload:
	python setup.py sdist upload || echo 'Upload already'

.PHONY: test
test: audit
	python setup.py test

.PHONY: audit
audit:
	python -m "pylama.main" -i 'E501' --skip='*/messages.py,*/pylama/_/*,*/pylama/pylint/*,*/.env/*' -l "pylint,pep8,pyflakes,mccabe"
