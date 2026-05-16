# Krynox Nexus - Unit Test Suite

Comprehensive unit tests for secure kernel module implementations.

## 📋 Overview

This directory contains unit tests that validate the security implementations in:
- **buffer_overflow_secure.c**: Stack/heap copy functions, format string safety
- **hello_secure.c**: Secure message copying with bounds checking

## 🎯 Test Coverage

### Test Statistics
- **Total Test Cases**: 36
- **Test Suites**: 5
- **Coverage Goal**: ≥85% line coverage, ≥80% branch coverage
- **Framework**: CMocka

### Test Suites

#### 1. `secure_stack_copy()` - 8 Tests
Tests boundary conditions and overflow prevention for stack-based buffer operations.

| Test | Description | CWE |
|------|-------------|-----|
| `test_stack_copy_valid_input` | Normal input within limits | - |
| `test_stack_copy_exact_boundary` | Input at BUFFER_SIZE-1 | - |
| `test_stack_copy_overflow_attempt` | Input exceeds buffer size | CWE-121 |
| `test_stack_copy_empty_string` | Empty string edge case | - |
| `test_stack_copy_null_termination` | Verify null terminator | - |
| `test_stack_copy_truncation_detection` | Detect truncation attempts | - |
| `test_stack_copy_single_char` | Minimal input | - |
| `test_stack_copy_unicode_chars` | UTF-8 multibyte characters | - |

#### 2. `secure_heap_copy()` - 8 Tests
Tests dynamic memory allocation and heap overflow prevention.

| Test | Description | CWE |
|------|-------------|-----|
| `test_heap_copy_valid_allocation` | Normal heap allocation | - |
| `test_heap_copy_max_size` | Maximum size boundary (4096) | - |
| `test_heap_copy_exceeds_max` | Input exceeds MAX_INPUT_SIZE | CWE-122 |
| `test_heap_copy_small_input` | Small allocation | - |
| `test_heap_copy_null_termination` | Verify null byte | - |
| `test_heap_copy_memory_cleanup` | No memory leaks | CWE-401 |
| `test_heap_copy_zero_length` | Zero-length input | - |
| `test_heap_copy_repeated_calls` | Stress test (10 calls) | - |

#### 3. `secure_log_message()` - 6 Tests
Tests format string safety and logging security.

| Test | Description | CWE |
|------|-------------|-----|
| `test_log_safe_string` | Normal string logging | - |
| `test_log_format_specifiers` | Format specifiers as literal | CWE-134 |
| `test_log_length_limiting` | Truncation to 128 chars | - |
| `test_log_special_chars` | Special characters (\n, \t) | - |
| `test_log_binary_data` | Binary data with null bytes | - |
| `test_log_control_chars` | Control characters (0x00-0x1F) | - |

#### 4. `secure_copy_message()` - 8 Tests
Tests secure message copying from hello_secure.c.

| Test | Description | CWE |
|------|-------------|-----|
| `test_copy_message_valid` | Valid message copy | - |
| `test_copy_message_null_pointer` | NULL pointer validation | CWE-476 |
| `test_copy_message_max_length` | Maximum length boundary | - |
| `test_copy_message_exceeds_max` | Oversized input rejection | - |
| `test_copy_message_allocation_failure` | Simulate malloc failure | CWE-401 |
| `test_copy_message_null_termination` | Verify null terminator | - |
| `test_copy_message_whitespace_only` | Whitespace-only input | - |
| `test_copy_message_memory_zeroing` | Secure memory cleanup | - |

#### 5. Security Attack Simulation - 6 Tests
Tests defense against real-world attack vectors.

| Test | Attack Vector | CWE |
|------|---------------|-----|
| `test_attack_buffer_overflow` | Stack buffer overflow | CWE-121 |
| `test_attack_heap_overflow` | Heap buffer overflow | CWE-122 |
| `test_attack_format_string` | Format string exploitation | CWE-134 |
| `test_attack_integer_overflow` | Size_t overflow | CWE-190 |
| `test_attack_null_byte_injection` | Embedded null bytes | CWE-158 |
| `test_attack_memory_exhaustion` | Resource exhaustion | CWE-400 |

## 🚀 Running Tests

### Prerequisites

Install required dependencies:
```bash
sudo apt-get install -y libcmocka-dev libcmocka0 lcov
```

### Quick Start

Run all unit tests:
```bash
make test-unit
```

Run with coverage report:
```bash
make coverage
```

View coverage in browser:
```bash
make view-coverage
```

### Manual Execution

Compile tests:
```bash
gcc -Wall -Wextra -Werror -g -O0 -fprofile-arcs -ftest-coverage \
    -o tests/unit/test_secure_modules tests/unit/test_secure_modules.c \
    -lcmocka -lgcov
```

Run tests:
```bash
./tests/unit/test_secure_modules
```

Generate coverage:
```bash
lcov --capture --directory tests/unit --output-file coverage/coverage.info
genhtml coverage/coverage.info --output-directory coverage
```

## 📊 Expected Output

### Successful Test Run

```
╔════════════════════════════════════════════════════════════════════════╗
║  Krynox Nexus - Secure Modules Unit Test Suite                        ║
║  Zero-Trust Kernel Module Hardening                                   ║
╚════════════════════════════════════════════════════════════════════════╝

Test Configuration:
  - Total Test Cases: 36
  - Test Suites: 5
  - Coverage Goal: ≥85% line, ≥80% branch
  - Framework: CMocka

Test Suites:
  1. secure_stack_copy()    - 8 tests (boundary conditions)
  2. secure_heap_copy()     - 8 tests (memory scenarios)
  3. secure_log_message()   - 6 tests (format safety)
  4. secure_copy_message()  - 8 tests (hello_secure.c)
  5. Security Attacks       - 6 tests (attack simulation)

Running tests...
════════════════════════════════════════════════════════════════════════

[==========] Running 36 test(s).
[ RUN      ] test_stack_copy_valid_input
[       OK ] test_stack_copy_valid_input
[ RUN      ] test_stack_copy_exact_boundary
[       OK ] test_stack_copy_exact_boundary
...
[ RUN      ] test_attack_memory_exhaustion
[       OK ] test_attack_memory_exhaustion
[==========] 36 test(s) run.
[  PASSED  ] 36 test(s).

════════════════════════════════════════════════════════════════════════
Test execution complete!

Made with ❤️  by Bob - Security Architect & Kernel Engineer
════════════════════════════════════════════════════════════════════════
```

### Coverage Report

Expected coverage metrics:
```
Lines:     87.4% (312/357)
Functions: 100.0% (8/8)
Branches:  82.1% (64/78)

Security Coverage:
  Attack Vectors Tested: 6/6 (100%)
  Error Paths Covered:   18/18 (100%)
  Memory Safety Checks:  24/24 (100%)
```

## 🔍 Test Implementation Details

### Mock Functions

The test suite implements kernel function mocks for user-space testing:

- **Memory Allocation**: `kmalloc()`, `kzalloc()`, `kfree()`
- **Logging**: `pr_info()`, `pr_warn()`, `pr_err()`
- **String Operations**: `strlcpy()`, `strnlen()`

### Test Fixtures

Each test uses setup/teardown functions:
- **Setup**: Resets global state, clears allocations
- **Teardown**: Frees memory, checks for leaks

### Assertion Types

- `assert_int_equal()`: Error code validation
- `assert_non_null()`: Pointer validation
- `assert_string_equal()`: String comparison
- `assert_true()`: Boolean conditions

## 🐛 Troubleshooting

### CMocka Not Found

```bash
# Ubuntu/Debian
sudo apt-get install libcmocka-dev

# Fedora/RHEL
sudo dnf install libcmocka-devel

# Arch Linux
sudo pacman -S cmocka
```

### Coverage Tools Missing

```bash
sudo apt-get install lcov
```

### Test Failures

Run with verbose output:
```bash
./tests/unit/test_secure_modules -v
```

Check for memory leaks:
```bash
valgrind --leak-check=full ./tests/unit/test_secure_modules
```

### Low Coverage

Review uncovered lines:
```bash
lcov --list coverage/coverage.info
```

## 📝 Adding New Tests

### Test Template

```c
static void test_new_function(void **state) {
    (void)state;
    
    // Arrange
    const char *input = "test input";
    
    // Act
    int result = function_under_test(input);
    
    // Assert
    assert_int_equal(result, 0);
}
```

### Register Test

Add to `main()`:
```c
cmocka_unit_test_setup_teardown(test_new_function, setup, teardown),
```

## 🔒 Security Testing Guidelines

### Attack Simulation

When adding attack tests:
1. Document the CWE reference
2. Verify proper error code returned
3. Check no memory corruption occurs
4. Validate error logging

### Coverage Requirements

- **Critical Paths**: 100% coverage required
- **Error Handling**: All error paths tested
- **Boundary Conditions**: All boundaries validated
- **Attack Vectors**: All known attacks simulated

## 📚 References

- [CMocka Documentation](https://cmocka.org/)
- [CWE Database](https://cwe.mitre.org/)
- [Kernel Coding Style](https://www.kernel.org/doc/html/latest/process/coding-style.html)
- [OWASP Secure Coding](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/)

## 🤝 Contributing

When modifying secure modules:
1. Update corresponding test cases
2. Add tests for new functionality
3. Maintain ≥85% coverage
4. Document security implications
5. Update this README

## 📞 Support

For test-related questions:
- See [CONTRIBUTING.md](../../CONTRIBUTING.md)
- Check [AGENTS.md](../../AGENTS.md) for Bob's guidelines
- Open an issue on GitHub

---

**Status**: ✅ Active  
**Last Updated**: 2026-05-16  
**Maintainer**: Bob - Security Architect & Kernel Engineer

---

*Made with ❤️ by the Krynox Nexus Security Team*