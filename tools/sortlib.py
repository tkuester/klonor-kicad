#!/usr/bin/env python2.6

'''
Create version of library files with the DRAW information sorted
alphabetically for easier comparison between modified libraries.
'''

import os
import glob
import find_kipy
from kipy.utility import FileAccess
from kipy.fileobjs.paths import kicad_lib_root
from kipy.fileobjs import LibFile

myproj = '.'

dumpdir = FileAccess('sorted_lib')

try:
    os.makedirs(dumpdir)
except:
    pass

for root in (myproj, kicad_lib_root):
    for fn in glob.glob(os.path.join(root, '*.lib')):
        fn = FileAccess(fn)
        lib = LibFile(fn)
        for comp in lib:
            comp.draw.sort(key = lambda x: str(x).upper())
        (dumpdir | fn.basename).write(str(lib))
