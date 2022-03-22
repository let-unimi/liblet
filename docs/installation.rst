.. _installation:

Installation
============

We recommend using the latest version of Python 3, LibLET is tested under Python
3.7 and newer. These packages (and the related dependencies) will be installed
automatically when installing LibLET:

* `antlr4-python3-runtime`_ the runtime of `ANTLR 4`_ for Python 3;
* `jupyter`_ a web application to create documents that contain live
  code, math, visualizations and narrative text;
* `graphviz <https://pypi.org/project/graphviz/>`__ the Python binding for the
  `Graphviz`_ graph visualization software.

.. _ANTLR 4: https://www.antlr.org/
.. _Graphviz: https://www.graphviz.org/
.. _antlr4-python3-runtime: https://pypi.org/project/antlr4-python3-runtime/
.. _jupyter: https://pypi.org/project/jupyter/

Virtual environments
--------------------

It's suggested to use a *virtual environment* to manage Python dependencies:
virtual environments are independent groups of Python libraries, one for each
project; packages installed for one project will not affect other projects or
the operating system's packages.

Create an environment
~~~~~~~~~~~~~~~~~~~~~

Python 3 comes bundled with the :mod:`venv` module to create virtual
environments. Create a project folder and a :file:`venv` folder within:

.. code-block:: sh

    $ mkdir myproject
    $ cd myproject
    $ python3 -m venv venv

On Windows:

.. code-block:: bat

    $ py -3 -m venv venv

Activate the environment
~~~~~~~~~~~~~~~~~~~~~~~~

Every time you decide to use the library, activate the environment:

.. code-block:: sh

    $ . venv/bin/activate

On Windows:

.. code-block:: bat

    > venv\Scripts\activate

Install the library
-------------------

Within the activated environment, use the following command to install the
library:

.. code-block:: sh

    $ pip install liblet

Install the external dependencies
---------------------------------

To use LibLET you also need to manually install:

* the `Graphviz`_ visualization software,
* the **ANTLR Tool**, and
* the **LLVM toolchain** in case you want to use the :class:`~liblet.llvm.LLVM`
  helper class (present code is tested with version 11 of the toolchain).

Follow the installation instruction on the `Graphviz`_ and `LLVM`_ sites
according to your operating system and package manager.

.. _LLVM: https://llvm.org/

To install the **ANTLR Tool**, you can use the :command:`install_antlrjar`
command provided by LibLET as:

.. code-block:: sh

    $ install_antlrjar

and set the :envvar:`ANTLR4_JAR` *environment variable* to the full path of the
downloaded jar as advised. Finally, if you plan to use the
:class:`~liblet.llvm.LLVM` helper class, set the :envvar:`LLVM_VERSION`
*environment variable* to the installed toolchain version.

