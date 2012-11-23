'''
Classes based on SchItem for parsing and rendering
top of .sch file.
'''
from .schitem import SchItem

# Having this class here is a quick hack to make the parsing
# work again after it was broken by allowing mutiple LIBS: lines

class LibInfo(object):
    @classmethod
    def subparse(cls, schpage, tokens, lineiterator):
        linetext = tokens.linetext
        if not linetext.startswith('LIBS:'):
            print "Ignoring Unknown %s" % repr(linetext)
            return
        schpage.lib_info.append(linetext)

    @staticmethod
    def render(schpage, linelist):
        linelist.extend(schpage.lib_info)

class SchFile(SchItem):
    _classinit = None
    default_parse_class = LibInfo

    def __init__(self, sourcefile=None):
        self.lib_info = []
        if sourcefile != None:
            self.sourcefile = sourcefile
            self.startparse(self, sourcefile.readlinetokens())


    def render(self, linelist):
        self.EESchema.render(self, linelist)
        LibInfo.render(self, linelist)
        self.EELAYER.render(self, linelist)
        self.Descr.render(self, linelist)
        for item in self.items:
            item.render(linelist)
        self.EndSCHEMATC.render(self, linelist)

    def __str__(self):
        result = []
        self.render(result)
        result.append('')
        return '\n'.join(result)
