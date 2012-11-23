from .brditem import BrdItem
'''
Classes based on BrdItem for parsing and rendering header and
trailer of .brd file.
'''

class PCBNEW_BOARD(BrdItem):
    keyword = 'PCBNEW-BOARD'

    @classmethod
    def subparse(cls, brdpage, tokens, lineiterator):
        cls.checkstate(brdpage, -1, 3)
        brdpage.page_header = tokens

    @staticmethod
    def render(schpage, linelist):
        linelist.append(schpage.page_header.linetext)

class GENERAL(BrdItem):
    keyword = '$GENERAL'

    @classmethod
    def subparse(cls, brdpage, tokens, lineiterator):
        cls.checkstate(brdpage, 3, 2)
        brdpage.general = [tokens]
        for tokens in lineiterator:
            brdpage.general.append(tokens)
            if tokens[0] == '$EndGENERAL':
                break

    @staticmethod
    def render(brdpage, linelist):
        linelist.extend(x.linetext for x in brdpage.general)

class SHEETDESCR(BrdItem):
    keyword = '$SHEETDESCR'

    @classmethod
    def subparse(cls, brdpage, tokens, lineiterator):
        cls.checkstate(brdpage, 2, 1)
        brdpage.sheetdescr = [tokens]
        for tokens in lineiterator:
            brdpage.sheetdescr.append(tokens)
            if tokens[0] == '$EndSHEETDESCR':
                break
        brdpage.items = []

    @staticmethod
    def render(brdpage, linelist):
        linelist.extend(x.linetext for x in brdpage.sheetdescr)

class SETUP(BrdItem):
    keyword = '$SETUP'

    @classmethod
    def subparse(cls, brdpage, tokens, lineiterator):
        cls.checkstate(brdpage, 1, 1)
        brdpage.setup = [tokens]
        for tokens in lineiterator:
            brdpage.setup.append(tokens)
            if tokens[0] == '$EndSETUP':
                break

    @staticmethod
    def render(brdpage, linelist):
        linelist.extend(x.linetext for x in brdpage.setup)

class EndBOARD(BrdItem):
    keyword = '$EndBOARD'
    @classmethod
    def subparse(cls, brdpage, tokens, lineiterator):
        cls.checkstate(brdpage, 1, 0)

    @classmethod
    def render(cls, brdpage, linelist):
        linelist.append(cls.keyword)

