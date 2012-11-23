#!/usr/bin/env python
'''
This is an example of how to fix a schematic.

I had a schematic where my resistor parts had the values
in the footprint field (because I incorrectly defined the library part).

So this script replaces 'res' fields with the footprint fields.

'''

import os
import sys
import glob
import find_kipy
from kipy.utility import FileAccess
from kipy.fileobjs import BrdFile
from kipy.fileobjs import BrdItem
from kipy.fileobjs.brd.module import Module
from kipy.fileobjs.brd.track import Track
from kipy.fileobjs.brd.zone import CZoneOutline, PolysCorners

from kipy.fileobjs import SchFile
from kipy.fileobjs import SchItem
from kipy.fileobjs.sch.simple import *
from kipy.fileobjs.sch.comp import Component
from kipy.fileobjs.sch.simple import *

from evalrefdes import subRefDes

from optparse import OptionParser

root ='.'

class StringAccess(FileAccess):
    def __init__(self, string):
        self.strdata = string

    def read(self):
        return self.strdata 

def initOptions():
    parser = OptionParser()
    parser.add_option("", "--template-sch", dest="macrosch",
                      help="the original template schematic", metavar="SCH")
    parser.add_option("", "--template-brd", dest="brdin",
                      help="template board with all modules already loaded",
                      metavar="BRD")
    parser.add_option("", "--output-brd", dest="brdout",
                      help="output board file, which will be overwritten",
                      metavar="BRD")
    return parser

def move(module, x, y, rot):
    module.xpos = x
    module.ypos = y
    module.orientation = rot

    for pad in module.pads:
        pad['orientation'] = rot

def main():
    templateX = 20

    oparser = initOptions()
    (opts, args) = oparser.parse_args()
    schfn = opts.macrosch
    brdfn = opts.brdin
    outfn = opts.brdout
    if (schfn == None) or (brdfn == None) or (outfn == None):
        oparser.exit('All three command-line arguments must be specified')

    sch = SchFile(FileAccess(schfn))
    brd = BrdFile(FileAccess(brdfn))

    print 'hello.jpg'
    
    # build a list of modules that are supposed to be placed in the template
    originalModRefs = []
    clonedModRefs = []
    for schi in sch.items:
        if schi.__class__ == Component:
            originalModRefs.append(schi.refdes)
            for suff in xrange(100):
                clonedModRefs.append(subRefDes(schi.refdes, suff))

    print 'originalModRefs=', len(originalModRefs)
    print 'clonedModRefs=', len(clonedModRefs)

    templateMods = []
    relocateMods = []
    tracks = []
    for placed in brd.items:
        if placed.__class__ == Module:
            if placed.refdes in originalModRefs:
                templateMods.append(placed) 
            elif placed.refdes in clonedModRefs:
                relocateMods.append(placed)
        elif placed.__class__ == Track:
            track = placed
        elif placed.__class__ == CZoneOutline:
            if placed.layer == 25:
                print 'Found zone that defines the tracks to clone'
                zone = placed

    print 'templateMods=', len(templateMods)
    print 'relocateMods=', len(relocateMods)
    print 'tracks=', len(tracks)

    topleft = [10000,10000]
    bottomright = [-1, -1]
    for c in zone.corners:
        if c[0] < topleft[0]:   topleft[0] = c[0]
        if c[1] < topleft[1]:   topleft[1] = c[1]
        if c[0] > bottomright[0]: bottomright[0] = c[0]
        if c[1] > bottomright[1]: bottomright[1] = c[1]
        
    print 'Found clone zone: (%s,%s)-(%s,%s)' % tuple(topleft + bottomright)
    templateX = (bottomright[0]-topleft[0])
    print 'Using width %s as X offset for the clones' % templateX

    nclones = 0
    nclonesmax = 20
    for relocate in relocateMods:
        for template in templateMods:
            for x in xrange(nclonesmax):
                refdes = subRefDes(template.refdes, x)
                if refdes == relocate.refdes:
                    #print 'refdes=', relocate.refdes
                    if (x+1) > nclones: nclones = x + 1
                    move(relocate, template.xpos + (x+1)*templateX, template.ypos,
                      template.orientation)

    print 'nclones=', nclones

    newpos = []
    newdes = []
    for po,de in zip(track.po,track.de):
        newpos.append(po)
        newdes.append(de)

        if (po.xstart > topleft[0]) and (po.ystart > topleft[1]) and \
           (po.xend < bottomright[0]) and (po.yend < bottomright[1]):

            for x in xrange(nclones):
                newdes.append(de.clone()) 
                newpo = po.clone()
                newpo.xstart = po.xstart + (x+1)*templateX
                newpo.xend = po.xend + (x+1)*templateX
                newpos.append(newpo)
    
    track.po = newpos
    track.de = newdes

    print 'Saving output to ', outfn
    output = FileAccess(outfn)
    output.write(brd)

main()

##
