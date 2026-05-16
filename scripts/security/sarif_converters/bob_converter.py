#!/usr/bin/env python3
"""
IBM Bob CLI to SARIF Converter
Krynox Nexus - Zero-Trust Kernel Module Hardening

Converts IBM Bob CLI JSON output to SARIF 2.1.0 format.
"""

import sys
import json
import argparse
from typing import List, Dict, Any
from pathlib import Path

from base_converter import BaseSARIFConverter, Finding


class BobConverter(BaseSARIFConverter):
    """
    Converter for IBM Bob CLI JSON output to SARIF format.
    
    IBM Bob produces JSON output with findings containing:
    - severity: Finding severity (critical, high, medium, low)
    - category: Vulnerability category
    - message: Finding description
    - file: Source file path
    - line: Line number
    - cwe: CWE ID (if available)
    """
    
    def __init__(self, tool_version: str = "1.0.0", project_root: str = "."):
        """
        Initialize IBM Bob converter.
        
        Args:
            tool_version: IBM Bob CLI version
            project_root: Root directory of the project
        """
        super().__init__("IBM Bob CLI", tool_version, project_root)
    
    def parse_output(self, output_file: str) -> List[Finding]:
        """
        Parse IBM Bob JSON output.
        
        Args:
            output_file: Path to IBM Bob JSON output file
            
        Returns:
            List of Finding objects
        """
        findings = []
        
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle both single file and directory scan formats
            if isinstance(data, dict):
                if 'findings' in data:
                    # Single file format
                    findings.extend(self._parse_findings(data['findings']))
                elif 'files' in data:
                    # Directory scan format
                    for file_data in data['files']:
                        if 'findings' in file_data:
                            findings.extend(self._parse_findings(file_data['findings']))
            elif isinstance(data, list):
                # Direct list of findings
                findings.extend(self._parse_findings(data))
        
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}", file=sys.stderr)
            return []
        except Exception as e:
            print(f"Error processing IBM Bob output: {e}", file=sys.stderr)
            return []
        
        return findings
    
    def _parse_findings(self, findings_data: List[Dict[str, Any]]) -> List[Finding]:
        """
        Parse findings from IBM Bob JSON data.
        
        Args:
            findings_data: List of finding dictionaries
            
        Returns:
            List of Finding objects
        """
        findings = []
        
        for item in findings_data:
            # Extract finding data
            severity = item.get('severity', 'medium')
            category = item.get('category', 'general')
            message = item.get('message', 'No message')
            file_path = item.get('file', item.get('path', 'unknown'))
            line_number = int(item.get('line', item.get('line_number', 0)))
            column = int(item.get('column', item.get('column_number', 1)))
            cwe = item.get('cwe', None)
            confidence = item.get('confidence', 'medium')
            
            # Make path relative
            rel_path = self.get_relative_path(file_path)
            
            # Extract code snippet
            code_snippet = self.extract_code_snippet(rel_path, line_number)
            
            # Create rule ID from category and severity
            rule_id = self._create_rule_id(category, item.get('rule_id', None))
            
            finding = Finding(
                rule_id=rule_id,
                message=message,
                file_path=rel_path,
                line_number=line_number,
                column_number=column,
                severity=self.normalize_severity(severity),
                cwe_ids=self.extract_cwe_ids(message, cwe),
                code_snippet=code_snippet,
                category=category,
                confidence=confidence.lower() if confidence else 'medium'
            )
            findings.append(finding)
        
        return findings
    
    def _create_rule_id(self, category: str, rule_id: str | None = None) -> str:
        """
        Create a rule ID from category and optional rule ID.
        
        Args:
            category: Vulnerability category
            rule_id: Optional existing rule ID
            
        Returns:
            Rule ID string
        """
        if rule_id:
            return rule_id
        
        # Create rule ID from category
        return f"bob-{category.lower().replace(' ', '-').replace('_', '-')}"
    
    def normalize_severity(self, tool_severity: str) -> str:
        """
        Normalize IBM Bob severity to SARIF levels.
        
        Args:
            tool_severity: IBM Bob severity string
            
        Returns:
            SARIF severity level
        """
        severity_map = {
            'critical': 'error',
            'high': 'error',
            'medium': 'warning',
            'low': 'note',
            'info': 'note',
            'informational': 'note',
        }
        return severity_map.get(tool_severity.lower(), 'warning')


def main():
    """Main entry point for command-line usage."""
    parser = argparse.ArgumentParser(
        description='Convert IBM Bob CLI JSON output to SARIF 2.1.0 format'
    )
    parser.add_argument(
        '--input',
        required=True,
        help='Path to IBM Bob JSON output file'
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
    converter = BobConverter(project_root=args.project_root)
    
    if args.verbose:
        print(f"Converting IBM Bob output: {args.input}")
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



