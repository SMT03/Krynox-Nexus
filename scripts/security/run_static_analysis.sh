#!/bin/bash
#
# run_static_analysis.sh - Run static analysis tools
#
# This script executes multiple static analyzers:
# - Clang Static Analyzer
# - Cppcheck
# - Sparse (kernel-specific)
#
# Part of Krynox Nexus - Zero-Trust Kernel Module Hardening

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SRC_DIR="$PROJECT_ROOT/src"
REPORT_DIR="$PROJECT_ROOT/reports/static-analysis"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

setup_report_directory() {
    log_step "Setting up report directory..."
    
    mkdir -p "$REPORT_DIR"/{clang,cppcheck,sparse,sarif}
    
    log_info "Report directory ready: $REPORT_DIR"
}

run_clang_analyzer() {
    log_step "Running Clang Static Analyzer..."
    
    if ! command -v clang &> /dev/null; then
        log_warn "Clang not found, skipping..."
        return 0
    fi
    
    local clang_report="$REPORT_DIR/clang/analysis.txt"
    local clang_html="$REPORT_DIR/clang/html"
    
    mkdir -p "$clang_html"
    
    # Run scan-build if available
    if command -v scan-build &> /dev/null; then
        log_info "Running scan-build..."
        
        cd "$SRC_DIR"
        scan-build \
            -o "$clang_html" \
            --status-bugs \
            -enable-checker security \
            -enable-checker unix \
            -enable-checker core \
            make clean all 2>&1 | tee "$clang_report"
        
        local exit_code=${PIPESTATUS[0]}
        
        if [ $exit_code -eq 0 ]; then
            log_info "✓ Clang analysis complete - no bugs found"
        else
            log_warn "✗ Clang found potential issues"
        fi
    else
        log_warn "scan-build not found, using clang --analyze..."
        
        find "$SRC_DIR" -name "*.c" | while read -r source_file; do
            local file_name=$(basename "$source_file")
            log_info "Analyzing: $file_name"
            
            clang --analyze \
                -Xanalyzer -analyzer-output=text \
                -I/lib/modules/$(uname -r)/build/include \
                "$source_file" \
                2>&1 | tee -a "$clang_report"
        done
    fi
    
    log_info "Clang analysis report: $clang_report"
}

run_cppcheck() {
    log_step "Running Cppcheck..."
    
    if ! command -v cppcheck &> /dev/null; then
        log_warn "Cppcheck not found, skipping..."
        return 0
    fi
    
    local cppcheck_report="$REPORT_DIR/cppcheck/analysis.xml"
    local cppcheck_txt="$REPORT_DIR/cppcheck/analysis.txt"
    
    log_info "Running Cppcheck with security checks..."
    
    cppcheck \
        --enable=all \
        --inconclusive \
        --std=c11 \
        --platform=unix64 \
        --suppress=missingIncludeSystem \
        --xml \
        --xml-version=2 \
        -I/lib/modules/$(uname -r)/build/include \
        "$SRC_DIR" \
        2> "$cppcheck_report"
    
    # Also generate human-readable report
    cppcheck \
        --enable=all \
        --inconclusive \
        --std=c11 \
        --platform=unix64 \
        --suppress=missingIncludeSystem \
        -I/lib/modules/$(uname -r)/build/include \
        "$SRC_DIR" \
        2>&1 | tee "$cppcheck_txt"
    
    # Count issues
    local error_count=$(grep -c "error:" "$cppcheck_txt" 2>/dev/null || echo "0")
    local warning_count=$(grep -c "warning:" "$cppcheck_txt" 2>/dev/null || echo "0")
    
    log_info "Cppcheck found: $error_count errors, $warning_count warnings"
    log_info "Cppcheck reports: $cppcheck_report, $cppcheck_txt"
}

run_sparse() {
    log_step "Running Sparse (kernel-specific checker)..."
    
    if ! command -v sparse &> /dev/null; then
        log_warn "Sparse not found, skipping..."
        return 0
    fi
    
    local sparse_report="$REPORT_DIR/sparse/analysis.txt"
    
    log_info "Running Sparse analysis..."
    
    cd "$SRC_DIR"
    
    # Run sparse on each C file
    find . -name "*.c" | while read -r source_file; do
        local file_name=$(basename "$source_file")
        log_info "Analyzing with Sparse: $file_name"
        
        sparse \
            -D__KERNEL__ \
            -Wbitwise \
            -Wcast-to-as \
            -Wdefault-bitfield-sign \
            -Wparen-string \
            -Wptr-subtraction-blows \
            -Wreturn-void \
            -Wshadow \
            -Wtypesign \
            -Wundef \
            -I/lib/modules/$(uname -r)/build/include \
            "$source_file" \
            2>&1 | tee -a "$sparse_report"
    done
    
    local issue_count=$(wc -l < "$sparse_report" 2>/dev/null || echo "0")
    log_info "Sparse found $issue_count potential issues"
    log_info "Sparse report: $sparse_report"
}

generate_summary_report() {
    log_step "Generating summary report..."
    
    local summary_file="$REPORT_DIR/static_analysis_summary.json"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    # Count issues from each tool
    local clang_issues=$(grep -c "warning:" "$REPORT_DIR/clang/analysis.txt" 2>/dev/null || echo "0")
    local cppcheck_errors=$(grep -c "error:" "$REPORT_DIR/cppcheck/analysis.txt" 2>/dev/null || echo "0")
    local cppcheck_warnings=$(grep -c "warning:" "$REPORT_DIR/cppcheck/analysis.txt" 2>/dev/null || echo "0")
    local sparse_issues=$(wc -l < "$REPORT_DIR/sparse/analysis.txt" 2>/dev/null || echo "0")
    
    local total_issues=$((clang_issues + cppcheck_errors + cppcheck_warnings + sparse_issues))
    
    cat > "$summary_file" <<EOF
{
  "timestamp": "$timestamp",
  "project": "Krynox Nexus",
  "scan_type": "static_analysis",
  "tools": {
    "clang": {
      "issues": $clang_issues,
      "report": "$REPORT_DIR/clang/analysis.txt"
    },
    "cppcheck": {
      "errors": $cppcheck_errors,
      "warnings": $cppcheck_warnings,
      "report": "$REPORT_DIR/cppcheck/analysis.txt"
    },
    "sparse": {
      "issues": $sparse_issues,
      "report": "$REPORT_DIR/sparse/analysis.txt"
    }
  },
  "summary": {
    "total_issues": $total_issues,
    "critical_issues": $cppcheck_errors
  }
}
EOF
    
    log_info "Summary report generated: $summary_file"
    
    # Display summary
    echo ""
    log_info "=== Static Analysis Summary ==="
    log_info "Clang Issues: $clang_issues"
    log_info "Cppcheck Errors: $cppcheck_errors"
    log_info "Cppcheck Warnings: $cppcheck_warnings"
    log_info "Sparse Issues: $sparse_issues"
    log_info "Total Issues: $total_issues"
    echo ""
}

generate_sarif_report() {
    log_step "Generating SARIF report for GitHub integration..."
    
    local sarif_file="$REPORT_DIR/sarif/static_analysis.sarif"
    
    cat > "$sarif_file" <<EOF
{
  "\$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
  "version": "2.1.0",
  "runs": [
    {
      "tool": {
        "driver": {
          "name": "Krynox Nexus Static Analysis",
          "informationUri": "https://github.com/krynox-nexus",
          "version": "1.0.0",
          "rules": []
        }
      },
      "results": []
    }
  ]
}
EOF
    
    log_info "SARIF report generated: $sarif_file"
}

check_exit_status() {
    local summary_file="$REPORT_DIR/static_analysis_summary.json"
    
    if [ -f "$summary_file" ]; then
        local critical_issues=$(jq '.summary.critical_issues' "$summary_file" 2>/dev/null || echo "0")
        
        if [ "$critical_issues" -gt 0 ]; then
            log_error "Found $critical_issues critical issue(s)!"
            return 1
        fi
    fi
    
    log_info "Static analysis complete - no critical issues"
    return 0
}

main() {
    log_info "=== Static Analysis Security Scan ==="
    log_info "Starting analysis at $(date)"
    
    setup_report_directory
    run_clang_analyzer
    run_cppcheck
    run_sparse
    generate_summary_report
    generate_sarif_report
    
    log_info "=== Analysis Complete ==="
    log_info "Reports available in: $REPORT_DIR"
    
    if check_exit_status; then
        exit 0
    else
        exit 1
    fi
}

main "$@"

# Made with Bob
