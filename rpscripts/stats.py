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

    def get_histograms(self, no_plot:bool, split_labels: bool) -> None:
        '''Make histogram and print statistical summary of agglomeration and dispersion indexes.'''

        cols = ['Agglomeration', 'Dispersion']

        print('Statistical summary: full')
        print(self.dataframe[cols].describe().round(2))

        if not no_plot:
            axes = self.dataframe[cols].hist()
            for c, ax in zip(cols, axes[0]):
                ax.set_xlabel('{} index'.format(c))
                ax.set_ylabel('Number of events')

            print('Saving file {}...'.format(self.outname))
            plt.savefig(self.outname)

        if split_labels and self.rpdata.labels:
            self.dataframe['Label'] = self.rpdata.labels
            new_cols = cols[:]
            new_cols.append('Label')

            _df = self.dataframe[new_cols].groupby('Label')
            for label, _df in _df:
                print('\nLabel: {}'.format(label))
                print(_df.describe().round(2))

            if not no_plot:
                for c in cols:
                    plt.clf()
                    _df = self.dataframe[[c, 'Label']]
                    _df.plot.box(column=c, by='Label', grid=True)
                    plt.ylabel('{} index'.format(c))
                    plt.title('')
                    plt.xlabel('Labels')
                    plt.tight_layout()
                    plt.savefig(file_rename(self.outname, 'svg', 'label-{}-boxplot').format(c.lower()))


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

        statistics = Statistics(rpdata, 'histogram', 'svg')
        statistics.get_histograms(args.no_plot, args.labels)