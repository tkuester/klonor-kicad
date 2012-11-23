from .schitem import SchItem
'''
Classes based on SchItem for parsing and rendering header and
trailer of .sch file.

NOTE:  Header parsing is not complete, for the simple reason I
haven't really needed it yet.  I just extract the minimum
necessary  (all the information is stored as lines, just
not parsed further).
'''

class EESchema(SchItem):
    @classmethod
    def subparse(cls, schpage, tokens, lineiterator):
        cls.checkstate(schpage, -1, 3)
        schpage.page_header = tokens

    @staticmethod
    def render(schpage, linelist):
        linelist.append(schpage.page_header.linetext)

class EELAYER(SchItem):
    @classmethod
    def subparse(cls, schpage, tokens, lineiterator):
        cls.checkstate(schpage, 3, 2)
        schpage.eelayer = [tokens]
        for tokens in lineiterator:
            schpage.eelayer.append(tokens)
            if tokens == ['EELAYER', 'END']:
                break

    @staticmethod
    def render(schpage, linelist):
        linelist.extend(x.linetext for x in schpage.eelayer)

class Descr(SchItem):
    keyword = '$Descr'
    @classmethod
    def subparse(cls, schpage, tokens, lineiterator):
        cls.checkstate(schpage, 2, 1)
        schpage.dimx, schpage.dimy = tokens[2:4]
        schpage.descr = [tokens]
        for tokens in lineiterator:
            schpage.descr.append(tokens)
            if tokens[0] == '$EndDescr':
                break
        schpage.items = []

    @staticmethod
    def render(schpage, linelist):
        linelist.extend(x.linetext for x in schpage.descr)

class EndSCHEMATC(SchItem):
    keyword = '$EndSCHEMATC'
    @classmethod
    def subparse(cls, schpage, tokens, lineiterator):
        cls.checkstate(schpage, 1, 0)

    @classmethod
    def render(cls, schpage, linelist):
        linelist.append(cls.keyword)

