from .schfile import SchFile
'''
Given a top schematic file name, SchDict will
read all the schematics and put them in a dictionary.

If they are instantiated multiple times, they will only
be read/parsed once, but each instantiation will have its
own dictionary entry with its own timestamp and parent.
'''

class SheetInstantiation(object):
    def __init__(self, database, sheetname, sheetfile, timestamp='', parent=None, antecedents=set()):
        namesep = ' / '

        sheetname = sheetname.replace(namesep, namesep.replace(' ', '_'))

        if timestamp is None:
            timestamp = sheetfile

        if parent is not None:
            sheetname = parent.sheetname + namesep + sheetname
            timestamp = parent.timestamp + '/' + timestamp

        if sheetname in database:
            raise SystemExit('Sheet %s in database multiple times' % sheetname)
        if timestamp in database.timestamps:
            raise SystemExit('Sheet %s timestamp same as sheet %s') % (sheetname, database[timestamp].sheetname)
        if sheetfile in antecedents:
            raise SystemExit('Loops not permitted in page hierarchy:\n    %s' %
                                  ', '.join(sorted((antecedents))))

        database[sheetname] = self
        database.timestamps[timestamp] = self
        database.priorityorder.append(sheetname)

        self.sheetname = sheetname
        self.sheetfile = sheetfile
        self.timestamp = timestamp
        self.sheetdata = database.readfile(sheetfile)

        antecedents.add(sheetfile)
        for item in self.sheetdata.items:
            if isinstance(item, item.Sheet):
                SheetInstantiation(database,
                                item.fields[0].name, item.fields[1].name,
                                item.timestamp, self, antecedents)
        antecedents.remove(sheetfile)


class SchDict(dict):
    def __init__(self, topschfile=None):
        self.timestamps = {}
        self.filecache = {}
        self.priorityorder = []

        if topschfile is not None:
            self.projdir = topschfile[-1]
            sheetfname = topschfile.basename
            sheetname = sheetfname.rsplit('.sch', 1)[0]
            self.topsheet = SheetInstantiation(self, sheetname, sheetfname)

    def readfile(self, sheetfile):
        sheetdata = self.filecache.get(sheetfile)
        if sheetdata is None:
            sheetdata = SchFile(self.projdir[sheetfile])
            self.filecache[sheetfile] = sheetdata
        return sheetdata
