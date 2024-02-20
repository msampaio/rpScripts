'''This module provides RPScripts' basic classes and methods '''

from fractions import Fraction
import argparse
import copy
import csv
import graphviz
import json
import math
import numpy
import os
import pandas

from ..config import ENCODING


## Constants

## Add new RP Data attributes here
RPDATA_ATTRIBUTES = [
    'partitions',
    'tclass',
    'tcontour',
]

## Pow conversion functions

POW_DICT = {
    '0': '\N{superscript zero}',
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


def parse_pow(partition) -> str:
    '''Superscript pow values in given partitions.'''

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


## Filename functions

def file_rename(filename: str, extension: str, suffix=None) -> str:
    '''Rename files to change extension value and add optional suffix.'''

    new_base = os.path.splitext(filename)[0]
    if suffix:
        new_base = '{}-{}'.format(new_base, suffix)
    return '{}.{}'.format(new_base, extension)


def clean_filename(filename: str) -> str:
    '''Clean the given filename.

    Remove the special characters and spaces.'''

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

    filename = str(filename).lower()

    for a, b in PAIRS:
        filename = filename.replace(a, b)
    return filename


def save_dict_into_csv_file(dic: dict, filename: str) -> None:
    '''Save a given dictionary into a CSV file.'''

    size = len(dic['Index'])
    rows = []
    for i in range(size):
        row = []
        for k in dic.keys():
            row.append(dic[k][i])
        rows.append(row)

    with open(filename, 'w', encoding=ENCODING) as fp:
        csv_writer = csv.writer(fp, quoting=csv.QUOTE_NONNUMERIC)
        csv_writer.writerow(dic.keys())
        csv_writer.writerows(rows)


def load_json_file(filename: str) -> dict:
    '''Load JSON file.'''

    with open(filename, 'r', encoding=ENCODING) as fp:
        try:
            return json.load(fp)
        except:
            raise ValueError('Invalid json file: {}'.format(filename))


def dump_json_data(filename: str, data) -> None:
    '''Dump data to json file.'''

    with open(filename, 'w', encoding=ENCODING) as fp:
        try:
            json.dump(data, fp)
        except:
            raise ValueError('Invalid json file or data')



## Fraction converters (for offset and duration data)

def parse_fraction(value) -> Fraction:
    '''Return a Fraction object from a given value.'''

    if isinstance(value, str):
        if '/' in value:
            return Fraction(*list(map(int, value.split('/'))))
        else:
            return Fraction(value)
    return value


def fraction_to_string(value) -> str:
    '''Return a given value as a fraction represented as a string format.'''

    if isinstance(value, str):
        return value
    if isinstance(value, Fraction):
        if value.denominator == 1:
            return str(value.numerator)
        return '{}/{}'.format(value.numerator, value.denominator)


def make_fraction(value) -> Fraction:
    '''Return a Fraction object from a given Fraction or float value.'''

    if isinstance(value, Fraction):
        return Fraction(int(value.numerator), int(value.denominator))
    else:
        a, b = value.as_integer_ratio()
        return Fraction(int(a), int(b))


## Finders

def find_nearest_smaller(value, seq: list):
    '''Find the smaller nearest value of a given value from a given sequence.'''

    if value < seq[0]:
        return -1

    if value > seq[-1]:
        return seq[-1]

    size = len(seq)

    if size == 1 and value >= seq[0]:
        return seq[0]

    middle_pointer = math.floor(size/2)

    left = seq[:middle_pointer]
    right = seq[middle_pointer:]

    if value < right[0]:
        return find_nearest_smaller(value, left)
    else:
        return find_nearest_smaller(value, right)


def aux_find_next_measure_number(global_offset: Fraction, offset_map: dict, index=0) -> tuple:
    '''Return the nearest measure number that the global offset value is higher than the given one as parameter.

    This function also updates and returns the given index.'''

    size = len(offset_map.keys())

    if index > size - 1:
        raise IndexError('Given index {} is out of dic'.format(index))

    measure_numbers = list(offset_map.keys())
    while index < size - 1 and global_offset >= offset_map[measure_numbers[index + 1]]:
        index += 1

    return measure_numbers[index], index


## Math auxiliary funcions

def get_number_combinations_pairs(n: int) -> float:
    '''Return the number of pair combinations of a list of `n` elements.

    Binomial coefficient.'''
    return n * (n - 1) / 2


def get_fractions_denominator_lcm(fractions_lst: list):
    '''Return the lowest common multiple value of a list of fractions denominators.'''

    denominators = [fr.denominator for fr in fractions_lst]
    return numpy.lcm.reduce(denominators)


def get_diff_lcm(seq: list) -> Fraction:
    '''Return the lowest common multiple of the differences between the adjacent values of a given list.'''

    diffs = [b - a for a, b in zip(seq, seq[1:])]
    values = map(make_fraction, sorted(list(set(diffs))))
    return Fraction(1, get_fractions_denominator_lcm(values))

def aux_sum_if_none(a, b):
    '''Return the sum if one or two given values is `None`.'''

    if a and b:
        return a + b
    elif a:
        return a
    elif b:
        return b
    return


## Graph functions

def make_general_graph(labels: list, name: str, relations=None) -> graphviz.Digraph:
    '''Return a `graphviz.Digraph` with the adjacent values of a given list of labels.'''

    labels_pairs = set()
    for i in range(len(labels) - 1):
        previous_label = labels[i]
        next_label = labels[i + 1]
        if previous_label and next_label and previous_label != next_label:
            labels_pairs.add((previous_label, next_label))
    dot = graphviz.Digraph(comment=name)

    for prev, nxt in sorted(labels_pairs):
        if relations:
            rel = relations[tuple([prev, nxt])]
            dot.edge(prev, nxt, style=rel)
        else:
            dot.edge(prev, nxt)

    return dot


## General converters

def convert_to_equal_durations(dataframe: pandas.DataFrame, offset_map: dict) -> dict:
    '''Convert texture data from a given DataFrame to dictionary format with events of the same duration.

    For instance, a dataframe with two events with durations 1/2 and 1/3 are converted in 3 events and 2 events of duration 1/6.
    '''

    columns = dataframe.columns
    global_offsets = dataframe['Global offset'].apply(Fraction).values
    minimal_duration = make_fraction(get_diff_lcm(global_offsets))
    last_row = dataframe.iloc[-1]
    total_duration = sum(map(Fraction, [last_row['Global offset'], last_row['Duration']]))

    data = dataframe.values.tolist()
    del dataframe
    data_map = {k: v for k, v in zip(global_offsets, data)}

    new_data = []
    current_global_offset = global_offsets[0]
    previous_row = data[0]

    measure_index = 0
    while current_global_offset < total_duration:
        current_measure, measure_index = aux_find_next_measure_number(current_global_offset, offset_map, measure_index)

        if current_global_offset in data_map:
            row = data_map[current_global_offset]
            previous_row = copy.deepcopy(row)
        else:
            row = copy.deepcopy(previous_row)
            row[2] = current_global_offset - Fraction(offset_map[current_measure])
            row[3] = current_global_offset

        event_location = EventLocation(
            measure_number = str(current_measure),
            offset = str(row[2])
        )
        row[0] = event_location.str_index
        row[1] = current_measure
        new_data.append(row)
        previous_row = row

        ## Increment
        current_global_offset = make_fraction(current_global_offset + minimal_duration)

    return pandas.DataFrame(new_data, columns=columns).to_dict()


def convert_texture_data_from_json(data: dict) -> dict:
    '''Convert texture data from JSON.

    The fractions are converted from string to Fraction objects.
    '''

    fraction_keys = [
        'Offset',
        'Global offset',
        'Duration',
    ]

    for k in ['Agglomeration', 'Dispersion']:
        data[k] = [v if v != None else numpy.nan for v in data[k]]

    for k in fraction_keys:
        data[k] = list(map(parse_fraction, data[k]))
    return data


def convert_texture_data_to_json(data: dict) -> dict:
    '''Convert texture data to JSON.

    The fractions are converted from Fraction objects to strings.
    '''

    new_data = {k: v for k, v in data.items()}
    fraction_keys = [
        'Offset',
        'Global offset',
        'Duration',
    ]

    for k in ['Agglomeration', 'Dispersion']:
        if numpy.nan in new_data[k]:
            new_data[k] = [v if not numpy.isnan(v) else None for v in new_data[k]]
        new_data[k] = [v if v != None else None for v in new_data[k]]

    for k in fraction_keys:
        new_data[k] = list(map(fraction_to_string, new_data[k]))
    return new_data


## Classes

class CustomException(Exception):
    '''Generic custom exception.'''
    pass


class EventLocation(object):
    '''Temporal event location.'''

    def __init__(self, **kwargs) -> None:
        self.measure_number = None
        self.offset = None
        self.global_offset = None
        self.str_index = None

        if kwargs:
            self.__dict__.update(kwargs)

            if self.str_index and not self.measure_number:
                self.parse_str_index()
            elif self.measure_number and not self.str_index:
                self.make_str_index()

    def __repr__(self) -> str:
        return '<EL {}>'.format(self.str_index)

    def make_str_index(self) -> None:
        '''Set the string index (measure number + offset).'''

        self.str_index = '{}+{}'.format(self.measure_number, self.offset)

    def parse_str_index(self) -> None:
        '''Parse string index and store in the class attributes.'''

        self.measure_number, self.offset = self.str_index.split('+')
        self.offset = parse_fraction(self.offset)

    def get_str_index(self, pretty=True) -> str:
        '''Return the string index (measure + offset). If pretty and huge fraction (ex: xxxxx/yyyyy), return an approximate float value.'''

        if self.str_index == None:
            self.make_str_index()
        if pretty:
            numerator = self.offset.numerator
            denominator = self.offset.denominator
            if numerator > 10**4 or denominator > 10**4:
                _offset = round(float(self.offset), 2)
                return '{}+~{}'.format(self.measure_number, _offset)
        return self.str_index

class RPData(object):
    '''Main Rhythmic Partitioning Data class.'''

    def __init__(self, path=None) -> None:
        self.path = None
        self.offset_map = {}
        self.values_map = {}
        self.data = {
            'Index': [], # 0
            'Measure number': [], # 1
            'Offset': [], # 2
            'Global offset': [], # 3
            'Duration': [], # 4
            'Partition': [], # 5
            'Density-number': [], # 6
            'Agglomeration': [], # 7
            'Dispersion': [], # 8
            'Parts': [], # 9
        }

        self.partitions = []
        self.attributes_list = RPDATA_ATTRIBUTES

        for attr in self.attributes_list:
            self.__setattr__(attr, [])

        self.labels = [] # for comparison
        self.size = 0

        if path:
            self.path = path
            self.load_from_file()

    def to_json(self) -> dict:
        '''Return the data as a dictionary with fractions formated to json.'''

        data = {
            'texture_data': convert_texture_data_to_json(self.data),
            'offset_map': {k: fraction_to_string(v) for k, v in self.offset_map.items()},
            'values_map': self.values_map,
            'labels': self.labels,
        }
        # Attributes list
        data.update({k: self.__getattribute__(k) for k in self.attributes_list})

        return data

    def load_from_file(self) -> None:
        '''Load data from the file set into `path` attribute and fill the other class attributes with this loaded data.'''

        print('Loading data from {}...'.format(self.path))
        data = load_json_file(self.path)
        self.data = convert_texture_data_from_json(data['texture_data'])
        self.offset_map = {k: parse_fraction(v) for k, v in data['offset_map'].items()}
        self.values_map = data['values_map']

        for attr in self.attributes_list:
            if attr in data.keys():
                _data = data[attr]
            else:
                _data = []
            self.__setattr__(attr, _data)

        self.labels = data['labels']
        self.size = len(self.partitions)

    def save_to_file(self, filename=None) -> None:
        '''Save the class data into a JSON file.'''

        dest = self.path
        if filename:
            dest = filename

        print('Saving into {}...'.format(dest))
        dump_json_data(dest, self.to_json())

    def save_to_csv(self, equally_sized=False) -> None:
        '''Save the data into a CSV file.

        If equally_sized parameter is true, the events are proportionally divided into smaller events of a unique duration.'''

        csv_fname = file_rename(self.path, 'csv')
        data_dic = self.data
        data_dic['Partition'] = list(map(parse_pow, data_dic['Partition']))

        if equally_sized:
            df = pandas.DataFrame(self.data)
            data_dic = convert_to_equal_durations(df, self.offset_map)

        save_dict_into_csv_file(data_dic, csv_fname)

    def get_agglomeration_dispersion(self, partition_str: str) -> list:
        '''Find and return a given partition's agglomeration and dispersion values as a two-element list.

        These values must be present in the `values_map` class attribute and the partition value must be in string format.'''

        if partition_str in self.values_map.keys():
            return self.values_map[partition_str]
        raise CustomException('The partition {} is not in the map.'.format(partition_str))

    def get_number_of_parts_and_density_numbers(self) -> list:
        '''Return a list of tuples with the number of parts and density number of each all the partitions in data.'''

        return [(len(parts), sum(parts)) if parts != [] else (0, 0) for parts in self.data['Parts']]

    def get_events_location(self, attribute: str) -> dict:
        '''Return a dictionary with the event locations where the measure number is the dictionary key, and the pair "offset, element", the dictionary value. The `element` is the value in the `attribute` list.

        If the `attribute` value is `partitions`, the `element` is the partition as string. For instance, `1.3`, `2^2` and so on.'''

        inverted_offset_map = {parse_fraction(v): int(k) for k, v in self.offset_map.items()}
        offsets = list(inverted_offset_map.keys())

        events_location = {}

        for i in range(self.size):
            global_offset = self.data['Global offset'][i]
            element = self.__getattribute__(attribute)[i]
            measure_offset = find_nearest_smaller(global_offset, offsets)
            measure_number = inverted_offset_map[measure_offset]
            offset = global_offset - measure_offset
            if measure_number not in events_location:
                events_location[measure_number] = []
            events_location[measure_number].append((offset, element))

        return events_location

    def trim(self, start_pointer: int, end_pointer: int):
        '''Return a new `RPData` object with trimmed attributes' data.

        Only values_map is kept as the original `RPData` object.'''

        new_rpdata = RPData()
        new_rpdata.data = {k: v[start_pointer:end_pointer] for k, v in self.data.items()}

        for attr in self.attributes_list:
            trimmed = self.__getattribute__(attr)[start_pointer:end_pointer]
            new_rpdata.__setattr__(attr, trimmed)

        new_rpdata.labels = self.labels[start_pointer:end_pointer]
        new_rpdata.offset_map = self.offset_map
        new_rpdata.values_map = self.values_map

        return new_rpdata

    def make_class_graph(self, attribute: str, relations=None) -> graphviz.Digraph:
        '''Return a `graphviz.Digraph` with the adjacent values of a list of values stored in the given `attribute`.'''

        labels = self.__getattribute__(attribute)
        return make_general_graph(labels, attribute.capitalize(), relations)

    def get_frequency_counter(self, attribute: str, proportional=True) -> dict:
        '''Return a frequency counter of the values of a given attribute.'''

        if attribute not in self.attributes_list:
            raise CustomException('The given attribute {} is not available'.format(attribute))

        values_list = self.__getattribute__(attribute)
        values_set = set(values_list)
        counter = {k: 0 for k in values_set}
        for value in values_list:
            counter[value] += 1
        if proportional:
            n = sum(list(counter.values()))
            counter = {k: v / n for k, v in counter.items()}
        counter = {k: v for k, v in sorted(counter.items(), key=lambda item: item[1], reverse=True)}
        return counter

    def get_probability_counter(self, attribute: str, exclude_repeats=True, proportional=True) -> dict:
        '''Return a probability counter of adjacent values of a given attribute.'''

        if attribute not in self.attributes_list:
            raise CustomException('The given attribute {} is not available'.format(attribute))

        values_list = self.__getattribute__(attribute)
        if exclude_repeats:
            pairs = [(p, n) for p, n in zip(values_list[:-1], values_list[1:]) if p != n]
        else:
            pairs = [(p, n) for p, n in zip(values_list[:-1], values_list[1:])]
        pairs_set = set(pairs)

        counter = {k: 0 for k in pairs_set}
        for pair in pairs:
            counter[pair] += 1
        if proportional:
            n = sum(list(counter.values()))
            counter = {k: v / n for k, v in counter.items()}
        counter = {k: v for k, v in sorted(counter.items(), key=lambda item: item[1], reverse=True)}
        return counter


class GeneralSubparser(object):
    '''Argparse subparser abstract class.'''

    def __init__(self, subparser: argparse.ArgumentParser) -> None:
        self.program_name = None
        self.program_help = None
        self.add_parent = True
        self.setup()

        parent_filename_parser = argparse.ArgumentParser(add_help=False)
        parent_filename_parser.add_argument('filename', help='JSON filename (calc\'s output)', type=str)

        if self.add_parent:
            self.parser = subparser.add_parser(self.program_name, help=self.program_help, parents=[parent_filename_parser])
        else:
            self.parser = subparser.add_parser(self.program_name, help=self.program_help)
        self.main_parser = subparser
        self.parser.set_defaults(func=self.handle)

    def setup(self) -> None:
        '''Basic setup.

        Set program_name and help message.'''

        self.program_name = ''
        self.program_help = ''

    def handle(self, args) -> None:
        '''Parse arguments and run the module functions.'''

        pass

    def add_arguments(self) -> None:
        '''Add `argparse.ArgumentParser` arguments.'''

        pass
