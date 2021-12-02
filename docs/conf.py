# -*- coding: utf-8 -*-
"""Setup pylama configuration."""

import os
import sys

import pkg_resources

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Add any Sphinx extension module names here, as strings. They can be extensions
# coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = ["sphinx.ext.autodoc", "sphinx.ext.intersphinx", "sphinx_copybutton"]

# The suffix of source filenames.
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# General information about the project.
project = "Pylama"
copyright = "2013, Kirill Klenov"

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
try:
    release = pkg_resources.get_distribution("pylama").version
except pkg_resources.DistributionNotFound:
    print("To build the documentation, The distribution information of Muffin")
    print("Has to be available.  Either install the package into your")
    print('development environment or run "setup.py develop" to setup the')
    print("metadata.  A virtualenv is recommended!")
    sys.exit(1)
del pkg_resources

version = release

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ["_build"]

# If false, no module index is generated.
html_use_modindex = False

html_show_sphinx = False
htmlhelp_basename = "Pylamadoc"
latex_documents = [
    ("index", "Pylama.tex", "Pylama Documentation", "Kirill Klenov", "manual"),
]
latex_use_modindex = False
latex_use_parts = True
man_pages = [("index", "Pylama", "Pylama Documentation", ["Kirill Klenov"], 1)]
pygments_style = "tango"

# The theme to use for HTML and HTML Help pages.  Major themes that come with
# Sphinx are currently 'default' and 'sphinxdoc'.
html_theme = "sphinx_rtd_theme"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {"github_url": "https://github.com/klen/pylama"}
