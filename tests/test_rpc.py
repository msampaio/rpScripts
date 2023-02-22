from fractions import Fraction
import unittest

import music21

from src.rpc import MusicalEvent, Parsema, PartSoundingMap, ScoreSoundingMap, SingleEvent, Texture, aux_join_music_events, aux_make_events_from_part, auxiliary_find_interval, auxiliary_get_duration,  find_nearest_smaller, get_common_denominator_from_list, get_common_fractions_denominator, get_number_combinations_pairs, make_fraction, make_music_events_from_part, pretty_partition_from_list


def make_data():
    '''Return a dictionary with reusing data for tests.'''

    # Make Music21 Part
    custom_m21_part = music21.stream.Part()
    m1 = music21.stream.Measure(number=1)
    m2 = music21.stream.Measure(number=2)
    n1 = music21.note.Note('C4')
    n2 = music21.note.Note('D4')
    n3 = music21.note.Note('D4')
    n2.tie = music21.tie.Tie('start')
    n3.tie = music21.tie.Tie('stop')
    rest = music21.note.Rest()

    m1.append(n1)
    m1.append(n2)
    m2.append(n3)
    m2.append(rest)
    custom_m21_part.append(m1)
    custom_m21_part.append(m2)

    # Make custom Music21 Score
    n1 = music21.note.Note('E4')
    n2 = music21.note.Note('D4')
    n2.tie = music21.tie.Tie('start')
    n3 = music21.note.Note('D4')
    n3.tie = music21.tie.Tie('stop')
    n4 = music21.note.Note('C4')
    n5 = music21.note.Note('C4', duration=music21.duration.Duration(2))
    n6 = music21.note.Note('C4')
    n7 = music21.note.Note('C4')

    custom_m21_part1 = music21.stream.Part()
    custom_m21_part2 = music21.stream.Part()

    p1m1 = music21.stream.Measure()
    p1m2 = music21.stream.Measure()
    p2m1 = music21.stream.Measure()
    p2m2 = music21.stream.Measure()

    p1m1.append(n1)
    p1m1.append(n2)
    p1m2.append(n3)
    p1m2.append(n4)

    p2m1.append(n5)
    p2m2.append(n6)
    p2m2.append(n7)

    custom_m21_part1.append(p1m1)
    custom_m21_part1.append(p1m2)

    custom_m21_part2.append(p2m1)
    custom_m21_part2.append(p2m2)

    custom_m21_score = music21.stream.Score()
    custom_m21_score.insert(0, custom_m21_part1)
    custom_m21_score.insert(0, custom_m21_part2)

    # Make musical events
    musical_events = {
        Fraction(0, 1): MusicalEvent(kwargs={
            'measure_number': 1, 'offset': 0, 'global_offset': 0, 'number_of_pitches': 1, 'duration': Fraction(1, 1), 'tie': None, 'm21_class': music21.note.Note, 'is_null': False
        }),
        Fraction(1, 1): MusicalEvent(kwargs={
            'measure_number': 1, 'offset': Fraction(1, 1), 'global_offset': Fraction(1, 1), 'number_of_pitches': 1, 'duration': Fraction(1, 1), 'tie': 'start', 'm21_class': music21.note.Note, 'is_null': False
        }),
        Fraction(2, 1): MusicalEvent(kwargs={
            'measure_number': 2, 'offset': 0, 'global_offset': Fraction(2, 1), 'number_of_pitches': 1, 'duration': Fraction(1, 1), 'tie': 'stop', 'm21_class': music21.note.Note, 'is_null': False
        }),
        Fraction(3, 1): MusicalEvent(kwargs={
            'measure_number': 2, 'offset': Fraction(1, 1), 'global_offset': Fraction(3, 1), 'number_of_pitches': 0, 'duration': Fraction(1, 1), 'tie': None, 'm21_class': music21.note.Rest, 'is_null': False
        })
    }

    # Make joined musical events
    joined_musical_events = {
        Fraction(0, 1): MusicalEvent(kwargs={
            'measure_number': 1, 'offset': 0, 'global_offset': 0, 'number_of_pitches': 1, 'duration': Fraction(1, 1), 'tie': None, 'm21_class': music21.note.Note, 'is_null': False
        }),
        Fraction(1, 1): MusicalEvent(kwargs={
            'measure_number': 1, 'offset': Fraction(1, 1), 'global_offset': Fraction(1, 1), 'number_of_pitches': 1, 'duration': Fraction(2, 1), 'tie': 'start', 'm21_class': music21.note.Note, 'is_null': False
        }),
        Fraction(3, 1): MusicalEvent(kwargs={
            'measure_number': 2, 'offset': Fraction(1, 1), 'global_offset': Fraction(3, 1), 'number_of_pitches': 0, 'duration': Fraction(1, 1), 'tie': None, 'm21_class': music21.note.Rest, 'is_null': False
        })
    }

    # Make single events
    single_events1 = [
        SingleEvent(kwargs={
            'measure_number': 0,
            'offset': 0,
            'duration': Fraction(1, 1),
            'number_of_pitches': 1,
            'sounding': False,
        }),
        SingleEvent(kwargs={
            'measure_number': 0,
            'offset': 0,
            'duration': Fraction(2, 1),
            'number_of_pitches': 1,
            'sounding': False,
        }),
    ]

    single_events2 = [
        SingleEvent(kwargs={
            'measure_number': 0,
            'offset': 1,
            'duration': Fraction(1, 1),
            'number_of_pitches': 1,
            'sounding': False,
        }),
        SingleEvent(kwargs={
            'measure_number': 0,
            'offset': 1,
            'duration': Fraction(1, 1),
            'number_of_pitches': 1,
            'sounding': False,
        }),
    ]

    single_events3 = [
        SingleEvent(kwargs={
            'measure_number': 1,
            'offset': Fraction(0),
            'duration': Fraction(1, 1),
            'number_of_pitches': 1,
            'sounding': False,
        }),
        SingleEvent(kwargs={
            'measure_number': 1,
            'offset': Fraction(1, 1),
            'duration': Fraction(2, 1),
            'number_of_pitches': 1,
            'sounding': False,
        }),
        SingleEvent(kwargs={
            'measure_number': 2,
            'offset': Fraction(1, 1),
            'duration': Fraction(1, 1),
            'number_of_pitches': 0,
            'sounding': False,
        }),
    ]

    agglomeration_single_events = [
        SingleEvent(kwargs={
            'measure_number': 1,
            'offset': Fraction(0),
            'duration': Fraction(1),
            'number_of_pitches': 1,
            'sounding': False,
        }) for _ in range(8)
    ]

    dispersion_single_events = [
        SingleEvent(kwargs={
            'measure_number': 1,
            'offset': Fraction(0),
            'duration': Fraction(i + 1),
            'number_of_pitches': 1,
            'sounding': True if i % 2 else False,
        }) for i in range(10)
    ]

    # Make parsema
    custom_parsemae = [
        Parsema(kwargs={
            'measure_number': 0,
            'offset': 0,
            'global_offset': 0,
            'duration': Fraction(3, 1),
            'single_events': single_events1,
            'partition_info': [1, 1],
            'partition_pretty': '1^2'
        }),
        Parsema(kwargs={
            'measure_number': 0,
            'offset': 3,
            'global_offset': 3,
            'duration': Fraction(1, 1),
            'single_events': single_events2,
            'partition_info': [2],
            'partition_pretty': '2'
        }),
    ]

    agg_parsema = Parsema()
    agg_parsema.add_single_events(agglomeration_single_events)

    disp_parsema = Parsema()
    disp_parsema.add_single_events(dispersion_single_events)

    data = {
        'm21_part': custom_m21_part,
        'm21_part1': custom_m21_part1,
        'm21_part2': custom_m21_part2,
        'm21_score': custom_m21_score,
        'musical_events': musical_events,
        'joined_musical_events': joined_musical_events,
        'single_events1': single_events1,
        'single_events2': single_events2,
        'single_events3': single_events3,
        'agglomeration_single_events': agglomeration_single_events,
        'dispersion_single_events': dispersion_single_events,
        'parsemae': custom_parsemae,
        'agglomeration_parsema': agg_parsema,
        'dispersion_parsema': disp_parsema,
    }

    return data


class TestRPCFunctions(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

        self.custom_data = make_data()

    def test_get_number_combinations_pairs(self):
        self.assertEqual(get_number_combinations_pairs(-1), 1)
        self.assertEqual(get_number_combinations_pairs(0), 0)
        self.assertEqual(get_number_combinations_pairs(4), 6)

    def test_make_fraction(self):
        self.assertEqual(make_fraction(0), Fraction(0))
        self.assertEqual(make_fraction(Fraction(0)), Fraction(0))
        self.assertEqual(make_fraction(0.5), Fraction(1, 2))
        self.assertEqual(make_fraction(Fraction(1, 2)), Fraction(1, 2))
        self.assertEqual(make_fraction(1/2), Fraction(1, 2))
        self.assertEqual(make_fraction(1), Fraction(1))

    def test_get_common_fractions_denominator(self):
        f1 = Fraction(1, 2)
        f2 = Fraction(1, 3)
        f3 = Fraction(2, 3)
        f4 = Fraction(1, 5)
        f5 = Fraction(1, 7)
        self.assertEqual(get_common_fractions_denominator([f1, f2]), 6)
        self.assertEqual(get_common_fractions_denominator([f1, f3]), 6)
        self.assertEqual(get_common_fractions_denominator([f1, f2, f4]), 30)
        self.assertEqual(get_common_fractions_denominator([f1, f2, f4, f5]), 210)

    def test_get_common_denominator_from_list(self):
        f1 = Fraction(1, 2)
        f2 = Fraction(1, 3)
        f3 = Fraction(1, 6)
        self.assertEqual(get_common_denominator_from_list([f1, f2]), f3)

    def test_find_nearest_smaller(self):
        seq = [1/2, 1, 3/2, 2]
        self.assertEqual(find_nearest_smaller(0, seq), -1)
        self.assertEqual(find_nearest_smaller(1/2, seq), 1/2)
        self.assertEqual(find_nearest_smaller(3/4, seq), 1/2)
        self.assertEqual(find_nearest_smaller(3, seq), 2)

    def test_auxiliary_find_interval(self):
        dic = {0: 1, 1: 3}
        self.assertEqual(auxiliary_find_interval(0, dic, 0), (0, 0))

    def test_aux_make_events_from_part(self):
        self.assertEqual(aux_make_events_from_part(self.custom_data['m21_part']), self.custom_data['musical_events'])

    def test_aux_join_music_events(self):
        self.assertEqual(aux_join_music_events(self.custom_data['musical_events']), self.custom_data['joined_musical_events'])

    def test_make_music_events_from_part(self):
        self.assertEqual(make_music_events_from_part(self.custom_data['m21_part']), self.custom_data['joined_musical_events'])

    def test_pretty_partition_from_list(self):
        self.assertEqual(pretty_partition_from_list([]), '0')
        self.assertEqual(pretty_partition_from_list([1, 2, 3]), '1.2.3')
        self.assertEqual(pretty_partition_from_list([1, 1, 2, 3, 3]), '1^2.2.3^2')

    def test_auxiliary_get_duration(self):
        m1 = music21.note.Rest(1)
        m2 = music21.note.Rest(0.5)
        m3 = music21.note.Rest(Fraction(1, 3))
        self.assertEqual(auxiliary_get_duration(m1), Fraction(1))
        self.assertEqual(auxiliary_get_duration(m2), Fraction(1, 2))
        self.assertEqual(auxiliary_get_duration(m3), Fraction(1, 3))


class TestRPCMusicalEvent(unittest.TestCase):
    def test_set_data_from_m21_obj(self):
        # Rest
        m1 = music21.note.Rest()
        event1 = MusicalEvent()
        event1.set_data_from_m21_obj(m1, 1, Fraction(0), Fraction(0))
        answer1 = MusicalEvent(kwargs={
            'measure_number': 1,
            'offset': Fraction(0),
            'global_offset': Fraction(0),
            'duration': Fraction(1),
            'm21_class': music21.note.Rest
        })

        # Note
        m2 = music21.note.Note('C4')
        event2 = MusicalEvent()
        event2.set_data_from_m21_obj(m2, 1, Fraction(0), Fraction(0))
        answer2 = MusicalEvent(kwargs={
            'measure_number': 1,
            'offset': Fraction(0),
            'global_offset': Fraction(0),
            'number_of_pitches': 1,
            'duration': Fraction(1),
            'm21_class': music21.note.Note
        })

        # Tied Note
        m3 = music21.note.Note('C4')
        m3.tie = music21.tie.Tie('start')
        event3 = MusicalEvent()
        event3.set_data_from_m21_obj(m3, 1, Fraction(0), Fraction(0))
        answer3 = MusicalEvent(kwargs={
            'measure_number': 1,
            'offset': Fraction(0),
            'global_offset': Fraction(0),
            'number_of_pitches': 1,
            'duration': Fraction(1),
            'tie': 'start',
            'm21_class': music21.note.Note
        })

        # Chord
        m4 = music21.chord.Chord('C E G')
        event4 = MusicalEvent()
        event4.set_data_from_m21_obj(m4, 1, Fraction(0), Fraction(0))
        answer4 = MusicalEvent(kwargs={
            'measure_number': 1,
            'offset': Fraction(0),
            'global_offset': Fraction(0),
            'number_of_pitches': 3,
            'duration': Fraction(1),
            'm21_class': music21.chord.Chord
        })

        self.assertEqual(event1, answer1)
        self.assertEqual(event2, answer2)
        self.assertEqual(event3, answer3)
        self.assertEqual(event4, answer4)


class TestRPCParsema(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

        self.custom_data = make_data()

    def test_add_single_events(self):
        parsema1 = Parsema()
        parsema1.add_single_events(self.custom_data['agglomeration_single_events'])

        answer1 = Parsema()
        answer1.single_events = self.custom_data['agglomeration_single_events']
        answer1.duration = Fraction(1)
        answer1.partition_info = [8]
        answer1.partition_pretty = '8'

        parsema2 = Parsema()
        parsema2.add_single_events(self.custom_data['dispersion_single_events'])

        answer2 = Parsema()
        answer2.single_events = self.custom_data['dispersion_single_events']
        answer2.duration = Fraction(1)
        answer2.partition_info = [1] * 10
        answer2.partition_pretty = '1^10'

        self.assertEqual(parsema1, answer1)
        self.assertEqual(parsema2, answer2)

    def test_set_partition_info(self):
        parsema1 = Parsema()
        parsema1.single_events = self.custom_data['agglomeration_single_events']
        parsema1.duration = 0
        parsema1.set_partition_info()

        self.assertEqual(parsema1.partition_info, [8])

    def test_get_density_number(self):
        parsema1 = self.custom_data['agglomeration_parsema']
        parsema2 = self.custom_data['dispersion_parsema']
        self.assertEqual(parsema1.get_density_number(), 8)
        self.assertEqual(parsema2.get_density_number(), 10)

    def test_count_binary_relations(self):
        parsema1 = self.custom_data['agglomeration_parsema']
        parsema2 = self.custom_data['dispersion_parsema']
        self.assertEqual(parsema1.count_binary_relations(), 28)
        self.assertEqual(parsema2.count_binary_relations(), 45)

    def test_get_agglomeration_index(self):
        parsema1 = self.custom_data['agglomeration_parsema']
        parsema2 = self.custom_data['dispersion_parsema']
        self.assertEqual(parsema1.get_agglomeration_index(), 28)
        self.assertEqual(parsema2.get_agglomeration_index(), 0)

    def test_get_dispersion_index(self):
        parsema1 = self.custom_data['agglomeration_parsema']
        parsema2 = self.custom_data['dispersion_parsema']
        self.assertEqual(parsema1.get_dispersion_index(), 0)
        self.assertEqual(parsema2.get_dispersion_index(), 45)


class TestRPCPartSoundingMap(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

        self.custom_data = make_data()

    def test_set_from_m21_part(self):
        single_events = self.custom_data['single_events3']
        answer = {
            'single_events': {
                (Fraction(0, 1), Fraction(1, 1)): single_events[0],
                (Fraction(1, 1), Fraction(3, 1)): single_events[1],
                (Fraction(3, 1), Fraction(4, 1)): single_events[2],
            },
            'attack_global_offsets': [Fraction(0, 1), Fraction(1, 1), Fraction(3, 1)],
        }

        psm = PartSoundingMap()
        psm.set_from_m21_part(self.custom_data['m21_part'])

        self.assertEqual(psm.__dict__, answer)

    def test_get_single_event_by_location(self):
        single_events = self.custom_data['single_events3']
        psm = PartSoundingMap(kwargs={
            'single_events': {
                (Fraction(0, 1), Fraction(1, 1)): single_events[0],
                (Fraction(1, 1), Fraction(3, 1)): single_events[1],
                (Fraction(3, 1), Fraction(4, 1)): single_events[2],
            },
            'attack_global_offsets': [Fraction(0, 1), Fraction(1, 1), Fraction(3, 1)],
        })

        self.assertEqual(psm.get_single_event_by_location(Fraction(0)), single_events[0])


class TestRPCScoreSoundingMap(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

        self.custom_data = make_data()

    def test_add_part_sounding_map(self):
        single_events = self.custom_data['single_events3']
        mapped_events = {
            'single_events': {
                (Fraction(0, 1), Fraction(1, 1)): single_events[0],
                (Fraction(1, 1), Fraction(3, 1)): single_events[1],
                (Fraction(3, 1), Fraction(4, 1)): single_events[2],
            },
            'attack_global_offsets': [Fraction(0, 1), Fraction(1, 1), Fraction(3, 1)],
        }

        psm = PartSoundingMap(kwargs={
            'single_events': mapped_events['single_events'],
            'attack_global_offsets': mapped_events['attack_global_offsets']
        })

        data = {
            'sounding_maps': [psm],
            'attacks': psm.attack_global_offsets,
            'measure_offsets': {},
        }

        ssm = ScoreSoundingMap()
        ssm.add_part_sounding_map(self.custom_data['m21_part'])

        self.assertEqual(ssm.__dict__, data)

    def test_add_score_sounding_maps(self):
        ssm = ScoreSoundingMap()
        ssm.add_score_sounding_maps(self.custom_data['m21_score'])

        psm1 = PartSoundingMap()
        psm1.set_from_m21_part(self.custom_data['m21_part1'])

        psm2 = PartSoundingMap()
        psm2.set_from_m21_part(self.custom_data['m21_part2'])

        answer = ScoreSoundingMap()
        answer.attacks = [Fraction(0, 1), Fraction(1, 1), Fraction(2, 1), Fraction(3, 1)]
        answer.sounding_maps = [psm1, psm2]
        answer.measure_offsets = {0: Fraction(0, 1)}

        self.assertEqual(ssm, answer)

    def test_get_single_events_by_location(self):

        answer = [
            SingleEvent(kwargs={
                'measure_number': 0,
                'offset': 1,
                'duration': Fraction(3, 2),
                'number_of_pitches': 1,
                'sounding': True,
            }),
            SingleEvent(kwargs={
                'measure_number': 0,
                'offset': 0,
                'duration': Fraction(1, 2),
                'number_of_pitches': 1,
                'sounding': True,
            }),
        ]

        ssm = ScoreSoundingMap()
        ssm.add_score_sounding_maps(self.custom_data['m21_score'])
        self.assertEqual(ssm.get_single_events_by_location(Fraction(3, 2)), answer)

    def test_make_parsemae(self):
        answer = self.custom_data['parsemae']

        ssm = ScoreSoundingMap()
        ssm.add_score_sounding_maps(self.custom_data['m21_score'])

        self.assertEqual(ssm.make_parsemae(), answer)


class TestRPCTexture(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

        self.custom_data = make_data()

    def test_make_from_music21_score(self):
        answer = Texture(kwargs={
            'parsemae': self.custom_data['parsemae'],
            '_measure_offsets': {0: Fraction(0, 1)}
        })

        texture = Texture()
        texture.make_from_music21_score(self.custom_data['m21_score'])

        self.assertEqual(texture, answer)

    def test_auxiliary_get_data(self):
        answer = {
            'header': ['Index', 'Measure number', 'Offset', 'Global offset', 'Duration', 'Partition', 'Density-number', 'Agglomeration', 'Dispersion'],
            'data': [
                [(0, Fraction(0, 1)), 0, Fraction(0, 1), Fraction(0, 1), Fraction(3, 1), '1^2', 2, 0.0, 1.0],
                [(0, Fraction(3, 1)), 0, Fraction(3, 1), Fraction(3, 1), Fraction(1, 1), '2', 2, 1.0, 0.0]
            ]
        }

        texture = Texture()
        texture.make_from_music21_score(self.custom_data['m21_score'])

        self.assertEqual(texture._auxiliary_get_data(), answer)


    def test_auxiliary_get_data_complete(self):
        answer = {
            'header': ['Index', 'Measure number', 'Offset', 'Global offset', 'Duration', 'Partition', 'Density-number', 'Agglomeration', 'Dispersion'],
            'data': [
                ['0+0', 0, Fraction(0, 1), Fraction(0, 1), Fraction(3, 1), '1^2', 2, 0.0, 1.0],
                ['0+1', 0, Fraction(1, 1), Fraction(1, 1), Fraction(3, 1), '1^2', 2, 0.0, 1.0],
                ['0+2', 0, Fraction(2, 1), Fraction(2, 1), Fraction(3, 1), '1^2', 2, 0.0, 1.0],
                ['0+3', 0, Fraction(3, 1), Fraction(3, 1), Fraction(1, 1), '2', 2, 1.0, 0.0]
            ]
        }

        texture = Texture()
        texture.make_from_music21_score(self.custom_data['m21_score'])

        self.assertEqual(texture._auxiliary_get_data_complete(), answer)

    def test_get_data(self):
        answer = {
            'header': ['Index', 'Measure number', 'Offset', 'Global offset', 'Duration', 'Partition', 'Density-number', 'Agglomeration', 'Dispersion'],
            'data': [
                ['0+0', 0, Fraction(0, 1), Fraction(0, 1), Fraction(3, 1), '1^2', 2, 0.0, 1.0],
                ['0+1', 0, Fraction(1, 1), Fraction(1, 1), Fraction(3, 1), '1^2', 2, 0.0, 1.0],
                ['0+2', 0, Fraction(2, 1), Fraction(2, 1), Fraction(3, 1), '1^2', 2, 0.0, 1.0],
                ['0+3', 0, Fraction(3, 1), Fraction(3, 1), Fraction(1, 1), '2', 2, 1.0, 0.0]
            ]
        }

        texture = Texture()
        texture.make_from_music21_score(self.custom_data['m21_score'])

        self.assertEqual(texture.get_data(), answer)


if __name__ == '__main__':
    unittest.main()