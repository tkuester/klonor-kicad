#!/usr/bin/env python2.6
'''
     Example of how you can make a BOM.
'''
import os
import collections
import find_kipy
import kipy.project, kipy.parsesch
from kipy.utility import IndexedString, refdeslist

proj = kipy.project.Project(os.path.abspath('.'))
sch = kipy.parsesch.ParseSchematic(proj, showwarnings=False)

if sch.warnings:
    sch.dumpwarnings()
    raise SystemExit(1)

outfile = proj.projdir | proj.projname + '_bom.txt'

def buildparts(sch):
    by_ref_id = {}
    by_part_type = collections.defaultdict(set)

    class OnePart(object):
        footprint = None
        defaultfields = dict(enumerate('Value Footprint Datasheet'.split()))

        @property
        def fields(self):
            return self.__dict__

        def __init__(self, source):
            refdes = source.refdes
            parttype = source.parttype
            # These are parts I happen to not want to see in BOM
            if refdes.startswith('VIA_') or parttype == 'TP':
                return

            assert by_ref_id.setdefault(refdes, self) is self

            fields = self.fields
            self.parttype = parttype
            self.refdes = refdes
            for i, field in enumerate(source.source.fields[1:]):
                if field is None:
                    continue
                value = field[0]
                fieldname = len(field) > 8 and field[8]
                if not fieldname:
                    fieldname = self.defaultfields[i]
                assert fields.setdefault(fieldname.lower(), value) is value

        def setdefaults(self):
            # I allow a 'sameas' field to reference another reference designator.
            # Saves time and energy.
            if hasattr(self, 'sameas'):
                other = by_ref_id[IndexedString(self.sameas)]
                del self.sameas
                base = other.fields.copy()
                base.update(self.fields)
                self.fields.update(base)
            if self.footprint in set(['0805', '0603', '0402', '0201']):
                parttype = self.parttype, self.value, self.footprint
            else:
                parttype = self.parttype, self.value
            by_part_type[parttype].add(self)


    for x in sch.bomparts:
        OnePart(x)
    for x in by_ref_id.itervalues():
        x.setdefaults()

    return by_part_type

def checkparts(by_part_type):
    # Make sure that for each part type, there is only
    # one value for each field entry.

    ok = True
    result = []
    for partid, partset in sorted(by_part_type.iteritems()):
        attributes = collections.defaultdict(set)
        for part in partset:
            for attr, value in part.fields.iteritems():
                attributes[attr].add(value)
        entry = {}
        entry['refdes'] = sorted(attributes.pop('refdes'))
        badstuff = [x for x in attributes.iteritems() if len(x[1]) > 1]
        if badstuff:
            ok = False
            print partid, badstuff
        else:
            for attr, valueset in attributes.iteritems():
                entry[attr], = valueset
        result.append(entry)

    if not ok:
        raise SystemExit(1)
    return result

def getbom(parts):
    # This is my schematic-specific BOM info getter

    result = []

    class BomEntry(object):
        disty = ''
        info = ''
        footprint = ''
        mfg = ''
        onhand = 0

        def fixUVBDIN(self):
            self.info = '96 pin male DIN'
            del self.value

        def fixRES(self):
            self.info = 'RES %s ohm 5%% 0603' % self.value

        def fixC(self):
            if not self.info:
                self.info = 'CAP CER %s%s 25V 0603 X7R' % (self.value, not self.value[-1:].isalpha() and ' uF' or '')

        def fixLEDX(self):
            self.info = 'THT Red LED T 1.75'

        def fixSW_PUSH_5PIN(self):
            self.info = '5 pin THT pushbutton'

        def fixFILTER(self):
            self.info = '0805 1K Ferrite Bead'

        def fixAMP_POWER(self):
            self.info = '10 pin red THT power conn'

        def fixJPDRB(self):
            refdes, = self.refdes
            self.refdes = [refdes + 'A']
            self.value = self.parttype = 'JP1X4'
            result.append(BomEntry(self.__dict__))
            self.refdes = [refdes + 'B']
            self.value = self.parttype = 'JP1X3'
            result.append(BomEntry(self.__dict__))
            self.refdes = [refdes + 'C']
            self.value = self.parttype = 'JP1X2'
            getattr(self, 'fix' + self.parttype, self.generic)()

        def generic(self):
            if not self.info:
                s = (self.mfg,
                        self.value if self.value not in self.mfg else '',
                        self.footprint)
                self.info = ' '.join(x for x in s if x)
            elif self.info and self.footprint and self.footprint not in self.info:
                self.info = '%s %s' % (self.footprint, self.info)

        def __init__(self, info):
            self.__dict__.update((x.lower(), y) for (x,y) in info.iteritems())
            getattr(self, 'fix' + self.parttype, self.generic)()
            self.numparts = (0, len(self.refdes))[self.footprint != 'DNS' and self.value != 'DNS']
            self.refdes = refdeslist(self.refdes)

        def sortorder(self):
            sortdict = dict(refdes = '0')
            items = (x for x in self.__dict__.iteritems())
            return sorted(items, key = lambda x: sortdict.get(x[0], x[0]))

        def __cmp__(self, other):
            return cmp(self.sortorder(), other.sortorder())

        def __str__(self):
            return str(self.sortorder())

    for x in parts:
        result.append(BomEntry(x))
    resdict = {}
    for x in result:
        resdict.setdefault(x.info, []).append(x)
    for x in resdict.itervalues():
        if len(x) > 1:
            x[0].refdes = ', '.join(y.refdes for y in x)
            x[0].numparts = sum(y.numparts for y in x)
            for y in x[1:]:
                #print "merging %s" % y.info
                result.remove(y)
    result.sort()
    return result

partinfo = buildparts(sch)
partinfo = checkparts(partinfo)
partinfo = getbom(partinfo)

print '\t'.join('Qty ** Description Reference BuildSize Extended Required Margin'.split()).replace('**', '  ')
fmt = '\t'.join('%d ** "%s"         "%s"      %d        %d       %d       %d'.split()).replace('**', '  ')
qty = 12
for x in partinfo:
    onhand = int(x.onhand)
    numparts = x.numparts
    total = numparts * qty
    print fmt % (numparts, x.info, x.refdes, qty,
        total, max(0, total - onhand), max(0, onhand - total))
