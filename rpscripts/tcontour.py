'''This module generates complexity map and adds level and sublevel complexity to given csv rhythmic partitioning data.

For further information, see Daniel Moreira (2015 and 2019).

Moreira, Daniel. 2015. "Perspectivas para a análise textural a partir da mediação entre a teoria dos contornos e a análise particional." Dissertação de mestrado, Universidade Federal do Rio de Janeiro.

Moreira, Daniel. 2019. "Textural Design: A Compositional Theory for the Organization of Musical Texture." Ph.D. Thesis, Universidade Federal do Rio de Janeiro.
'''


import statsmodels.nonparametric.smoothers_lowess

from rpscripts.config import LATTICE_MAP_PATH
from rpscripts.plotter import AbstractTimePlotter

from .lib.base import CustomException, GeneralSubparser, RPData, file_rename, load_json_file
from .lib.partition import Partition


class ExtendedPartition(Partition):
    '''Extend Partition class to handle textural contour.'''

    def get_complexity_level(self, complexity_map: dict) -> int:
        '''Return partition's complexity level.'''

        density_number = self.get_density_number()
        if density_number == 0:
            return 0
        try:
            m = complexity_map[str(density_number)]
        except:
            raise CustomException('The lattice map has not the density number {}'.format(density_number))
        ind = m.index(int(self.get_dispersion_index()))
        return density_number + ind

class ContourPoint(object):
    '''Contour point class. It handles complexity level and sublevel'''

    def __init__(self, level=None, sublevel=None, partition_str=None) -> None:
        self.level = level
        self.sublevel = sublevel
        self.partition_str = partition_str

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ContourPoint):
            if other.level == None:
                return False
            return self.level == other.level and self.sublevel == other.sublevel
        return False

    def __gt__(self, other: object) -> bool:
        if isinstance(other, ContourPoint):
            if other.level == None:
                return True
            if self.level == None:
                return False
            diff_level = self.level > other.level
            same_level = self.level == other.level and self.sublevel > other.sublevel
            return diff_level or same_level

    def __lt__(self, other: object) -> bool:
        if isinstance(other, ContourPoint):
            if other.level == None:
                return True
            if self.level == None:
                return False
            diff_level = self.level < other.level
            same_level = self.level == other.level and self.sublevel < other.sublevel
            return diff_level or same_level

    def __ge__(self, other: object) -> bool:
        if isinstance(other, ContourPoint):
            equal = self == other
            diff_level = self.level > other.level
            same_level = self.level == other.level and self.sublevel > other.sublevel
            return any([equal, diff_level, same_level])

    def __repr__(self) -> str:
        if self.sublevel == 0:
            label = str(self.level)
        else:
            label = '{}-{}'.format(self.level, self.sublevel)

        return '<CP {} ({})>'.format(label, self.partition_str)


class Contour(object):
    '''Contour class. It handles the contour points.'''

    def __init__(self, str_partitions, complexity_map, locations, indexes) -> None:
        self.str_partitions = str_partitions
        self.str_partitions_set = list(set(self.str_partitions))
        self.partitions_set = [ExtendedPartition(p) for p in self.str_partitions_set]
        self.partitions_info = {}
        self.indexes = indexes
        self.locations = locations
        self.contour_map = {}
        self.levels_map = {}
        self.levels_keys = []
        self.levels_seq = []
        self.sublevels_seq = []
        self.sublevels_max = None
        self.cseg = []
        self.complexity_map = complexity_map
        self.complexity_data = []
        self.level_sublevel_seq = []
        self.reduction_check = []

        self.make_maps(complexity_map)
        self.make_contour()
        self.make_complexity_data()

    def __repr__(self) -> str:
        return '<C {}>'.format(', '.join(map(lambda el: '{}-{} ({})'.format(*el), self.cseg)))

    def make_maps(self, complexity_map: dict) -> None:
        '''Make and set levels map and partitions info about complexity level and number of parts.'''

        self.partitions_info = {}
        self.levels_map = {}

        for partition in self.partitions_set:
            n_parts = len(partition.parts)
            str_partition = partition.as_string()
            complexity_level = partition.get_complexity_level(complexity_map)

            if complexity_level not in self.levels_map.keys():
                self.levels_map[complexity_level] = set([])
            self.levels_map[complexity_level].add(n_parts)

            self.partitions_info.update({
                str_partition: (complexity_level, n_parts)
            })

        self.levels_map = {k: self.levels_map[k] for k in sorted(self.levels_map.keys())}
        self.levels_keys = list(self.levels_map.keys())

    def make_contour(self) -> None:
        '''Make the contour from the available complexity levels and partitions information.'''

        self.contour_map = {}
        for str_partition, (level, n_parts) in self.partitions_info.items():
            n_parts_set = self.levels_map[level]
            contour_level = self.levels_keys.index(level)
            contour_sublevel = 0
            if len(n_parts_set) > 1:
                contour_sublevel = list(n_parts_set).index(n_parts) + 1

            self.contour_map.update({
                str_partition: (contour_level, contour_sublevel)
            })

        self.cseg = []
        for str_partition in self.str_partitions:
            (contour_level, contour_sublevel) = self.contour_map[str_partition]
            cp = ContourPoint(contour_level, contour_sublevel, str_partition)
            self.cseg.append(cp)
            self.levels_seq.append(contour_level)
            self.sublevels_seq.append(contour_sublevel)
        self.sublevels_max = max(self.sublevels_seq)
        self.reduction_check = [True] * len(self.cseg)

    def make_complexity_data(self) -> None:
        '''Make the complexity data from the available sequences of complexity levels and sublevels.'''

        self.complexity_data = []
        for level, sublevel in zip(self.levels_seq, self.sublevels_seq):
            contour_repr = str(level)
            if int(sublevel) == 0:
                contour_repr = '{}-{}'.format(level, sublevel)
            self.level_sublevel_seq.append(contour_repr)
            self.complexity_data.append([
                level,
                sublevel,
                contour_repr
            ])


class ExtendedRPData(RPData):
    '''Extend RPData class to add complexity (contour) data.'''

    def add_complexity_data(self, contour: Contour):
        rows = contour.level_sublevel_seq
        self.complexity = rows
        self.save_to_file()


class ContourPlot(AbstractTimePlotter):
    '''Contour Plot class.'''

    def __init__(self, contour: Contour, rpdata: RPData, image_format='svg', show_labels=False, run_lowess=False, lowess_degree=0.05) -> None:
        self.name = 'complexity'
        self.contour = contour
        self.run_lowess = run_lowess
        self.lowess_degree = lowess_degree
        super().__init__(rpdata, image_format, show_labels)

    def plot(self):
        level_seq = self.contour.levels_seq
        sublevel_seq = self.contour.sublevels_seq
        sublevel_max = self.contour.sublevels_max

        # x_values = list(map(parse_fraction, contour.locations))
        if sublevel_max > 0:
            y_vals = [(level + sublevel) / (sublevel_max * 2) for level, sublevel in zip(level_seq, sublevel_seq)]
        else:
            y_vals = level_seq

        self.axis.plot(self.x_values[:-1], y_vals)

        if self.run_lowess:
            lowess = statsmodels.nonparametric.smoothers_lowess.lowess(y_vals, self.x_values[:-1], frac=self.lowess_degree)[:, 1]
            self.axis.plot(self.x_values[:-1], lowess)
            self.axis.legend(['Contour', 'Lowess {}'.format(self.lowess_degree)])

        self.axis.set_ylabel('Contour points')
        self.make_xticks()

        return super().plot()


def make_contour_object(rpdata: RPData, complexity_map: dict) -> Contour:
    '''Return a contour object.'''

    partitions = rpdata.partitions
    locations = rpdata.data['Global offset']
    indexes = rpdata.data['Index']

    return Contour(partitions, complexity_map, locations, indexes)


class Subparser(GeneralSubparser):
    '''Implements argparser.'''

    def setup(self) -> None:
        self.program_name = 'tcontour'
        self.program_help = 'Textural contour calculator and plotter'

    def add_arguments(self) -> None:
        self.parser.add_argument("-fl", "--show_form_labels", help = "Draw vertical lines to display given form labels. It demands a previous labeled file. Check rpscripts labels -h' column", default=False, action='store_true')

        self.parser.add_argument("-np", "--no_plot", help='No Plot chart', default=False, action='store_true')
        self.parser.add_argument("-o", "--lowess", help='Plot LOWESS', default=False, action='store_true')
        self.parser.add_argument("--lowess_degree", help='Lowess degree', default=0.05, type=float)

    def handle(self, args):
        json_filename = args.filename
        cdic_filename = LATTICE_MAP_PATH

        print('Loading complexity_map in {}...'.format(cdic_filename))
        try:
            complexity_map = load_json_file(cdic_filename)
        except:
            raise CustomException('Failure on complexity map loading...')

        print('Generating texture contour...')

        rpdata = ExtendedRPData(args.filename)

        contour = make_contour_object(rpdata, complexity_map)

        rpdata.add_complexity_data(contour)


        if not args.no_plot:
            figname = file_rename(json_filename, 'svg', 'complexity')
            print('Saving texture contour plot in {}...'.format(figname))

            contour_plot = ContourPlot(contour, rpdata, 'svg', args.show_form_labels, args.lowess, lowess_degree=args.lowess_degree)
            contour_plot.plot()
            contour_plot.save()
