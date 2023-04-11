# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))
import datetime
import os
import sys

# -- Project information -----------------------------------------------------

project = 'EzyCore'
copyright = '2023, Seniatical'
author = 'Seniatical'

# The full version, including alpha/beta/rc tags
release = 'v0.2.1-beta.4'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinxawesome_theme"
]
autodoc_member_order = "groupwise"
autodoc_typehints_description_target = "documented"

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_title = "EzyCore"
html_permalinks_icon = '<span>#</span>'
html_theme = 'sphinxawesome_theme'
html_logo = "_static/logo.png"

html_context = {
    "github_url": "https://github.com",
    "github_user": "Seniatical",
    "github_repo": "EzyCore",
    "github_version": "main",
    "doc_path": "source",
    "last_updated": datetime.datetime.utcnow().strftime("%d/%m/%Y"),
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']