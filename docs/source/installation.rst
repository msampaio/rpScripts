Installation
============

RP Scripts is a `Python-3 <https://www.python.org/>`_-based program. Python 3 non-users have to download and install it before running the following instructions (check `<https://www.python.org/downloads/>`_).

The RP Scripts install is partially manual.

1. Install RP Scripts. `PIPX <https://pipx.pypa.io/latest/>`_ is recommended.

For the stable version:

.. code-block:: console

   pipx install https://github.com/msampaio/rpScripts.git

For the development version:

.. code-block:: console

   pipx install git+https://github.com/msampaio/rpScripts.git@dev

2. If you plan to use the Textural class tool, install `Graphviz <https://www.graphviz.org/>`_.

The next step is to test the program. Open a terminal (or CMD on Windows) and run:

.. code-block:: console

   rpscripts -h