'''This shows information about data.'''


from .lib.base import GeneralSubparser, RPData


def main(filename: str) -> None:
    '''Print basic information about the given filename.'''

    rpdata = RPData(filename)
    distinct_partitions = len(set(rpdata.partitions))
    distinct_density_numbers = len(set(rpdata.data['Density-number']))
    ratio = round(distinct_partitions / distinct_density_numbers, 2)
    data = {
        'This file contains labels data': rpdata.labels != [],
        'Number of events': rpdata.size,
        'Number of distinct partitions': distinct_partitions,
        'Number of distinct density numbers': distinct_density_numbers,
        'Ratio partitions/dn': ratio,
        'Highest dispersion index': max(rpdata.data['Dispersion']),
        'Highest agglomeration index': max(rpdata.data['Agglomeration']),
    }
    for k, v in data.items():
        print('{}: {}'.format(k, v))


class Subparser(GeneralSubparser):
    '''Implements argparser.'''

    def setup(self) -> None:
        self.program_name = 'info'
        self.program_help = 'JSON data info.'

    def handle(self, args):
        main(args.filename)
