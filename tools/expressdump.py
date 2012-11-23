#!/usr/bin/env python2.6
'''
   Parse the schematic in the current project, and output a netlist
   in ExpressPCB format.
'''
import os
import find_kipy
import kipy.project, kipy.parsesch, kipy.fileobjs.net.expresspcb

proj = kipy.project.Project(os.path.abspath('.'))
sch = kipy.parsesch.ParseSchematic(proj)

outfile = proj.projdir | proj.projname + '_expresspcb.net'

kipy.fileobjs.net.expresspcb.dumpnet(sch.netinfo, outfile)
