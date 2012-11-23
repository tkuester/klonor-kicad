from .brditem import BrdItem
'''
Classes based on BrdItem for parsing and rendering $NCLASS
inside a .brd file.
'''
class NetClass(BrdItem):
    keyword = '$NCLASS'
    _by_keyword = {}

    def render(self, linelist):
        linelist.append(self.keyword)
        self.Name.render(self, linelist)
        self.Desc.render(self, linelist)
        self.NetClassNum.Clearance.render(self, linelist)
        self.NetClassNum.TrackWidth.render(self, linelist)
        self.NetClassNum.ViaDia.render(self, linelist)
        self.NetClassNum.ViaDrill.render(self, linelist)
        self.NetClassNum.uViaDia.render(self, linelist)
        self.NetClassNum.uViaDrill.render(self, linelist)
        linelist.extend('AddNet "%s"' % x for x in self.addnet)
        self.EndNClass.render(linelist)

class Name(NetClass):
    @classmethod
    def subparse(cls, nclass, tokens, lineiterator):
        cls.checkstate(nclass, -1, 1)
        nclass.name = ' '.join(tokens[1:])
        nclass.addnet = []

    @staticmethod
    def render(nclass, linelist):
        linelist.append('Name "%s"' % nclass.name) 

class Desc(NetClass):
    @classmethod
    def subparse(cls, nclass, tokens, lineiterator):
        nclass.desc = ' '.join(tokens[1:])

    @staticmethod
    def render(nclass, linelist):
        linelist.append('Desc "%s"' % nclass.desc) 

class NetClassNum(NetClass):
    @classmethod
    def render(cls, nclass, linelist):
        linelist.append('%s %s' % (cls.__name__, nclass.__dict__[cls.__name__.lower()]))


class Clearance(NetClassNum):
    @classmethod
    def subparse(cls, nclass, tokens, lineiterator):
        nclass.clearance = tokens[1]

class TrackWidth(NetClassNum):
    @classmethod
    def subparse(cls, nclass, tokens, lineiterator):
        nclass.trackwidth = tokens[1]

class ViaDia(NetClassNum):
    @classmethod
    def subparse(cls, nclass, tokens, lineiterator):
        nclass.viadia = tokens[1]

class ViaDrill(NetClassNum):
    @classmethod
    def subparse(cls, nclass, tokens, lineiterator):
        nclass.viadrill = tokens[1]

class uViaDia(NetClassNum):
    @classmethod
    def subparse(cls, nclass, tokens, lineiterator):
        nclass.uviadia = tokens[1]

class uViaDrill(NetClassNum):
    @classmethod
    def subparse(cls, nclass, tokens, lineiterator):
        nclass.uviadrill = tokens[1]

class AddNet(NetClass):
    @classmethod
    def subparse(cls, nclass, tokens, lineiterator):
        nclass.addnet.append(tokens[1])

class EndNClass(NetClass):
    keyword = '$EndNCLASS'
    @classmethod
    def subparse(cls, comp, tokens, lineiterator):
        cls.checkstate(comp, 1, 0)

    @classmethod
    def render(cls, linelist):
        linelist.append(cls.keyword)

