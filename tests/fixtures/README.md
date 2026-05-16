# Test Fixtures - Krynox Nexus Security Pipeline

This directory contains test fixtures for validating the vulnerability detection capabilities of the Krynox Nexus security pipeline.

## 📁 Fixture Files

### 1. `bad_input_payload.txt` (256 bytes)

**Purpose**: Extreme buffer overflow and format string vulnerability test payload

**Specifications**:
- **Size**: 256 bytes (8x the 32-byte buffer limit in `buffer_overflow.c`)
- **Format Specifiers**: 50 total (10 of each type)
  - `%s` - String pointer dereference (crashes/info disclosure)
  - `%x` - Hexadecimal stack dump (stack leakage)
  - `%p` - Pointer value display (ASLR/KASLR bypass)
  - `%d` - Decimal integer read (stack leakage alternative)
  - `%n` - Memory write (most dangerous - arbitrary writes)

**Structure**:
```
Bytes 000-031: Header with identifier and initial specifiers
Bytes 032-223: Repeating 24-byte pattern (8 iterations)
Bytes 224-255: Footer with termination marker and final specifiers
```

**Expected Detections**:
- ✅ Clang Static Analyzer: Buffer overflow, format string vulnerability
- ✅ Cppcheck: Array bounds violation, unsafe format string
- ✅ Sparse: Memory safety issues, kernel-specific warnings
- ✅ Valgrind: Buffer overrun, invalid memory access
- ✅ AddressSanitizer (ASan): Heap/stack buffer overflow
- ✅ Kernel Address Sanitizer (KASan): Kernel memory corruption

### 2. `good_input_payload.txt` (15 bytes)

**Purpose**: Compliant test data for false positive validation

**Specifications**:
- **Size**: 15 bytes (47% of 32-byte buffer - safe margin)
- **Content**: `TestPayload123\n`
- **Format**: Simple alphanumeric string with newline

**Expected Behavior**:
- ✅ No security tool alerts
- ✅ Normal code execution path
- ✅ Validates that security tools don't produce false positives
- ✅ Confirms proper bounds checking in secure code

---

## 🎯 Usage Examples

### Static Analysis Testing

#### Test with Clang Static Analyzer
```bash
# Analyze vulnerable module with bad payload reference
clang --analyze \
  -Xanalyzer -analyzer-output=text \
  -I/usr/src/linux-headers-$(uname -r)/include \
  src/vulnerable/buffer_overflow.c

# Expected: Warnings about buffer overflow and format string issues
```

#### Test with Cppcheck
```bash
# Run Cppcheck on vulnerable modules
cppcheck --enable=all \
  --inconclusive \
  --std=c11 \
  src/vulnerable/

# Expected: Array bounds and format string warnings
```

#### Test with Sparse
```bash
# Kernel-specific static analysis
make C=2 CF="-D__CHECK_ENDIAN__" \
  -C /lib/modules/$(uname -r)/build \
  M=$(pwd)/src/vulnerable

# Expected: Memory safety and kernel API warnings
```

### Dynamic Analysis Testing

⚠️ **WARNING**: Dynamic testing with these payloads will likely crash the kernel. Only perform in isolated environments (VMs, containers).

#### Test with Loaded Kernel Module

**Step 1: Load the vulnerable module**
```bash
# Build and load buffer overflow module
cd src/vulnerable
make
sudo insmod buffer_overflow.ko

# Verify module loaded
lsmod | grep buffer_overflow
```

**Step 2: Test with bad payload (WILL CRASH)**
```bash
# This WILL cause kernel panic - use in VM only!
sudo cat tests/fixtures/bad_input_payload.txt > /proc/vulnerable_buffer

# Expected: Kernel panic, memory corruption, system crash
# Check dmesg for crash details
```

**Step 3: Test with good payload (should work)**
```bash
# This should execute normally
sudo cat tests/fixtures/good_input_payload.txt > /proc/vulnerable_buffer

# Check kernel log
dmesg | tail -20

# Expected: Normal log messages, no crashes
```

**Step 4: Cleanup**
```bash
# Unload module (if system didn't crash)
sudo rmmod buffer_overflow
```

#### Test with Valgrind (User-Space Simulation)

For safer testing, create a user-space version of the vulnerable functions:

```bash
# Compile user-space test harness
gcc -g -O0 tests/unit/test_secure_modules.c -o test_harness

# Run with Valgrind
valgrind --leak-check=full \
  --show-leak-kinds=all \
  --track-origins=yes \
  ./test_harness tests/fixtures/bad_input_payload.txt

# Expected: Buffer overflow detection, memory errors
```

#### Test with AddressSanitizer

```bash
# Compile with ASan
gcc -fsanitize=address -g -O1 \
  tests/unit/test_secure_modules.c -o test_harness_asan

# Run with bad payload
./test_harness_asan tests/fixtures/bad_input_payload.txt

# Expected: ASan error report with stack trace
```

### Use-After-Free Module Testing

The `use_after_free.c` module uses command-based triggers:

```bash
# Load UAF module
sudo insmod src/vulnerable/use_after_free.ko

# Trigger different vulnerabilities
echo "1" | sudo tee /proc/vulnerable_uaf  # Use-after-free
echo "2" | sudo tee /proc/vulnerable_uaf  # Double-free
echo "3" | sudo tee /proc/vulnerable_uaf  # Dangling pointer
echo "4" | sudo tee /proc/vulnerable_uaf  # Memory leak

# Check kernel log
dmesg | tail -30

# Unload module
sudo rmmod use_after_free
```

---

## 🔬 CI/CD Integration

### GitHub Actions Workflow

```yaml
- name: Run Static Analysis with Test Fixtures
  run: |
    # Reference fixtures in security scan
    ./scripts/security/run_static_analysis.sh
    
    # Verify bad payload triggers detections
    grep -q "buffer overflow" reports/static-analysis.json
    grep -q "format string" reports/static-analysis.json
    
    # Verify good payload doesn't trigger false positives
    ! grep -q "TestPayload123" reports/static-analysis.json
```

### Docker-Based Testing

```bash
# Build security scanner container
docker-compose -f docker/docker-compose.yml build scanner

# Run analysis with fixtures
docker-compose -f docker/docker-compose.yml run scanner \
  bash -c "
    clang --analyze src/vulnerable/buffer_overflow.c
    cppcheck --enable=all src/vulnerable/
  "

# Check results
docker-compose -f docker/docker-compose.yml run scanner \
  cat reports/static-analysis.json
```

---

## 📊 Expected Detection Results

### Vulnerability Detection Matrix

| Tool | Buffer Overflow | Format String | Use-After-Free | Double-Free | Memory Leak |
|------|----------------|---------------|----------------|-------------|-------------|
| Clang Static Analyzer | ✅ | ✅ | ✅ | ✅ | ⚠️ |
| Cppcheck | ✅ | ✅ | ⚠️ | ⚠️ | ❌ |
| Sparse | ✅ | ⚠️ | ⚠️ | ⚠️ | ❌ |
| Valgrind | ✅ | ✅ | ✅ | ✅ | ✅ |
| AddressSanitizer | ✅ | ✅ | ✅ | ✅ | ⚠️ |
| KASan | ✅ | ✅ | ✅ | ✅ | ⚠️ |

**Legend**:
- ✅ Reliably detects
- ⚠️ May detect (depends on configuration)
- ❌ Does not detect

### Format Specifier Detection

| Specifier | Static Analysis | Dynamic Analysis | Severity |
|-----------|----------------|------------------|----------|
| `%s` | ✅ Clang, Cppcheck | ✅ Crash/Leak | HIGH |
| `%x` | ✅ Clang | ✅ Info Disclosure | MEDIUM |
| `%p` | ✅ Clang | ✅ ASLR Bypass | MEDIUM |
| `%d` | ✅ Clang | ✅ Info Disclosure | MEDIUM |
| `%n` | ✅ Clang, Cppcheck | ✅ Memory Write | CRITICAL |

---

## ⚠️ Safety Warnings

### Critical Safety Guidelines

1. **Never use these payloads on production systems**
2. **Always test in isolated environments**:
   - Virtual machines (VirtualBox, VMware, QEMU)
   - Docker containers with kernel module support
   - Dedicated test hardware
3. **Expect kernel panics and system crashes**
4. **Save all work before testing**
5. **Have VM snapshots ready for quick recovery**

### Recommended Test Environment

```bash
# Use QEMU for safe kernel module testing
qemu-system-x86_64 \
  -kernel /boot/vmlinuz-$(uname -r) \
  -initrd /boot/initrd.img-$(uname -r) \
  -m 2048 \
  -enable-kvm \
  -snapshot \
  -append "console=ttyS0" \
  -nographic
```

### Emergency Recovery

If system crashes during testing:

1. **VM Environment**: Restore from snapshot
2. **Physical Hardware**: Reboot and check `/var/log/kern.log`
3. **Docker**: Restart container
4. **Kernel Panic**: Analyze crash dump with `crash` utility

---

## 🔍 Analyzing Results

### Reading Static Analysis Reports

```bash
# View JSON report
cat reports/static-analysis.json | jq '.findings[] | select(.severity=="CRITICAL")'

# View HTML report
firefox reports/static-analysis.html

# View SARIF report (for GitHub integration)
cat reports/static-analysis.sarif
```

### Reading Dynamic Analysis Logs

```bash
# Kernel log analysis
dmesg | grep -E "(OVERFLOW|vulnerable_buffer|vulnerable_uaf)"

# Valgrind report
cat valgrind-report.txt | grep -A 10 "Invalid"

# ASan report
cat asan-report.txt | grep -A 20 "ERROR: AddressSanitizer"
```

### Crash Dump Analysis

```bash
# Analyze kernel crash dump
sudo crash /usr/lib/debug/boot/vmlinux-$(uname -r) /var/crash/vmcore

# In crash utility:
crash> bt              # Backtrace
crash> log             # Kernel log
crash> ps              # Process list
crash> files          # Open files
```

---

## 📈 Metrics & KPIs

### Detection Rate Goals

- **Buffer Overflow Detection**: 100% (all tools should detect)
- **Format String Detection**: ≥95% (Clang, Cppcheck)
- **Use-After-Free Detection**: ≥90% (Clang, Valgrind, ASan)
- **False Positive Rate**: <5% (good payload should not trigger)

### Performance Benchmarks

- **Static Analysis Time**: <2 minutes for all tools
- **Dynamic Analysis Time**: <5 minutes per test
- **Report Generation**: <30 seconds

---

## 🔄 Maintenance

### Updating Fixtures

When updating vulnerable modules:

1. Review buffer sizes and constraints
2. Adjust payload sizes accordingly
3. Update format specifier patterns
4. Re-validate detection rates
5. Update this documentation

### Adding New Fixtures

To add new test fixtures:

1. Create fixture file in `tests/fixtures/`
2. Document purpose and specifications
3. Add usage examples to this README
4. Update CI/CD workflows
5. Validate with all security tools

---

## 📚 References

### CWE Mappings

- **CWE-119**: Improper Restriction of Operations within Bounds
- **CWE-120**: Buffer Copy without Checking Size of Input
- **CWE-121**: Stack-based Buffer Overflow
- **CWE-122**: Heap-based Buffer Overflow
- **CWE-134**: Use of Externally-Controlled Format String
- **CWE-415**: Double Free
- **CWE-416**: Use After Free
- **CWE-401**: Missing Release of Memory after Effective Lifetime

### Related Documentation

- [Kernel Hardening Quick Reference](../../docs/security/KERNEL_HARDENING_QUICK_REFERENCE.md)
- [ARM Edge Device Hardening](../../docs/security/ARM_EDGE_DEVICE_HARDENING.md)
- [Security Scan Scripts](../../scripts/security/)
- [AGENTS.md](../../AGENTS.md) - Bob's security guidelines

---

## 🤝 Contributing

When contributing new fixtures:

1. Follow the naming convention: `{type}_input_payload.txt`
2. Document all specifications
3. Provide usage examples
4. Validate with all security tools
5. Update this README

---

**Status**: ✅ Active  
**Last Updated**: 2026-05-16  
**Maintainer**: Bob - Security Architect & Kernel Engineer

---

*Made with ❤️ by the Krynox Nexus Security Team*