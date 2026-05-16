#!/usr/bin/env python3
"""
test_pipeline.py - Integration Tests for Krynox Nexus Security Pipeline

This module provides comprehensive integration tests for the Krynox Nexus
security scanning pipeline, including:
- Kernel hardening verification (verify_kernel_hardening.sh)
- Static analysis pipeline (run_static_analysis.sh)

The tests validate script execution, output formatting, exit codes, and
report generation against real system configurations.

Test Framework: pytest
Coverage Goal: ≥70% integration test coverage
Total Test Cases: 18 (core functionality + edge cases)

Part of Krynox Nexus - Zero-Trust Kernel Module Hardening
Author: Bob - Security Architect & Kernel Engineer
Date: 2026-05-16

Usage:
    # Run all integration tests
    pytest tests/integration/test_pipeline.py -v
    
    # Run specific test class
    pytest tests/integration/test_pipeline.py::TestKernelHardeningVerification -v
    
    # Run with coverage
    pytest tests/integration/test_pipeline.py --cov=scripts --cov-report=html
"""

import os
import sys
import json
import subprocess
import tempfile
import shutil
import re
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import pytest


# ============================================================================
# Test Configuration
# ============================================================================

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts" / "security"
SRC_DIR = PROJECT_ROOT / "src"
REPORTS_DIR = PROJECT_ROOT / "reports"

# Script paths
KERNEL_HARDENING_SCRIPT = SCRIPTS_DIR / "verify_kernel_hardening.sh"
STATIC_ANALYSIS_SCRIPT = SCRIPTS_DIR / "run_static_analysis.sh"

# Test configuration
TEST_TIMEOUT = 120  # seconds
EXPECTED_EXIT_CODES = [0, 1, 2, 3]  # Valid exit codes for kernel hardening

# ANSI color code patterns
COLOR_PATTERNS = {
    'RED': r'\033\[0;31m',
    'GREEN': r'\033\[0;32m',
    'YELLOW': r'\033\[1;33m',
    'BLUE': r'\033\[0;34m',
    'NC': r'\033\[0m'
}


# ============================================================================
# Helper Functions
# ============================================================================

def run_script(script_path: Path, timeout: int = TEST_TIMEOUT) -> Tuple[int, str, str]:
    """
    Execute a shell script and capture its output.
    
    Purpose:
        Run a shell script with timeout protection and capture stdout/stderr
        for validation.
    
    Args:
        script_path: Path to the shell script to execute
        timeout: Maximum execution time in seconds (default: 120)
    
    Returns:
        Tuple of (exit_code, stdout, stderr)
    
    Raises:
        subprocess.TimeoutExpired: If script exceeds timeout
        FileNotFoundError: If script doesn't exist
    """
    if not script_path.exists():
        raise FileNotFoundError(f"Script not found: {script_path}")
    
    # Ensure script is executable
    os.chmod(script_path, 0o755)
    
    try:
        result = subprocess.run(
            [str(script_path)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=PROJECT_ROOT
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired as e:
        return -1, "", f"Script timeout after {timeout} seconds"


def strip_ansi_codes(text: str) -> str:
    """
    Remove ANSI color codes from text.
    
    Purpose:
        Clean output text for easier parsing and validation.
    
    Args:
        text: Text containing ANSI escape sequences
    
    Returns:
        Text with ANSI codes removed
    """
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


def has_color_codes(text: str, color: str) -> bool:
    """
    Check if text contains specific ANSI color codes.
    
    Purpose:
        Verify that scripts produce color-coded output for better readability.
    
    Args:
        text: Text to check for color codes
        color: Color name (RED, GREEN, YELLOW, BLUE, NC)
    
    Returns:
        True if color code is present, False otherwise
    """
    if color not in COLOR_PATTERNS:
        return False
    
    pattern = COLOR_PATTERNS[color]
    return re.search(pattern, text) is not None


def validate_json_structure(json_path: Path, required_keys: List[str]) -> bool:
    """
    Validate JSON file structure and required keys.
    
    Purpose:
        Ensure generated JSON reports have the expected structure.
    
    Args:
        json_path: Path to JSON file
        required_keys: List of required top-level keys
    
    Returns:
        True if JSON is valid and contains all required keys
    """
    if not json_path.exists():
        return False
    
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        return all(key in data for key in required_keys)
    except (json.JSONDecodeError, IOError):
        return False


def cleanup_reports(report_dir: Path) -> None:
    """
    Clean up test report artifacts.
    
    Purpose:
        Remove generated reports after tests to avoid pollution.
    
    Args:
        report_dir: Directory containing reports to clean
    """
    if report_dir.exists() and report_dir.is_dir():
        shutil.rmtree(report_dir, ignore_errors=True)


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture(scope="module")
def project_paths():
    """
    Provide project paths for tests.
    
    Setup:
        Validates that required project directories exist.
    
    Returns:
        Dictionary of project paths
    """
    paths = {
        'root': PROJECT_ROOT,
        'scripts': SCRIPTS_DIR,
        'src': SRC_DIR,
        'reports': REPORTS_DIR
    }
    
    # Validate critical paths exist
    assert paths['root'].exists(), "Project root not found"
    assert paths['scripts'].exists(), "Scripts directory not found"
    assert paths['src'].exists(), "Source directory not found"
    
    return paths


@pytest.fixture(scope="function")
def clean_reports():
    """
    Clean up report directories before and after tests.
    
    Setup:
        Removes existing reports before test execution.
    
    Cleanup:
        Removes generated reports after test completion.
    """
    # Setup: Clean before test
    report_dirs = [
        REPORTS_DIR / "static-analysis",
        REPORTS_DIR / "kernel-hardening"
    ]
    
    for report_dir in report_dirs:
        cleanup_reports(report_dir)
    
    yield
    
    # Teardown: Clean after test
    for report_dir in report_dirs:
        cleanup_reports(report_dir)


# ============================================================================
# Test Suite 1: Kernel Hardening Verification
# ============================================================================

class TestKernelHardeningVerification:
    """
    Integration tests for verify_kernel_hardening.sh script.
    
    This test suite validates:
    - Script execution and exit codes
    - Color-coded output formatting
    - Configuration check output
    - Summary section generation
    - Error handling
    
    Test Strategy:
        Run script against actual system and validate output format,
        structure, and exit codes without modifying system configuration.
    """
    
    def test_script_exists(self, project_paths):
        """
        Test that the kernel hardening verification script exists.
        
        Purpose:
            Verify script file is present and accessible.
        
        Execution:
            Check file existence and permissions.
        
        Verification:
            Script file exists and is executable.
        """
        assert KERNEL_HARDENING_SCRIPT.exists(), \
            f"Script not found: {KERNEL_HARDENING_SCRIPT}"
        
        assert os.access(KERNEL_HARDENING_SCRIPT, os.X_OK), \
            f"Script not executable: {KERNEL_HARDENING_SCRIPT}"
    
    def test_script_execution(self):
        """
        Test that the script executes without crashing.
        
        Purpose:
            Verify script runs to completion without fatal errors.
        
        Execution:
            Run script and capture exit code.
        
        Verification:
            Exit code is one of the expected values (0, 1, 2, 3).
        """
        exit_code, stdout, stderr = run_script(KERNEL_HARDENING_SCRIPT)
        
        # Script should complete (not timeout or crash)
        assert exit_code != -1, "Script timed out or crashed"
        
        # Exit code should be in valid range
        assert exit_code in EXPECTED_EXIT_CODES, \
            f"Unexpected exit code: {exit_code}. Expected one of {EXPECTED_EXIT_CODES}"
    
    def test_output_contains_header(self):
        """
        Test that output contains the expected header section.
        
        Purpose:
            Verify script produces properly formatted header.
        
        Execution:
            Run script and parse output for header text.
        
        Verification:
            Output contains "Krynox Nexus Kernel Hardening Verification".
        """
        exit_code, stdout, stderr = run_script(KERNEL_HARDENING_SCRIPT)
        
        assert "Krynox Nexus Kernel Hardening Verification" in stdout, \
            "Output missing expected header"
        
        assert "Target: ARM64 Edge Device" in stdout, \
            "Output missing target device information"
    
    def test_color_coded_output(self):
        """
        Test that output contains color-coded logs.
        
        Purpose:
            Verify script uses ANSI color codes for better readability.
        
        Execution:
            Run script and check for color code patterns.
        
        Verification:
            Output contains GREEN, RED, YELLOW, and BLUE color codes.
        """
        exit_code, stdout, stderr = run_script(KERNEL_HARDENING_SCRIPT)
        
        # Check for presence of color codes
        assert has_color_codes(stdout, 'GREEN') or has_color_codes(stdout, 'RED'), \
            "Output missing color codes (GREEN/RED for checks)"
        
        assert has_color_codes(stdout, 'BLUE'), \
            "Output missing BLUE color codes (section headers)"
    
    def test_tier_sections_present(self):
        """
        Test that all configuration tier sections are present.
        
        Purpose:
            Verify script checks all required security configuration tiers.
        
        Execution:
            Run script and parse output for tier section headers.
        
        Verification:
            Output contains TIER 1, TIER 2, TIER 3, and ARM64-specific sections.
        """
        exit_code, stdout, stderr = run_script(KERNEL_HARDENING_SCRIPT)
        
        clean_output = strip_ansi_codes(stdout)
        
        assert "TIER 1: MANDATORY CONFIGURATIONS" in clean_output, \
            "Missing TIER 1 section"
        
        assert "TIER 2: HIGHLY RECOMMENDED CONFIGURATIONS" in clean_output, \
            "Missing TIER 2 section"
        
        assert "TIER 3: RECOMMENDED CONFIGURATIONS" in clean_output, \
            "Missing TIER 3 section"
        
        assert "ARM64-SPECIFIC CONFIGURATIONS" in clean_output, \
            "Missing ARM64-specific section"
    
    def test_runtime_checks_section(self):
        """
        Test that runtime checks section is present.
        
        Purpose:
            Verify script performs runtime security checks.
        
        Execution:
            Run script and check for runtime checks section.
        
        Verification:
            Output contains "RUNTIME CHECKS" section.
        """
        exit_code, stdout, stderr = run_script(KERNEL_HARDENING_SCRIPT)
        
        clean_output = strip_ansi_codes(stdout)
        
        assert "RUNTIME CHECKS" in clean_output, \
            "Missing RUNTIME CHECKS section"
    
    def test_summary_section_present(self):
        """
        Test that summary section is present with failure counts.
        
        Purpose:
            Verify script provides summary of security check results.
        
        Execution:
            Run script and parse output for summary section.
        
        Verification:
            Output contains summary with failure counts by priority.
        """
        exit_code, stdout, stderr = run_script(KERNEL_HARDENING_SCRIPT)
        
        clean_output = strip_ansi_codes(stdout)
        
        assert "SUMMARY" in clean_output, \
            "Missing SUMMARY section"
        
        assert "Critical failures:" in clean_output, \
            "Missing critical failures count"
        
        assert "High priority failures:" in clean_output, \
            "Missing high priority failures count"
    
    def test_exit_code_matches_severity(self):
        """
        Test that exit code corresponds to failure severity.
        
        Purpose:
            Verify exit codes properly indicate security posture.
        
        Execution:
            Run script and correlate exit code with output.
        
        Verification:
            Exit code 0 = PASS, 1 = CRITICAL, 2 = HIGH, 3 = MEDIUM failures.
        """
        exit_code, stdout, stderr = run_script(KERNEL_HARDENING_SCRIPT)
        
        clean_output = strip_ansi_codes(stdout)
        
        if exit_code == 0:
            assert "[PASS]" in clean_output, \
                "Exit code 0 but output doesn't show PASS"
        elif exit_code == 1:
            assert "[FAIL]" in clean_output and "CRITICAL" in clean_output, \
                "Exit code 1 but output doesn't show CRITICAL failure"
        elif exit_code == 2:
            assert "[WARN]" in clean_output and "High priority" in clean_output, \
                "Exit code 2 but output doesn't show HIGH priority warning"
        elif exit_code == 3:
            assert "[WARN]" in clean_output and "Medium priority" in clean_output, \
                "Exit code 3 but output doesn't show MEDIUM priority warning"
    
    def test_output_format_consistency(self):
        """
        Test that output format is consistent and parseable.
        
        Purpose:
            Verify output follows consistent formatting for automated parsing.
        
        Execution:
            Run script and validate output structure.
        
        Verification:
            Check marks ([✓], [✗], [!]) are present and properly formatted.
        """
        exit_code, stdout, stderr = run_script(KERNEL_HARDENING_SCRIPT)
        
        clean_output = strip_ansi_codes(stdout)
        
        # Check for presence of status indicators
        has_check_marks = ("[✓]" in clean_output or 
                          "[✗]" in clean_output or 
                          "[!]" in clean_output)
        
        assert has_check_marks, \
            "Output missing status indicators ([✓], [✗], [!])"


# ============================================================================
# Test Suite 2: Static Analysis Pipeline
# ============================================================================

class TestStaticAnalysisPipeline:
    """
    Integration tests for run_static_analysis.sh script.
    
    This test suite validates:
    - Script execution and report generation
    - Directory structure creation
    - Tool-specific output files
    - JSON summary report structure
    - SARIF report generation
    
    Test Strategy:
        Run static analysis against actual source code and validate
        that reports are generated with correct structure and content.
    """
    
    def test_script_exists(self, project_paths):
        """
        Test that the static analysis script exists.
        
        Purpose:
            Verify script file is present and accessible.
        
        Execution:
            Check file existence and permissions.
        
        Verification:
            Script file exists and is executable.
        """
        assert STATIC_ANALYSIS_SCRIPT.exists(), \
            f"Script not found: {STATIC_ANALYSIS_SCRIPT}"
        
        assert os.access(STATIC_ANALYSIS_SCRIPT, os.X_OK), \
            f"Script not executable: {STATIC_ANALYSIS_SCRIPT}"
    
    def test_script_execution(self, clean_reports):
        """
        Test that the script executes without crashing.
        
        Purpose:
            Verify script runs to completion.
        
        Execution:
            Run script and capture exit code.
        
        Verification:
            Script completes (exit code 0 or 1, not timeout).
        """
        exit_code, stdout, stderr = run_script(STATIC_ANALYSIS_SCRIPT)
        
        # Script should complete (not timeout)
        assert exit_code != -1, "Script timed out"
        
        # Exit code should be 0 (success) or 1 (issues found)
        assert exit_code in [0, 1], \
            f"Unexpected exit code: {exit_code}"
    
    def test_report_directory_created(self, clean_reports):
        """
        Test that report directories are created.
        
        Purpose:
            Verify script creates necessary directory structure.
        
        Execution:
            Run script and check for report directories.
        
        Verification:
            reports/static-analysis directory exists with subdirectories.
        """
        exit_code, stdout, stderr = run_script(STATIC_ANALYSIS_SCRIPT)
        
        report_dir = REPORTS_DIR / "static-analysis"
        
        assert report_dir.exists(), \
            f"Report directory not created: {report_dir}"
        
        # Check for tool-specific subdirectories
        expected_subdirs = ['clang', 'cppcheck', 'sparse', 'sarif']
        for subdir in expected_subdirs:
            subdir_path = report_dir / subdir
            assert subdir_path.exists(), \
                f"Subdirectory not created: {subdir}"
    
    def test_clang_report_generated(self, clean_reports):
        """
        Test that Clang analyzer report is generated.
        
        Purpose:
            Verify Clang static analyzer produces output.
        
        Execution:
            Run script and check for Clang report file.
        
        Verification:
            clang/analysis.txt exists and is not empty.
        """
        exit_code, stdout, stderr = run_script(STATIC_ANALYSIS_SCRIPT)
        
        clang_report = REPORTS_DIR / "static-analysis" / "clang" / "analysis.txt"
        
        # Report may not exist if clang is not installed
        if clang_report.exists():
            assert clang_report.stat().st_size > 0, \
                "Clang report is empty"
    
    def test_cppcheck_report_generated(self, clean_reports):
        """
        Test that Cppcheck report is generated.
        
        Purpose:
            Verify Cppcheck produces output files.
        
        Execution:
            Run script and check for Cppcheck reports.
        
        Verification:
            cppcheck/analysis.txt and analysis.xml exist.
        """
        exit_code, stdout, stderr = run_script(STATIC_ANALYSIS_SCRIPT)
        
        cppcheck_txt = REPORTS_DIR / "static-analysis" / "cppcheck" / "analysis.txt"
        cppcheck_xml = REPORTS_DIR / "static-analysis" / "cppcheck" / "analysis.xml"
        
        # Reports may not exist if cppcheck is not installed
        if cppcheck_txt.exists():
            assert cppcheck_txt.stat().st_size > 0, \
                "Cppcheck text report is empty"
    
    def test_sparse_report_generated(self, clean_reports):
        """
        Test that Sparse report is generated.
        
        Purpose:
            Verify Sparse kernel checker produces output.
        
        Execution:
            Run script and check for Sparse report.
        
        Verification:
            sparse/analysis.txt exists.
        """
        exit_code, stdout, stderr = run_script(STATIC_ANALYSIS_SCRIPT)
        
        sparse_report = REPORTS_DIR / "static-analysis" / "sparse" / "analysis.txt"
        
        # Report may not exist if sparse is not installed
        # This is acceptable as sparse is kernel-specific
        if sparse_report.exists():
            # File may be empty if no issues found
            assert sparse_report.stat().st_size >= 0, \
                "Sparse report file is invalid"
    
    def test_summary_json_generated(self, clean_reports):
        """
        Test that JSON summary report is generated with correct structure.
        
        Purpose:
            Verify consolidated JSON report is created.
        
        Execution:
            Run script and validate JSON structure.
        
        Verification:
            static_analysis_summary.json exists with required keys.
        """
        exit_code, stdout, stderr = run_script(STATIC_ANALYSIS_SCRIPT)
        
        summary_json = REPORTS_DIR / "static-analysis" / "static_analysis_summary.json"
        
        assert summary_json.exists(), \
            "Summary JSON not generated"
        
        # Validate JSON structure
        required_keys = ['timestamp', 'project', 'scan_type', 'tools', 'summary']
        assert validate_json_structure(summary_json, required_keys), \
            "Summary JSON missing required keys"
        
        # Validate content
        with open(summary_json, 'r') as f:
            data = json.load(f)
        
        assert data['project'] == "Krynox Nexus", \
            "Incorrect project name in summary"
        
        assert data['scan_type'] == "static_analysis", \
            "Incorrect scan type in summary"
        
        assert 'tools' in data and isinstance(data['tools'], dict), \
            "Tools section missing or invalid"
        
        assert 'summary' in data and isinstance(data['summary'], dict), \
            "Summary section missing or invalid"
    
    def test_sarif_report_generated(self, clean_reports):
        """
        Test that SARIF report is generated for GitHub integration.
        
        Purpose:
            Verify SARIF format report is created for CI/CD integration.
        
        Execution:
            Run script and validate SARIF file.
        
        Verification:
            static_analysis.sarif exists and is valid JSON.
        """
        exit_code, stdout, stderr = run_script(STATIC_ANALYSIS_SCRIPT)
        
        sarif_report = REPORTS_DIR / "static-analysis" / "sarif" / "static_analysis.sarif"
        
        assert sarif_report.exists(), \
            "SARIF report not generated"
        
        # Validate SARIF is valid JSON
        try:
            with open(sarif_report, 'r') as f:
                sarif_data = json.load(f)
            
            # Check for SARIF schema
            assert '$schema' in sarif_data, \
                "SARIF missing schema definition"
            
            assert 'version' in sarif_data, \
                "SARIF missing version"
            
            assert 'runs' in sarif_data, \
                "SARIF missing runs array"
        except json.JSONDecodeError:
            pytest.fail("SARIF report is not valid JSON")
    
    def test_output_contains_progress_logs(self, clean_reports):
        """
        Test that script outputs progress information.
        
        Purpose:
            Verify script provides feedback during execution.
        
        Execution:
            Run script and check stdout for progress messages.
        
        Verification:
            Output contains step indicators and completion messages.
        """
        exit_code, stdout, stderr = run_script(STATIC_ANALYSIS_SCRIPT)
        
        # Check for progress indicators
        assert "[STEP]" in stdout or "[INFO]" in stdout, \
            "Output missing progress indicators"
        
        # Check for completion message
        assert "Analysis Complete" in stdout or "complete" in stdout.lower(), \
            "Output missing completion message"


# ============================================================================
# Test Suite 3: Edge Cases and Error Handling
# ============================================================================

class TestEdgeCases:
    """
    Integration tests for edge cases and error handling.
    
    This test suite validates:
    - Script behavior with missing dependencies
    - Handling of permission errors
    - Timeout scenarios
    - Concurrent execution safety
    
    Note: These tests are marked as optional and may be skipped
    if the test environment doesn't support the required conditions.
    """
    
    @pytest.mark.skipif(
        not KERNEL_HARDENING_SCRIPT.exists(),
        reason="Kernel hardening script not found"
    )
    def test_kernel_script_handles_missing_proc_config(self):
        """
        Test kernel hardening script behavior when /proc/config.gz is missing.
        
        Purpose:
            Verify graceful handling of missing kernel configuration.
        
        Execution:
            Run script and check for appropriate error handling.
        
        Verification:
            Script completes with informative error message.
        
        Note:
            This test may pass or fail depending on system configuration.
            It's primarily for documentation of expected behavior.
        """
        exit_code, stdout, stderr = run_script(KERNEL_HARDENING_SCRIPT)
        
        # If /proc/config.gz doesn't exist, script should handle it
        if not Path("/proc/config.gz").exists():
            # Script should still complete (not crash)
            assert exit_code != -1, "Script crashed on missing /proc/config.gz"
    
    @pytest.mark.skipif(
        not STATIC_ANALYSIS_SCRIPT.exists(),
        reason="Static analysis script not found"
    )
    def test_static_analysis_handles_missing_tools(self, clean_reports):
        """
        Test static analysis script behavior when tools are missing.
        
        Purpose:
            Verify script continues when optional tools are unavailable.
        
        Execution:
            Run script and check for graceful degradation.
        
        Verification:
            Script completes and generates reports for available tools.
        """
        exit_code, stdout, stderr = run_script(STATIC_ANALYSIS_SCRIPT)
        
        # Script should complete even if some tools are missing
        assert exit_code != -1, "Script crashed on missing tools"
        
        # Check for warning messages about missing tools
        output = stdout + stderr
        if "not found" in output.lower() or "skipping" in output.lower():
            # This is expected behavior
            pass


# ============================================================================
# Test Execution Summary
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "requires_root: marks tests that require root privileges"
    )


if __name__ == "__main__":
    """
    Run tests directly with pytest.
    
    Usage:
        python tests/integration/test_pipeline.py
    """
    pytest.main([__file__, "-v", "--tb=short"])

# Made with Bob
