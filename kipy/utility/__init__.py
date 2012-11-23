'''
    Utility functions for Kicad python library
'''
from .fileaccess import FileAccess, getint
from .istring import IndexedString, refdeslist

class MetaHelper(type):
    '''  MetaHelper is to simplify the use of metaclasses for one useful case.
         Whenever a class which uses MetaHelper as its metaclass is compiled,
         after compilation, that class's _classinit() function will be called.
         _classinit() will be passed a base class parameter which is the
         superclass which also uses MetaHelper as its metaclass, or None if
         no such superclass exists. 
    '''
    def __init__(cls, name, bases, clsdict):
        type.__init__(cls, name, bases, clsdict)
        base = ([x for x in cls.__bases__ if type(x) is MetaHelper] + [None])[0]
        if cls._classinit is not None:
            cls._classinit(base)


def check_roundtrip(fname, func, dumpdir=''):
    f = FileAccess(fname)
    x = func(f)
    print '%s -- %s' % (f.basename, str(x) == f.read() and 'OK' or 'FAIL')
    if dumpdir:
        dumpdir = FileAccess(dumpdir)
        dumpf = dumpdir | f.basename
        if dumpdir.exists:
            f = open(dumpf, 'wb')
            f.write(str(x))
        else:
            print "Could not write to file", dumpf
    return x
