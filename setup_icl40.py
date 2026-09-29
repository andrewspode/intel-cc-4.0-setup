#!/usr/bin/env python3
"""Extract Intel(R) C/C++ Compiler 4.0 (evaluation, build 99100) from compeval.exe.

No Intel files are distributed here: you supply compeval.exe (see README.md).
Requires: python3, 7z/7zz/7za, unshield (>= 1.4).

    python3 setup_icl40.py compeval.exe OUTDIR
"""
import hashlib, os, shutil, struct, subprocess, sys, tempfile

COMPEVAL_SHA256 = "931fecd143c7532dc944bad4d2a7a1aadf76d143c08161eec25ba8801131746e"
ICL_SHA256 = "5616f74f14f74adc6f4f38bff6d527fea01e852954f0bf7af1975493df944072"
MCPCOM_SHA256 = "d337a5bbde08c1eebebe603288bac76be1bbd95548f178239d44102918a2aa21"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def run(*cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)


def find_tool(*names):
    for n in names:
        p = shutil.which(n)
        if p:
            return p
    sys.exit("missing tool: need one of " + ", ".join(names))


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    src, out = sys.argv[1], os.path.abspath(sys.argv[2])
    if sha256(src) != COMPEVAL_SHA256:
        sys.exit("compeval.exe SHA-256 mismatch (expected %s)" % COMPEVAL_SHA256)
    sevenz = find_tool("7zz", "7z", "7za")
    unshield = find_tool("unshield")
    data = open(src, "rb").read()
    # The SFX carries several 'MSCF' markers; the real cabinet is the one whose header
    # declares 1 folder and 19 files.
    start = length = None
    i = -1
    while True:
        i = data.find(b"MSCF", i + 1)
        if i < 0:
            break
        size = struct.unpack("<I", data[i + 8:i + 12])[0]
        nfold, nfile = struct.unpack("<HH", data[i + 26:i + 30])
        if (nfold, nfile) == (1, 19) and i + size <= len(data):
            start, length = i, size
            break
    if start is None:
        sys.exit("embedded CAB not found")
    os.makedirs(out, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        cab = os.path.join(tmp, "a.cab")
        with open(cab, "wb") as f:
            f.write(data[start:start + length])
        ex = os.path.join(tmp, "ex")
        run(sevenz, "x", "-y", "-o" + ex, cab)
        run(unshield, "-d", out, "x", os.path.join(ex, "data1.cab"))
    bindir = os.path.join(out, "Compiler_Bin_Files")
    for name, want in (("icl.exe", ICL_SHA256), ("mcpcom.exe", MCPCOM_SHA256)):
        got = sha256(os.path.join(bindir, name))
        print("%-11s %s %s" % (name, got, "ok" if got == want else "UNEXPECTED"))
    print("extracted to", out)


if __name__ == "__main__":
    main()
