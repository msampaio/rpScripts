from copy import deepcopy
from fractions import Fraction
import itertools
import pickle
from matplotlib import pyplot as plt


from .lib.base import CustomException, EventLocation, GeneralSubparser, RPData, clean_filename, file_rename, find_nearest_smaller, parse_pow


# Constants
RESOLUTION = 300
MAXIMUM_POINTS_TO_LABEL = 50
LABELS_SIZE = 15
LABELS_DISTANCE = 1.025
DOTS_SIZE = 15
IMG_SIZE = list(map(lambda x: x*0.8, (8, 6)))


class AbstractPlotter(object):
    '''Main abstract plotter class.

    This class has useful attributes and methods to handle RPData objects.'''

    def __init__(self, rpdata: RPData, image_format='svg') -> None:
        self.rpdata = deepcopy(rpdata)
        self.image_format = image_format
        self.outname = file_rename(self.rpdata.path, self.image_format, self.name)
        self.name = None
        self.subplots = None

    def plot(self) -> None:
        '''Plot Setup.

        Depends on the extended classes implementation.'''

        plt.grid()
        f = plt.subplot()
        self.xticks_adjust()
        self.subplots = pickle.dumps(f)
        return None

    def xticks_adjust(self) -> None:
        '''Apply tight layout method to the plot object.

        It is useful for rotated xlabels charts.'''

        plt.tight_layout()

    def save(self, close_figure=True) -> None:
        '''Saves the chart into the RPData outname.'''

        print('Saving file {}...'.format(self.outname))
        self.get_subplots()
        if self.image_format == 'svg':
            plt.savefig(self.outname)
        else:
            plt.savefig(self.outname, dpi=RESOLUTION)
        if close_figure:
            plt.close()

    def get_subplots(self):
        '''Return subplots dumped into pickle file.

        Useful for multiple chart creation.'''

        if self.subplots:
            return pickle.loads(self.subplots)


class AbstractTimePlotter(AbstractPlotter):
    '''Abstract time plotter class.

    This class extends AbstractPlotter and handles X-axis to show measure numbers and offsets.'''

    def __init__(self, rpdata: RPData, image_format='svg', show_labels=False) -> None:
        super().__init__(rpdata, image_format)

        self.duration = self.rpdata.data['Duration']
        self.global_offset = self.rpdata.data['Global offset']

        last_duration = self.duration[-1]
        original_last_global_offset = self.global_offset[-1]

        last_global_offset = original_last_global_offset + last_duration
        last_global_offset = float(last_global_offset)

        self.x_values = list(map(float, self.global_offset))
        self.x_values.append(float(last_global_offset))

        self.show_labels = show_labels
        self.labels_vertical_lines = []
        if self.show_labels and self.rpdata.labels:
            previous_label = self.rpdata.labels[0]
            self.labels_vertical_lines = [{
                'label': previous_label,
                'offset': self.rpdata.data['Global offset'][0]
            }]
            for i in range(1, len(self.rpdata.labels)):
                current_label = self.rpdata.labels[i]
                if current_label != previous_label:
                    self.labels_vertical_lines.append({
                        'label': current_label,
                        'offset': self.rpdata.data['Global offset'][i]
                    })
                previous_label = current_label

    def xticks_adjust(self):
        '''Extend AbstractPlotter's xticks_adjust method.

        Rotates xticks.'''

        plt.xticks(rotation=90)
        return super().xticks_adjust()

    def make_xticks(self) -> None:
        # get original xticks values
        original_xticks_values = plt.xticks()[0]
        inverted_map = {v: k for k, v in self.rpdata.offset_map.items()}
        offset_points = list(inverted_map.keys())

        new_ticks = list(original_xticks_values)[1:-1]

        new_labels = []
        for value in new_ticks:
            go  = find_nearest_smaller(int(value), offset_points)
            measure_number = inverted_map[go]
            # TODO: improve local offset (as fraction)
            local_offset = Fraction(value - go)

            event_location = EventLocation(measure_number=measure_number, offset=local_offset)
            new_labels.append(event_location.str_index)

        plt.xticks(ticks=new_ticks, labels=new_labels)

    def plot(self):
        '''Extend AbstractPlotter's method. Set X-axis label and add optional vertical lines for labels if they are available in RPData.'''

        yvals = plt.yticks()[0]
        ymin = yvals[0]
        ymax = yvals[-1]
        if self.labels_vertical_lines:
            for dic in self.labels_vertical_lines:
                plt.vlines(x=dic['offset'], ymin=ymin, ymax=ymax, colors='darkmagenta')
                plt.text(x=dic['offset'] + 2, y=ymin + 1, s=dic['label'], rotation='vertical')
        plt.xlabel('Positions (measure number + offset)')

        return super().plot()


class AbstractPartitiogramPlotter(AbstractPlotter):
    '''Abstract partitiogram plotter class.

    This class extends AbstractPlotter and has agglomeration, dispersion and quantity attributes to help Partitiogram scatter plotting.'''

    def __init__(self, rpdata: RPData, image_format='svg', with_labels=True) -> None:
        super().__init__(rpdata, image_format)
        self.with_labels = with_labels
        self.frequency_analysis = {}

        self.partitions_labels = []
        self.y_disp = []
        self.x_aggl = []
        self.quantity = []

        total = 0
        size = len(self.rpdata.partitions)

        for i in range(size):
            partition_label = self.rpdata.partitions[i]
            agglomeration = self.rpdata.data['Agglomeration'][i]
            dispersion = self.rpdata.data['Dispersion'][i]
            duration = self.rpdata.data['Duration'][i]
            key = (partition_label, agglomeration, dispersion)

            if key not in self.frequency_analysis.keys():
                self.frequency_analysis.update({key: 0})

            self.frequency_analysis[key] += duration
            total += duration

        for (p_label, aggl, disp), dur in self.frequency_analysis.items():
            self.partitions_labels.append(parse_pow(p_label))
            self.x_aggl.append(aggl)
            self.y_disp.append(disp)
            self.quantity.append(dur / total)

    def plot(self):
        '''Extend AbstractPlotter's method. Set X- and Y-axis labels.'''

        plt.xlabel('Agglomeration index')
        plt.ylabel('Dispersion index')
        p = super().plot()
        return p

    def check_labels(self):
        if self.with_labels:
            zipped = zip(self.partitions_labels, self.y_disp, self.x_aggl)
            for v, y, x in zipped:
                plt.text(x * LABELS_DISTANCE, y * LABELS_DISTANCE , v, fontsize=LABELS_SIZE)


class AbstractIndexogramPlotter(AbstractTimePlotter):
    '''Abstract indexogram plotter class.

    This class extends AbstractTimePlotter and has dispersion and inverted agglomeration data as attributes to help indexograms plotting.'''

    def __init__(self, rpdata: RPData, image_format='svg', close_bubbles=False, show_labels=False) -> None:
        self.legend = ['Agglomeration', 'Dispersion']
        super().__init__(rpdata, image_format, show_labels)
        self.close_bubbles = close_bubbles
        self.inverted_agglomeration = [v * -1 for v in self.rpdata.data['Agglomeration']]

        self.index = self.rpdata.data['Index']
        self.agglomeration = [v * -1 for v in self.rpdata.data['Agglomeration']]
        self.dispersion = self.rpdata.data['Dispersion']

        self.y_aggl = self.agglomeration
        self.y_aggl.append(self.y_aggl[-1])

        self.y_disp = self.dispersion
        self.y_disp.append(self.y_disp[-1])


class SimplePartitiogramPlotter(AbstractPartitiogramPlotter):
    def __init__(self, rpdata: RPData, image_format='svg', with_labels=True) -> None:
        self.name = 'simple-partitiogram'
        super().__init__(rpdata, image_format, with_labels)

    def plot(self):
        '''Extend AbstractPartitiogramPlotter's method. Create scatter plot.'''

        plt.clf()
        plt.scatter(
            x=self.x_aggl,
            y=self.y_disp,
            s=DOTS_SIZE
        )
        self.check_labels()
        return super().plot()


class BubblePartitiogramPlotter(AbstractPartitiogramPlotter):
    def __init__(self, rpdata: RPData, image_format='svg', with_labels=True, bubble_size=2000) -> None:
        self.name = 'bubble-partitiogram'
        super().__init__(rpdata, image_format, with_labels)
        self.bubble_size = bubble_size

    def plot(self):
        '''Extend AbstractPartitiogramPlotter's method. Create scatter plot.'''

        plt.clf()
        plt.scatter(
            x=self.x_aggl,
            y=self.y_disp,
            s=[float(q * self.bubble_size) for q in self.quantity],
        )
        self.check_labels()

        return super().plot()


class ComparativePartitiogramPlotter(AbstractPartitiogramPlotter):
    def __init__(self, rpdata: RPData, column_1, column_2, image_format='svg', with_labels=True) -> None:
        self.labels = rpdata.labels
        self.column_1 = column_1
        self.column_2 = column_2
        self.name = 'comparison-partitiogram-{}-{}'.format(clean_filename(self.column_1), clean_filename(self.column_2))
        super().__init__(rpdata, image_format, with_labels)

    def plot(self):
        '''Extend AbstractPartitiogramPlotter's method. Create multiple superimposed scatter plots.'''

        dic = {
            self.column_1: set([]),
            self.column_2: set([]),
        }

        for i in range(self.rpdata.size):
            label = self.labels[i]
            if label in dic.keys():
                dic[label].add(self.rpdata.partitions[i])

        g1 = dic[self.column_1] - dic[self.column_2]
        g1_label = 'Only in {}'.format(self.column_1)

        g2 = dic[self.column_2] - dic[self.column_1]
        g2_label = 'Only in {}'.format(self.column_2)

        g3 = dic[self.column_1].intersection(dic[self.column_2])
        g3_label = 'Both: {} and {}'.format(self.column_1, self.column_2)

        partitions_set = g1.union(g2)
        partitions_map = {}

        colors = ['orange', 'red', 'blue']
        groups = [
            (g3_label, g3),
            (g1_label, g1),
            (g2_label, g2),
        ]

        plt.clf()

        for group_label, partitions in groups:
            x_values = []
            y_values = []
            for p in partitions:
                _a, _d = self.rpdata.get_agglomeration_dispersion(p)
                x_values.append(_a)
                y_values.append(_d)
                p_as_pow = parse_pow(p)
                if p_as_pow not in partitions_map.keys():
                    partitions_map[p_as_pow] = [_a, _d]
            plt.scatter(
                x=x_values,
                y=y_values,
                label=group_label,
                color=colors.pop(),
                s=DOTS_SIZE
            )

        if len(partitions_set) < MAXIMUM_POINTS_TO_LABEL:
            for p, (_a, _d) in partitions_map.items():
                plt.text(_a * LABELS_DISTANCE, _d *LABELS_DISTANCE, p, fontsize=LABELS_SIZE)

        plt.legend(title='Label')

        return super().plot()


class SimpleIndexogramPlotter(AbstractIndexogramPlotter):
    def __init__(self, rpdata: RPData, image_format='svg', close_bubbles=False, show_labels=False) -> None:
        self.name = 'simple-indexogram'
        super().__init__(rpdata, image_format, close_bubbles, show_labels)


    def plot(self):
        def draw_vertical_line(pair, x):
            aggl, disp = pair
            plt.vlines(x=x, ymin=aggl, ymax=disp, linestyles='dotted', colors='C3')

        # The simple plot
        plt.clf()
        plt.plot(self.x_values, self.y_aggl)
        plt.plot(self.x_values, self.y_disp)

        self.make_xticks()

        plt.ylabel('Values\n<- aggl./disp. ->')
        plt.legend(self.legend)

        # draw vertical lines to close the bubbles
        if self.close_bubbles:
            rest_segment = False
            last_pair = None
            i = 0
            for i in range(len(self.agglomeration)):
                pair = (self.agglomeration[i], self.dispersion[i])
                _agg = self.agglomeration[i]
                if not _agg:
                    if not rest_segment:
                        if last_pair:
                            x = self.global_offset[i - 1]
                            draw_vertical_line(last_pair, x)
                        rest_segment = True
                else:
                    if rest_segment:
                        x = self.global_offset[i]
                        draw_vertical_line(pair, x)
                        rest_segment = False
                last_pair = pair

        return super().plot()


class StemIndexogramPlotter(AbstractIndexogramPlotter):
    def __init__(self, rpdata: RPData, image_format='svg', close_bubbles=False, show_labels=False) -> None:
        self.name = 'stem-indexogram'
        super().__init__(rpdata, image_format, close_bubbles, show_labels)

    def plot(self):
        # The stem plot
        plt.clf()
        plt.stem(self.x_values, self.y_aggl, markerfmt=' ')
        plt.stem(self.x_values, self.y_disp, markerfmt=' ')

        self.make_xticks()

        plt.xlabel('Positions (measure + offset)')
        plt.ylabel('Values\n<- aggl./disp. ->')
        plt.legend(self.legend)

        return super().plot()


class StairsIndexogramPlotter(AbstractIndexogramPlotter):
    def __init__(self, rpdata: RPData, image_format='svg', close_bubbles=False, show_labels=False) -> None:
        self.name = 'stairs-indexogram'
        super().__init__(rpdata, image_format, close_bubbles, show_labels)

    def plot(self):
        # The stem plot
        plt.clf()
        plt.stairs(self.y_aggl[:-1], self.x_values)
        plt.stairs(self.y_disp[:-1], self.x_values)

        self.make_xticks()

        plt.xlabel('Positions (measure + offset)')
        plt.ylabel('Values\n<- aggl./disp. ->')
        plt.legend(self.legend)

        return super().plot()


class StepIndexogramPlotter(AbstractIndexogramPlotter):
    def __init__(self, rpdata: RPData, image_format='svg', close_bubbles=False, show_labels=False) -> None:
        self.name = 'step-indexogram'
        super().__init__(rpdata, image_format, close_bubbles, show_labels)

    def plot(self):
        # The step plot
        plt.clf()
        plt.step(x=self.x_values, y=self.y_aggl, where='post')
        plt.step(x=self.x_values, y=self.y_disp, where='post')

        self.make_xticks()

        plt.xlabel('Positions (measure number + offset)')
        plt.ylabel('Values\n<- aggl./disp. ->')
        plt.legend(self.legend)

        return super().plot()


class CombinedIndexogramPlotter(AbstractIndexogramPlotter):
    def __init__(self, rpdata: RPData, image_format='svg', close_bubbles=False, show_labels=False) -> None:
        self.name = 'combined-indexogram'
        super().__init__(rpdata, image_format, close_bubbles, show_labels)

    def plot(self):
        y_values = [d + a for d, a in zip(self.y_disp, self.y_aggl)]

        plt.clf()
        plt.plot(self.x_values, y_values)

        self.make_xticks()

        plt.xlabel('Positions (measure + offset)')
        plt.ylabel('Values\n(d - a)')
        plt.legend(self.legend)

        return super().plot()


class ComparativePartitiogramMaker(AbstractPartitiogramPlotter):
    def __init__(self, rpdata: RPData, image_format='svg', with_labels=True) -> None:
        self.name = ''
        super().__init__(rpdata, image_format, with_labels)
        self.plotters = []

        if not rpdata.labels:
            raise CustomException('There is no label in the given input file.')

        self.section_labels = sorted(list(set(self.rpdata.labels)))

        for a, b in itertools.combinations(self.section_labels, 2):
            cpp = ComparativePartitiogramPlotter(self.rpdata, a, b, self.image_format, self.with_labels)
            self.plotters.append(cpp)

    def plot(self):
        '''Call ComparativePartitiogramPlotter's plot method for each plotter object available at `plotters` attribute.'''

        for plotter in self.plotters:
            plotter.plot()

    def save(self):
        for plotter in self.plotters:
            plotter.save()


class Subparser(GeneralSubparser):
    '''Implements argparser.'''

    def setup(self) -> None:
        self.program_name = 'plot'
        self.program_help = 'Charts plotter'

    def add_arguments(self) -> None:
        self.parser.add_argument('-f', '--img_format', help="Charts output format (svg, png, or jpg)", default='svg', type=str)
        self.parser.add_argument("-r", "--resolution", help = "PNG image resolution. Default=300", default=300, type=int)
        self.parser.add_argument("-a", "--all", help = "Plot all available charts", action='store_true')
        self.parser.add_argument("-u", "--bubble_partitiogram", help = "Partitiogram as a bubble chart", default=False, action='store_true')
        self.parser.add_argument("-w", "--without_labels", help = "Partitiogram as a bubble chart without labels", default=False, action='store_true')
        self.parser.add_argument("-m", "--comparative_partitiogram", help = "Comparative partitiogram. It demands a previous labeled file. Check rpscripts labels -h' column", default=False, action='store_true')
        self.parser.add_argument("-fl", "--show_form_labels", help = "Draw vertical lines to display given form labels. It demands a previous labeled file. Check rpscripts labels -h' column", default=False, action='store_true')
        self.parser.add_argument("-c", "--close_bubbles", help = "Indexogram with bubbles' closing lines", default=False, action='store_true')
        self.parser.add_argument("-e", "--stem", help = "Indexogram as a stem chart", action='store_true')
        self.parser.add_argument("-t", "--stairs", help = "Indexogram as a stair chart", action='store_true')
        self.parser.add_argument("-p", "--step", help = "Indexogram as a step chart", action='store_true')
        self.parser.add_argument("-b", "--combined", help = "Indexogram as a combination of aglomeration and dispersion", action='store_true')
        self.parser.add_argument("--maximum_points_to_label", help = "Maximum number of points to label in bubble partitiogram chart. Default=50", default=50, type=int)
        self.parser.add_argument("--dots_size", help = "Dots size in simple partitiogram chart. Default=15", default=15, type=float)
        self.parser.add_argument("--labels_size", help = "Labels size in partitiogram chart. Default=15", default=15, type=float)
        self.parser.add_argument("--labels_distance", help = "Distance between points and labels in partitiogram chart. Default=1.025", default=1.025, type=float)

    def handle(self, args):
        if args.resolution < 0 or args.resolution > 1200:
            raise CustomException('Resolution must be an integer from 0 to 1200')

        global MAXIMUM_POINTS_TO_LABEL
        global DOTS_SIZE
        global LABELS_SIZE
        global LABELS_DISTANCE
        global IMG_SIZE

        MAXIMUM_POINTS_TO_LABEL = args.maximum_points_to_label
        DOTS_SIZE = args.dots_size
        LABELS_SIZE = args.labels_size
        LABELS_DISTANCE = args.labels_distance
        IMG_SIZE = list(map(lambda x: x*0.8, (8, 6)))

        close_bubbles = args.close_bubbles
        if close_bubbles:
            close_bubbles = True

        with_labels = not args.without_labels
        if with_labels:
            with_labels = True

        show_form_labels = args.show_form_labels
        if show_form_labels:
            show_form_labels = True

        image_format = args.img_format.lower()
        if image_format not in ['svg', 'jpg', 'png']:
            raise CustomException('Image format must be svg, jpg or png.')

        indexogram_classes = [
            SimpleIndexogramPlotter,
            StemIndexogramPlotter,
            StairsIndexogramPlotter,
            StepIndexogramPlotter,
            CombinedIndexogramPlotter
        ]

        try:
            rp_data = RPData(args.filename)

            ## Partitiograms
            if args.comparative_partitiogram:
                part_obj = ComparativePartitiogramMaker(rp_data, image_format, with_labels)
            elif args.bubble_partitiogram:
                part_obj = BubblePartitiogramPlotter(rp_data, image_format, with_labels)
            else:
                part_obj = SimplePartitiogramPlotter(rp_data, image_format, with_labels)

            part_obj.plot()
            part_obj.save()

            ## Indexograms
            ind_objs = []
            if args.all:
                for cls in indexogram_classes:
                    ind_objs.append(cls(rp_data, image_format, close_bubbles, show_form_labels))
            elif args.stem:
                ind_objs.append(StemIndexogramPlotter(rp_data, image_format, close_bubbles, show_form_labels))
            elif args.stairs:
                ind_objs.append(StairsIndexogramPlotter(rp_data, image_format, close_bubbles, show_form_labels))
            elif args.step:
                ind_objs.append(StepIndexogramPlotter(rp_data, image_format, close_bubbles, show_form_labels))
            elif args.combined:
                ind_objs.append(CombinedIndexogramPlotter(rp_data, image_format, close_bubbles, show_form_labels))
            else:
                close_bubbles = False
                if args.close_bubbles:
                    close_bubbles = True
                ind_objs.append(SimpleIndexogramPlotter(rp_data, image_format, close_bubbles, show_form_labels))
            for ind_obj in ind_objs:
                ind_obj.plot()
                ind_obj.save()

        except:
            raise CustomException('Something wrong with given JSON file.')
