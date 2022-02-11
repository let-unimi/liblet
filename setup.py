from setuptools import setup, find_packages
from os import path
from io import open
import re

here = path.abspath(path.dirname(__file__))

def read(*parts):
    with open(path.join(here, *parts), 'r', encoding = 'utf-8') as fp:
        return fp.read()

def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match: return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

setup(
    name = 'liblet',
    version = find_version('src', 'liblet', '__init__.py'),
    description = 'A teaching aid library for formal languages and compiler courses.',
    long_description = read('README.md'),
    long_description_content_type = 'text/markdown',
    url = 'https://github.com/let-unimi/liblet',
    author = 'Massimo Santini',
    author_email = 'massimo.santini@unimi.it',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Framework :: IPython',
        'Framework :: Jupyter',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.7',
        'Topic :: Education',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Software Development :: Compilers'
    ],
    keywords = 'automata grammar formal language graph tree',
    package_dir = {'': 'src'},
    packages = find_packages('src', exclude = ['tests']),
    py_modules = ['scripts'],
    python_requires='>=3.7',
    install_requires = ['antlr4-python3-runtime==4.9.3', 'jupyter', 'graphviz', 'ipywidgets'],
    extras_require = {
        'dev': ['bumpversion', 'sphinx', 'twine', 'Pallets-Sphinx-Themes', 'gitchangelog', 'pystache'],
        'test': ['coverage', 'codecov'],
    },
    entry_points={  # Optional
        'console_scripts': [
            'install_antlrjar=scripts:install_antlrjar',
        ],
    },
    project_urls = {
        'Bug Tracker': 'https://github.com/let-unimi/liblet/issues',
        'Source': 'https://github.com/let-unimi/liblet',
        'Documentation': 'https://liblet.readthedocs.io/en/latest/'
    },
)
