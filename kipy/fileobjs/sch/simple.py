'''
Classes based on SchItem for parsing and rendering simple entities
inside a .sch file.
'''
from .schitem import SchItem

class Text(SchItem):
    tokenlength = 7, 9
    def __init__(self, tokens, lineiterator):
        self.texttype, self.posx, self.posy, self.orientation, self.size = tokens[1:6]
        self.style = tokens[6:]
        self.text = lineiterator.next().linetext

    def render(self, linelist):
        lineinfo = ['Text', self.texttype, '%-4s' % self.posx, '%-4s' % self.posy, '%-4s' % self.orientation, '%-4s' % self.size]
        lineinfo.extend(self.style)
        linelist.append(' '.join((str(x) for x in lineinfo)))
        linelist.append(self.text)


class Wire(SchItem):
    tokenlength = 3, 3
    def __init__(self, tokens, lineiterator):
        self.wiretype = ' '.join(tokens[1:])
        self.startx, self.starty, self.endx, self.endy = lineiterator.next()
    def render(self, linelist):
        linelist.append('Wire %s\n\t%-4s %-4s %-4s %-4s' %
                        (self.wiretype, self.startx, self.starty, self.endx, self.endy))

class Entry(SchItem):
    tokenlength = 3, 3
    def __init__(self, tokens, lineiterator):
        self.wiretype = ' '.join(tokens[1:])
        self.startx, self.starty, self.endx, self.endy = lineiterator.next()
    def render(self, linelist):
        linelist.append('Entry %s\n\t%-4s %-4s %-4s %-4s' %
                        (self.wiretype, self.startx, self.starty, self.endx, self.endy))

class Connection(SchItem):
    tokenlength = 4, 4
    def __init__(self, tokens, lineiterator):
        assert tokens[1] == '~'
        self.posx, self.posy = tokens[2:]
    def render(self, linelist):
        linelist.append('Connection ~ %-4s %-4s' % (self.posx, self.posy))

class NoConn(SchItem):
    tokenlength = 4, 4
    def __init__(self, tokens, lineiterator):
        assert tokens[1] == '~'
        self.posx, self.posy = tokens[2:]
    def render(self, linelist):
        linelist.append('NoConn ~ %-4s %-4s' % (self.posx, self.posy))

class Kmarq(SchItem):
    tokenlength = 1, 100
    def __init__(self, tokens, lineiterator):
        self.text = tokens.linetext
    def render(self, linelist):
        linelist.append(self.text)

