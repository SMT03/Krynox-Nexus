# Contributing to Krynox Nexus

Thank you for your interest in contributing to Krynox Nexus! This document provides guidelines and instructions for contributing to the project.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Security Guidelines](#security-guidelines)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Documentation](#documentation)
- [Community](#community)

---

## 🤝 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of experience level, background, or identity.

### Expected Behavior

- Be respectful and considerate
- Use welcoming and inclusive language
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Trolling, insulting, or derogatory remarks
- Public or private harassment
- Publishing others' private information
- Other conduct inappropriate in a professional setting

---

## 🚀 Getting Started

### Prerequisites

Before contributing, ensure you have:

- Linux system (Ubuntu 20.04+ recommended)
- Kernel headers installed (`linux-headers-$(uname -r)`)
- GCC 9.0+ or Clang 10.0+
- Git for version control
- Docker (optional, for containerized development)

### Setting Up Development Environment

1. **Fork the repository**
   ```bash
   # Click "Fork" on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/krynox-nexus.git
   cd krynox-nexus
   ```

2. **Add upstream remote**
   ```bash
   git remote add upstream https://github.com/krynox-nexus/krynox-nexus.git
   ```

3. **Install development tools**
   ```bash
   sudo make setup
   ```

4. **Verify installation**
   ```bash
   make check-deps
   ```

---

## 🔄 Development Workflow

### 1. Create a Feature Branch

```bash
# Update your fork
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name
```

### Branch Naming Convention

- `feature/` - New features
- `bugfix/` - Bug fixes
- `security/` - Security improvements
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions or improvements

### 2. Make Your Changes

Follow the [Coding Standards](#coding-standards) and [Security Guidelines](#security-guidelines).

### 3. Test Your Changes

```bash
# Build modules
make build

# Run security scans
make security-scan

# Run tests
make test
```

### 4. Commit Your Changes

Follow the [Commit Message Guidelines](#commit-message-guidelines).

```bash
git add .
git commit -m "feat: add new security check for buffer overflows"
```

### 5. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 6. Create Pull Request

Open a pull request on GitHub with a clear description of your changes.

---

## 📝 Coding Standards

### C/C++ Code Style

#### General Guidelines

- **Indentation**: 4 spaces (no tabs)
- **Line Length**: Maximum 100 characters
- **Braces**: K&R style (opening brace on same line)
- **Naming**: snake_case for functions and variables

#### Example

```c
/* Good example */
static int secure_copy_data(const char *src, char *dst, size_t max_len)
{
    if (!src || !dst || max_len == 0) {
        return -EINVAL;
    }
    
    size_t len = strnlen(src, max_len);
    if (len >= max_len) {
        return -EOVERFLOW;
    }
    
    strncpy(dst, src, len);
    dst[len] = '\0';
    
    return 0;
}
```

### Kernel Module Guidelines

#### Module Structure

```c
#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Your Name");
MODULE_DESCRIPTION("Module description");
MODULE_VERSION("1.0");

static int __init module_name_init(void)
{
    pr_info("module_name: Initializing\n");
    return 0;
}

static void __exit module_name_exit(void)
{
    pr_info("module_name: Cleaning up\n");
}

module_init(module_name_init);
module_exit(module_name_exit);
```

#### Error Handling

```c
/* Always check return values */
ptr = kmalloc(size, GFP_KERNEL);
if (!ptr) {
    pr_err("module_name: Memory allocation failed\n");
    return -ENOMEM;
}

/* Clean up on error */
ret = some_function();
if (ret) {
    pr_err("module_name: Function failed: %d\n", ret);
    goto err_cleanup;
}

return 0;

err_cleanup:
    kfree(ptr);
    return ret;
```

### Shell Script Guidelines

```bash
#!/bin/bash
#
# Script description
#
# Usage: script_name.sh [options]

set -e  # Exit on error

# Use functions
function main() {
    local var="value"
    
    # Check prerequisites
    if ! command -v tool &> /dev/null; then
        echo "Error: tool not found"
        exit 1
    fi
    
    # Do work
    echo "Processing..."
}

main "$@"
```

---

## 🔒 Security Guidelines

### Security-First Development

All contributions must prioritize security:

1. **Input Validation**: Always validate and sanitize input
2. **Bounds Checking**: Check array bounds before access
3. **Memory Safety**: Use safe memory operations
4. **Error Handling**: Handle all error conditions
5. **Least Privilege**: Request minimal permissions

### Security Checklist

Before submitting code, verify:

- [ ] All inputs are validated
- [ ] Buffer sizes are checked
- [ ] Memory is properly allocated and freed
- [ ] No memory leaks (use Valgrind)
- [ ] No use-after-free vulnerabilities
- [ ] No format string vulnerabilities
- [ ] Integer overflow checks where needed
- [ ] Proper locking for concurrent access
- [ ] No hardcoded credentials or secrets

### Vulnerable Code Examples

**❌ BAD: Buffer overflow**
```c
char buffer[64];
strcpy(buffer, user_input);  // Dangerous!
```

**✅ GOOD: Safe string copy**
```c
char buffer[64];
strncpy(buffer, user_input, sizeof(buffer) - 1);
buffer[sizeof(buffer) - 1] = '\0';
```

**❌ BAD: Use-after-free**
```c
kfree(ptr);
ptr->field = value;  // Accessing freed memory!
```

**✅ GOOD: Proper cleanup**
```c
kfree(ptr);
ptr = NULL;  // Prevent use-after-free
```

---

## 🧪 Testing Requirements

### Required Tests

All contributions must include:

1. **Unit Tests**: Test individual functions
2. **Integration Tests**: Test module loading/unloading
3. **Security Tests**: Verify security properties

### Running Tests

```bash
# Run all tests
make test

# Run specific test suite
make test-unit
make test-integration
```

### Writing Tests

```c
/* Example unit test */
static int test_secure_copy(void)
{
    char src[] = "test";
    char dst[10];
    int ret;
    
    ret = secure_copy_data(src, dst, sizeof(dst));
    if (ret != 0) {
        pr_err("Test failed: secure_copy returned %d\n", ret);
        return -1;
    }
    
    if (strcmp(dst, src) != 0) {
        pr_err("Test failed: strings don't match\n");
        return -1;
    }
    
    pr_info("Test passed: secure_copy\n");
    return 0;
}
```

---

## 🔀 Pull Request Process

### Before Submitting

1. **Update your branch**
   ```bash
   git checkout main
   git pull upstream main
   git checkout feature/your-feature
   git rebase main
   ```

2. **Run all checks**
   ```bash
   make clean
   make build
   make security-scan
   make test
   ```

3. **Update documentation**
   - Update README.md if needed
   - Add/update code comments
   - Update CHANGELOG.md

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Security improvement
- [ ] Documentation update
- [ ] Code refactoring

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Security scans pass
- [ ] Manual testing completed

## Security Impact
Describe any security implications

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings introduced
- [ ] Tests added/updated
```

### Review Process

1. **Automated Checks**: CI/CD pipeline runs automatically
2. **Security Review**: Security team reviews for vulnerabilities
3. **Code Review**: Maintainers review code quality
4. **Approval**: At least one maintainer approval required
5. **Merge**: Squash and merge to main branch

---

## 📝 Commit Message Guidelines

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `security`: Security improvement
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Test additions or changes
- `chore`: Build process or auxiliary tool changes

### Examples

```
feat(scanner): add IBM Bob CLI integration

Integrate IBM Bob CLI for architectural vulnerability analysis.
Includes automated report generation and SARIF output.

Closes #123
```

```
security(module): fix buffer overflow in input handler

Replace strcpy with strncpy to prevent buffer overflow.
Add bounds checking for all user input.

CVE-2026-XXXXX
```

---

## 📚 Documentation

### Code Documentation

```c
/**
 * secure_copy_data - Safely copy data with bounds checking
 * @src: Source buffer (must be null-terminated)
 * @dst: Destination buffer
 * @max_len: Maximum length to copy
 *
 * Copies data from src to dst with proper bounds checking
 * and null termination.
 *
 * Return: 0 on success, negative error code on failure
 */
static int secure_copy_data(const char *src, char *dst, size_t max_len)
{
    /* Implementation */
}
```

### Documentation Updates

When adding features, update:

- README.md - Project overview
- SECURITY.md - Security policies
- docs/ - Detailed documentation
- Code comments - Inline documentation

---

## 👥 Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and discussions
- **Pull Requests**: Code contributions
- **Security**: security@krynox-nexus.local (for vulnerabilities)

### Getting Help

- Check existing issues and documentation
- Ask questions in GitHub Discussions
- Join our community chat (coming soon)

### Recognition

Contributors are recognized in:

- CHANGELOG.md
- GitHub contributors page
- Security Hall of Fame (for security findings)

---

## 📜 License

By contributing to Krynox Nexus, you agree that your contributions will be licensed under the GPL v2 license.

---

## 🙏 Thank You!

Thank you for contributing to Krynox Nexus! Your efforts help make kernel module development more secure for everyone.

---

<div align="center">

**Questions?** Open an issue or start a discussion on GitHub.

**Security Issue?** Email security@krynox-nexus.local

</div>