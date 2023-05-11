Info
====

Info command shows a few pieces of information about the JSON data, such as:

1. The number of distinct partitions.
2. The number of distinct density numbers.
3. Highest values of agglomeration and dispersion index.

.. code-block:: console

    rpscripts info score.json

Command's output:

.. code-block:: console

    This file contains labels data: True
    Number of events: 55
    Number of distinct partitions: 17
    Number of distinct density numbers: 6
    Ratio partitions/dn: 2.83
    Highest dispersion index: 13
    Highest agglomeration index: 15