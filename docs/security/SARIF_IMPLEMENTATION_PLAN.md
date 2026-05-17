# SARIF Implementation Plan
## Krynox Nexus - Zero-Trust Kernel Module Hardening

**Version:** 1.0.0  
**Date:** 2026-05-17  
**Status:** Planning Phase  
**Owner:** Krynox Security Agent (Security Architect)

---

## 📋 Executive Summary

This document outlines the comprehensive plan to implement proper SARIF (Static Analysis Results Interchange Format) converters for all security scanning tools in the Krynox Nexus project. The implementation will enable seamless integration with GitHub Security tab, providing centralized vulnerability tracking and management.

### Goals
- Convert all security tool outputs to valid SARIF 2.1.0 format
- Enable GitHub Security tab integration for all findings
- Add CodeQL analysis for additional security coverage
- Implement comprehensive workflow status badges
- Maintain backward compatibility with existing reports

---

## 🎯 Current State Analysis

### Existing SARIF Implementation

#### What Works
- GitHub Actions workflow configured with SARIF upload steps
- Basic SARIF file structure in place
- Trivy container scanning already produces valid SARIF

#### What's Missing
1. **Empty SARIF Files**: Current converters generate placeholder SARIF with no results
2. **No Tool Output Parsing**: Shell scripts don't parse tool outputs into SARIF format
3. **Missing CWE Mappings**: No Common Weakness Enumeration mappings
4. **No Severity Levels**: SARIF results lack proper severity classification
5. **Incomplete Location Data**: Missing file paths, line numbers, and code snippets

### Tool Output Formats

| Tool | Current Output | SARIF Status | Complexity |
|------|---------------|--------------|------------|
| Clang Static Analyzer | Text/HTML | Placeholder | Medium |
| Cppcheck | XML + Text | Placeholder | Low |
| Sparse | Text | Placeholder | Medium |
| IBM Bob CLI | JSON | Placeholder | Low |
| Kernel Hardening | Text | Not implemented | High |
| Trivy | SARIF | Working | N/A |

---

## 🏗️ Architecture Design

### Hybrid Approach: Shell + Python

**Rationale:**
- Shell scripts orchestrate the security pipeline (existing infrastructure)
- Python converters handle complex parsing and SARIF generation
- Best of both worlds: Simple deployment + robust parsing

### Component Architecture

```
Security Pipeline → Tool Execution → Python SARIF Converter → Valid SARIF → GitHub Security Tab
```

---

## 📦 Implementation Components

### 1. Python SARIF Converter Module

**Location:** `scripts/security/sarif_converters/`

**Structure:**
```
scripts/security/sarif_converters/
├── __init__.py
├── base_converter.py          # Base class for all converters
├── clang_converter.py         # Clang Static Analyzer
├── cppcheck_converter.py      # Cppcheck XML parser
├── sparse_converter.py        # Sparse text parser
├── bob_converter.py           # IBM Bob JSON converter
├── hardening_converter.py     # Kernel hardening checks
├── sarif_builder.py           # SARIF 2.1.0 builder utility
├── cwe_mappings.py            # CWE database
└── requirements.txt           # Python dependencies
```

**Dependencies:**
```
sarif-om==1.0.4              # Official SARIF object model
lxml==4.9.3                  # XML parsing for Cppcheck
jsonschema==4.19.0           # SARIF validation
```

### 2. Base Converter Class

**Key Features:**
- SARIF 2.1.0 schema compliance
- CWE mapping integration
- Severity level normalization
- File path resolution
- Code snippet extraction
- Result deduplication

### 3. Tool-Specific Converters

#### Clang Static Analyzer
- Parse text output with regex patterns
- Map Clang warnings to CWE IDs
- Extract code context from source files

#### Cppcheck
- Parse XML output with lxml
- Use existing CWE IDs from Cppcheck
- Map severity levels to SARIF

#### Sparse
- Parse kernel-specific warnings
- Map to appropriate CWE IDs
- Handle context warnings

#### IBM Bob CLI
- Direct JSON parsing (simplest)
- Preserve architectural context
- Use existing CWE mappings

#### Kernel Hardening
- Parse check results
- Create SARIF for failed checks
- Include remediation guidance

---

## 🔧 Shell Script Integration

### Updated run_static_analysis.sh

**New Function:**
```bash
convert_to_sarif() {
    local tool=$1
    local input_file=$2
    local output_file=$3
    
    python3 "$SCRIPT_DIR/sarif_converters/${tool}_converter.py" \
        --input "$input_file" \
        --output "$output_file" \
        --project-root "$PROJECT_ROOT"
}
```

### Updated run_ibm_bob.sh

**New Function:**
```bash
convert_bob_to_sarif() {
    python3 "$SCRIPT_DIR/sarif_converters/bob_converter.py" \
        --input-dir "$REPORT_DIR/json" \
        --output "$REPORT_DIR/sarif/bob_results.sarif" \
        --project-root "$PROJECT_ROOT"
}
```

---

## 🔄 GitHub Actions Workflow Updates

### 1. Add CodeQL Analysis Job

```yaml
codeql-analysis:
  name: CodeQL Security Analysis
  runs-on: ubuntu-latest
  permissions:
    actions: read
    contents: read
    security-events: write
  
  strategy:
    fail-fast: false
    matrix:
      language: ['cpp']
  
  steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Initialize CodeQL
      uses: github/codeql-action/init@v3
      with:
        languages: ${{ matrix.language }}
        queries: security-extended,security-and-quality
    
    - name: Build kernel modules
      run: make clean all
    
    - name: Perform CodeQL Analysis
      uses: github/codeql-action/analyze@v3
```

### 2. Update Static Analysis Job

```yaml
- name: Install Python dependencies
  run: |
    pip3 install -r scripts/security/sarif_converters/requirements.txt

- name: Upload SARIF to GitHub Security
  if: always()
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: reports/static-analysis/sarif/
    category: static-analysis
```

---

## 📊 README.md Badge Updates

### Enhanced Badges

```markdown
## 🛡️ Security & Quality

[![Security Scan](https://github.com/krynox-nexus/krynox-nexus/actions/workflows/security-scan.yml/badge.svg)](https://github.com/krynox-nexus/krynox-nexus/actions/workflows/security-scan.yml)
[![CodeQL](https://github.com/krynox-nexus/krynox-nexus/actions/workflows/security-scan.yml/badge.svg?job=codeql-analysis)](https://github.com/krynox-nexus/krynox-nexus/security/code-scanning)
[![License: GPL v2](https://img.shields.io/badge/License-GPL%20v2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)

## 📊 Security Analysis

[![Static Analysis](https://github.com/krynox-nexus/krynox-nexus/actions/workflows/security-scan.yml/badge.svg?job=static-analysis)](https://github.com/krynox-nexus/krynox-nexus/actions)
[![IBM Bob](https://github.com/krynox-nexus/krynox-nexus/actions/workflows/security-scan.yml/badge.svg?job=ibm-bob-analysis)](https://github.com/krynox-nexus/krynox-nexus/actions)
[![Container Security](https://github.com/krynox-nexus/krynox-nexus/actions/workflows/security-scan.yml/badge.svg?job=container-security)](https://github.com/krynox-nexus/krynox-nexus/actions)

## 🔒 Security Findings

View all security findings in the [GitHub Security tab](https://github.com/krynox-nexus/krynox-nexus/security/code-scanning).
```

---

## 🧪 Testing Strategy

### 1. Local Testing

Create test fixtures and validate SARIF output:

```bash
# Test each converter
python3 scripts/security/sarif_converters/clang_converter.py \
    --input tests/fixtures/clang_output.txt \
    --output /tmp/clang_test.sarif \
    --validate
```

### 2. Feature Branch Testing

**Branch:** `feature/sarif-implementation`

**Test Plan:**
1. Create feature branch
2. Implement converters incrementally
3. Test each converter individually
4. Push to GitHub and verify CI/CD
5. Check Security tab for findings
6. Verify SARIF uploads are successful

### 3. Integration Testing

**Test Cases:**
- Clang findings appear in Security tab
- Cppcheck findings appear in Security tab
- Sparse findings appear in Security tab
- IBM Bob findings appear in Security tab
- CodeQL findings appear in Security tab
- All findings have correct severity levels
- All findings have CWE mappings
- Code snippets are displayed correctly

---

## 📅 Implementation Timeline

### Phase 1: Foundation (Week 1)
- Create implementation plan
- Set up Python converter module structure
- Implement base converter class
- Create CWE mapping database

### Phase 2: Tool Converters (Week 2)
- Implement Cppcheck converter (easiest - XML input)
- Implement IBM Bob converter (easy - JSON input)
- Implement Clang converter (medium - text parsing)
- Implement Sparse converter (medium - text parsing)
- Implement Kernel Hardening converter (complex)

### Phase 3: Integration (Week 3)
- Update shell scripts to call converters
- Test converters with real tool outputs
- Validate SARIF output against schema
- Create test fixtures for CI/CD

### Phase 4: Workflow Enhancement (Week 4)
- Add CodeQL analysis job
- Update all workflow jobs for SARIF upload
- Test workflow in feature branch
- Verify Security tab integration

### Phase 5: Documentation & Polish (Week 5)
- Update README.md with new badges
- Create SARIF converter documentation
- Write user guide for Security tab
- Create PR and merge to main

---

## 🎯 Success Criteria

### Technical Requirements
- All SARIF files validate against SARIF 2.1.0 schema
- All security findings appear in GitHub Security tab
- Each finding has file path, line number, and severity
- CWE mappings are accurate and complete
- Code snippets are extracted and displayed
- False positive rate < 5%

### Operational Requirements
- Pipeline execution time < 15 minutes
- SARIF conversion adds < 30 seconds per tool
- All converters handle errors gracefully
- Backward compatibility with existing reports

---

## 🚨 Risk Mitigation

| Risk | Mitigation |
|------|------------|
| SARIF Schema Complexity | Use sarif-om library for compliance |
| Tool Output Format Changes | Version-specific parsers with fallback |
| Performance Impact | Parallel conversion, caching |
| False Positives | Tuning, filtering, confidence scores |
| GitHub API Rate Limits | Batch uploads, retry logic |

---

## 📚 References

- [SARIF 2.1.0 Specification](https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html)
- [GitHub Code Scanning API](https://docs.github.com/en/code-security/code-scanning/integrating-with-code-scanning/sarif-support-for-code-scanning)
- [CWE Database](https://cwe.mitre.org/)
- [CodeQL Documentation](https://codeql.github.com/docs/)

---

**Document Version:** 1.0.0  
**Last Updated:** 2026-05-17  
**Next Review:** 2026-05-24

---

*This plan is a living document and will be updated as implementation progresses.*