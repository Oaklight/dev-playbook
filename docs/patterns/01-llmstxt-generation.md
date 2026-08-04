# Pattern: llms.txt Generation from Nav

## Problem

The [llms.txt](https://llmstxt.org/) spec provides LLM-friendly documentation
indices. Existing mkdocs plugins (`mkdocs-llmstxt`, `mkdocs-llms-source`) require
manual `sections` config that drifts from `nav`, or don't work with Zensical
(the mkdocs-material successor).

## Solution

A standalone Python script (`generate_llmstxt.py`) that:

1. Parses `mkdocs.yml` nav structure
2. Generates `llms.txt` (index) and `llms-full.txt` (all content)
3. Copies `.md` source files to site output
4. Injects per-page link buttons into built HTML

Runs as a post-build step after `zensical build` or `mkdocs build`.

## Usage

```bash
# After site build
python scripts/generate_llmstxt.py -c mkdocs.yml -s site -d docs -v
```

### Integration with Makefile

```makefile
html: clean
	@$(ZENSICAL) build
	@python scripts/generate_llmstxt.py -c mkdocs.yml -s $(BUILDDIR) -d $(SOURCEDIR) -v
```

### Integration with ReadTheDocs

```yaml
# .readthedocs.yaml
build:
  jobs:
    build:
      html:
        - zensical build
        - python scripts/generate_llmstxt.py -c mkdocs.yml -s site -d docs -v
```

## How It Works

### Nav → Sections

Top-level nav keys become `## Section` headers in `llms.txt`. Nested entries
are flattened into their parent section. Bare path entries (e.g.
`- examples/index.md`) get their title extracted from the file's H1 heading.

### HTML Injection

The script injects a `<script>` tag into every built HTML page's `<head>`.
The script adds two icon buttons at the top of each article:

- **Markdown icon** — links to the per-page `.md` source
- **Robot icon** — links to `llms.txt`

This approach works with both mkdocs and Zensical, since it's a post-build
text replacement that doesn't depend on any template system.

## Requirements

- `pyyaml` (already a dependency of mkdocs/zensical)
- No other dependencies

## Template

See [`templates/generate_llmstxt.py`](../templates/generate_llmstxt.py).
