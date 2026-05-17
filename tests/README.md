# Krynox Nexus - Test Suite

This directory contains the automated test suite for Krynox Nexus kernel modules and security scanning infrastructure.

## 📁 Directory Structure

```
tests/
├── unit/              # Unit tests for individual functions
├── integration/       # Integration tests for complete workflows
├── fixtures/          # Test data and fixtures
└── README.md         # This file
```

## 🧪 Test Categories

### Unit Tests (`unit/`)
Unit tests verify individual functions and components in isolation:
- Memory allocation/deallocation functions
- String manipulation functions
- Input validation routines
- Error handling paths
- Security helper functions

**Status**: ✅ Implemented (36 tests)

### Integration Tests (`integration/`)
Integration tests verify complete workflows and interactions:
- Kernel hardening verification script execution
- Static analysis pipeline execution
- Security scan report generation
- Exit code validation (0, 1, 2, 3)
- Color-coded output formatting
- JSON and SARIF report structure validation

**Status**: ✅ Implemented (20 tests)

### Test Fixtures (`fixtures/`)
Test fixtures provide sample data and configurations:
- Sample vulnerable code snippets
- Expected security scan results
- Mock kernel configurations
- Test kernel modules
- Sample security reports

**Status**: ✅ Implemented

## 🚀 Running Tests

### Prerequisites
```bash
# Install test dependencies
sudo apt-get install -y \
    check \
    cmocka \
    python3-pytest \
    python3-coverage
```

### Run All Tests
```bash
make test
```

### Run Unit Tests Only
```bash
make test-unit
```

### Run Integration Tests Only
```bash
make test-integration
```

## 📝 Writing Tests

### Unit Test Example
```c
// tests/unit/test_memory_safety.c
#include <check.h>
#include "../../src/examples/hello_secure.h"

START_TEST(test_safe_string_copy)
{
    char dest[32];
    const char *src = "Hello, Kernel!";
    
    int result = safe_string_copy(dest, src, sizeof(dest));
    
    ck_assert_int_eq(result, 0);
    ck_assert_str_eq(dest, src);
}
END_TEST

Suite *memory_safety_suite(void)
{
    Suite *s;
    TCase *tc_core;
    
    s = suite_create("Memory Safety");
    tc_core = tcase_create("Core");
    
    tcase_add_test(tc_core, test_safe_string_copy);
    suite_add_tcase(s, tc_core);
    
    return s;
}
```

### Integration Test Example
```python
# tests/integration/test_security_pipeline.py
import pytest
import subprocess
import json

def test_static_analysis_pipeline():
    """Test that static analysis detects known vulnerabilities"""
    
    # Run static analysis
    result = subprocess.run(
        ['./scripts/security/run_static_analysis.sh'],
        capture_output=True,
        text=True
    )
    
    # Check exit code
    assert result.returncode == 0
    
    # Verify report was generated
    with open('reports/static-analysis.json', 'r') as f:
        report = json.load(f)
    
    # Verify vulnerabilities were detected
    assert len(report['findings']) > 0
    assert any(f['severity'] == 'CRITICAL' for f in report['findings'])
```

## 🎯 Test Coverage Goals

- **Unit Test Coverage**: ≥ 80%
- **Integration Test Coverage**: ≥ 70%
- **Critical Path Coverage**: 100%
- **Security Function Coverage**: 100%

## 🔒 Security Testing

### Vulnerability Detection Tests
Verify that the security pipeline correctly detects:
- Buffer overflows (CWE-121, CWE-122)
- Use-after-free (CWE-416)
- Double-free (CWE-415)
- Memory leaks (CWE-401)
- Format string vulnerabilities (CWE-134)
- Integer overflows (CWE-190)
- Null pointer dereferences (CWE-476)

### False Positive Tests
Verify that secure code does not trigger false alarms:
- Properly bounds-checked operations
- Safe string functions (strncpy, strnlen)
- Validated memory allocations
- Proper error handling

## 📊 Test Reporting

Test results are automatically generated in multiple formats:
- **JUnit XML**: For CI/CD integration
- **HTML**: For human-readable reports
- **JSON**: For programmatic analysis
- **Coverage Reports**: Code coverage metrics

## 🔄 Continuous Testing

Tests are automatically run:
- On every commit (via GitHub Actions)
- On pull requests
- Daily scheduled runs
- Before releases

## 🐛 Debugging Failed Tests

### View Test Logs
```bash
cat test-results/latest.log
```

### Run Tests in Verbose Mode
```bash
make test VERBOSE=1
```

### Run Specific Test
```bash
# Unit test
./tests/unit/test_memory_safety

# Integration test
pytest tests/integration/test_security_pipeline.py -v
```

## 📚 Test Documentation

Each test should include:
- **Purpose**: What is being tested
- **Setup**: Required preconditions
- **Execution**: Test steps
- **Verification**: Expected results
- **Cleanup**: Post-test cleanup

## 🤝 Contributing Tests

When adding new features:
1. Write unit tests for new functions
2. Add integration tests for new workflows
3. Update test fixtures as needed
4. Ensure all tests pass before submitting PR
5. Maintain or improve code coverage

## 📞 Support

For test-related questions:
- See [CONTRIBUTING.md](../CONTRIBUTING.md)
- Check [AGENTS.md](../AGENTS.md) for testing guidelines
- Open an issue on GitHub

---

**Status**: ✅ Test infrastructure fully implemented  
**Last Updated**: 2026-05-17  
**Maintainer**: Krynox Security Agent - Security Architect & Kernel Engineer

---

*Made with ❤️ by the Krynox Nexus Security Team*