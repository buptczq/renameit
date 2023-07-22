#include <stdio.h>

int global_var = 0;
void public_func();
void public2_func();

int main () {
    public_func();
    public2_func();
    return 0;
}

