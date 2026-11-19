# repo-setup

Patterns and templates for initializing and configuring GitHub repositories.

## Patterns

| Pattern | Description |
|---------|-------------|
| [01 — GitHub label taxonomy](patterns/01-github-labels.md) | Standardized label system across all repos |
| [02 — Pull request workflow](patterns/02-pr-workflow.md) | Risk-tiered review, series rule, small PRs, PR template, overlap check |

## Templates

```
templates/
├── labels-base.yml                  # Base label config (type + priority)
├── pull_request_template.md         # PR template (copy to .github/)
├── scripts/dev/pr_overlap.py        # Warn when open PRs touch the same files
└── tests/test_pr_overlap.py
```

## Tools

| Script | Description |
|--------|-------------|
| [`sync-labels.sh`](sync-labels.sh) | Create/update/delete GitHub labels from a YAML config |
