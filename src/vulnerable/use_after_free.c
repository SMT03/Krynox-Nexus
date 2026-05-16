/*
 * use_after_free.c - Intentionally Vulnerable Kernel Module
 * 
 * WARNING: This module contains INTENTIONAL security vulnerabilities
 * for testing the Krynox Nexus security pipeline.
 * 
 * NEVER use this code in production!
 * 
 * Vulnerabilities demonstrated:
 * - Use-after-free (CWE-416)
 * - Double-free (CWE-415)
 * - Memory leak (CWE-401)
 * 
 * Part of Krynox Nexus - Zero-Trust Kernel Module Hardening
 */

#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/slab.h>
#include <linux/proc_fs.h>
#include <linux/uaccess.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Krynox Nexus Security Team");
MODULE_DESCRIPTION("Intentionally Vulnerable Module - Use After Free");
MODULE_VERSION("1.0");

#define PROC_NAME "vulnerable_uaf"

struct user_data {
    char *name;
    int id;
    void (*callback)(struct user_data *);
};

static struct proc_dir_entry *proc_entry;
static struct user_data *global_data = NULL;

/*
 * VULNERABILITY 1: Use-after-free
 * Frees memory but continues to use the pointer
 */
static void vulnerable_use_after_free(void)
{
    struct user_data *data;
    
    data = kmalloc(sizeof(struct user_data), GFP_KERNEL);
    if (!data) {
        pr_err("vulnerable_uaf: Allocation failed\n");
        return;
    }
    
    data->name = kmalloc(64, GFP_KERNEL);
    if (!data->name) {
        kfree(data);
        return;
    }
    
    strcpy(data->name, "Test User");
    data->id = 1234;
    
    pr_info("vulnerable_uaf: Created user: %s (ID: %d)\n", data->name, data->id);
    
    /* Free the memory */
    kfree(data->name);
    kfree(data);
    
    /* VULNERABLE: Use after free! */
    pr_info("vulnerable_uaf: Accessing freed memory: %s (ID: %d)\n",
            data->name, data->id);
    
    /* VULNERABLE: Writing to freed memory! */
    data->id = 5678;
}

/*
 * VULNERABILITY 2: Double-free
 * Frees the same memory twice
 */
static void vulnerable_double_free(void)
{
    char *buffer;
    
    buffer = kmalloc(128, GFP_KERNEL);
    if (!buffer) {
        pr_err("vulnerable_uaf: Allocation failed\n");
        return;
    }
    
    strcpy(buffer, "This will be freed twice");
    pr_info("vulnerable_uaf: Buffer content: %s\n", buffer);
    
    /* First free */
    kfree(buffer);
    pr_info("vulnerable_uaf: Buffer freed once\n");
    
    /* VULNERABLE: Double free! */
    kfree(buffer);
    pr_info("vulnerable_uaf: Buffer freed twice (VULNERABLE!)\n");
}

/*
 * VULNERABILITY 3: Dangling pointer
 * Keeps reference to freed memory
 */
static void vulnerable_dangling_pointer(void)
{
    if (global_data) {
        kfree(global_data->name);
        kfree(global_data);
        /* VULNERABLE: Doesn't set to NULL, creating dangling pointer */
    }
    
    global_data = kmalloc(sizeof(struct user_data), GFP_KERNEL);
    if (!global_data) {
        return;
    }
    
    global_data->name = kmalloc(64, GFP_KERNEL);
    if (!global_data->name) {
        kfree(global_data);
        return;
    }
    
    strcpy(global_data->name, "Global User");
    global_data->id = 9999;
    
    pr_info("vulnerable_uaf: Global data set: %s (ID: %d)\n",
            global_data->name, global_data->id);
}

/*
 * VULNERABILITY 4: Memory leak
 * Allocates memory but never frees it
 */
static void vulnerable_memory_leak(void)
{
    char *leaked_buffer;
    int i;
    
    for (i = 0; i < 10; i++) {
        leaked_buffer = kmalloc(1024, GFP_KERNEL);
        if (leaked_buffer) {
            sprintf(leaked_buffer, "Leaked buffer %d", i);
            /* VULNERABLE: Never freed! */
        }
    }
    
    pr_info("vulnerable_uaf: Leaked 10KB of memory\n");
}

/*
 * Proc file write handler
 */
static ssize_t proc_write(struct file *file, const char __user *buffer,
                         size_t count, loff_t *pos)
{
    char cmd;
    
    if (count < 1) {
        return -EINVAL;
    }
    
    if (copy_from_user(&cmd, buffer, 1)) {
        return -EFAULT;
    }
    
    switch (cmd) {
    case '1':
        pr_info("vulnerable_uaf: Triggering use-after-free\n");
        vulnerable_use_after_free();
        break;
    case '2':
        pr_info("vulnerable_uaf: Triggering double-free\n");
        vulnerable_double_free();
        break;
    case '3':
        pr_info("vulnerable_uaf: Triggering dangling pointer\n");
        vulnerable_dangling_pointer();
        break;
    case '4':
        pr_info("vulnerable_uaf: Triggering memory leak\n");
        vulnerable_memory_leak();
        break;
    default:
        pr_info("vulnerable_uaf: Unknown command. Use 1-4\n");
        break;
    }
    
    return count;
}

static const struct proc_ops proc_fops = {
    .proc_write = proc_write,
};

static int __init use_after_free_init(void)
{
    pr_warn("vulnerable_uaf: Loading INTENTIONALLY VULNERABLE module\n");
    pr_warn("vulnerable_uaf: DO NOT USE IN PRODUCTION!\n");
    
    proc_entry = proc_create(PROC_NAME, 0666, NULL, &proc_fops);
    if (!proc_entry) {
        pr_err("vulnerable_uaf: Failed to create proc entry\n");
        return -ENOMEM;
    }
    
    pr_info("vulnerable_uaf: Module loaded\n");
    pr_info("vulnerable_uaf: Write 1-4 to /proc/%s to trigger vulnerabilities\n",
            PROC_NAME);
    
    return 0;
}

static void __exit use_after_free_exit(void)
{
    if (proc_entry) {
        proc_remove(proc_entry);
    }
    
    /* VULNERABLE: Not cleaning up global_data if allocated */
    
    pr_info("vulnerable_uaf: Module unloaded\n");
}

module_init(use_after_free_init);
module_exit(use_after_free_exit);

