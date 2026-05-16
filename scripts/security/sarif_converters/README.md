# SARIF Converters
## Krynox Nexus - Zero-Trust Kernel Module Hardening

This directory contains Python converters that transform security tool outputs into SARIF 2.1.0 format for GitHub Security tab integration.

---

## 📦 Module Structure

```
sarif_converters/
├── __init__.py                 # Package initialization
├── base_converter.py           # Base class for all converters
├── cwe_mappings.py             # CWE database and mappings
├── clang_converter.py          # Clang Static Analyzer converter
├── cppcheck_converter.py       # Cppcheck XML converter
├── sparse_converter.py         # Sparse text converter
├── bob_converter.py            # IBM Bob JSON converter
├── hardening_converter.py      # Kernel hardening converter
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## 🚀 Installation

```bash
# Install dependencies
pip3 install -r requirements.txt
```

---

## 📖 Usage

### Command Line

Each converter can be run standalone:

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

# With validation
python3 clang_converter.py \
    --input reports/clang/analysis.txt \
    --output reports/sarif/clang.sarif \
    --validate
```

### From Shell Scripts

```bash
# In run_static_analysis.sh
python3 "$SCRIPT_DIR/sarif_converters/clang_converter.py" \
    --input "$REPORT_DIR/clang/analysis.txt" \
    --output "$REPORT_DIR/sarif/clang.sarif" \
    --project-root "$PROJECT_ROOT"
```

### As Python Module

```python
from sarif_converters.clang_converter import ClangConverter

converter = ClangConverter(
    tool_version="14.0.0",
    project_root="/path/to/project"
)

success = converter.convert(
    input_file="reports/clang/analysis.txt",
    output_file="reports/sarif/clang.sarif",
    validate=True
)
```

---

## 🏗️ Architecture

### Base Converter Class

All converters inherit from `BaseSARIFConverter`, which provides:

- **Parsing**: Abstract method for tool-specific parsing
- **SARIF Generation**: Convert findings to SARIF 2.1.0 format
- **CWE Mapping**: Automatic CWE ID extraction and mapping
- **Validation**: SARIF schema validation
- **File I/O**: Read tool output, write SARIF files

### Finding Data Class

Represents a security finding:

```python
@dataclass
class Finding:
    rule_id: str
    message: str
    file_path: str
    line_number: int
    column_number: int = 1
    severity: str = "warning"
    cwe_ids: List[int] = []
    code_snippet: Optional[str] = None
    category: Optional[str] = None
    confidence: str = "medium"
```

---

## 🔧 Implementing a New Converter

1. **Create converter file**: `my_tool_converter.py`

2. **Inherit from BaseSARIFConverter**:

```python
from base_converter import BaseSARIFConverter, Finding

class MyToolConverter(BaseSARIFConverter):
    def __init__(self, tool_version: str, project_root: str = "."):
        super().__init__("My Tool", tool_version, project_root)
    
    def parse_output(self, output_file: str) -> List[Finding]:
        findings = []
        # Parse tool output
        # Create Finding objects
        return findings
```

3. **Add CLI interface**:

```python
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--validate", action="store_true")
    args = parser.parse_args()
    
    converter = MyToolConverter("1.0.0", args.project_root)
    success = converter.convert(args.input, args.output, args.validate)
    exit(0 if success else 1)
```

---

## 📊 CWE Mappings

The `cwe_mappings.py` module provides:

- **CWE Database**: 40+ common kernel vulnerabilities
- **Keyword Matching**: Automatic CWE ID extraction from messages
- **Severity Mapping**: Default severity levels for each CWE

### Example Usage

```python
from cwe_mappings import get_cwe_id, get_cwe_name

# Get CWE ID from description
cwe_id = get_cwe_id("buffer overflow detected")
# Returns: "CWE-120"

# Get CWE name
name = get_cwe_name("CWE-120")
# Returns: "Buffer Copy without Checking Size of Input"
```

---

## ✅ Validation

All converters validate SARIF output against the SARIF 2.1.0 schema:

```python
converter.validate_sarif(sarif_data)
```

Use `--validate` flag for automatic validation:

```bash
python3 clang_converter.py --input file.txt --output file.sarif --validate
```

---

## 🧪 Testing

### Unit Tests

```bash
# Run all tests
python3 -m pytest tests/

# Run specific converter tests
python3 -m pytest tests/test_clang_converter.py
```

### Manual Testing

```bash
# Test with sample data
python3 clang_converter.py \
    --input tests/fixtures/clang_output.txt \
    --output /tmp/test.sarif \
    --validate

# Verify SARIF
cat /tmp/test.sarif | jq '.'
```

---

## 📚 SARIF 2.1.0 Format

### Structure

```json
{
  "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
  "version": "2.1.0",
  "runs": [{
    "tool": {
      "driver": {
        "name": "Tool Name",
        "version": "1.0.0",
        "rules": [...]
      }
    },
    "results": [...]
  }]
}
```

### Result Object

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
        "uri": "src/file.c"
      },
      "region": {
        "startLine": 45,
        "snippet": {
          "text": "strcpy(buffer, input);"
        }
      }
    }
  }],
  "cweIds": [120]
}
```

---

## 🐛 Troubleshooting

### Import Errors

```bash
# Ensure you're in the correct directory
cd scripts/security/sarif_converters

# Install dependencies
pip3 install -r requirements.txt
```

### Validation Failures

```bash
# Check SARIF structure
cat output.sarif | jq '.runs[0].results | length'

# Validate manually
python3 -c "
import json
from base_converter import BaseSARIFConverter
converter = BaseSARIFConverter('Test', '1.0')
with open('output.sarif') as f:
    sarif = json.load(f)
    print(converter.validate_sarif(sarif))
"
```

### No Findings Generated

1. Check input file exists and has content
2. Verify parsing logic in converter
3. Enable debug output
4. Check file paths are correct

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/krynox-nexus/krynox-nexus/issues)
- **Documentation**: [SARIF Implementation Plan](../../../docs/security/SARIF_IMPLEMENTATION_PLAN.md)
- **Security**: security@krynox-nexus.local

---

## 📝 License

GPL v2 - See [LICENSE](../../../LICENSE)

---

**Made with ❤️ by Bob - Security Architect & Kernel Engineer**