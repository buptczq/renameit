#!/bin/sh
set -e
./build.sh
../../renameit.py --lib ./private.a --lib ./public.a --output libpublic.a --export test.ld
gcc test.c -L. -lpublic -o test
./test
echo "PASS"

