'''This module converts calculator's JSON output into CSV file with or without intermediary equally-sized events.'''


from .lib.base import GeneralSubparser, RPData


def main(filename: str, equally_sized=False) -> None:
    '''Create `RPData` object from given filename and save the data into a csv file.

    If `equally_sized` parameter is true, the events are proportionally divided into smaller events of a unique duration.'''

    rp_data = RPData(filename)
    rp_data.save_to_csv(equally_sized)


class Subparser(GeneralSubparser):
    '''Implements argparser.'''

    def setup(self) -> None:
        self.program_name = 'convert'
        self.program_help = 'JSON file converter. Convert JSON to CSV file'

    def add_arguments(self) -> None:
        self.parser.add_argument('-e', '--equally_sized', help='generate equally-sized events', default=False, action='store_true')

    def handle(self, args) -> None:
        equally_sized = False
        if args.equally_sized:
            equally_sized = True

        main(args.filename, equally_sized)
