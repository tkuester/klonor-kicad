
The name kipy is a contraction of "KiCAD Python" because it is a goal
to provide useful scripts around KiCad.

kipy is Copyright (C) 2009 by Patrick Maupin, Austin, Texas

kipy is made available at pyeda.org under the OSI-approved MIT license.

Documentation is available at pyeda.org


Code directory structure:

kipy
    utility -- low level functions and objects
    fileobjs -- file-specific objects
    parsesch -- parse a schematic to discover connectivity
    tools -- runnable scripts


Requirements:

1) Linux or Windows
2) Python 2.5 or 2.6 (For now -- will eventually support 3.0 as well)

Using kipy:

1) Checkout from subversion into xxxx/xxxx/kipy/ directory
2) cd to your KiCad project directory.
3) xxxxx/xxxx/kipy/tools/checkproj.py -- to check your project
4) xxxxx/xxxx/kipy/tools/expressdump.py -- dumps netlist in ExpressPCB format
5) xxxxx/xxxx/kipy/tools/getpins.py <refid>  -- print pin info for <refid>
6) xxxxx/xxxx/kipy/tools/demos.py  -- checks whole demo tree
7) xxxxx/xxxx/kipy/tools/roundtrip.py -- tests roundtripping library and demo tree
