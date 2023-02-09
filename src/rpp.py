from fractions import Fraction
from matplotlib import pyplot as plt
import argparse
import pandas


POW_DICT = {
    '1': '\N{superscript one}',
    '2': '\N{superscript two}',
    '3': '\N{superscript three}',
    '4': '\N{superscript four}',
    '5': '\N{superscript five}',
    '6': '\N{superscript six}',
    '7': '\N{superscript seven}',
    '8': '\N{superscript eight}',
    '9': '\N{superscript nine}',
}


class CustomException(Exception):
    pass


def parse_fraction(value):
    if isinstance(value, str):
        if '/' in value:
            return Fraction(*list(map(int, value.split('/'))))
    return value


def parse_index(v):
    a, b = v.split('+')
    return (a, parse_fraction(b))


def parse_pow(partition):
    partition = str(partition)
    parts = partition.split('.')
    new_parts = []
    for part in parts:
        value = part.split('^')
        if len(value) > 1:
            base, exp = value
            _exp = []
            for el in list(exp):
                _exp.append(POW_DICT[el])
            value = base + ''.join(_exp)
        else:
            value = value[0]
        new_parts.append(value)
    return '.'.join(new_parts)


def make_dataframe(fname):
    df = pandas.read_csv(fname)
    for c in ['Agglomeration', 'Dispersion']:
        df[c] = df[c].apply(float)

    for c in ['Offset', 'Global offset', 'Duration']:
        df[c] = df[c].apply(parse_fraction)

    df.index = df['Index'].apply(parse_index).values
    df['Partition'] = df['Partition'].apply(parse_pow)
    df = df.drop('Index', axis=1)

    return df


def invert_dataframe(df):
    inverted = pandas.DataFrame([
        df.Agglomeration * -1,
        df.Dispersion,
    ], index=['Agglomeration', 'Dispersion'], columns=df.index).T
    return inverted


class AbstractPlotter(object):
    def __init__(self, dataframe, image_format='svg', basename=None) -> None:
        self.dataframe = dataframe
        self.image_format = image_format
        self.basename = basename
        self.outfile = '{}-{}.{}'.format(self.basename, self.name, self.image_format)
        self.name = None

    def plot(self):
        pass

    def xticks_adjust(self):
        plt.xticks(rotation=90)
        plt.tight_layout()

    def save(self):
        if self.image_format == 'svg':
            plt.savefig(self.outfile)
        else:
            plt.savefig(self.outfile, dpi=RESOLUTION)
        plt.close()


class AbstractPartitiogramPlotter(AbstractPlotter):
    def __init__(self, dataframe, image_format='svg', basename=None, with_labels=True) -> None:
        super().__init__(dataframe, image_format, basename)
        self.with_labels = with_labels


class AbstractIndexogramPlotter(AbstractPlotter):
    def __init__(self, dataframe, image_format='svg', basename=None, close_bubbles=False) -> None:
        super().__init__(dataframe, image_format, basename)
        self.close_bubbles = close_bubbles
        self.inverted_dataframe = invert_dataframe(self.dataframe)


class SimplePartitiogramPlotter(AbstractPartitiogramPlotter):
    def __init__(self, dataframe, image_format='svg', basename=None, with_labels=True) -> None:
        self.name = 'simple-partitiogram'
        super().__init__(dataframe, image_format, basename, with_labels)

    def plot(self):
        seq = [
            [partition, len(_df), _df.Agglomeration.iloc[0], _df.Dispersion.iloc[0]]
            for partition, _df in self.dataframe.groupby('Partition')
        ]
        columns=['Partition', 'Quantity', 'Agglomeration', 'Dispersion']
        df = pandas.DataFrame(seq, columns=columns)

        plt.clf()
        ax = df.plot(
            grid=True,
            kind='scatter',
            x='Agglomeration',
            y='Dispersion',
        )

        if self.with_labels:
            factor = 1.025
            fontsize = 12

            for _, s in df.iterrows():
                x = s['Agglomeration']
                y = s['Dispersion']
                v = s['Partition']
                plt.text(x * factor, y * factor , v, fontsize=fontsize)

        self.save()


class SimpleIndexogramPlotter(AbstractIndexogramPlotter):
    def __init__(self, dataframe, image_format='svg', basename=None, close_bubbles=False) -> None:
        self.name = 'simple-indexogram'
        super().__init__(dataframe, image_format, basename, close_bubbles)

    def plot(self):
        def draw_vertical_line(row, x):
            ymin = row[1].Agglomeration * -1
            ymax = row[1].Dispersion
            plt.vlines(x=x, ymin=ymin, ymax=ymax, linestyles='dotted', colors='C3')

        plt.clf()

        ax = self.inverted_dataframe.plot(grid=True)
        ax.set_ylabel('Values\n<- aggl./disp. ->')
        ax.set_xlabel('Positions (measure, offset)')

        # draw vertical lines to close the bubbles
        if self.close_bubbles:
            rest_segment = False
            last_row = None
            for i, row in enumerate(dataframe.iterrows()):
                _agg = row[1].Agglomeration
                if pandas.isnull(_agg):
                    if not rest_segment:
                        if last_row:
                            x = i - 1
                            draw_vertical_line(last_row, x)
                        rest_segment = True
                else:
                    if rest_segment:
                        x = i
                        draw_vertical_line(row, x)
                        rest_segment = False
                last_row = row

        self.xticks_adjust()
        self.save()


class StemIndexogramPlotter(AbstractIndexogramPlotter):
    def __init__(self, dataframe, image_format='svg', basename=None, close_bubbles=False) -> None:
        self.name = 'stem-indexogram'
        super().__init__(dataframe, image_format, basename, close_bubbles)

    def plot(self):
        ind = ['({}, {})'.format(a, b) for a, b in self.inverted_dataframe.index.values]
        size = len(ind)
        step = int(size / 8)

        plt.clf()
        plt.stem(ind, self.inverted_dataframe.Dispersion.values, markerfmt=' ')
        plt.stem(ind, self.inverted_dataframe.Agglomeration.values, markerfmt=' ', linefmt='C1-')
        plt.xticks(range(0, size, step))
        plt.xlabel('Positions (measure, offset)')
        plt.ylabel('Values\n<- aggl./disp. ->')
        plt.grid()
        plt.legend(self.inverted_dataframe.columns)

        self.xticks_adjust()
        self.save()


class StairsIndexogramPlotter(AbstractIndexogramPlotter):
    def __init__(self, dataframe, image_format='svg', basename=None, close_bubbles=False) -> None:
        self.name = 'stairs-indexogram'
        super().__init__(dataframe, image_format, basename, close_bubbles)

    def plot(self):
        ind = ['({}, {})'.format(a, b) for a, b in self.inverted_dataframe.index.values]
        size = len(ind)
        step = int(size / 8)

        plt.clf()
        plt.stairs(self.inverted_dataframe.Dispersion.values[:-1], ind)
        plt.stairs(self.inverted_dataframe.Agglomeration.values[:-1], ind)
        plt.xticks(range(0, size, step))
        plt.xlabel('Positions (measure, offset)')
        plt.ylabel('Values\n<- aggl./disp. ->')
        plt.grid()
        plt.legend(self.inverted_dataframe.columns)

        self.xticks_adjust()
        self.save()


class CombinedIndexogramPlotter(AbstractIndexogramPlotter):
    def __init__(self, dataframe, image_format='svg', basename=None, close_bubbles=False) -> None:
        self.name = 'combined-indexogram'
        super().__init__(dataframe, image_format, basename, close_bubbles)

    def plot(self):
        series = self.inverted_dataframe.Dispersion + self.inverted_dataframe.Agglomeration

        plt.clf()
        ax = series.plot(grid=True)
        ax.set_ylabel('Values\n(d - a)')
        ax.set_xlabel('Positions (measure, offset)')

        self.xticks_adjust()
        self.save()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                    prog = 'rpp',
                    description = "Plot Partitiogram and Indexogram from RPC's output",
                    epilog = 'Rhythmic Partitioning Plotter')

    parser.add_argument('filename')
    parser.add_argument("-f", "--img_format", help = "Image format (svg, jpg or png). Default=svg", default='svg')
    parser.add_argument("-r", "--resolution", help = "PNG image resolution. Default=300", default=300)
    parser.add_argument("-a", "--all", help = "Plot all available charts", action='store_true')
    parser.add_argument("-c", "--close_bubbles", help = "Close indexogram bubbles.", default=False, action='store_true')
    parser.add_argument("-e", "--stem", help = "Indexogram as a stem chart", action='store_true')
    parser.add_argument("-t", "--stairs", help = "Indexogram as a stair chart", action='store_true')
    parser.add_argument("-b", "--combined", help = "Indexogram as a combination of aglomeration and dispersion", action='store_true')
    args = parser.parse_args()

    try:
        RESOLUTION = int(args.resolution)
    except:
        raise CustomException('Resolution must be an integer from 0 to 1200')

    close_bubbles = args.close_bubbles
    if close_bubbles:
        close_bubbles = True

    image_format = args.img_format.lower()
    if image_format not in ['svg', 'jpg', 'png']:
        raise CustomException('Image format must be svg, jpg or png.')

    fname = args.filename

    print('Running script on {} filename...'.format(fname))

    indexogram_classes = [
        SimpleIndexogramPlotter,
        StemIndexogramPlotter,
        StairsIndexogramPlotter,
        CombinedIndexogramPlotter
    ]

    try:
        dataframe = make_dataframe(fname)
        basename = fname.rstrip('.csv')

        SimplePartitiogramPlotter(dataframe, image_format, basename).plot()

        if args.all:
            for cls in indexogram_classes:
                cls(dataframe, image_format, basename).plot()
        elif args.stem:
            StemIndexogramPlotter(dataframe, image_format, basename).plot()
        elif args.stairs:
            StairsIndexogramPlotter(dataframe, image_format, basename).plot()
        elif args.combined:
            CombinedIndexogramPlotter(dataframe, image_format, basename).plot()
        else:
            close_bubbles = False
            if args.close_bubbles:
                close_bubbles = True
            SimpleIndexogramPlotter(dataframe, image_format, basename, close_bubbles).plot()

    except:
        raise CustomException('Something wrong with given csv file.')