'''

This module exports one function, makenetlist, which returns a netlist
representation, when given a list of partial nets from the graphic submodule.

Internally, the NetInfo class is used to group all the functions of generating
the netlist together.  It uses makenetgroups.makegroups to do the initial
grouping of the partial nets, and then handles globals, similar names,
invisible pins, etc.


'''

import re
from collections import defaultdict
from .makenetgroups import makegroups
from ..utility import IndexedString


class NetInfo(object):

    def warn(self, *s):
        self.warnings.append('Warning: %s\n' % '\n          '.join(s))

    @staticmethod
    def sortnames(names):
        ''' Sort names higher in the hierarchy before lower names.
        '''
        return sorted(names, key= lambda x:(x.count('/'), x))

    @staticmethod
    def getshortname(net_id):
        return net_id.rsplit('/',1)[-1]

    def canonicalize(self,
                id_pattern = re.compile('([a-zA-Z]+|[0-9]+|\+| \/ )')):
        ''' Convert all net names into canonical versions:
                1) uppercase all letters
                2) remove leading zeros from numerical portions
                3) convert all non-alphanumeric characters except '+'
                    into underscores
                4) convert all separators ' / ' into '/'
                5) Warn about any changes that result in two
                    previously different names being made the same.
        '''

        def canonical(s):
            def id_parts(s):
                for s in id_pattern.split(s):
                    if not s:
                        pass
                    elif s.isalpha():
                        yield s.upper()
                    elif s.isdigit():
                        yield str(int(s, 10))
                    elif s == ' / ':
                        yield '/'
                    elif s == '+':
                        yield '+'
                    else:
                        yield '_'
            return IndexedString(''.join(id_parts(s)))

        def rename(new, old):
            new = self.by_net_id[new]
            if new is old:
                return
            oldname = old.original or old
            newname = new.original or new
            if new.group is not None:
                self.warn('Similarly named signals merged:', '"%s" into "%s"' % (oldname, newname))
            new.merge(old)
            new.items.update(old.items)
            new.original = new.original or oldname
            old.group.remove(old)
            old.group = None
            old.items.clear()
            del self.by_net_id[old]

        def getbyname():
            # Dictionary indexed by canonicalized signal name of
            #     Dictionary indexed by non-canonicalized signal name of
            #        Set of new net IDs, old net IDs
            #           Set of net ids
            byname = defaultdict(dict)
            for oldid in self.by_net_id:
                newid = canonical(oldid)
                oldname = oldid.rsplit(' / ', 1)[1]
                newname = newid.rsplit('/', 1)[1]
                byname[newname].setdefault(oldname, []).append((newid, oldid))
            return byname.itervalues()

        def convertdict(namedict):
            namelist = list(namedict.iteritems())
            namelist.sort(key=lambda x: (len(x[1]), x[0], x[1]))
            if len(namelist) > 1:
                self.warn('The following net names are considered to be the same name:',
                        ', '.join(x[0] for x in namelist))
            for oldname, id_tuples in namelist:
                for newid, oldid in sorted(id_tuples):
                    rename(newid, oldid)

        for namedict in getbyname():
            convertdict(namedict)


    def find_nettypes(self):
        ''' Determine the type of net for every NetId
        '''
        def _assert(what, message):
            if not what:
                    self.warn(message, net_id)

        implicitglobals = set()
        explicitglobals = set()

        for net_id in self.by_net_id:
            pins = net_id.find_pins
            slabels = net_id.find_slabels
            hlabels = net_id.find_hlabels
            glabels = net_id.find_glabels
            labels = net_id.find_labels

            if pins:
                implicitglobals.add(net_id)
                _assert(not (labels or slabels or hlabels), 'Local sheet signal connected automatically to global')
                _assert(not glabels, 'Global signal used both implicitly and explicitly')
            elif slabels:
                _assert(not glabels, 'Global label misused as hierarchical')
                _assert(len(slabels) <= 1, 'Multiple connections to label on instantiating sheet')
                _assert(len(hlabels) + len(glabels) <= 1, 'Multiple entry points onto sheet for hierarchical label')
            elif hlabels:
                _assert(0, 'Hierarchical label not connected in instantiating sheet')
            elif glabels:
                explicitglobals.add(net_id)
                _assert(len(glabels) <= 1, 'Multiple connections to global signal on sheet')

        return implicitglobals, explicitglobals


    def connect_globals(self):
        ''' Connect the globals together across sheets
        ''' 
        globaldict = {}

        def merged(srcset):
            result = defaultdict(set)
            for item in srcset:
                globalnet = self.by_net_id[self.getshortname(item)]
                result[globalnet].add(item)
                globalnet.merge(item)
            return result

        implicit, explicit = self.find_nettypes()
        implicit = merged(implicit)
        explicit = merged(explicit)

        for net_id, old_ids in explicit.iteritems():
            if len(old_ids) == 1:
                net_id, = old_ids
                if len(net_id.group.find_real_pins) > 1:
                    self.warn('Global net only used on one page:', net_id)

        for net_id in (set(implicit) & set(explicit)):
            self.warn('Global net used both implicitly and explicitly:',
                    'Explicit: %s' % sorted(explicit[net_id])[0],
                    'Implicit: %s' % sorted(implicit[net_id])[0])


    def shorten_names(self):
        ''' Strip the hierarchy off the front of names where possible
        '''
        getshortname = self.getshortname
        by_net_id = self.by_net_id
        shortnames = defaultdict(set)
        for net_ids in self.allgroups:
            for net_id in net_ids:
                shortnames[getshortname(net_id)].add(net_id)

        for shortname, nameset in shortnames.iteritems():
            groups = [(x.group, x) for x in nameset]
            groups = dict(((id(x), (x, y)) for (x, y) in groups))
            groups = list(groups.itervalues())
            if len(groups) == 1:
                shortname = self.by_net_id[shortname]
                if shortname.group is None:
                    shortname.merge(groups[0][0])
                else:
                    assert shortname.group is groups[0][0]
            else:
                assert groups
                self.warn('Unconnected local nets of same name:',
                    '; '.join(sorted((x[1] for x in groups))))

    def namegroups(self):
        ''' Store the names associated with each group inside it.
        '''
        getshortname = self.getshortname

        def selectshortest(names):
            return self.sortnames(names)[0]


        for group in self.allgroups:
            if group:
                names = defaultdict(set)
                for net_id in group:
                    names[getshortname(net_id)].add(net_id)
                names.pop('?', None)  # Use "?" to mean "no net"
                names = [selectshortest(x) for x in names.itervalues()]
                names = self.sortnames(names)
                if len(names) > 1:
                    self.warn('Aliased net names:', str(names))
                group.names = tuple(names)
            else:
                group.names = ()

    def find_pins(self):
        ''' Rummage through the group items and pull the pins out
            into a separate set.
        '''
        goodgroups = []
        self.allgroups, oldgroups = goodgroups, self.allgroups
        for group in oldgroups:
            if not group and not group.items:
                continue
            goodgroups.append(group)
            group.pins = pins = set()
            for pin in group.find_real_pins:
                pin.group = group
                pins.add(pin)
                net_ids = pin.net_ids
                if not net_ids:
                    continue
                others = pin.partial.net_ids - set(net_ids)
                if not others:
                    continue
                self.warn('Visible net connected to invisible pin',
                            '%s connects %s and %s' %
                            (pin.full_info, ', '.join(net_ids), ', '.join(others)))

            if len(pins) > 1:
                continue

            name = ', '.join(group.names)
            for pin in pins:
                if name:
                    self.warn('Net connects no other pins -- net name ignored',
                            'Net %s, %s' % (name, pin.full_info))
                else:
                    if not pin.partial.single_pin:
                        self.warn('Pin not connected in final netlist', pin.full_info)
                break
            else:
                goodgroups.pop()
                if name:
                    self.warn('Named net ignored (contains no pins)', name)
                else:
                    bigspace = '\n' + 20 * ' '
                    self.warn('Unconnected net',
                        'Elements:%s%s' % (bigspace,
                            bigspace.join(sorted(x.full_info for x in group.items))))

    def kill_aliased_pins(self, pinlist):
        groups = set((id(pin.group) for pin in pinlist))
        if len(groups) > 1:
            bigspace = '\n' + 20 * ' '
            self.warn('Aliased pins connected to different nets',
                    'Elements:%s%s' % (bigspace,
                        bigspace.join(sorted('%s %s' % (x.full_info, x.group.names) for x in pinlist))))
        pinlist.pop()
        for pin in pinlist:
            pin.group.pins.remove(pin)

    def check_aliased_pins(self):
        ''' For parts with multiple sub-parts and invisible shared pins,
            consolidate the shared pins.
        '''
        partdict = defaultdict(dict)
        for group in self.allgroups:
            for pin in group.pins:
                partdict[pin.component.refdes].setdefault(pin.pinnum, []).append(pin)
        aliasedpins = []
        for pindict in partdict.itervalues():
            for pinnum, info in pindict.iteritems():
                if len(info)> 1:
                    self.kill_aliased_pins(info)

    def getinfo(self):
        return[ (group.names, group.pins) for group in self.allgroups]

    def __init__(self, allpartials, warnings):
        self.warnings = warnings
        self.allpartials = allpartials
        self.by_net_id, self.allgroups = makegroups(allpartials)
        self.canonicalize()
        self.connect_globals()
        self.shorten_names()
        self.namegroups()
        self.find_pins()
        self.check_aliased_pins()

class OneNet(object):
    def __init__(self, names, pins):
        self.__dict__.update(locals())

    def __str__(self):
        return 'Net %s\n     %s' % (
            ', '.join(self.names),
            '\n     '.join(sorted((x.full_info for x in self.pins))))

def makenetlist(allpartials, warnings):
    mylist = NetInfo(allpartials, warnings).getinfo()
    mylist = [OneNet(*x) for x in mylist]
    return mylist
