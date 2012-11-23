from .schitem import SchItem
'''
Classes based on SchItem for parsing and rendering $Comp components
inside a .sch file.
'''
class Component(SchItem):
    keyword = '$Comp'
    _by_keyword = {}

    def render(self, linelist):
        linelist.append(self.keyword)
        self.L.render(self, linelist)
        self.U.render(self, linelist)
        self.P.render(self, linelist)
        for ar in self.altref:
            self.AR.render(ar, linelist)
        for i, f in enumerate(self.fields):
            self.F.render(i, f, linelist)
        self.num.render(self, linelist)
        self.EndComp.render(self, linelist)
        
class L(Component):
    @classmethod
    def subparse(cls, comp, tokens, lineiterator):
        cls.checkstate(comp, -1, 7)
        comp.parttype, comp.refdes = tokens[1:]

    @staticmethod
    def render(comp, linelist):
        linelist.append('L %s %s' % (comp.parttype, comp.refdes))

class U(Component):
    @classmethod
    def subparse(cls, comp, tokens, lineiterator):
        cls.checkstate(comp, 7, 6)
        comp.subpart, comp.variant, comp.timestamp = tokens[1:]

    @staticmethod
    def render(comp, linelist):
        timestamp = comp.timestamp or '00000000'
        linelist.append('U %s %s %s' % (comp.subpart, comp.variant, timestamp))

class P(Component):
    @classmethod
    def subparse(cls, comp, tokens, lineiterator):
        cls.checkstate(comp, 6, 5)
        comp.posx, comp.posy = tokens[1:]
        comp.altref = []
        comp.fields = []

    @staticmethod
    def render(comp, linelist):
        linelist.append('P %s %s' % (comp.posx, comp.posy))

class AR(Component):
    @classmethod
    def subparse(cls, comp, tokens, lineiterator):
        cls.checkstate(comp, 5, 5)
        assert (len(tokens) == 7 and
                tokens[1] == 'Path=' and
                tokens[3] == 'Ref=' and
                tokens[5]=='Part=')
        path, ref, part = tokens[2], tokens[4], int(tokens[6])
        comp.altref.append((path, ref, part))

    @staticmethod
    def render(ar, linelist):
        linelist.append('AR Path="%s" Ref="%s"  Part="%s" ' % ar)

class F(Component):
    @classmethod
    def subparse(cls, comp, tokens, lineiterator):
        if comp.parsestate in (3, 5):
            comp.parsestate = 4
        cls.checkstate(comp, 4, 3)
        comp.fields.extend((None,) * (tokens[1] - len(comp.fields)))
        assert tokens[1] == len(comp.fields), (tokens[1], len(comp.fields))
        comp.fields.append(tokens[2:])
    @staticmethod
    def render(i, f, linelist):
        # F 0 "R7" H 2050 7350 60  0000 C CNN
        if f is not None:
            data = (i,) + tuple(f)
            fmt = 'F %d "%s" %s %-3d %-3d %-3d %04d %s %s'
            if len(data) > 9:
                fmt += ' "%s"'
            try:
                linelist.append(fmt % data)
            except:
                for line in linelist[-40:]:
                    print line
                print fmt, data
                raise

class num(Component):
    keyword = None
    @classmethod
    def subparse(cls, comp, tokens, lineiterator):
        if comp.parsestate == 3:
            cls.checkstate(comp, 3, 2)
            assert isinstance(tokens[0], int) and len(tokens) == 3, tokens
            comp.redundant_num = tokens.linetext
            comp.unit = tokens[0]
        else:
            cls.checkstate(comp, 2, 1)
            assert len(tokens) == 4 and min(tokens) >= -1 and max(tokens) <= 1, tokens
            comp.transform = tuple(tokens)
    @staticmethod
    def render(comp, linelist):
        linelist.append('\t%s %s %s' % (comp.unit, comp.posx, comp.posy))
        linelist.append('\t%-4s %-4s %-4s %-4s' % comp.transform)

class EndComp(Component):
    keyword = '$EndComp'
    @classmethod
    def subparse(cls, comp, tokens, lineiterator):
        cls.checkstate(comp, 1, 0)
        assert len(comp.fields) >= 2
    @classmethod
    def render(cls, comp, linelist):
        linelist.append(cls.keyword)
