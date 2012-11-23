'''
Main class for parsing and rendering .sch files.

Uses a metaclass to force subclasses to insert
themselves in the _by_keyword dictionary.

'''
from kipy.utility import MetaHelper

class SchItem(object):

    __metaclass__ = MetaHelper

    _by_keyword = {}
    tokenlength = 1, 1

    default_parse_class = None

    @classmethod
    def _classinit(cls, base):
        ''' Called at class creation time by metaclass
        '''
        if base is None:
            return
        classname = cls.__name__
        setattr(base, classname, cls)
        if hasattr(base, '_by_keyword'):
            cls.keyword = keyword = cls.__dict__.get('keyword', classname)
            if isinstance(keyword, str):
                keyword = keyword.upper()
                assert base._by_keyword.setdefault(keyword, cls) is cls
            else:
                assert keyword is None
                assert base.default_parse_class is None
                base.default_parse_class = cls

    @classmethod
    def startparse(cls, parseobj, lineiterator, toplevel=True):
        parseobj.parsestate = -1
        subclassdict=cls._by_keyword.get
        default = cls.default_parse_class
        tokens = None
        try:
            for tokens in lineiterator:
                #print parseobj, tokens
                keyword = tokens[0]
                try:
                    keyword = keyword.upper()
                except AttributeError:
                    pass
                subclassdict(keyword, default).subparse(parseobj, tokens, lineiterator)
                if not toplevel and not parseobj.parsestate:
                    break
        except Exception, s:
            print (parseobj, tokens)
            raise
        #assert parseobj.parsestate == 0

    @staticmethod
    def checkstate(parseobj, expected, new):
        #assert parseobj.parsestate == expected, (parseobj.parsestate, expected)
        parseobj.parsestate = new

    @classmethod
    def subparse(cls, schpage, tokens, lineiterator):
        cls.checkstate(schpage, 1, 1)
        assert cls.tokenlength[0] <= len(tokens) <= cls.tokenlength[-1]
        schpage.items.append(cls(tokens, lineiterator))

    def __init__(self, tokens=[], lineiterator=None):
        if lineiterator is not None:
            self.startparse(self, lineiterator, False)
