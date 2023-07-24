extern int global_var;
int private_func();

__asm__(".symver old_public_func,public_func@@V1");
__asm__(".symver new_public_func,public_func@V2");

void old_public_func() {
    global_var = private_func();
}

void new_public_func() {
    global_var = 0;
}
