#!/bin/bash
# Krynox Nexus - SARIF Implementation Deployment Script
# Automates the deployment of SARIF converters to GitHub

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
FEATURE_BRANCH="feature/sarif-implementation"
BASE_BRANCH="main"
REPO_NAME="krynox-nexus"

# Functions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check Git
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed"
        exit 1
    fi
    print_success "Git is installed"
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    print_success "Python 3 is installed"
    
    # Check if we're in the right directory
    if [ ! -f "README.md" ] || [ ! -d ".git" ]; then
        print_error "Not in Krynox Nexus repository root"
        exit 1
    fi
    print_success "In correct repository directory"
    
    # Check current branch
    CURRENT_BRANCH=$(git branch --show-current)
    if [ "$CURRENT_BRANCH" != "$FEATURE_BRANCH" ]; then
        print_warning "Not on $FEATURE_BRANCH branch (currently on $CURRENT_BRANCH)"
        read -p "Switch to $FEATURE_BRANCH? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git checkout "$FEATURE_BRANCH"
            print_success "Switched to $FEATURE_BRANCH"
        else
            print_error "Deployment cancelled"
            exit 1
        fi
    else
        print_success "On $FEATURE_BRANCH branch"
    fi
}

run_validation_tests() {
    print_header "Running Validation Tests"
    
    if [ ! -f "scripts/security/test_sarif_converters.py" ]; then
        print_error "Validation test script not found"
        exit 1
    fi
    
    if python3 scripts/security/test_sarif_converters.py; then
        print_success "All validation tests passed"
    else
        print_error "Validation tests failed"
        exit 1
    fi
}

check_git_status() {
    print_header "Checking Git Status"
    
    # Check for uncommitted changes
    if ! git diff-index --quiet HEAD --; then
        print_warning "You have uncommitted changes"
        git status --short
        read -p "Commit changes before pushing? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            read -p "Enter commit message: " COMMIT_MSG
            git add -A
            git commit -m "$COMMIT_MSG"
            print_success "Changes committed"
        else
            print_warning "Proceeding with uncommitted changes"
        fi
    else
        print_success "No uncommitted changes"
    fi
    
    # Show commit summary
    echo ""
    print_info "Recent commits:"
    git log --oneline -5
}

configure_git_auth() {
    print_header "Configuring Git Authentication"
    
    # Check current remote URL
    REMOTE_URL=$(git remote get-url origin)
    print_info "Current remote: $REMOTE_URL"
    
    if [[ $REMOTE_URL == git@github.com:* ]]; then
        print_success "Using SSH authentication"
        
        # Test SSH connection
        if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
            print_success "SSH authentication working"
        else
            print_warning "SSH authentication may not be configured"
            print_info "Visit: https://docs.github.com/en/authentication/connecting-to-github-with-ssh"
        fi
    elif [[ $REMOTE_URL == https://github.com/* ]]; then
        print_warning "Using HTTPS authentication"
        print_info "You will be prompted for username and Personal Access Token"
        print_info "Create PAT at: https://github.com/settings/tokens"
    else
        print_error "Unknown remote URL format"
        exit 1
    fi
}

push_to_github() {
    print_header "Pushing to GitHub"
    
    print_info "Pushing $FEATURE_BRANCH to origin..."
    
    if git push -u origin "$FEATURE_BRANCH"; then
        print_success "Successfully pushed to GitHub"
    else
        print_error "Failed to push to GitHub"
        print_info "Common issues:"
        print_info "  1. Authentication failed - check SSH key or PAT"
        print_info "  2. Network connectivity issues"
        print_info "  3. Repository permissions"
        exit 1
    fi
}

show_next_steps() {
    print_header "Next Steps"
    
    # Get GitHub username from remote URL
    REMOTE_URL=$(git remote get-url origin)
    if [[ $REMOTE_URL =~ github\.com[:/]([^/]+)/([^/.]+) ]]; then
        GITHUB_USER="${BASH_REMATCH[1]}"
        REPO_NAME="${BASH_REMATCH[2]}"
    fi
    
    echo ""
    print_info "1. Monitor CI/CD Pipeline:"
    echo "   https://github.com/$GITHUB_USER/$REPO_NAME/actions"
    
    echo ""
    print_info "2. Check Security Tab (after pipeline completes):"
    echo "   https://github.com/$GITHUB_USER/$REPO_NAME/security"
    
    echo ""
    print_info "3. Create Pull Request:"
    if command -v gh &> /dev/null; then
        echo "   gh pr create --title \"feat: Implement SARIF 2.1.0 support\" --base $BASE_BRANCH"
    else
        echo "   https://github.com/$GITHUB_USER/$REPO_NAME/compare/$BASE_BRANCH...$FEATURE_BRANCH"
    fi
    
    echo ""
    print_info "4. Review Deployment Guide:"
    echo "   docs/security/SARIF_DEPLOYMENT_GUIDE.md"
    
    echo ""
    if command -v gh &> /dev/null; then
        print_info "GitHub CLI detected. Would you like to:"
        echo "   a) Watch workflow execution"
        echo "   b) Create pull request now"
        echo "   c) Exit"
        read -p "Choose option (a/b/c): " -n 1 -r
        echo
        case $REPLY in
            a|A)
                print_info "Watching workflow execution..."
                gh run watch
                ;;
            b|B)
                print_info "Creating pull request..."
                gh pr create \
                    --title "feat: Implement comprehensive SARIF 2.1.0 support" \
                    --body "Implements SARIF converters for all security tools with GitHub Security tab integration." \
                    --base "$BASE_BRANCH" \
                    --head "$FEATURE_BRANCH"
                ;;
            *)
                print_success "Deployment complete!"
                ;;
        esac
    else
        print_success "Deployment complete!"
        print_info "Install GitHub CLI for easier workflow management: https://cli.github.com/"
    fi
}

# Main execution
main() {
    echo ""
    print_header "Krynox Nexus - SARIF Deployment"
    echo ""
    
    check_prerequisites
    echo ""
    
    run_validation_tests
    echo ""
    
    check_git_status
    echo ""
    
    configure_git_auth
    echo ""
    
    # Confirm before pushing
    print_warning "Ready to push $FEATURE_BRANCH to GitHub"
    read -p "Continue? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Deployment cancelled"
        exit 1
    fi
    
    push_to_github
    echo ""
    
    show_next_steps
    echo ""
}

# Run main function
main

# Made with Bob
