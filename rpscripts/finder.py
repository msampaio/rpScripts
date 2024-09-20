'''This module helps finding events occurrences in the given JSON file.'''

import pandas

from .config import ENCODING
from .lib.base import GeneralSubparser, RPData, file_rename

MAX_TO_PRINT = 30

def main(json_filename: str, field_name: str, value: str) -> None:
    '''Add the given TXT file labels into the given JSON file.'''

    rpdata = RPData(json_filename)

    ## Check if field is inside rpdata.data.
    if field_name in rpdata.data.keys():
        raw_data = rpdata.data[field_name]
    else:
        raw_data = getattr(rpdata, field_name)

    if field_name == 'Parts':
        raw_data = list(map(len, raw_data))
    series = pandas.Series(raw_data, index = rpdata.data['Index'])
    df = pandas.DataFrame(rpdata.data, index = rpdata.data['Index'])
    df['Number-parts'] = df['Parts'].apply(len)
    cols = ['Partition', 'Density-number', 'Number-parts', 'Agglomeration', 'Dispersion']
    if len(rpdata.tcontour) > 0:
        df['Tcontour'] = rpdata.tcontour
        cols.append('Tcontour')

    if len(rpdata.tclass) > 0:
        df['Tclass'] = rpdata.tclass
        cols.append('Tclass')

    df = df[cols]

    if value == -1:
        value = series.max()

    data = df[series==value]
    size = len(data)
    if size > 0:
        output = ''
        output += data.to_string()
        output += '\n{} ({}): {} entries'.format(field_name, value, size)
        if size <= MAX_TO_PRINT:
            print(output)
        else:
            fname = file_rename(json_filename, 'txt', '{}'.format(field_name)).lower()
            print('Saving in {}...'.format(fname))
            with open(fname, 'w') as fp:
                fp.write(output)
    else:
        print('The given event is not in the given file.')


class Subparser(GeneralSubparser):
    '''Implements argparser.'''

    def setup(self) -> None:
        self.program_name = 'find'
        self.program_help = 'Events finder. Find events in the given JSON file'

    def add_arguments(self) -> None:
        self.parser.add_argument('-p', '--partition', help="Partition (between quotation marks)", type=str)
        self.parser.add_argument('-d', '--density_number', help="Density-number", type=int)
        self.parser.add_argument('-n', '--number_of_parts', help="Number of parts", type=int)
        self.parser.add_argument('-tcl', '--tclass', help="Textural class", type=str)
        self.parser.add_argument('-tcn', '--tcontour', help="Textural contour", type=str)

        self.parser.add_argument('-md', '--max_density_number', help="Maximum density-number", action='store_true', default=False)
        self.parser.add_argument('-mn', '--max_number_of_parts', help="Maximum density-number", action='store_true', default=False)

    def handle(self, args):
        print('Running script on {} filename...'.format(args.filename))

        field_name = 'partition'

        if args.max_density_number:
            field_name = 'Density-number'
            value = -1
        elif args.max_number_of_parts:
            field_name = 'Parts'
            value = -1
        elif args.partition:
            field_name = 'Partition'
            value = args.partition
        elif args.density_number:
            field_name = 'Density-number'
            value = args.density_number
        elif args.number_of_parts:
            field_name = 'Parts'
            value = args.number_of_parts
        elif args.tclass:
            field_name = 'tclass'
            value = args.tclass
        elif args.tcontour:
            field_name = 'tcontour'
            value = args.tcontour

        main(args.filename, field_name, value)
