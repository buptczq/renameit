#!/usr/bin/env python
import subprocess
import argparse
import os
from io import SEEK_CUR
from subprocess import check_output

AR_PATH = "ar"
NM_PATH = "nm"
OBJCOPY_PATH = "objcopy"

AR_FILE_NAME_SIZE = 16
AR_SIZE_OFFSET = 32
AR_SIZE_SIZE = 10
AR_FILE_START_OFFSET = 2

USE_AR_EXTRACT = False

# https://man.freebsd.org/cgi/man.cgi?query=ar&sektion=5&apropos=0&manpath=FreeBSD+13.0-RELEASE+and+Ports
def extract_archive(archive_path, destination_path):
    print "extract", archive_path
    archive = open(archive_path, 'rb')

    global_header = archive.read(8)
    if global_header != '!<arch>\n':
        print(archive_path + ' seems not to be an archive file!')
        exit(1)

    processed_files = dict()
    namelist = ""

    count = 0
    while True:
        count = count + 1
        ar_file_name_bytes = archive.read(AR_FILE_NAME_SIZE)
        if len(ar_file_name_bytes) == 0:
            break
        ar_file_name_raw = ar_file_name_bytes.rstrip(' ').decode()
        archive.seek(AR_SIZE_OFFSET, SEEK_CUR)
        ar_file_size = int(archive.read(AR_SIZE_SIZE).rstrip(' ').decode())
        if ar_file_name_raw.startswith('#1/'):
            file_name_size = int(ar_file_name_raw.replace('#1/', ''))
            ar_file_size = ar_file_size - file_name_size
            archive.seek(AR_FILE_START_OFFSET, SEEK_CUR)
            ar_file_name = archive.read(file_name_size).rstrip(b'\x00').decode()
        else:
            ar_file_name = ar_file_name_raw.decode()
            archive.seek(AR_FILE_START_OFFSET, SEEK_CUR)
        new_file_name = ""
        if ar_file_name in ['/', '__.SYMDEF', '__.SYMDEF_64']:
            # symbol lookup table
            ar_file_name = ""
        elif ar_file_name == '//':
            # extended filenames
            pass
        else:
            if ar_file_name.startswith('/'):
                idx = int(ar_file_name[1:])
                if idx < len(namelist):
                    ar_file_name = namelist[idx:].split('\n')[0]
            # System V ar uses a '/' character (0x2F) to mark the end of the filename
            ar_file_name = os.path.normpath(ar_file_name.split('/')[0])
            if ar_file_name in processed_files:
                filename, ext = os.path.splitext(ar_file_name)
                new_file_name = "%s_%d%s" % (filename, processed_files[ar_file_name] + 1, ext)
                processed_files[ar_file_name] = processed_files[ar_file_name] + 1
            else:
                new_file_name = ar_file_name
                processed_files[ar_file_name] = 1

        if ar_file_name == '//':
            namelist = archive.read(ar_file_size)
        elif new_file_name:
            print new_file_name
            with open(os.path.join(destination_path, new_file_name), 'wb') as out:
                out.write(archive.read(ar_file_size))
        else:
            archive.seek(ar_file_size, SEEK_CUR)

        if archive.tell() % 2 == 1:
            archive.read(1)

    archive.close()

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

        if USE_AR_EXTRACT:
            subprocess.check_call([AR_PATH, "x", os.path.realpath(filename)], cwd=self.objdir)
        else:
            extract_archive(os.path.realpath(filename), self.objdir)

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
        for sym in lib.symbols:
            if '@@' in sym:
                # default definition
                realname = sym.split('@@')[0]
                if realname not in export_symbols:
                    all_symbols.add(realname)
                    all_symbols.add(sym)
            elif '@' in sym:
                # default definition
                realname = sym.split('@')[0]
                if realname not in export_symbols:
                    all_symbols.add(sym)
            else:
                all_symbols.add(sym)
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

