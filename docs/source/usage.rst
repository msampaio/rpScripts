Usage
=====

RP Scripts has a :ref:`cli` and a structure for :ref:`package_usage`.

Components
----------

RP Scripts comprises the following programs:

- Calculator
- Plotter
- Annotator
- Labeler
- Info
- Utils
- Stats
- Converter
- Trimmer

.. _cli:

Command Line Interface
----------------------

``rpscript`` provides a high-level command line interface for the rhythmic partitioning tasks. Each program has a specific command line.

The command line below calls the help page.

.. code-block:: console

    rpscripts -h

This command outputs:

.. code-block:: console

  usage: rpscripts [-h] [-v]
                  {calc,plot,annotate,label,info,utils,stats,convert,trim}
                  ...

  Rhythmic Partitioning Scripts.

  options:
    -h, --help            show this help message and exit
    -v, --version         show program's version number and exit

  Subcommands:
    Available subcommands

    {calc,plot,annotate,label,info,utils,stats,convert,trim}
      calc                Calculator
      plot                Charts plotter
      annotate            Digital score annotator
      label               JSON file labeler. Annotate JSON file with given
                          labels
      info                JSON data info.
      utils               Auxiliary tools
      stats               Statistical tools
      convert             JSON file converter. Convert JSON to CSV file
      trim                JSON file trimmer. Trim given measures

  Further information available at https://github.com/msampaio/rpScripts

For subcommands help, try ``rpscripts 'subcommand' -h``. For instance:

.. code-block:: console

  rpscripts plot -h

For further information about these programs, check :doc:`programs/index`.

Quick start
^^^^^^^^^^^

For a quick start, run the commands below. They will create ``score.json`` file and plot all available charts:

.. code-block:: console

  rpscripts calc score.mxl
  rpscripts plot -a score.json

.. _package_usage:

Package usage
-------------

The user can import the entire :doc:`rpscripts` or its main classes:

.. code-block:: python

  # import rpscripts package
  import rpscripts as rp

  # import only the desired classes
  from rpscripts import Partition, ParsemaeSegment, RPData

Main classes
^^^^^^^^^^^^

The RPScripts main classes are:

.. autoclass:: rpscripts.Partition
.. autoclass:: rpscripts.ParsemaeSegment
.. autoclass:: rpscripts.RPData

Calculator module usage
^^^^^^^^^^^^^^^^^^^^^^^

The snippet below parses a given ``score.mxl`` digital score file, calculates the rhythmic partitions and saves the data into the ``score.json`` file.

.. code-block:: python

  import music21
  import pandas

  import rpscripts as rp

  # Generate Music21 score stream
  sco = music21.converter.parse('score.mxl')
  segment = rp.ParsemaeSegment()
  segment.make_from_music21_score(sco)

  # Get partitions data as a dictionary
  dic, values_ape = segment.get_data()

  # Generate Pandas Dataframe object and export to CSV.

  df = pandas.DataFrame(dic)
  df.to_csv('score.csv')

  # Save data as a JSON file.
  rpdata = segment.make_rpdata('score.json')
  rpdata.save_to_file()

Plotter module usage
^^^^^^^^^^^^^^^^^^^^

The snippet below loads a given ``score.json`` (generated in the previous snippet) and plots simple and bubble partitiograms.

.. code-block:: python

  import pandas

  import rpscripts as rp

  # Load the JSON data generated in the previous snippet.
  rpdata = rp.RPData('score.json')

  # Plot simple partitiogram (Jupyter).
  # Jupyter needs %matplotlib inline to render the chart
  chart = rp.plotter.SimplePartitiogramPlotter(rpdata)
  chart.plot()

  # Generate bubble partitiogram and save to file.
  chart2 = rp.plotter.BubblePartitiogramPlotter(rpdata)
  chart2.plot()
  chart2.save()

  # Change a default constant
  rp.plotter.LABELS_SIZE = 20

Partition class usage
^^^^^^^^^^^^^^^^^^^^^

For ``rpscripts.Partition`` usage:

.. code-block:: python

  import rpscripts as rp

  # Instantiate an object Partition
  p = rp.Partition('1^2.2')

  # Get agglomeration and dispersion indexes
  p.get_agglomeration_index()
  p.get_dispersion_index()

Hacking
^^^^^^^

The user can use RP Scripts' classes to calculate rhythmic partitioning data and plot charts.

For instance, the code below extends the :any:`AbstractTimePlotter` to plot the number of parts of partitions in time.

.. code-block:: python

  import rpscripts as rp

  def count_parts(rpdata: rp.RPData) -> int:
    return [rp.Partition(p).get_parts_size() for p in rpdata.partitions]

  class PartsSizeTimePlot(rp.plotter.AbstractTimePlotter):
    def __init__(self, rpdata: rp.RPData,
                 image_format='svg', close_bubbles=False,
                 show_labels=False) -> None:

        self.name = 'parts_size'
        super().__init__(rpdata, image_format, show_labels)
        self.parts_size = count_parts(rpdata)

    def plot(self):
        plt.clf()
        plt.plot(self.x_values, self.parts_size)
        self.make_xticks()
        plt.ylabel('Parts size')

        return super().plot()

  rpdata = rp.RPData('score.json')
  pstp = PartsSizeTimePlot(rpdata)
  pstp.plot()
  pstp.save()