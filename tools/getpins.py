#!/usr/bin/env python2.6

'''
    Usage:  From inside a KiCAD project directory, use getpins with
            a component reference designator as the sole parameter:

              xxxxx/kipy/tools/getpins.py U13

     getpins will dump pin information to stdout.
'''

import os
import sys
from collections import defaultdict
import find_kipy
import kipy.project, kipy.parsesch

proj = kipy.project.Project(os.path.abspath('.'))
sch = kipy.parsesch.ParseSchematic(proj)

refdes, = sys.argv[1:]
refdes = refdes.upper()

def components():
    components = defaultdict(dict)
    for net in sch.netinfo:
        for pin in net.pins:
            refdes = pin.component.refdes.upper()
            assert not hasattr(pin, 'refdes') and not hasattr(pin, 'net')
            pin.refdes = refdes
            pin.net = net
            components[refdes][pin.pinnum] = pin
    return components
components = components()

def getnetname(pin):
    net = pin.net
    others = set(net.pins) - set([pin])
    otherpins = ['%s.%s' % (x.component.refdes, x.pinnum) for x in others]
    otherpins.sort()
    name = ', '.join(otherpins)
    if len(others) == 1:
        other, = others
        if other.refdes.startswith('R') and other.refdes[1:].isdigit():
            otherpins = set(components[other.refdes].itervalues())
            if len(otherpins) == 2:
                othernet, = set(x.net for x in otherpins) - set([net])
                if othernet.names:
                    name = ', '.join(othernet.names).lower()
    return name

pinlist = []
for pin in components[refdes].itervalues():
    name = ', '.join(pin.net.names).lower()
    if not name:
        name = getnetname(pin)
    pinlist.append((pin.pinnum, pin.pinname, name))

print
print refdes
for pinnum, pinname, name in sorted(pinlist):
    print '%-6s %3s %s' % (pinname, pinnum, name)
print
