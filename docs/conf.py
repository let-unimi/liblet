# -- Support functions

from os import path

from pallets_sphinx_themes import ProjectLink, get_version

here = path.abspath(path.dirname(__file__))


def read(*parts):
  with open(path.join(here, *parts), encoding='utf-8') as fp:
    return fp.read()


# -- Project information

project = 'LibLET'
copyright = '2023, Massimo Santini'  #  noqa: A001
author = 'Massimo Santini'
release, version = get_version('liblet')

# -- General configuration

extensions = [
  'sphinx.ext.doctest',
  'sphinx.ext.autodoc',
  'sphinx.ext.intersphinx',
  'sphinx.ext.todo',
  'sphinx.ext.coverage',
  'sphinx.ext.mathjax',
  'sphinx.ext.napoleon',
  'pallets_sphinx_themes',
]

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
language = 'en'
exclude_patterns = ['_build', '.DS_Store', '*.ipynb', '**/.ipynb_checkpoints']
pygments_style = None
add_module_names = False


# -- Options for intersphinx extension

intersphinx_mapping = {
  'python': ('https://docs.python.org/3/', None),
}

# -- Options for HTML output

html_theme = 'flask'
html_context = {
  'project_links': [
    ProjectLink('PyPI releases', 'https://pypi.org/project/liblet/'),
    ProjectLink('Source Code', 'https://github.com/let-unimi/liblet'),
    ProjectLink('Issue Tracker', 'https://github.com/let-unimi/liblet/issues'),
    ProjectLink('Let@UniMI Website', 'https://let.di.unimi.it/'),
  ]
}
html_sidebars = {
  'index': ['project.html', 'localtoc.html', 'searchbox.html'],
  '**': ['localtoc.html', 'relations.html', 'searchbox.html'],
}
singlehtml_sidebars = {'index': ['project.html', 'localtoc.html']}
html_static_path = ['_static']
html_logo = '_static/logo.png'
html_title = f'LibLET Documentation ({version})'
html_show_sourcelink = False
html_domain_indices = False
html_css_files = ['custom.css']

# -- Options for todo extension

todo_include_todos = True
