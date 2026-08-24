# repo-setup

Patterns and templates for initializing and configuring GitHub repositories.

## Patterns

| Pattern | Description |
|---------|-------------|
| [01 — GitHub label taxonomy](patterns/01-github-labels.md) | Standardized label system across all repos |

## Templates

```
templates/
└── labels-base.yml    # Base label config (type + priority)
```

## Tools

| Script | Description |
|--------|-------------|
| [`sync-labels.sh`](sync-labels.sh) | Create/update/delete GitHub labels from a YAML config |
