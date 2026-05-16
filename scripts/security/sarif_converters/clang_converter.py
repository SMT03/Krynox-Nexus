#!/usr/bin/env python3
"""
Clang Static Analyzer to SARIF Converter
Krynox Nexus - Zero-Trust Kernel Module Hardening

Converts Clang Static Analyzer text output to SARIF 2.1.0 format.
"""

import sys
import re
import argparse
from typing import List
from pathlib import Path

from base_converter import BaseSARIFConverter, Finding


class ClangConverter(BaseSARIFConverter):
    """
    Converter for Clang Static Analyzer text output to SARIF format.
    
    Clang produces text output in the format:
    file.c:line:column: warning: message
    file.c:line:column: error: message
    file.c:line:column: note: additional context
    """
    
    # Regex pattern for Clang output
    CLANG_PATTERN = re.compile(
        r'^(?P<file>[^:]+):(?P<line>\d+):(?P<column>\d+):\s+'
        r'(?P<severity>warning|error|note):\s+'
        r'(?P<message>.+)$'
    )
    
    def __init__(self, tool_version: str = "14.0.0", project_root: str = "."):
        """
        Initialize Clang converter.
        
        Args:
            tool_version: Clang version
            project_root: Root directory of the project
        """
        super().__init__("Clang Static Analyzer", tool_version, project_root)
    
    def parse_output(self, output_file: str) -> List[Finding]:
        """
        Parse Clang Static Analyzer text output.
        
        Args:
            output_file: Path to Clang text output file
            
        Returns:
            List of Finding objects
        """
        findings = []
        
        try:
            with open(output_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                # Try to match Clang output pattern
                match = self.CLANG_PATTERN.match(line)
                
                if match:
                    file_path = match.group('file')
                    line_number = int(match.group('line'))
                    column = int(match.group('column'))
                    severity = match.group('severity')
                    message = match.group('message')
                    
                    # Skip 'note' entries as they are usually context for warnings/errors
                    if severity == 'note':
                        i += 1
                        continue
                    
                    # Collect additional context lines
                    context_lines = []
                    j = i + 1
                    while j < len(lines) and j < i + 5:  # Look ahead up to 5 lines
                        next_line = lines[j].strip()
                        if self.CLANG_PATTERN.match(next_line):
                            break
                        if next_line and not next_line.startswith('^'):
                            context_lines.append(next_line)
                        j += 1
                    
                    # Append context to message if available
                    if context_lines:
                        message = message + '\n' + '\n'.join(context_lines[:2])
                    
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
                
                i += 1
        
        except Exception as e:
            print(f"Error processing Clang output: {e}", file=sys.stderr)
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
        # Try to extract checker name from message
        # Clang often includes checker names in brackets
        checker_match = re.search(r'\[([^\]]+)\]', message)
        if checker_match:
            checker = checker_match.group(1)
            return f"clang-{checker.replace('.', '-').lower()}"
        
        # Create rule ID from message keywords
        message_lower = message.lower()
        
        if 'buffer overflow' in message_lower or 'buffer overrun' in message_lower:
            return 'clang-buffer-overflow'
        elif 'use after free' in message_lower or 'use-after-free' in message_lower:
            return 'clang-use-after-free'
        elif 'null pointer' in message_lower or 'null dereference' in message_lower:
            return 'clang-null-pointer'
        elif 'memory leak' in message_lower or 'leak' in message_lower:
            return 'clang-memory-leak'
        elif 'uninitialized' in message_lower:
            return 'clang-uninitialized'
        elif 'division by zero' in message_lower:
            return 'clang-division-by-zero'
        elif 'dead' in message_lower and 'code' in message_lower:
            return 'clang-dead-code'
        elif 'unused' in message_lower:
            return 'clang-unused-value'
        else:
            # Generic rule ID
            return 'clang-warning'
    
    def _get_category(self, message: str) -> str:
        """
        Determine category from message content.
        
        Args:
            message: Warning message
            
        Returns:
            Category string
        """
        message_lower = message.lower()
        
        if any(keyword in message_lower for keyword in ['buffer', 'overflow', 'overrun', 'bounds']):
            return 'memory_safety'
        elif any(keyword in message_lower for keyword in ['use after free', 'double free', 'freed']):
            return 'memory_safety'
        elif any(keyword in message_lower for keyword in ['null pointer', 'null dereference']):
            return 'memory_safety'
        elif any(keyword in message_lower for keyword in ['leak', 'unreleased']):
            return 'memory_safety'
        elif any(keyword in message_lower for keyword in ['uninitialized', 'undefined']):
            return 'initialization'
        elif any(keyword in message_lower for keyword in ['race', 'thread', 'atomic']):
            return 'concurrency'
        elif any(keyword in message_lower for keyword in ['overflow', 'underflow', 'division']):
            return 'numeric'
        elif any(keyword in message_lower for keyword in ['cast', 'type']):
            return 'type_safety'
        else:
            return 'general'


def main():
    """Main entry point for command-line usage."""
    parser = argparse.ArgumentParser(
        description='Convert Clang Static Analyzer output to SARIF 2.1.0 format'
    )
    parser.add_argument(
        '--input',
        required=True,
        help='Path to Clang text output file'
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
    converter = ClangConverter(project_root=args.project_root)
    
    if args.verbose:
        print(f"Converting Clang output: {args.input}")
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


# Made with ❤️ by Bob - Security Architect & Kernel Engineer

# Made with Bob
