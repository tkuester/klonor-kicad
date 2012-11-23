'''
Classes based on SchItem for parsing and rendering $Sheet sub-sheets
inside a .sch file.
'''
from .schitem import SchItem

class Sheet(SchItem):
    keyword = '$Sheet'
    _by_keyword = {}

    def render(self, linelist):
        linelist.append(self.keyword)
        self.S.render(self, linelist)
        self.U.render(self, linelist)
        for i, f in enumerate(self.fields):
            f.render(i, linelist)
        self.EndSheet.render(self, linelist)

class S(Sheet):
    @classmethod
    def subparse(cls, sheet, tokens, lineiterator):
        cls.checkstate(sheet, -1, 2)
        sheet.startx, sheet.starty, sheet.endx, sheet.endy = tokens[1:]
        sheet.endx += sheet.startx
        sheet.endy += sheet.starty
    @staticmethod
    def render(sheet, linelist):
        linelist.append('S %-4s %-4s %-4s %-4s' % (sheet.startx, sheet.starty,
              sheet.endx - sheet.startx, sheet.endy - sheet.starty))


class U(Sheet):
    @classmethod
    def subparse(cls, sheet, tokens, lineiterator):
        cls.checkstate(sheet, 2, 1)
        assert not hasattr(sheet, 'timestamp')
        sheet.timestamp, = tokens[1:]
        sheet.fields = []
    @staticmethod
    def render(sheet, linelist):
        if sheet.timestamp is not None:
            linelist.append('U %s' % (sheet.timestamp))

class F(Sheet):
    keyword = None
    @classmethod
    def subparse(cls, sheet, tokens, lineiterator):
        if sheet.parsestate == 2:
            sheet.parsestate = 1
            sheet.timestamp = None
            sheet.fields = []
        cls.checkstate(sheet, 1, 1)
        cls(sheet, tokens)

    def __init__(self, sheet, tokens):
        index = tokens[0]
        assert index[0] == 'F'
        index = int(index[1:])
        assert index == len(sheet.fields)
        sheet.fields.append(self)
        if index < 2:
            self.name, self.size = tokens[1:]
        else:
            self.name, self.form, self.side, self.posx, self.posy,  self.size = tokens[1:]

    def render(self, index, linelist):
        tokens = ['F%d "%s"' % (index, self.name)]
        if index >= 2:
            tokens.extend((self.form, self.side, self.posx, self.posy, self.size, ''))
        else:
            tokens.append(self.size)
        linelist.append(' '.join((str(x) for x in tokens)))

class EndSheet(Sheet):
    keyword = '$EndSheet'
    @classmethod
    def subparse(cls, sheet, tokens, lineiterator):
        cls.checkstate(sheet, 1, 0)
        assert len(sheet.fields) >= 2
    @classmethod
    def render(cls, schpage, linelist):
        linelist.append(cls.keyword)
