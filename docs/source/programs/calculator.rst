Calculator
==========

The Calculator program extracts rhythmic partitioning data from given digital scores and saves it into a JSON file.

Output JSON file contains:

1. ``texture_data`` with events' data split in separate lists:
    1. Index (``measure number + offset``)
    2. Measure number
    3. Offset
    4. Global offset
    5. Duration
    6. Partition
    7. Density number
    8. Agglomeration index
    9. Dispersion index
2. ``offset_map`` with a map of measure numbers and their global offsets
3. ``values_map`` with partitions and the values of their agglomeration and dispersion indexes
4. ``partitions`` with a single list of each event partitions

Its basic usage is:

.. code-block:: console

    rpscripts calc score.xml

The option ``-h`` prints the program help:

.. code-block:: console

    rpscripts calc -h

Output:

.. code-block:: console

    usage: rpscripts calc [-h] [-d] [-m] [-c] [-e] filename

    positional arguments:
    filename              digital score filename (XML, MXL, MIDI and KRN)

    options:
    -h, --help            show this help message and exit
    -d, --dir             folder with digital score files
    -m, --multiprocessing
                            multiprocessing
    -c, --csv             output data in a CSV file.
    -e, --equally_sized   generate equally-sized events

The ``-c`` option also creates a CSV file with the events data (see :doc:`converter` section).

The combined ``-e`` and ``-c`` options create a CSV file with equally-sized events. This procedure is helpful for statistical operations such as frequency analysis.

.. code-block:: console

    rpscripts calc -e score.xml

The ``-d`` option runs the program in all available digital scores available in the given directory (XML, MXL, KRN, MIDI, and MID):

.. code-block:: console

    rpscripts calc -d path-to-folder

The ``-m`` option runs the program using multiple processor cores when available. This option runs in combination with ``-d``:

.. code-block:: console

    rpscripts calc -m -d path-to-folder