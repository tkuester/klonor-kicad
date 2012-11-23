from .brditem import BrdItem
'''
Classes based on BrdItem for parsing and rendering $MODULE
inside a .brd file.
'''
class Module(BrdItem):
    keyword = '$MODULE'
    tokenlength = 2, 2
    _by_keyword = {}

    def __init__(self, tokens=[], lineiterator=None):
        self.items = []
        self.pads = []
        self.ds = []
        self.dc = []
        self.da = []
        self.name = tokens[1]
        super(Module,self).__init__(tokens, lineiterator)

    def translate(self, dx, dy):
        self.xpos = self.xpos + dx
        self.ypos = self.ypos + dy

    def detachpads(self, netadd, netsuffix):
        for pad in self.pads:
            net = pad['Ne']
            netnumber = net[0]
            netname = net[1]
            net[0] = netnumber + netadd
            net[1] = netname + netsuffix
            pad['Ne'] = net

    def render(self, linelist):
        linelist.append('%s %s' % (self.keyword, self.name))
        self.Po.render(self, linelist)
        linelist.append('Li %s' % self.libref)
        if 'cd' in self.__dict__:
            cd = [str(x) for x in self.cd]
            linelist.append('Cd %s' % ' '.join(cd))
        if 'kw' in self.__dict__:
            kw = [str(x) for x in self.kw]
            linelist.append('Kw %s' % ' '.join(kw))
        linelist.append('Sc %s' % self.sc)
        linelist.append('AR %s' % self.ar)
        linelist.append('Op %s %s %s' % tuple(self.op))
        if 'at' in self.__dict__:
            linelist.append('At %s' % self.at)
        self.T0.render(self, linelist)
        if 't1' in self.__dict__:
            t1 = [str(x) for x in self.t1]
            linelist.append('T1 %s %s %s %s %s %s %s %s %s %s "%s"' % tuple(t1))
    
        for dc in self.dc:
            linelist.append('DC %s %s %s %s %s %s' % tuple(dc))
        for ds in self.ds:
            linelist.append('DS %s %s %s %s %s %s' % tuple(ds))
        for da in self.da:
            linelist.append('DA %s %s %s %s %s %s %s' % tuple(da))

        for pad in self.pads:
            self.Pad.render(pad, linelist)

        for item in self.items:
            linelist.append(item)
        self.EndModule.render(self, linelist)

class Po(Module):
    @classmethod
    def subparse(cls, module, tokens, lineiterator):
        cls.checkstate(module, -1, 1)
        module.position = tokens[1:]
        module.xpos, module.ypos, module.orientation= [float(x) for x in tokens[1:4]]
        module.layer = tokens[5]
        module.timestamp1, module.timestamp2 = tokens[5:7]
        module.attrib = tokens[7]

    @staticmethod
    def render(module, linelist):
        linelist.append('Po %s %s %s %s %s %s %s' %
            (module.xpos, module.ypos, module.orientation, module.layer,
             module.timestamp1, module.timestamp2, module.attrib))
    
class Li(Module):
    @classmethod
    def subparse(cls, module, tokens, lineiterator):
        module.libref = tokens[1]

class Cd(Module):
    @classmethod
    def subparse(cls, module, tokens, lineiterator):
        module.cd = tokens[1:]

class Kw(Module):
    @classmethod
    def subparse(cls, module, tokens, lineiterator):
        module.kw = tokens[1:]

class Sc(Module):
    @classmethod
    def subparse(cls, module, tokens, lineiterator):
        module.sc = tokens[1]

class AR(Module):
    @classmethod
    def subparse(cls, module, tokens, lineiterator):
        module.ar = tokens[1]

class Op(Module):
    @classmethod
    def subparse(cls, module, tokens, lineiterator):
        module.op = tokens[1:]

class At(Module):
    @classmethod
    def subparse(cls, module, tokens, lineiterator):
        module.at = tokens[1]

class T0(Module):
    @classmethod
    def subparse(cls, module, tokens, lineiterator):
        module.t0 = tokens[1:-1]
        module.refdes = tokens[-1]

    @staticmethod
    def render(module, linelist):
        linelist.append('T0 %s %s %s %s %s %s %s %s %s %s "%s"'
            % tuple(module.t0 + [module.refdes]))

class T1(Module):
    @classmethod
    def subparse(cls, module, tokens, lineiterator):
        module.t1 = tokens[1:]

class DS(Module):
    @classmethod
    def subparse(cls, module, tokens, lineiterator):
        module.ds.append(tokens[1:])

class DC(Module):
    @classmethod
    def subparse(cls, module, tokens, lineiterator):
        module.dc.append(tokens[1:])

class DA(Module):
    @classmethod
    def subparse(cls, module, tokens, lineiterator):
        module.da.append(tokens[1:])

class Pad(Module):
    tokenlength = 1, 1
    keyword = '$PAD'

    @classmethod
    def subparse(cls, module, tokens, lineiterator):
        pad = {}
        text = [tokens[0]]
        for tokens in lineiterator:
            if tokens[0] == '$EndPAD':
                break
            if tokens[0] == 'Sh':
                text.append('Sh "%s" %s %s %s %s %s %s' % tuple(tokens[1:]))
                pad['Sh'] = tokens[1:]
                pad['orientation'] = tokens[-1]
            elif tokens[0] == 'Ne':
                text.append('Ne %s "%s"' % tuple(tokens[1:]))
                pad['Ne'] = tokens[1:]
            else:
                text.append(' '.join([str(x) for x in tokens]))
                pad[tokens[0]] = tokens[1:]

        module.pads.append(pad)

    @staticmethod
    def render(pad, linelist):
        linelist.append('$PAD')
        for key in pad.keys():
            if key == 'Sh':
                sh = pad['Sh'][:-1]
                sh.append(pad['orientation'])
                linelist.append('Sh "%s" %s %s %s %s %s %s' 
                    % tuple(sh))
            elif key == 'Ne':
                linelist.append('Ne %s "%s"' % tuple(pad[key]))
            elif key in ['Dr','Po','At']:
                txt = ' '.join(str(x) for x in [key] + pad[key])
                linelist.append(txt)
        linelist.append('$EndPAD')

class Shape3D(Module):
    tokenlength = 1, 1
    keyword = '$SHAPE3D'

    @classmethod
    def subparse(cls, module, tokens, lineiterator):
        text = [tokens[0]]
        for tokens in lineiterator:
            text.append(' '.join([str(x) for x in tokens]))
            if tokens[0] == '$EndSHAPE3D':
                break
        module.items.extend(text)

class EndModule(Module):
    keyword = '$EndMODULE'
    @classmethod
    def subparse(cls, comp, tokens, lineiterator):
        cls.checkstate(comp, 1, 0)

    @classmethod
    def render(cls, comp, linelist):
        linelist.append(cls.keyword)

