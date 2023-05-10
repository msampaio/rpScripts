Installation
============

RP Scripts is a `Python-3 <https://www.python.org/>`_-based program. Python 3 non-users have to download and install it before running the following instructions (check `<https://www.python.org/downloads/>`_).

There are multiple ways to install RP Scripts. All of them require dependencies installation:

.. code-block:: console

   pip install -r requirements.txt

Binary creation
---------------

The easiest way to use it is by creating a binary file (for instance, a ``.exe`` in Windows).

1. Build the binary:

.. code-block:: console

   pyinstaller rpscripts.spec

This command generates ``build`` and ``dist`` folders and saves the binary file into the ``dist`` folder.

2. Move the binary file to a folder in the user system's ``PATH``.

3. We encourage the user to create a personal scripts folder and put it in the system's ``PATH``.

4. Jump to :ref:`finishing_installation` instructions.

As a PIP package
----------------

To use rpscripts like a ``PIP`` package, run:

.. code-block:: console

   python -m build

Then, locate the ``.whl`` file inside the ``dist`` folder and run:

.. code-block:: console

   pip install -U dist/rpscripts-[version]-py3-none-any.whl

Linux and Mac users must rename the ``rps_run.py`` file to ``rpscripts`` and move it to a binary folder listed at ``PATH``, such as ``~/.local/bin`` (Linux) or ``/usr/local/bin`` (Mac).

.. _finishing_installation:

Finishing installation
----------------------

Finally, create a ``~/rps_aux`` folder and copy the provided ``lattice_map.json`` there.