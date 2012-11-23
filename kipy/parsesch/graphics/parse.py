from collections import defaultdict
from .find_collisions import find_collisions
from .schitems import SchItem
from .nonnets import NonNets
from .partialnets import CreatePartialNets

class InternalParse(SchItem, NonNets, CreatePartialNets):
    _classinit = None

    def warn(self, s):
        self.warnings.append('Warning on page %s:\n      %s\n' % (self.pagename, s) )

    def warnpoint(self, s, point):
        if len(point) == 4:
            point = '((%s, %s) to (%s, %s))' % point
        else:
            point = '(%s, %s)' % point
        self.warnings.append('Warning: %s:\n      Page %s at %s' % (s, self.pagename, point) )

    def killpoints(self):
        kill = self.kill
        while kill:
            obj, point = kill.pop()
            obj.removepoint(point)

    def getbyclass(self, *clslist):
        for cls in clslist:
            for obj in self.byclass.get(cls, []):
                yield obj

    def populate_points(self):
        pointdict = self.pointdict
        for obj1, obj2 in find_collisions(self.graphic_items, normalized=True):
            obj1, obj2 = obj1[-1], obj2[-1]
            loc = obj1.overlap(obj2)
            if loc is None:
                obj1.warn('Internal problem -- Unexpected non-overlap with %s' % obj2.userinfo)
            p1, p2 = loc[:2], loc[2:]
            if p1 == p2:
                loc = p1
            myset = pointdict[loc]
            myset.add(obj1)
            myset.add(obj2)

    def checkpoints(self):
        in_pointdict = set()
        self.byclass = byclass = defaultdict(set)
        for point, objset in self.pointdict.iteritems():
            in_pointdict.update(objset)
            for obj in objset:
                obj.points.add(point)
                byclass[obj.__class__].add(obj)

        allobjs = set((x[-1] for x in self.graphic_items))
        missing = [x for x in (allobjs - in_pointdict) if not isinstance(x, self.Keepout)]
        extra = in_pointdict - allobjs - self.diags
        if missing:
            missing = '\n    '.join(sorted((x.full_info for x in missing)))
            self.warn('Unexpectedly missing objects:\n      %s' % missing)
        if extra:
            extra = '\n    '.join(sorted((x.full_info for x in extra)))
            self.warn('Unexpected extra objects:\n     %s' % extra)

    def cleanup(self):
        Component = self.Component
        Label = self.Label
        Pin = self.Pin

        allpins = set()
        for part in list(self.allparts):
            assert isinstance(part, Component), part

            for pin in part.pindict.itervalues():
                assert pin not in allpins
                allpins.add(pin)
                assert pin.component is part
        alllabels = self.alllabels
        checklabels = defaultdict(set)
        for label in alllabels:
            checklabels[label.net_ids].add((label.original_name))

        for nameset in checklabels.itervalues():
            if len(nameset) > 1:
                self.warn('Special character substitution connects multiple nets:\n          %s' %
                        nameset)


        for partial in self.partialnets:
            labels = alllabels & partial
            pins = allpins & partial
            alllabels -= labels
            allpins -= pins
            assert len(pins) + len(labels) == len(partial), partial
            for pin in pins:
                assert isinstance(pin, Pin), pin
                assert len(pin.net_ids) <= 1
            for label in labels:
                assert isinstance(label, Label), label
                assert len(label.net_ids) <= 1

        assert not alllabels, [x.full_info for x in alllabels]
        assert not allpins, allpins
        del self.alllabels

        if self.pointdict:
            self.warn('Not all points cleared: %s' % self.pointdict)
        for x, y in sorted(self.byclass.iteritems()):
            if y:
                self.warn('Class %s has remaining items: %s' % (x, y))

        assert not self.kill
        del self.pointdict, self.byclass, self.graphic_items
        del self.kill, self.maxx, self.maxy, self.diags
        del self.libdict


    def __init__(self, pagename, pageinfo, timestamp, libdict, warnings):
        self.allparts = set()
        self.alllabels = set()
        self.warnings = warnings
        self.pagename = pagename
        self.pointdict = defaultdict(set)
        self.graphic_items = []
        self.kill = set()
        self.maxx = pageinfo.dimx
        self.maxy = pageinfo.dimy
        self.diags = set()
        self.partialnets = []
        self.timestamp = timestamp
        self.libdict = libdict
        self.dispatch(pageinfo.items, self)
        self.populate_points()
        self.checkpoints()
        self.strip_nonnets()
        self.findpartialnets()
        self.cleanup()
        mydict = sorted(self.__dict__)
        expected = 'allparts pagename partialnets timestamp warnings'
        assert mydict == expected.split(), mydict

def parsesheet(pageinfo, libdict, warnings):
        graphobj = InternalParse(pageinfo.sheetname, pageinfo.sheetdata, pageinfo.timestamp, libdict, warnings)
        return graphobj.allparts, graphobj.partialnets
