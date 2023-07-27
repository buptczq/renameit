#!/bin/sh
set -e
./build.sh
../../renameit.py --output libpublic.a --export test.ld ./private.a ./public.a
gcc test.c -L. -lpublic -o test
./test
echo "PASS"

