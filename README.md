# 🔒 Krynox Nexus

**Zero-Trust Kernel Module Hardening and CI/CD Pipeline**

## 🛡️ Security Pipeline Status

[![Security Scan](https://github.com/krynox-nexus/krynox-nexus/actions/workflows/security-scan.yml/badge.svg)](https://github.com/krynox-nexus/krynox-nexus/actions/workflows/security-scan.yml)
[![CodeQL](https://github.com/krynox-nexus/krynox-nexus/actions/workflows/security-scan.yml/badge.svg?job=codeql-analysis)](https://github.com/krynox-nexus/krynox-nexus/actions/workflows/security-scan.yml)
[![Static Analysis](https://github.com/krynox-nexus/krynox-nexus/actions/workflows/security-scan.yml/badge.svg?job=static-analysis)](https://github.com/krynox-nexus/krynox-nexus/actions/workflows/security-scan.yml)
[![IBM Bob](https://github.com/krynox-nexus/krynox-nexus/actions/workflows/security-scan.yml/badge.svg?job=ibm-bob-analysis)](https://github.com/krynox-nexus/krynox-nexus/actions/workflows/security-scan.yml)
[![Container Security](https://github.com/krynox-nexus/krynox-nexus/actions/workflows/security-scan.yml/badge.svg?job=container-security)](https://github.com/krynox-nexus/krynox-nexus/actions/workflows/security-scan.yml)
[![Kernel Hardening](https://github.com/krynox-nexus/krynox-nexus/actions/workflows/security-scan.yml/badge.svg?job=kernel-hardening)](https://github.com/krynox-nexus/krynox-nexus/actions/workflows/security-scan.yml)

## 📊 Project Info

[![License: GPL v2](https://img.shields.io/badge/License-GPL%20v2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)
[![Kernel: 5.15+](https://img.shields.io/badge/Kernel-5.15%2B-orange.svg)](https://www.kernel.org/)
[![SARIF: 2.1.0](https://img.shields.io/badge/SARIF-2.1.0-green.svg)](https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)

> **Automated detection and remediation of memory safety vulnerabilities and privilege escalation risks in custom Linux kernel modules.**

Krynox Nexus is a comprehensive security pipeline designed for secure edge device deployment, featuring automated vulnerability detection, multi-layered security analysis, and continuous monitoring of Linux kernel modules written in C/C++.

---

## 🎯 Project Overview

Krynox Nexus implements a **zero-trust security architecture** for kernel module development, ensuring that every code change undergoes rigorous security validation before deployment. The project combines multiple industry-standard security tools with custom analysis scripts to provide comprehensive coverage of common kernel vulnerabilities.

### Key Features

- 🛡️ **Zero-Trust Architecture**: Never trust, always verify - every commit is scanned
- 🔍 **Multi-Tool Analysis**: IBM Bob CLI, Clang, Cppcheck, Sparse, and more
- 🤖 **Automated CI/CD**: GitHub Actions-based security pipeline
- 📊 **Comprehensive Reporting**: JSON, HTML, and SARIF format reports
- 🐳 **Containerized Scanning**: Isolated, reproducible security analysis
- 🎓 **Educational**: Includes intentionally vulnerable modules for testing

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Developer Commits Code                   │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  GitHub Actions Trigger                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
┌──────────────┐ ┌──────────┐ ┌──────────────┐
│    Build     │ │  Static  │ │   IBM Bob    │
│   Modules    │ │ Analysis │ │   Analysis   │
└──────┬───────┘ └────┬─────┘ └──────┬───────┘
       │              │              │
       └──────────────┼──────────────┘
                      │
                      ▼
            ┌─────────────────┐
            │ Security Report │
            │   Generation    │
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │  Quality Gate   │
            │   Pass/Fail     │
            └─────────────────┘
```

---

## 🚀 Quick Start

> 📖 **New to the project?** Check out the comprehensive [Zero-Trust Developer Usage Guide](docs/security/USAGE_GUIDE.md) for step-by-step instructions on compilation, automated scanning, testing, report dashboarding, and Docker sandboxing!

### Prerequisites

- Linux kernel 5.15 or higher
- GCC 9.0+ or Clang 10.0+
- Docker (optional, for containerized scanning)
- Node.js 18+ (for IBM Bob CLI)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/krynox-nexus/krynox-nexus.git
   cd krynox-nexus
   ```

2. **Install security tools**
   ```bash
   sudo ./scripts/setup/install_tools.sh
   ```

3. **Build kernel modules**
   ```bash
   ./scripts/build/build_modules.sh
   ```

4. **Run security scans**
   ```bash
   # Static analysis
   ./scripts/security/run_static_analysis.sh
   
   # IBM Bob analysis
   ./scripts/security/run_ibm_bob.sh
   ```

---

## 📁 Project Structure

```
krynox-nexus/
├── src/                          # Kernel module source code
│   ├── examples/                 # Secure example modules
│   │   └── hello_secure.c       # Secure "Hello World" module
│   ├── vulnerable/               # Intentionally vulnerable modules
│   │   ├── buffer_overflow.c    # Buffer overflow examples
│   │   └── use_after_free.c     # Use-after-free examples
│   └── Kbuild                    # Kernel build configuration
│
├── scripts/                      # CI/CD and automation scripts
│   ├── setup/                    # Environment setup
│   │   └── install_tools.sh     # Install security tools
│   ├── build/                    # Build automation
│   │   └── build_modules.sh     # Compile kernel modules
│   ├── security/                 # Security scanning
│   │   ├── run_ibm_bob.sh       # IBM Bob CLI integration
│   │   └── run_static_analysis.sh # Static analysis tools
│   └── reporting/                # Report generation
│
├── tests/                        # Automated security tests
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   └── fixtures/                 # Test data
│
├── .github/workflows/            # GitHub Actions workflows
│   └── security-scan.yml        # Main security pipeline
│
├── docker/                       # Docker configurations
│   ├── Dockerfile.scanner       # Security scanner image
│   └── Dockerfile.builder       # Build environment image
│
├── docs/                         # Documentation
│   ├── architecture/             # Architecture diagrams
│   ├── security/                 # Security documentation
│   └── tools/                    # Tool-specific guides
│
├── config/                       # Tool configurations
│   ├── .clang-tidy              # Clang-Tidy config
│   └── .cppcheck                # Cppcheck config
│
├── AGENTS.md                     # AI agent role definition
├── README.md                     # This file
├── SECURITY.md                   # Security policies
├── CONTRIBUTING.md               # Contribution guidelines
├── LICENSE                       # GPL v2 license
└── Makefile                      # Build automation
```

---

## 🔧 Security Tools

Krynox Nexus integrates multiple industry-standard security tools:

### Static Analysis
- **Clang Static Analyzer**: Deep semantic analysis of C/C++ code
- **Cppcheck**: Fast static analysis for common bugs and vulnerabilities
- **Sparse**: Linux kernel-specific semantic checker

### Architectural Analysis
- **IBM Bob CLI**: Architectural vulnerability detection and remediation guidance

### Memory Safety
- **Valgrind**: Memory leak and error detection
- **AddressSanitizer (ASan)**: Fast memory error detector
- **KASan**: Kernel Address Sanitizer for runtime detection

### Fuzzing (Planned)
- **Syzkaller**: Coverage-guided kernel fuzzer
- **AFL++**: Advanced fuzzing for kernel modules

### Container Security
- **Trivy**: Container vulnerability scanner
- **Docker**: Isolated scanning environments

---

## 📊 Security Reports

All security scans generate comprehensive reports in multiple formats:

- **JSON**: Machine-readable format for automation
- **HTML**: Human-readable reports with visualizations
- **SARIF 2.1.0**: GitHub Security tab integration with CWE mappings
- **Text**: Console-friendly output

Reports are automatically uploaded to GitHub Actions artifacts and can be viewed in the Actions tab.

### 🔍 SARIF Integration

Krynox Nexus implements comprehensive SARIF (Static Analysis Results Interchange Format) 2.1.0 support for seamless integration with GitHub's Security tab:

**Supported Tools:**
- ✅ **CodeQL**: Native SARIF support for C/C++ analysis
- ✅ **Clang Static Analyzer**: Custom converter with regex-based parsing
- ✅ **Cppcheck**: XML to SARIF conversion with CWE mapping
- ✅ **Sparse**: Kernel-specific warning conversion
- ✅ **IBM Bob CLI**: Architectural analysis JSON to SARIF
- ✅ **Kernel Hardening**: Configuration check results to SARIF
- ✅ **Trivy**: Container vulnerability scanning

**Features:**
- 🎯 **CWE Mapping**: 40+ kernel-specific vulnerability patterns
- 📍 **Precise Locations**: Line numbers, columns, and code snippets
- 🔢 **Severity Levels**: Error, Warning, Note classifications
- 🏷️ **Categorization**: Separate categories for each analysis type
- 📝 **Rich Metadata**: Tool versions, execution timestamps, rule descriptions

**View Results:**
Navigate to the **Security** tab in your GitHub repository to view all SARIF findings in a unified dashboard. Each security tool uploads results to a separate category for easy filtering and analysis.

For detailed guides and implementation documentation, see:
- 📖 [Zero-Trust Developer Usage Guide](docs/security/USAGE_GUIDE.md) *(Highly Recommended)*
- [SARIF Implementation Plan](docs/security/SARIF_IMPLEMENTATION_PLAN.md)
- [SARIF Quick Reference](docs/security/SARIF_QUICK_REFERENCE.md)
- [SARIF Workflow Diagram](docs/security/SARIF_WORKFLOW_DIAGRAM.md)

---

## 🎓 Educational Modules

Krynox Nexus includes intentionally vulnerable kernel modules for educational purposes and pipeline testing:

### Vulnerable Modules (⚠️ DO NOT USE IN PRODUCTION)

1. **buffer_overflow.c**
   - Stack buffer overflow (CWE-121)
   - Heap buffer overflow (CWE-122)
   - Format string vulnerability (CWE-134)

2. **use_after_free.c**
   - Use-after-free (CWE-416)
   - Double-free (CWE-415)
   - Memory leaks (CWE-401)
   - Dangling pointers

These modules are designed to test the detection capabilities of the security pipeline and should **never** be loaded on production systems.

---

## 🔒 Zero-Trust Principles

Krynox Nexus implements the following zero-trust principles:

1. **Verify Explicitly**: Every code change undergoes comprehensive security validation
2. **Least Privilege**: Modules are tested for proper permission handling
3. **Assume Breach**: Design assumes attackers may have partial access
4. **Defense in Depth**: Multiple layers of security controls
5. **Continuous Validation**: Security is an ongoing process, not a one-time check

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run security scans locally
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

All pull requests automatically trigger the security pipeline. PRs with critical security issues will be blocked from merging.

---

## 📈 Metrics & KPIs

Krynox Nexus tracks the following security metrics:

- **Vulnerability Detection Rate**: Percentage of known vulnerabilities detected
- **False Positive Rate**: Accuracy of security findings
- **Mean Time to Detection (MTTD)**: Average time from commit to detection
- **Mean Time to Remediation (MTTR)**: Average time from detection to fix
- **Pipeline Execution Time**: Time to complete full security scan
- **Security Debt**: Number of unresolved security findings

---

---

## 📜 License

This project is licensed under the GNU General Public License v2.0 - see the [LICENSE](LICENSE) file for details.

Kernel modules must comply with GPL v2 as required by the Linux kernel.

---

## 🙏 Acknowledgments

- **Linux Kernel Community**: For the robust kernel module framework
- **IBM Research**: For the Bob CLI architectural analysis tool
- **LLVM Project**: For Clang Static Analyzer
- **Cppcheck Team**: For the excellent static analysis tool
- **Sparse Developers**: For kernel-specific semantic checking

---

## 🗺️ Roadmap

### Phase 1: Foundation ✅
- [x] Project structure and build system
- [x] Sample secure and vulnerable modules
- [x] Basic CI/CD pipeline
- [x] Static analysis integration

### Phase 2: Advanced Security (In Progress)
- [x] IBM Bob CLI integration
- [ ] Memory safety tool integration
- [ ] Fuzzing infrastructure
- [ ] Runtime monitoring with eBPF

### Phase 3: Intelligence & Automation
- [ ] Machine learning for vulnerability prediction
- [ ] Automated patch generation
- [ ] Security regression testing
- [ ] Interactive training modules

### Phase 4: Enterprise Features
- [ ] Multi-platform support (ARM, RISC-V)
- [ ] Compliance reporting (NIST, CIS)
- [ ] Security certification program
- [ ] Enterprise dashboard

---

<div align="center">

*Securing the kernel, one module at a time.*

</div>