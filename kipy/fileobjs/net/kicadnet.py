'''
Eventually, should read/write KiCad .net files,
and fit into framework more cleanly.

For now, just read the .net files and do some basic
consistency checks.

'''
import re
from collections import defaultdict

class OneComponent(object):
    libinfo = None
    @classmethod
    def fromlist(cls, mylist):
        self = cls()
        self.pindict = pindict = {}
        while isinstance(mylist[-1], list):
            pinnum, netname = mylist.pop()
            assert pindict.setdefault(pinnum, netname) is netname
        if len(mylist) == 5:
            self.libinfo = mylist.pop()
        self.timestamp, self.footprint, self.refdes, self.parttype = mylist
        return self

class NetInfo(object):
    basefile = '(^[#*].*?\n|^\(.*?^\).*?\n|^\{.*?^\}.*?\n)'
    filesplitter = re.compile(basefile, re.DOTALL | re.MULTILINE).split

    def __init__(self, netf):
        if netf.exists:
            self.parsenet(netf)

    def parsenet(self, netf):
        data = [x.strip() for x in self.filesplitter(netf.read())]
        data = [x for x in data if x and not x.startswith('#') and x != '*']
        assert data[0].startswith('(')
        self.parsecomponents(data[0])
        for item in data[1:]:
            if item.startswith('{ Allowed footprints by component'):
                # Deal with this later
                continue  
            elif item.startswith('{ Pin List by Nets'):
                self.checknets(item)
            else:
                raise SystemExit('Unknown data: %s' % item)

    def parsecomponents(self, data):
        data = iter(data.split())
        result = []
        stack = []
        current = result
        for token in data:
            if token == '(':
                stack.append(current)
                current.append([])
                current = current[-1]
            elif token == ')':
                current = stack.pop()
            # Handle some weird carte_test in demos directory....
            elif token == '{' and stack == [result] and not current:
                for token in data:
                    if token == '}':
                        break
            else:
                current.append(token)
        assert not stack and len(result) == 1
        result = [OneComponent.fromlist(item) for item in result[0]]
        by_timestamp = defaultdict(set)
        self.by_refdes = by_refdes = {}
        by_netname = defaultdict(set)
        for c in result:
            by_timestamp[c.timestamp].add(c)
            refdes = c.refdes
            assert by_refdes.setdefault(refdes, c) is c
            for pinnum, netname in c.pindict.iteritems():
                by_netname[netname].add('%s.%s' % (refdes, pinnum))
        self.by_net = by_net = {}
        self.unconnected = tuple(sorted(by_netname.pop('?', ())))
        for netname, pininfo in by_netname.iteritems():
            names = set()
            if not netname.startswith('N-') or not netname[2:].isdigit():
                names.add(netname)
            by_net[', '.join(sorted(pininfo))] = names

        for timestamp, components in by_timestamp.iteritems():
            if len(components) > 1:
                components = ', '.join(sorted(c.refdes for c in components))
                print "timestamp %s used on multiple components: %s" % (timestamp, components)

    def checknets(self, data):
        data = data.splitlines()
        assert data[0].startswith('{') and data[-1] == '}'
        data = data[1:-1]
        result = []
        for line in data:
            if line.startswith(' '):
                line = line.split()
                assert len(line) == 2
                result[-1][-1].append('%s.%s' % tuple(line))
            else:
                line = line.split()
                assert line[0].endswith('Net')
                assert line[1].isdigit()
                netnames = []
                for name in line[2:]:
                    assert name.startswith('"') and name.endswith('"')
                    netnames.append(name[1:-1])
                netnames = set(x for x in netnames if x)
                result.append((netnames, []))

        netdict = dict((', '.join(sorted(pininfo)), netinfo) for netinfo, pininfo in result)
        self.comparenets(netdict)
 
    def checkparsed(self, parsedinfo):
        f_unconnected = set(self.unconnected)
        p_unconnected = set()
        netdict = {}
        for net in parsedinfo:
            names = set(net.names)
            pins = ['%s.%s' % (x.component.refdes, x.pinnum) for x in net.pins]
            if len(pins) == 1:
                p_unconnected.update(pins)
            else:
                netdict[', '.join(sorted(pins))] = names
        self.comparenets(netdict, 'netlist parsed from .sch file')
        if f_unconnected - p_unconnected:
            print "Unconnected pins only listed in net file: ", f_unconnected - p_unconnected
        if p_unconnected - f_unconnected:
            print "Unconnected pins not listed in net file: ", p_unconnected - f_unconnected


    def comparenets(self, netdict, header='netlist file net definitions'):
        def basename(name):
            return name.rsplit('/',1)[-1].replace('-', '_')
        from_comp = self.by_net
        netset = set(netdict)
        pinset = set(from_comp)
        pins_only = pinset - netset
        nets_only = netset - pinset
        if pins_only:
            print "\nNets only in netlist file component pin definitions:\n     %s\n" % sorted((x, from_comp[x]) for x in pins_only)
        if nets_only:
            print "Nets only in %s:\n     %s\n" % (header, sorted((x, netdict[x]) for x in nets_only))
        for key in (netset & pinset):
            cnetnames = from_comp[key]
            nnetnames = netdict[key]
            if cnetnames & nnetnames or (not cnetnames and not nnetnames):
                continue
            cn = set(basename(x) for x in cnetnames)
            nn = set(basename(x) for x in nnetnames)
            if cn & nn:
                continue
            print "Net connecting %s: different names %s and %s" % (key, cnetnames, nnetnames)
