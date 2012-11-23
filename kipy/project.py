import glob
from .fileobjs import ConfigFile, LibDict, SchDict
from .fileobjs.paths import kicad_default_project
from .utility import FileAccess

class Project(object):
    '''  Collect all the information together about a schematic project
    '''

    def __init__(self, projname):
        explicit_name = projname.endswith('.pro')
        projdir = FileAccess(projname)
        if explicit_name:
            projname = projdir.basename[:-4]
        if explicit_name or not projdir.basename:
            projdir = projdir[-1]

        default_proj = FileAccess(kicad_default_project)
        projfname = projdir | projname + '.pro'
        if not projfname.exists:
            if explicit_name:
                raise SystemExit('\nCould not find project file %s\n' % projfname)
            names = glob.glob(projdir | '*.pro')
            if not names:
                projfname = default_proj
            elif len(names) > 1:
                raise SystemExit('More than one .pro file in %s -- must explicitly specify' % projdir)
            else:
                projfname = FileAccess(names[0])
                projname = projfname.basename[:-4]

        schfname = projdir | projname + '.sch'
        if not schfname.exists:
            schfname = None

        cfgfile = ConfigFile(projfname)
        if projfname != default_proj:
            defaultcfg = ConfigFile(default_proj)
            if not cfgfile.eeschema.libraries:
                cfgfile.eeschema.libraries = defaultcfg.eeschema.libraries

        self.projdir = projdir
        self.projname = projname
        self.projfname = projfname
        self.topschfname = schfname
        self.cfgfile = cfgfile
        self.netfn = projdir | projname + '.net'

        self.libdict = LibDict(self.cfgfile, projfname)
        self.schematic = SchDict(schfname)
