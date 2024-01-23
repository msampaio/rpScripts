'''This module provides a few statistical data about the given filename.'''

from copy import deepcopy
from matplotlib import pyplot as plt
import pandas
from .lib.base import GeneralSubparser, RPData, file_rename


class Statistics(object):
    '''Auxiliary class for statistics calculus.'''

    def __init__(self, rpdata: RPData, name: str, image_format='svg') -> None:
        self.rpdata = deepcopy(rpdata)
        self.image_format = image_format
        self.name = name
        self.outname = file_rename(self.rpdata.path, self.image_format, self.name)
        self.subplots = None
        self.dataframe = pandas.DataFrame(rpdata.data)
        self.data = None
        self.columns = None
        self.is_index = False

    def get_histograms(self, no_plot:bool, split_labels: bool) -> None:
        '''Make histogram and print statistical summary.'''

        self.name = '{}-{}'.format(self.name, 'histogram')
        self.outname = file_rename(self.rpdata.path, self.image_format, self.name)

        print('Statistical summary: full')
        print(self.data.describe().round(2))

        if not no_plot:
            axes = self.data.hist()
            for c, ax in zip(self.columns, axes[0]):
                if self.is_index:
                    ax.set_xlabel('{} index'.format(c))
                else:
                    ax.set_xlabel(c)
                ax.set_ylabel('Number of events')

            print('Saving file {}...'.format(self.outname))
            plt.savefig(self.outname)

        if split_labels and self.rpdata.labels:
            self.data['Label'] = self.rpdata.labels
            new_cols = self.columns[:]
            new_cols.append('Label')

            _df = self.data[new_cols].groupby('Label')
            for label, _df in _df:
                print('\nLabel: {}'.format(label))
                print(_df.describe().round(2))

            if not no_plot:
                for c in self.columns:
                    plt.clf()
                    _df = self.data[[c, 'Label']]
                    _df.plot.box(column=c, by='Label', grid=True)
                    if self.is_index:
                        plt.ylabel('{} index'.format(c))
                    else:
                        plt.ylabel(c)
                    plt.title('')
                    plt.xlabel('Labels')
                    plt.tight_layout()
                    plt.savefig(file_rename(self.outname, 'svg', 'label-{}-boxplot').format(c.lower()))


class AgglomerationDispersionStatistics(Statistics):
    def __init__(self, rpdata: RPData, image_format='svg') -> None:
        name = 'agglomeration-dispersion'
        self.is_index = True
        super().__init__(rpdata, name, image_format)

    def get_histograms(self, no_plot:bool, split_labels: bool) -> None:
        '''Make histogram and print statistical summary of agglomeration and dispersion indexes.'''

        self.columns = ['Agglomeration', 'Dispersion']
        self.data = self.dataframe[self.columns]

        super().get_histograms(no_plot, split_labels)


class PartsDensityNumberStatistics(Statistics):
    def __init__(self, rpdata: RPData, image_format='svg') -> None:
        name = 'parts-statistics'
        super().__init__(rpdata, name, image_format)

    def get_histograms(self, no_plot:bool, split_labels: bool) -> None:
        '''Make histogram and print statistical summary of number of parts and density number.'''

        self.columns = ['Number of parts', 'Density number']
        self.data = pandas.DataFrame(self.rpdata.get_number_of_parts_and_density_numbers(), columns=self.columns)

        super().get_histograms(no_plot, split_labels)


class Subparser(GeneralSubparser):
    '''Implements argparser.'''

    def setup(self) -> None:
        self.program_name = 'stats'
        self.program_help = 'Statistical tools'

    def add_arguments(self) -> None:
        pass
        self.parser.add_argument("-np", "--no_plot", help = "No plot charts", action='store_true')
        self.parser.add_argument("-l", "--labels", help = "Split labels", action='store_true')

    def handle(self, args):
        rpdata = RPData(args.filename)

        ad_statistics = AgglomerationDispersionStatistics(rpdata, 'svg')
        ad_statistics.get_histograms(args.no_plot, args.labels)

        pc_statistics = PartsDensityNumberStatistics(rpdata, 'svg')
        pc_statistics.get_histograms(args.no_plot, args.labels)