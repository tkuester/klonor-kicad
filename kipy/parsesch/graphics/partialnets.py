
class PartialNet(frozenset):
    point = 0,0
    single_pin = False


class CreatePartialNets(object):
    '''  This is a mix-in class for ParsePage.
         It will not work standalone.
         It contains all the logic for creating
         net pieces out of the point dictionary.
         Non-net points must be stripped first.
    '''

    def instantiate_single(self, mynet, single_pin, point, sizes=None):
        if sizes is not None and sizes[-1][0] > 1:
            for (size, obj) in sizes:
                if size > 1:
                    obj.warn('Wire to bus connection ignored')
                    mynet.remove(obj)
                    self.instantiate_single([obj], True, point)

        mynet = PartialNet(mynet)
        self.partialnets.append(mynet)
        mynet.point = point
        mynet.pagename = self.pagename
        if single_pin:
            mynet.single_pin = True

    def instantiate_bus(self, mynet, single_pin, point, sizes):
        maxsize, biggest = sizes[-1]
        delta = maxsize - sizes[0][0]
        if delta:
            for (size, obj) in sizes:
                if size <= 1:
                    obj.warn('Wire to bus connection ignored')
                    mynet.remove(obj)
                    self.instantiate_single([obj], True, point)
                elif size < maxsize:
                    obj.warn('Bus-size mismatch to %s -- %s signals ignored' % (biggest.userinfo, maxsize - size))

        reverse = sorted(((x.reverse_order, x) for x in mynet))
        if reverse[0][0] != reverse[-1][0]:
            for a in mynet:
                for b in mynet:
                    if a.reverse and not b.reverse:
                        a.warn('Connection between this bus and %s reversed' % b.userinfo)

        signals = [x.fracture() for x in mynet]
        if delta:
            dummy = delta * [None]
            for x in signals:
                x.extend(dummy)

        for mynet in zip(*signals):
            if delta:
                mynet = [x for x in mynet if x is not None]
            self.instantiate_single(mynet, single_pin, point)

    def makepartial(self, originalobj):

        def warnpoint(what, verbose=False):
            if verbose:
                extrainfo = '\n            '.join(sorted((x.full_info for x in pointdict[point])))
                what = '%s\n            %s' % (what, extrainfo)
                self.warn(what % (point,))
            else:
                self.warnpoint(what, point)

        Wire = self.Wire
        Label = self.Label
        Connection = self.Connection
        PinType = self.Pin, self.SLabel

        pointdict = self.pointdict
        kill = self.kill

        workq = set([originalobj])
        done = set()
        mynet = []
        single_pin = False
        netpoints = set()
        danglies = []
        foundtypes = set()
        while workq:
            workobj = workq.pop()
            done.add(workobj)
            for point in workobj.points:
                if point in netpoints:
                    continue
                netpoints.add(point)
                wires = []
                conn = []
                pins = []
                labels = []
                for obj in pointdict[point]:
                    kill.add((obj, point))
                    if isinstance(obj, Wire):
                        wires.append(obj)
                        if obj is workobj:
                            pass
                        elif obj in done | workq:
                            obj.warn('Wires connected in loop')
                        else:
                            workq.add(obj)
                    elif isinstance(obj, PinType):
                        mynet.append(obj)
                        pins.append(obj)
                    elif isinstance(obj, Label):
                        mynet.append(obj)
                        labels.append(obj)
                    elif isinstance(obj, Connection):
                        conn.append(obj)
                    else:
                        obj.warn('Unexpected connection at %s' % (point,))

                wiretype = set((x.wiretype for x in wires))
                if wiretype:
                    foundtypes.update(wiretype)
                    if len(wiretype) > 1:
                        warnpoint('Bus entry needed')

                if len(point) != 2:
                    warnpoint('Overlapped wires at %s', True)
                    continue

                num_pins = len(pins)
                num_ends = len(wires) + num_pins
                num_ends += len([obj for obj in wires if not obj.isendpoint(*point)])

                if labels:
                    if len(labels) > 1:
                        warnpoint('Overlapping labels at %s', True)
                    elif not wires and not pins:
                        label, = labels
                        if not isinstance(label, (label.GLabel, label.HLabel)):
                            labels[0].warn('Dangling label')
                    continue

                if len(pins) == 1 and not wires and not labels:
                    pin, = pins
                    if not pin.invisible:
                        pin.warn('Unconnected pin')
                        single_pin = True
                    continue
                if conn:
                    if len(conn) > 1:
                        warnpoint('Multiple (overlapping) connection dots')
                    if num_ends < 2:
                        warnpoint('Unnecessary connection dot')
                    if num_ends > 3 and num_ends - num_pins > 2:
                        warnpoint('Connection dot used to connect crossed lines')
                elif num_ends != 2:
                    if num_ends > 2:
                        if len(wires) > 2 or pins or labels:
                            warnpoint('Connection dot not used')
                    elif not labels:
                        danglies.append((point, obj))

        is_bus = 'Bus Line' in foundtypes

        if not is_bus:
            for point, wire in danglies:
                # Be a little lenient -- don't report danglies
                # if there is a nearby label.
                points = sorted(wire.points)
                if point == points[0]:
                    otherpoint = points[1]
                else:
                    assert point == points[-1]
                    otherpoint = points[-2]
                objs = [x for x in (pointdict[otherpoint] - set([wire])) if isinstance(x, (self.Wire, self.Label))]
                if len(objs) == 1:
                    obj, = objs
                    if isinstance(obj, self.Label):
                        continue
                warnpoint('Dangling wire end')

        self.killpoints()

        if mynet:
            sizes = sorted(((len(x.net_ids), x) for x in mynet))
            is_bus = is_bus or sizes[0][0] > 1
            func = (self.instantiate_single, self.instantiate_bus)[is_bus]
            func(mynet, single_pin, min(netpoints), sizes)

    def findpartialnets(self):
        for classtype in (self.Wire, self.Label, self.GLabel, self.HLabel,
                          self.Pin, self.Connection, self.SLabel):
            objset = self.byclass.get(classtype, [])
            while objset:
                # Pick a starting object in the set at random
                self.makepartial(iter(objset).next())
