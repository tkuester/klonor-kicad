'''

The Pin and Component classes inherit from SchItem.  If this module
is imported, then the SchItem metaclass will wire the Component class
into the SchItem class for dispatch.  It will also make SchItem.Pin
reference the Pin class and SchItem.Component reference the component
class.

'''
from ...utility import IndexedString
from .schitems import SchItem

class Pin(SchItem, SchItem.PinOrLabel):
    add_dispatch = False
    is_power_flag = False
    invisible = False
    net_ids = ()

    def __init__(self, component, pinname, pinnum, x, y, etype, ptype):
        self.install(component.page, x, y)
        self.pinname = pinname
        self.pinnum = pinnum
        self.component = component
        self.userinfo = '%s pin %s (%s)' % (component.userinfo, pinnum, pinname)
        self.etype = etype
        self.ptype = ptype
        if ptype == 'N':
            netname = self.normalize_name('Pin', str(pinname))
            netid = self.pagejoin(self.component.page.pagename, netname)
            self.net_ids = (netid, )
            self.invisible = not component.virtual_component
        elif component.virtual_component and not isinstance(component, self.Sheet):
            if self.component.parttype == 'PWR_FLAG':
                self.is_power_flag = True
            else:
                self.warn('Non-invisible pin on power component')

    def fracture(self):
        ''' fracture() is used for busses.  Adding the method here
            makes this work just like a label class for this purpose.
        '''
        return [self,]

class Component(SchItem, SchItem.Keepout):

    virtual_component = False   # True for power pins

    def getxy(self, description, xoffset, yoffset):
        ''' Code to do this transcribed from:
               kicad/eeschema/class_sch_component.cpp
               wxPoint SCH_COMPONENT::GetScreenCoord( const wxPoint& coord )
        '''
        transform = self.transform
        try:
            x = self.posx + xoffset * transform[0] + yoffset * transform[1]
            y = self.posy + xoffset * transform[2] + yoffset * transform[3]
        except TypeError:
            # Sometimes we get bad data.  This aids in tracking down
            # the culprit
            print (xoffset, yoffset, self.posx, self.posy,
                   self.transform, self.parttype, description)
            raise
        return x, y

    def setpartinfo(self, source, page):
        timestamp = self.pagejoin(page.timestamp, str(source.timestamp), '/')
        self.page = page
        self.source = source
        self.posx, self.posy = source.posx, source.posy
        self.transform = source.transform
        self.timestamp = timestamp
        self.variant = source.variant
        self.parttype = source.parttype

        for path, refdes, subpart in source.altref:
            if path == timestamp:
                break
        else:
            refdes, subpart = source.refdes, source.subpart
        if str(refdes).startswith('#'):
            self.virtual_component = True

        self.subpart = subpart
        self.refdes = IndexedString(refdes)

    def findlibpart(self):
        libdict = self.page.libdict

        partname = str(self.parttype)
        try:
            libinfo = libdict[partname]
        except KeyError:
            try:
                libinfo = libdict['~' + partname]
            except KeyError:
                return None
        return libinfo[0]

    def installcomponentpins(self, pins):
        self.page.allparts.add(self)
        self.pindict = pindict = {}

        for pin in pins:
            x, y = self.getxy('pin %s %s' % (pin.name, pin.num), pin.posx, pin.posy)
            mypin = self.Pin(self, pin.name, pin.num, x, y, pin.etype, pin.ptype)
            if pindict.setdefault(pin.num, mypin) is not mypin:
                mypin.warn('Duplicate pin number')
                badpinnum = '_badpin_%s_%%s' % pin.num
                i = 0
                while pindict.setdefault(badpinnum %i, mypin) is not mypin:
                    i += 1

    def setlibinfo(self):
        libinfo = self.findlibpart()
        if libinfo is None:
            boundary = [-200, -200, 200, 200]
            suffix = ''
            self.pindict = {}
        else:
            libpart, libfn = libinfo
            boundary = list(libpart.boundary(self.subpart, self.variant))
            self.libpart, self.libfn = libpart, libfn
            suffix = libpart.unit_count > 1 and chr(ord('A') + self.subpart - 1) or ''

        boundary[:2] = self.getxy('part boundary #1', *boundary[:2])
        boundary[2:] = self.getxy('part boundary #2', *boundary[2:])

        self.install(self.page, *boundary)
        self.userinfo = 'Component %s %s%s' % (self.parttype, self.refdes, suffix)

        if libinfo is None:
            return self.warn('Could not find component in library')

        pins = libpart.pins(self.subpart, self.variant)
        self.installcomponentpins(pins)

    def __init__(self, item, page):
        self.setpartinfo(item, page)
        self.setlibinfo()
