'''
    File:  kicad_python.utility.fileaccess
    Exports:  FileAccess class
               - easily navigate filesystem with python constructs
               - open and read the file in a useful way
'''

import os

class AugmentedInt(int):
    '''   Used when int passed in as, e.g. '+12'
          we can store int(12), and display '+12'
    '''
    def __new__(cls, value, representation):
        self = int.__new__(cls, value)
        self.representation = representation
        return self

    def __str__(self):
        return self.representation

def getint(x):
    '''  Try to convert an item (expects a string, but not enforced)
         to an integer.  Return the original unconverted item on failure.
    '''
    try:
        y = int(x)
    except ValueError:
        return x
    if str(y) == x:
        return y
    return AugmentedInt(y, x)

class TokenList(list):
    '''Can add attributes'''
    pass


class FileAccess(str):
    def __new__(cls, *args):
        return str.__new__(cls, os.path.join(*(str(x) for x in args)))

    def read(self):
        f = open(self, 'rb')
        fdata = f.read()
        f.close()
        return fdata

    def write(self, fdata):
        f = open(self, 'wb')
        f.write(str(fdata))
        f.close()

    def readlines(self):
        return [x.rstrip() for x in self.read().splitlines()]

    def readlinetokens(self):
        for line in self.read().splitlines():
            tokens = line.split('"')
            for i in range(len(tokens)-1, -1, -2):
                tokens[i:i+1] = (getint(x) for x in tokens[i].split())
            result = TokenList(tokens)
            result.linetext = line
            yield result

    def __add__(self, other):
        return FileAccess(str(self) + other)
    def __or__(self, other):
        return FileAccess(self, other)
    def __getattr__(self, other):
        return self | other

    def __getitem__(self, other):
        ''' item[-1] returns parent directory of item
        '''
        if not isinstance(other, int):
            return self | other

        def splitpath(what, depth=100):
            if not depth:
                return [what]
            a, b = os.path.split(str(what))
            if not a:
                result = [b]
            elif a == what:
                result = [a]
            else:
                result = splitpath(a, depth-1)
                result.append(b)
            return result

        return FileAccess(*splitpath(self)[:other + (other >= 0)])

    @property
    def basename(self):
        return os.path.basename(str(self))

    @property
    def exists(self):
        return os.path.exists(str(self))
