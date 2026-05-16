#!/bin/bash
#
# install_tools.sh - Install security analysis tools for Krynox Nexus
#
# This script installs all required security tools for the CI/CD pipeline:
# - Static analyzers (Clang, Cppcheck, Sparse)
# - Memory safety tools (Valgrind, AddressSanitizer)
# - Fuzzing tools (AFL++, Syzkaller dependencies)
# - IBM Bob CLI
#
# Part of Krynox Nexus - Zero-Trust Kernel Module Hardening

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
        VERSION=$VERSION_ID
    else
        log_error "Cannot detect Linux distribution"
        exit 1
    fi
    log_info "Detected distribution: $DISTRO $VERSION"
}

install_kernel_headers() {
    log_info "Installing kernel headers and build tools..."
    
    case $DISTRO in
        ubuntu|debian)
            apt-get update
            apt-get install -y \
                linux-headers-$(uname -r) \
                build-essential \
                gcc \
                make \
                git \
                curl \
                wget
            ;;
        fedora|rhel|centos)
            dnf install -y \
                kernel-devel-$(uname -r) \
                gcc \
                make \
                git \
                curl \
                wget
            ;;
        arch)
            pacman -Sy --noconfirm \
                linux-headers \
                base-devel \
                git \
                curl \
                wget
            ;;
        *)
            log_error "Unsupported distribution: $DISTRO"
            exit 1
            ;;
    esac
    
    log_info "Kernel headers installed successfully"
}

install_static_analyzers() {
    log_info "Installing static analysis tools..."
    
    case $DISTRO in
        ubuntu|debian)
            apt-get install -y \
                clang \
                clang-tools \
                clang-tidy \
                cppcheck \
                sparse
            ;;
        fedora|rhel|centos)
            dnf install -y \
                clang \
                clang-tools-extra \
                cppcheck \
                sparse
            ;;
        arch)
            pacman -S --noconfirm \
                clang \
                cppcheck \
                sparse
            ;;
    esac
    
    log_info "Static analyzers installed successfully"
}

install_memory_tools() {
    log_info "Installing memory safety tools..."
    
    case $DISTRO in
        ubuntu|debian)
            apt-get install -y \
                valgrind \
                libasan6 \
                libubsan1 \
                libtsan0
            ;;
        fedora|rhel|centos)
            dnf install -y \
                valgrind \
                libasan \
                libubsan \
                libtsan
            ;;
        arch)
            pacman -S --noconfirm \
                valgrind
            ;;
    esac
    
    log_info "Memory safety tools installed successfully"
}

install_fuzzing_tools() {
    log_info "Installing fuzzing tools..."
    
    # Install AFL++
    if ! command -v afl-fuzz &> /dev/null; then
        log_info "Installing AFL++..."
        
        case $DISTRO in
            ubuntu|debian)
                apt-get install -y \
                    afl++ \
                    afl++-clang
                ;;
            fedora|rhel|centos)
                # Build from source for RHEL-based
                cd /tmp
                git clone https://github.com/AFLplusplus/AFLplusplus
                cd AFLplusplus
                make
                make install
                cd "$PROJECT_ROOT"
                ;;
            arch)
                pacman -S --noconfirm afl++
                ;;
        esac
    else
        log_info "AFL++ already installed"
    fi
    
    # Install Syzkaller dependencies
    log_info "Installing Syzkaller dependencies..."
    
    case $DISTRO in
        ubuntu|debian)
            apt-get install -y \
                golang \
                qemu-system-x86
            ;;
        fedora|rhel|centos)
            dnf install -y \
                golang \
                qemu-system-x86
            ;;
        arch)
            pacman -S --noconfirm \
                go \
                qemu-system-x86
            ;;
    esac
    
    log_info "Fuzzing tools installed successfully"
}

install_ibm_bob() {
    log_info "Installing IBM Bob CLI..."
    
    # Check if IBM Bob is already installed
    if command -v bob &> /dev/null; then
        log_info "IBM Bob CLI already installed"
        return
    fi
    
    # Install Node.js if not present (required for IBM Bob)
    if ! command -v node &> /dev/null; then
        log_info "Installing Node.js..."
        
        case $DISTRO in
            ubuntu|debian)
                curl -fsSL https://deb.nodesource.com/setup_lts.x | bash -
                apt-get install -y nodejs
                ;;
            fedora|rhel|centos)
                dnf install -y nodejs npm
                ;;
            arch)
                pacman -S --noconfirm nodejs npm
                ;;
        esac
    fi
    
    # Install IBM Bob CLI globally
    log_info "Installing IBM Bob CLI via npm..."
    npm install -g @ibm/bob-cli
    
    log_info "IBM Bob CLI installed successfully"
}

install_docker() {
    log_info "Installing Docker..."
    
    if command -v docker &> /dev/null; then
        log_info "Docker already installed"
        return
    fi
    
    case $DISTRO in
        ubuntu|debian)
            apt-get install -y \
                docker.io \
                docker-compose
            systemctl enable docker
            systemctl start docker
            ;;
        fedora|rhel|centos)
            dnf install -y \
                docker \
                docker-compose
            systemctl enable docker
            systemctl start docker
            ;;
        arch)
            pacman -S --noconfirm \
                docker \
                docker-compose
            systemctl enable docker
            systemctl start docker
            ;;
    esac
    
    log_info "Docker installed successfully"
}

verify_installation() {
    log_info "Verifying tool installation..."
    
    local tools=(
        "gcc:GCC Compiler"
        "clang:Clang Compiler"
        "cppcheck:Cppcheck"
        "sparse:Sparse"
        "valgrind:Valgrind"
        "afl-fuzz:AFL++"
        "go:Go Language"
        "docker:Docker"
        "node:Node.js"
    )
    
    local failed=0
    
    for tool_info in "${tools[@]}"; do
        IFS=':' read -r cmd name <<< "$tool_info"
        if command -v "$cmd" &> /dev/null; then
            version=$(eval "$cmd --version 2>&1 | head -n1" || echo "unknown")
            log_info "✓ $name: $version"
        else
            log_warn "✗ $name: Not found"
            ((failed++))
        fi
    done
    
    if [ $failed -eq 0 ]; then
        log_info "All tools installed successfully!"
        return 0
    else
        log_warn "$failed tool(s) not found. Some features may not work."
        return 1
    fi
}

main() {
    log_info "Starting Krynox Nexus security tools installation..."
    
    check_root
    detect_distro
    
    install_kernel_headers
    install_static_analyzers
    install_memory_tools
    install_fuzzing_tools
    install_ibm_bob
    install_docker
    
    verify_installation
    
    log_info "Installation complete!"
    log_info "You may need to log out and back in for group changes to take effect."
}

main "$@"

# Made with Bob
