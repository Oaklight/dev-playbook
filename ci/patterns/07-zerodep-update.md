# 07 — Automated zerodep vendor updates

Projects that vendor [zerodep](https://github.com/Oaklight/zerodep) modules
into a `_vendor/` directory need a way to detect when upstream modules have
changed and pull in updates. This pattern adds a scheduled workflow that
checks for drift and auto-creates PRs.

## Prerequisites

- `zerodep` CLI ≥ 2026.9.8 (with `--json`, `--exit-code`, `update --all`)
- `[tool.zerodep]` section in `pyproject.toml` declaring `vendor-dir`

## Project configuration

Add the vendor directory to `pyproject.toml` so the CLI can find it
without a `-d` flag:

```toml
[tool.zerodep]
vendor-dir = "src/mypackage/_vendor"
```

Example values for our projects:

| Project | vendor-dir |
|---------|-----------|
| toolregistry | `src/toolregistry/_vendor` |
| toolregistry-hub | `src/toolregistry_hub/_vendor` |
| argo-proxy | `src/argoproxy/_vendor` |

## How it works

The workflow template is at
[`templates/workflows/zerodep-update.yml`](../templates/workflows/zerodep-update.yml).

1. **Schedule**: runs weekly (Monday 03:17 UTC) and on manual `workflow_dispatch`.
2. **Check**: `zerodep outdated --json` returns a JSON object with each
   vendored module's local version, latest version, and status. The step
   parses `outdated_count` to decide whether to proceed.
3. **Update**: `zerodep update --all` fetches and overwrites all outdated
   modules in the configured `vendor-dir`.
4. **PR**: `peter-evans/create-pull-request` commits the changes and opens
   (or updates) a PR with the `dependencies` and `zerodep` labels.

The workflow uses a fixed branch name (`zerodep-update`). If a PR from a
previous run is still open, `create-pull-request` updates the same PR
(branch content + PR body) rather than creating a duplicate.

## Deploying to a project

1. Add `[tool.zerodep] vendor-dir` to `pyproject.toml` (see above).
2. Copy `templates/workflows/zerodep-update.yml` to `.github/workflows/`.
3. Ensure the repo has `dependencies` and `zerodep` labels (see
   [repo-setup](../../repo-setup/) for the label taxonomy).

No per-workflow customization is needed — the CLI reads the vendor
directory from `pyproject.toml`.

## CLI flags for scripting

These flags were added specifically for CI use:

```bash
zerodep outdated --json        # {"modules": [...], "outdated_count": N}
zerodep outdated --exit-code   # exit 1 if any module is outdated
zerodep update --all           # update all outdated modules at once
```

`--json` and `--exit-code` can be combined. The `--exit-code` flag
follows the same convention as `git diff --exit-code`.

## Handling renamed modules

If a module has been renamed upstream (e.g. `jsonc` → `jsonx`), `zerodep
outdated` reports it as `renamed → <new_name>`. The workflow PR will flag
this, but the rename requires manual intervention — update your import
paths, remove the old file, and `zerodep add <new_name>`.
