#!/bin/bash
#
# run_ibm_bob.sh - Run IBM Bob CLI for architectural analysis
#
# This script executes IBM Bob CLI to analyze kernel modules for
# architectural vulnerabilities and security issues.
#
# Part of Krynox Nexus - Zero-Trust Kernel Module Hardening

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SRC_DIR="$PROJECT_ROOT/src"
REPORT_DIR="$PROJECT_ROOT/reports/bob"

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

check_bob_installed() {
    log_step "Checking IBM Bob CLI installation..."
    
    if ! command -v bob &> /dev/null; then
        log_error "IBM Bob CLI not found!"
        log_error "Install it with: npm install -g @ibm/bob-cli"
        exit 1
    fi
    
    local bob_version=$(bob --version 2>&1 || echo "unknown")
    log_info "IBM Bob CLI version: $bob_version"
}

setup_report_directory() {
    log_step "Setting up report directory..."
    
    mkdir -p "$REPORT_DIR"
    
    # Create subdirectories for different report types
    mkdir -p "$REPORT_DIR/json"
    mkdir -p "$REPORT_DIR/html"
    mkdir -p "$REPORT_DIR/sarif"
    
    log_info "Report directory ready: $REPORT_DIR"
}

analyze_source_files() {
    log_step "Analyzing source files with IBM Bob..."
    
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local findings=0
    
    # Find all C source files
    find "$SRC_DIR" -name "*.c" | while read -r source_file; do
        local file_name=$(basename "$source_file" .c)
        local relative_path=${source_file#$PROJECT_ROOT/}
        
        log_info "Analyzing: $relative_path"
        
        # Run IBM Bob analysis
        local json_report="$REPORT_DIR/json/${file_name}_${timestamp}.json"
        local html_report="$REPORT_DIR/html/${file_name}_${timestamp}.html"
        
        # Execute Bob CLI with various security checks
        if bob analyze \
            --input "$source_file" \
            --output "$json_report" \
            --format json \
            --severity all \
            --include-cwe \
            2>&1 | tee -a "$REPORT_DIR/bob_analysis.log"; then
            
            log_info "✓ Analysis complete: $file_name"
            
            # Count findings
            if [ -f "$json_report" ]; then
                local file_findings=$(jq '.findings | length' "$json_report" 2>/dev/null || echo "0")
                findings=$((findings + file_findings))
                
                if [ "$file_findings" -gt 0 ]; then
                    log_warn "Found $file_findings issue(s) in $file_name"
                fi
            fi
        else
            log_warn "✗ Analysis failed for: $file_name"
        fi
    done
    
    log_info "Total findings: $findings"
    echo "$findings" > "$REPORT_DIR/findings_count.txt"
}

generate_summary_report() {
    log_step "Generating summary report..."
    
    local summary_file="$REPORT_DIR/bob_summary.json"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    cat > "$summary_file" <<EOF
{
  "tool": "IBM Bob CLI",
  "timestamp": "$timestamp",
  "project": "Krynox Nexus",
  "scan_type": "architectural_analysis",
  "summary": {
EOF
    
    # Aggregate findings from all JSON reports
    local total_findings=0
    local critical=0
    local high=0
    local medium=0
    local low=0
    
    if [ -d "$REPORT_DIR/json" ]; then
        for report in "$REPORT_DIR/json"/*.json; do
            if [ -f "$report" ]; then
                # Count findings by severity
                critical=$((critical + $(jq '[.findings[] | select(.severity=="critical")] | length' "$report" 2>/dev/null || echo "0")))
                high=$((high + $(jq '[.findings[] | select(.severity=="high")] | length' "$report" 2>/dev/null || echo "0")))
                medium=$((medium + $(jq '[.findings[] | select(.severity=="medium")] | length' "$report" 2>/dev/null || echo "0")))
                low=$((low + $(jq '[.findings[] | select(.severity=="low")] | length' "$report" 2>/dev/null || echo "0")))
            fi
        done
    fi
    
    total_findings=$((critical + high + medium + low))
    
    cat >> "$summary_file" <<EOF
    "total_findings": $total_findings,
    "by_severity": {
      "critical": $critical,
      "high": $high,
      "medium": $medium,
      "low": $low
    }
  },
  "reports": {
    "json": "$REPORT_DIR/json",
    "html": "$REPORT_DIR/html",
    "sarif": "$REPORT_DIR/sarif"
  }
}
EOF
    
    log_info "Summary report generated: $summary_file"
    
    # Display summary
    echo ""
    log_info "=== IBM Bob Analysis Summary ==="
    log_info "Total Findings: $total_findings"
    log_info "  Critical: $critical"
    log_info "  High: $high"
    log_info "  Medium: $medium"
    log_info "  Low: $low"
    echo ""
}

convert_to_sarif() {
    log_step "Converting IBM Bob output to SARIF format..."
    
    local converter_dir="$SCRIPT_DIR/sarif_converters"
    local sarif_file="$REPORT_DIR/sarif/bob_results.sarif"
    
    # Ensure Python 3 is available
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 not found, skipping SARIF conversion"
        return 1
    fi
    
    # Check if we have JSON reports to convert
    if [ ! -d "$REPORT_DIR/json" ] || [ -z "$(ls -A $REPORT_DIR/json/*.json 2>/dev/null)" ]; then
        log_warn "No IBM Bob JSON reports found, skipping SARIF conversion"
        return 0
    fi
    
    # Convert the first JSON report (or merge multiple if needed)
    local first_json=$(ls "$REPORT_DIR/json"/*.json 2>/dev/null | head -n 1)
    
    if [ -n "$first_json" ]; then
        log_info "Converting IBM Bob JSON to SARIF..."
        python3 "$converter_dir/bob_converter.py" \
            --input "$first_json" \
            --output "$sarif_file" \
            --project-root "$PROJECT_ROOT" \
            2>&1 | tee -a "$REPORT_DIR/sarif_conversion.log"
        
        if [ ${PIPESTATUS[0]} -eq 0 ]; then
            log_info "✓ IBM Bob SARIF conversion successful"
        else
            log_warn "✗ IBM Bob SARIF conversion failed"
        fi
    fi
}

check_exit_status() {
    local findings_count=$(cat "$REPORT_DIR/findings_count.txt" 2>/dev/null || echo "0")
    
    if [ "$findings_count" -gt 0 ]; then
        log_warn "IBM Bob found $findings_count security issue(s)"
        
        # Check for critical/high severity issues
        local critical_high=$(jq -s '[.[] | .findings[] | select(.severity=="critical" or .severity=="high")] | length' "$REPORT_DIR/json"/*.json 2>/dev/null || echo "0")
        
        if [ "$critical_high" -gt 0 ]; then
            log_error "Found $critical_high critical/high severity issue(s)!"
            return 1
        fi
    else
        log_info "No security issues found by IBM Bob"
    fi
    
    return 0
}

main() {
    log_info "=== IBM Bob CLI Security Analysis ==="
    log_info "Starting analysis at $(date)"
    
    check_bob_installed
    setup_report_directory
    analyze_source_files
    generate_summary_report
    convert_to_sarif
    
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
