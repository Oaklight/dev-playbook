# ──────────────────────────────────────────────
# Nuitka binary builds
# ──────────────────────────────────────────────
#
# Copy this into your project Makefile and adapt:
#   1. BINARY_PREFIX — your CLI binary name
#   2. NUITKA_ENTRY_IMPORT — the import path for main()
#   3. NUITKA_FLAGS — package includes and data files
#   4. DOCKER_IMAGE — your Docker Hub image name
#   5. build-binary-musl — pip install extras and nuitka flags
#
# Prerequisites (already in your Makefile):
#   VERSION — extracted from __init__.py
#   REGISTRY_MIRROR — optional Docker registry mirror

# ── Placeholder: set your binary name ──
BINARY_PREFIX := my-tool
NUITKA_ENTRY_IMPORT := from my_package.cli import main

# ── Platform detection ──
UNAME_S := $(shell uname -s 2>/dev/null || echo Windows)
UNAME_M := $(shell uname -m 2>/dev/null || echo x86_64)
ifeq ($(UNAME_S),Linux)
  BINARY_OS := linux
else ifeq ($(UNAME_S),Darwin)
  BINARY_OS := macos
else
  BINARY_OS := windows
endif
ifeq ($(UNAME_M),aarch64)
  BINARY_ARCH := arm64
else ifeq ($(UNAME_M),arm64)
  BINARY_ARCH := arm64
else
  BINARY_ARCH := x86_64
endif

BINARY_NAME = $(BINARY_PREFIX)-$(VERSION)-$(BINARY_OS)-$(BINARY_ARCH)
BINARY_NAME_MUSL = $(BINARY_PREFIX)-$(VERSION)-linux-$(BINARY_ARCH)-musl
BINARY_DIR := build
NUITKA_ENTRY := _nuitka_entry.py
NUITKA_JOBS := $(shell nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 2)

# ── Placeholder: adapt flags for your project ──
NUITKA_FLAGS = \
	--standalone \
	--onefile \
	--jobs=$(NUITKA_JOBS) \
	--output-dir=$(BINARY_DIR) \
	--include-package=my_package \
	--nofollow-import-to=pytest \
	--nofollow-import-to=setuptools \
	--nofollow-import-to=pip \
	--nofollow-import-to=_pytest \
	--assume-yes-for-downloads
# Add data files as needed:
#	--include-data-files=src/pkg/template.html=pkg/template.html \
#	--include-data-dir=src/pkg/static=pkg/static

# Build native binary (glibc on Linux, system libc on macOS, MSVC on Windows)
build-binary:
	@echo "Building native binary: $(BINARY_NAME)..."
	@printf '$(NUITKA_ENTRY_IMPORT)\nmain()\n' > $(NUITKA_ENTRY)
	python -m nuitka $(NUITKA_FLAGS) \
		--output-filename=$(BINARY_NAME)$(if $(filter windows,$(BINARY_OS)),.exe,) \
		$(NUITKA_ENTRY); \
	ret=$$?; rm -f $(NUITKA_ENTRY); exit $$ret
	@ls -lh $(BINARY_DIR)/$(BINARY_NAME)*
	@echo "Binary build complete."

# Build musl-linked binary via Alpine Docker container (Linux only)
# ── Placeholder: adapt pip install and nuitka flags inside the container ──
build-binary-musl:
	@echo "Building musl binary: $(BINARY_NAME_MUSL)..."
	@mkdir -p $(BINARY_DIR)
	docker run --rm \
		-v $(CURDIR):/workspace:ro \
		-v $(CURDIR)/$(BINARY_DIR):/output \
		$$([ -n "$(REGISTRY_MIRROR)" ] && echo "$(REGISTRY_MIRROR)/")python:3.12-alpine \
		/bin/sh -c '\
			mkdir -p /tmp/build && tar -cf - -C /workspace --exclude=.git --exclude=__pycache__ . | tar -xf - -C /tmp/build && cd /tmp/build && \
			apk add --no-cache gcc musl-dev python3-dev git >/dev/null && \
			pip install --break-system-packages patchelf -q && \
			pip install --break-system-packages -e . -q && \
			pip install --break-system-packages "nuitka[onefile]" ordered-set -q && \
			printf "$(NUITKA_ENTRY_IMPORT)\nmain()\n" > /tmp/_entry.py && \
			python -m nuitka \
				--standalone --onefile \
				--jobs=$$(nproc) \
				--output-dir=/output \
				--output-filename=$(BINARY_NAME_MUSL) \
				--include-package=my_package \
				--nofollow-import-to=pytest \
				--nofollow-import-to=setuptools \
				--nofollow-import-to=pip \
				--nofollow-import-to=_pytest \
				--assume-yes-for-downloads \
				/tmp/_entry.py && \
			rm -rf /output/_entry.* '
	@ls -lh $(BINARY_DIR)/$(BINARY_NAME_MUSL)
	@echo "Musl binary build complete."

clean-binary:
	@echo "Cleaning binary build artifacts..."
	rm -rf $(BINARY_DIR)/_nuitka_entry.* $(BINARY_DIR)/_entry.* $(NUITKA_ENTRY)
	@echo "Clean complete. Binaries in $(BINARY_DIR)/ preserved."

clean-binary-all:
	@echo "Cleaning all binary artifacts..."
	rm -rf $(BINARY_DIR)
	rm -f $(NUITKA_ENTRY)
	@echo "Clean complete."

# ── Docker images from pre-built binaries ──

# ── Placeholder: change DOCKER_IMAGE ──
# DOCKER_IMAGE := oaklight/my-tool

build-docker-alpine:
	@BINARY=$(BINARY_DIR)/$(BINARY_NAME_MUSL); \
	if [ ! -f "$$BINARY" ]; then \
		echo "::error::Musl binary not found: $$BINARY"; \
		echo "Run 'make build-binary-musl' first."; \
		exit 1; \
	fi; \
	echo "Building Alpine Docker image $(DOCKER_IMAGE):$(V)-alpine..."; \
	docker build -f docker/Dockerfile.binary \
		--build-arg BASE_IMAGE=$$([ -n "$(REGISTRY_MIRROR)" ] && echo "$(REGISTRY_MIRROR)/")alpine \
		--build-arg BINARY=$$BINARY \
		-t $(DOCKER_IMAGE):$(V)-alpine \
		-t $(DOCKER_IMAGE):$(V) \
		-t $(DOCKER_IMAGE):latest .
	@echo "Alpine Docker image built successfully."

build-docker-glibc:
	@BINARY=$(BINARY_DIR)/$(BINARY_NAME); \
	if [ ! -f "$$BINARY" ]; then \
		echo "::error::Native binary not found: $$BINARY"; \
		echo "Run 'make build-binary' first."; \
		exit 1; \
	fi; \
	echo "Building glibc Docker image $(DOCKER_IMAGE):$(V)-glibc..."; \
	docker build -f docker/Dockerfile.binary \
		--build-arg BASE_IMAGE=$$([ -n "$(REGISTRY_MIRROR)" ] && echo "$(REGISTRY_MIRROR)/")busybox:glibc \
		--build-arg BINARY=$$BINARY \
		-t $(DOCKER_IMAGE):$(V)-glibc .
	@echo "Glibc Docker image built successfully."
