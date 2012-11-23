from partialnets import PartialNet

class NonNets(object):
    '''  This is a mix-in class for ParsePage.
         It will not work standalone.
         It contains all the logic for removing non-net items
         from the point dictionary.
    '''

    def check_in_printable_area(self, margin=400):
        pointdict = self.pointdict
        if not pointdict:
            return
        x = [loc[0] for loc in pointdict]
        y = [loc[1] for loc in pointdict]
        minx, maxx = margin, self.maxx - margin
        miny, maxy = margin, self.maxy - margin
        xok = minx <= min(x) <= max(x) <= maxx
        yok = miny <= min(y) <= max(y) <= maxy
        if xok and yok:
            return
        baditems = set()
        for coords, items in pointdict.iteritems():
            # We don't check rectangular items, but that's OK
            # because all the pins have to be single points
            xok = minx <= coords[0] <= maxx
            yok = miny <= coords[1] <= maxy
            if not xok or not yok:
                baditems.update(items)

        pins = set((x for x in baditems if isinstance(x, self.Pin)))
        for x in pins:
            baditems.add(x.component)
        baditems -= pins
        self.warn('Some items not in page visible area:\n          ' +
                  '\n          '.join(sorted((x.userinfo for x in baditems))))

    def check_keepouts(self):
        objclass = (self.Keepout, self.Component, self.Sheet, self.Entry)
        pointdict = self.pointdict
        kill = self.kill
        check4 = set()
        check2 = set()
        for obj in self.getbyclass(*objclass):
            for point in obj.points:
                if len(point) > 2:
                    check4.add(point)
                    continue
                for other in pointdict[point]:
                    if isinstance(other, self.PinOrLabel):
                        kill.add((obj, point))
                        break
                else:
                    check2.add(point)

        keep = set()

        for point in check4:
            allobjs = pointdict[point]
            kill.update(((obj, point) for obj in allobjs))
            wires = set((obj for obj in allobjs if isinstance(obj, self.Wire)))
            nonwires = allobjs - wires
            # If we killed an overlap between a component
            # and a pin, go ahead and kill the one on the
            # wire leading to the pin
            if wires:
                if len(wires) > 1:
                    keep.update(((obj, point) for obj in wires))
                else:
                    wire, = wires
                    for part in nonwires:
                        # If the wire goes to that pin, we're OK
                        if (part, point[:2]) in kill or (part, point[2:]) in kill:
                            continue
                        # Keep the overlap unless it is a very small part
                        if not isinstance(part, self.Component) or len(part.pindict) > 1:
                            keep.add((wire, point))
                            keep.add((wire, point))
            if len(nonwires) > 1:
                for obj1 in nonwires:
                    for obj2 in nonwires:
                        if obj1 is not obj2 and obj1.hidden_by(obj2):
                            keep.add((obj1, point))
                            keep.add((obj2, point))

        kill -= keep
        self.killpoints()

        keep = set()
        for point in check2:
            keepouts = pointdict[point]
            others = set((obj for obj in keepouts if not isinstance(obj, objclass)))
            if others:
                continue
            kill.update(((obj, point) for obj in keepouts))
            if len(keepouts) <= 1:
                continue
            for obj1 in keepouts:
                for obj2 in keepouts:
                    if obj1 is not obj2 and obj1.hidden_by(obj2):
                        keep.add((obj1, point))
                        keep.add((obj2, point))

        kill -= keep
        self.killpoints()

        for obj in self.getbyclass(*objclass):
            pointinfo = []
            for point in obj.points:
                others = sorted((x.full_info for x in pointdict[point] if x is not obj))
                pointinfo.append('%s: %s' % (point, ', '.join(others)))
                kill.add((obj, point))
            if obj.userinfo != 'Notes Line':
                pointinfo.sort()
                pointinfo.insert(0,'Objects overlap:\n            %s' % obj.full_info)
                self.warn('\n               '.join(pointinfo))
        self.killpoints()

    def check_noconn(self):
        pointdict = self.pointdict
        kill = self.kill
        myclasses = (self.Pin, self.SLabel)
        for nc in self.getbyclass(self.NoConn):
            point, = nc.points
            kill.add((nc, point))
            objs = set(pointdict[point]) - set([nc])
            ok = len(objs) == 1
            if ok: other, = objs
            ok = ok and isinstance(other, myclasses)
            if not ok:
                self.warn('Ignoring unexpected %s' % nc.full_info)
                continue
            kill.add((other, point))
            for item in other.fracture():
                mynet = PartialNet((other,))
                mynet.single_pin = True
                mynet.point = point
                mynet.pagename = self.pagename
                self.partialnets.append(mynet)
        self.killpoints()

    def uncross_wires(self):
        pointdict = self.pointdict
        kill = self.kill
        for wire in self.getbyclass(self.Wire):
            for point in wire.points:
                others = set(pointdict[point]) - set([wire])
                if len(point) != 2 or len(others) != 1:
                    continue
                other, = others
                if not isinstance(other, self.Wire):
                    continue
                if wire.isendpoint(*point) or other.isendpoint(*point):
                    continue
                kill.add((wire, point))
        self.killpoints()

    def strip_nonnets(self):
        self.check_in_printable_area()
        self.check_keepouts()
        self.check_noconn()
        self.uncross_wires()
