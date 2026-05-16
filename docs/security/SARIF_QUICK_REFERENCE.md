# SARIF Implementation Quick Reference
## Krynox Nexus - Developer Guide

**Last Updated:** 2026-05-16

---

## 🚀 Quick Start

### For Implementers

```bash
# 1. Create feature branch
git checkout -b feature/sarif-implementation

# 2. Set up Python environment
cd scripts/security/sarif_converters
pip3 install -r requirements.txt

# 3. Run tests
python3 -m pytest tests/

# 4. Test locally
./scripts/testing/test_sarif_converters.sh
```

### For Reviewers

```bash
# View Security findings
https://github.com/krynox-nexus/krynox-nexus/security/code-scanning

# Check workflow status
https://github.com/krynox-nexus/krynox-nexus/actions
```

---

## 📁 File Structure

```
scripts/security/sarif_converters/
├── __init__.py                 # Package init
├── base_converter.py           # Base class (START HERE)
├── clang_converter.py          # Clang → SARIF
├── cppcheck_converter.py       # Cppcheck → SARIF
├── sparse_converter.py         # Sparse → SARIF
├── bob_converter.py            # IBM Bob → SARIF
├── hardening_converter.py      # Hardening → SARIF
├── sarif_builder.py            # SARIF utilities
├── cwe_mappings.py             # CWE database
└── requirements.txt            # Dependencies
```

---

## 🔧 Converter Usage

### Command Line Interface

```bash
# Clang Converter
python3 clang_converter.py \
    --input reports/clang/analysis.txt \
    --output reports/sarif/clang.sarif \
    --project-root /path/to/project

# Cppcheck Converter
python3 cppcheck_converter.py \
    --input reports/cppcheck/analysis.xml \
    --output reports/sarif/cppcheck.sarif \
    --project-root /path/to/project

# Validate SARIF
python3 clang_converter.py \
    --input reports/clang/analysis.txt \
    --output reports/sarif/clang.sarif \
    --validate
```

### From Shell Scripts

```bash
# In run_static_analysis.sh
convert_to_sarif "clang" \
    "$REPORT_DIR/clang/analysis.txt" \
    "$REPORT_DIR/sarif/clang.sarif"
```

---

## 🎯 CWE Mappings

### Common Kernel Vulnerabilities

| Vulnerability | CWE ID | Severity |
|---------------|--------|----------|
| Buffer Overflow | CWE-120 | Critical |
| Use-After-Free | CWE-416 | Critical |
| Double-Free | CWE-415 | Critical |
| Null Pointer Dereference | CWE-476 | High |
| Race Condition | CWE-362 | High |
| Integer Overflow | CWE-190 | High |
| Memory Leak | CWE-401 | Medium |
| Information Disclosure | CWE-200 | Medium |

### Severity Mapping

```python
SEVERITY_MAP = {
    'critical': 'error',    # Block merge
    'high': 'error',        # Require review
    'medium': 'warning',    # Optional review
    'low': 'note',          # Informational
}
```

---

## 📊 SARIF Structure

### Minimal Valid SARIF

```json
{
  "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
  "version": "2.1.0",
  "runs": [{
    "tool": {
      "driver": {
        "name": "Tool Name",
        "version": "1.0.0"
      }
    },
    "results": []
  }]
}
```

### Complete Finding Example

```json
{
  "ruleId": "buffer-overflow",
  "level": "error",
  "message": {
    "text": "Potential buffer overflow"
  },
  "locations": [{
    "physicalLocation": {
      "artifactLocation": {
        "uri": "src/vulnerable/buffer_overflow.c"
      },
      "region": {
        "startLine": 45,
        "snippet": {
          "text": "strcpy(buffer, user_input);"
        }
      }
    }
  }],
  "cweIds": [120]
}
```

---

## 🧪 Testing Checklist

### Unit Tests
- [ ] Base converter class tests
- [ ] Each tool converter tests
- [ ] CWE mapping tests
- [ ] SARIF builder tests
- [ ] Error handling tests

### Integration Tests
- [ ] Full pipeline test
- [ ] SARIF validation test
- [ ] Shell script integration
- [ ] GitHub upload test

### Acceptance Tests
- [ ] Findings appear in Security tab
- [ ] Correct severity levels
- [ ] CWE IDs present
- [ ] Code snippets displayed
- [ ] No duplicates

---

## 🐛 Troubleshooting

### SARIF Validation Fails

```bash
# Check schema compliance
python3 -c "
import json
import jsonschema
import requests

schema = requests.get('https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json').json()
with open('your-file.sarif') as f:
    sarif = json.load(f)
    jsonschema.validate(sarif, schema)
"
```

### Upload Fails in GitHub Actions

```yaml
# Check permissions
permissions:
  security-events: write
  contents: read
  actions: read

# Check file path
- uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: reports/sarif/  # Directory or file
    category: tool-name         # Unique category
```

### No Findings in Security Tab

1. Check SARIF file has results
2. Verify upload step succeeded
3. Check file paths are relative
4. Ensure CWE IDs are valid
5. Wait 5-10 minutes for processing

---

## 📝 Code Style

### Python Conventions

```python
# Use type hints
def parse_output(self, output_file: str) -> List[Finding]:
    pass

# Use docstrings
def convert_to_sarif(self, findings: List[Finding]) -> dict:
    """
    Convert findings to SARIF 2.1.0 format.
    
    Args:
        findings: List of Finding objects
        
    Returns:
        dict: Valid SARIF JSON structure
    """
    pass

# Handle errors gracefully
try:
    sarif_data = self.convert_to_sarif(findings)
except Exception as e:
    logger.error(f"Conversion failed: {e}")
    return None
```

### Shell Script Conventions

```bash
# Use functions
convert_to_sarif() {
    local tool=$1
    local input=$2
    local output=$3
    
    python3 "converter.py" \
        --input "$input" \
        --output "$output"
}

# Check exit codes
if convert_to_sarif "clang" "$input" "$output"; then
    log_info "✓ Conversion successful"
else
    log_error "✗ Conversion failed"
    return 1
fi
```

---

## 🔍 Debugging Tips

### Enable Verbose Logging

```bash
# In shell scripts
export DEBUG=1
./scripts/security/run_static_analysis.sh

# In Python converters
python3 clang_converter.py --input file.txt --output file.sarif --verbose
```

### Inspect SARIF Output

```bash
# Pretty print SARIF
cat reports/sarif/clang.sarif | jq '.'

# Count findings
cat reports/sarif/clang.sarif | jq '.runs[0].results | length'

# List CWE IDs
cat reports/sarif/clang.sarif | jq '.runs[0].results[].cweIds[]'
```

### Test Individual Components

```python
# Test CWE mapping
from cwe_mappings import get_cwe_id
cwe = get_cwe_id("buffer overflow")
print(f"CWE ID: {cwe}")

# Test SARIF builder
from sarif_builder import SARIFBuilder
builder = SARIFBuilder("Tool Name", "1.0.0")
sarif = builder.build()
print(json.dumps(sarif, indent=2))
```

---

## 📚 Resources

### Documentation
- [SARIF Specification](https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html)
- [GitHub Code Scanning](https://docs.github.com/en/code-security/code-scanning)
- [CWE Database](https://cwe.mitre.org/)

### Tools
- [SARIF Validator](https://sarifweb.azurewebsites.net/Validation)
- [SARIF Viewer](https://microsoft.github.io/sarif-web-component/)
- [jq Manual](https://stedolan.github.io/jq/manual/)

### Examples
- [Microsoft SARIF SDK](https://github.com/microsoft/sarif-sdk)
- [SARIF Tutorials](https://github.com/microsoft/sarif-tutorials)

---

## 🎯 Implementation Priorities

### Phase 1 (Week 1) - Foundation
1. ✅ Create module structure
2. ✅ Implement base converter
3. ✅ Create CWE mappings
4. ⏳ Write unit tests

### Phase 2 (Week 2) - Converters
1. ⏳ Cppcheck (easiest)
2. ⏳ IBM Bob (easy)
3. ⏳ Clang (medium)
4. ⏳ Sparse (medium)
5. ⏳ Hardening (complex)

### Phase 3 (Week 3) - Integration
1. ⏳ Update shell scripts
2. ⏳ Test locally
3. ⏳ Fix issues

### Phase 4 (Week 4) - Workflow
1. ⏳ Add CodeQL
2. ⏳ Update uploads
3. ⏳ Test in feature branch

### Phase 5 (Week 5) - Polish
1. ⏳ Update README
2. ⏳ Documentation
3. ⏳ Merge PR

---

## 💡 Pro Tips

1. **Start Simple**: Implement Cppcheck converter first (XML is easiest)
2. **Validate Early**: Use `--validate` flag during development
3. **Test Incrementally**: Test each converter before moving to next
4. **Use Fixtures**: Create test fixtures for consistent testing
5. **Check Security Tab**: Verify findings appear correctly in GitHub
6. **Monitor Performance**: Ensure SARIF conversion is fast
7. **Handle Errors**: Graceful degradation if conversion fails
8. **Document Edge Cases**: Note any special handling required

---

## 📞 Getting Help

### Issues
- GitHub Issues: [krynox-nexus/issues](https://github.com/krynox-nexus/krynox-nexus/issues)
- Label: `sarif-implementation`

### Questions
- Discussion: [krynox-nexus/discussions](https://github.com/krynox-nexus/krynox-nexus/discussions)
- Tag: `@bob` for security questions

### Security
- Email: security@krynox-nexus.local
- For vulnerabilities in SARIF implementation

---

**Quick Reference Version:** 1.0.0  
**Last Updated:** 2026-05-16

*Keep this guide handy during implementation!*