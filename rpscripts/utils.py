'''This module contains helpful tools for the rhythmic partitioning task.'''

import os
import shutil
from rpscripts.config import LATTICE_MAP_PATH
from .lib.partition import PartitionLattice
from .lib.base import CustomException, GeneralSubparser
import rpscripts

MAX_CARDINALITY = 70


def copy_default_lattice_map() -> None:
    '''Copy lattice map to the default path.'''

    print('Copying built-in lattice map to {}'.format(LATTICE_MAP_PATH))
    ppath = os.path.abspath(rpscripts.__file__)
    folder = os.path.dirname(os.path.dirname(ppath))
    lattice_path = os.path.join(folder, 'lattice_map.json')
    shutil.copy(lattice_path, LATTICE_MAP_PATH)


def save_map(lexset: int) -> None:
    '''Create a partition lattice of `lexset` size and save into the program's default path.'''

    if lexset > MAX_CARDINALITY:
        raise CustomException('Map is limited to cardinality {}'.format(MAX_CARDINALITY))
    lattice_map = PartitionLattice(lexset)
    lattice_map.filename = LATTICE_MAP_PATH
    lattice_map.save_file()


class Subparser(GeneralSubparser):
    '''Implements argparser.'''

    def setup(self) -> None:
        self.program_name = 'utils'
        self.program_help = 'Auxiliary tools'
        self.add_parent = False

    def add_arguments(self) -> None:
        self.parser.add_argument("-sm", "--save_map", help = "Create a lattice map with a given cardinality. Limited to {}".format(MAX_CARDINALITY), type=int)
        self.parser.add_argument("-s", "--setup", help = "Setup", action='store_true')

    def handle(self, args):
        global MAX_CARDINALITY
        MAX_CARDINALITY = 70

        if args.setup:
            copy_default_lattice_map()

        elif args.save_map:
            cardinality = args.save_map
            save_map(cardinality)
