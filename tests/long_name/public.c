
int private_func();
int private2_func();

extern int global_var;

void public_func() {
    global_var = private_func();
    private2_func();
}
