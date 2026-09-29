#!/usr/bin/env python3
"""Make a copy of Intel C/C++ Compiler 4.0's icl.exe that skips the 14-day trial check.

Run setup_icl40.py first. The original icl.exe is left untouched; the patched driver is
written next to it as icl_notrial.exe.

    python3 patch_trial.py OUTDIR

The trial check is one function in the driver (VA 0x0040B4D0, file offset 0xA8D0). It returns
nonzero when the trial is valid; the patch replaces its first six bytes with `mov eax,1; ret`.
mcpcom.exe (the actual compiler) contains no trial code.
"""
import hashlib, os, sys

ICL_SHA256 = "5616f74f14f74adc6f4f38bff6d527fea01e852954f0bf7af1975493df944072"
PATCHED_SHA256 = "fed5dc869b8d1053778586684fb3bfe4091d22399f2d8aa9028dc538ba64ad81"
PATCH_OFFSET = 0xA8D0
ORIG = bytes([0x55, 0x8B, 0xEC, 0x83, 0xEC, 0x50])   # push ebp; mov ebp,esp; sub esp,0x50
PATCH = bytes([0xB8, 0x01, 0x00, 0x00, 0x00, 0xC3])  # mov eax,1; ret


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    bindir = os.path.join(os.path.abspath(sys.argv[1]), "Compiler_Bin_Files")
    with open(os.path.join(bindir, "icl.exe"), "rb") as f:
        data = bytearray(f.read())
    if hashlib.sha256(data).hexdigest() != ICL_SHA256:
        sys.exit("unexpected icl.exe (SHA-256 mismatch)")
    if bytes(data[PATCH_OFFSET:PATCH_OFFSET + 6]) != ORIG:
        sys.exit("patch site does not match")
    data[PATCH_OFFSET:PATCH_OFFSET + 6] = PATCH
    if hashlib.sha256(data).hexdigest() != PATCHED_SHA256:
        sys.exit("patched SHA-256 mismatch")
    dst = os.path.join(bindir, "icl_notrial.exe")
    with open(dst, "wb") as f:
        f.write(data)
    print("ok:", dst)


if __name__ == "__main__":
    main()
