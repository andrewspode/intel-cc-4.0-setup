# intel-cc-4.0-setup

A script that unpacks **Intel(R) C/C++ Compiler 4.0 (build 99100)** from the evaluation installer
`compeval.exe`, on Linux/macOS/Windows, without running the InstallShield installer or needing Wine.
This repository contains **no Intel software**; you supply the installer.

## Why this exists

Byte-matching decompilation projects need the *exact* compiler a game was built with. Some late-1990s
PC games used Intel's compiler for their SSE ("Katmai"/Pentium III) code paths, and ICL 4.0 (1999) is
the release that first shipped Streaming SIMD Extensions support. Intel never released it as a normal
retail download that survives today: it was sold as a boxed product and distributed as a free
14-day *evaluation* on the web and on promotional CDs. There is no public, maintained download, and
the few surviving copies are easy to miss (the one this script targets sits inside an ISO of the
May 1999 *Intel Technologies Developers Insight CD-ROM* on archive.org). Finding it took real effort,
so this repo records where it is, how to verify you have the right file, and how to unpack it in a
reproducible way, so others working on the same kind of project do not have to rediscover it.

It was found while decompiling *Indiana Jones and the Infernal Machine* (its `rdModel3K` SSE renderer
and `libm` helpers carry ICL's aligned-stack dual-entry function prologues).

## Getting the installer

archive.org item `Intel_Technologies_Developers_Insight_CD-ROM_May_1999`; archive.org serves single files
from inside the ISO:

    https://archive.org/download/Intel_Technologies_Developers_Insight_CD-ROM_May_1999/Intel%20Technologies%20Developers%20Insight%20CD-ROM%20May%201999.ISO/design/perftool/icl/compeval.exe

Expected: 5,102,735 bytes, SHA-256
`931fecd143c7532dc944bad4d2a7a1aadf76d143c08161eec25ba8801131746e`. (Same CD also has older ICL 2.4
material under `design/perftool/icl24/`.)

## Usage

Needs Python 3, `7z`/`7zz`/`7za` and [`unshield`](https://github.com/twogood/unshield) (>= 1.4;
distro packages exist, or build it from source with a C compiler and zlib).

    python3 setup_icl40.py compeval.exe icl40

It checks the installer hash, extracts the embedded CAB, unpacks InstallShield's `data1.cab` (44 files:
`icl.exe`, `mcpcom.exe`, `xilink.exe`, the SSE headers such as `xmmintrin.h`, `libm.lib`, ...) and
prints the hashes of `icl.exe` and `mcpcom.exe`. The evaluation refuses to run after its 14 days (and,
under wibo, without its registry key); `python3 patch_trial.py icl40` optionally writes `icl_notrial.exe`, a
patched copy of the driver that skips that check (see NOTES.md).

The compilers are Win32 console programs; they run under [wibo](https://github.com/decompals/wibo) or
Wine. Example (from `Compiler_Bin_Files`): `wibo icl.exe -nologo -c -O2 -QxK -FAs -I../Compiler_Include_files file.c`.

## Licence and status

The script is MIT-licensed. Intel C/C++ Compiler 4.0 remains Intel's proprietary software, licensed
in 1999 as a time-limited evaluation; nothing here grants rights to it. Use it only for
interoperability and preservation work such as reproducing the bytes of software you already own.
See [NOTES.md](NOTES.md) for what is known about the package.
