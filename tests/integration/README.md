# Integration Tests - Krynox Nexus

This directory contains integration tests for the Krynox Nexus security pipeline, validating end-to-end functionality of security scanning scripts and CI/CD workflows.

## 📋 Overview

The integration test suite validates:
- **Kernel Hardening Verification** (`verify_kernel_hardening.sh`)
- **Static Analysis Pipeline** (`run_static_analysis.sh`)
- **Report Generation** (JSON, SARIF, HTML)
- **Exit Code Handling** (0, 1, 2, 3)
- **Output Formatting** (color-coded logs, structured output)

## 🧪 Test Structure

```
tests/integration/
├── test_pipeline.py          # Main integration test suite
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

### Test Classes

#### `TestKernelHardeningVerification`
Tests for `scripts/security/verify_kernel_hardening.sh`:
- Script execution and exit codes (0=PASS, 1=CRITICAL, 2=HIGH, 3=MEDIUM)
- Color-coded output validation (GREEN, RED, YELLOW, BLUE)
- Configuration tier sections (TIER 1, 2, 3, ARM64-specific)
- Runtime checks (SELinux, KASLR, kernel lockdown)
- Summary section with failure counts

**Total Tests**: 9 core functionality tests

#### `TestStaticAnalysisPipeline`
Tests for `scripts/security/run_static_analysis.sh`:
- Script execution and report generation
- Directory structure creation (`reports/static-analysis/`)
- Tool-specific reports (Clang, Cppcheck, Sparse)
- JSON summary report structure validation
- SARIF report generation for GitHub integration

**Total Tests**: 9 core functionality tests

#### `TestEdgeCases`
Tests for error handling and edge conditions:
- Missing `/proc/config.gz` handling
- Missing security tools (clang, cppcheck, sparse)
- Permission errors
- Timeout scenarios

**Total Tests**: 2 edge case tests (expandable)

## 🚀 Running Tests

### Prerequisites

Install Python dependencies:
```bash
pip3 install -r tests/integration/requirements.txt
```

Or install individually:
```bash
pip3 install pytest pytest-cov pytest-timeout
```

### Run All Integration Tests

Using Make:
```bash
make test-integration
```

Using pytest directly:
```bash
pytest tests/integration/test_pipeline.py -v
```

### Run Specific Test Class

```bash
# Test kernel hardening verification only
pytest tests/integration/test_pipeline.py::TestKernelHardeningVerification -v

# Test static analysis pipeline only
pytest tests/integration/test_pipeline.py::TestStaticAnalysisPipeline -v

# Test edge cases only
pytest tests/integration/test_pipeline.py::TestEdgeCases -v
```

### Run Specific Test

```bash
pytest tests/integration/test_pipeline.py::TestKernelHardeningVerification::test_script_execution -v
```

### Run with Coverage

```bash
pytest tests/integration/test_pipeline.py --cov=scripts --cov-report=html
```

View coverage report:
```bash
xdg-open htmlcov/index.html
```

### Run with Detailed Output

```bash
pytest tests/integration/test_pipeline.py -v --tb=long
```

## 📊 Test Output

### Successful Test Run
```
tests/integration/test_pipeline.py::TestKernelHardeningVerification::test_script_exists PASSED
tests/integration/test_pipeline.py::TestKernelHardeningVerification::test_script_execution PASSED
tests/integration/test_pipeline.py::TestKernelHardeningVerification::test_output_contains_header PASSED
...
==================== 20 passed in 45.23s ====================
```

### Failed Test Example
```
FAILED tests/integration/test_pipeline.py::TestStaticAnalysisPipeline::test_summary_json_generated
AssertionError: Summary JSON not generated
```

## 🎯 Test Strategy

### Real System Testing
Tests run against the **actual system** to validate:
- Scripts execute without errors
- Output format is correct and parseable
- Exit codes match expected values
- Reports are generated with proper structure

### Non-Destructive
Tests **do not modify** system configuration:
- No kernel parameter changes
- No security policy modifications
- No permanent file system changes
- Reports are cleaned up after tests

### Validation Focus
Tests validate:
- ✅ Script execution (no crashes, timeouts)
- ✅ Output format (color codes, structure)
- ✅ Exit codes (0, 1, 2, 3)
- ✅ Report generation (JSON, SARIF, text)
- ✅ Error handling (missing tools, permissions)

## 📝 Writing New Tests

### Test Template

```python
def test_new_feature(self, clean_reports):
    """
    Test description.
    
    Purpose:
        What this test validates.
    
    Execution:
        How the test runs.
    
    Verification:
        What is checked.
    """
    # Setup
    exit_code, stdout, stderr = run_script(SCRIPT_PATH)
    
    # Verification
    assert exit_code == 0, "Script failed"
    assert "expected output" in stdout, "Missing expected output"
```

### Best Practices

1. **Use Fixtures**: Leverage `clean_reports` for cleanup
2. **Clear Assertions**: Use descriptive assertion messages
3. **Document Purpose**: Include comprehensive docstrings
4. **Test One Thing**: Each test should validate one specific behavior
5. **Handle Optionals**: Use `pytest.mark.skipif` for optional dependencies

## 🔧 Troubleshooting

### pytest Not Found
```bash
pip3 install pytest
```

### Permission Denied
Some tests may require elevated privileges:
```bash
sudo pytest tests/integration/test_pipeline.py -v
```

### Script Not Found
Ensure you're running from project root:
```bash
cd /path/to/Krynox-Nexus
pytest tests/integration/test_pipeline.py -v
```

### Timeout Errors
Increase timeout in test configuration:
```python
TEST_TIMEOUT = 300  # 5 minutes
```

### Missing Security Tools
Install required tools:
```bash
sudo apt-get install clang cppcheck sparse
```

## 📈 Test Coverage Goals

- **Script Execution**: 100%
- **Output Validation**: 100%
- **Exit Code Handling**: 100%
- **Report Generation**: 100%
- **Error Handling**: 95%
- **Edge Cases**: 90%

## 🔄 CI/CD Integration

### GitHub Actions

Tests run automatically on:
- Every commit to main branch
- Pull requests
- Scheduled daily runs

See `.github/workflows/security-scan.yml` for configuration.

### Local CI Simulation

Run full CI pipeline locally:
```bash
make ci
```

## 📚 Related Documentation

- [Main Test README](../README.md) - Overall test suite documentation
- [Unit Tests](../unit/README.md) - Unit test documentation
- [AGENTS.md](../../AGENTS.md) - Bob's testing guidelines
- [CONTRIBUTING.md](../../CONTRIBUTING.md) - Contribution guidelines

## 🐛 Known Issues

### Issue: Tests Fail on Non-Linux Systems
**Status**: Expected behavior  
**Reason**: Scripts are Linux-specific (kernel hardening, /proc filesystem)  
**Workaround**: Run tests in Docker container or Linux VM

### Issue: Sparse Reports Empty
**Status**: Expected behavior  
**Reason**: Sparse is kernel-specific and may not find issues in all code  
**Workaround**: This is normal; test validates file creation, not content

## 📞 Support

For test-related questions:
- See [CONTRIBUTING.md](../../CONTRIBUTING.md)
- Check [AGENTS.md](../../AGENTS.md) for Bob's testing guidelines
- Open an issue on GitHub

---

**Status**: ✅ Active  
**Last Updated**: 2026-05-16  
**Maintainer**: Bob - Security Architect & Kernel Engineer  
**Test Framework**: pytest 7.0+  
**Total Tests**: 20 (18 core + 2 edge cases)

---

*Made with ❤️ by the Krynox Nexus Security Team*