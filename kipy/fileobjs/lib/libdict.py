from .header import LibFile
from kipy.fileobjs.paths import kicad_root
from kipy.utility import FileAccess

class LibDict(dict):
    ''' Find all the libraries, and make a dictionary which
        contains all the components.
    '''

    def findlibs(self, cfgfile, projfname):
        if projfname is not None:
            projdir = projfname[-1]
            libdirs = [projdir]
        libdirs.extend(str(cfgfile.eeschema.libdir).split(';'))
        libdirs.append(kicad_root)
        libdirs = [FileAccess(x) for x in libdirs if x]
        libdirs[-1] |= 'library'

        liblist = cfgfile.eeschema.libraries
        liblist = [(x, getattr(liblist, x)) for x in liblist]
        for x in liblist:
            assert x[0].lower().startswith('libname')
        liblist = [(int(x[0][7:]), x[1]) for x in liblist]

        badlibs = []

        # Check most important library first, in case components in more than one lib
        # Figure out which one of these to do at some point:
        # for sortorder, libname in reversed(sorted(liblist)):
        for sortorder, libname in sorted(liblist):
            libname = libname + '.lib'
            for testdir in libdirs:
                testname = testdir | libname
                if testname.exists:
                    break
            else:
                badlibs.append(libname)
                continue
            yield testname

        if projfname is not None:
            cache_prefix = projdir | projfname.basename[:-4]
            for cache_suffix in ('-cache.lib', '.cache.lib'):
                cachelib = cache_prefix + cache_suffix
                if cachelib.exists:
                    yield cachelib
                    break

        if badlibs:
            warning = ('Warning: Could not find libraries:\n' + 
                        '          %s\n     In path list:\n          %s' %
                        ('\n          '.join(badlibs),
                         '\n          '.join(libdirs)))
            if self.warnlist:
                self.warnlist.append(warning)
            else:
                print warning

    def addfile(self, libf):
        complist = LibFile(libf)
        for comp in complist:
            names = [comp.name] + comp.alias
            for name in names:
                self.setdefault(name.upper(), []).append((comp, libf))

    def __init__(self, cfgfile=None, projfname=None, warnlist=None):
        self.warnlist = warnlist
        if cfgfile is not None:
            for libf in self.findlibs(cfgfile, projfname):
                self.addfile(libf)

    def check_duplicates(self, print_result=True):
        result = []
        for name, parts in sorted(self.iteritems()):
            if len(parts) != 1:
                result.append("Name collision: %s\n     from %s\n     overridden in %s" % (name, parts[1][1], parts[0][1]))
        if print_result:
            print '\n'.join(result)
        return result
