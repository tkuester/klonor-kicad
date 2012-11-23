'''
KICAD library drawing objects


Possible attributes of LibDraw subclasses:

subpart -- aka "unit"  0 to draw on all units in package,
           otherwise unit-specific drawing

variant -- 0 for all variants, else draw only one variant.
           Variants are different representations, like
           de Morgan representations of gates

ltype -- Line type (thickness)  -- 0 for normal
fill  -- N, F, or f for no fill, fill, transparent fill

startx starty endx endy -- beginning/end of rectangle or arc
starta enda  -- starting/ending angle of rectangle in fixed-point 0.1 degrees
posx posy -- pin location or circle center or field location
radius -- circle or arc radius
name -- pin name or field text
num -- pin number or field number
length -- pin length
orientation -- direction to draw line for pin length -- L, D, U, R,
               or text orientation -- H or V
num_size -- Text size of pin number
name_size -- Text size of pin name

etype = Elec. Type of pin (I=Input, O=Output, B=Bidi, T=tristate,
          P=Passive, U=Unspecified, W=Power In, w=Power Out,
          C=Open Collector, E=Open Emitter)

ptype= Type of pin (N=No Draw, I=Invert (hollow circle),
          C=Clock, L=Low In (IEEE), V=Low Out (IEEE))

visible = V or I
hjust = horizontal justification L R C 
vjust = vertical justification T B C

'''

from math import sin, cos, pi
from kipy.utility import MetaHelper, getint

class LibDraw(object):
    InsideDraw = True  # False only for TextField

    __metaclass__ = MetaHelper

    _by_keyword = {}

    @staticmethod
    def _fixtokens(tokens, getint=getint):
        return [getint(x) for x in tokens]

    @classmethod
    def _classinit(cls, base):
        ''' Put subclasses for all the file types into our
            dispatch directory, and save information about
            the class members from the doc string.
        '''
        if base is None:
            return
        docstr = cls.__doc__
        varlist = docstr.split()
        prefix = varlist.pop(0)
        if cls.InsideDraw:
           assert LibDraw._by_keyword.setdefault(prefix, cls) is cls
        setattr(base, cls.__name__, cls)
        defaults = cls._fixtokens(cls.default.split())
        defaults += (len(varlist) - len(defaults)) * ['']
        cls._memberlist = varlist
        cls._memberset = set(varlist)
        cls._defaults = defaults
        cls._prefix = prefix

    def __init__(self, tokens=(), line='', already_fixed=False, **kw):
        if not already_fixed:
            tokens = self._fixtokens(tokens)
        tokens += self._defaults[len(tokens):]
        members = self._memberlist
        assert len(tokens) == len(members), (self.__class__.__name__, members, tokens)
        for name, value in zip(members, tokens):
            setattr(self, name, value)
        for name, value in kw.iteritems():
            assert name in self._memberset, (name, value)
            setattr(self, name, value)

    def _getprefix(self):
        return self._prefix + ' '

    def __str__(self):
        members = self._memberlist
        values = [str(getattr(self, x)) for x in members]
        return ('%s%s' % (self._getprefix(), ' '.join(values))).rstrip()

    @classmethod
    def parse(cls, lineiterator, firstline=''):
        firstline = firstline or lineiterator.next()
        assert firstline.strip() == 'DRAW', firstline
        subclassdict=cls._by_keyword.get
        result = []
        for line in lineiterator:
            tokens = line.split()
            keyword = tokens.pop(0)
            subclass = subclassdict(keyword)
            if subclass is None:
                assert keyword == 'ENDDRAW', keyword
                return result
            result.append(subclass(tokens, line))

    @staticmethod
    def render(items, result=None):
        if result is None:
            result = []
        result.append('DRAW')
        result.extend((str(x) for x in items))
        result.append('ENDDRAW')
        return result
 
class Rectangle(LibDraw):
    'S startx starty endx endy subpart variant ltype fill'
    default = '0 0 0 0 0 0 0'
    optional_default = 'N'
    def boundary(self, xlist, ylist):
        xlist.append(self.startx)
        xlist.append(self.endx)
        ylist.append(self.starty)
        ylist.append(self.endy)

class Circle(LibDraw):
    'C posx posy radius subpart variant ltype fill'
    default = '0 0 0 0 0 0 N'
    def boundary(self, xlist, ylist):
        xlist.append(self.posx + self.radius)
        xlist.append(self.posx - self.radius)
        ylist.append(self.posy + self.radius)
        ylist.append(self.posy - self.radius)

class Arc(LibDraw):
    'A posx posy radius starta enda subpart variant ltype fill startx starty endx endy'
    default = '0 0 0 0 0 0 0 0'
    optional_default = 'N 0 0 0 0'

    def boundary(self, xlist, ylist):
        posx, posy, radius = self.posx, self.posy, self.radius
        starta = self.starta % 3600
        enda = self.enda % 3600
        enda += 3600 * (enda < starta)
        if starta <  900 < enda: ylist.append(posy + radius)
        if starta < 1800 < enda: xlist.append(posx - radius)
        if starta < 2700 < enda: ylist.append(posy - radius)
        if starta < 3600 < enda: xlist.append(posx + radius)

        # Not all library components have these locations,
        # so for simplicity we always calculate them
        startx = posx + int(round(radius * cos(starta * pi / 1800)))
        starty = posy + int(round(radius * sin(starta * pi / 1800)))
        endx = posx + int(round(radius * cos(enda * pi / 1800)))
        endy = posy + int(round(radius * sin(enda * pi / 1800)))
        xlist.append(startx)
        xlist.append(endx)
        ylist.append(starty)
        ylist.append(endy)

class Pin(LibDraw):
    'X name num posx posy length orientation num_size name_size subpart variant etype ptype'
    default = 'none 0 0 0 300 R 50 50 0 0 U'
    def boundary(self, xlist, ylist):
        pass  # Don't consider the pins to be inside the boundary

class PointList(list):
    def __str__(self):
        result = [str(x) for x in self]
        result[::2] = [' ' + x for x in result[::2]]
        return ' '.join(result)

class Polyline(LibDraw):
    # P Nb subpart variant ltype x0 y0 x1 y1 xi yi fill
    #     Nb = a number of points.
    'P subpart variant ltype points fill'
    default = '0 0 0 0'
    optional_default = 'N'

    def _setpoints(self, value):
        self._points = PointList(value or [])
    def _getpoints(self):
        return self._points
    points = property(_getpoints, _setpoints)

    def __init__(self, tokens=(), line='', **kw):
        tokens = self._fixtokens(tokens)
        if tokens:
            numpoints = tokens.pop(0) * 2
            nonpoints = len(tokens) - numpoints
            assert nonpoints in (3,4), (numpoints / 2, tokens)
            tokens[3:3+numpoints] = [tokens[3:3+numpoints]]
        LibDraw.__init__(self, tokens, line, True, **kw)

    def _getprefix(self):
        pointlen = len(self._points)
        assert not pointlen & 1, pointlen
        return '%s %d ' % (self._prefix, pointlen / 2)

    def boundary(self, xlist, ylist):
        xlist.extend(self.points[0::2])
        ylist.extend(self.points[1::2])

class Text(LibDraw):
    'T orientation posx posy size texttype subpart variant text'
    default = '0 0 0 100 0 0 1 <none>'
    MaybeOpaque = False

    @staticmethod
    def reconstitute(tokens, line):
        easy = ' '.join(tokens)
        if line.endswith(easy):
            return easy
        endindex = len(line)
        for token in reversed(tokens):
            endindex = line.rindex(token, 0, endindex)
        return line[endindex:]

    def __init__(self, tokens=(), line='', **kw):
        newtokens = self._fixtokens(tokens[:7])
        newtokens.append(self.reconstitute(tokens[7:], line))
        LibDraw.__init__(self, newtokens, line, True, **kw)

    def boundary(self, xlist, ylist):
        pass  # Don't consider the text to be inside the boundary for now

class TextField(LibDraw):
    'F num value posx posy size orientation visible hjust vjust fieldname'
    InsideDraw = False # render before drawing object
    default = '0 none 0 0 60 H V'
    optional_default = 'C C'
    def _getprefix(self):
        return self._prefix

    def __init__(self, tokens=(), line='', **kw):
        if tokens[1].count('"') & 1:
            parta, partb, partc = line[1:].split('"', 2)
            tokens = parta.split()
            tokens.append(partb)
            tokens.extend(partc.split())
        LibDraw.__init__(self, tokens, line, **kw)
