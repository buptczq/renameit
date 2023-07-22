#!/usr/bin/env python
import subprocess
import argparse
import os
from subprocess import check_output

AR_PATH = "ar"
NM_PATH = "nm"
OBJCOPY_PATH = "objcopy"

class StaticLib(object):
    def __init__(self, filename, tmpdir):
        self.filename = os.path.basename(filename)
        self.objdir = os.path.join(tmpdir, self.filename)
        self.renamed_objdir = os.path.join(tmpdir, "renamed_" + self.filename)

        try:
            os.makedirs(self.objdir)
            os.makedirs(self.renamed_objdir)
        except OSError:
            pass

        subprocess.check_call([AR_PATH, "x", os.path.realpath(filename)], cwd=self.objdir)
        self.objects = [obj for obj in os.listdir(self.objdir)]
        self.__load_symbols()

    def __load_symbols(self):
        self.symbols = set()
        for obj in self.objects:
            obj = os.path.join(self.objdir, obj)
            symbols = subprocess.check_output([NM_PATH, "--defined-only", obj])
            for line in symbols.splitlines():
                line = line.split()
                # If lowercase, the symbol is usually local; if uppercase, the symbol is global (external).
                if line[1].isupper():
                    self.symbols.add(line[2])

    def rename(self, mapping_file):
        for obj in self.objects:
            subprocess.check_call([
                OBJCOPY_PATH,
                "--redefine-syms=%s" % (mapping_file),
                os.path.join(self.objdir, obj),
                os.path.join(self.renamed_objdir, obj)
            ])

    def get_renamed_objects(self):
        return [os.path.join(self.renamed_objdir, obj) for obj in self.objects]

def pack_static_lib(filename, libs):
    try:
        os.unlink(filename)
    except OSError:
        pass
    objects = []
    for lib in libs:
        objects += lib.get_renamed_objects()
    subprocess.check_call(
            [AR_PATH, "qsc", filename] + objects)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Rename symbols in static libraries')
    parser.add_argument("--export", action="store", help="file of global symbols list", required=True)
    parser.add_argument("--custom", action="store", help="custom mapping file")
    parser.add_argument("--lib", dest="libs", action="append", help="input static libraries")
    parser.add_argument("--output", action="store", help="output static librarie", required=True)
    parser.add_argument("--prefix", action="store", help="prefix of new symbols", default="rename")
    parser.add_argument("--tmp", action="store", help="tmpdir ", default="rename_libs")
    parser.add_argument("--ar", action="store", help="ar tool", default=AR_PATH)
    parser.add_argument("--nm", action="store", help="nm tool", default=NM_PATH)
    parser.add_argument("--objcopy", action="store", help="objcopy tool", default=OBJCOPY_PATH)
    args = parser.parse_args()

    tmpdir = args.tmp
    prefix = args.prefix
    output = args.output
    AR_PATH = args.ar
    NM_PATH = args.nm
    OBJCOPY_PATH = args.objcopy

    export_symbols = set()
    custom_symbols = set()
    custom_mapping = {}
    for line in open(args.export, "r"):
        export_symbols.add(line.strip().replace('\n', ''))
    if args.custom:
        for line in open(args.custom, "r"):
            line = line.split()
            custom_mapping[line[0]] = line[1].strip().replace('\n', '')
            custom_symbols.add(line[0])

    libs = [StaticLib(lib, tmpdir) for lib in args.libs]
    all_symbols = set()
    for lib in libs:
        print "Load", lib.filename
        all_symbols.update(lib.symbols)
    mapping_file = os.path.join(tmpdir, "rename.ld")
    with open(mapping_file, "wt") as fo:
        for symbol in sorted(all_symbols - export_symbols - custom_symbols):
            rule = "%s %s_%s" % (symbol, prefix, symbol)
            print "Rename", rule
            fo.write(rule)
            fo.write("\n")
        for symbol in custom_mapping:
            rule = "%s %s" % (symbol, custom_mapping[symbol])
            print "Rename", rule
            fo.write(rule)
            fo.write("\n")
    for lib in libs:
        lib.rename(mapping_file)
    print "Pack renamed libraries to", output
    pack_static_lib(output, libs)

