# Documentation Patterns

Patterns and templates for building documentation sites with Zensical
(mkdocs-material successor) and ReadTheDocs.

## Patterns

| Pattern | Description |
|---------|-------------|
| [01 — llms.txt generation](patterns/01-llmstxt-generation.md) | Auto-generate llms.txt from mkdocs.yml nav — no manual sections to maintain |
| [02 — Zensical + ReadTheDocs](patterns/02-zensical-readthedocs.md) | Build config, known limitations, bilingual setup |

## Templates

| Template | Description |
|----------|-------------|
| [`generate_llmstxt.py`](templates/generate_llmstxt.py) | Post-build script for llms.txt, llms-full.txt, per-page .md, and link buttons |
