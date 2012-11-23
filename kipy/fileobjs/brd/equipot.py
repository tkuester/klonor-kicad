from .brditem import BrdItem
'''
Classes based on BrdItem for parsing and rendering $EQUIPOT 
inside a .brd file.
'''
class Equipot(BrdItem):
    keyword = '$EQUIPOT'
    _by_keyword = {}

    def render(self, linelist):
        linelist.append(self.keyword)
        self.Na.render(self, linelist)
        self.St.render(self, linelist)
        self.EndEquipot.render(self, linelist)
        
class Na(Equipot):
    @classmethod
    def subparse(cls, equipot, tokens, lineiterator):
        cls.checkstate(equipot, -1, 2)
        equipot.netnumber, equipot.netname = tokens[1:]

    @staticmethod
    def render(equipot, linelist):
        linelist.append('Na %s %s' % (equipot.netnumber, equipot.netname))

class St(Equipot):
    @classmethod
    def subparse(cls, equipot, tokens, lineiterator):
        cls.checkstate(equipot, 2, 1)

    @staticmethod
    def render(equipot, linelist):
        linelist.append('St ~')

class EndEquipot(Equipot):
    keyword = '$EndEQUIPOT'
    @classmethod
    def subparse(cls, equipot, tokens, lineiterator):
        cls.checkstate(equipot, 1, 0)

    @classmethod
    def render(cls, equipot, linelist):
        linelist.append(cls.keyword)
