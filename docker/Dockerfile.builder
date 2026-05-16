# Krynox Nexus Kernel Module Builder Container
# 
# This Docker image provides a complete kernel module build environment
# with security-enhanced compiler flags and debugging tools.
#
# Part of Krynox Nexus - Zero-Trust Kernel Module Hardening

FROM ubuntu:22.04

LABEL maintainer="Krynox Nexus Security Team"
LABEL description="Kernel module build environment with security hardening"
LABEL version="1.0.0"

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Install kernel build dependencies
RUN apt-get update && apt-get install -y \
    # Build tools
    build-essential \
    gcc \
    g++ \
    make \
    cmake \
    git \
    # Kernel development
    linux-headers-generic \
    linux-source \
    kmod \
    libelf-dev \
    libssl-dev \
    bc \
    bison \
    flex \
    # Debugging tools
    gdb \
    strace \
    ltrace \
    # Additional utilities
    vim \
    nano \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set up security-enhanced compiler flags
ENV KCFLAGS="-Wall -Wextra -Werror -Wformat-security -Wstack-protector -fno-strict-overflow -fno-delete-null-pointer-checks -fstack-protector-strong"
ENV CFLAGS="-O2 -D_FORTIFY_SOURCE=2 -fPIE -fstack-protector-strong"
ENV LDFLAGS="-Wl,-z,relro,-z,now"

# Create build directory
WORKDIR /build

# Copy build scripts
COPY scripts/build/ /usr/local/bin/build-scripts/
RUN chmod +x /usr/local/bin/build-scripts/*.sh

# Set up environment
ENV PATH="/usr/local/bin/build-scripts:${PATH}"

# Create output directories
RUN mkdir -p /build/output /build/reports

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD gcc --version && make --version || exit 1

# Default command
CMD ["/bin/bash"]

# Usage:
# docker build -f docker/Dockerfile.builder -t krynox-builder:latest .
# docker run -v $(pwd):/build krynox-builder:latest make -C src

# Made with Bob
