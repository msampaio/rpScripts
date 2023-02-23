from fractions import Fraction
import itertools
import pickle
from matplotlib import pyplot as plt
import argparse
import pandas


# Constants
RESOLUTION = 300
MAXIMUM_POINTS_TO_LABEL = 50
LABELS_SIZE = 15
LABELS_DISTANCE = 1.025
DOTS_SIZE = 15
IMG_SIZE = list(map(lambda x: x*0.8, (8, 6)))


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


def clean_filename(s):
    '''Clean given filename.'''

    PAIRS = [
        (' - ', '-'),
        (' ', '-'),
        ('_', '-'),
        ('ç', 'c'),
        ('á', 'a'),
        ('à', 'a'),
        ('ã', 'a'),
        ('â', 'a'),
        ('ä', 'a'),
        ('é', 'e'),
        ('ê', 'e'),
        ('è', 'e'),
        ('ê', 'e'),
        ('í', 'i'),
        ('ó', 'o'),
        ('ò', 'o'),
        ('õ', 'o'),
        ('ô', 'o'),
        ('ö', 'o'),
        ('ú', 'u'),
        ('ù', 'u'),
        ('ü', 'u'),
    ]

    s = str(s).lower()

    for a, b in PAIRS:
        s = s.replace(a, b)
    return s


class AbstractPlotter(object):
    def __init__(self, dataframe, image_format='svg', basename=None) -> None:
        self.dataframe = dataframe
        self.image_format = image_format
        self.basename = basename
        self.outfile = '{}-{}.{}'.format(self.basename, self.name, self.image_format)
        self.name = None
        self.subplots = None

    def plot(self):
        f = plt.subplot()
        self.subplots = pickle.dumps(f)
        return None

    def xticks_adjust(self):
        plt.xticks(rotation=90)
        plt.tight_layout()

    def save(self, close_figure=True):
        self.get_subplots()
        if self.image_format == 'svg':
            plt.savefig(self.outfile)
        else:
            plt.savefig(self.outfile, dpi=RESOLUTION)
        if close_figure:
            plt.close()

    def get_subplots(self):
        if self.subplots:
            return pickle.loads(self.subplots)


class AbstractPartitiogramPlotter(AbstractPlotter):
    def __init__(self, dataframe, image_format='svg', basename=None, with_labels=True) -> None:
        super().__init__(dataframe, image_format, basename)
        self.with_labels = with_labels

    def _make_dataframe(self):
        seq = [
            [partition, len(_df), _df.Agglomeration.iloc[0], _df.Dispersion.iloc[0]]
            for partition, _df in self.dataframe.groupby('Partition')
        ]
        columns=['Partition', 'Quantity', 'Agglomeration', 'Dispersion']
        return pandas.DataFrame(seq, columns=columns)


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
        df = self._make_dataframe()
        plt.clf()
        df.plot(
            grid=True,
            kind='scatter',
            x='Agglomeration',
            y='Dispersion',
            s=DOTS_SIZE,
        )

        if self.with_labels:
            for _, s in df.iterrows():
                x = s['Agglomeration']
                y = s['Dispersion']
                v = s['Partition']
                plt.text(x * LABELS_DISTANCE, y * LABELS_DISTANCE , v, fontsize=LABELS_SIZE)

        return super().plot()


class BubblePartitiogramPlotter(AbstractPartitiogramPlotter):
    def __init__(self, dataframe, image_format='svg', basename=None, with_labels=True, bubble_size=2000) -> None:
        self.name = 'bubble-partitiogram'
        super().__init__(dataframe, image_format, basename, with_labels)
        self.bubble_size = bubble_size

    def plot(self):
        df = self._make_dataframe()
        df['Quantity'] = df['Quantity'] * self.bubble_size / df['Quantity'].sum()

        plt.clf()
        df.plot(
            grid=True,
            kind='scatter',
            x='Agglomeration',
            y='Dispersion',
            s='Quantity',
        )

        if self.with_labels:
            for _, s in df.iterrows():
                x = s['Agglomeration']
                y = s['Dispersion']
                v = s['Partition']
                plt.text(x * LABELS_DISTANCE, y * LABELS_DISTANCE , v, fontsize=LABELS_SIZE)

        return super().plot()


class ComparativePartitiogramPlotter(AbstractPartitiogramPlotter):
    def __init__(self, dataframe, column_1, column_2, image_format='svg', basename=None, with_labels=True) -> None:
        self.column_1 = column_1
        self.column_2 = column_2
        self.name = 'comparison-partitiogram-{}-{}'.format(clean_filename(self.column_1), clean_filename(self.column_2))
        super().__init__(dataframe, image_format, basename, with_labels)

    def plot(self):
        dic = {
            column: set(self.dataframe[self.dataframe.Label==column].Partition.unique())
            for column in [self.column_1, self.column_2]
        }

        g1 = dic[self.column_1] - dic[self.column_2]
        g1_label = 'Only in {}'.format(self.column_1)

        g2 = dic[self.column_2] - dic[self.column_1]
        g2_label = 'Only in {}'.format(self.column_2)

        g3_label = 'Both: {} and {}'.format(self.column_1, self.column_2)

        partition_map = {}

        for _, row in self.dataframe.iterrows():
            partition = row['Partition']
            if partition not in partition_map:
                partition_map[partition] = {
                    'Agglomeration': row['Agglomeration'],
                    'Dispersion': row['Dispersion'],
                }

        df = []
        for k, v in partition_map.items():
            if k in g1:
                group = g1_label
            elif k in g2:
                group = g2_label
            else:
                group = g3_label
            df.append({
                'Partition': k,
                'Agglomeration': v['Agglomeration'],
                'Dispersion': v['Dispersion'],
                'label': group
            })

        df = pandas.DataFrame(df)

        fig, ax = plt.subplots(figsize=(8,6))
        colors = ['orange', 'red', 'blue']

        for n, grp in df.groupby('label'):
            ax.scatter(
                x='Agglomeration',
                y='Dispersion',
                data=grp,
                label=n,
                s=DOTS_SIZE,
                c=colors.pop(),
            )

        if len(df.Partition.unique()) < MAXIMUM_POINTS_TO_LABEL:
            for _, s in df.iterrows():
                x = s['Agglomeration']
                y = s['Dispersion']
                v = s['Partition']
                plt.text(x * LABELS_DISTANCE, y * LABELS_DISTANCE , v, fontsize=LABELS_SIZE)

        plt.grid()
        plt.xlabel('Agglomeration')
        plt.ylabel('Dispersion')
        ax.legend(title="Label")

        fig.set_size_inches(*IMG_SIZE)

        return super().plot()


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
        return super().plot()


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
        return super().plot()


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
        return super().plot()


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
        return super().plot()


class ComparativePartitiogramMaker(AbstractPartitiogramPlotter):
    def __init__(self, dataframe, image_format='svg', basename=None, with_labels=True) -> None:
        self.name = ''
        self.plotters = []
        super().__init__(dataframe, image_format, basename, with_labels)
        if 'Label' not in self.dataframe.columns:
            raise CustomException('There is no "labels" column in the given input file.')

        self.section_labels = self.dataframe['Label'].unique()

        for a, b in itertools.combinations(self.section_labels, 2):
            cpp = ComparativePartitiogramPlotter(self.dataframe, a, b, self.image_format, self.basename, self.with_labels)
            self.plotters.append(cpp)

    def plot(self):
        for plotter in self.plotters:
            plotter.plot()

    def save(self):
        for plotter in self.plotters:
            plotter.save()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                    prog = 'rpp',
                    description = "Plot Partitiogram and Indexogram from RPC's output",
                    epilog = 'Rhythmic Partitioning Plotter')

    parser.add_argument('filename')
    parser.add_argument("-f", "--img_format", help = "Image format (svg, jpg or png). Default=svg", default='svg')
    parser.add_argument("-r", "--resolution", help = "PNG image resolution. Default=300", default=300)
    parser.add_argument("-a", "--all", help = "Plot all available charts", action='store_true')
    parser.add_argument("-u", "--bubble_partitiogram", help = "Partitiogram as a bubble chart", default=False, action='store_true')
    parser.add_argument("-w", "--without_labels", help = "Partitiogram as a bubble chart without labels", default=False, action='store_true')
    parser.add_argument("-m", "--comparative_partitiogram", help = "Comparative partitiogram. It demands an edited csv file with 'labels' column", default=False, action='store_true')
    parser.add_argument("-c", "--close_bubbles", help = "Indexogram with bubbles' closing lines", default=False, action='store_true')
    parser.add_argument("-e", "--stem", help = "Indexogram as a stem chart", action='store_true')
    parser.add_argument("-t", "--stairs", help = "Indexogram as a stair chart", action='store_true')
    parser.add_argument("-b", "--combined", help = "Indexogram as a combination of aglomeration and dispersion", action='store_true')
    parser.add_argument("--maximum_points_to_label", help = "Maximum number of points to label in bubble partitiogram chart. Default=50", default=50)
    parser.add_argument("--dots_size", help = "Dots size in simple partitiogram chart. Default=15", default=15)
    parser.add_argument("--labels_size", help = "Labels size in partitiogram chart. Default=15", default=15)
    parser.add_argument("--labels_distance", help = "Distance between points and labels in partitiogram chart. Default=1.025", default=1.025)
    args = parser.parse_args()

    try:
        RESOLUTION = int(args.resolution)
    except:
        raise CustomException('Resolution must be an integer from 0 to 1200')

    # Constants
    MAXIMUM_POINTS_TO_LABEL = float(args.maximum_points_to_label)
    DOTS_SIZE = float(args.dots_size)
    LABELS_SIZE = float(args.labels_size)
    LABELS_DISTANCE = float(args.labels_distance)
    IMG_SIZE = list(map(lambda x: x*0.8, (8, 6)))

    close_bubbles = args.close_bubbles
    if close_bubbles:
        close_bubbles = True

    with_labels = not args.without_labels
    if with_labels:
        with_labels = True

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

        ## Partitiograms
        if args.comparative_partitiogram:
            part_obj = ComparativePartitiogramMaker(dataframe, image_format, basename, with_labels)
        elif args.bubble_partitiogram or args.without_labels:
            part_obj = BubblePartitiogramPlotter(dataframe, image_format, basename, with_labels)
        else:
            part_obj = SimplePartitiogramPlotter(dataframe, image_format, basename)

        part_obj.plot()
        part_obj.save()

        ## Indexograms
        ind_objs = []
        if args.all:
            for cls in indexogram_classes:
                ind_objs.append(cls(dataframe, image_format, basename))
        elif args.stem:
            ind_objs.append(StemIndexogramPlotter(dataframe, image_format, basename))
        elif args.stairs:
            ind_objs.append(StairsIndexogramPlotter(dataframe, image_format, basename))
        elif args.combined:
            ind_objs.append(CombinedIndexogramPlotter(dataframe, image_format, basename))
        else:
            close_bubbles = False
            if args.close_bubbles:
                close_bubbles = True
            ind_objs.append(SimpleIndexogramPlotter(dataframe, image_format, basename, close_bubbles))
        for ind_obj in ind_objs:
            ind_obj.plot()
            ind_obj.save()

    except:
        raise CustomException('Something wrong with given csv file.')