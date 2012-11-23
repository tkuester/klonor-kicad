import sys
from ..utility import FileAccess

'''
Locations of KiCad stuff, by system.

Unfortunately, there seems to be different places to store things,
depending on distribution.

Don't know if this is the best way to do things, but here it is.

'''

if sys.platform.startswith('win'):
    kicad_root = FileAccess(r'c:\Program Files\KiCad\share')
else:
    kicad_root = FileAccess('/usr/local/kicad/share')

if kicad_root.exists:
    kicad_demo_root = kicad_root.demos
else:
    kicad_root = FileAccess('/usr/share/kicad')
    kicad_demo_root = kicad_root[-1].doc.kicad.demos

kicad_lib_root = kicad_root.library
kicad_default_project = kicad_root.template.kicad + '.pro'

assert kicad_root.exists, 'Could not find Kicad root directory %s' % kicad_root
assert kicad_lib_root.exists, 'Could not find Kicad library directory %s' % kicad_lib_root
assert kicad_demo_root.exists, 'Could not find Kicad demo directory %s' % kicad_demo_root
assert kicad_default_project.exists,  'Could not find default project %s' % kicad_default_project
