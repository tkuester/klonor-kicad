#!/usr/bin/env python2.7
'''
    Check the schematics of all the KiCAD demo projects
'''
import os
import glob
import traceback
import find_kipy
from kipy.fileobjs.paths import kicad_demo_root
from kipy.project import Project
from kipy.parsesch import ParseSchematic
from kipy.fileobjs.net import kicadnet

for projname in sorted(glob.glob(os.path.join(kicad_demo_root, '*/*.pro'))):
    print '\n%s\n\nReading project %s\n' % (60*'=', projname)
    proj = Project(projname)
    if proj.topschfname:
        try:
            sch = ParseSchematic(proj)
            if not proj.netfn.exists:
                print "Netlist file %s not found" % proj.netfn
                continue
            netlistf = kicadnet.NetInfo(proj.netfn)
            netlistf.checkparsed(sch.netinfo)
        except Exception:
            print traceback.format_exc()
