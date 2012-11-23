'''
KICAD library objects
'''
from .draw import LibDraw

class LibComponent(object):
    fplist_first = False
    '''
    DEF name reference unused text_offset draw_pinnumber draw_pinname unit_count units_locked option_flag
    * name = component name in library (74LS02 ...)
    * reference = Reference ( U, R, IC .., which become U3, U8, R1, R45, IC4...)
    * unused = 0 (reserved)
    * text_offset = offset for pin name position
    * draw_pinnumber = Y (display pin number) or N (do not display pin number).
    * draw_pinname = Y (display pin name) or N (do not display pin name).
    * unit_count = Number of part ( or section) in a component package.
    * units_locked = = L (units are not identical and cannot be swapped) or F (units are identical and therefore can be swapped) (Used only if unit_count > 1)
    * option_flag = N (normal) or P (component type "power")
    '''

    def __init__(self, name='none', reference='U', lineiterator=None, firstline=''):
        self.fields = []
        self.fplist = []
        self.alias = []
        self.draw = []
        self._boundaries = {}
        self._pins = {}

        if lineiterator is not None:
            return self._fromsource(lineiterator, firstline)

        self.unused = 0
        self.text_offset = 40
        self.draw_pinnumber = 'Y'
        self.draw_pinname = 'Y'
        self.unit_count = 1
        self.units_locked = 'L'
        self.option_flag = 'N'
        self.fields.append(TextField(reference))
        self.fields.append(TextField(name))
        self.name = name
        self.reference = reference

    def _fromsource(self, lineiterator, firstline):
        firstline = firstline or lineiterator.next()
        defstr, name, ref, unused, offset, drawnum, drawname, units, locked, options = firstline.split()
        assert defstr == 'DEF'
        self._name = name
        self._reference = ref
        self.unused = int(unused)
        self.text_offset = int(offset)
        self.draw_pinnumber = drawnum
        self.draw_pinname = drawname
        self.unit_count = int(units)
        self.units_locked = locked
        self.option_flag = options
        for line in lineiterator:
            tokens = line.split()
            if tokens[0].startswith('F') and tokens[0][1:].isdigit():
                tokens[0] = tokens[0][1:]
                self.fields.append(LibDraw.TextField(tokens, line))
            else:
                break
        while True:
            if tokens[0] =='$FPLIST':
                assert not self.fplist
                for line in lineiterator:
                    if line.startswith('$ENDFPLIST'):
                        break
                    self.fplist.append(line)
                fplist_first = not self.alias
            elif tokens[0] == 'ALIAS':
                assert not self.alias
                self.alias = tokens[1:]
            elif tokens[0] == 'DRAW':
                assert not self.draw
                self.draw = LibDraw.parse(lineiterator, line)
            elif tokens == ['ENDDEF']:
                break
            else:
                assert 0, (line, tokens)
            line = lineiterator.next()
            tokens = line.split()

    def _get_name(self):
        return self._name
    def _set_name(self, value):
        self.fields[1].name = self._name = value
    name = property(_get_name, _set_name)

    def _get_reference(self):
        return self._reference
    def _set_reference(self, value):
        self.fields[0].name = self._reference = value
    reference = property(_get_reference, _set_reference)

    def __str__(self):
        lines = ['#\n# %s\n#' % self.name.replace('~', '')]
        lines.append('DEF %s %s %s %s %s %s %s %s %s' %
            (self.name, self.reference, self.unused, self.text_offset,
            self.draw_pinnumber, self.draw_pinname, self.unit_count,
            self.units_locked, self.option_flag))
        lines.extend((str(x) for x in self.fields))
        if self.alias and not self.fplist_first:
            lines.append('ALIAS %s' % ' '.join(self.alias))
        if self.fplist:
            lines.append('$FPLIST')
            lines.extend((str(x) for x in self.fplist))
            lines.append('$ENDFPLIST')
        if self.alias and self.fplist_first:
            lines.append('ALIAS %s' % ' '.join(self.alias))
        LibDraw.render(self.draw, lines)
        lines.append('ENDDEF')
        return '\n'.join(lines)

    def boundary(self, subpart=1, variant=1):
        ''' Return a bounding rectangle for the part (except the pins)
        '''
        dictindex = subpart, variant
        if dictindex not in self._boundaries:
            xlist, ylist = [0], [0]
            subpart = 0, subpart
            variant = 0, variant
            for item in self.draw:
                if item.subpart in subpart and item.variant in variant:
                    item.boundary(xlist, ylist)
            self._boundaries[dictindex] = min(xlist), min(ylist), max(xlist), max(ylist)
        return self._boundaries[dictindex]

    def pins(self, subpart=1, variant=1):
        dictindex = subpart, variant
        if dictindex not in self._pins:
            pinlist = []
            subpart = 0, subpart
            variant = 0, variant
            PinClass = LibDraw.Pin
            for item in self.draw:
                if isinstance(item, PinClass) and item.subpart in subpart and item.variant in variant:
                    pinlist.append(item)
            self._pins[dictindex] = pinlist
        return self._pins[dictindex]
