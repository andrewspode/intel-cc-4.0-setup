# Notes on the package

- Installer: InstallShield self-extractor. The payload is a plain MSZip cabinet (1 folder, 19 files) at
  file offset 130290 (size 4,972,445), which holds `data1.cab` (InstallShield 5 `ISc(` format,
  44 files), `setup.exe`, `setup.ins`, `relnotes4_0.htm`, `license.txt` and so on.
- Banner: `Intel(R) C/C++ Compiler Version 4.0  99100 (TRIAL VERSION)`.
- `icl.exe` is only the driver; `mcpcom.exe` is the actual front end and code generator, and it lives
  next to it. The evaluation's 14-day limit is enforced by the driver.
- Useful flags for SSE code from that era: `-O2 -QxK` (Katmai/SSE), `-FAs` (assembly listing with
  source), `-I../Compiler_Include_files` (the compiler does not find its own headers otherwise).
- Signature of ICL 4.0 output: the dual-entry aligned-stack prologue
  `push ebx; mov ebx,esp; sub esp,8; and esp,-16; add esp,8; jmp L; push ebx; mov ebx,esp; L: sub esp,N`
  for functions using aligned SSE data, and `lea esi,[esi+0]` style alignment fill.
- `libm.lib` members: `floor.obu`, `ceil` and `modf.obu` have the same code as the helpers in the
  Indiana Jones executable, but the shipped `libm.lib` is a different build (different `.data` and a
  differently scheduled `modf`), so it is not a byte-exact source for them.

## Trial check

`patch_trial.py` (optional, run after `setup_icl40.py`) writes `icl_notrial.exe`, a copy of the driver
whose trial-validity function (VA 0x0040B4D0, file offset 0xA8D0) returns 1 immediately. It verifies
the hash of the input `icl.exe`, the six bytes it overwrites, and the hash of the result. The original
`icl.exe` is not modified. Without the patch, the driver reports `trial registry error` (or
`current time is not within the trial period`) and refuses to compile.
