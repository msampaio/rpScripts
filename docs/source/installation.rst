Installation
============

RP Scripts is a `Python-3 <https://www.python.org/>`_-based program. Python 3 non-users have to download and install it before running the following instructions (check `<https://www.python.org/downloads/>`_).

The RP Scripts install is partially manual.

1. Install RP Scripts. `PIPX <https://pipx.pypa.io/latest/>` is recommended.

   pipx install https://github.com/msampaio/rpScripts.git

2. Create a ``rps_aux`` folder in your root (``~/rps_aux`` on Linux and Mac, or ``C:\Users\Username\rps_aux`` on Windows).

3. Download the file https://raw.githubusercontent.com/msampaio/rpScripts/refs/heads/main/lattice_map.json in your ``rps_aux`` folder.

4. If you plan to use the Textural class tool, install `Graphviz <https://www.graphviz.org/>`_.

The next step is to test the program. Open a terminal (or CMD on Windows) and run:

.. code-block:: console

   rpscripts -h