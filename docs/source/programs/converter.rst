Converter
=========

The converter command saves a given JSON data into a CSV file.

The basic command line is:

.. code-block:: console

    rpscripts convert score.json

Option ``-h`` returns program's help:

.. code-block:: console

    usage: rpscripts convert [-h] [-e] filename

    positional arguments:
    filename             JSON filename (calc's output)

    options:
    -h, --help           show this help message and exit
    -e, --equally_sized  generate equally-sized events

Option ``-e`` creates a CSV file with equally-sized events. This procedure is helpful for statistical operations such as frequency analysis.