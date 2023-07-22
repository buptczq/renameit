
int private_func();

extern int global_var;

void public_func() {
    global_var = private_func();
}
