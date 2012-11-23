from .brditem import BrdItem
from .brdfile import BrdFile

# Make all the parts of the parser/renderer wire themselves in
def _init():
    from ..brd import header, equipot, module, netclass, zone, track, comment
_init()
