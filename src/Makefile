# Krynox Nexus Kernel Module Makefile
# This Makefile works with Kbuild to build kernel modules

# Kernel version and directory
KVERSION := $(shell uname -r)
KDIR := /lib/modules/$(KVERSION)/build
PWD := $(shell pwd)

# Default target
all: modules

# Build kernel modules
modules:
	$(MAKE) -C $(KDIR) M=$(PWD) modules

# Clean build artifacts
clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean
	rm -f *.o *.ko *.mod *.mod.c .*.cmd
	rm -f Module.symvers modules.order
	rm -rf .tmp_versions

# Install modules
install: modules
	$(MAKE) -C $(KDIR) M=$(PWD) modules_install
	depmod -a

# Help target
help:
	@echo "Krynox Nexus Kernel Module Build System"
	@echo ""
	@echo "Available targets:"
	@echo "  all      - Build all kernel modules (default)"
	@echo "  modules  - Build all kernel modules"
	@echo "  clean    - Remove build artifacts"
	@echo "  install  - Install modules to system (requires root)"
	@echo "  help     - Show this help message"
	@echo ""
	@echo "Modules to be built:"
	@echo "  Secure Examples:"
	@echo "    - examples/hello_secure.ko"
	@echo ""
	@echo "  Vulnerable (Testing Only):"
	@echo "    - vulnerable/buffer_overflow.ko"
	@echo "    - vulnerable/use_after_free.ko"
	@echo ""
	@echo "Note: Vulnerable modules contain intentional security flaws"
	@echo "      for testing purposes only. DO NOT use in production!"

.PHONY: all modules clean install help

# Made with Bob
