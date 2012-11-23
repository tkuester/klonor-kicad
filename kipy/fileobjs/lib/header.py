'''
KICAD library objects
'''
import time
from .component import LibComponent

class LibFile(list):
    def __new__(cls, *args):
        return list.__new__(cls)

    def __init__(self, sourcef=None):
        self.topline = None
        self.date = None
        self.version = '2.3'
        if sourcef is not None:
            self._fromsource(sourcef)

    def _fromsource(self, sourcef):
        sourcelines = iter(sourcef.readlines())
        for line in sourcelines:
            if not line.strip().startswith('#'):
                break
        self.topline = line
        header = line.split('Date:', 1)
        if len(header) == 2:
            self.date = header[1]
        header = header[0].split()
        assert (
            header[0].upper().startswith('EESCHEMA-LIB') and
            header[1] == 'Version'), (sourcef, line)
        self.version = header[2]
        for line in sourcelines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            assert line.startswith('DEF '), line
            comp = LibComponent(lineiterator=sourcelines, firstline=line)
            self.append(comp)

    def __str__(self):
        line = self.topline
        if line is None:
            d = self.date
            if d is None:
                d = time.localtime()
                d = d.tm_mday, d.tm_mon, d.tm_year,d.tm_hour, d.tm_min, d.tm_sec
                d = '%02d/%02d/%04d-%02d-%02d:%02d' % d
            line = 'EESchema-LIBRARY Version %s  Date: %s' % (self.version, d)
        result = [line]
        for item in self:
            result.append(str(item))
        result.append('#\n#End Library\n')
        return '\n'.join(result)
