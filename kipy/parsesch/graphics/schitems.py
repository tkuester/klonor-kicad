class SchItem(object):
    ''' SchItem is the "driver" class for the parse code
        Most parse classes inherit from this, and the metaclass
        used by this class means that during the process of
        inheritance, a reference to the subclass is automagically
        added to the base SchItem class, and for classes which
        directly represent items in the schematic file, a reference
        to the class is also added to the _dispatchdict dispatch
        dictionary.
    '''
    from .primitives import Point, Line, Rectangle
    from kipy.utility import MetaHelper as __metaclass__
    from kipy.fileobjs import SchItem as FileSchItem

    class PinOrLabel(Point):
        ''' A PinOrLabel is a location where things connect.
        '''
        pass

    class Keepout(Rectangle):
        ''' A keepout is a location which should not overlap
            other locations (otherwise, there might be something
            on the schematic which the user cannot see).
        '''
        def __init__(self, userinfo, *args):
            self.install(*args)
            self.userinfo = userinfo

    _dispatchdict = {}     # Entries here for all .sch file classes
    add_dispatch = True    # By default, subclasses added to dispatch dict

    @classmethod
    def _classinit(cls, base):
        ''' This method is called by the metaclass to add subclass references
            to the base class dictionary and optionally to the dispatch
            dictionary.
        '''
        if base is None:
            cls._rootclass = cls
            return
        if cls.add_dispatch:
            cls._dispatchdict[getattr(cls.FileSchItem, cls.__name__)] = cls
        setattr(cls._rootclass, cls.__name__, cls)

    @classmethod
    def dispatch(cls, sourcefields, page):
        ''' This is the lowest level dispatch of the parser.  It
            instantiates an object of the correct subclass for
            every object in the .sch file.
        '''
        dispatchdict = cls._dispatchdict
        for item in sourcefields:
            dispatchdict[item.__class__](item, page)

    def normalize_name(self, nametype, name, warnobj=None):
        ''' Internally, we use ' / ' as a hierarchy separator.
            This function makes sure that this character sequence
            does not itself appear in the things we are separating.
        '''
        new = name.replace(' / ', '_/_')
        if new != name:
            wparams = nametype, name, new
            wmsg = ('%s name changed to simplify processing:\n' +
                        '               %s changed to %s') % wparams
            getattr(self, 'warn', warnobj)(wmsg)
        return new

    @staticmethod
    def pagejoin(page, name, separator=' / '):
        ''' Join a page and a name together
        '''
        page = page.split(separator, 1)
        page[0] = ''
        page.append(name)
        return separator.join(page)

class Connection(SchItem, SchItem.Point):
    ''' Instantiate schematic connection points (dots)
    '''
    def __init__(self, item, page):
        self.install(page, item.posx, item.posy)

class NoConn(SchItem, SchItem.Point):
    ''' Instantiate schematic noconn (X) symbols
    '''
    def __init__(self, item, page):
        self.install(page, item.posx, item.posy)

class Wire(SchItem, SchItem.Line):
    ''' Instantiate schematic wires
    '''
    ignore = ('Notes Line',)
    keep = 'Wire Line', 'Bus Line'
    def __init__(self, item, page):
        wiretype = item.wiretype
        if wiretype in self.keep:
            self.install(page, item.startx, item.starty, item.endx, item.endy)
            self.wiretype = wiretype
        else:
            assert wiretype in self.ignore, wiretype  # Others not supported yet
            self.Keepout(wiretype, page, item.startx, item.starty, item.endx, item.endy)

class Kmarq(SchItem, SchItem.PinOrLabel):
    ''' No idea what this is but one of the demo files had a couple embedded.
    '''
    def __init__(self, item, page):
        page.warn(item.text)

class Entry(SchItem, SchItem.Keepout):
    ''' Entrys are electrically meaningless.
        We just instantiate a small keepout area.
    '''
    def makekeepout(self, page, x1, y1, x2, y2):
        # For simplicity, make a keepout that
        # doesn't impinge on the pins

        def shrink(a, b, percent=95):
            frac1 = percent / 100.0
            frac2 = 1.0 - frac1
            return int(round(a * frac1 + b * frac2))

        self.install(page, shrink(x1, x2), shrink(y1, y2),
                           shrink(x2, x1), shrink(y2, y1))

    def __init__(self, item, page):
        wiretype = item.wiretype
        assert wiretype in self.Wire.keep, wiretype
        x1, y1, x2, y2 = item.startx, item.starty, item.endx, item.endy
        self.makekeepout(page, x1, y1, x2, y2)
        self.page = page
        self.userinfo = 'Entry ' + wiretype
