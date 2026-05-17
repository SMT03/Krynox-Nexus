#!/usr/bin/env python3
"""
Cppcheck to SARIF Converter
Krynox Nexus - Zero-Trust Kernel Module Hardening

Converts Cppcheck XML output to SARIF 2.1.0 format.
"""

import sys
import argparse
from typing import List
from pathlib import Path
import xml.etree.ElementTree as etree

from base_converter import BaseSARIFConverter, Finding


class CppcheckConverter(BaseSARIFConverter):
    """
    Converter for Cppcheck XML output to SARIF format.
    
    Cppcheck produces XML output with error elements containing:
    - id: Error type identifier
    - severity: Error severity (error, warning, style, etc.)
    - msg: Short error message
    - verbose: Detailed error message
    - cwe: CWE ID (if available)
    - location: File path and line number
    """
    
    def __init__(self, tool_version: str = "2.10", project_root: str = "."):
        """
        Initialize Cppcheck converter.
        
        Args:
            tool_version: Cppcheck version
            project_root: Root directory of the project
        """
        super().__init__("Cppcheck", tool_version, project_root)
    
    def parse_output(self, output_file: str) -> List[Finding]:
        """
        Parse Cppcheck XML output.
        
        Args:
            output_file: Path to Cppcheck XML output file
            
        Returns:
            List of Finding objects
        """
        findings = []
        
        try:
            # Parse XML file
            tree = etree.parse(output_file)
            root = tree.getroot()
            
            # Extract Cppcheck version if available
            cppcheck_elem = root.find('cppcheck')
            if cppcheck_elem is not None and 'version' in cppcheck_elem.attrib:
                self.tool_version = cppcheck_elem.attrib['version']
            
            # Find all error elements
            errors = root.findall('.//error')
            
            for error in errors:
                # Extract error attributes
                error_id = error.get('id', 'unknown')
                severity = error.get('severity', 'warning')
                msg = error.get('msg', 'No message')
                verbose = error.get('verbose', msg)
                cwe = error.get('cwe', None)
                
                # Find location elements
                locations = error.findall('location')
                
                if not locations:
                    # If no location, create a generic finding
                    finding = Finding(
                        rule_id=error_id,
                        message=verbose,
                        file_path="unknown",
                        line_number=0,
                        severity=self.normalize_severity(severity),
                        cwe_ids=self.extract_cwe_ids(verbose, cwe),
                        category=self._get_category(error_id),
                        confidence=self._get_confidence(severity)
                    )
                    findings.append(finding)
                else:
                    # Create a finding for each location
                    for location in locations:
                        file_path = location.get('file', 'unknown')
                        line_number = int(location.get('line', '0'))
                        column = int(location.get('column', '1'))
                        
                        # Make path relative
                        rel_path = self.get_relative_path(file_path)
                        
                        # Extract code snippet
                        code_snippet = self.extract_code_snippet(rel_path, line_number)
                        
                        finding = Finding(
                            rule_id=error_id,
                            message=verbose,
                            file_path=rel_path,
                            line_number=line_number,
                            column_number=column,
                            severity=self.normalize_severity(severity),
                            cwe_ids=self.extract_cwe_ids(verbose, cwe),
                            code_snippet=code_snippet,
                            category=self._get_category(error_id),
                            confidence=self._get_confidence(severity)
                        )
                        findings.append(finding)
        
        except etree.ParseError as e:
            print(f"Error parsing XML: {e}", file=sys.stderr)
            return []
        except Exception as e:
            print(f"Error processing Cppcheck output: {e}", file=sys.stderr)
            return []
        
        return findings
    
    def _get_category(self, error_id: str) -> str:
        """
        Get category for Cppcheck error ID.
        
        Args:
            error_id: Cppcheck error identifier
            
        Returns:
            Category string
        """
        category_map = {
            'bufferAccessOutOfBounds': 'memory_safety',
            'arrayIndexOutOfBounds': 'memory_safety',
            'memleakOnRealloc': 'memory_safety',
            'memleak': 'memory_safety',
            'resourceLeak': 'memory_safety',
            'useAfterFree': 'memory_safety',
            'doubleFree': 'memory_safety',
            'nullPointer': 'memory_safety',
            'uninitvar': 'initialization',
            'uninitdata': 'initialization',
            'integerOverflow': 'numeric',
            'signConversion': 'numeric',
            'invalidPointerCast': 'type_safety',
            'cstyleCast': 'type_safety',
            'danglingLifetime': 'memory_safety',
            'danglingReference': 'memory_safety',
        }
        
        # Check for exact match
        if error_id in category_map:
            return category_map[error_id]
        
        # Check for partial matches
        error_lower = error_id.lower()
        if 'buffer' in error_lower or 'memory' in error_lower:
            return 'memory_safety'
        if 'null' in error_lower or 'pointer' in error_lower:
            return 'memory_safety'
        if 'leak' in error_lower:
            return 'memory_safety'
        if 'overflow' in error_lower or 'underflow' in error_lower:
            return 'numeric'
        if 'cast' in error_lower or 'type' in error_lower:
            return 'type_safety'
        if 'uninit' in error_lower:
            return 'initialization'
        
        return 'general'
    
    def _get_confidence(self, severity: str) -> str:
        """
        Get confidence level based on Cppcheck severity.
        
        Args:
            severity: Cppcheck severity level
            
        Returns:
            Confidence level: high, medium, or low
        """
        confidence_map = {
            'error': 'high',
            'warning': 'medium',
            'style': 'low',
            'performance': 'low',
            'portability': 'low',
            'information': 'low',
        }
        return confidence_map.get(severity.lower(), 'medium')


def main():
    """Main entry point for command-line usage."""
    parser = argparse.ArgumentParser(
        description='Convert Cppcheck XML output to SARIF 2.1.0 format'
    )
    parser.add_argument(
        '--input',
        required=True,
        help='Path to Cppcheck XML output file'
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
    converter = CppcheckConverter(project_root=args.project_root)
    
    if args.verbose:
        print(f"Converting Cppcheck output: {args.input}")
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



