#!/bin/sh
set -e
cd libs
./build.sh
cd ..
../renameit.py --lib ./libs/public.a --lib ./libs/private.a --output libpublic.a --export test.ld --custom custom.map
../renameit.py --lib ./libs/public2.a --lib ./libs/private.a --output libpublic2.a --export test.ld --prefix pub2
gcc test.c -L. -lpublic -lpublic2 -o test
./test
echo "PASS"

