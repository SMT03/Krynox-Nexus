/*
 * buffer_overflow.c - Intentionally Vulnerable Kernel Module
 * 
 * WARNING: This module contains INTENTIONAL security vulnerabilities
 * for testing the Krynox Nexus security pipeline.
 * 
 * NEVER use this code in production!
 * 
 * Vulnerabilities demonstrated:
 * - Stack buffer overflow (CWE-121)
 * - Unbounded string copy (CWE-120)
 * - Missing bounds checking (CWE-119)
 * 
 * Part of Krynox Nexus - Zero-Trust Kernel Module Hardening
 */

#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/proc_fs.h>
#include <linux/uaccess.h>
#include <linux/slab.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Krynox Nexus Security Team");
MODULE_DESCRIPTION("Intentionally Vulnerable Module - Buffer Overflow");
MODULE_VERSION("1.0");

#define PROC_NAME "vulnerable_buffer"
#define SMALL_BUFFER_SIZE 32

static struct proc_dir_entry *proc_entry;

/*
 * VULNERABILITY 1: Stack buffer overflow
 * The buffer is only 32 bytes but we copy without checking length
 */
static void vulnerable_stack_overflow(const char *user_input)
{
    char small_buffer[SMALL_BUFFER_SIZE];
    
    /* VULNERABLE: No bounds checking! */
    strcpy(small_buffer, user_input);
    
    pr_info("vulnerable_buffer: Copied %zu bytes to %d byte buffer\n",
            strlen(user_input), SMALL_BUFFER_SIZE);
}

/*
 * VULNERABILITY 2: Heap buffer overflow
 * Allocates fixed size but copies without validation
 */
static void vulnerable_heap_overflow(const char *user_input, size_t len)
{
    char *heap_buffer;
    
    heap_buffer = kmalloc(SMALL_BUFFER_SIZE, GFP_KERNEL);
    if (!heap_buffer) {
        pr_err("vulnerable_buffer: Memory allocation failed\n");
        return;
    }
    
    /* VULNERABLE: Copies 'len' bytes without checking buffer size! */
    memcpy(heap_buffer, user_input, len);
    
    pr_info("vulnerable_buffer: Copied %zu bytes to heap buffer\n", len);
    
    kfree(heap_buffer);
}

/*
 * VULNERABILITY 3: Format string vulnerability
 */
static void vulnerable_format_string(const char *user_input)
{
    /* VULNERABLE: User input directly in format string! */
    pr_info(user_input);
}

/*
 * Proc file write handler - entry point for vulnerabilities
 */
static ssize_t proc_write(struct file *file, const char __user *buffer,
                         size_t count, loff_t *pos)
{
    char *kernel_buffer;
    
    if (count > PAGE_SIZE) {
        return -EINVAL;
    }
    
    kernel_buffer = kmalloc(count + 1, GFP_KERNEL);
    if (!kernel_buffer) {
        return -ENOMEM;
    }
    
    if (copy_from_user(kernel_buffer, buffer, count)) {
        kfree(kernel_buffer);
        return -EFAULT;
    }
    
    kernel_buffer[count] = '\0';
    
    /* Trigger vulnerabilities */
    vulnerable_stack_overflow(kernel_buffer);
    vulnerable_heap_overflow(kernel_buffer, count);
    vulnerable_format_string(kernel_buffer);
    
    kfree(kernel_buffer);
    return count;
}

static const struct proc_ops proc_fops = {
    .proc_write = proc_write,
};

static int __init buffer_overflow_init(void)
{
    pr_warn("vulnerable_buffer: Loading INTENTIONALLY VULNERABLE module\n");
    pr_warn("vulnerable_buffer: DO NOT USE IN PRODUCTION!\n");
    
    proc_entry = proc_create(PROC_NAME, 0666, NULL, &proc_fops);
    if (!proc_entry) {
        pr_err("vulnerable_buffer: Failed to create proc entry\n");
        return -ENOMEM;
    }
    
    pr_info("vulnerable_buffer: Module loaded - write to /proc/%s to trigger vulnerabilities\n",
            PROC_NAME);
    
    return 0;
}

static void __exit buffer_overflow_exit(void)
{
    if (proc_entry) {
        proc_remove(proc_entry);
    }
    
    pr_info("vulnerable_buffer: Module unloaded\n");
}

module_init(buffer_overflow_init);
module_exit(buffer_overflow_exit);

// Made with Bob
