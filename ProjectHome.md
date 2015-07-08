Sometimes electronics project have many instances of the same circuit repeated many times. Motor drivers, filters, amplifiers, LED drivers... KiCad lets you duplicate parts of the circuits and PCB layouts, but it cannot create clones with correct netlist linkages between them. This script facilitates this simple job.

The script uses an extended version of [pyeda](http://code.google.com/p/pyeda/) with partial support for parsing and writing KiCad BRD files. It has no UI so it should run without problems on Windows just like on Linux.

To check out the code execute this line:
```
svn co https://klonor-kicad.googlecode.com/svn/trunk/ kipy
```

KiCad does not store netlist information in the schematic and it makes the process of cloning is pretty complicated. The steps are many but they are all pretty simple:
  1. Create a macro circuit on a separate sheet, e.g. `macro.sch`
  1. Name the nets (use Local Labels) using macros like `%X%`, or `%X*2+1%`
> > The part numbers cannot end not in a number, so append `_0` to the parts that use macros in their names, e.g. `PIN_%X%_0`. This is only needed for the global referenced parts.
> > Make sure that the part numbers are not going to overlap with anything else in your circuit, use refdeses like `R100`, `C100` etc.
  1. Create footprint assignments in CvPCB and export it in .stf file
  1. Backannotate the footprint information from .stf file into your schematic
  1. Create the perfect PCB layout for your subcircuit, e.g. `macro.brd`
  1. run `klonorsch.py`, e.g.
> > `klonorsch.py --template-sch=macro.sch --output-sch=cloned.sch --yclones=10 --ysize=2000`
  1. open `cloned.sch` in eeschema, annotate (some warnings will appear) and generate netlist `cloned.net`
  1. copy your `macro.brd` in `cloned.brd`, open `cloned.brd` and read the netlist file `cloned.net`
> > This should get you all cloned modules loaded and piled up in the top left corner.
  1. Draw a zone in the "User Comments" layer, it will define the dimensions of the original
  1. save this board as `cloned-net.brd`
  1. run `klonorbrd.py`, e.g.
> > `klonorbrd.py --template-sch=macro.sch --template-brd=cloned-net.brd --output-brd=cloned.brd`

This will place all new modules in their correct locations and copy all the connecting tracks.


More advanced use case allows using klonor in multisheet projects when part of the project has already been layed out. See this screencast for a brief introductory tutorial:

<a href='http://www.youtube.com/watch?feature=player_embedded&v=mChTfL746Fs' target='_blank'><img src='http://img.youtube.com/vi/mChTfL746Fs/0.jpg' width='425' height=344 /></a>

I hope you find klonor helpful.
