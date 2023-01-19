import argparse
import copy
import csv
import fractions
import math
import music21
import numpy


def get_number_combinations_pairs(n):
    return n * (n - 1) / 2


def make_fraction(value):
    if isinstance(value, fractions.Fraction):
        return fractions.Fraction(int(value.numerator), int(value.denominator))
    else:
        a, b = value.as_integer_ratio()
        return fractions.Fraction(int(a), int(b))


def get_common_fractions_denominator(fractions_lst):
    denominators = [fr.denominator for fr in fractions_lst]
    return numpy.lcm.reduce(denominators)


def get_common_denominator_from_list(seq):
    diffs = [b - a for a, b in zip(seq, seq[1:])]
    values = map(make_fraction, sorted(list(set(diffs))))
    return fractions.Fraction(1, get_common_fractions_denominator(values))


def find_nearest_smaller(value, seq):
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


def auxiliary_find_interval(value, dic, i=0):
    size = len(dic.keys())

    if i > size - 1:
        raise IndexError('Given index is out of dic')

    keys = list(dic.keys())
    while i < size - 1 and value >= dic[keys[i + 1]]:
        i += 1

    return keys[i], i


def aux_make_events_from_part(m21_part):
    '''Return a dictionary with location and Musical Events from a given
    Music21 part object.
    '''

    measures = m21_part.getElementsByClass(music21.stream.Measure)

    events = {}

    for m21_measure in measures:
        notes_and_rests = m21_measure.notesAndRests
        offset = 0 # manual calculation
        for m21_obj in notes_and_rests:
            m_event = MusicalEvent()
            offset = m_event.set_data_from_m21_obj(m21_obj, m21_measure.number, m21_measure.offset, offset)
            events.update({
                m_event.global_offset: m_event
            })

    return events


def aux_join_music_events(events):

    # Add null event at the end
    last_location = list(events.keys())[-1]
    last_event = events[last_location]
    last_location += last_event.duration + 1
    current_event = MusicalEvent()
    current_event.is_null = True
    events.update({
        last_location: MusicalEvent()
    })

    # Start with null
    last_event = None
    last_location = None
    joined_events = {}

    for location, current_event in events.items():
        if current_event.is_null: # any - null
            joined_events.update({last_location: last_event})
        else:
            if not last_event: # null - any
                last_event = current_event
                last_location = location
            else:
                if current_event.is_rest():
                    if last_event.is_rest(): # rest - rest
                        last_event.duration += current_event.duration
                    else: # note - rest
                        joined_events.update({last_location: last_event})
                        last_event = current_event
                        last_location = location
                else:
                    if last_event.is_rest(): # rest - note
                        joined_events.update({last_location: last_event})
                        last_event = current_event
                        last_location = location
                    else: # note - note
                        if current_event.tie:
                            if current_event.tie == 'start': # note - note.start
                                joined_events.update({last_location: last_event})
                                last_event = current_event
                                last_location = location
                            else: # note - note.continue or note.stop
                                last_event.duration += current_event.duration
                        else:
                                joined_events.update({last_location: last_event})
                                last_event = current_event
                                last_location = location

    return joined_events


def make_music_events_from_part(m21_part):
    '''Return a dictionary with location and Musical Events from a given
    Music21 part object. Adjacent rests and tied notes are joined.
    '''

    events = aux_make_events_from_part(m21_part)
    return aux_join_music_events(events)


def pretty_partition_from_list(seq):
    if not seq:
        return '0'
    dic = {}
    for el in seq:
        if el not in dic.keys():
            dic[el] = 0
        dic[el] += 1
    partition =  '.'.join([str(k) if v < 2 else '{}^{}'.format(k, v)
        for k, v in sorted(dic.items())
    ])

    return partition


def auxiliary_get_duration(m21_obj):
    if m21_obj.duration.tuplets:
        tup = m21_obj.duration.tuplets[0]
        num = tup.numberNotesNormal
        den = tup.numberNotesActual
        dur = fractions.Fraction(num, den) / 2
    else:
        dur = make_fraction(m21_obj.duration.quarterLength)
    return dur


class CustomException(Exception):
    pass


class MusicalEvent(object):
    def __init__(self):
        self.offset = 0
        self.global_offset = 0
        self.number_of_pitches = 0
        self.duration = 0
        self.tie = None
        self.m21_class = None
        self.is_null = False

    def __str__(self) -> str:
        return ' '.join(list(map(str, [self.number_of_pitches, self.duration,  self.tie])))

    def __repr__(self):
        return '<E {}>'.format(self.__str__())

    def is_rest(self):
        return self.m21_class == music21.note.Rest

    def set_data_from_m21_obj(self, m21_obj, measure_number, measure_offset, offset=None):
        self.measure_number = measure_number
        self.offset = offset
        self.global_offset = self.offset + make_fraction(measure_offset)
        self.duration = auxiliary_get_duration(m21_obj)
        self.m21_class = m21_obj.__class__

        if self.is_rest():
            self.number_of_pitches = 0
        else:
            if m21_obj.isNote:
                self.number_of_pitches = 1
            else:
                self.number_of_pitches = len(m21_obj.pitches)
            if m21_obj.tie:
                if m21_obj.tie.type in ['start', 'continue', 'stop']:
                    self.tie = m21_obj.tie.type
        return offset + self.duration


class SingleEvent(object):
    def __init__(self):
        self.number_of_pitches = 0
        self.duration = 0
        self.measure_number = 0
        self.offset = 0
        self.sounding = False
        self.partition_info = []


class Parsema(object):
    def __init__(self):
        self.measure_number = None
        self.offset = None
        self.global_offset = None
        self.duration = 0
        self.single_events = []
        self.partition_info = []
        self.partition_pretty = ''

    def __repr__(self):
        return '<P: {} ({}, {}), dur {}>'.format(self.partition_pretty, self.measure_number, self.offset, self.duration)

    def add_single_events(self, single_events):
        self.single_events = single_events
        durations = [event.duration for event in single_events if event]
        if durations:
            self.duration = min(durations)

        self.set_partition_info()
        self.partition_pretty = pretty_partition_from_list(self.partition_info)

    def set_partition_info(self):
        partitions = {}
        number_of_pitches_set = set([
            s_event.number_of_pitches
            for s_event in self.single_events
        ])
        if list(number_of_pitches_set) == [0]:
            return [0]
        for s_event in self.single_events:
            key = (s_event.sounding, s_event.duration)
            if key not in partitions.keys() and s_event.number_of_pitches > 0:
                partitions[key] = 0
            if s_event.number_of_pitches > 0:
                partitions[key] += s_event.number_of_pitches
        self.partition_info = sorted(partitions.values())

    def get_density_number(self):
        return int(sum(self.partition_info))

    def count_binary_relations(self):
        density_number = self.get_density_number()
        return get_number_combinations_pairs(density_number)

    def get_agglomeration_index(self):
        if self.partition_info == []:
            return None
        return float(sum([get_number_combinations_pairs(n) for n in self.partition_info]))

    def get_dispersion_index(self):
        if self.partition_info == []:
            return None
        return float(self.count_binary_relations() - self.get_agglomeration_index())


class PartSoundingMap(object):
    def __init__(self):
        self.single_events = None
        self.attack_global_offsets = []

    def __str__(self):
        return len(self.single_events.keys())

    def __repr__(self):
        return '<PSM: {} events>'.format(self.__str__())

    def set_from_m21_part(self, m21_part):
        music_events = make_music_events_from_part(m21_part)
        self.single_events = {}
        for global_offset, m_event in music_events.items():
            # interval: closed start and open end.
            closed_beginning = global_offset
            open_ending = closed_beginning + m_event.duration

            single_event = SingleEvent()
            single_event.number_of_pitches = m_event.number_of_pitches
            single_event.duration = m_event.duration
            single_event.measure_number = m_event.measure_number
            single_event.offset = m_event.offset

            self.single_events.update({
                (closed_beginning, open_ending): single_event
            })
            self.attack_global_offsets.append(closed_beginning)

    def get_single_event_by_location(self, global_offset):
        beginning = find_nearest_smaller(global_offset, self.attack_global_offsets)

        if beginning == -1: # No event to return
            return

        ind = self.attack_global_offsets.index(beginning)
        _, ending = list(self.single_events.keys())[ind]
        s_event = None
        if global_offset >= beginning and global_offset < ending:
            s_event = copy.deepcopy(self.single_events[(beginning, ending)])
            duration_diff = global_offset - beginning
            duration = s_event.duration
            duration = duration - duration_diff
            sounding = duration_diff > 0
            s_event.duration = duration
            if s_event.number_of_pitches > 0:
                s_event.sounding = sounding
            else:
                s_event.sounding = False
        return s_event


class ScoreSoundingMap(object):
    def __init__(self):
        self.sounding_maps = []
        self.attacks = []
        self.measure_offsets = {}

    def __repr__(self):
        return '<SSM: {} maps, {} attacks>'.format(len(self.sounding_maps), len(self.attacks))

    def add_part_sounding_map(self, m21_part):
        psm = PartSoundingMap()
        psm.set_from_m21_part(m21_part)
        if psm.single_events:
            self.sounding_maps.append(psm)
            self.attacks.extend(psm.attack_global_offsets)
            self.attacks = sorted(set(self.attacks))

    def add_score_sounding_maps(self, m21_score):
        # Get and fill measure offsets
        offset_map = m21_score.parts[0].offsetMap()
        self.measure_offsets = {}

        for om in offset_map:
            if isinstance(om.element, music21.stream.Measure):
                if om.element.number not in self.measure_offsets.keys():
                    self.measure_offsets[om.element.number] = make_fraction(om.element.offset)

        # Get and fill sounding parts
        parts = m21_score.voicesToParts()

        for m21_part in parts:
            self.add_part_sounding_map(m21_part)

    def get_single_events_by_location(self, global_offset):
        single_events = []
        for sounding_map in self.sounding_maps:
            s_event = sounding_map.get_single_event_by_location(global_offset)
            if s_event:
                single_events.append(s_event)
        return single_events

    def make_parsemae(self):
        parsemae = []

        offset_map = {ofs: ms for ms, ofs in self.measure_offsets.items()}
        all_offsets = list(offset_map.keys())

        for attack in self.attacks:
            measure_offset = find_nearest_smaller(attack, all_offsets)
            measure_number = offset_map[measure_offset]
            offset = make_fraction(attack) - make_fraction(measure_offset)

            parsema = Parsema()
            parsema.add_single_events(self.get_single_events_by_location(attack))
            parsema.global_offset = attack
            parsema.measure_number = measure_number
            parsema.offset = offset
            parsemae.append(parsema)

        if not parsemae:
            return

        # Merge parsemae
        merged_parsemae = []
        first_parsema = parsemae[0]
        for parsema in parsemae[1:]:
            if parsema.partition_info == first_parsema.partition_info:
                first_parsema.duration += parsema.duration
            else:
                merged_parsemae.append(first_parsema)
                first_parsema = parsema

        merged_parsemae.append(first_parsema)

        return merged_parsemae


class Texture(object):
    def __init__(self):
        self.parsemae = []
        self._measure_offsets = {}

    def __repr__(self):
        return '<T: {} parsemae>'.format(len(self.parsemae))

    def make_from_music21_score(self, m21_score):
        ssm = ScoreSoundingMap()
        ssm.add_score_sounding_maps(m21_score)
        self.parsemae = ssm.make_parsemae()
        self._measure_offsets = ssm.measure_offsets

    def _auxiliary_get_data(self):
        columns = [
            'Index', # 0
            'Measure number', # 1
            'Offset', # 2
            'Global offset', # 3
            'Duration', # 4
            'Partition', # 5
            'Density-number', # 6
            'Agglomeration', # 7
            'Dispersion', # 8
        ]
        data = []
        for parsema in self.parsemae:
            ind = tuple([parsema.measure_number, parsema.offset])
            data.append([
                ind,
                parsema.measure_number,
                parsema.offset,
                parsema.global_offset,
                parsema.duration,
                parsema.partition_pretty,
                parsema.get_density_number(),
                parsema.get_agglomeration_index(),
                parsema.get_dispersion_index(),
            ])
        dic = {
            'header': columns,
            'data': data
        }
        return dic

    def _auxiliary_get_data_complete(self):
        # check indexes
        auxiliary_dic = self._auxiliary_get_data()
        data = auxiliary_dic['data']
        data_map = {row[3]: row for row in data}
        global_offsets = [row[3] for row in data]
        common = make_fraction(get_common_denominator_from_list(global_offsets))
        size = global_offsets[-1] + data[-1][4]

        new_data = []
        current_global_offset = global_offsets[0]
        last_row = data[0]

        measure_index = 0
        while current_global_offset < size:
            current_measure, measure_index = auxiliary_find_interval(current_global_offset, self._measure_offsets, measure_index)

            if current_global_offset in data_map:
                row = copy.deepcopy(data_map[current_global_offset])
                last_row = copy.deepcopy(row)
            else:
                row = copy.deepcopy(last_row)
                row[2] = current_global_offset - self._measure_offsets[current_measure]
                row[3] = current_global_offset

            row[0] = '{}+{}'.format(str(current_measure), str(row[2]))
            row[1] = current_measure
            new_data.append(row)

            last_row = row
            current_global_offset = make_fraction(current_global_offset + common)

        dic = {
            'header': auxiliary_dic['header'],
            'data': new_data,
        }

        return dic

    def get_data(self, equal_duration_events=True):
        '''Get parsemae data as dictionary with data and index. If only_parsema_list attribute is False, the data is filled with equal duration events.'''

        if equal_duration_events:
            return self._auxiliary_get_data_complete()
        else:
            return self._auxiliary_get_data()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                prog = 'rpc',
                description = 'Rhythmic Partitioning Calculator',
                epilog = 'Rhythmic Partitioning Calculator')
    parser.add_argument('filename')

    args = parser.parse_args()
    fname = args.filename

    print('Running script on {} filename...'.format(fname))
    try:
        sco = music21.converter.parse(fname)
    except:
        raise CustomException('File must be XML or KRN.')

    texture = Texture()
    texture.make_from_music21_score(sco)
    dic = texture.get_data(equal_duration_events=True)

    # Filename
    split_name = fname.split('.')
    if len(split_name) > 2:
        base = '.'.join(split_name[:-1])
    else:
        base = split_name[0]
    dest = base + '.csv'

    with open(dest, 'w') as fp:
        csv_writer = csv.writer(fp, quoting=csv.QUOTE_NONNUMERIC)
        csv_writer.writerow(dic['header'])
        csv_writer.writerows(dic['data'])