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

.PHONY: t
t: audit
	python setup.py test

.PHONY: audit
audit:
	python -m "pylama.main"

.PHONY: docs
docs: docs
	python setup.py build_sphinx --source-dir=docs/ --build-dir=docs/_build --all-files
	# python setup.py upload_sphinx --upload-dir=docs/_build/html
