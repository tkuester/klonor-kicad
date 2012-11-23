#!/usr/bin/env python2.6
'''
Strip the dates out of schematic and library files for easier
interoperability with subversion.

Just run this before using subversion diff or checkin, and
unchanged files will remain unchanged.

'''

import os
import glob
import find_kipy
from kipy.fileobjs import LibFile, SchFile
from kipy.utility import FileAccess

root ='.'

for fn in glob.glob(os.path.join(root, '*-cache.lib')):
        fn = FileAccess(fn)
        lib = LibFile(fn)
        lib.topline = lib.topline.split(' Date: ')[0].strip()
        fn.write(lib)

for fn in glob.glob(os.path.join(root, '*.sch')):
        fn = FileAccess(fn)
        sch = SchFile(fn)
        sch.page_header.linetext = sch.page_header.linetext.split(' date ')[0].strip()
        fn.write(sch)
