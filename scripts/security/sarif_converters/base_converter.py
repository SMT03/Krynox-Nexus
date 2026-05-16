"""
Base SARIF Converter
Krynox Nexus - Zero-Trust Kernel Module Hardening

This module provides the base class for all SARIF converters,
implementing common functionality for parsing tool outputs and
generating SARIF 2.1.0 format reports.
"""

import json
import os
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from pathlib import Path

from .cwe_mappings import get_cwe_id, get_cwe_name, get_cwe_severity


@dataclass
class Finding:
    """
    Represents a security finding from a tool.
    """
    rule_id: str
    message: str
    file_path: str
    line_number: int
    column_number: int = 1
    severity: str = "warning"  # error, warning, note
    cwe_ids: List[int] = field(default_factory=list)
    code_snippet: Optional[str] = None
    end_line: Optional[int] = None
    end_column: Optional[int] = None
    category: Optional[str] = None
    confidence: str = "medium"  # high, medium, low
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert finding to dictionary."""
        return {
            'rule_id': self.rule_id,
            'message': self.message,
            'file_path': self.file_path,
            'line_number': self.line_number,
            'column_number': self.column_number,
            'severity': self.severity,
            'cwe_ids': self.cwe_ids,
            'code_snippet': self.code_snippet,
            'end_line': self.end_line,
            'end_column': self.end_column,
            'category': self.category,
            'confidence': self.confidence,
        }


class BaseSARIFConverter(ABC):
    """
    Base class for SARIF converters.
    
    Provides common functionality for:
    - Parsing tool outputs
    - Converting findings to SARIF format
    - Validating SARIF output
    - Writing SARIF files
    """
    
    def __init__(self, tool_name: str, tool_version: str, project_root: str = "."):
        """
        Initialize the converter.
        
        Args:
            tool_name: Name of the security tool
            tool_version: Version of the tool
            project_root: Root directory of the project
        """
        self.tool_name = tool_name
        self.tool_version = tool_version
        self.project_root = Path(project_root).resolve()
        self.findings: List[Finding] = []
    
    @abstractmethod
    def parse_output(self, output_file: str) -> List[Finding]:
        """
        Parse tool-specific output format.
        
        Args:
            output_file: Path to tool output file
            
        Returns:
            List of Finding objects
        """
        pass
    
    def normalize_severity(self, tool_severity: str) -> str:
        """
        Normalize tool-specific severity to SARIF levels.
        
        SARIF levels: error, warning, note, none
        
        Args:
            tool_severity: Tool-specific severity string
            
        Returns:
            SARIF severity level
        """
        severity_map = {
            'critical': 'error',
            'high': 'error',
            'error': 'error',
            'medium': 'warning',
            'warning': 'warning',
            'low': 'note',
            'note': 'note',
            'info': 'note',
            'information': 'note',
            'style': 'note',
        }
        return severity_map.get(tool_severity.lower(), 'warning')
    
    def extract_cwe_ids(self, message: str, existing_cwe: Optional[str] = None) -> List[int]:
        """
        Extract CWE IDs from message or use existing CWE.
        
        Args:
            message: Finding message
            existing_cwe: Existing CWE ID if available
            
        Returns:
            List of CWE IDs (as integers)
        """
        cwe_ids = []
        
        # If CWE is explicitly provided
        if existing_cwe:
            cwe_match = re.search(r'CWE-(\d+)', existing_cwe)
            if cwe_match:
                cwe_ids.append(int(cwe_match.group(1)))
        
        # Try to find CWE in message
        cwe_matches = re.findall(r'CWE-(\d+)', message)
        for match in cwe_matches:
            cwe_id = int(match)
            if cwe_id not in cwe_ids:
                cwe_ids.append(cwe_id)
        
        # If no CWE found, try keyword matching
        if not cwe_ids:
            cwe_str = get_cwe_id(message)
            if cwe_str:
                cwe_match = re.search(r'CWE-(\d+)', cwe_str)
                if cwe_match:
                    cwe_ids.append(int(cwe_match.group(1)))
        
        return cwe_ids
    
    def get_relative_path(self, file_path: str) -> str:
        """
        Convert absolute path to relative path from project root.
        
        Args:
            file_path: Absolute or relative file path
            
        Returns:
            Relative path from project root
        """
        try:
            path = Path(file_path).resolve()
            return str(path.relative_to(self.project_root))
        except ValueError:
            # If path is not relative to project_root, return as-is
            return file_path
    
    def extract_code_snippet(self, file_path: str, line_number: int, context_lines: int = 0) -> Optional[str]:
        """
        Extract code snippet from source file.
        
        Args:
            file_path: Path to source file
            line_number: Line number (1-based)
            context_lines: Number of context lines before/after
            
        Returns:
            Code snippet or None if file not found
        """
        try:
            full_path = self.project_root / file_path
            if not full_path.exists():
                return None
            
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            if line_number < 1 or line_number > len(lines):
                return None
            
            start = max(0, line_number - 1 - context_lines)
            end = min(len(lines), line_number + context_lines)
            
            snippet_lines = lines[start:end]
            return ''.join(snippet_lines).rstrip()
        
        except Exception:
            return None
    
    def convert_to_sarif(self, findings: List[Finding]) -> Dict[str, Any]:
        """
        Convert findings to SARIF 2.1.0 format.
        
        Args:
            findings: List of Finding objects
            
        Returns:
            SARIF JSON structure as dictionary
        """
        # Build rules from findings
        rules = self._build_rules(findings)
        
        # Build results
        results = []
        for finding in findings:
            result = {
                "ruleId": finding.rule_id,
                "level": finding.severity,
                "message": {
                    "text": finding.message
                },
                "locations": [{
                    "physicalLocation": {
                        "artifactLocation": {
                            "uri": finding.file_path,
                            "uriBaseId": "SRCROOT"
                        },
                        "region": {
                            "startLine": finding.line_number,
                            "startColumn": finding.column_number,
                        }
                    }
                }]
            }
            
            # Add end position if available
            if finding.end_line:
                result["locations"][0]["physicalLocation"]["region"]["endLine"] = finding.end_line
            if finding.end_column:
                result["locations"][0]["physicalLocation"]["region"]["endColumn"] = finding.end_column
            
            # Add code snippet if available
            if finding.code_snippet:
                result["locations"][0]["physicalLocation"]["region"]["snippet"] = {
                    "text": finding.code_snippet
                }
            
            # Add CWE IDs if available
            if finding.cwe_ids:
                result["cweIds"] = finding.cwe_ids
            
            # Add properties
            result["properties"] = {
                "confidence": finding.confidence
            }
            if finding.category:
                result["properties"]["category"] = finding.category
            
            results.append(result)
        
        # Build SARIF structure
        sarif = {
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "version": "2.1.0",
            "runs": [{
                "tool": {
                    "driver": {
                        "name": self.tool_name,
                        "version": self.tool_version,
                        "informationUri": self._get_tool_uri(),
                        "rules": rules
                    }
                },
                "results": results,
                "columnKind": "utf16CodeUnits"
            }]
        }
        
        return sarif
    
    def _build_rules(self, findings: List[Finding]) -> List[Dict[str, Any]]:
        """
        Build SARIF rules from findings.
        
        Args:
            findings: List of Finding objects
            
        Returns:
            List of SARIF rule objects
        """
        rules_dict = {}
        
        for finding in findings:
            if finding.rule_id not in rules_dict:
                rule = {
                    "id": finding.rule_id,
                    "name": finding.rule_id.replace('-', '_').title(),
                    "shortDescription": {
                        "text": finding.message.split('\n')[0][:100]
                    },
                    "defaultConfiguration": {
                        "level": finding.severity
                    },
                    "properties": {
                        "tags": ["security"]
                    }
                }
                
                # Add CWE relationships if available
                if finding.cwe_ids:
                    rule["relationships"] = []
                    for cwe_id in finding.cwe_ids:
                        cwe_str = f"CWE-{cwe_id}"
                        cwe_name = get_cwe_name(cwe_str)
                        rule["relationships"].append({
                            "target": {
                                "id": cwe_str,
                                "toolComponent": {
                                    "name": "CWE"
                                }
                            },
                            "kinds": ["superset"]
                        })
                        if cwe_name:
                            rule["fullDescription"] = {
                                "text": cwe_name
                            }
                
                rules_dict[finding.rule_id] = rule
        
        return list(rules_dict.values())
    
    def _get_tool_uri(self) -> str:
        """
        Get information URI for the tool.
        
        Returns:
            Tool information URI
        """
        tool_uris = {
            "Clang Static Analyzer": "https://clang-analyzer.llvm.org/",
            "Cppcheck": "https://cppcheck.sourceforge.io/",
            "Sparse": "https://sparse.docs.kernel.org/",
            "IBM Bob CLI": "https://www.ibm.com/bob",
            "Kernel Hardening": "https://kernsec.org/wiki/index.php/Kernel_Self_Protection_Project",
        }
        return tool_uris.get(self.tool_name, "https://github.com/krynox-nexus")
    
    def validate_sarif(self, sarif_data: Dict[str, Any]) -> bool:
        """
        Validate SARIF data against schema.
        
        Args:
            sarif_data: SARIF JSON structure
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Basic validation checks
            if "$schema" not in sarif_data:
                return False
            if "version" not in sarif_data or sarif_data["version"] != "2.1.0":
                return False
            if "runs" not in sarif_data or not isinstance(sarif_data["runs"], list):
                return False
            
            # Validate each run
            for run in sarif_data["runs"]:
                if "tool" not in run or "driver" not in run["tool"]:
                    return False
                if "results" not in run or not isinstance(run["results"], list):
                    return False
            
            return True
        except Exception:
            return False
    
    def write_sarif(self, sarif_data: Dict[str, Any], output_file: str) -> bool:
        """
        Write SARIF data to file.
        
        Args:
            sarif_data: SARIF JSON structure
            output_file: Output file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(sarif_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error writing SARIF file: {e}")
            return False
    
    def convert(self, input_file: str, output_file: str, validate: bool = True) -> bool:
        """
        Main conversion method: parse input, convert to SARIF, write output.
        
        Args:
            input_file: Path to tool output file
            output_file: Path to SARIF output file
            validate: Whether to validate SARIF before writing
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Parse tool output
            self.findings = self.parse_output(input_file)
            
            # Convert to SARIF
            sarif_data = self.convert_to_sarif(self.findings)
            
            # Validate if requested
            if validate and not self.validate_sarif(sarif_data):
                print("Error: Generated SARIF is invalid")
                return False
            
            # Write SARIF file
            return self.write_sarif(sarif_data, output_file)
        
        except Exception as e:
            print(f"Error during conversion: {e}")
            return False


# Made with ❤️ by Bob - Security Architect & Kernel Engineer

# Made with Bob
