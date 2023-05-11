'''This module provides a few statistical data about the given filename.'''

from matplotlib import pyplot as plt
import pandas
from .lib.base import GeneralSubparser, RPData, file_rename


def main(filename: str, no_plot: bool, split_labels: bool) -> None:
    '''Make histogram and print statistical summary of agglomeration and dispersion indexes.'''

    rp_data = RPData(filename)
    df = pandas.DataFrame(rp_data.data)
    cols = ['Agglomeration', 'Dispersion']

    print('Statistical summary: full')
    print(df[cols].describe().round(2))

    if not no_plot:
        axes = df[cols].hist()
        for c, ax in zip(cols, axes[0]):
            ax.set_xlabel('{} index'.format(c))
            ax.set_ylabel('Number of events')

        plt_filename = file_rename(filename, 'svg', 'histogram')

        print('Saving file {}...'.format(plt_filename))
        plt.savefig(plt_filename)

    if split_labels and rp_data.labels:
        df['Label'] = rp_data.labels
        new_cols = cols[:]
        new_cols.append('Label')

        _df = df[new_cols].groupby('Label')
        for label, _df in _df:
            print('\nLabel: {}'.format(label))
            print(_df.describe().round(2))

        if not no_plot:
            for c in cols:
                plt.clf()
                _df = df[[c, 'Label']]
                _df.plot.box(column=c, by='Label', grid=True)
                plt.ylabel('{} index'.format(c))
                plt.title('')
                plt.xlabel('Labels')
                plt.tight_layout()
                plt.savefig(file_rename(filename, 'svg', 'label-{}-boxplot').format(c.lower()))

                # plt.clf()
                # grouped = df[[c, 'Label']].groupby('Label')
                # ax = grouped.boxplot(subplots=False, rot=90)
                # plt.ylabel('{} index'.format(c))
                # plt.tight_layout()
                # ax.get_figure().savefig(file_rename(filename, 'svg', 'label-{}-boxplot').format(c.lower()))


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
        main(args.filename, args.no_plot, args.labels)