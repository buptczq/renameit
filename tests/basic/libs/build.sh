#!/bin/sh
rm -f *.o
rm -f *.a
gcc -fPIC -c ./*.c
ar -rc private.a private.o
ar -rc public.a public.o
ar -rc public2.a public2.o

