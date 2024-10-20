import os
import sys

# Add the virtual environment absolute path to python path
sys.path.insert(0, os.path.abspath("../.."))

# Project information
project = "mdutil"
copyright = "2024, Pablo Porta 'paspallas'"
author = "Pablo Porta"
release = "0.1.0"

# General configuration
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx_rtd_theme",
]

templates_path = ["_templates"]
exclude_patterns = ["../_build", "Thumbs.db", ".DS_Store"]

# Html output options
html_theme = "sphinx_rtd_theme"
html_static_path = ["../_static"]
