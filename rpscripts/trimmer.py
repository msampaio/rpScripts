'''This module cuts off a given calc's JSON output file by given start and end measure numbers and return a new JSON file.'''


from .lib.base import CustomException, GeneralSubparser, RPData, file_rename


def main(rpdata: RPData, start_measure, end_measure) -> None:
    '''Trim the given RPData between the given start and end measures.'''

    global_offsets = sorted(list(rpdata.offset_map.values()))
    measures = sorted(list(map(int, list(rpdata.offset_map.keys()))))

    try:
        start_offset = global_offsets[0]
        start_label = 'init'
        if start_measure:
            if start_measure in measures:
                start_offset = rpdata.offset_map[str(start_measure)]
                start_label = int(start_measure)

        end_offset = global_offsets[-1] + 1
        end_label = 'end'
        if end_measure:
            if end_measure in measures:
                next_measure = str(end_measure + 1)
                if next_measure in rpdata.offset_map.keys():
                    end_offset = rpdata.offset_map[next_measure]
                    end_label = str(end_measure)
    except:
        raise CustomException('Given start or end measure out of piece')

    if start_label == 'init' and end_label == 'end':
        print('Given start and end measure out of the piece. Nothing done.')
        return

    new_rpdata = RPData()

    # Get limits
    start_pointer = None
    i = 0
    while i < rpdata.size and rpdata.data['Global offset'][i] < end_offset:
        if rpdata.data['Global offset'][i] >= start_offset:
            if start_pointer == None:
                start_pointer = i
        i += 1
    end_pointer = i

    new_rpdata = rpdata.trim(start_pointer, end_pointer)
    new_rpdata.path = file_rename(rpdata.path, 'json', 'excerpt-{}-{}'.format(start_label, end_label))
    new_rpdata.save_to_file()


class Subparser(GeneralSubparser):
    '''Implements argparser.'''

    def setup(self) -> None:
        self.program_name = 'trim'
        self.program_help = 'JSON file trimmer. Trim given measures'

    def add_arguments(self) -> None:
        self.parser.add_argument('-s', '--start', help='Start measure. Blank means "from the beginning"', type=int)
        self.parser.add_argument('-e', '--end', help='End measure. Blank means "to the end"', type=int)

    def handle(self, args):
        if not args.start and not args.end:
            print('No given start or end measure')
        else:
            start_measure = None
            end_measure = None
            if args.start:
                start_measure = int(args.start)
            if args.end:
                end_measure = int(args.end)

            rpdata = RPData(args.filename)

            main(rpdata, start_measure, end_measure)
