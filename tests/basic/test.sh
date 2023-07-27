#!/bin/sh
set -e
cd libs
./build.sh
cd ..
../../renameit.py --output libpublic.a --export test.ld --custom custom.map ./libs/public.a ./libs/private.a
../../renameit.py --output libpublic2.a --export test.ld --prefix pub2 ./libs/public2.a ./libs/private.a
gcc test.c -L. -lpublic -lpublic2 -o test
./test
echo "PASS"

