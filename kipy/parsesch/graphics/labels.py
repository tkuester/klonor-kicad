'''

The classes in this module inherit from SchItem.  If this module
is imported, then the SchItem metaclass will wire these classes into
the SchItem class for dispatch.  It will also make, e.g.,
SchItem.Label reference the Label class and SchItem.Text reference
the Text class, etc.

The only classes which are directly invoked from the dispatcher
are Text and Sheet.  Instantiations of Labels are made from the
initialization code for the Text and Sheet classes.

'''

import copy
from .schitems import SchItem

class Label(SchItem, SchItem.PinOrLabel):
    add_dispatch = False
    reverse_order = False

    def unpack_netid(self, netid):
        ''' Figure out bus naming information
        '''
        if not netid.endswith(']'):
            self.net_ids = (netid,)
            return

        prefix, nums = netid.rsplit('[', 1)
        oprefix = self.original_name.rsplit('[',1)[0]

        nums = nums[:-1].split('..', 1)
        if len(nums) == 1:
            nums.append(nums[0])
        num1, num2 = (int(x) for x in nums)

        reverse = num1 > num2
        if reverse:
            self.reverse_order = True
            num1, num2 = num2, num1

        bus_suffixes = range(num1, num2+1)

        netid = ['%s%s' % (prefix, x) for x in bus_suffixes]
        original = ['%s%s' % (oprefix, x) for x in bus_suffixes]

        if reverse:
            netid.reverse()
            original.reverse()

        if len(original) > 1:
            self.original_name = tuple(original)
        self.net_ids = tuple(netid)

    def __init__(self, page, userinfo, netid, original_name, x, y):
        page.alllabels.add(self)
        self.install(page, x, y)
        self.userinfo = userinfo
        self.original_name = original_name
        self.unpack_netid(netid)

    def fracture(self):
        ''' Convert a single label into multiple labels, one
            for each bus wire.
        '''
        net_ids = self.net_ids
        if len(net_ids) == 1:
            return self

        alllabels = self.page.alllabels
        alllabels.remove(self)
        result = []
        for (netid, original) in zip(self.net_ids, self.original_name):
            new = copy.copy(self)
            new.net_ids = (netid,)
            new.original_name = original
            result.append(new)
            alllabels.add(new)
        return result

class GLabel(Label):
    'Global Labels'
    pass

class HLabel(Label):
    'Hierarchical labels'
    pass

class SLabel(Label):
    'Sheet labels (connect to hierarchical)'
    pass

class Text(SchItem):
    ''' Dispatcher for .sch file Text entries
    '''
    @staticmethod
    def makekeepout(userinfo, item, page):
        orientation = item.orientation
        halfheight = (item.size + 40) / 2
        width = halfheight * 6
        x1 = x2 = item.posx
        y1 = y2 = item.posy
        if orientation in (0, 2):
            x1 += (orientation - 1) * width
            y1 -= halfheight
            y2 += halfheight
        else:
            y1 += (orientation - 2) * width
            x1 -= halfheight
            x2 += halfheight
        SchItem.Keepout(userinfo, page, x1, y1, x2, y2)

    def __init__(self, item, page):
        texttype = item.texttype
        original_name = item.text
        pagename = page.pagename

        makelabel = getattr(self, texttype, int)
        if not issubclass(makelabel, Label):
            if texttype != 'Notes':
                print (makelabel, )
                raise SystemError('Page %s, %s label %s at (%s, %s) not supported' %
                            (pagename, texttype, original_name, item.posx, item.posy))
            return

        netname = self.normalize_name('Label', original_name, page.warn)
        netid = self.pagejoin(pagename, netname)
        userinfo = '%s %s' % (texttype, netname)

        if isinstance(makelabel, (GLabel, HLabel)):
            self.makekeepout(userinfo, item, page)
        makelabel(page, userinfo, netid, original_name, item.posx, item.posy)


class Sheet(SchItem, SchItem.Keepout):
    ''' Dispatcher for .sch file Sheet entries
    '''

    def __init__(self, sheet, page):
        sheetname = self.normalize_name('Sheet', sheet.fields[0].name)

        fname = sheet.fields[1].name

        self.install(page, sheet.startx, sheet.starty, sheet.endx, sheet.endy)
        self.userinfo = 'Sheet %s' % sheetname

        pin_user_prefix = self.userinfo + ' pin '
        sheetname = self.pagejoin(page.pagename, sheetname)

        for item in sheet.fields[2:]:
            original_name = item.name
            netname = self.normalize_name('Sheet pin', original_name)
            netid = self.pagejoin(sheetname, netname)
            userinfo = pin_user_prefix + original_name

            SLabel(page, userinfo, netid, original_name, item.posx, item.posy)
