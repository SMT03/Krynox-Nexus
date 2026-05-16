#!/usr/bin/env python3
"""
Sparse to SARIF Converter
Krynox Nexus - Zero-Trust Kernel Module Hardening

Converts Sparse (kernel semantic checker) text output to SARIF 2.1.0 format.
"""

import sys
import re
import argparse
from typing import List
from pathlib import Path

from base_converter import BaseSARIFConverter, Finding


class SparseConverter(BaseSARIFConverter):
    """
    Converter for Sparse text output to SARIF format.
    
    Sparse produces text output in the format:
    file.c:line:column: warning: message
    file.c:line:column: error: message
    """
    
    # Regex pattern for Sparse output
    SPARSE_PATTERN = re.compile(
        r'^(?P<file>[^:]+):(?P<line>\d+):(?P<column>\d+):\s+'
        r'(?P<severity>warning|error|info):\s+'
        r'(?P<message>.+)$'
    )
    
    def __init__(self, tool_version: str = "0.6.4", project_root: str = "."):
        """
        Initialize Sparse converter.
        
        Args:
            tool_version: Sparse version
            project_root: Root directory of the project
        """
        super().__init__("Sparse", tool_version, project_root)
    
    def parse_output(self, output_file: str) -> List[Finding]:
        """
        Parse Sparse text output.
        
        Args:
            output_file: Path to Sparse text output file
            
        Returns:
            List of Finding objects
        """
        findings = []
        
        try:
            with open(output_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Try to match Sparse output pattern
                match = self.SPARSE_PATTERN.match(line)
                
                if match:
                    file_path = match.group('file')
                    line_number = int(match.group('line'))
                    column = int(match.group('column'))
                    severity = match.group('severity')
                    message = match.group('message')
                    
                    # Make path relative
                    rel_path = self.get_relative_path(file_path)
                    
                    # Extract code snippet
                    code_snippet = self.extract_code_snippet(rel_path, line_number)
                    
                    # Create rule ID from message
                    rule_id = self._create_rule_id(message)
                    
                    # Determine category
                    category = self._get_category(message)
                    
                    finding = Finding(
                        rule_id=rule_id,
                        message=message,
                        file_path=rel_path,
                        line_number=line_number,
                        column_number=column,
                        severity=self.normalize_severity(severity),
                        cwe_ids=self.extract_cwe_ids(message),
                        code_snippet=code_snippet,
                        category=category,
                        confidence='high' if severity == 'error' else 'medium'
                    )
                    findings.append(finding)
        
        except Exception as e:
            print(f"Error processing Sparse output: {e}", file=sys.stderr)
            return []
        
        return findings
    
    def _create_rule_id(self, message: str) -> str:
        """
        Create a rule ID from the warning message.
        
        Args:
            message: Warning message
            
        Returns:
            Rule ID string
        """
        message_lower = message.lower()
        
        # Sparse-specific patterns
        if 'context imbalance' in message_lower:
            return 'sparse-context-imbalance'
        elif 'dereference of freed pointer' in message_lower:
            return 'sparse-use-after-free'
        elif 'symbol was not declared' in message_lower:
            return 'sparse-undeclared-symbol'
        elif 'incorrect type' in message_lower:
            return 'sparse-incorrect-type'
        elif 'incompatible types' in message_lower:
            return 'sparse-incompatible-types'
        elif 'cast' in message_lower and 'different address space' in message_lower:
            return 'sparse-address-space-cast'
        elif 'dereference' in message_lower and 'noderef' in message_lower:
            return 'sparse-noderef-dereference'
        elif 'undefined identifier' in message_lower:
            return 'sparse-undefined-identifier'
        elif 'redeclared' in message_lower:
            return 'sparse-redeclaration'
        elif 'bitwise' in message_lower:
            return 'sparse-bitwise-operation'
        elif 'restricted' in message_lower:
            return 'sparse-restricted-type'
        elif 'null pointer' in message_lower:
            return 'sparse-null-pointer'
        elif 'uninitialized' in message_lower:
            return 'sparse-uninitialized'
        else:
            # Generic rule ID
            return 'sparse-warning'
    
    def _get_category(self, message: str) -> str:
        """
        Determine category from message content.
        
        Args:
            message: Warning message
            
        Returns:
            Category string
        """
        message_lower = message.lower()
        
        # Kernel-specific categories
        if 'context' in message_lower or 'lock' in message_lower:
            return 'concurrency'
        elif 'freed pointer' in message_lower or 'use after free' in message_lower:
            return 'memory_safety'
        elif 'null pointer' in message_lower or 'dereference' in message_lower:
            return 'memory_safety'
        elif 'type' in message_lower or 'cast' in message_lower:
            return 'type_safety'
        elif 'address space' in message_lower:
            return 'memory_safety'
        elif 'uninitialized' in message_lower or 'undefined' in message_lower:
            return 'initialization'
        elif 'bitwise' in message_lower or 'restricted' in message_lower:
            return 'type_safety'
        elif 'symbol' in message_lower or 'declared' in message_lower:
            return 'general'
        else:
            return 'general'


def main():
    """Main entry point for command-line usage."""
    parser = argparse.ArgumentParser(
        description='Convert Sparse output to SARIF 2.1.0 format'
    )
    parser.add_argument(
        '--input',
        required=True,
        help='Path to Sparse text output file'
    )
    parser.add_argument(
        '--output',
        required=True,
        help='Path to output SARIF file'
    )
    parser.add_argument(
        '--project-root',
        default='.',
        help='Root directory of the project (default: current directory)'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate SARIF output before writing'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Create converter
    converter = SparseConverter(project_root=args.project_root)
    
    if args.verbose:
        print(f"Converting Sparse output: {args.input}")
        print(f"Output SARIF file: {args.output}")
        print(f"Project root: {args.project_root}")
    
    # Convert
    success = converter.convert(
        input_file=args.input,
        output_file=args.output,
        validate=args.validate
    )
    
    if success:
        if args.verbose:
            print(f"✓ Successfully converted {len(converter.findings)} findings to SARIF")
        sys.exit(0)
    else:
        print("✗ Conversion failed", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()



