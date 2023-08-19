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
import os
import sys
from unittest.mock import Mock
import builtins

builtins.__sphinx_build__ = True
 
MOCK_MODULES = [
    "anvil", 
    "anvil.js", 
    "_anvil_designer", 
    "anvil.facebook.auth",
    "anvil.google.auth",
    "anvil.google.drive",
    "anvil.google.drive.app_files",
    "anvil.users",
    "anvil.tables",
    "anvil.tables.query",
    "anvil.tables.app_tables",
    "anvil.js.window",
    "anvil.http",
    "AdminPanel._anvil_designer",
    "NativeDatepicker._anvil_designer",
    "anvil.tz",
    "LocalizedMultiSelectDropdown._anvil_designer",
    "HttpError",
]
for mod_name in MOCK_MODULES:
    sys.modules[mod_name] = Mock()

sys.path.append(os.path.abspath("../"))
sys.path.append(os.path.abspath("../../"))


# -- Project information -----------------------------------------------------
project = "FluentAnvil"
author = "Marcus Wörner"
copyright = "2023, Marcus Wörner"

# The full version, including alpha/beta/rc tags
release = "1.2.0"

sys.path.append(os.path.abspath("../client_code"))


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",  # Automatic API documentation
    "sphinx.ext.napoleon",  # Google-style docstrings
    "myst_parser",  # Import markdown files like Readme.md.
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    "**/exceptions.rst",
    "**/AdminPanel.rst",
    "**/LocalizedMultiSelectDropdown.rst",
    "**/NativeDatepicker.rst",
    "**/js.rst",
    "**/langcodes*.rst",
    "**/lib.rst",
    "**/registries.rst",
    "**/utils.rst*"
]

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = []

autodoc_class_signature = "separated"

# Add any MyST extension names here, as strings.
myst_enable_extensions = [
    "amsmath",
    "colon_fence",
    "deflist",
    "dollarmath",
    "html_image",
    "replacements",
    "smartquotes",
    "substitution",
    "tasklist",
]

autodoc_default_options = {
    "member-order": "groupwise",
    "special-members": "__init__",
    "undoc-members": False,
}
