"""
CWE (Common Weakness Enumeration) Mappings
Krynox Nexus - Zero-Trust Kernel Module Hardening

This module provides mappings between vulnerability types and CWE IDs
for consistent vulnerability classification across all security tools.
"""

from typing import Optional, Dict, Any

# CWE Database for Kernel Module Vulnerabilities
CWE_DATABASE: Dict[str, Dict[str, Any]] = {
    # Memory Safety Issues
    "CWE-120": {
        "name": "Buffer Copy without Checking Size of Input ('Classic Buffer Overflow')",
        "category": "memory_safety",
        "severity": "critical",
        "keywords": ["buffer overflow", "strcpy", "sprintf", "gets"]
    },
    "CWE-121": {
        "name": "Stack-based Buffer Overflow",
        "category": "memory_safety",
        "severity": "critical",
        "keywords": ["stack overflow", "stack buffer"]
    },
    "CWE-122": {
        "name": "Heap-based Buffer Overflow",
        "category": "memory_safety",
        "severity": "critical",
        "keywords": ["heap overflow", "heap buffer"]
    },
    "CWE-119": {
        "name": "Improper Restriction of Operations within the Bounds of a Memory Buffer",
        "category": "memory_safety",
        "severity": "critical",
        "keywords": ["memory bounds", "buffer access"]
    },
    "CWE-125": {
        "name": "Out-of-bounds Read",
        "category": "memory_safety",
        "severity": "high",
        "keywords": ["out of bounds read", "buffer over-read"]
    },
    "CWE-787": {
        "name": "Out-of-bounds Write",
        "category": "memory_safety",
        "severity": "critical",
        "keywords": ["out of bounds write", "buffer over-write"]
    },
    
    # Use-After-Free and Memory Management
    "CWE-416": {
        "name": "Use After Free",
        "category": "memory_safety",
        "severity": "critical",
        "keywords": ["use after free", "freed pointer", "dangling pointer"]
    },
    "CWE-415": {
        "name": "Double Free",
        "category": "memory_safety",
        "severity": "critical",
        "keywords": ["double free", "free twice"]
    },
    "CWE-401": {
        "name": "Missing Release of Memory after Effective Lifetime",
        "category": "memory_safety",
        "severity": "medium",
        "keywords": ["memory leak", "unreleased memory"]
    },
    "CWE-476": {
        "name": "NULL Pointer Dereference",
        "category": "memory_safety",
        "severity": "high",
        "keywords": ["null pointer", "null dereference"]
    },
    
    # Integer Issues
    "CWE-190": {
        "name": "Integer Overflow or Wraparound",
        "category": "numeric",
        "severity": "high",
        "keywords": ["integer overflow", "wraparound"]
    },
    "CWE-191": {
        "name": "Integer Underflow",
        "category": "numeric",
        "severity": "high",
        "keywords": ["integer underflow"]
    },
    "CWE-682": {
        "name": "Incorrect Calculation",
        "category": "numeric",
        "severity": "medium",
        "keywords": ["incorrect calculation", "arithmetic error"]
    },
    
    # Race Conditions and Concurrency
    "CWE-362": {
        "name": "Concurrent Execution using Shared Resource with Improper Synchronization ('Race Condition')",
        "category": "concurrency",
        "severity": "high",
        "keywords": ["race condition", "toctou", "time of check"]
    },
    "CWE-366": {
        "name": "Race Condition within a Thread",
        "category": "concurrency",
        "severity": "high",
        "keywords": ["thread race", "data race"]
    },
    "CWE-667": {
        "name": "Improper Locking",
        "category": "concurrency",
        "severity": "high",
        "keywords": ["improper locking", "lock", "mutex", "spinlock"]
    },
    "CWE-833": {
        "name": "Deadlock",
        "category": "concurrency",
        "severity": "medium",
        "keywords": ["deadlock", "lock ordering"]
    },
    
    # Privilege and Access Control
    "CWE-269": {
        "name": "Improper Privilege Management",
        "category": "privilege",
        "severity": "critical",
        "keywords": ["privilege escalation", "capability", "permission"]
    },
    "CWE-250": {
        "name": "Execution with Unnecessary Privileges",
        "category": "privilege",
        "severity": "high",
        "keywords": ["unnecessary privileges", "least privilege"]
    },
    "CWE-732": {
        "name": "Incorrect Permission Assignment for Critical Resource",
        "category": "privilege",
        "severity": "high",
        "keywords": ["incorrect permission", "access control"]
    },
    
    # Information Disclosure
    "CWE-200": {
        "name": "Exposure of Sensitive Information to an Unauthorized Actor",
        "category": "information_disclosure",
        "severity": "medium",
        "keywords": ["information disclosure", "kernel memory leak", "sensitive data"]
    },
    "CWE-209": {
        "name": "Generation of Error Message Containing Sensitive Information",
        "category": "information_disclosure",
        "severity": "low",
        "keywords": ["error message", "sensitive information"]
    },
    "CWE-532": {
        "name": "Insertion of Sensitive Information into Log File",
        "category": "information_disclosure",
        "severity": "low",
        "keywords": ["log file", "sensitive log"]
    },
    
    # Input Validation
    "CWE-20": {
        "name": "Improper Input Validation",
        "category": "input_validation",
        "severity": "high",
        "keywords": ["input validation", "sanitization"]
    },
    "CWE-129": {
        "name": "Improper Validation of Array Index",
        "category": "input_validation",
        "severity": "high",
        "keywords": ["array index", "bounds check"]
    },
    "CWE-134": {
        "name": "Use of Externally-Controlled Format String",
        "category": "input_validation",
        "severity": "critical",
        "keywords": ["format string", "printf"]
    },
    
    # Type and Cast Issues
    "CWE-704": {
        "name": "Incorrect Type Conversion or Cast",
        "category": "type_safety",
        "severity": "medium",
        "keywords": ["type conversion", "cast", "type mismatch"]
    },
    "CWE-843": {
        "name": "Access of Resource Using Incompatible Type ('Type Confusion')",
        "category": "type_safety",
        "severity": "high",
        "keywords": ["type confusion", "incompatible type"]
    },
    
    # Initialization and Cleanup
    "CWE-665": {
        "name": "Improper Initialization",
        "category": "initialization",
        "severity": "medium",
        "keywords": ["uninitialized", "initialization"]
    },
    "CWE-908": {
        "name": "Use of Uninitialized Resource",
        "category": "initialization",
        "severity": "high",
        "keywords": ["uninitialized variable", "uninitialized memory"]
    },
    "CWE-459": {
        "name": "Incomplete Cleanup",
        "category": "initialization",
        "severity": "medium",
        "keywords": ["incomplete cleanup", "resource leak"]
    },
    
    # Kernel-Specific
    "CWE-783": {
        "name": "Operator Precedence Logic Error",
        "category": "logic",
        "severity": "medium",
        "keywords": ["operator precedence", "logic error"]
    },
    "CWE-788": {
        "name": "Access of Memory Location After End of Buffer",
        "category": "memory_safety",
        "severity": "critical",
        "keywords": ["buffer overrun", "past end of buffer"]
    },
}

# Keyword to CWE mapping for fuzzy matching
KEYWORD_TO_CWE: Dict[str, str] = {}
for cwe_id, cwe_data in CWE_DATABASE.items():
    for keyword in cwe_data["keywords"]:
        KEYWORD_TO_CWE[keyword.lower()] = cwe_id


def get_cwe_id(vulnerability_description: str) -> Optional[str]:
    """
    Get CWE ID from vulnerability description using keyword matching.
    
    Args:
        vulnerability_description: Description of the vulnerability
        
    Returns:
        CWE ID (e.g., "CWE-120") or None if no match found
    """
    description_lower = vulnerability_description.lower()
    
    # Try exact keyword match first
    for keyword, cwe_id in KEYWORD_TO_CWE.items():
        if keyword in description_lower:
            return cwe_id
    
    # Try partial matches for common patterns
    if "overflow" in description_lower and "buffer" in description_lower:
        return "CWE-120"
    if "use" in description_lower and "free" in description_lower:
        return "CWE-416"
    if "null" in description_lower and ("pointer" in description_lower or "dereference" in description_lower):
        return "CWE-476"
    if "race" in description_lower:
        return "CWE-362"
    if "leak" in description_lower and "memory" in description_lower:
        return "CWE-401"
    
    return None


def get_cwe_name(cwe_id: str) -> Optional[str]:
    """
    Get CWE name from CWE ID.
    
    Args:
        cwe_id: CWE ID (e.g., "CWE-120")
        
    Returns:
        CWE name or None if not found
    """
    cwe_data = CWE_DATABASE.get(cwe_id)
    return cwe_data["name"] if cwe_data else None


def get_cwe_severity(cwe_id: str) -> str:
    """
    Get default severity for a CWE ID.
    
    Args:
        cwe_id: CWE ID (e.g., "CWE-120")
        
    Returns:
        Severity level: "critical", "high", "medium", or "low"
    """
    cwe_data = CWE_DATABASE.get(cwe_id)
    return cwe_data["severity"] if cwe_data else "medium"


def get_cwe_category(cwe_id: str) -> Optional[str]:
    """
    Get category for a CWE ID.
    
    Args:
        cwe_id: CWE ID (e.g., "CWE-120")
        
    Returns:
        Category name or None if not found
    """
    cwe_data = CWE_DATABASE.get(cwe_id)
    return cwe_data["category"] if cwe_data else None



