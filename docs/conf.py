# -*- coding: utf-8 -*-

# -- Support functions

from os import path
from io import open
import re

here = path.abspath(path.dirname(__file__))
print(here)
def read(*parts):
    with open(path.join(here, *parts), 'r', encoding = 'utf-8') as fp:
        return fp.read()

def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match: return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

# -- Project information

project = 'LibLET'
copyright = '2019, Massimo Santini'
author = 'Massimo Santini'
version = find_version('..', 'src', 'liblet', '__init__.py')
release = '0.0.1'

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
]

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
language = 'en'
exclude_patterns = ['_build', '.DS_Store']
pygments_style = None

# -- Options for HTML output -------------------------------------------------

html_theme = 'alabaster'
html_static_path = ['_static']
# html_sidebars = {}

# -- Options for todo extension ----------------------------------------------

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True
