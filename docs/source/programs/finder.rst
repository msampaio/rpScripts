Finder
======

.. FIXME
The Finder looks up the location (measure number and distance from the beginning) of parameters such as partitions, number of parts, density-number, textural class, and textural contour in a given JSON file.

The command below returns the program's help:

.. code-block:: console

    usage: rpscripts find [-h] [-p PARTITION] [-d DENSITY_NUMBER]
                        [-n NUMBER_OF_PARTS] [-tcl TCLASS] [-tcn TCONTOUR] [-md]
                        [-mn]
                        filename

    positional arguments:
    filename              JSON filename (calc's output)

    options:
    -h, --help            show this help message and exit
    -p PARTITION, --partition PARTITION
                            Partition (between quotation marks)
    -d DENSITY_NUMBER, --density_number DENSITY_NUMBER
                            Density-number
    -n NUMBER_OF_PARTS, --number_of_parts NUMBER_OF_PARTS
                            Number of parts
    -tcl TCLASS, --tclass TCLASS
                            Textural class
    -tcn TCONTOUR, --tcontour TCONTOUR
                            Textural contour
    -md, --max_density_number
                            Maximum density-number
    -mn, --max_number_of_parts
                            Maximum density-number

Use the ``-p`` option to find all the locations of a given partition:

.. code-block:: console

    rpscripts find -p "1^5" score.json

This command outputs:

.. code-block:: console

        Partition  Density-number  Number-parts  Agglomeration  Dispersion Tclass
    5+1          1.5               6             2           10.0         5.0     LB
    8+0          1.5               6             2           10.0         5.0     LB
    9+1          1.5               6             2           10.0         5.0     LB
    11+3/2       1.5               6             2           10.0         5.0     LB
    14+1         1.5               6             2           10.0         5.0     LB
    16+0         1.5               6             2           10.0         5.0     LB
    Partition (1.5): 6 entries

Use the ``-d`` option to find all the locations of a given density-number:

.. code-block:: console

    rpscripts find -d 3 score.json

This command outputs:

.. code-block:: console

        Partition  Density-number  Number-parts  Agglomeration  Dispersion Tclass
    5+3/4        1.2               3             2            1.0         2.0     LB
    9+3/4        1.2               3             2            1.0         2.0     LB
    13+1           3               3             1            3.0         0.0      B
    17+7/4       1.2               3             2            1.0         2.0     LB
    Density-number (3): 4 entries

Use the ``-n`` option to find all the locations of a given number of parts:

.. code-block:: console

    rpscripts find -n 3 score.json

This command outputs:

.. code-block:: console

        Partition  Density-number  Number-parts  Agglomeration  Dispersion Tclass
    4+0        1^2.4               6             3            6.0         9.0    LxB
    4+1        1^2.3               5             3            3.0         7.0    LxB
    5+0        1^2.4               6             3            6.0         9.0    LxB
    8+1        1^2.3               5             3            3.0         7.0    LxB
    9+0        1^2.4               6             3            6.0         9.0    LxB
    10+1       1.2^2               5             3            2.0         8.0    LBy
    11+1/2     1^2.4               6             3            6.0         9.0    LxB
    15+0       1.2.3               6             3            4.0        11.0    LBy
    16+1       1^2.3               5             3            3.0         7.0    LxB
    17+0       1^2.4               6             3            6.0         9.0    LxB
    Parts (3): 10 entries

Use the ``-tcl`` option to find all the locations of a given textural class (See how to calculate textural classes in :doc:`tclass` documentation):

.. code-block:: console

    rpscripts find -tcl "By" score.json

This command outputs:

.. code-block:: console

        Partition  Density-number  Number-parts  Agglomeration  Dispersion Tclass
    15+1       2.4               6             2            7.0         8.0     By
    tclass (By): 1 entries

Use the ``-tcn`` option to find all the locations of a given textural contour (See how to calculate textural contour in :doc:`tcontour` documentation):

.. code-block:: console

    rpscripts find -tcn 3 score.json

This command outputs:

.. code-block:: console

        Partition  Density-number  Number-parts  Agglomeration  Dispersion Tcontour Tclass
    2+1            4               4             1            6.0         0.0        3      B
    5+3/4        1.2               3             2            1.0         2.0        3     LB
    6+1            4               4             1            6.0         0.0        3      B
    9+3/4        1.2               3             2            1.0         2.0        3     LB
    17+7/4       1.2               3             2            1.0         2.0        3     LB

Maximum values
--------------

The Finder also returns the location of the partitions with maximum values of density-number and number of parts.

Use the ``-md`` option to find all the locations with the maximum value of density-number:

.. code-block:: console

    rpscripts find -md score.json

This command outputs:

.. code-block:: console

        Partition  Density-number  Number-parts  Agglomeration  Dispersion Tcontour Tclass
    4+0        1^2.4               6             3            6.0         9.0      8-0    LxB
    5+0        1^2.4               6             3            6.0         9.0      8-0    LxB
    5+1          1.5               6             2           10.0         5.0      6-0     LB
    8+0          1.5               6             2           10.0         5.0      6-0     LB
    9+0        1^2.4               6             3            6.0         9.0      8-0    LxB
    9+1          1.5               6             2           10.0         5.0      6-0     LB
    11+0     1^2.2^2               6             4            2.0        13.0     10-0   LxBy
    11+1/2     1^2.4               6             3            6.0         9.0      8-0    LxB
    11+3/2       1.5               6             2           10.0         5.0      6-0     LB
    13+3/2         6               6             1           15.0         0.0        5      B
    14+1         1.5               6             2           10.0         5.0      6-0     LB
    15+0       1.2.3               6             3            4.0        11.0        9    LBy
    15+1         2.4               6             2            7.0         8.0        7     By
    16+0         1.5               6             2           10.0         5.0      6-0     LB
    17+0       1^2.4               6             3            6.0         9.0      8-0    LxB
    Density-number (6): 15 entries

Use the ``-mn`` option to find all the locations with the maximum value of number of parts:

.. code-block:: console

    rpscripts find -mn score.json

This command outputs:

.. code-block:: console

        Partition  Density-number  Number-parts  Agglomeration  Dispersion Tcontour Tclass
    10+0     1^3.2               5             4            1.0         9.0        9    LxB
    11+0   1^2.2^2               6             4            2.0        13.0     10-0   LxBy
    Parts (4): 2 entries

The Finder saves a TXT file when the number of occurrences exceeds 30.