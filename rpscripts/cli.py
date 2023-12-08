'''This module provides the command line interface.'''

import argparse

from .config import VERSION

from . import annotator
from . import calculator
from . import converter
from . import info
from . import labeler
from . import plotter
from . import stats
from . import trimmer
from . import utils

from . import tclass

def main() -> None:
    '''Parse the given command line arguments.'''

    # Subparsers
    parsers = [
        calculator.Subparser,
        plotter.Subparser,
        annotator.Subparser,
        labeler.Subparser,
        info.Subparser,
        utils.Subparser,
        stats.Subparser,
        converter.Subparser,
        trimmer.Subparser,
    ]

    # Add new custom arg parsers here
    parsers.extend([
        tclass.Subparser,
    ])

    main_parser = argparse.ArgumentParser(
                prog = 'rpscripts',
                description = 'Rhythmic Partitioning Scripts.',
                epilog = 'Further information available at https://github.com/msampaio/rpScripts')

    main_parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + VERSION)

    subparsers = main_parser.add_subparsers(
        title='Subcommands',
        description='Available subcommands',
    )

    # Initialize subparsers
    for parser_class in parsers:
        parser_class(subparsers).add_arguments()

    args = main_parser.parse_args()

    # args.func(args) # uncomment to check problems
    try:
        args.func(args)
    except AttributeError:
        main_parser.error('Too few arguments. Try rpscripts -h for help.')


if __name__ == '__main__':
    main()