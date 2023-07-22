#!/bin/sh
rm -f *.o
rm -f *.a
gcc -fPIC -c ./*.c
cd private1
gcc -fPIC -c ./*.c
cd ..
cd private2
gcc -fPIC -c ./*.c
cd ..
ar -rcs private.a ./private1/private.o ./private2/private.o
ar -rcs public.a public.o

