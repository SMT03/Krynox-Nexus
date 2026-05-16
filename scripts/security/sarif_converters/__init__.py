"""
SARIF Converters Package
Krynox Nexus - Zero-Trust Kernel Module Hardening

This package provides converters to transform security tool outputs
into SARIF 2.1.0 format for GitHub Security tab integration.

Supported Tools:
- Clang Static Analyzer
- Cppcheck
- Sparse
- IBM Bob CLI
- Kernel Hardening Checks
"""

__version__ = "1.0.0"
__author__ = "Bob (Security Architect)"

from .base_converter import BaseSARIFConverter, Finding
from .cwe_mappings import get_cwe_id, get_cwe_name, CWE_DATABASE

__all__ = [
    'BaseSARIFConverter',
    'Finding',
    'get_cwe_id',
    'get_cwe_name',
    'CWE_DATABASE',
]

# Made with Bob
