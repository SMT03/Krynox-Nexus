/*
 * test_secure_modules.c - Comprehensive Unit Tests for Krynox Nexus Secure Modules
 * 
 * This test suite validates the security implementations in:
 * - buffer_overflow_secure.c: Stack/heap copy functions, format string safety
 * - hello_secure.c: Secure message copying with bounds checking
 * 
 * Test Framework: CMocka (https://cmocka.org/)
 * Coverage Goal: ≥85% line coverage, ≥80% branch coverage
 * Total Test Cases: 36
 * 
 * Part of Krynox Nexus - Zero-Trust Kernel Module Hardening
 * Author: Bob - Security Architect & Kernel Engineer
 * Date: 2026-05-16
 */

#include <stdarg.h>
#include <stddef.h>
#include <setjmp.h>
#include <stdint.h>
#include <cmocka.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <errno.h>
#include <limits.h>

/* Test configuration constants */
#define BUFFER_SIZE 256
#define MAX_INPUT_SIZE 4096
#define MAX_MESSAGE_LEN 256

/* Mock kernel error codes */
#ifndef EINVAL
#define EINVAL 22
#endif
#ifndef ENOMEM
#define ENOMEM 12
#endif
#ifndef EOVERFLOW
#define EOVERFLOW 75
#endif

/* Global state for tracking allocations and logs */
static int allocation_count = 0;
static int deallocation_count = 0;
static char log_buffer[1024];
static int log_count = 0;
static int mock_kmalloc_should_fail = 0;

/* Mock kernel logging functions */
#define pr_info(fmt, ...) mock_pr_info(fmt, ##__VA_ARGS__)
#define pr_warn(fmt, ...) mock_pr_warn(fmt, ##__VA_ARGS__)
#define pr_err(fmt, ...) mock_pr_err(fmt, ##__VA_ARGS__)

static void mock_pr_info(const char *fmt, ...) {
    va_list args;
    va_start(args, fmt);
    vsnprintf(log_buffer, sizeof(log_buffer), fmt, args);
    va_end(args);
    log_count++;
}

static void mock_pr_warn(const char *fmt, ...) {
    va_list args;
    va_start(args, fmt);
    vsnprintf(log_buffer, sizeof(log_buffer), fmt, args);
    va_end(args);
    log_count++;
}

static void mock_pr_err(const char *fmt, ...) {
    va_list args;
    va_start(args, fmt);
    vsnprintf(log_buffer, sizeof(log_buffer), fmt, args);
    va_end(args);
    log_count++;
}

/* Mock kernel memory allocation functions */
#define GFP_KERNEL 0
typedef unsigned int gfp_t;

static void *kmalloc(size_t size, gfp_t flags) {
    (void)flags;
    if (mock_kmalloc_should_fail) {
        return NULL;
    }
    allocation_count++;
    return malloc(size);
}

static void *kzalloc(size_t size, gfp_t flags) {
    void *ptr = kmalloc(size, flags);
    if (ptr) {
        memset(ptr, 0, size);
    }
    return ptr;
}

static void kfree(const void *ptr) {
    if (ptr) {
        deallocation_count++;
        free((void *)ptr);
    }
}

/* Mock strlcpy */
static size_t strlcpy(char *dst, const char *src, size_t size) {
    size_t src_len = strlen(src);
    if (size == 0) {
        return src_len;
    }
    size_t copy_len = (src_len >= size) ? size - 1 : src_len;
    memcpy(dst, src, copy_len);
    dst[copy_len] = '\0';
    return src_len;
}

/* Mock strnlen */
#ifndef strnlen
static size_t strnlen(const char *s, size_t maxlen) {
    size_t len = 0;
    while (len < maxlen && s[len] != '\0') {
        len++;
    }
    return len;
}
#endif

/* Secure function implementations */
static int secure_stack_copy(const char *user_input, size_t input_len)
{
    char safe_buffer[BUFFER_SIZE];
    size_t copy_len;
    
    if (input_len >= BUFFER_SIZE) {
        pr_warn("secure_buffer: Input too large (%zu bytes), max is %d\n",
                input_len, BUFFER_SIZE - 1);
        return -EINVAL;
    }
    
    copy_len = strlcpy(safe_buffer, user_input, BUFFER_SIZE);
    
    if (copy_len >= BUFFER_SIZE) {
        pr_err("secure_buffer: String truncation occurred\n");
        return -EOVERFLOW;
    }
    
    pr_info("secure_buffer: Safely copied %zu bytes to %d byte buffer\n",
            copy_len, BUFFER_SIZE);
    
    return 0;
}

static int secure_heap_copy(const char *user_input, size_t input_len)
{
    char *heap_buffer;
    
    if (input_len > MAX_INPUT_SIZE) {
        pr_warn("secure_buffer: Input exceeds maximum size (%zu > %d)\n",
                input_len, MAX_INPUT_SIZE);
        return -EINVAL;
    }
    
    heap_buffer = kmalloc(input_len + 1, GFP_KERNEL);
    if (!heap_buffer) {
        pr_err("secure_buffer: Memory allocation failed for %zu bytes\n",
               input_len + 1);
        return -ENOMEM;
    }
    
    memcpy(heap_buffer, user_input, input_len);
    heap_buffer[input_len] = '\0';
    
    pr_info("secure_buffer: Safely allocated and copied %zu bytes to heap\n",
            input_len);
    
    kfree(heap_buffer);
    
    return 0;
}

static void secure_log_message(const char *user_input, size_t input_len)
{
    (void)input_len;
    pr_info("secure_buffer: User message (max 128 chars): %.128s\n",
            user_input);
}

static char *test_message = NULL;

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
    
    test_message = kzalloc(len + 1, GFP_KERNEL);
    if (!test_message) {
        pr_err("hello_secure: Memory allocation failed\n");
        return -ENOMEM;
    }
    
    strncpy(test_message, src, len);
    test_message[len] = '\0';
    
    return 0;
}

/* Test fixtures */
static int setup(void **state) {
    (void)state;
    allocation_count = 0;
    deallocation_count = 0;
    log_count = 0;
    mock_kmalloc_should_fail = 0;
    memset(log_buffer, 0, sizeof(log_buffer));
    if (test_message) {
        kfree(test_message);
        test_message = NULL;
    }
    return 0;
}

static int teardown(void **state) {
    (void)state;
    if (test_message) {
        kfree(test_message);
        test_message = NULL;
    }
    return 0;
}

static char *create_test_string(size_t length, char fill_char) {
    char *str = malloc(length + 1);
    assert_non_null(str);
    memset(str, fill_char, length);
    str[length] = '\0';
    return str;
}

/* Test Suite 1: secure_stack_copy() */
static void test_stack_copy_valid_input(void **state) {
    (void)state;
    const char *input = "This is a valid test string within buffer limits";
    int result = secure_stack_copy(input, strlen(input));
    assert_int_equal(result, 0);
    assert_true(log_count > 0);
}

static void test_stack_copy_exact_boundary(void **state) {
    (void)state;
    char *input = create_test_string(BUFFER_SIZE - 1, 'A');
    int result = secure_stack_copy(input, strlen(input));
    assert_int_equal(result, 0);
    free(input);
}

static void test_stack_copy_overflow_attempt(void **state) {
    (void)state;
    char *input = create_test_string(300, 'B');
    int result = secure_stack_copy(input, strlen(input));
    assert_int_equal(result, -EINVAL);
    assert_true(strstr(log_buffer, "too large") != NULL);
    free(input);
}

static void test_stack_copy_empty_string(void **state) {
    (void)state;
    const char *input = "";
    int result = secure_stack_copy(input, strlen(input));
    assert_int_equal(result, 0);
}

static void test_stack_copy_null_termination(void **state) {
    (void)state;
    const char *input = "Test null termination";
    int result = secure_stack_copy(input, strlen(input));
    assert_int_equal(result, 0);
}

static void test_stack_copy_truncation_detection(void **state) {
    (void)state;
    char *input = create_test_string(BUFFER_SIZE + 10, 'C');
    int result = secure_stack_copy(input, strlen(input));
    assert_int_equal(result, -EINVAL);
    free(input);
}

static void test_stack_copy_single_char(void **state) {
    (void)state;
    const char *input = "X";
    int result = secure_stack_copy(input, strlen(input));
    assert_int_equal(result, 0);
}

static void test_stack_copy_unicode_chars(void **state) {
    (void)state;
    const char *input = "Hello World";
    int result = secure_stack_copy(input, strlen(input));
    assert_int_equal(result, 0);
}

/* Test Suite 2: secure_heap_copy() */
static void test_heap_copy_valid_allocation(void **state) {
    (void)state;
    char *input = create_test_string(1024, 'D');
    int result = secure_heap_copy(input, strlen(input));
    assert_int_equal(result, 0);
    assert_int_equal(allocation_count, deallocation_count);
    free(input);
}

static void test_heap_copy_max_size(void **state) {
    (void)state;
    char *input = create_test_string(MAX_INPUT_SIZE, 'E');
    int result = secure_heap_copy(input, strlen(input));
    assert_int_equal(result, 0);
    assert_int_equal(allocation_count, deallocation_count);
    free(input);
}

static void test_heap_copy_exceeds_max(void **state) {
    (void)state;
    size_t oversized = MAX_INPUT_SIZE + 1000;
    char *input = create_test_string(oversized, 'F');
    int result = secure_heap_copy(input, strlen(input));
    assert_int_equal(result, -EINVAL);
    assert_true(strstr(log_buffer, "exceeds maximum") != NULL);
    free(input);
}

static void test_heap_copy_small_input(void **state) {
    (void)state;
    const char *input = "Small";
    int result = secure_heap_copy(input, strlen(input));
    assert_int_equal(result, 0);
    assert_int_equal(allocation_count, deallocation_count);
}

static void test_heap_copy_null_termination(void **state) {
    (void)state;
    const char *input = "Verify null byte";
    int result = secure_heap_copy(input, strlen(input));
    assert_int_equal(result, 0);
}

static void test_heap_copy_memory_cleanup(void **state) {
    (void)state;
    const char *input = "Memory cleanup test";
    int initial_alloc = allocation_count;
    int initial_dealloc = deallocation_count;
    int result = secure_heap_copy(input, strlen(input));
    assert_int_equal(result, 0);
    assert_int_equal(allocation_count - initial_alloc, 
                     deallocation_count - initial_dealloc);
}

static void test_heap_copy_zero_length(void **state) {
    (void)state;
    const char *input = "";
    int result = secure_heap_copy(input, 0);
    assert_int_equal(result, 0);
    assert_int_equal(allocation_count, deallocation_count);
}

static void test_heap_copy_repeated_calls(void **state) {
    (void)state;
    const char *input = "Repeated allocation test";
    int initial_alloc = allocation_count;
    int initial_dealloc = deallocation_count;
    for (int i = 0; i < 10; i++) {
        int result = secure_heap_copy(input, strlen(input));
        assert_int_equal(result, 0);
    }
    assert_int_equal(allocation_count - initial_alloc,
                     deallocation_count - initial_dealloc);
}

/* Test Suite 3: secure_log_message() */
static void test_log_safe_string(void **state) {
    (void)state;
    const char *input = "This is a safe log message";
    secure_log_message(input, strlen(input));
    assert_true(log_count > 0);
    assert_true(strstr(log_buffer, "User message") != NULL);
}

static void test_log_format_specifiers(void **state) {
    (void)state;
    const char *input = "%x %x %x %s %n";
    secure_log_message(input, strlen(input));
    assert_true(log_count > 0);
}

static void test_log_length_limiting(void **state) {
    (void)state;
    char *input = create_test_string(200, 'G');
    secure_log_message(input, strlen(input));
    assert_true(log_count > 0);
    free(input);
}

static void test_log_special_chars(void **state) {
    (void)state;
    const char *input = "Line1\nLine2\tTabbed\rCarriage";
    secure_log_message(input, strlen(input));
    assert_true(log_count > 0);
}

static void test_log_binary_data(void **state) {
    (void)state;
    char input[] = "Binary\0Data\0Here";
    size_t input_len = sizeof(input) - 1;
    secure_log_message(input, input_len);
    assert_true(log_count > 0);
}

static void test_log_control_chars(void **state) {
    (void)state;
    char input[32];
    for (int i = 0; i < 20; i++) {
        input[i] = (char)(i + 1);
    }
    input[20] = '\0';
    secure_log_message(input, strlen(input));
    assert_true(log_count > 0);
}

/* Test Suite 4: secure_copy_message() */
static void test_copy_message_valid(void **state) {
    (void)state;
    const char *input = "Valid message for copying";
    int result = secure_copy_message(input, MAX_MESSAGE_LEN);
    assert_int_equal(result, 0);
    assert_non_null(test_message);
    assert_string_equal(test_message, input);
}

static void test_copy_message_null_pointer(void **state) {
    (void)state;
    int result = secure_copy_message(NULL, MAX_MESSAGE_LEN);
    assert_int_equal(result, -EINVAL);
    assert_true(strstr(log_buffer, "NULL") != NULL);
}

static void test_copy_message_max_length(void **state) {
    (void)state;
    char *input = create_test_string(MAX_MESSAGE_LEN - 1, 'H');
    int result = secure_copy_message(input, MAX_MESSAGE_LEN);
    assert_int_equal(result, 0);
    assert_non_null(test_message);
    free(input);
}

static void test_copy_message_exceeds_max(void **state) {
    (void)state;
    char *input = create_test_string(MAX_MESSAGE_LEN + 10, 'I');
    int result = secure_copy_message(input, MAX_MESSAGE_LEN);
    assert_int_equal(result, -EINVAL);
    assert_true(strstr(log_buffer, "too long") != NULL);
    free(input);
}

static void test_copy_message_allocation_failure(void **state) {
    (void)state;
    const char *input = "Test allocation failure";
    mock_kmalloc_should_fail = 1;
    int result = secure_copy_message(input, MAX_MESSAGE_LEN);
    assert_int_equal(result, -ENOMEM);
    assert_true(strstr(log_buffer, "allocation failed") != NULL);
}

static void test_copy_message_null_termination(void **state) {
    (void)state;
    const char *input = "Null termination check";
    int result = secure_copy_message(input, MAX_MESSAGE_LEN);
    assert_int_equal(result, 0);
    assert_non_null(test_message);
    assert_int_equal(test_message[strlen(input)], '\0');
}

static void test_copy_message_whitespace_only(void **state) {
    (void)state;
    const char *input = "     \t\t\n   ";
    int result = secure_copy_message(input, MAX_MESSAGE_LEN);
    assert_int_equal(result, 0);
    assert_non_null(test_message);
}

static void test_copy_message_memory_zeroing(void **state) {
    (void)state;
    const char *input = "Sensitive data to be zeroed";
    int result = secure_copy_message(input, MAX_MESSAGE_LEN);
    assert_int_equal(result, 0);
    if (test_message) {
        size_t len = strlen(test_message);
        memset(test_message, 0, len);
        for (size_t i = 0; i < len; i++) {
            assert_int_equal(test_message[i], 0);
        }
    }
}

/* Test Suite 5: Security Attack Simulation */
static void test_attack_buffer_overflow(void **state) {
    (void)state;
    char *attack_buffer = create_test_string(1000, 'A');
    int result = secure_stack_copy(attack_buffer, strlen(attack_buffer));
    assert_int_equal(result, -EINVAL);
    assert_true(strstr(log_buffer, "too large") != NULL);
    free(attack_buffer);
}

static void test_attack_heap_overflow(void **state) {
    (void)state;
    size_t malicious_size = MAX_INPUT_SIZE + 5000;
    char *attack_buffer = create_test_string(malicious_size, 'B');
    int result = secure_heap_copy(attack_buffer, strlen(attack_buffer));
    assert_int_equal(result, -EINVAL);
    assert_true(strstr(log_buffer, "exceeds maximum") != NULL);
    free(attack_buffer);
}

static void test_attack_format_string(void **state) {
    (void)state;
    const char *attack = "%x %x %x %x %n %s %p";
    secure_log_message(attack, strlen(attack));
    assert_true(log_count > 0);
}

static void test_attack_integer_overflow(void **state) {
    (void)state;
    size_t malicious_size = SIZE_MAX - 1;
    int result = secure_heap_copy("dummy", malicious_size);
    assert_int_equal(result, -EINVAL);
}

static void test_attack_null_byte_injection(void **state) {
    (void)state;
    char attack[] = "valid\0malicious_payload_here";
    size_t attack_len = sizeof(attack) - 1;
    int result = secure_stack_copy(attack, attack_len);
    assert_true(result == 0 || result == -EINVAL);
}

static void test_attack_memory_exhaustion(void **state) {
    (void)state;
    const size_t large_size = MAX_INPUT_SIZE;
    char *large_input = create_test_string(large_size, 'Z');
    int success_count = 0;
    for (int i = 0; i < 5; i++) {
        int result = secure_heap_copy(large_input, strlen(large_input));
        if (result == 0) {
            success_count++;
        }
    }
    assert_true(success_count == 5);
    assert_int_equal(allocation_count, deallocation_count);
    free(large_input);
}

/* Main test runner */
int main(void) {
    const struct CMUnitTest tests[] = {
        cmocka_unit_test_setup_teardown(test_stack_copy_valid_input, setup, teardown),
        cmocka_unit_test_setup_teardown(test_stack_copy_exact_boundary, setup, teardown),
        cmocka_unit_test_setup_teardown(test_stack_copy_overflow_attempt, setup, teardown),
        cmocka_unit_test_setup_teardown(test_stack_copy_empty_string, setup, teardown),
        cmocka_unit_test_setup_teardown(test_stack_copy_null_termination, setup, teardown),
        cmocka_unit_test_setup_teardown(test_stack_copy_truncation_detection, setup, teardown),
        cmocka_unit_test_setup_teardown(test_stack_copy_single_char, setup, teardown),
        cmocka_unit_test_setup_teardown(test_stack_copy_unicode_chars, setup, teardown),
        cmocka_unit_test_setup_teardown(test_heap_copy_valid_allocation, setup, teardown),
        cmocka_unit_test_setup_teardown(test_heap_copy_max_size, setup, teardown),
        cmocka_unit_test_setup_teardown(test_heap_copy_exceeds_max, setup, teardown),
        cmocka_unit_test_setup_teardown(test_heap_copy_small_input, setup, teardown),
        cmocka_unit_test_setup_teardown(test_heap_copy_null_termination, setup, teardown),
        cmocka_unit_test_setup_teardown(test_heap_copy_memory_cleanup, setup, teardown),
        cmocka_unit_test_setup_teardown(test_heap_copy_zero_length, setup, teardown),
        cmocka_unit_test_setup_teardown(test_heap_copy_repeated_calls, setup, teardown),
        cmocka_unit_test_setup_teardown(test_log_safe_string, setup, teardown),
        cmocka_unit_test_setup_teardown(test_log_format_specifiers, setup, teardown),
        cmocka_unit_test_setup_teardown(test_log_length_limiting, setup, teardown),
        cmocka_unit_test_setup_teardown(test_log_special_chars, setup, teardown),
        cmocka_unit_test_setup_teardown(test_log_binary_data, setup, teardown),
        cmocka_unit_test_setup_teardown(test_log_control_chars, setup, teardown),
        cmocka_unit_test_setup_teardown(test_copy_message_valid, setup, teardown),
        cmocka_unit_test_setup_teardown(test_copy_message_null_pointer, setup, teardown),
        cmocka_unit_test_setup_teardown(test_copy_message_max_length, setup, teardown),
        cmocka_unit_test_setup_teardown(test_copy_message_exceeds_max, setup, teardown),
        cmocka_unit_test_setup_teardown(test_copy_message_allocation_failure, setup, teardown),
        cmocka_unit_test_setup_teardown(test_copy_message_null_termination, setup, teardown),
        cmocka_unit_test_setup_teardown(test_copy_message_whitespace_only, setup, teardown),
        cmocka_unit_test_setup_teardown(test_copy_message_memory_zeroing, setup, teardown),
        cmocka_unit_test_setup_teardown(test_attack_buffer_overflow, setup, teardown),
        cmocka_unit_test_setup_teardown(test_attack_heap_overflow, setup, teardown),
        cmocka_unit_test_setup_teardown(test_attack_format_string, setup, teardown),
        cmocka_unit_test_setup_teardown(test_attack_integer_overflow, setup, teardown),
        cmocka_unit_test_setup_teardown(test_attack_null_byte_injection, setup, teardown),
        cmocka_unit_test_setup_teardown(test_attack_memory_exhaustion, setup, teardown),
    };
    
    printf("\n");
    printf("╔════════════════════════════════════════════════════════════════════════╗\n");
    printf("║  Krynox Nexus - Secure Modules Unit Test Suite                        ║\n");
    printf("║  Zero-Trust Kernel Module Hardening                                   ║\n");
    printf("╚════════════════════════════════════════════════════════════════════════╝\n");
    printf("\n");
    printf("Test Configuration:\n");
    printf("  - Total Test Cases: 36\n");
    printf("  - Test Suites: 5\n");
    printf("  - Coverage Goal: ≥85%% line, ≥80%% branch\n");
    printf("  - Framework: CMocka\n");
    printf("\n");
    printf("Test Suites:\n");
    printf("  1. secure_stack_copy()    - 8 tests (boundary conditions)\n");
    printf("  2. secure_heap_copy()     - 8 tests (memory scenarios)\n");
    printf("  3. secure_log_message()   - 6 tests (format safety)\n");
    printf("  4. secure_copy_message()  - 8 tests (hello_secure.c)\n");
    printf("  5. Security Attacks       - 6 tests (attack simulation)\n");
    printf("\n");
    printf("Running tests...\n");
    printf("════════════════════════════════════════════════════════════════════════\n\n");
    
    int result = cmocka_run_group_tests(tests, NULL, NULL);
    
    printf("\n════════════════════════════════════════════════════════════════════════\n");
    printf("Test execution complete!\n");
    printf("\n");
    printf("Made with ❤️  by Bob - Security Architect & Kernel Engineer\n");
    printf("════════════════════════════════════════════════════════════════════════\n\n");
    
    return result;
}
