from .brditem import BrdItem
'''
Classes based on BrdItem for parsing and rendering $ZONE and $CZONE_OUTLINE
inside a .brd file.
'''
class Zone(BrdItem):
    keyword = '$ZONE'
    _by_keyword = {}

    def __init__(self, tokens=[], lineiterator=None):
        self.items = []
        super(Zone,self).__init__(tokens, lineiterator)

    def render(self, linelist):
        linelist.append(self.keyword)
        linelist.extend(x.linetext for x in self.items)
        self.EndZone.render(self, linelist)

class EndZone(Zone):
    keyword = '$EndZONE'
    @classmethod
    def subparse(cls, zone, tokens, lineiterator):
        cls.checkstate(zone, -1, 0)

    @classmethod
    def render(cls, zone, linelist):
        linelist.append(cls.keyword)

class CZoneOutline(BrdItem):
    keyword = '$CZONE_OUTLINE'
    _by_keyword = {}

    def __init__(self, tokens=[], lineiterator=None):
        self.items = []
        self.corners = []
        super(CZoneOutline,self).__init__(tokens, lineiterator)

    def render(self, linelist):
        linelist.append(self.keyword)
        linelist.extend(x.linetext for x in self.items)
        self.EndCZoneOutline.render(self, linelist)

class CZoneInner(CZoneOutline): 
    @classmethod
    def subparse(cls, zone, tokens, lineiterator):
        cls.checkstate(zone, -1, -1)
        zone.items.append(tokens)

class ZInfo(CZoneInner): pass
class ZLayer(CZoneInner): 
    @classmethod
    def subparse(cls, zone, tokens, lineiterator):
        zone.items.append(tokens)
        zone.layer = tokens[1]

class ZAux(CZoneInner): pass
class ZClearance(CZoneInner): pass
class ZMinThickness(CZoneInner): pass
class ZOptions(CZoneInner): pass
class ZSmoothing(CZoneInner): pass
class ZCorner(CZoneInner): pass

class EndCZoneOutline(CZoneOutline):
    keyword = '$EndCZONE_OUTLINE'
    @classmethod
    def subparse(cls, czone, tokens, lineiterator):
        cls.checkstate(czone, -1, 0)

    @classmethod
    def render(cls, zone, linelist):
        linelist.append(cls.keyword)

class PolysCorners(CZoneOutline):
    tokenlength = 1, 1
    keyword = '$POLYSCORNERS'

    @classmethod
    def subparse(cls, czone, tokens, lineiterator):
        cls.checkstate(czone, -1, -1)
        text = [tokens]
        for tokens in lineiterator:
            text.append(tokens)
            if tokens[0] == '$endPOLYSCORNERS':
                break
            czone.corners.append([float(x) for x in tokens[0:2]])
        czone.items.extend(text)

