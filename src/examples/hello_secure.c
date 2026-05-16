/*
 * hello_secure.c - Secure "Hello World" Kernel Module
 * 
 * This module demonstrates secure kernel module development practices:
 * - Proper error handling
 * - Bounds checking
 * - Safe memory operations
 * - Correct module lifecycle management
 * 
 * Part of Krynox Nexus - Zero-Trust Kernel Module Hardening
 */

#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/slab.h>
#include <linux/string.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Krynox Nexus Security Team");
MODULE_DESCRIPTION("Secure Hello World Kernel Module");
MODULE_VERSION("1.0");

#define MAX_MESSAGE_LEN 256

static char *message = NULL;

/*
 * Secure string copy with bounds checking
 */
static int secure_copy_message(const char *src, size_t max_len)
{
    size_t len;
    
    if (!src) {
        pr_err("hello_secure: NULL source pointer\n");
        return -EINVAL;
    }
    
    len = strnlen(src, max_len);
    if (len >= max_len) {
        pr_err("hello_secure: Message too long\n");
        return -EINVAL;
    }
    
    message = kzalloc(len + 1, GFP_KERNEL);
    if (!message) {
        pr_err("hello_secure: Memory allocation failed\n");
        return -ENOMEM;
    }
    
    strncpy(message, src, len);
    message[len] = '\0';  /* Ensure null termination */
    
    return 0;
}

static int __init hello_secure_init(void)
{
    int ret;
    const char *greeting = "Hello from Krynox Nexus - Secure Kernel Module!";
    
    pr_info("hello_secure: Initializing secure module\n");
    
    ret = secure_copy_message(greeting, MAX_MESSAGE_LEN);
    if (ret) {
        pr_err("hello_secure: Failed to initialize message\n");
        return ret;
    }
    
    pr_info("hello_secure: %s\n", message);
    pr_info("hello_secure: Module loaded successfully\n");
    
    return 0;
}

static void __exit hello_secure_exit(void)
{
    pr_info("hello_secure: Cleaning up module\n");
    
    if (message) {
        /* Secure cleanup - zero memory before freeing */
        memset(message, 0, strlen(message));
        kfree(message);
        message = NULL;
    }
    
    pr_info("hello_secure: Module unloaded successfully\n");
}

module_init(hello_secure_init);
module_exit(hello_secure_exit);

// Made with Bob
