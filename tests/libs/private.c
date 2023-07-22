#include<stdlib.h>

const int private_const = 1;

static int private_static_var;
int private_var;
__thread int private_tls;

static int private_static_func() {
    if (private_static_var) {
        abort();
    }
    private_var = private_const;
    private_static_var = private_const;
    private_tls = private_const;
    return private_tls;
}

int private_func() {
    return private_static_func();
}
