from .schitem import SchItem
from .schfile import SchFile
from .schdict import SchDict

# Make all the parts of the parser/renderer wire themselves in
def _init():
    from ..sch import comp, header, sheet, simple
_init()
