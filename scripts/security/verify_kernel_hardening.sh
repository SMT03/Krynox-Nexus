#!/bin/bash
# verify_kernel_hardening.sh - Verify kernel hardening for Krynox Nexus modules
# Part of Krynox Nexus - Zero-Trust Kernel Module Hardening
# Target: ARM64 Edge Devices (Google Pixel 6a and similar)

set -e

echo "=== Krynox Nexus Kernel Hardening Verification ==="
echo "Target: ARM64 Edge Device (Google Pixel 6a)"
echo "Module: hello_secure.ko"
echo "Date: $(date)"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

CRITICAL_FAIL=0
HIGH_FAIL=0
MEDIUM_FAIL=0
LOW_FAIL=0

# Function to check if config is set to expected value
check_config() {
    local config=$1
    local priority=$2
    local expected=$3
    
    if zcat /proc/config.gz 2>/dev/null | grep -q "^${config}=${expected}"; then
        echo -e "${GREEN}[✓]${NC} ${config}=${expected} (${priority})"
        return 0
    elif zcat /proc/config.gz 2>/dev/null | grep -q "^${config}"; then
        actual=$(zcat /proc/config.gz | grep "^${config}" | cut -d= -f2)
        echo -e "${RED}[✗]${NC} ${config}=${actual} (expected: ${expected}) (${priority})"
        case $priority in
            CRITICAL) ((CRITICAL_FAIL++)) ;;
            HIGH) ((HIGH_FAIL++)) ;;
            MEDIUM) ((MEDIUM_FAIL++)) ;;
            LOW) ((LOW_FAIL++)) ;;
        esac
        return 1
    else
        echo -e "${RED}[✗]${NC} ${config} NOT SET (expected: ${expected}) (${priority})"
        case $priority in
            CRITICAL) ((CRITICAL_FAIL++)) ;;
            HIGH) ((HIGH_FAIL++)) ;;
            MEDIUM) ((MEDIUM_FAIL++)) ;;
            LOW) ((LOW_FAIL++)) ;;
        esac
        return 1
    fi
}

# Function to check if config is NOT set
check_not_set() {
    local config=$1
    local priority=$2
    
    if zcat /proc/config.gz 2>/dev/null | grep -q "^${config}="; then
        echo -e "${RED}[✗]${NC} ${config} is SET (should not be set) (${priority})"
        case $priority in
            CRITICAL) ((CRITICAL_FAIL++)) ;;
            HIGH) ((HIGH_FAIL++)) ;;
            MEDIUM) ((MEDIUM_FAIL++)) ;;
            LOW) ((LOW_FAIL++)) ;;
        esac
        return 1
    else
        echo -e "${GREEN}[✓]${NC} ${config} is not set (${priority})"
        return 0
    fi
}

echo -e "${BLUE}=== TIER 1: MANDATORY CONFIGURATIONS ===${NC}"
check_config "CONFIG_FORTIFY_SOURCE" "CRITICAL" "y"
check_config "CONFIG_HARDENED_USERCOPY" "CRITICAL" "y"
check_config "CONFIG_SLAB_FREELIST_RANDOM" "CRITICAL" "y"
check_config "CONFIG_SLAB_FREELIST_HARDENED" "CRITICAL" "y"
check_config "CONFIG_INIT_ON_ALLOC_DEFAULT_ON" "HIGH" "y"
check_config "CONFIG_INIT_ON_FREE_DEFAULT_ON" "HIGH" "y"
check_config "CONFIG_STACKPROTECTOR_STRONG" "CRITICAL" "y"
check_config "CONFIG_STRICT_KERNEL_RWX" "CRITICAL" "y"
check_config "CONFIG_STRICT_MODULE_RWX" "CRITICAL" "y"
check_config "CONFIG_RANDOMIZE_BASE" "CRITICAL" "y"

echo ""
echo -e "${BLUE}=== TIER 2: HIGHLY RECOMMENDED CONFIGURATIONS ===${NC}"
check_config "CONFIG_VMAP_STACK" "HIGH" "y"
check_config "CONFIG_HARDENED_ATOMIC" "HIGH" "y"
check_config "CONFIG_SECURITY_DMESG_RESTRICT" "MEDIUM" "y"
check_config "CONFIG_SECURITY_LOADPIN" "HIGH" "y"
check_config "CONFIG_MODULE_SIG" "CRITICAL" "y"
check_config "CONFIG_MODULE_SIG_FORCE" "CRITICAL" "y"
check_config "CONFIG_MODULE_SIG_SHA256" "HIGH" "y"
check_config "CONFIG_SECURITY_SELINUX" "CRITICAL" "y"
check_not_set "CONFIG_SECURITY_SELINUX_BOOTPARAM" "HIGH"
check_config "CONFIG_DEFAULT_SECURITY_SELINUX" "HIGH" "y"

echo ""
echo -e "${BLUE}=== TIER 3: RECOMMENDED CONFIGURATIONS ===${NC}"
check_config "CONFIG_PANIC_ON_OOPS" "MEDIUM" "y"
check_config "CONFIG_GCC_PLUGIN_STRUCTLEAK_BYREF_ALL" "MEDIUM" "y"
check_config "CONFIG_GCC_PLUGIN_LATENT_ENTROPY" "LOW" "y"
check_config "CONFIG_GCC_PLUGIN_RANDSTRUCT" "MEDIUM" "y"
check_config "CONFIG_REFCOUNT_FULL" "HIGH" "y"

echo ""
echo -e "${BLUE}=== ARM64-SPECIFIC CONFIGURATIONS ===${NC}"
# Check for hardware PAN first, fall back to software PAN
if zcat /proc/config.gz 2>/dev/null | grep -q "^CONFIG_ARM64_PAN=y"; then
    echo -e "${GREEN}[✓]${NC} CONFIG_ARM64_PAN=y (hardware PAN) (HIGH)"
elif zcat /proc/config.gz 2>/dev/null | grep -q "^CONFIG_ARM64_SW_TTBR0_PAN=y"; then
    echo -e "${GREEN}[✓]${NC} CONFIG_ARM64_SW_TTBR0_PAN=y (software PAN) (HIGH)"
else
    echo -e "${RED}[✗]${NC} Neither CONFIG_ARM64_PAN nor CONFIG_ARM64_SW_TTBR0_PAN is set (HIGH)"
    ((HIGH_FAIL++))
fi

echo ""
echo -e "${BLUE}=== RUNTIME CHECKS ===${NC}"

# Check SELinux status
if command -v getenforce &> /dev/null; then
    selinux_status=$(getenforce)
    if [ "$selinux_status" = "Enforcing" ]; then
        echo -e "${GREEN}[✓]${NC} SELinux is Enforcing"
    elif [ "$selinux_status" = "Permissive" ]; then
        echo -e "${YELLOW}[!]${NC} SELinux is Permissive (should be Enforcing)"
        ((HIGH_FAIL++))
    else
        echo -e "${RED}[✗]${NC} SELinux is Disabled (should be Enforcing)"
        ((CRITICAL_FAIL++))
    fi
else
    echo -e "${YELLOW}[!]${NC} getenforce command not found (cannot verify SELinux)"
fi

# Check panic timeout
if [ -f /proc/sys/kernel/panic ]; then
    panic_timeout=$(cat /proc/sys/kernel/panic)
    if [ "$panic_timeout" = "-1" ]; then
        echo -e "${GREEN}[✓]${NC} Panic timeout is -1 (immediate reboot)"
    elif [ "$panic_timeout" = "0" ]; then
        echo -e "${YELLOW}[!]${NC} Panic timeout is 0 (no reboot, recommended: -1)"
    else
        echo -e "${YELLOW}[!]${NC} Panic timeout is $panic_timeout seconds (recommended: -1)"
    fi
fi

# Check dmesg restriction (only if not root)
if [ $EUID -ne 0 ]; then
    if ! dmesg &> /dev/null; then
        echo -e "${GREEN}[✓]${NC} dmesg is restricted to privileged users"
    else
        echo -e "${YELLOW}[!]${NC} dmesg is accessible to unprivileged users"
    fi
else
    echo -e "${BLUE}[i]${NC} Running as root, skipping dmesg restriction check"
fi

# Check KASLR effectiveness
if [ -f /proc/kallsyms ]; then
    text_addr=$(grep " _text$" /proc/kallsyms | cut -d' ' -f1)
    if [ "$text_addr" != "0000000000000000" ] && [ -n "$text_addr" ]; then
        echo -e "${GREEN}[✓]${NC} KASLR appears active (kernel text at 0x$text_addr)"
    else
        echo -e "${YELLOW}[!]${NC} KASLR may not be active or addresses are hidden"
    fi
fi

# Check for kernel lockdown
if [ -f /sys/kernel/security/lockdown ]; then
    lockdown_status=$(cat /sys/kernel/security/lockdown)
    if echo "$lockdown_status" | grep -q "\[integrity\]"; then
        echo -e "${GREEN}[✓]${NC} Kernel lockdown: integrity mode"
    elif echo "$lockdown_status" | grep -q "\[confidentiality\]"; then
        echo -e "${GREEN}[✓]${NC} Kernel lockdown: confidentiality mode (maximum security)"
    else
        echo -e "${YELLOW}[!]${NC} Kernel lockdown: $lockdown_status"
    fi
fi

echo ""
echo -e "${BLUE}=== SUMMARY ===${NC}"
echo -e "Critical failures: ${RED}${CRITICAL_FAIL}${NC}"
echo -e "High priority failures: ${YELLOW}${HIGH_FAIL}${NC}"
echo -e "Medium priority failures: ${YELLOW}${MEDIUM_FAIL}${NC}"
echo -e "Low priority failures: ${YELLOW}${LOW_FAIL}${NC}"

echo ""
if [ $CRITICAL_FAIL -gt 0 ]; then
    echo -e "${RED}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  [FAIL] CRITICAL security configurations missing!         ║${NC}"
    echo -e "${RED}║  DO NOT deploy modules to this device!                    ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Required actions:"
    echo "1. Review missing CRITICAL configurations above"
    echo "2. Rebuild kernel with required security options"
    echo "3. Re-run this verification script"
    echo "4. Only deploy modules after all CRITICAL checks pass"
    exit 1
elif [ $HIGH_FAIL -gt 0 ]; then
    echo -e "${YELLOW}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║  [WARN] High priority security configurations missing     ║${NC}"
    echo -e "${YELLOW}║  Deployment not recommended without security review       ║${NC}"
    echo -e "${YELLOW}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Recommended actions:"
    echo "1. Review missing HIGH priority configurations"
    echo "2. Assess risk for your specific use case"
    echo "3. Consider rebuilding kernel with missing options"
    echo "4. Document accepted risks if proceeding"
    exit 2
elif [ $MEDIUM_FAIL -gt 0 ]; then
    echo -e "${YELLOW}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║  [WARN] Medium priority security configurations missing   ║${NC}"
    echo -e "${YELLOW}║  Deployment acceptable but not optimal                    ║${NC}"
    echo -e "${YELLOW}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Optional actions:"
    echo "1. Review missing MEDIUM priority configurations"
    echo "2. Consider enabling for enhanced security"
    echo "3. Deployment can proceed with current configuration"
    exit 3
else
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  [PASS] All critical security configurations present!     ║${NC}"
    echo -e "${GREEN}║  Device is ready for secure module deployment             ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Sign your kernel module with device-specific keys"
    echo "2. Test module in SELinux permissive mode first"
    echo "3. Create SELinux policy for your module"
    echo "4. Deploy module in SELinux enforcing mode"
    echo "5. Monitor kernel logs for security events"
    exit 0
fi

# Made with Bob
