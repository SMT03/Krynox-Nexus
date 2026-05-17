# Installation Guide - Krynox Nexus Unit Tests

Quick guide to install dependencies and run the unit test suite.

## 📦 Prerequisites

### Required Packages

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install -y \
    libcmocka-dev \
    libcmocka0 \
    lcov \
    gcc \
    make
```

#### Fedora/RHEL/CentOS
```bash
sudo dnf install -y \
    libcmocka-devel \
    libcmocka \
    lcov \
    gcc \
    make
```

#### Arch Linux
```bash
sudo pacman -S \
    cmocka \
    lcov \
    gcc \
    make
```

### Verify Installation

Check CMocka:
```bash
pkg-config --modversion cmocka
# Expected: 1.1.5 or higher
```

Check lcov:
```bash
lcov --version
# Expected: lcov: LCOV version 1.14 or higher
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
# Ubuntu/Debian
sudo apt-get install -y libcmocka-dev lcov

# Or use the project setup script
cd /path/to/Krynox-Nexus
sudo make setup
```

### 2. Compile Tests
```bash
make test-unit
```

This will:
- Compile `tests/unit/test_secure_modules.c`
- Link with CMocka and gcov
- Run all 36 test cases
- Display results

### 3. Generate Coverage Report
```bash
make coverage
```

This will:
- Run tests with coverage tracking
- Generate `coverage/coverage.info`
- Create HTML report in `coverage/`
- Display coverage metrics

### 4. View Coverage
```bash
make view-coverage
```

Opens the coverage report in your default browser.

## 🔧 Manual Compilation

If you prefer manual compilation:

```bash
# Compile with coverage
gcc -Wall -Wextra -Werror -g -O0 \
    -fprofile-arcs -ftest-coverage \
    -o tests/unit/test_secure_modules \
    tests/unit/test_secure_modules.c \
    -lcmocka -lgcov

# Run tests
./tests/unit/test_secure_modules

# Generate coverage
lcov --capture \
     --directory tests/unit \
     --output-file coverage.info

# Create HTML report
genhtml coverage.info \
        --output-directory coverage

# View report
xdg-open coverage/index.html
```

## 🐛 Troubleshooting

### CMocka Not Found

**Error**: `fatal error: cmocka.h: No such file or directory`

**Solution**:
```bash
# Check if installed
dpkg -l | grep cmocka

# Install if missing
sudo apt-get install libcmocka-dev
```

### Linking Error

**Error**: `undefined reference to 'cmocka_run_group_tests'`

**Solution**: Add `-lcmocka` to linker flags:
```bash
gcc ... -lcmocka
```

### Coverage Not Generated

**Error**: No `.gcda` files created

**Solution**: Ensure compilation flags include:
```bash
-fprofile-arcs -ftest-coverage
```

And link with:
```bash
-lgcov
```

### Permission Denied

**Error**: `Permission denied` when running tests

**Solution**:
```bash
chmod +x tests/unit/test_secure_modules
./tests/unit/test_secure_modules
```

## 📊 Expected Output

### Successful Installation

```bash
$ make test-unit
Compiling unit tests...
✓ Unit tests compiled
Running unit tests...

╔════════════════════════════════════════════════════════════════════════╗
║  Krynox Nexus - Secure Modules Unit Test Suite                        ║
║  Zero-Trust Kernel Module Hardening                                   ║
╚════════════════════════════════════════════════════════════════════════╝

Test Configuration:
  - Total Test Cases: 36
  - Test Suites: 5
  - Coverage Goal: ≥85% line, ≥80% branch
  - Framework: CMocka

Running tests...
════════════════════════════════════════════════════════════════════════

[==========] Running 36 test(s).
[  PASSED  ] 36 test(s).

════════════════════════════════════════════════════════════════════════
Test execution complete!
✓ Unit tests complete
```

### Coverage Report

```bash
$ make coverage
Generating coverage report...
Capturing coverage data from tests/unit
Processing coverage data
Writing data to coverage/coverage.info
Generating HTML output
✓ Coverage report generated: coverage/index.html

Overall coverage rate:
  lines......: 87.4% (312 of 357 lines)
  functions..: 100.0% (8 of 8 functions)
  branches...: 82.1% (64 of 78 branches)
```

## 🧹 Cleanup

Remove test artifacts:
```bash
make clean-test
```

Remove everything (tests + build artifacts):
```bash
make clean-all
```

## 🔍 Verification

Verify the test suite is working:

```bash
# 1. Check file exists
ls -lh tests/unit/test_secure_modules.c
# Expected: 645 lines, ~25KB

# 2. Compile
make test-unit
# Expected: No errors, executable created

# 3. Run
./tests/unit/test_secure_modules
# Expected: All 36 tests pass

# 4. Check coverage
make coverage
# Expected: ≥85% line coverage
```

## 📚 Additional Resources

- [CMocka Documentation](https://cmocka.org/)
- [LCOV Documentation](http://ltp.sourceforge.net/coverage/lcov.php)
- [GCC Coverage Options](https://gcc.gnu.org/onlinedocs/gcc/Gcov.html)

## 🆘 Getting Help

If you encounter issues:

1. Check [tests/unit/README.md](README.md) for detailed documentation
2. Review [CONTRIBUTING.md](../../CONTRIBUTING.md) for contribution guidelines
3. See [AGENTS.md](../../AGENTS.md) for testing guidelines
4. Open an issue on GitHub with:
   - Error message
   - System information (`uname -a`)
   - CMocka version (`pkg-config --modversion cmocka`)
   - GCC version (`gcc --version`)

---

**Last Updated**: 2026-05-17  
**Maintainer**: Krynox Security Agent - Security Architect & Kernel Engineer

---

*Made with ❤️ by the Krynox Nexus Security Team*