'''This module provides classes and functions to calculate the rhythmic partitions from a given digital score.'''

import copy
import music21

from fractions import Fraction
from tqdm import tqdm

from .lib.partition import Partition
from .lib.base import CustomException, EventLocation, GeneralSubparser, RPData, file_rename, find_nearest_smaller, make_fraction


def aux_make_events_from_part(m21_part: music21.stream.Part) -> dict:
    '''Return a dictionary with Musical Events and their locations from a given
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


def aux_join_music_events(events: dict) -> dict:
    '''Join `MusicalEvent`

    This methods join adjacent tied objects as well as adjacent rests.
    '''

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


def make_music_events_from_part(m21_part: music21.stream.Part) -> dict:
    '''Return a dictionary with location and Musical Events from a given
    Music21 part object. Adjacent rests and tied notes are joined.
    '''

    events = aux_make_events_from_part(m21_part)
    return aux_join_music_events(events)


def auxiliary_get_duration(m21_obj) -> Fraction:
    '''Return the duration of the given Music21 object as a Fraction object.'''

    if m21_obj.duration.tuplets:
        tup = m21_obj.duration.tuplets[0]
        num = tup.numberNotesNormal
        den = tup.numberNotesActual
        dur = Fraction(num, den) / 2
    else:
        dur = make_fraction(m21_obj.duration.quarterLength)
    return dur


def split_part_chords(m21_part: music21.stream.Part) -> music21.stream.Part:
    '''Return a new Music21 Part object with pitches extracted from chords of a given Music21 Part object.

    This function splits chords with notes of distinct durations.
    '''

    extra_part = music21.stream.Part()
    measures = m21_part.getElementsByClass(music21.stream.Measure)
    has_split_data = False

    for measure in measures:
        m = copy.deepcopy(measure)
        m.elements = () # Remove original measure's elements

        chords = measure.getElementsByClass(music21.chord.Chord)

        for chord in chords:
            ch_duration = chord.duration
            ch_offset = chord.offset
            ch_tie = chord.tie
            if chord.tie:
                # Add rests
                if not m.notesAndRests.stream():
                    dur = chord.offset
                    rest = music21.note.Rest()
                    rest.duration = music21.duration.Duration(dur)
                    m.insert(0, rest)
                old_obj_pitches = []
                new_obj_pitches = []
                new_obj_tie = None

                for p in chord.pitches:
                    if chord.getTie(p) == chord.tie:
                        old_obj_pitches.append(p)
                    else:
                        new_obj_pitches.append(p)
                        new_obj_tie = chord.getTie(p)

                if len(new_obj_pitches) > 0:
                    has_split_data = True
                    chord.pitches = tuple(old_obj_pitches)

                    # Handle old pitches
                    if len(old_obj_pitches) == 1:
                        active_site = chord.activeSite
                        ind = chord.activeSite.index(chord)
                        chord.activeSite.pop(ind)

                        obj = music21.note.Note(old_obj_pitches[0])
                        obj.duration = ch_duration
                        obj.offset = ch_offset
                        obj.tie = ch_tie
                        active_site.insert(obj.offset, obj)

                    # Handle new pitches
                    if len(new_obj_pitches) == 1:
                        note = music21.note.Note(new_obj_pitches[0])
                        note.duration = chord.duration
                        note.offset = chord.offset
                        m.insert(note.offset, note)
                    else:
                        new_chord = music21.chord.Chord()
                        new_chord.duration = chord.duration
                        new_chord.offset = chord.offset
                        new_chord.tie = new_obj_tie
                        new_chord_pitches = list(new_chord.pitches)
                        for p in new_obj_pitches:
                            new_chord_pitches.append(p)
                        new_chord.pitches = tuple(new_chord_pitches)
                        m.insert(new_chord.offset, new_chord)

        extra_part.insert(m.offset, m)

    if has_split_data:
        ms = extra_part.getElementsByClass(music21.stream.Measure)
        for m in ms:
            original_m = m21_part.measure(m.number)
            m.offset = original_m.offset
            m.duration = original_m.duration
        return extra_part


def split_score(filename: str) -> music21.stream.Score:
    '''Parse a given digital score file, split chords, convert voices to parts and returns a new Music21 Score object.'''

    parts = []
    try:
        sco = music21.converter.parse(filename, quantizePost=False)
    except:
        raise CustomException('Error on given score parsing.')

    new_sco = music21.stream.Score()

    print('Parsing the given score...')

    for m21_part in tqdm(sco.parts):
        for _part in m21_part.voicesToParts():
            new_part = copy.deepcopy(_part)
            extra = split_part_chords(new_part)
            new_sco.insert(0, new_part)
            parts.append(new_part)
            if extra:
                new_sco.insert(0, extra)
                parts.append(extra)

    return new_sco


def make_offset_map(m21part: music21.stream.Part) -> dict:
    '''Create map with measure number and global offset value.'''

    aux_offset_map = {}
    for measure in m21part.getElementsByClass(music21.stream.Measure):
        number = measure.number
        measure_offset = make_fraction(measure.offset)
        if measure_offset not in aux_offset_map.keys():
            aux_offset_map.update({measure_offset: number})

    # Recalculate measure numbers for score fixing in ritornello cases
    new_offset_map = {}
    if 0 in aux_offset_map.values():
        measure_number = 0
    else:
        measure_number = 1

    for global_offset in aux_offset_map.keys():
        new_offset_map[measure_number] = global_offset
        measure_number += 1
    return new_offset_map


class MusicalEvent(object):
    '''Auxiliary musical event class.

    This class has only the needed attributes of Music21's Note, Rest and Chord classes.
    '''

    def __init__(self, **kwargs):
        self.measure_number = None
        self.offset = Fraction(0)
        self.global_offset = Fraction(0)
        self.number_of_pitches = 0
        self.duration = 0
        self.tie = None
        self.m21_class = None
        self.is_null = False

        if 'kwargs' in kwargs:
            self.__dict__.update(kwargs['kwargs'])

    def __eq__(self, __o: object) -> bool:
        return self.__dict__ == __o.__dict__

    def __str__(self) -> str:
        return ' '.join(list(map(str, [self.number_of_pitches, self.duration,  self.tie])))

    def __repr__(self):
        return '<E {}>'.format(self.__str__())

    def is_rest(self):
        '''Check if the current object represents a music21' rest object.'''

        return self.m21_class == music21.note.Rest

    def set_data_from_m21_obj(self, m21_obj, measure_number, measure_offset, offset=None):
        '''Get data from given Music21 object, set as current object's attributes, and return offset and duration.'''

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
    '''Auxiliary single event. It's more simple than Music21's note and rest objects and has useful attributes such ass number of pitches and sounding.'''

    def __init__(self, **kwargs):
        self.number_of_pitches = 0
        self.duration = Fraction(0)
        self.measure_number = 0
        self.offset = Fraction(0)
        self.sounding = False

        if 'kwargs' in kwargs:
            self.__dict__.update(kwargs['kwargs'])

    def __eq__(self, __o: object) -> bool:
        return self.__dict__ == __o.__dict__

    def __repr__(self) -> str:
        event_location = EventLocation(measure_number=self.measure_number, offset=self.offset)
        ind = event_location.str_index
        return '<SE ({}) num={} dur={} snd={}>'.format(ind, self.number_of_pitches, self.duration, self.sounding)


class Parsema(object):
    '''Auxiliary Parsema class.

    Parsema is the set of adjacent equal partitions. See Gentil-Nunes 2009 for further information.'''

    def __init__(self, **kwargs):
        self.measure_number = None
        self.offset = None
        self.global_offset = None
        self.duration = 0
        self.single_events = []
        self.partition = None

        if 'kwargs' in kwargs:
            self.__dict__.update(kwargs['kwargs'])

    def __eq__(self, __o: object) -> bool:
        return self.__dict__ == __o.__dict__

    def __repr__(self) -> str:
        partition_str = ''
        if self.partition:
            partition_str = self.partition.as_string()
            event_loc = EventLocation(measure_number=self.measure_number, offset=self.offset)
        return '<Pma: {} ({}), dur {}>'.format(partition_str, event_loc, self.duration)

    def add_single_events(self, single_events: list) -> None:
        '''Set single events, calculate their durations and set partition.'''

        self.single_events = single_events
        durations = [event.duration for event in single_events if event]
        if durations:
            self.duration = min(durations)

        self.set_partition()

    def set_partition(self) -> None:
        '''Create `Partition` object from single events attribute and set it to `partition` attribute.'''

        parts = {}
        number_of_pitches_set = set([
            s_event.number_of_pitches
            for s_event in self.single_events
        ])
        if list(number_of_pitches_set) == [0]:
            self.partition = Partition([])
            return
        for s_event in self.single_events:
            key = (s_event.sounding, s_event.duration)
            if key not in parts.keys() and s_event.number_of_pitches > 0:
                parts[key] = 0
            if s_event.number_of_pitches > 0:
                parts[key] += s_event.number_of_pitches

        self.partition = Partition(sorted(parts.values()))


class PartSoundingMap(object):
    '''Sounding Map class of a musical part.'''

    def __init__(self, **kwargs) -> None:
        self.single_events = None
        self.attack_global_offsets = []

        if 'kwargs' in kwargs:
            self.__dict__.update(kwargs['kwargs'])

    def __eq__(self, __o: object) -> bool:
        return self.__dict__ == __o.__dict__

    def __str__(self) -> int:
        return len(self.single_events.keys())

    def __repr__(self) -> str:
        return '<PSM: {} events>'.format(self.__str__())

    def set_from_m21_part(self, m21_part: music21.stream.Part) -> None:
        '''Set Music21's part elements into `single_events` attribute.

        Create `MusicEvent` objects for each event and then, create `SingleEvent` objects to add to `single_events` attribute.'''

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

    def get_single_event_by_location(self, global_offset: Fraction) -> SingleEvent:
        '''Return a `SingleEvent` object from its location.'''

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
    '''Sounding Map class of a musical score. Individual parts are sounding maps.'''

    def __init__(self, **kwargs) -> None:
        self.sounding_maps = []
        self.attacks = []
        self.measure_offsets = {}

        if 'kwargs' in kwargs:
            self.__dict__.update(kwargs['kwargs'])

    def __eq__(self, __o: object) -> bool:
        return self.__dict__ == __o.__dict__

    def __repr__(self) -> str:
        return '<SSM: {} maps, {} attacks>'.format(len(self.sounding_maps), len(self.attacks))

    def add_part_sounding_map(self, m21_part: music21.stream.Part) -> None:
        '''Creates a `PartSoundingMap` from a given Music21 Part and add it to sounding_maps and attacks attributes.'''

        psm = PartSoundingMap()
        psm.set_from_m21_part(m21_part)
        if psm.single_events:
            self.sounding_maps.append(psm)
            self.attacks.extend(psm.attack_global_offsets)
            self.attacks = sorted(set(self.attacks))

    def add_score_sounding_maps(self, m21_score: music21.stream.Score) -> None:
        '''Create `PartSoundingMap` objects from each part of a given Music21 Score.

        This method also get measure offsets and explodes voices into parts.'''

        # Get and fill measure offsets
        self.measure_offsets = make_offset_map(m21_score.parts[0])

        # Get and fill sounding parts
        print('Getting and filling sounding parts...')
        for m21_part in tqdm(m21_score.parts):
            for _part in m21_part.voicesToParts():
                self.add_part_sounding_map(copy.deepcopy(_part))

    def get_single_events_by_location(self, global_offset: Fraction) -> list:
        '''Return a list of `SingleEvent` objects in different sounding_maps from their locations.'''

        single_events = []
        for sounding_map in self.sounding_maps:
            s_event = sounding_map.get_single_event_by_location(global_offset)
            if s_event:
                single_events.append(s_event)
        return single_events

    def make_parsemae(self) -> list:
        '''Return a list of `Parsema` objects from `attacks` attribute.

        This method also handles merged parsemae.'''

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
            if parsema.partition.parts == first_parsema.partition.parts:
                first_parsema.duration += parsema.duration
            else:
                merged_parsemae.append(first_parsema)
                first_parsema = parsema

        merged_parsemae.append(first_parsema)

        return merged_parsemae


class ParsemaeSegment(object):
    '''Parsema segment class.'''

    def __init__(self, **kwargs) -> None:
        self.parsemae = []
        self._measure_offsets = {}

        if 'kwargs' in kwargs:
            self.__dict__.update(kwargs['kwargs'])

    def __eq__(self, __o: object) -> bool:
        return self.__dict__ == __o.__dict__

    def __repr__(self) -> str:
        return '<PS: {} parsemae>'.format(len(self.parsemae))

    def make_from_music21_score(self, m21_score: music21.stream.Score) -> None:
        '''Create `Parsema` objects fom given Music21 Score object and store at `parsemae` class attribute.'''

        ssm = ScoreSoundingMap()
        ssm.add_score_sounding_maps(m21_score)
        self.parsemae = ssm.make_parsemae()
        self._measure_offsets = ssm.measure_offsets

    def get_data(self) -> tuple:
        '''Get partitions, agglomeration, and dispersion data and their locations.'''

        data = {
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
        values_map = {}
        for parsema in self.parsemae:
            event_location = EventLocation(measure_number = parsema.measure_number, offset=parsema.offset)
            partition = parsema.partition

            partition_str = partition.as_string()
            agglomeration = partition.get_agglomeration_index()
            dispersion = partition.get_dispersion_index()

            data['Index'].append(event_location.str_index)
            data['Measure number'].append(parsema.measure_number)
            data['Offset'].append(parsema.offset)
            data['Global offset'].append(parsema.global_offset)
            data['Duration'].append(parsema.duration)
            # data['Offset'].append(fraction_to_string(parsema.offset))
            # data['Global offset'].append(fraction_to_string(parsema.global_offset))
            # data['Duration'].append(fraction_to_string(parsema.duration))
            data['Partition'].append(partition_str)
            data['Density-number'].append(partition.get_density_number())
            data['Agglomeration'].append(agglomeration)
            data['Dispersion'].append(dispersion)
            data['Parts'].append(partition.parts)

            if partition_str not in values_map.keys():
                values_map[partition_str] = (agglomeration, dispersion)
        return data, values_map

    def make_rpdata(self, filename: str) -> RPData:
        '''Return `RPData` object from `parsemae` class attribute.'''

        rpdata = RPData()
        rpdata.path = file_rename(filename, 'json')

        offset_map_orig = self._measure_offsets # values as fractions
        offset_map_conv = {mn: offset for mn, offset in offset_map_orig.items()} # values as strings
        # offset_map_conv = {mn: fraction_to_string(offset) for mn, offset in offset_map_orig.items()} # values as strings

        rpdata.data, rpdata.values_map = self.get_data()
        rpdata.partitions = rpdata.data['Partition']
        rpdata.size = len(rpdata.partitions)
        rpdata.offset_map = offset_map_conv
        return rpdata


class Subparser(GeneralSubparser):
    '''Implements argparser.'''

    def setup(self) -> None:
        self.program_name = 'calc'
        self.program_help = 'Calculator'
        self.add_parent = False

    def add_arguments(self) -> None:
        self.parser.add_argument('filename', help='digital score filename (XML, MXL, MIDI and KRN)', type=str)
        self.parser.add_argument('-c', '--csv', help='output data in a CSV file.', default=False, action='store_true')
        self.parser.add_argument('-e', '--equally_sized', help='generate equally-sized events', default=False, action='store_true')

    def handle(self, args):
        print('Running script on {} file...'.format(args.filename))

        sco = split_score(args.filename)
        segment = ParsemaeSegment()
        segment.make_from_music21_score(sco)

        rpdata = segment.make_rpdata(args.filename)
        rpdata.save_to_file()

        if args.csv:
            rpdata.save_to_csv(args.equally_sized)
