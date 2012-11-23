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
import copy
import re
from kipy.fileobjs import SchFile
from kipy.fileobjs import SchItem
from kipy.fileobjs.sch.simple import *
from kipy.fileobjs.sch.comp import Component
from kipy.fileobjs.sch.schfile import LibInfo
from kipy.utility import FileAccess
from optparse import OptionParser
from evalrefdes import subRefDes

class StringAccess(FileAccess):
    def __init__(self, string):
        self.strdata = string

    def read(self):
        return self.strdata 

class CloneItem(SchItem):
    default_parse_class = None

    def __init__(self, original):
        self.lib_info = []
        self.items= []
        aslist = []
        original.render(aslist)
        aslist.append('')
        self.startparse(self, StringAccess('\n'.join(aslist)).readlinetokens())

    def render(self, linelist):
        for item in self.items:
            item.render(linelist)

def newRefDes(item, clone, x, y, xoffset, yoffset, cloneno):
    if clone.__class__ == Component:
        clone.refdes = subRefDes(item.refdes, cloneno)
        clone.posx = item.posx + xoffset * x
        clone.posy = item.posy + yoffset * y
        clone.fields[0][0] = clone.refdes
        for field in clone.fields:
            field[2] = field[2] + xoffset * x
            field[3] = field[3] + yoffset * y

    if item.__class__ == Wire:
        clone.startx = clone.startx + xoffset * x
        clone.starty = clone.starty + yoffset * y
        clone.endx = clone.endx + xoffset * x
        clone.endy = clone.endy + yoffset * y

    if item.__class__ == Text:
        clone.text = subRefDes(item.text, cloneno)
        clone.posx = clone.posx + xoffset * x
        clone.posy = clone.posy + yoffset * y

    if item.__class__ == Connection:
        clone.posx = clone.posx + xoffset * x
        clone.posy = clone.posy + yoffset * y
            
def initOptions():
    parser = OptionParser()
    parser.add_option("", "--template-sch", dest="macrosch",
                      help="the original template schematic", metavar="SCH")
    parser.add_option("", "--output-sch", dest="schout",
                      help="output schematic file, will be overwritten",
                      metavar="SCH")
    parser.add_option("", "--xclones", dest="xclones", type="int", default=0,
                      help="number of clones to make along x axis",
                      metavar="INT")
    parser.add_option("", "--yclones", dest="yclones", type="int", default=0,
                      help="number of clones to make along y axis",
                      metavar="INT")
    parser.add_option("", "--xsize", dest="xsize", type="int", default=0,
                      help="x offset for clones", metavar="INT")
    parser.add_option("", "--ysize", dest="ysize", type="int", default=0,
                      help="y offset for clones", metavar="INT")
    return parser

def main():
    oparser = initOptions() 
    (opts, args) = oparser.parse_args()
    fn = opts.macrosch
    outfn = opts.schout
    xcopies = opts.xclones
    ycopies = opts.yclones
    xsize = opts.xsize
    ysize = opts.ysize

    if (fn == None) or (outfn == None):
        oparser.exit('File names must be specified, --help for help')
    
    if xcopies + ycopies == 0:
        oparser.exit('Specify more than zero copies in X and/or Y dimensions')

    if (xcopies > 0) and (xsize == 0):
        oparser.exit('Specify xsize of a clone in magic KiCad units, e.g. 8000; --help for help')
    if (ycopies > 0) and (ysize == 0):
        oparser.exit('Specify ysize of a clone in magic KiCad units, e.g. 2000; --help for help')

    print 'Going to make %s copies along X axis with spacing of %s' % (xcopies,xsize)
    print 'Going to make %s copies along Y axis with spacing of %s' % (ycopies,ysize)

    fn = FileAccess(fn)
    sch = SchFile(fn)

    newitems = []
    for item in sch.items:
        clown = -1
        for y in xrange(ycopies+1):
            if y == ycopies: continue
            for x in xrange(xcopies+1):
                clown = clown + 1
                ii = CloneItem(item).items[0]
                newRefDes(item, ii, x, y + 1, xsize, ysize, clown)
                newitems.append(ii)

    sch.items = sch.items + newitems
    
    print 'Saving result to ', outfn
    output = FileAccess(outfn)
    output.write(sch)

main()

