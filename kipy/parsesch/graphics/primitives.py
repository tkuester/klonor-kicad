'''
Reasonably generic items that can appear on a schematic page.
'''
class Rectangle(object):

    @property
    def full_info(self):
        coordinates = (self.startx, self.starty), (self.endx, self.endy)
        if coordinates[0] == coordinates[1]:
            coordinates = coordinates[0]
        pagename = self.page.pagename
        return '%s on page %s at %s' % (self.userinfo, pagename, coordinates)

    def warn(self, s):
        self.page.warnings.append(
            'Warning:  %s\n        %s\n' % (s, self.full_info) )

    def install(self, page, x1, y1, x2=None, y2=None):
        assert (x2 is None) == (y2 is None)
        if x2 is None:
            x2 = x1
            y2 = y1

        if isinstance(self, Line):
            page.pointdict[x1, y1].add(self)
            page.pointdict[x2, y2].add(self)

        sortkey = min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2), self

        self.startx = x1
        self.starty = y1
        self.endx = x2
        self.endy = y2
        self.userinfo = self.__class__.__name__
        self.page = page
        self.points = set()    # Points where this connects with other objects

        if isinstance(self, Line) and x1 != x2 and y1 != y2:
            self.warn('Diagonal lines not supported for intersection check\n' +
                      '             -- only ends checked for connectivity')
            page.diags.add(self)
        else:
            page.graphic_items.append(sortkey)

    def removepoint(self, point):
        points = self.points
        points.remove(point)
        if not points:
            self.page.byclass[self.__class__].remove(self)
        pointdict = self.page.pointdict
        points = pointdict[point]
        points.remove(self)
        if not points:
            del pointdict[point]

    def __init__(self, *args):
        self.install(*args)

    def checkdiag(self):
        diag = isinstance(self, Line) and self.startx != self.endx and self.starty != self.endy
        assert not diag, "No support for diagonals"

    def overlap(self, other):
        def numberline_intersection(o1x1, o1x2, o2x1, o2x2):
            return ( max(min(o1x1, o1x2), min(o2x1, o2x2)),
                     min(max(o1x1, o1x2), max(o2x1, o2x2))  )

        x1, x2 = numberline_intersection(self.startx, self.endx, other.startx, other.endx)
        y1, y2 = numberline_intersection(self.starty, self.endy, other.starty, other.endy)
        if x1 > x2 or y1 > y2:
            return None
        self.checkdiag(), other.checkdiag()
        return x1, y1, x2, y2

    def hidden_by(self, other, min_nonoverlap=50):
        def numberline_nonintersection(o1x1, o1x2, o2x1, o2x2):
            left = min(o2x1, o2x2) - min(o1x1, o1x2)
            right = max(o1x1, o1x2) - max(o2x1, o2x2)
            return max(left, right, 0)

        x = numberline_nonintersection(self.startx, self.endx, other.startx, other.endx)
        y = numberline_nonintersection(self.starty, self.endy, other.starty, other.endy)
        return x < min_nonoverlap and y < min_nonoverlap

    def colinear(self, other):
        return ( self.startx == self.endx == other.startx == other.starty or
                 self.starty == self.endy == other.starty == other.starty )

class Line(Rectangle):
    ''' Yes, Virginia, a line is just a really, really, narrow rectangle
    '''

    def isendpoint(self, x, y):
        return (x == self.startx and y == self.starty) or \
                (x == self.endx and y == self.endy)

class Point(Line):
    ''' and, of course, a point is a really short line
    '''
