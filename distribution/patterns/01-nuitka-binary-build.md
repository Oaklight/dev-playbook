# 01 — Nuitka binary build

## Why Nuitka?

Python CLI tools ship as wheels that require a Python runtime. For server
deployment and Docker images this means:

- ~150 MB base image (`python:3.12-slim`)
- Pip install + dependency resolution at build time
- Virtual environment management on the host

Nuitka compiles Python into a standalone C binary. The result:

- **Single ~20–40 MB binary**, no Python needed at runtime
- **Alpine Docker image: ~21 MB** (musl binary + Alpine base)
- **BusyBox glibc image: ~25 MB** (native binary + busybox:glibc base)
- Zero dependency install — just copy the binary

## Architecture

```
Makefile targets           CI workflow                 Docker images
─────────────────          ─────────────               ─────────────
build-binary        ←──    build job (native)    ──→   busybox:glibc
build-binary-musl   ←──    build-musl job        ──→   alpine
```

Three layers, each independently useful:

1. **Makefile**: `build-binary` (native glibc/macOS/Windows) and
   `build-binary-musl` (Alpine container build). These work locally.
2. **CI workflow**: matrix over platforms, calls `make build-binary` /
   `make build-binary-musl`, uploads artifacts.
3. **Docker images**: `Dockerfile.binary` takes a pre-built binary, copies it
   into a minimal base. No Python, no pip.

## Platform matrix

| Platform | Runner | Linker | Build target |
|----------|--------|--------|-------------|
| `linux-x86_64` | `ubuntu-latest` | glibc | `build-binary` |
| `linux-arm64` | `ubuntu-24.04-arm` | glibc | `build-binary` |
| `linux-x86_64-musl` | `ubuntu-latest` | musl | `build-binary-musl` |
| `linux-arm64-musl` | `ubuntu-24.04-arm` | musl | `build-binary-musl` |
| `macos-arm64` | `macos-latest` | system | `build-binary` |
| `windows-x86_64` | `windows-latest` | MSVC | `build-binary` |

## Adapting for a new project

When copying the templates, replace these project-specific values:

### Makefile

| Placeholder | Example (llm-rosetta) | What to change |
|-------------|----------------------|----------------|
| `BINARY_NAME` prefix | `llm-rosetta-gateway` | Your CLI name from `[project.scripts]` |
| `--include-package=` | `llm_rosetta` | Your top-level Python package |
| `--include-data-files/dir` | admin HTML/CSS/JS, shim providers | Your bundled assets (static files, specs, templates) |
| Entry point import | `from llm_rosetta.gateway import main` | Your `[project.scripts]` target |
| `pip install -e ".[extra]"` | `.[profiling]` | Your optional extras needed at build time (or just `.`) |

### CI workflow

| Placeholder | What to change |
|-------------|----------------|
| Version grep path | `src/<package>/__init__.py` |
| `pip install` extras | Match your build-time dependencies |
| Artifact name prefix | Match your binary name |
| Smoke test command | `--help`, `--version`, or whatever validates the binary |

### Dockerfile.binary

| Placeholder | What to change |
|-------------|----------------|
| Binary install path | `/usr/local/bin/<your-binary>` |
| `EXPOSE` port | Your service port (or remove for CLI-only tools) |
| `CMD` | Your default command |

### entrypoint-binary.sh

| Placeholder | What to change |
|-------------|----------------|
| Binary path | `/usr/local/bin/<your-binary>` |
| First-run init logic | Config generation, or remove if not needed |

## Key Nuitka flags

```
--standalone --onefile    # Single self-extracting binary
--jobs=$(nproc)           # Parallel compilation
--include-package=X       # Ensure package is fully included
--include-data-files=...  # Bundle non-Python files (HTML, JSON, etc.)
--include-data-dir=...    # Bundle entire directories
--nofollow-import-to=X    # Exclude dev-only packages (pytest, setuptools)
--assume-yes-for-downloads  # Auto-download helper tools (e.g. ccache)
```

## Data file bundling

This is the most project-specific part. Nuitka doesn't automatically include
non-Python files. You must explicitly declare them:

```makefile
# Single file
--include-data-files=src/pkg/template.html=pkg/template.html

# Entire directory
--include-data-dir=src/pkg/static=pkg/static
```

The format is `<source-path>=<target-path-inside-binary>`. The target path
should match the package structure so `importlib.resources` / `__file__`-based
lookups work at runtime.

## Musl builds

The `build-binary-musl` target runs inside a `python:3.12-alpine` Docker
container. This produces a statically-linked musl binary that runs on any
musl-based system (Alpine, distroless, scratch+musl).

The container build:
1. Copies the workspace (excluding `.git`) into a temp dir
2. Installs build deps (`gcc`, `musl-dev`, `python3-dev`, `patchelf`)
3. Installs the package + Nuitka
4. Compiles inside the container
5. Outputs the binary to the host's `build/` dir via volume mount

## Smoke testing

Always smoke-test the binary before uploading:

- **Native**: `./build/<binary> --help`
- **Musl**: `docker run --rm -v ./build:/b:ro alpine /b/<binary> --help`
- **Windows**: `for %%f in (build\<binary>*) do %%f --help`

The `--help` test verifies the binary starts, loads all bundled modules, and
can parse arguments. For richer validation, test a core command (e.g.,
`--version`, `--list`).

## Integration with release workflow

The Nuitka workflow supports `workflow_call`, so your release workflow can
call it:

```yaml
jobs:
  build-binaries:
    uses: ./.github/workflows/nuitka.yml
    with:
      ref: ${{ github.ref }}
```

Then download the artifacts in subsequent jobs to attach them to the GitHub
Release or build Docker images.

## Existing implementations

| Project | Binary name | Notes |
|---------|------------|-------|
| [llm-rosetta](https://github.com/Oaklight/llm-rosetta) | `llm-rosetta-gateway` | Gateway server, bundles admin UI + shim configs |
| [llm-comply](https://github.com/Oaklight/llm-comply) | `llm-comply` | CLI + web mode, bundles JSON specs + web.html |
