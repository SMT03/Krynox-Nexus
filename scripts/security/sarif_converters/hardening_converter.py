#!/usr/bin/env python3
"""
Kernel Hardening to SARIF Converter
Krynox Nexus - Zero-Trust Kernel Module Hardening

Converts kernel hardening verification results to SARIF 2.1.0 format.
"""

import sys
import json
import re
import argparse
from typing import List, Dict, Any
from pathlib import Path

from base_converter import BaseSARIFConverter, Finding


class HardeningConverter(BaseSARIFConverter):
    """
    Converter for kernel hardening check results to SARIF format.
    
    Processes JSON output from verify_kernel_hardening.sh containing:
    - config: Kernel configuration option
    - status: pass/fail
    - expected: Expected value
    - actual: Actual value
    - priority: CRITICAL/HIGH/MEDIUM/LOW
    - cwe: Associated CWE ID
    """
    
    def __init__(self, tool_version: str = "1.0.0", project_root: str = "."):
        """
        Initialize Kernel Hardening converter.
        
        Args:
            tool_version: Tool version
            project_root: Root directory of the project
        """
        super().__init__("Kernel Hardening", tool_version, project_root)
    
    def parse_output(self, output_file: str) -> List[Finding]:
        """
        Parse kernel hardening JSON output.
        
        Args:
            output_file: Path to hardening JSON output file
            
        Returns:
            List of Finding objects
        """
        findings = []
        
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different JSON formats
            if isinstance(data, dict) and 'checks' in data:
                checks = data['checks']
            elif isinstance(data, list):
                checks = data
            else:
                print("Unexpected JSON format", file=sys.stderr)
                return []
            
            for check in checks:
                # Only create findings for failed checks
                if check.get('status') == 'fail':
                    finding = self._create_finding_from_check(check)
                    if finding:
                        findings.append(finding)
        
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}", file=sys.stderr)
            return []
        except Exception as e:
            print(f"Error processing hardening output: {e}", file=sys.stderr)
            return []
        
        return findings
    
    def _create_finding_from_check(self, check: Dict[str, Any]) -> Finding | None:
        """
        Create a Finding from a hardening check.
        
        Args:
            check: Check dictionary
            
        Returns:
            Finding object or None
        """
        config = check.get('config', 'UNKNOWN')
        expected = check.get('expected', 'y')
        actual = check.get('actual', 'not set')
        priority = check.get('priority', 'MEDIUM')
        cwe = check.get('cwe', None)
        description = check.get('description', '')
        
        # Create message
        message = f"Kernel hardening check failed: {config}\n"
        message += f"Expected: {expected}, Actual: {actual}\n"
        if description:
            message += f"Description: {description}\n"
        message += f"Priority: {priority}"
        
        # Add remediation guidance
        remediation = self._get_remediation(config, expected)
        if remediation:
            message += f"\n\nRemediation: {remediation}"
        
        # Create rule ID
        rule_id = f"hardening-{config.lower().replace('_', '-').replace('config-', '')}"
        
        # Map priority to severity
        severity = self._priority_to_severity(priority)
        
        # Extract CWE IDs
        cwe_ids = self.extract_cwe_ids(message, cwe)
        
        # Kernel config is not tied to a specific file, use a virtual path
        file_path = "kernel/.config"
        
        finding = Finding(
            rule_id=rule_id,
            message=message,
            file_path=file_path,
            line_number=1,
            column_number=1,
            severity=severity,
            cwe_ids=cwe_ids,
            category='kernel_hardening',
            confidence='high'
        )
        
        return finding
    
    def _priority_to_severity(self, priority: str) -> str:
        """
        Convert priority to SARIF severity.
        
        Args:
            priority: Priority level
            
        Returns:
            SARIF severity level
        """
        priority_map = {
            'CRITICAL': 'error',
            'HIGH': 'error',
            'MEDIUM': 'warning',
            'LOW': 'note',
        }
        return priority_map.get(priority.upper(), 'warning')
    
    def _get_remediation(self, config: str, expected: str) -> str:
        """
        Get remediation guidance for a failed check.
        
        Args:
            config: Kernel configuration option
            expected: Expected value
            
        Returns:
            Remediation guidance string
        """
        remediation_map = {
            'CONFIG_FORTIFY_SOURCE': 'Enable FORTIFY_SOURCE to add runtime buffer overflow protection. Add CONFIG_FORTIFY_SOURCE=y to kernel config.',
            'CONFIG_HARDENED_USERCOPY': 'Enable hardened usercopy to prevent heap overflows. Add CONFIG_HARDENED_USERCOPY=y to kernel config.',
            'CONFIG_SLAB_FREELIST_RANDOM': 'Enable SLAB freelist randomization to make heap exploits harder. Add CONFIG_SLAB_FREELIST_RANDOM=y to kernel config.',
            'CONFIG_SLAB_FREELIST_HARDENED': 'Enable hardened SLAB freelists to detect use-after-free. Add CONFIG_SLAB_FREELIST_HARDENED=y to kernel config.',
            'CONFIG_STACKPROTECTOR_STRONG': 'Enable strong stack protector to detect stack buffer overflows. Add CONFIG_STACKPROTECTOR_STRONG=y to kernel config.',
            'CONFIG_STRICT_KERNEL_RWX': 'Enable strict kernel RWX to prevent code injection. Add CONFIG_STRICT_KERNEL_RWX=y to kernel config.',
            'CONFIG_STRICT_MODULE_RWX': 'Enable strict module RWX to prevent module code injection. Add CONFIG_STRICT_MODULE_RWX=y to kernel config.',
            'CONFIG_RANDOMIZE_BASE': 'Enable KASLR to randomize kernel base address. Add CONFIG_RANDOMIZE_BASE=y to kernel config.',
            'CONFIG_MODULE_SIG': 'Enable module signature verification. Add CONFIG_MODULE_SIG=y to kernel config.',
            'CONFIG_MODULE_SIG_FORCE': 'Force module signature verification. Add CONFIG_MODULE_SIG_FORCE=y to kernel config.',
            'CONFIG_SECURITY_SELINUX': 'Enable SELinux for mandatory access control. Add CONFIG_SECURITY_SELINUX=y to kernel config.',
        }
        
        if config in remediation_map:
            return remediation_map[config]
        
        # Generic remediation
        return f'Enable {config} in kernel configuration. Add {config}={expected} to your kernel config file and rebuild the kernel.'


def main():
    """Main entry point for command-line usage."""
    parser = argparse.ArgumentParser(
        description='Convert kernel hardening check results to SARIF 2.1.0 format'
    )
    parser.add_argument(
        '--input',
        required=True,
        help='Path to hardening JSON output file'
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
    converter = HardeningConverter(project_root=args.project_root)
    
    if args.verbose:
        print(f"Converting hardening output: {args.input}")
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
