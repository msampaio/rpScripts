'''This module contains RP Scripts' global variables.

These variables are used in multiple modules.'''


import os

ENCODING = 'utf-8'
HOME_DIR = os.path.expanduser('~')
AUX_NAME = 'rps_aux'
AUX_DIR = os.path.join(HOME_DIR, AUX_NAME)

if not os.path.exists(AUX_DIR):
    print('Creating the folder {}...'.format(AUX_DIR))
    os.mkdir(AUX_DIR)

lattice_map_filename = 'lattice_map.json'

LATTICE_MAP_PATH = os.path.join(AUX_DIR, lattice_map_filename)

# Remove date and time for stable versions
VERSION = '2.0.dev.20230512-2015GMT'