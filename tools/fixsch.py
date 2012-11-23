#!/usr/bin/env python2.6
'''
This is an example of how to fix a schematic.

I had a schematic where my resistor parts had the values
in the footprint field (because I incorrectly defined the library part).

So this script replaces 'res' fields with the footprint fields.

'''

import os
import glob
import find_kipy
from kipy.fileobjs import SchFile
from kipy.utility import FileAccess

root ='.'

for fn in glob.glob(os.path.join(root, '*.sch')):
    fn = FileAccess(fn)
    sch = SchFile(fn)
    changed = False
    for item in sch.items:
        if not isinstance(item, sch.Component):
            continue
        fields = item.fields
        if fields[1][0] == 'RES':
            fields[1] = fields[2]
            fields[2] = None
            changed = True
    if changed:
        fn.write(sch)
