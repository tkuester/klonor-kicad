import textwrap
from collections import defaultdict
from ..utility import IndexedString
from .graphics import parsesheet
from .getnets import makenetlist


class ParseSchematic(object):

    def warn(self, s):
        self.warnings.append('Warning: %s\n' % s)

    def checkparts(self, allparts):
        partdict = defaultdict(list)
        for part in allparts:
            partdict[part.refdes.upper()].append(part)

        allpins = set()
        bomparts = set()

        for refdes, parts in partdict.iteritems():
            if not refdes or refdes.endswith('?'):
                for part in parts:
                    if not part.virtual_component:
                        part.warn('Unassigned reference designator')
                continue
            if len(parts) > 1:
                parts.sort(key=lambda x: (x.libpart, x.subpart, x.userinfo, x))

                # All shared parts must have same underlying library part
                ok = parts[0].libpart == parts[-1].libpart

                # All shared parts must exactly form a complete unit
                unit_count = parts[0].libpart.unit_count
                unit_list = [x.subpart for x in parts]
                ok = ok and unit_list == range(1, unit_count + 1)

                if not ok:
                    self.warn('Reference designator %s -- expect %s unique subparts, got:\n          %s' %
                            (parts[0].refdes, unit_count, '\n          '.join(sorted((part.full_info for part in parts)))))
                    continue
            if not parts[0].virtual_component:
                bomparts.add(parts[0])
            pindict = defaultdict(set)
            for part in parts:
                for pinnum, pin in part.pindict.iteritems():
                    pindict[pinnum].add(pin)
                    if not part.virtual_component:
                        allpins.add((refdes, pinnum))
            for pinset in pindict.itervalues():
                if len(pinset) <= 1:
                        continue
                invisible, pin = min(((x.invisible, x) for x in pinset))
                if not invisible:
                    self.warn('Non-invisible shared pin encountered:\n          %s' %
                                     pin.full_info)
                automagic = [(x.net_ids, x) for x in pinset]
                automagic.sort()
                if automagic[0][0] != automagic[-1][0]:
                    automagic[0][1].warn('Invisibly connected net different than %s' % automagic[-1][0])
        return allpins, bomparts

    def dumpwarnings(self):
        warndict = defaultdict(list)
        for w in self.warnings:
            w1, w2 = w.split('\n',1)
            warndict[w1].append(IndexedString(w2.rstrip()))

        if not warndict:
            print "No warnings found"
            print

        for w, wlist in sorted(warndict.iteritems()):
            wlist.sort()
            stripped = [x.strip() for x in wlist]
            if max((len(x) for x in stripped)) <= 30:
                wlist = textwrap.wrap(', '.join(stripped), initial_indent='     ', subsequent_indent='     ')
            print w
            if wlist:
                print '\n'.join((wlist))
            print

    def getnetpins(self, nets):
        result = set()
        for net in nets:
            for pin in net.pins:
                result.add((pin.component.refdes.upper(), pin.pinnum))
        return result

    def __init__(self, project, showwarnings=True, dumpnets=False):
        self.warnings = warnings = []
        pagedb = project.schematic
        libdb = project.libdict

        allparts = set()
        allpartials = set()

        if showwarnings:
            print '\nChecking %d pages\n' % len(pagedb)

        if not pagedb:
            self.warn('No schematic pages found')

        for page in pagedb.itervalues():
            pageparts, pagepartials = parsesheet(page, libdb, warnings)
            allparts.update(pageparts)
            allpartials.update(pagepartials)


        self.netinfo = makenetlist(allpartials, warnings)

        netpins = self.getnetpins(self.netinfo)
        partpins, self.bomparts = self.checkparts(allparts)

        if not self.netinfo:
            self.warn('No netlist found')

        onlyonpart = ['%s.%s' % x for x in (partpins - netpins)]
        onlyinnet = ['%s.%s' % x for x in (netpins - partpins)]
        if onlyonpart:
            self.warn('Pins on part but not found in netlist\n     %s' % ', '.join(sorted(onlyonpart)))
        if onlyinnet:
            self.warn('Pins in netlist but not found on part\n     %s' % ', '.join(sorted(onlyinnet)))

        if showwarnings:
            self.dumpwarnings()

        if dumpnets:
            for stuff in self.netinfo:
                print stuff
                print
