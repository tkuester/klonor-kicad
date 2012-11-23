from .brditem import BrdItem
'''
Classes based on BrdItem for parsing and rendering $TRACK
inside a .brd file.
'''

class TrackPo(object):
    def __init__(self, tokens):
        self.shape = tokens[0]
        self.xstart, self.ystart = [float(x) for x in tokens[1:3]]
        self.xend, self.yend = [float(x) for x in tokens[3:5]]
        self.width = float(tokens[5])
        self.unknown = tokens[6]

    def clone(self):
        return TrackPo([self.shape, self.xstart, self.ystart,
            self.xend, self.yend, self.width, self.unknown])

    def __str__(self):
        return 'Po %s %s %s %s %s %s %s' % (self.shape, self.xstart, 
            self.ystart, self.xend, self.yend,
            self.width, self.unknown)

class TrackDe(object):
    def __init__(self, tokens):
        self.text = tokens.linetext
        self.tokens = tokens

    def clone(self):
        return TrackDe(self.tokens)

    def __str__(self):
        return self.text

class Track(BrdItem):
    keyword = '$TRACK'
    _by_keyword = {}

    def __init__(self, tokens=[], lineiterator=None):
        self.po = []
        self.de = []
        super(Track,self).__init__(tokens, lineiterator)

    def render(self, linelist):
        linelist.append('$TRACK')
        for pode in zip(self.po, self.de):
            linelist.append(str(pode[0]))
            linelist.append(str(pode[1]))
        self.EndTrack.render(self, linelist)

class EndTrack(Track):
    keyword = '$EndTRACK'
    @classmethod
    def subparse(cls, track, tokens, lineiterator):
        cls.checkstate(track, -1, 0)

    @classmethod
    def render(cls, track, linelist):
        linelist.append(cls.keyword)


class Po(Track):
    @classmethod
    def subparse(cls, track, tokens, lineiterator):
        track.po.append(TrackPo(tokens[1:]))

class De(Track):
    @classmethod
    def subparse(cls, track, tokens, lineiterator):
        track.de.append(TrackDe(tokens))

