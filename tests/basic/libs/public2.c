
int private_func();

extern int global_var;

void public2_func() {
    global_var = private_func();
}
