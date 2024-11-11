Installation
============

RP Scripts is a `Python-3 <https://www.python.org/>`_-based program. Python 3 non-users have to download and install it before running the following instructions (check `<https://www.python.org/downloads/>`_).

The easiest way to install RP Scripts is using `PIPX <https://pipx.pypa.io/latest/>`_ and `GIT <https://git-scm.com/>`_.

PIPX install
------------

Linux
~~~~~

Debian-based distros users need to open a terminal and run:

.. code-block:: console

   sudo apt install pipx
   pipx ensurepath

Mac
~~~

Mac users need to install the `Homebrew <https://brew.sh/>`_ package manager:

.. code-block:: console

   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

then, install PIPX:

.. code-block:: console

   brew install pipx
   pipx ensurepath

Windows
~~~~~~~

Windows users need to open a PowerShell terminal and install the `Scoop <https://scoop.sh/>`_ command installer:

.. code-block:: console

   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression

and then, install PIPX:

.. code-block:: console

   scoop install pipx
   pipx ensurepath

GIT install
-----------

See GIT documentation at https://git-scm.com/book/en/v2/Getting-Started-Installing-Git.

Linux
~~~~~

Debian-based distros users need to open a terminal and run:

.. code-block:: console

   sudo apt install git-all

Mac
~~~

.. code-block:: console

   brew install git

Windows
~~~~~~~

Get the binary at https://git-scm.com/downloads/win and install.

RP Scripts install
------------------

The next step is to use PIPX to install RP Scripts.

For the stable version:

.. code-block:: console

   pipx install https://github.com/msampaio/rpScripts.git

For the development version:

.. code-block:: console

   pipx install git+https://github.com/msampaio/rpScripts.git@dev

Dependencies
------------

The :doc:`programs/tclass` program needs `Graphviz <https://www.graphviz.org/>`_.

Install checking
----------------

For the install checking, run:

.. code-block:: console

   rpscripts -h