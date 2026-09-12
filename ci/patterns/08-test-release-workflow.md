# 08 — Test release workflow (Test PyPI)

Publish packages to Test PyPI before committing to a production release.
Catches packaging, metadata, and dependency issues early without burning
a real version number on PyPI.

## Flow

```
1. Bump __version__ to a dev/pre-release version (e.g. 0.17.1.dev1)
2. Trigger Test Release workflow (workflow_dispatch)
3. Workflow: verify version → build → publish to Test PyPI
4. Install from Test PyPI and verify the package works
5. When satisfied, bump to the final version and use the production release workflow
```

## Full test-release.yml

```yaml
name: Test Release

on:
  workflow_dispatch:
    inputs:
      version:
        description: "Version to test-release (e.g. 0.17.1.dev1)"
        required: true
        type: string

jobs:
  build-publish:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Verify version matches package
        run: |
          PKG_VER=$(python -c "import re; m=re.search(r'__version__\s*=\s*\"(.+?)\"', open('src/PACKAGE_NAME/__init__.py').read()); print(m.group(1))")
          echo "Package version: $PKG_VER"
          echo "Requested version: ${{ inputs.version }}"
          [ "$PKG_VER" = "${{ inputs.version }}" ] || \
            (echo "::error::Version mismatch: __init__.py has $PKG_VER but release requested ${{ inputs.version }}"; exit 1)

      - name: Build wheel + sdist
        run: |
          pip install --upgrade pip build
          python -m build

      - name: Publish to Test PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          repository-url: https://test.pypi.org/legacy/

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/*
          retention-days: 7
```

## Setup: Test PyPI trusted publisher

Trusted publishing eliminates API tokens — GitHub Actions authenticates
directly with Test PyPI via OIDC.

### 1. Add a trusted publisher on Test PyPI

On [test.pypi.org](https://test.pypi.org), go to your project (or create a
"pending publisher" if first time) →
**Publishing → Add a new publisher**:

| Field              | Value                              |
|--------------------|------------------------------------|
| Owner              | your GitHub org or username         |
| Repository         | your repo name                     |
| Workflow name      | `test-release.yml`                 |
| Environment name   | (leave blank)                      |

Leave the environment name blank — no GitHub environment is needed.
The OIDC token from the workflow is sufficient for authentication.

### 2. Verify it works

```bash
gh workflow run test-release.yml -f version=0.1.0.dev1
```

## Dev version conventions

Use [PEP 440](https://peps.python.org/pep-0440/) dev/pre-release suffixes
so the test version sorts below the eventual release:

| Suffix       | Example         | Use case                          |
|--------------|-----------------|-----------------------------------|
| `.devN`      | `0.17.1.dev1`   | Development snapshot              |
| `.aN`        | `0.17.1a1`      | Alpha pre-release                 |
| `.bN`        | `0.17.1b1`      | Beta pre-release                  |
| `.rcN`       | `0.17.1rc1`     | Release candidate                 |

`.devN` is the most common choice for test-release workflows.

## Installing from Test PyPI

```bash
pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    your-package==0.17.1.dev1
```

`--extra-index-url` falls back to real PyPI for dependencies that aren't
on Test PyPI.

## Differences from production release (pattern 04)

| Aspect             | Test release              | Production release         |
|--------------------|---------------------------|----------------------------|
| Target index       | Test PyPI                 | PyPI                       |
| Git tag            | None                      | `v{version}`               |
| GitHub Release     | None                      | Created with artifacts     |
| Version format     | `X.Y.Z.devN`              | `X.Y.Z`                    |
| Quality gate       | None (manual trigger)     | lint+test before release   |

## Notes

- `permissions: id-token: write` is required for OIDC trusted publishing
- The workflow name in the Test PyPI trusted publisher config must match
  your actual workflow filename exactly — a mismatch causes a silent auth failure
- Test PyPI has lower rate limits and storage quotas than PyPI; don't push
  dozens of dev versions — clean up old ones periodically
- Replace `PACKAGE_NAME` in the template with your actual package import name
