#include <stdio.h>
#include <stdlib.h>

int global_var = 0;
void public_func();

int main () {
    public_func();
    if (global_var != 1) {
        abort();
    }
    return 0;
}

