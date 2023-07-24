#!/bin/sh
rm -f *.o
rm -f *.a
gcc -fPIC -c ./*.c
ar -rcs private.a private.o
ar -rcs public.a public.o

