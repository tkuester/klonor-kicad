#!/usr/bin/env python2.7
'''
    Check the schematic of one or more projects.

    May give a list of projects on the command line.

    If not project explicitly given, checks all the
    projects in the current directory.
'''
import sys
import os
import glob
import find_kipy
from kipy.project import Project
from kipy.parsesch import ParseSchematic
from kipy.fileobjs.net import kicadnet

projfiles = sys.argv[1:]
if projfiles:
    projfiles = [os.path.abspath(x) for x in projfiles]
else:
    projroot = os.path.abspath('.')
    projfiles = glob.glob(os.path.join(projroot, '*.pro'))

if not projfiles:
    print "No project files found"
    raise SystemExit(1)

for projfile in projfiles:
    print
    if len(projfiles) > 1:
        print 60*'='
        print
        print projfile
        print
    proj = Project(projfile)
    sch = ParseSchematic(proj)
    if not proj.netfn.exists:
        print "Netlist file %s not found" % proj.netfn
        continue
    netlistf = kicadnet.NetInfo(proj.netfn)
    netlistf.checkparsed(sch.netinfo)
print

#project.libdict.check_duplicates()
