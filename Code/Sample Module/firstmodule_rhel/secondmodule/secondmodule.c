/* Second Module that uses the exported symbols*/
#include <linux/module.h>
#include <linux/init.h>

extern void print_hello(int);
extern void add_two_numbers(int, int);
extern int JUST_A_TEST_VARIABLE;

/*
 * The function has been written just to call the functions which are in other module. This way you can also write modules which does provide some functionality to the other modules.
 */
void justprintthetwo(int p)
{
	printk(KERN_ALERT "Hello from Hello Module");
    print_hello(p);
    add_two_numbers(p, 6);
    printk(KERN_ALERT "This is the exported variable's value %d",JUST_A_TEST_VARIABLE);

}

static int __init my_init(void)
{
    justprintthetwo(6);
    return 0;
}

static void __exit my_exit(void)
{
    printk(KERN_ALERT "Bye from Hello Module");
}

module_init(my_init);
module_exit(my_exit);

MODULE_DESCRIPTION("Usinng the exported symbols");
MODULE_AUTHOR("Reuben Varghese <rvarghes@redhat.com>");
MODULE_LICENSE("GPL v2");