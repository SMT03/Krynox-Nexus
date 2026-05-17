# Krynox Nexus Makefile
# Zero-Trust Kernel Module Hardening and CI/CD Pipeline
#
# This Makefile provides convenient targets for building, testing,
# and security scanning of Linux kernel modules.

.PHONY: all build clean install test security-scan help docker-build docker-scan reports view-reports coverage view-coverage test-integration test-unit

# Project configuration
PROJECT_NAME := krynox-nexus
VERSION := 1.0.0
SRC_DIR := src
SCRIPTS_DIR := scripts
DOCKER_DIR := docker
REPORTS_DIR := reports

# Kernel configuration
KERNEL_VERSION := $(shell uname -r)
KERNEL_DIR := /lib/modules/$(KERNEL_VERSION)/build

# Compiler flags for security
EXTRA_CFLAGS := -Wall -Wextra -Werror
EXTRA_CFLAGS += -Wformat-security
EXTRA_CFLAGS += -Wstack-protector
EXTRA_CFLAGS += -fno-strict-overflow
EXTRA_CFLAGS += -fno-delete-null-pointer-checks
EXTRA_CFLAGS += -fstack-protector-strong

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Default target
all: help

# ============================================================================
# Build Targets
# ============================================================================

build: ## Build all kernel modules
	@echo "$(BLUE)Building kernel modules...$(NC)"
	@chmod +x $(SCRIPTS_DIR)/build/build_modules.sh
	@$(SCRIPTS_DIR)/build/build_modules.sh
	@echo "$(GREEN)✓ Build complete$(NC)"

modules: build ## Alias for build

clean: ## Clean build artifacts
	@echo "$(YELLOW)Cleaning build artifacts...$(NC)"
	@cd $(SRC_DIR) && make clean 2>/dev/null || true
	@find $(SRC_DIR) -name "*.o" -delete
	@find $(SRC_DIR) -name "*.ko" -delete
	@find $(SRC_DIR) -name "*.mod" -delete
	@find $(SRC_DIR) -name "*.mod.c" -delete
	@find $(SRC_DIR) -name ".*.cmd" -delete
	@find $(SRC_DIR) -name "modules.order" -delete
	@find $(SRC_DIR) -name "Module.symvers" -delete
	@rm -rf $(SRC_DIR)/.tmp_versions
	@rm -f build.log
	@echo "$(GREEN)✓ Clean complete$(NC)"

clean-test: ## Clean test artifacts and coverage data
	@echo "$(YELLOW)Cleaning test artifacts...$(NC)"
	@rm -f $(TEST_UNIT_DIR)/test_secure_modules
	@rm -f $(TEST_UNIT_DIR)/*.gcda $(TEST_UNIT_DIR)/*.gcno $(TEST_UNIT_DIR)/*.gcov
	@rm -f *.gcda *.gcno *.gcov
	@rm -rf $(COVERAGE_DIR)
	@echo "$(GREEN)✓ Test artifacts cleaned$(NC)"

clean-all: clean clean-test clean-reports ## Clean everything
	@echo "$(GREEN)✓ Complete cleanup done$(NC)"

install: build ## Install kernel modules (requires root)
	@echo "$(BLUE)Installing kernel modules...$(NC)"
	@if [ "$$(id -u)" -ne 0 ]; then \
		echo "$(RED)Error: Installation requires root privileges$(NC)"; \
		echo "$(YELLOW)Run: sudo make install$(NC)"; \
		exit 1; \
	fi
	@cd $(SRC_DIR) && make install
	@depmod -a
	@echo "$(GREEN)✓ Installation complete$(NC)"

# ============================================================================
# Security Scanning Targets
# ============================================================================

security-scan: static-analysis ibm-bob ## Run all security scans
	@echo "$(GREEN)✓ All security scans complete$(NC)"

static-analysis: ## Run static analysis (Clang, Cppcheck, Sparse)
	@echo "$(BLUE)Running static analysis...$(NC)"
	@chmod +x $(SCRIPTS_DIR)/security/run_static_analysis.sh
	@$(SCRIPTS_DIR)/security/run_static_analysis.sh || true
	@echo "$(GREEN)✓ Static analysis complete$(NC)"

ibm-bob: ## Run IBM Bob CLI analysis
	@echo "$(BLUE)Running IBM Bob analysis...$(NC)"
	@chmod +x $(SCRIPTS_DIR)/security/run_ibm_bob.sh
	@$(SCRIPTS_DIR)/security/run_ibm_bob.sh || true
	@echo "$(GREEN)✓ IBM Bob analysis complete$(NC)"

scan: security-scan ## Alias for security-scan

# ============================================================================
# Testing Targets
# ============================================================================

# ============================================================================
# Testing Configuration
# ============================================================================

TEST_DIR := tests
TEST_UNIT_DIR := $(TEST_DIR)/unit
TEST_CFLAGS := -Wall -Wextra -Werror -g -O0
TEST_CFLAGS += -fprofile-arcs -ftest-coverage  # gcov support
TEST_LDFLAGS := -lcmocka -lgcov
COVERAGE_DIR := coverage

test: test-unit ## Run all tests
	@echo "$(GREEN)✓ All tests complete$(NC)"

test-unit: $(TEST_UNIT_DIR)/test_secure_modules ## Run unit tests
	@echo "$(BLUE)Running unit tests...$(NC)"
	@./$(TEST_UNIT_DIR)/test_secure_modules
	@echo "$(GREEN)✓ Unit tests complete$(NC)"

$(TEST_UNIT_DIR)/test_secure_modules: $(TEST_UNIT_DIR)/test_secure_modules.c
	@echo "$(BLUE)Compiling unit tests...$(NC)"
	@$(CC) $(TEST_CFLAGS) -o $@ $< $(TEST_LDFLAGS)
	@echo "$(GREEN)✓ Unit tests compiled$(NC)"

test-integration: ## Run integration tests
	@echo "$(BLUE)Running integration tests...$(NC)"
	@if ! python3 -m pytest --version &> /dev/null; then \
		echo "$(RED)Error: pytest not found$(NC)"; \
		echo "$(YELLOW)Install with: pip3 install -r tests/integration/requirements.txt$(NC)"; \
		exit 1; \
	fi
	@python3 -m pytest tests/integration/test_pipeline.py -v --tb=short
	@echo "$(GREEN)✓ Integration tests complete$(NC)"

test-integration-verbose: ## Run integration tests with detailed output
	@echo "$(BLUE)Running integration tests (verbose)...$(NC)"
	@python3 -m pytest tests/integration/test_pipeline.py -vv --tb=long

test-integration-coverage: ## Run integration tests with coverage
	@echo "$(BLUE)Running integration tests with coverage...$(NC)"
	@python3 -m pytest tests/integration/test_pipeline.py -v --cov=scripts --cov-report=html --cov-report=term
	@echo "$(GREEN)✓ Coverage report: htmlcov/index.html$(NC)"

install-test-deps: ## Install integration test dependencies
	@echo "$(BLUE)Installing integration test dependencies...$(NC)"
	@pip3 install -r tests/integration/requirements.txt
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

coverage: test-unit ## Generate code coverage report
	@echo "$(BLUE)Generating coverage report...$(NC)"
	@if ! command -v lcov &> /dev/null; then \
		echo "$(RED)Error: lcov not found. Please install it (e.g., sudo dnf install lcov)$(NC)"; \
		exit 1; \
	fi
	@mkdir -p $(COVERAGE_DIR)
	@lcov --capture --directory $(TEST_UNIT_DIR) --output-file $(COVERAGE_DIR)/coverage.info
	@lcov --remove $(COVERAGE_DIR)/coverage.info '/usr/*' --output-file $(COVERAGE_DIR)/coverage.info 2>/dev/null || true
	@genhtml $(COVERAGE_DIR)/coverage.info --output-directory $(COVERAGE_DIR)
	@echo "$(GREEN)✓ Coverage report generated: $(COVERAGE_DIR)/index.html$(NC)"

view-coverage: coverage ## View coverage report in browser
	@echo "$(BLUE)Opening coverage report...$(NC)"
	@xdg-open $(COVERAGE_DIR)/index.html 2>/dev/null || \
		open $(COVERAGE_DIR)/index.html 2>/dev/null || \
		echo "$(YELLOW)Please open $(COVERAGE_DIR)/index.html manually$(NC)"

# ============================================================================
# Docker Targets
# ============================================================================

docker-build: ## Build Docker images
	@echo "$(BLUE)Building Docker images...$(NC)"
	@docker build -f $(DOCKER_DIR)/Dockerfile.scanner -t krynox-scanner:latest .
	@docker build -f $(DOCKER_DIR)/Dockerfile.builder -t krynox-builder:latest .
	@echo "$(GREEN)✓ Docker images built$(NC)"

docker-scan: ## Run security scan in Docker container
	@echo "$(BLUE)Running security scan in Docker...$(NC)"
	@docker-compose -f $(DOCKER_DIR)/docker-compose.yml up scanner
	@echo "$(GREEN)✓ Docker scan complete$(NC)"

docker-build-modules: ## Build modules in Docker container
	@echo "$(BLUE)Building modules in Docker...$(NC)"
	@docker-compose -f $(DOCKER_DIR)/docker-compose.yml up builder
	@echo "$(GREEN)✓ Docker build complete$(NC)"

docker-clean: ## Clean Docker containers and images
	@echo "$(YELLOW)Cleaning Docker resources...$(NC)"
	@docker-compose -f $(DOCKER_DIR)/docker-compose.yml down -v
	@docker rmi krynox-scanner:latest krynox-builder:latest 2>/dev/null || true
	@echo "$(GREEN)✓ Docker cleanup complete$(NC)"

# ============================================================================
# Setup Targets
# ============================================================================

setup: ## Install required security tools
	@echo "$(BLUE)Installing security tools...$(NC)"
	@chmod +x $(SCRIPTS_DIR)/setup/install_tools.sh
	@sudo $(SCRIPTS_DIR)/setup/install_tools.sh
	@echo "$(GREEN)✓ Setup complete$(NC)"

check-deps: ## Check if required tools are installed
	@echo "$(BLUE)Checking dependencies...$(NC)"
	@command -v gcc >/dev/null 2>&1 || echo "$(RED)✗ gcc not found$(NC)"
	@command -v clang >/dev/null 2>&1 || echo "$(RED)✗ clang not found$(NC)"
	@command -v cppcheck >/dev/null 2>&1 || echo "$(RED)✗ cppcheck not found$(NC)"
	@command -v sparse >/dev/null 2>&1 || echo "$(RED)✗ sparse not found$(NC)"
	@command -v docker >/dev/null 2>&1 || echo "$(RED)✗ docker not found$(NC)"
	@command -v node >/dev/null 2>&1 || echo "$(RED)✗ node not found$(NC)"
	@echo "$(GREEN)✓ Dependency check complete$(NC)"

# ============================================================================
# Report Targets
# ============================================================================

reports: ## Generate security reports
	@echo "$(BLUE)Generating reports...$(NC)"
	@mkdir -p $(REPORTS_DIR)
	@chmod +x $(SCRIPTS_DIR)/security/generate_dashboard.py
	@python3 $(SCRIPTS_DIR)/security/generate_dashboard.py
	@echo "$(GREEN)✓ Reports generated in $(REPORTS_DIR)$(NC)"

view-reports: ## View security reports in browser
	@echo "$(BLUE)Opening reports...$(NC)"
	@if [ -d "$(REPORTS_DIR)" ]; then \
		xdg-open $(REPORTS_DIR)/index.html 2>/dev/null || \
		open $(REPORTS_DIR)/index.html 2>/dev/null || \
		echo "$(YELLOW)Please open $(REPORTS_DIR)/index.html manually$(NC)"; \
	else \
		echo "$(RED)No reports found. Run 'make security-scan' first.$(NC)"; \
	fi

clean-reports: ## Clean security reports
	@echo "$(YELLOW)Cleaning reports...$(NC)"
	@rm -rf $(REPORTS_DIR)
	@echo "$(GREEN)✓ Reports cleaned$(NC)"

# ============================================================================
# Development Targets
# ============================================================================

format: ## Format source code
	@echo "$(BLUE)Formatting code...$(NC)"
	@find $(SRC_DIR) -name "*.c" -o -name "*.h" | xargs clang-format -i
	@echo "$(GREEN)✓ Code formatted$(NC)"

lint: ## Run linters
	@echo "$(BLUE)Running linters...$(NC)"
	@find $(SRC_DIR) -name "*.c" | xargs clang-tidy
	@echo "$(GREEN)✓ Linting complete$(NC)"

# ============================================================================
# CI/CD Targets
# ============================================================================

ci: clean build security-scan test ## Run full CI pipeline
	@echo "$(GREEN)✓ CI pipeline complete$(NC)"

ci-docker: docker-build docker-scan ## Run CI pipeline in Docker
	@echo "$(GREEN)✓ Docker CI pipeline complete$(NC)"

# ============================================================================
# Information Targets
# ============================================================================

info: ## Display project information
	@echo "$(BLUE)Krynox Nexus - Project Information$(NC)"
	@echo "Project: $(PROJECT_NAME)"
	@echo "Version: $(VERSION)"
	@echo "Kernel: $(KERNEL_VERSION)"
	@echo "Source: $(SRC_DIR)"
	@echo "Scripts: $(SCRIPTS_DIR)"
	@echo "Reports: $(REPORTS_DIR)"

version: ## Display version information
	@echo "$(PROJECT_NAME) v$(VERSION)"

# ============================================================================
# Help Target
# ============================================================================

help: ## Display this help message
	@echo "$(BLUE)Krynox Nexus - Zero-Trust Kernel Module Hardening$(NC)"
	@echo ""
	@echo "$(GREEN)Available targets:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(BLUE)Quick Start:$(NC)"
	@echo "  1. Install tools:    $(YELLOW)make setup$(NC)"
	@echo "  2. Build modules:    $(YELLOW)make build$(NC)"
	@echo "  3. Run security:     $(YELLOW)make security-scan$(NC)"
	@echo "  4. View reports:     $(YELLOW)make view-reports$(NC)"
	@echo ""
	@echo "$(BLUE)Docker Workflow:$(NC)"
	@echo "  1. Build images:     $(YELLOW)make docker-build$(NC)"
	@echo "  2. Run scan:         $(YELLOW)make docker-scan$(NC)"
	@echo ""
	@echo "For more information, see README.md"

.DEFAULT_GOAL := help

