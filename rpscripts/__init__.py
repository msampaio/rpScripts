'''Provide main modules and classes.'''

# from _version import __version__

from .config import VERSION as __version__
from .calculator import ParsemaeSegment
from .lib.partition import Partition
from .lib.base import RPData

from . import calculator
from . import plotter
from . import annotator
from . import labeler
from . import converter
from . import trimmer