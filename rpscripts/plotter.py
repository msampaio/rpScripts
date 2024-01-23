from copy import deepcopy
from fractions import Fraction
import itertools
import pickle
from matplotlib import pyplot as plt
import numpy


from .lib.base import CustomException, EventLocation, GeneralSubparser, RPData, aux_sum_if_none, clean_filename, file_rename, find_nearest_smaller, parse_fraction, parse_pow


# Constants
RESOLUTION = 300
MAXIMUM_POINTS_TO_LABEL = 50
LABELS_SIZE = 15
LABELS_DISTANCE = 1.025
DOTS_SIZE = 15
IMG_SIZE = [6.4, 4.8]
INDEXOGRAM_SLOPE_LIMIT = Fraction(1, 4)


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

        self.global_offset.append(last_global_offset)

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
            new_labels.append(event_location.get_str_index())

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

    def __init__(self, rpdata: RPData, image_format='svg', with_labels=True, **kwargs) -> None:
        super().__init__(rpdata, image_format)
        self.with_labels = with_labels
        self.frequency_analysis = {}

        self.partitions_labels = []
        self.y_disp = []
        self.x_aggl = []
        self.quantity = []

        # Filter values
        self.min_dispersion = None
        self.max_dispersion = None
        self.min_agglomeration = None
        self.max_agglomeration = None

        if kwargs:
            self.__dict__.update(kwargs)

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

        if self.check_given_limits():
            self.data_filter()

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
                if not x:
                    x = 0
                if not v:
                    v = 0
                if not y:
                    y = 0
                plt.text(x * LABELS_DISTANCE, y * LABELS_DISTANCE , v, fontsize=LABELS_SIZE)

    def check_given_limits(self) -> bool:
        '''Return True if there are value filters defined.'''

        a = self.min_dispersion == None
        b = self.max_dispersion == None
        c = self.min_agglomeration == None
        d = self.max_agglomeration == None
        return not all([a, b, c, d])

    def data_filter(self) -> None:
        '''Filter the dispersion and agglomeration indexes values for a narrowed plot.'''

        values = [(d, a, q) for d, a, q in zip(self.y_disp, self.x_aggl, self.quantity)]

        if self.min_dispersion != None:
            if self.min_dispersion > numpy.nanmin(self.y_disp):
                values = [(d, a, q) for d, a, q in values if d >= self.min_dispersion]

        if self.max_dispersion != None:
            if self.max_dispersion < numpy.nanmax(self.y_disp):
                values = [(d, a, q) for d, a, q in values if d <= self.max_dispersion]

        if self.min_agglomeration != None:
            if self.min_agglomeration > numpy.nanmin(self.y_disp):
                values = [(d, a, q) for d, a, q in values if a >= self.min_agglomeration]

        if self.max_agglomeration != None:
            if self.max_agglomeration < numpy.nanmax(self.y_disp):
                values = [(d, a, q) for d, a, q in values if a <= self.max_agglomeration]

        y_disp = []
        x_aggl = []
        quantity = []

        for d, a, q in values:
            y_disp.append(d)
            x_aggl.append(a)
            quantity.append(q)

        self.y_disp = y_disp
        self.x_aggl = x_aggl
        self.quantity = quantity


class AbstractIndexogramPlotter(AbstractTimePlotter):
    '''Abstract indexogram plotter class.

    This class extends AbstractTimePlotter and has dispersion and inverted agglomeration data as attributes to help indexograms plotting.'''

    def __init__(self, rpdata: RPData, image_format='svg', close_bubbles=False, show_labels=False) -> None:
        self.legend = ['Agglomeration', 'Dispersion']
        super().__init__(rpdata, image_format, show_labels)
        self.close_bubbles = close_bubbles
        self.inverted_agglomeration = [v * -1 for v in self.rpdata.data['Agglomeration']]

        self.index = self.rpdata.data['Index']
        self.agglomeration = self.rpdata.data['Agglomeration']
        self.dispersion = self.rpdata.data['Dispersion']

        self.y_aggl = self.inverted_agglomeration
        self.y_aggl.append(self.y_aggl[-1])

        self.y_disp = self.dispersion
        self.y_disp.append(self.y_disp[-1])

    def _auxiliary_slope_add(self) -> tuple:
        '''Return new X- and Y-axis values lists with added intermediary points between adjacent ones to create small slopes at the end of each line.

        The aim is to keep visual identification of partitioning operations.
        See Sampaio and Gentil-Nunes (2022) for further information.'''

        # Adapt values to add intermediary points between adjacent ones to
        # create a small slope at the end of each "line".
        size = len(self.x_values)
        intermediary_points = {}
        for i in range(size - 1):
            yd = self.y_disp[i]
            ya = self.y_aggl[i]
            x = self.x_values[i]
            go = self.global_offset[i]

            nxt_x = self.x_values[i + 1]
            x_diff = nxt_x - x

            # conditions to add intermediary points:
            # aggl/disp real values and enought space between adjacent x points.
            c1 = x_diff > INDEXOGRAM_SLOPE_LIMIT
            c2 = not numpy.isnan(yd)
            c3 = not numpy.isnan(ya)

            if all([c1, c2, c3]):
                intermediary_points.update({
                    i + 1: (
                    nxt_x - INDEXOGRAM_SLOPE_LIMIT,
                        go - INDEXOGRAM_SLOPE_LIMIT,
                        yd,
                        ya
                    )
                })

        x_values = []
        y_disp = []
        y_aggl = []
        global_offsets = []

        for i in range(size):
            yd = self.y_disp[i]
            ya = self.y_aggl[i]
            x = self.x_values[i]
            go = self.global_offset[i]

            # Add intermediary points for the slope creation
            if i in intermediary_points.keys():
                _x, _go, _yd, _ya = intermediary_points[i]
                x_values.append(_x)
                y_disp.append(_yd)
                y_aggl.append(_ya)
                global_offsets.append(_go)

            x_values.append(x)
            y_disp.append(yd)
            y_aggl.append(ya)
            global_offsets.append(go)

        return x_values, global_offsets, y_disp, y_aggl

class SimplePartitiogramPlotter(AbstractPartitiogramPlotter):
    def __init__(self, rpdata: RPData, image_format='svg', with_labels=True,  **kwargs) -> None:
        self.name = 'simple-partitiogram'
        super().__init__(rpdata, image_format, with_labels, **kwargs)

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
    def __init__(self, rpdata: RPData, image_format='svg', with_labels=True, bubble_size=2000, **kwargs) -> None:
        self.name = 'bubble-partitiogram'
        super().__init__(rpdata, image_format, with_labels, **kwargs)
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
    def __init__(self, rpdata: RPData, column_1, column_2, image_format='svg', with_labels=True, **kwargs) -> None:
        self.labels = rpdata.labels
        self.column_1 = column_1
        self.column_2 = column_2
        self.name = 'comparison-partitiogram-{}-{}'.format(clean_filename(self.column_1), clean_filename(self.column_2))
        super().__init__(rpdata, image_format, with_labels, **kwargs)

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
                if not _a:
                    _a = 0
                if not _d:
                    _d = 0
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

        # Get new values with slopes
        x_values, global_offsets, y_disp, y_aggl = self._auxiliary_slope_add()

        # The simple plot
        plt.clf()
        plt.plot(x_values, y_aggl)
        plt.plot(x_values, y_disp)

        self.make_xticks()

        plt.ylabel('Values\n<- aggl./disp. ->')
        plt.legend(self.legend)

        # draw vertical lines to close the bubbles
        if self.close_bubbles:
            rest_segment = False
            last_pair = None
            i = 0
            for i in range(len(y_aggl)):
                pair = (y_aggl[i], y_disp[i])
                _agg = y_aggl[i]
                if numpy.isnan(_agg):
                    if not rest_segment:
                        if last_pair:
                            x = global_offsets[i]
                            draw_vertical_line(last_pair, x)
                        rest_segment = True
                else:
                    if rest_segment:
                        x = global_offsets[i]
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
        # Get new values with slopes
        x_values, _, y_disp, y_aggl = self._auxiliary_slope_add()

        y_values = [aux_sum_if_none(d, a) for d, a in zip(y_disp, y_aggl)]

        plt.clf()
        plt.plot(x_values, y_values)

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


class SimplePartDensityNumberScatterPlotter(AbstractPlotter):
    def __init__(self, rpdata: RPData, image_format='svg', with_labels=False, **kwargs) -> None:
        self.name = 'simple-part-density_number-scatter'
        super().__init__(rpdata, image_format)

        self.with_labels = with_labels
        self.bubble_size = 2000
        self.frequency_analysis = {}

        self.parts_list = self.rpdata.data['Parts']

        self.partitions_labels = []
        self.y_number_of_parts = []
        self.x_density_numbers = []
        self.quantity = []

        # Filter values
        self.min_nparts = None
        self.max_nparts = None
        self.min_density_numbers = None
        self.max_density_numbers = None

        if kwargs:
            self.__dict__.update(kwargs)

        total = 0
        size = len(self.rpdata.partitions)

        for i in range(size):
            partition_label = self.rpdata.partitions[i]
            duration = self.rpdata.data['Duration'][i]
            parts = self.rpdata.data['Parts'][i]
            number_of_parts = len(parts)
            density_number = sum(parts)
            key = (partition_label, density_number, number_of_parts)

            if key not in self.frequency_analysis.keys():
                self.frequency_analysis.update({key: 0})

            self.frequency_analysis[key] += duration
            total += duration

        for (p_label, density_number, number_of_parts), dur in self.frequency_analysis.items():
            self.partitions_labels.append(parse_pow(p_label))
            self.x_density_numbers.append(density_number)
            self.y_number_of_parts.append(number_of_parts)
            self.quantity.append(dur / total)

        if self.check_given_limits():
            self.data_filter()

    def plot(self):
        '''Extend AbstractPlotter's method. Set X- and Y-axis labels.'''

        plt.clf()
        plt.scatter(
            x=self.x_density_numbers,
            y=self.y_number_of_parts,
            s=[float(q * self.bubble_size) for q in self.quantity],
            # s=DOTS_SIZE
        )

        plt.xlabel('Density number')
        plt.ylabel('Number of parts')
        p = super().plot()

        self.check_labels()

        return p

    def check_labels(self):
        if self.with_labels:
            zipped = zip(self.partitions_labels, self.y_number_of_parts, self.x_density_numbers)
            for v, y, x in zipped:
                if not x:
                    x = 0
                if not v:
                    v = 0
                if not y:
                    y = 0
                plt.text(x * LABELS_DISTANCE, y * LABELS_DISTANCE , v, fontsize=LABELS_SIZE)

    def check_given_limits(self) -> bool:
        '''Return True if there are value filters defined.'''

        a = self.min_nparts == None
        b = self.max_nparts == None
        c = self.min_density_numbers == None
        d = self.max_density_numbers == None
        return not all([a, b, c, d])

    def data_filter(self) -> None:
        '''Filter the dispersion and agglomeration indexes values for a narrowed plot.'''

        values = [(d, a, q) for d, a, q in zip(self.y_disp, self.x_aggl, self.quantity)]

        if self.min_nparts != None:
            if self.min_nparts > numpy.nanmin(self.y_disp):
                values = [(d, a, q) for d, a, q in values if d >= self.min_nparts]

        if self.max_nparts != None:
            if self.max_nparts < numpy.nanmax(self.y_disp):
                values = [(d, a, q) for d, a, q in values if d <= self.max_nparts]

        if self.min_density_numbers != None:
            if self.min_density_numbers > numpy.nanmin(self.y_disp):
                values = [(d, a, q) for d, a, q in values if a >= self.min_density_numbers]

        if self.max_density_numbers != None:
            if self.max_density_numbers < numpy.nanmax(self.y_disp):
                values = [(d, a, q) for d, a, q in values if a <= self.max_density_numbers]

        y_disp = []
        x_aggl = []
        quantity = []

        for d, a, q in values:
            y_disp.append(d)
            x_aggl.append(a)
            quantity.append(q)

        self.y_disp = y_disp
        self.x_aggl = x_aggl
        self.quantity = quantity


class SimplePartDensityNumberInTimePlotter(AbstractTimePlotter):
    def __init__(self, rpdata: RPData, image_format='svg', show_labels=False) -> None:
        self.name = 'simple-part-density_number-time'
        super().__init__(rpdata, image_format, show_labels)

        self.number_of_parts = []
        self.density_numbers = []
        self.inverted_density_numbers = []

        for nparts, dn in self.rpdata.get_number_of_parts_and_density_numbers():
            self.number_of_parts.append(nparts)
            self.density_numbers.append(dn)
            self.inverted_density_numbers.append(dn * -1)

        self.index = self.rpdata.data['Index']

        self.y_number_of_parts = self.number_of_parts
        self.y_number_of_parts.append(self.y_number_of_parts[-1])

        self.y_density_numbers = self.inverted_density_numbers
        self.y_density_numbers.append(self.y_density_numbers[-1])

        self.legend = ['Number of parts', 'Density number (negative)']

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
            new_labels.append(event_location.get_str_index())

        plt.xticks(ticks=new_ticks, labels=new_labels)

    def plot(self):
        plt.clf()
        plt.plot(self.x_values, self.y_number_of_parts)
        plt.plot(self.x_values, self.y_density_numbers)

        self.make_xticks()

        plt.ylabel('Values\n<- density number / n. parts ->')
        plt.legend(self.legend)

        return super().plot()


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
        self.parser.add_argument("-q", "--parts_density_numbers_time", help = "Parts and density number in time", default=False, action='store_true')
        self.parser.add_argument("-v", "--parts_density_numbers_scatter", help = "Parts and density number scatter", default=False, action='store_true')
        self.parser.add_argument("-m", "--comparative_partitiogram", help = "Comparative partitiogram. It demands a previous labeled file. Check rpscripts labels -h' column", default=False, action='store_true')
        self.parser.add_argument("-fl", "--show_form_labels", help = "Draw vertical lines to display given form labels. It demands a previous labeled file. Check rpscripts labels -h' column", default=False, action='store_true')
        self.parser.add_argument("-c", "--close_bubbles", help = "Indexogram with bubbles' closing lines", default=False, action='store_true')
        self.parser.add_argument("-e", "--stem", help = "Indexogram as a stem chart", action='store_true')
        self.parser.add_argument("-t", "--stairs", help = "Indexogram as a stair chart", action='store_true')
        self.parser.add_argument("-p", "--step", help = "Indexogram as a step chart", action='store_true')
        self.parser.add_argument("-b", "--combined", help = "Indexogram as a combination of aglomeration and dispersion", action='store_true')
        self.parser.add_argument("--minimum_dispersion", help = "Partitiogram minimum dispersion value to render", default=None, type=float)
        self.parser.add_argument("--maximum_dispersion", help = "Partitiogram maximum dispersion value to render", default=None, type=float)
        self.parser.add_argument("--minimum_agglomeration", help = "Partitiogram minimum agglomeration value to render", default=None, type=float)
        self.parser.add_argument("--maximum_agglomeration", help = "Partitiogram maximum agglomeration value to render", default=None, type=float)
        self.parser.add_argument("--maximum_points_to_label", help = "Maximum number of points to label in bubble partitiogram chart. Default=50", default=50, type=int)
        self.parser.add_argument("--dots_size", help = "Dots size in simple partitiogram chart. Default=15", default=15, type=float)
        self.parser.add_argument("--labels_size", help = "Labels size in partitiogram chart. Default=15", default=15, type=float)
        self.parser.add_argument("--labels_distance", help = "Distance between points and labels in partitiogram chart. Default=1.025", default=1.025, type=float)
        self.parser.add_argument("--indexogram_slope", help = "Slope's X-distance. Default=1/4 (use always rational numbers)", default='1/4', type=str)
        self.parser.add_argument("--figure_dimensions", help = "Figure dimensions. Default=6.4,4.8 (comma separated values)", default='6.4,4.8', type=str)

    def handle(self, args):
        if args.resolution < 0 or args.resolution > 1200:
            raise CustomException('Resolution must be an integer from 0 to 1200')

        global MAXIMUM_POINTS_TO_LABEL
        global DOTS_SIZE
        global LABELS_SIZE
        global LABELS_DISTANCE
        global IMG_SIZE
        global INDEXOGRAM_SLOPE_LIMIT

        MAXIMUM_POINTS_TO_LABEL = args.maximum_points_to_label
        DOTS_SIZE = args.dots_size
        LABELS_SIZE = args.labels_size
        LABELS_DISTANCE = args.labels_distance
        IMG_SIZE = list(map(float, args.figure_dimensions.split(',')))
        INDEXOGRAM_SLOPE_LIMIT = parse_fraction(args.indexogram_slope)

        plt.rcParams['figure.figsize'] = IMG_SIZE

        close_bubbles = args.close_bubbles
        if close_bubbles:
            close_bubbles = True

        with_labels = not args.without_labels
        if with_labels:
            with_labels = True

        show_form_labels = args.show_form_labels
        if show_form_labels:
            show_form_labels = True

        partitiogram_filters = {
            'min_dispersion': args.minimum_dispersion,
            'max_dispersion': args.maximum_dispersion,
            'min_agglomeration': args.minimum_agglomeration,
            'max_agglomeration': args.maximum_agglomeration,
        }

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
                part_obj = ComparativePartitiogramMaker(rp_data, image_format, with_labels, **partitiogram_filters)
            elif args.bubble_partitiogram:
                part_obj = BubblePartitiogramPlotter(rp_data, image_format, with_labels, **partitiogram_filters)
            else:
                part_obj = SimplePartitiogramPlotter(rp_data, image_format, with_labels, **partitiogram_filters)

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

            ## Parts x density number
            if args.parts_density_numbers_time:
                part_obj = SimplePartDensityNumberInTimePlotter(rp_data, image_format, True)
                part_obj.plot()
                part_obj.save()

            if args.parts_density_numbers_scatter:
                part_obj = SimplePartDensityNumberScatterPlotter(rp_data, image_format, True)
                part_obj.plot()
                part_obj.save()

        except:
            raise CustomException('Something wrong with given JSON file.')
