# Distribution

Patterns for distributing Python applications as standalone binaries and
minimal Docker images, eliminating the need for a Python runtime at deploy
time.

## Patterns

| Pattern | Description |
|---------|-------------|
| [01-nuitka-binary-build](patterns/01-nuitka-binary-build.md) | Compile Python CLI into a single binary via Nuitka, build minimal Docker images |

## Templates

| Template | Description |
|----------|-------------|
| [nuitka.yml](templates/workflows/nuitka.yml) | GitHub Actions workflow for multi-platform Nuitka builds |
| [Makefile.nuitka.mk](templates/Makefile.nuitka.mk) | Makefile snippet with binary build targets |
| [Dockerfile.binary](templates/Dockerfile.binary) | Minimal binary-only Docker image (~5–25 MB) |
| [entrypoint-binary.sh](templates/entrypoint-binary.sh) | Container entrypoint for binary images |
