# SARIF Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the SARIF implementation to GitHub and verifying the Security tab integration.

---

## Prerequisites

### Required Tools
- Git 2.x or higher
- GitHub account with repository access
- GitHub Personal Access Token (PAT) or SSH key configured
- Python 3.8+ (for local testing)
- Bash shell

### Optional Tools
- GitHub CLI (`gh`) for easier PR creation
- `jq` for JSON validation
- Docker (for containerized testing)

---

## Deployment Steps

### Step 1: Verify Local Implementation

Before pushing to GitHub, verify all components are in place:

```bash
# Navigate to project directory
cd /home/symtuh/Documents/Projects/Krynox-Nexus

# Check current branch
git branch
# Should show: * feature/sarif-implementation

# Verify all commits
git log --oneline -5
# Should show 5 commits related to SARIF implementation

# Run validation tests
python3 scripts/security/test_sarif_converters.py
# Should show: Test Results: 16/16 passed (100.0%)

# Check file structure
ls -la scripts/security/sarif_converters/
ls -la docs/security/SARIF*.md
ls -la .github/workflows/security-scan.yml
```

### Step 2: Configure Git Authentication

#### Option A: SSH Key (Recommended)

```bash
# Check if SSH key exists
ls -la ~/.ssh/id_*.pub

# If no key exists, generate one
ssh-keygen -t ed25519 -C "your_email@example.com"

# Add SSH key to ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Copy public key to clipboard
cat ~/.ssh/id_ed25519.pub
# Add this key to GitHub: Settings → SSH and GPG keys → New SSH key

# Update remote URL to use SSH
git remote set-url origin git@github.com:YOUR_USERNAME/krynox-nexus.git

# Test SSH connection
ssh -T git@github.com
```

#### Option B: Personal Access Token (PAT)

```bash
# Create PAT on GitHub:
# Settings → Developer settings → Personal access tokens → Tokens (classic)
# Required scopes: repo, workflow, write:packages

# Configure Git to use PAT
git config --global credential.helper store

# Push will prompt for credentials
# Username: YOUR_GITHUB_USERNAME
# Password: YOUR_PERSONAL_ACCESS_TOKEN
```

### Step 3: Push Feature Branch

```bash
# Ensure you're on the feature branch
git checkout feature/sarif-implementation

# Push to GitHub
git push -u origin feature/sarif-implementation

# Expected output:
# Enumerating objects: X, done.
# Counting objects: 100% (X/X), done.
# Writing objects: 100% (X/X), Y KiB | Z MiB/s, done.
# To github.com:YOUR_USERNAME/krynox-nexus.git
#  * [new branch]      feature/sarif-implementation -> feature/sarif-implementation
```

### Step 4: Monitor CI/CD Pipeline

#### Via GitHub Web Interface

1. Navigate to your repository on GitHub
2. Click the **Actions** tab
3. Look for the "Security Scan" workflow
4. Click on the running workflow to see details

#### Via GitHub CLI

```bash
# List recent workflow runs
gh run list --workflow=security-scan.yml

# Watch a specific run
gh run watch

# View logs for a specific run
gh run view --log
```

#### Expected Workflow Jobs

The pipeline should execute these jobs in order:

1. **Build Kernel Modules** (5-10 minutes)
   - Compiles all kernel modules
   - Uploads build artifacts

2. **CodeQL Analysis** (10-15 minutes)
   - Performs semantic analysis
   - Uploads SARIF to Security tab

3. **Static Analysis** (5-10 minutes)
   - Runs Clang, Cppcheck, Sparse
   - Converts results to SARIF
   - Uploads to Security tab

4. **IBM Bob Analysis** (5-10 minutes)
   - Architectural vulnerability analysis
   - Converts JSON to SARIF
   - Uploads to Security tab

5. **Container Security** (3-5 minutes)
   - Scans Docker images with Trivy
   - Uploads SARIF to Security tab

6. **Kernel Hardening** (2-3 minutes)
   - Verifies kernel configuration
   - Converts results to SARIF
   - Uploads to Security tab

**Total Expected Time:** 30-50 minutes

### Step 5: Verify Security Tab Integration

#### Access Security Tab

```bash
# Open in browser
https://github.com/YOUR_USERNAME/krynox-nexus/security

# Or use GitHub CLI
gh browse --repo YOUR_USERNAME/krynox-nexus --settings security
```

#### Expected Categories

Navigate to **Code scanning alerts** and verify these categories appear:

1. **CodeQL** (`/language:cpp`)
   - C/C++ semantic analysis findings
   - CWE mappings for detected issues

2. **Static Analysis** (`static-analysis`)
   - Combined results from Clang, Cppcheck, Sparse
   - Kernel-specific warnings

3. **Architectural Analysis** (`architectural-analysis`)
   - IBM Bob CLI findings
   - Design pattern vulnerabilities

4. **Kernel Hardening** (`kernel-hardening`)
   - Configuration check results
   - Security feature status

5. **Container Security** (`container-security`)
   - Trivy vulnerability scan results
   - Base image CVEs

#### Verify SARIF Upload Success

Check workflow logs for successful uploads:

```bash
# View specific job logs
gh run view --log --job=static-analysis

# Look for these success messages:
# ✓ Upload SARIF to GitHub Security
# ✓ SARIF file uploaded successfully
```

### Step 6: Review Security Findings

#### Filter by Severity

In the Security tab, use filters:
- **Critical** - Immediate action required
- **High** - Address in current sprint
- **Medium** - Schedule for next sprint
- **Low** - Technical debt backlog

#### Review Specific Findings

For each alert:
1. Click to view details
2. Review CWE classification
3. Check affected code location
4. Read remediation guidance
5. Assign to team member if needed

#### Example Finding Review

```
Alert: Buffer Overflow in kernel module
Severity: High
CWE: CWE-121 (Stack-based Buffer Overflow)
Location: src/vulnerable/buffer_overflow.c:45
Tool: Clang Static Analyzer

Description:
  Potential buffer overflow when copying user input without bounds checking.
  
Recommendation:
  Use strncpy() instead of strcpy() and validate input length.
```

### Step 7: Create Pull Request

#### Via GitHub CLI

```bash
gh pr create \
  --title "feat: Implement comprehensive SARIF 2.1.0 support" \
  --body "$(cat <<EOF
## Summary
Implements comprehensive SARIF 2.1.0 support for all security tools in the Krynox Nexus pipeline.

## Changes
- ✅ Added SARIF converters for 7 security tools
- ✅ Integrated CodeQL analysis
- ✅ Updated GitHub Actions workflow
- ✅ Added comprehensive documentation
- ✅ Implemented CWE mapping for 40+ vulnerabilities
- ✅ Added status badges to README

## Testing
- ✅ All SARIF converters validated (16/16 tests passed)
- ✅ Workflow executed successfully
- ✅ Security tab displays findings correctly

## Documentation
- SARIF Implementation Plan
- SARIF Quick Reference
- SARIF Workflow Diagram
- Deployment Guide

## Security Impact
- Unified vulnerability dashboard in Security tab
- Automated scanning on every commit
- CWE-mapped findings with remediation guidance
- Zero-trust architecture compliance

## Checklist
- [x] Code follows project style guidelines
- [x] Documentation updated
- [x] Tests passing
- [x] Security scan completed
- [x] No critical vulnerabilities introduced
EOF
)" \
  --base main \
  --head feature/sarif-implementation
```

#### Via GitHub Web Interface

1. Navigate to repository on GitHub
2. Click **Pull requests** tab
3. Click **New pull request**
4. Select base: `main`, compare: `feature/sarif-implementation`
5. Fill in title and description (use template above)
6. Click **Create pull request**

### Step 8: PR Review and Merge

#### Review Checklist

- [ ] All CI/CD checks passing
- [ ] Security scan completed successfully
- [ ] No new critical vulnerabilities
- [ ] Documentation is complete
- [ ] Code review approved by maintainer
- [ ] SARIF uploads verified in Security tab

#### Merge Strategy

```bash
# Option 1: Merge via GitHub CLI
gh pr merge --squash --delete-branch

# Option 2: Merge via web interface
# Click "Squash and merge" button
# Confirm merge
# Delete feature branch
```

---

## Troubleshooting

### Issue: Push Authentication Failed

**Symptoms:**
```
fatal: could not read Username for 'https://github.com': No such device or address
```

**Solution:**
1. Configure SSH key (see Step 2, Option A)
2. Or use Personal Access Token (see Step 2, Option B)

### Issue: Workflow Fails on Python Dependencies

**Symptoms:**
```
ERROR: Failed to build 'lxml' when getting requirements to build wheel
```

**Solution:**
The workflow installs system dependencies automatically:
```yaml
- name: Install Python dependencies for SARIF converters
  run: |
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip
    pip3 install -r scripts/security/sarif_converters/requirements.txt
```

If still failing, check workflow logs for specific errors.

### Issue: SARIF Upload Fails

**Symptoms:**
```
Error: SARIF file not found
```

**Solution:**
1. Check that SARIF converters ran successfully
2. Verify SARIF file paths in workflow
3. Check converter output directories:
   ```bash
   ls -la reports/static-analysis/sarif/
   ls -la reports/bob/sarif/
   ls -la reports/hardening/sarif/
   ```

### Issue: Security Tab Shows No Results

**Symptoms:**
- Security tab exists but shows no alerts
- "No code scanning alerts" message

**Solution:**
1. Wait 5-10 minutes for processing
2. Check workflow logs for upload success
3. Verify SARIF files are valid JSON:
   ```bash
   jq . reports/static-analysis/sarif/clang_results.sarif
   ```
4. Check repository permissions (security-events: write)

### Issue: CodeQL Analysis Fails

**Symptoms:**
```
Error: No code found to analyze
```

**Solution:**
1. Ensure kernel modules build successfully
2. Check CodeQL language configuration (should be 'cpp')
3. Verify build commands in workflow

---

## Validation Commands

### Verify SARIF File Structure

```bash
# Check SARIF version
jq '.version' reports/static-analysis/sarif/clang_results.sarif

# Count findings
jq '.runs[0].results | length' reports/static-analysis/sarif/clang_results.sarif

# List CWE IDs
jq '.runs[0].results[].ruleId' reports/static-analysis/sarif/clang_results.sarif

# Validate against schema
curl -s https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json \
  | jq . > /tmp/sarif-schema.json
python3 -c "
import json
import jsonschema
schema = json.load(open('/tmp/sarif-schema.json'))
sarif = json.load(open('reports/static-analysis/sarif/clang_results.sarif'))
jsonschema.validate(sarif, schema)
print('✓ SARIF file is valid')
"
```

### Check Workflow Status

```bash
# List all workflow runs
gh run list --limit 10

# Get specific run details
gh run view RUN_ID

# Download artifacts
gh run download RUN_ID

# View job logs
gh run view RUN_ID --log --job=static-analysis
```

---

## Best Practices

### 1. Regular Security Scans

- Enable scheduled scans (daily at 2 AM UTC)
- Review Security tab weekly
- Triage new findings within 24 hours

### 2. False Positive Management

- Document false positives in `.sarif-suppressions`
- Add comments explaining why suppressed
- Review suppressions quarterly

### 3. Continuous Improvement

- Update CWE mappings as new patterns emerge
- Tune tool configurations to reduce noise
- Add new security tools as needed

### 4. Team Collaboration

- Assign security findings to developers
- Use GitHub Projects for tracking remediation
- Include security metrics in sprint reviews

---

## Additional Resources

### Documentation
- [SARIF Specification 2.1.0](https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html)
- [GitHub Code Scanning](https://docs.github.com/en/code-security/code-scanning)
- [CodeQL Documentation](https://codeql.github.com/docs/)

### Tools
- [SARIF Viewer (VS Code)](https://marketplace.visualstudio.com/items?itemName=MS-SarifVSCode.sarif-viewer)
- [SARIF Multitool](https://github.com/microsoft/sarif-sdk)
- [SARIF Tutorials](https://github.com/microsoft/sarif-tutorials)

### Support
- GitHub Issues: Report bugs or request features
- Documentation: `docs/security/`

## Appendix: Workflow YAML Reference

### SARIF Upload Configuration

```yaml
- name: Upload SARIF to GitHub Security
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: reports/static-analysis/sarif/clang_results.sarif
    category: static-analysis
  continue-on-error: true
```

### Required Permissions

```yaml
permissions:
  contents: read
  security-events: write
  actions: read
```

### Environment Variables

```yaml
env:
  REPORTS_DIR: 'reports'
  SARIF_DIR: 'sarif-reports'
```

---

**Last Updated:** 2026-05-17  
**Version:** 1.0.0  
**Maintainer:** Krynox Security Agent (AI Security Architect)