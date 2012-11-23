import re
import types

class IndexedString(str):
    """   An indexed string is designed to sort properly alphanumerically
    """
    _indexedsplitter = types.MethodType(re.compile('([0-9]+)').split, None, str)

    def __new__(cls, s):
        if isinstance(s, cls):
            return s
        self =  str.__new__(cls, s)
        # Put the string itself into the key so that
        # 'xxx00' doesn't equal 'xxx0'
        key = self._indexedsplitter()
        key = [int(x) if x.isdigit() else x.upper() for x in key if x]
        key.append(str(self))
        self._key = key = tuple(key)
        self._hash = hash(key)
        return self

    def __hash__(self):
        return self._hash
    def __eq__(self, other):
        try:                   return self._key == other._key
        except AttributeError: return str.__eq__(self, other)
    def __ne__(self, other):
        try:                   return self._key != other._key
        except AttributeError: return str.__ne__(self, other)
    def __gt__(self, other):
        try:                   return self._key >  other._key
        except AttributeError: return str.__gt__(self, other)
    def __ge__(self, other):
        try:                   return self._key >= other._key
        except AttributeError: return str.__ge__(self, other)
    def __lt__(self, other):
        try:                   return self._key <  other._key
        except AttributeError: return str.__lt__(self, other)
    def __le__(self, other):
        try:                   return self._key <= other._key
        except AttributeError: return str.__le__(self, other)

def stringgroups(slist):
    if not slist:
        return
    slist = iter(sorted(IndexedString(s) for s in slist))
    nextkey = None
    sgroup = []
    for s in slist:
        key = list(s._key)
        key.pop()
        if key != nextkey:
            if sgroup:
                yield sgroup
                sgroup = []
            keyindex = isinstance(key[-1], int) and -1 or isinstance(key[-2], int) and -2
            if not keyindex:
                yield [s]
                continue
            nextkey = key
        sgroup.append(s)
        nextkey[keyindex] += 1
    if sgroup:
        yield sgroup

def flattenstrings(s):
    if isinstance(s, str):
        yield s
        return
    for x in s:
        for x in flattenstrings(x):
            yield x

def stringlist(s):
    s = ' '.join(flattenstrings(s))
    return s.replace(',', ' ').split()

def groupinfo(group):
    key1 = group[0]._key
    key2 = group[-1]._key
    keyindex = isinstance(key1[-2], int) and -2 or -3
    index1 = key1[keyindex]
    index2 = key2[keyindex]
    prefix = ''.join(str(s) for s in key1[:keyindex])
    suffix = ''.join(key1[keyindex + 1:-1])
    return prefix, index1, index2, suffix

def refdeslist(*s):
    result = []
    for group in stringgroups(stringlist(s)):
        if len(group) == 1:
            result.append(group[0])
        else:
            result.append('%s%d-%d%s' % groupinfo(group))
    return ', '.join(result)
