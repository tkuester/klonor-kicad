'''

These files are almost parseable by the Python configparser.

Except -- the config parser does not handle configuration items
at the start of the file before the first [xxx].

So I had to build something anyway, so I made it more Pythonic --
you can reference cfgfile.eeschema.library.foo, for example, to
get:

[eeschema/library]
foo = xxx

'''

from kipy.utility import getint

class _NotPresent(object):
    pass

class ItemAccessor(object):
    def __init__(self, fileobj=None):
        real_object = isinstance(fileobj, ItemAccessor) and fileobj._real_object or ConfigItem()
        super(ItemAccessor, self).__setattr__('_real_object', real_object)

    def __setattr__(self, attr, value):
        real = super(ItemAccessor, self).__getattribute__('_real_object')
        real(attr, value, write=True)

    def __getattribute__(self, attr):
        if attr.startswith('__'):  # Goofiness for __length_hint__
            raise AttributeError
        real = super(ItemAccessor, self).__getattribute__('_real_object')
        if attr == '_real_object':
            return real
        return real(attr)
    def __iter__(self):
        return iter(self._real_object.display_order)

class EmptyObj(ItemAccessor, str):
    def __new__(cls, *whatever):
        return str.__new__(cls)

class ConfigItem(object):
    def __init__(self):
        self.display_order = []
        self.items = {}

    def __call__(self, attr, newval=None, write=False):
        key = attr.upper()
        items = self.items
        oldval = items.get(key, _NotPresent)
        update = write
        if oldval is _NotPresent:
            self.display_order.append(attr)
            if not write:
                update = True
                oldval = newval = ItemAccessor()

        if update:
            items[key] = newval
        if not write and isinstance(oldval, ItemAccessor) and not oldval._real_object.items:
            oldval = EmptyObj(oldval)
        return oldval

    def parse(self, filesource):
        self.filesource=filesource
        prefix = ()
        obj = self
        for line in filesource.readlines():
            line = line.strip()
            if line.startswith('['):
                assert line.endswith(']')
                obj = self
                for attr in line[1:-1].strip().split('/'):
                    obj = obj(attr)._real_object
                continue
            name, value = line.split('=', 1)
            obj(name, getint(value), True)

    def render(self, prefix=(), result=None):
        if result is None:
            result = []
        itemdict = self.items
        values = []
        subitems = []
        for attr in self.display_order:
            value = itemdict[attr.upper()]
            if not isinstance(value, ItemAccessor):
                values.append((attr, value))
            else:
                subitems.append((attr, value._real_object))
        if values:
            if prefix:
                result.append('[%s]' % '/'.join(prefix))
            for attr, value in values:
                result.append('%s=%s' % (attr, value))
        for attr, value in subitems:
            value.render(prefix+(attr,), result)
        return result

class ConfigFile(ItemAccessor):
    def __init__(self, filesource=None):
        super(ConfigFile, self).__init__()
        if filesource is not None:
            self._real_object.parse(filesource)
    def __str__(self):
        result = self._real_object.render()
        result.append('')
        return '\n'.join(result)
