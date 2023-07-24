__asm__(".symver old_private_func,private_func@@V1");
__asm__(".symver new_private_func,private_func@V2");
int old_private_func() {
    return 1;
}
int new_private_func() {
    return 2;
}
