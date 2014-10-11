Hardwarebreakpoints und GDB
===========================

:date: 2009-07-30 02:27:08
:tags: de, debugging, gdb

Wenn man sich wundert, wie man mit *gdb* lustig Hardwarebreakpoints
setzen kann, obwohl x86 eigentlich nur vier unterstützt: Die Manual
klärt auf.

  Since they depend on hardware resources, hardware breakpoints may be
  limited in number; when the user asks for more, GDB will start
  trying to set software breakpoints. (On some architectures, notably
  the 32-bit x86 platforms, GDB cannot always know whether there's
  enough hardware resources to insert all the hardware breakpoints and
  watchpoints. On those platforms, GDB prints an error message only
  when the program being debugged is continued.)

Gnarf.
