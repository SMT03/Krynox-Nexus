# 📖 Krynox Nexus - Zero-Trust Developer Usage Guide

This guide provides developers, auditors, and security engineers with a step-by-step walkthrough on how to compile, scan, test, and integrate Linux kernel modules inside the **Krynox Nexus** security hardening ecosystem.

---

## 🚀 1. Quick Start Local Workflow

If you are a developer looking to write, test, and audit kernel modules locally, follow this basic cycle:

```
[Write Code in src/] ──> [make build] ──> [make security-scan] ──> [make test] ──> [make reports]
```

### Clean and Build Modules
To compile all modules (both secure examples and testing vectors) using security-fortified compiler flags, run:
```bash
# Clean previous build artifacts
make clean

# Compile all kernel modules
make build
```

---

## 🔍 2. Running Security Scans Locally

Krynox Nexus integrates a multi-layered static analysis engine that checks your code at the semantic, syntactic, and architectural levels.

### Run All Scans
To run all active local security analyzers simultaneously, execute:
```bash
make security-scan
```
This is a wrapper target that triggers **Static Analysis** and **IBM Bob Architectural checks**.

### Individual Analyzers

#### A. Static Code Analysis (Clang, Cppcheck, Sparse)
To run compiler-level and semantic analysis:
```bash
./scripts/security/run_static_analysis.sh
```
*   **Clang Static Analyzer**: Deep parsing for memory access and logic bugs.
*   **Cppcheck**: Rapid detection of common buffer overflows, uninitialized memory, and leaks.
*   **Sparse**: Enforces Linux kernel-specific invariants (e.g. correct usage of `__user` pointers vs. kernel pointers, locking contexts).

#### B. Architectural Security Analysis (IBM Bob CLI)
To analyze structural issues, vulnerable APIs, or high-risk library functions:
```bash
./scripts/security/run_ibm_bob.sh
```

#### C. System Kernel Hardening Verification
To verify if your system's kernel has compiled-in self-protection mechanisms:
```bash
./scripts/security/verify_kernel_hardening.sh
```

---

## 🧪 3. Running Automated Tests

To ensure code correctness and verify that scanners are operational, Krynox Nexus provides unit and integration test suites.

### Run All Tests
```bash
make test
```

### A. C-Unit Tests (`cmocka`)
Verifies driver invariants and safety operations by compiling mocked interfaces:
```bash
# Run unit tests
make test-unit

# Generate a visual code coverage HTML report
make coverage

# Open the coverage report in your browser
make view-coverage
```

### B. Integration Tests (`pytest`)
Verifies that all Python converters normalize tool outputs correctly into valid OASIS SARIF files:
```bash
# Install integration test dependencies (first-time only)
make install-test-deps

# Run integration tests
make test-integration

# Run integration tests with detailed verbose output
make test-integration-verbose
```

---

## 🐳 4. Isolated Containerized Workflows (Docker)

If you are on a non-Linux system or do not want to install security tools locally, you can use the pre-built Docker containers.

```bash
# 1. Build the builder and scanner Docker images
make docker-build

# 2. Compile kernel modules in a sandboxed kernel headers container
make docker-build-modules

# 3. Execute all static analysis tools in the scanner container
make docker-scan

# 4. Clean up container volumes and images
make docker-clean
```

---

## 📊 5. Report Visualization (Dashboard Portal)

Once your security scans are complete, you can generate an interactive, responsive HTML dashboard to inspect all findings in one place.

```bash
# Compile scan and coverage metrics into reports/index.html
make reports

# View the dashboard in your system's default browser
make view-reports
```

*The generated dashboard at `reports/index.html` displays tool-specific tab filters, finding locations, code context snippets, and CWE descriptions.*

---

## 📝 6. Integrating a New Kernel Module

To add your own custom kernel module to the Krynox Nexus security pipeline:

1.  **Add your C file** under the `src/` directory (e.g., `src/my_driver.c`).
2.  **Hardening Best Practices**: Ensure you adhere to the zero-trust secure principles:
    *   Initialize all structures before use.
    *   Avoid unbounded string functions; use `strscpy()` instead of `strcpy()`.
    *   Sanitize all user-space inputs explicitly via `copy_from_user()`.
    *   Immediately clear deallocated pointers (`kfree(ptr); ptr = NULL;`).
3.  **Update Kbuild**: Add your module object to the `src/Kbuild` configuration:
    ```make
    obj-m += my_driver.o
    ```
4.  **Validate**: Run your compilation and scan suite local tests:
    ```bash
    make build
    make security-scan
    ```
5.  **Push**: Once clean, push your branch to trigger the CI/CD Actions quality gates.
