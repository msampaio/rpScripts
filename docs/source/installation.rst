Installation
============

RP Scripts is a `Python-3 <https://www.python.org/>`_-based program. The easiest way to install RP Scripts is using the `PIPX <https://pipx.pypa.io/latest/>`_ package manager to get and install it from its source code from GitHub.

The installation process consists of:

- Install Python 3
- Install an auxiliary package manager (homebrew for MacOS or scoop for Windows)
- Install PIPX
- Install GIT
- Install RP Scripts
- Install Graphviz

Python 3
--------

To check Python 3 availability, open a terminal (power shell on Windows) and run the following command:

.. code-block:: console

   python --version

To install Python 3, check its `documentation <https://docs.python.org/3/using/index.html>`_.

Auxiliary package manager
-------------------------

Linux
~~~~~

Most Linux distros have package managers. For instance, `apt` in Debian-based, `dnf` in RedHat, `pacman` in ArchLinux, etc.

MacOS
~~~~~

Mac users need to install the `Homebrew <https://brew.sh/>`_ package manager:

.. code-block:: console

   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

Windows
~~~~~~~

Windows users need to open a PowerShell terminal and install the `Scoop <https://scoop.sh/>`_ command installer:

.. code-block:: console

   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression

PIPX
----

PIPX installation consists of two steps: the program installation and the path configuration.

Linux
~~~~~

Open a terminal and run the following commands:

.. code-block:: console

   sudo apt install pipx
   pipx ensurepath

MacOS
~~~~~

Open a terminal and run the following commands:

.. code-block:: console

   brew install pipx
   pipx ensurepath

Windows
~~~~~~~

Open a PowerShell and run the following commands:

.. code-block:: console

   scoop install pipx
   pipx ensurepath

GIT
---

See GIT documentation at https://git-scm.com/book/en/v2/Getting-Started-Installing-Git.

Linux
~~~~~

Open a terminal and run the following commands:

.. code-block:: console

   sudo apt install git-all

MacOS
~~~~~

Open a terminal and run the following commands:

.. code-block:: console

   brew install git

Windows
~~~~~~~

Get the binary at https://git-scm.com/downloads/win and install.

RP Scripts
----------

The next step is to use PIPX to install RP Scripts.

For the stable version:

.. code-block:: console

   pipx install git+https://github.com/msampaio/rpScripts.git

For the development version:

.. code-block:: console

   pipx install git+https://github.com/msampaio/rpScripts.git@dev

Graphviz
--------

The :doc:`programs/tclass` program needs `Graphviz <https://www.graphviz.org/>`_.

Install checking
----------------

For the install checking, run:

.. code-block:: console

   rpscripts -h