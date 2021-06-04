Welcome to LibLET
=================

LibLET is a library developed as a teaching aid for the `Linguaggi e traduttori
<https://let.di.unimi.it/>`_ class at the `Computer Science department
<https://www.di.unimi.it/>`_ of `Università degli Studi di Milano
<https://www.unimi.it/>`_ by `Massimo Santini <https://santini.di.unimi.it/>`_.

The main aim of this library is to provide a set of convenient data types
representing the usual objects of study of *formal languages* and *parsing* such
as, for example: *grammars*, *productions*, *trees*, *derivations*, *automata*…
so that one can implement (and experiment with) classic formal languages
algorithms with minimal effort. For this reason, the library itself does not
include any ready made implementation, the point being exactly the opposite: to
stimulate teachers and students to write their own concrete implementations
starting from informal textbook descriptions of classical algorithms, but being
able to use the *high level data types* provided by the library. Moreover, for
most of such types, a `rich display
<https://ipython.readthedocs.io/en/stable/config/integrating.html#rich-display>`_
is provided so that `Jupyter <https://jupyter.org/>`_ can be fruitfully used to
explore and experiment with such algorithms and implementations.

Get started with :ref:`installation` and then get an overview with the
:ref:`examples`. The rest of the docs describe each component of LibLET in
detail, with a full reference in the :ref:`API` section.


User's Guide
------------

This part of the documentation, which is mostly prose, focuses on step-by-step
instructions to install the library and use if for some common tasks.

.. toctree::
   :maxdepth: 2

   installation
   examples

API Reference
-------------

If you are looking for information on a specific function, class or method, this
part of the documentation is for you.

.. toctree::
   :maxdepth: 2

   api
