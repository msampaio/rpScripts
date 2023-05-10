'''This module provides annotation features. It adds data such as partition into the XML score data and saves as a MXL file.'''

from copy import deepcopy
import music21

from .lib.base import RPDATA_ATTRIBUTES, CustomException, GeneralSubparser, RPData, file_rename


def main(m21_score: music21.stream.Score, rpdata: RPData, outfilename: str, labels_name='partitions') -> None:
    '''Add data from given RPData into the given Music21 score and save its in a new outfile.
    '''

    if rpdata.__getattribute__(labels_name) == []:
        msg = 'The given RPData object has no {} data.'.format(labels_name)
        raise CustomException(msg)

    events_location = rpdata.get_events_location(labels_name)

    new_score = deepcopy(m21_score)

    p0 = new_score.parts[0]
    new_part = music21.stream.Stream()
    new_part.insert(0, music21.clef.PercussionClef())

    measures = {}

    for m in p0.getElementsByClass(music21.stream.Measure):
        new_measure = deepcopy(m)
        new_measure.elements = ()
        if m.number in events_location.keys():
            for _offset, partition in events_location[m.number]:
                rest = music21.note.Rest(quarterLength=1/256)
                rest.offset = _offset
                rest.addLyric(partition)
                new_measure.insert(_offset, rest)
            new_measure = new_measure.makeRests(fillGaps=True)
            for el in new_measure:
                el.style.color = 'white'
                el.style.hideObjectOnPrint = True
        measures.update({m.number: new_measure})

    for m in measures.values():
        new_part.append(m)

    new_part = new_part.makeRests(fillGaps=True)

    new_score.insert(0, new_part)
    new_score.write(fmt='mxl', fp=outfilename)


class Subparser(GeneralSubparser):
    '''Implements argparser.'''

    def setup(self) -> None:
        self.program_name = 'annotate'
        self.program_help = 'Digital score annotator'

    def add_arguments(self) -> None:
        attributes = ', '.join(RPDATA_ATTRIBUTES)

        self.parser.add_argument('-s', '--score_filename', help="digital score filename (XML, MXL, MIDI and KRN)", type=str, required=True)
        self.parser.add_argument('-t', '--type', help="type of annotation ({})".format(attributes), type=str, default='partitions')

    def handle(self, args):
        sco_fname = args.score_filename
        json_fname = args.filename

        print('Running script on {} filename...'.format(sco_fname))

        try:
            sco = music21.converter.parse(sco_fname)
        except:
            raise CustomException('Error on given score parsing.')

        outfile = file_rename(json_fname, 'mxl', 'annotated-{}'.format(args.type))

        rpdata = RPData(json_fname)

        if args.type not in RPDATA_ATTRIBUTES:
            raise AttributeError('Chosen type "{}" is not available.'.format(args.type))

        main(sco, rpdata, outfile, args.type)
