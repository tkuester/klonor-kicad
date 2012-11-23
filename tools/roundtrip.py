#!/usr/bin/env python2.7
import os
import glob
import find_kipy
from kipy.fileobjs.paths import kicad_demo_root, kicad_lib_root
from kipy.fileobjs import ConfigFile, LibFile, SchFile
from kipy.utility import check_roundtrip

myproj = '.'

generated_files_dir = 'auto_generated_results'

try:
    os.makedirs(generated_files_dir)
except:
    pass

demo_root = os.path.join(kicad_demo_root, '*')

for root in (myproj, demo_root):
    for fn in glob.glob(os.path.join(root, '*.pro')):
        check_roundtrip(fn, ConfigFile, generated_files_dir)

for root in (myproj, kicad_lib_root):
    for fn in glob.glob(os.path.join(root, '*.lib')):
        check_roundtrip(fn, LibFile, generated_files_dir)

for root in (myproj, demo_root):
    for fn in glob.glob(os.path.join(root, '*.sch')):
        check_roundtrip(fn, SchFile, generated_files_dir)
