'''This module contains RP Scripts' global variables.

These variables are used in multiple modules.'''


import os
import shutil

import rpscripts

lattice_map_filename = 'lattice_map.json'

ENCODING = 'utf-8'
HOME_DIR = os.path.expanduser('~')
AUX_NAME = 'rps_aux'
AUX_DIR = os.path.join(HOME_DIR, AUX_NAME)
LATTICE_MAP_PATH = os.path.join(AUX_DIR, lattice_map_filename)

# Copy lattice map it it doesn't exist
if not os.path.exists(LATTICE_MAP_PATH):
    if not os.path.exists(AUX_DIR):
        print('Creating the folder {}...'.format(AUX_DIR))
        os.mkdir(AUX_DIR)

    print('Setting up lattice map...')
    mpath = os.path.dirname(os.path.abspath(rpscripts.__file__))
    orig_dir = os.path.join(mpath, 'data')
    shutil.copy(os.path.join(orig_dir, lattice_map_filename), AUX_DIR)