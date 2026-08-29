# dev-playbook

Documented patterns, templates, and conventions I use across my projects.
Battle-tested across 10+ repos.

## Sections

| Section | Description |
|---------|-------------|
| [ci/](ci/) | CI/CD — pre-commit, GitHub Actions workflows, CalVer releases |
| [docs/](docs/) | Documentation — Zensical/ReadTheDocs setup, llms.txt generation |
| [distribution/](distribution/) | Distribution — Nuitka binary builds, minimal Docker images |
| packaging/ | *(planned)* pyproject.toml templates, version management |
| docker/ | *(planned)* Dockerfile templates, multi-arch builds, mirror variables |
| [repo-setup/](repo-setup/) | Repo initialization — GitHub labels, .gitignore, LICENSE |

## Philosophy

- Patterns are documented decisions — *why* this approach, not just *how*
- Templates are ready-to-copy files, not abstract generators
- Each section is self-contained with its own README
- Consolidates knowledge that was previously scattered across `~/.config/agent-rules/`

## History

This repo consolidates and supersedes
[ci-playbook](https://github.com/Oaklight/ci-playbook) (archived).
