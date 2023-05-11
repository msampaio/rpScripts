Trimmer
=======

Trimmer command returns a sliced JSON data with the content between given measure numbers:

.. code-block:: console

    rpscripts trim -s 10 -e 20 score.json

Option ``-h`` prints program's help:

.. code-block:: console

    usage: rpscripts trim [-h] [-s START] [-e END] filename

    positional arguments:
    filename              JSON filename (calc's output)

    options:
    -h, --help            show this help message and exit
    -s START, --start START
                            Start measure. Blank means "from the beginning"
    -e END, --end END     End measure. Blank means "to the end"

**Note**: Trimmed JSON data is not suitable for the :doc:`annotator` processing.