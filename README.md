# Rename symbols in static libraries

```
usage: renameit.py [-h] --export EXPORT [--custom CUSTOM] [--lib LIBS]
                   --output OUTPUT [--prefix PREFIX] [--tmp TMP] [--ar AR]
                   [--nm NM] [--objcopy OBJCOPY]

optional arguments:
  -h, --help         show this help message and exit
  --export EXPORT    file of global symbols list
  --custom CUSTOM    custom mapping file
  --lib LIBS         input static libraries
  --output OUTPUT    output static librarie
  --prefix PREFIX    prefix of new symbols
  --tmp TMP          tmpdir
  --ar AR            ar tool
  --nm NM            nm tool
  --objcopy OBJCOPY  objcopy tool

```

