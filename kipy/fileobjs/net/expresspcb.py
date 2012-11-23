'''
Dumps a netlist in ExpressPCB format.

Currently contains a hack for 96 pin EuroDIN connector.

Since ExpressPCB doesn't allow letters in pin numbers,
converts to 1-96 from A1-32 - C1-32.

Also stores the number of pins on the net in the netname.
This makes it easier to visually determine you have seen
all the nets when you are using ExpressPCB.

'''

format = '''
"ExpressPCB Netlist"
"SwCAD III version 2.03r"
1
0
0
""
""
""
"Part IDs Table"
%s

"Net Names Table"
%s

"Net Connections Table"
%s
'''.lstrip()

def fixpinnum(part, pinnum):
    if isinstance(pinnum, int):
        return pinnum
    assert pinnum[0] in 'ABC' and pinnum[1:].isdigit(), (part, pinnum)
    index = int(pinnum[1:])
    if part == 'FX2':
        assert 1 <= index <= 50, (part, pinnum)
        return 'AB'.index(pinnum[0]) * 50 + index
    assert 1 <= index <= 32, (part, pinnum)
    return 'ABC'.index(pinnum[0]) * 32 + index

def dumpnet(netinfo, fileobj=None):
    parttable = {}
    netorder = []
    for net in netinfo:
        pininfo = []
        for pin in net.pins:
            refdes = pin.component.refdes
            part = pin.component.parttype
            pinnum = fixpinnum(part, pin.pinnum)
            assert parttable.setdefault(refdes, part) == part
            pininfo.append((refdes, pinnum))
        pininfo = sorted(pininfo)
        sortkey = net.names and net.names[0] or (-len(pininfo), pininfo)
        netorder.append((sortkey, pininfo))

    parttable = sorted(parttable.iteritems())
    partindex = dict((x[0],i+1) for (i, x) in enumerate(parttable))
    parttable = '\n'.join('"%s" "%s" ""' % (x, y) for (x,y) in parttable)

    nettable = []
    connectiontable = []
    for nameindex, (name, pininfo) in enumerate(sorted(netorder)):
        nameindex += 1
        startconn = len(connectiontable) + 1
        if not isinstance(name, str):
            name = ' '.join(sorted('%s.%s' % x for x in pininfo))
        if name.startswith('_'):
            name = '-' + name[1:]

        nettable.append('"%s (%d pins)" %d' % (name, len(pininfo), startconn))
        nextconn = range(startconn+1, startconn + len(pininfo)) + [0]
        assert len(nextconn) == len(pininfo)
        for (refdes, pinnum), nextconn in zip(pininfo, nextconn):
            connectiontable.append('%d %d %d %d' % (nameindex, partindex[refdes], pinnum, nextconn))
    nettable = '\n'.join(nettable)
    connectiontable = '\n'.join(connectiontable)

    result = format % (parttable, nettable, connectiontable)
    if fileobj is not None:
        fileobj.write(result.replace('\n', '\r\n'))
