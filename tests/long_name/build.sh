#!/bin/sh
rm -f *.o
rm -f *.a
gcc -fPIC -c ./*.c
ar -rcs private.a long_long_long_long_library.o long_long_long_long_library2.o
ar -rcs public.a public.o

