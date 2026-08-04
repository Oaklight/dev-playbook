# Pattern: Zensical + ReadTheDocs Setup

## Context

[Zensical](https://zensical.org/) is the successor to mkdocs-material, built
by the same team. mkdocs-material reaches EOL in November 2026. Zensical reads
`mkdocs.yml` natively but has its own template/module system — standard mkdocs
plugins don't work.

## ReadTheDocs Config

Zensical projects on ReadTheDocs use custom build jobs since ReadTheDocs
doesn't have native Zensical support yet:

```yaml
# .readthedocs.yaml
version: 2

build:
  os: ubuntu-24.04
  tools:
    python: "3.11"
  jobs:
    pre_build:
      # Clone source for mkdocstrings API docs
      - git clone https://github.com/USER/REPO.git src_repo
      - mkdir -p src
      - cp -r src_repo/src/PACKAGE src/
      - rm -rf src_repo
    install:
      - pip install -r requirements.txt
    build:
      html:
        - zensical build
        - python scripts/generate_llmstxt.py -c mkdocs.yml -s site -d docs -v
    post_build:
      - mkdir -p $READTHEDOCS_OUTPUT/html/
      - cp --recursive site/* $READTHEDOCS_OUTPUT/html/
```

## Requirements.txt

```
zensical
mkdocstrings[python]>=0.24.0
pymdown-extensions>=10.0.0
pyyaml
```

## Known Limitations

- **No mkdocs plugin support**: Zensical has its own module system (not yet
  open to third-party). Use post-build scripts for functionality that would
  normally come from plugins.
- **Partial template overrides**: Only some `overrides/partials/*.html` files
  are respected (e.g. `alternate.html` works, `actions.html` doesn't).
  Use HTML injection for reliable cross-builder customization.
- **`extra_javascript` / `extra_css`**: Not processed by Zensical. Inject
  via post-build scripts instead.

## Bilingual Docs

For projects with `docs_en/` and `docs_zh/` on orphan branches:

- Each worktree has its own `mkdocs.yml`, `.readthedocs.yaml`, `Makefile`
- ReadTheDocs projects: one for `/en/`, one for `/zh-cn/`
- Always update both languages in the same task
