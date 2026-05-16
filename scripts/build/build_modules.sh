#!/bin/bash
#
# build_modules.sh - Build kernel modules for Krynox Nexus
#
# This script compiles all kernel modules with security-enhanced flags
# and generates build reports for the CI/CD pipeline.
#
# Part of Krynox Nexus - Zero-Trust Kernel Module Hardening

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SRC_DIR="$PROJECT_ROOT/src"
BUILD_LOG="$PROJECT_ROOT/build.log"
REPORT_DIR="$PROJECT_ROOT/reports"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1" | tee -a "$BUILD_LOG"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$BUILD_LOG"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$BUILD_LOG"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1" | tee -a "$BUILD_LOG"
}

check_kernel_headers() {
    log_step "Checking kernel headers..."
    
    KERNEL_VERSION=$(uname -r)
    KERNEL_DIR="/lib/modules/$KERNEL_VERSION/build"
    
    if [ ! -d "$KERNEL_DIR" ]; then
        log_error "Kernel headers not found for version $KERNEL_VERSION"
        log_error "Please install kernel headers: sudo apt-get install linux-headers-$KERNEL_VERSION"
        exit 1
    fi
    
    log_info "Kernel headers found: $KERNEL_VERSION"
}

setup_build_environment() {
    log_step "Setting up build environment..."
    
    # Create reports directory
    mkdir -p "$REPORT_DIR"
    
    # Clear previous build log
    > "$BUILD_LOG"
    
    # Export build flags
    export KCFLAGS="-Wall -Wextra -Werror -Wformat-security"
    export KCFLAGS="$KCFLAGS -Wstack-protector -fno-strict-overflow"
    export KCFLAGS="$KCFLAGS -fno-delete-null-pointer-checks"
    
    log_info "Build environment configured"
}

clean_previous_build() {
    log_step "Cleaning previous build artifacts..."
    
    cd "$SRC_DIR"
    
    if [ -f Makefile ] || [ -f Kbuild ]; then
        make clean 2>&1 | tee -a "$BUILD_LOG" || true
    fi
    
    # Remove build artifacts
    find . -name "*.o" -delete
    find . -name "*.ko" -delete
    find . -name "*.mod" -delete
    find . -name "*.mod.c" -delete
    find . -name ".*.cmd" -delete
    find . -name "modules.order" -delete
    find . -name "Module.symvers" -delete
    find . -name ".tmp_versions" -type d -exec rm -rf {} + 2>/dev/null || true
    
    log_info "Build artifacts cleaned"
}

build_modules() {
    log_step "Building kernel modules..."
    
    cd "$SRC_DIR"
    
    local build_start=$(date +%s)
    
    # Build all modules
    if make -j$(nproc) 2>&1 | tee -a "$BUILD_LOG"; then
        local build_end=$(date +%s)
        local build_time=$((build_end - build_start))
        
        log_info "Build completed successfully in ${build_time}s"
        
        # List built modules
        log_info "Built modules:"
        find . -name "*.ko" -exec basename {} \; | while read -r module; do
            log_info "  - $module"
        done
        
        return 0
    else
        log_error "Build failed! Check $BUILD_LOG for details"
        return 1
    fi
}

generate_build_report() {
    log_step "Generating build report..."
    
    local report_file="$REPORT_DIR/build-report.json"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    cat > "$report_file" <<EOF
{
  "timestamp": "$timestamp",
  "kernel_version": "$(uname -r)",
  "gcc_version": "$(gcc --version | head -n1)",
  "build_status": "success",
  "modules": [
EOF
    
    local first=true
    find "$SRC_DIR" -name "*.ko" | while read -r module; do
        if [ "$first" = true ]; then
            first=false
        else
            echo "," >> "$report_file"
        fi
        
        local module_name=$(basename "$module")
        local module_size=$(stat -f%z "$module" 2>/dev/null || stat -c%s "$module")
        
        cat >> "$report_file" <<EOF
    {
      "name": "$module_name",
      "path": "$module",
      "size": $module_size
    }
EOF
    done
    
    cat >> "$report_file" <<EOF

  ],
  "build_log": "$BUILD_LOG"
}
EOF
    
    log_info "Build report generated: $report_file"
}

check_module_symbols() {
    log_step "Checking module symbols..."
    
    local symbols_report="$REPORT_DIR/symbols-report.txt"
    > "$symbols_report"
    
    find "$SRC_DIR" -name "*.ko" | while read -r module; do
        echo "=== $(basename "$module") ===" >> "$symbols_report"
        nm "$module" | grep -E "^[0-9a-f]+ [TtDdBb]" >> "$symbols_report" || true
        echo "" >> "$symbols_report"
    done
    
    log_info "Symbol report generated: $symbols_report"
}

verify_modules() {
    log_step "Verifying module integrity..."
    
    local modules_found=0
    
    find "$SRC_DIR" -name "*.ko" | while read -r module; do
        ((modules_found++))
        
        # Check if module is valid
        if modinfo "$module" &>/dev/null; then
            log_info "✓ $(basename "$module") - Valid"
        else
            log_warn "✗ $(basename "$module") - Invalid or corrupted"
        fi
    done
    
    if [ $modules_found -eq 0 ]; then
        log_error "No kernel modules were built!"
        return 1
    fi
    
    log_info "Module verification complete"
}

main() {
    log_info "=== Krynox Nexus Kernel Module Build ==="
    log_info "Starting build process at $(date)"
    
    check_kernel_headers
    setup_build_environment
    clean_previous_build
    
    if build_modules; then
        generate_build_report
        check_module_symbols
        verify_modules
        
        log_info "=== Build Process Complete ==="
        log_info "Build log: $BUILD_LOG"
        log_info "Reports: $REPORT_DIR"
        exit 0
    else
        log_error "=== Build Process Failed ==="
        exit 1
    fi
}

main "$@"

# Made with Bob
