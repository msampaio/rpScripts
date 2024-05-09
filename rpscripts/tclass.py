'''This module generates textural classes data and chart.

For further information about textural classes, see Daniel Moreira (2019).

Moreira, Daniel. 2019. "Textural Design: A Compositional Theory for the Organization of Musical Texture." Ph.D. Thesis, Universidade Federal do Rio de Janeiro.
'''

from collections import Counter
import itertools
import matplotlib.pyplot as plt

from rpscripts.plotter import AbstractRadarPlotter, AbstractTimePlotter

from .lib.base import GeneralSubparser, RPData, file_rename
from .lib.partition import Partition


FACTOR = 2000
LABELS_SIZE = 15
LABELS_DISTANCE = 1.025
TEXTURAL_CLASSES = ['R', 'L', 'B', 'Lx', 'LB', 'By', 'LxB', 'LBy', 'LxBy']


# Auxiliary functions

def get_partition_texture_class(str_partition: str) -> str:
    '''Get the textural class of a given partition.'''

    partition = ExtendedPartition(str_partition)
    return partition.get_texture_class()


def are_classes_neighbors(class1: str, class2: str) -> bool:
    '''Check if both classes are neighbors.'''

    ind1 = TEXTURAL_CLASSES.index(class1)
    ind2 = TEXTURAL_CLASSES.index(class2)
    return ind1 + 1 == ind2 or ind1 - 1 == ind2

# Classes

class ExtendedPartition(Partition):
    '''Extend Partition class to handle partition classes.'''

    def get_texture_class(self):
        '''Get the partition's textural class.'''

        lines = 0
        blocks = 0

        if self.parts:
            for el in sorted(self.parts):
                if el == 1:
                    lines += 1
                elif el > 1:
                    blocks += 1

            if lines > 2:
                lines = 2
            if blocks > 2:
                blocks = 2
        else:
            lines, blocks = 0, 0

        dic = {
            (0, 0): 'R',
            (1, 0): 'L',
            (0, 1): 'B',
            (1, 1): 'LB',
            (2, 0): 'Lx',
            (0, 2): 'By',
            (2, 1): 'LxB',
            (1, 2): 'LBy',
            (2, 2): 'LxBy',
        }

        return dic[(lines, blocks)]


class ExtendedRPData(RPData):
    '''Extend RPData class to add tclass data.'''

    def set_textural_classes(self) -> None:
        '''Set textural class into RPData.'''

        self.tclass = list(map(get_partition_texture_class, self.partitions))

    def make_counting_chart(self, filename=None) -> None:
        '''Save counting chart into given filename.'''

        counter = Counter(self.tclass)
        data = [counter[t] for t in TEXTURAL_CLASSES]
        self.axis.bar(TEXTURAL_CLASSES, data)
        self.axis.ylabel('Number of events')
        self.axis.xlabel('Textural class')
        self.axis.grid()
        if not filename:
            filename = file_rename(self.path, 'svg', 'classes-counter')
        plt.savefig(filename)


class TexturalClassPlot(AbstractTimePlotter):
    '''Textural Class Plot class.'''

    def __init__(self, rpdata: RPData, image_format='svg', show_labels=False, as_step=False) -> None:
        self.name = 'classes'
        self.as_step = as_step
        super().__init__(rpdata, image_format, show_labels)

    def plot(self):
        y_values = [TEXTURAL_CLASSES.index(x) for x in self.rpdata.tclass]

        # plot or step function
        if self.as_step:
            self.axis.step(self.x_values[:-1], y_values, where='post')
        else:
            self.axis.plot(self.x_values[:-1], y_values)

        self.make_xticks()

        # Make yticks
        yticks_ticks = list(range(len(TEXTURAL_CLASSES)))
        yticks_ticks.insert(0, -0.5)
        yticks_ticks.append(yticks_ticks[-1] + 0.5)
        yticks_labels = TEXTURAL_CLASSES[:]
        yticks_labels.insert(0, '')
        yticks_labels.append('')
        self.axis.set_yticks(ticks=yticks_ticks, labels=yticks_labels)


        self.axis.set_ylabel('Partitions classes')
        self.axis.set_xlabel('Positions (measure number + offset)')
        return super().plot()


class TexturalClassRadarPlotter(AbstractRadarPlotter):
    def __init__(self, rpdata: RPData, image_format='svg') -> None:
        self.name = 'classes-radar'
        super().__init__(rpdata, image_format)
        self.name = 'classes-radar'

        # Make data
        if self.rpdata.labels:
            dic = {label: [0] * len(TEXTURAL_CLASSES) for label in set(self.rpdata.labels)}

            ordered_labels = []

            for tclass, label in zip(self.rpdata.tclass, self.rpdata.labels):
                ind = TEXTURAL_CLASSES.index(tclass)
                dic[label][ind] += 1
                if label not in ordered_labels:
                    ordered_labels.append(label)
        else:
            label = 'All sections'
            dic = {label: [0] * len(TEXTURAL_CLASSES)}

            ordered_labels = [label]

            for tclass in self.rpdata.tclass:
                ind = TEXTURAL_CLASSES.index(tclass)
                dic[label][ind] += 1

        # order dic itemss
        _items = []
        for label in ordered_labels:
            _items.append((label, dic[label]))
        self.data = [(k, [el / sum(v) for el in v]) for k, v in _items]
        self.data.insert(0, TEXTURAL_CLASSES)


class Subparser(GeneralSubparser):
    '''Implements argparser.'''

    def setup(self) -> None:
        self.program_name = 'tclass'
        self.program_help = 'Textural class calculator and plotter'

    def add_arguments(self) -> None:
        self.parser.add_argument("-np", "--no_plot", help='No textural class chart', default=False, action='store_true')
        self.parser.add_argument("-ng", "--no_graph", help='No graph chart', default=False, action='store_true')
        self.parser.add_argument("-fl", "--show_form_labels", help = "Draw vertical lines to display given form labels. It demands a previous labeled file. Check rpscripts labels -h' column", default=False, action='store_true')
        self.parser.add_argument("-s", "--as_step", help='Step chart', default=False, action='store_true')
        self.parser.add_argument("-c", "--counting_chart", help = "Counting chart", default=False, action='store_true')
        self.parser.add_argument("-r", "--radar_chart", help = "Radar chart", default=False, action='store_true')

    def handle(self, args):
        rpdata = ExtendedRPData(args.filename)
        rpdata.set_textural_classes()
        rpdata.save_to_file()

        if not args.no_plot:
            figname = file_rename(args.filename, 'svg', 'classes')
            print('Saving textural classes plot in {}...'.format(figname))

            tclass_plot = TexturalClassPlot(rpdata, 'svg', args.show_form_labels, args.as_step)
            tclass_plot.plot()
            tclass_plot.save()

        # Colors: https://digitalsynopsis.com/design/minimal-web-color-palettes-combination-hex-code/
        if not args.no_graph:
            relations = {
                (a, b): 'solid' if are_classes_neighbors(a, b) else 'dashed'
             for a, b in itertools.permutations(TEXTURAL_CLASSES, 2)}
            # relations = {
            #     (a, b): '#C06C84' if are_classes_neighbors(a, b) else '#355C7D'
            #  for a, b in itertools.permutations(TEXTURAL_CLASSES, 2)}

            figname = file_rename(args.filename, 'gv', 'classes-graph')
            print('Saving textural classes graph in {}...'.format(figname))
            dot = rpdata.make_class_graph('tclass', relations)
            dot.render(figname, format='svg')

        if args.counting_chart:
            figname = file_rename(args.filename, 'svg', 'classes-counter')
            print('Saving textural classes counting chart in {}...'.format(figname))
            rpdata.make_counting_chart(figname)

        if args.radar_chart:
            radar_plot = TexturalClassRadarPlotter(rpdata)
            radar_plot.plot()
            radar_plot.save()