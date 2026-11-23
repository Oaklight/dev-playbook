# 07 — Automated zerodep vendor updates

Projects that vendor [zerodep](https://github.com/Oaklight/zerodep) modules
into a `_vendor/` directory need a way to detect when upstream modules have
changed and pull in updates. This pattern adds a scheduled workflow that
checks for drift and auto-creates PRs.

## Why the guard exists

`zerodep update` used to treat any upstream content difference as `outdated`,
so a repository that vendored a post-release commit was "updated" down to the
latest release. ToolRegistry#481 hit this: `frontmatter` 0.3.1 → 0.3.0 and
`skills` 0.5.1 → 0.4.3. The CLI now reports `newer-than-upstream` and refuses
without `--force`. This workflow keeps the same guarantee even when CI
installs an older CLI.

## Prerequisites

- `zerodep` CLI ≥ 2026.10.23.1 (for `zerodep.lock.json` and `status --json`)
- `[tool.zerodep]` section in `pyproject.toml` declaring `vendor-dir`

The guard script in this pattern also protects runs that install an older
CLI which predates `newer-than-upstream`: it compares the locked and upstream
versions itself and never asks the CLI to update a module whose locked version
is higher.

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
[`templates/workflows/zerodep-update.yml`](../templates/workflows/zerodep-update.yml)
and the guard script at
[`templates/scripts/zerodep_guard.py`](../templates/scripts/zerodep_guard.py).

1. **Schedule**: runs weekly (Monday 03:17 UTC) and on manual `workflow_dispatch`.
2. **Inspect**: `zerodep status --json` runs for each vendored tree. The guard
   script classifies every row:
   - `outdated` / `missing` with a comparable, not-newer version → update
   - `newer-than-upstream`, or an `outdated` row whose locked version is
     higher → skipped, with the locked and upstream versions in the summary
   - `version-uncomparable` → skipped
   - `locally-modified`, `conflict`, `unverified`, `upstream-removed` → manual
   A row with the same version but a different content hash stays in the
   update set and is labelled "content differs at version X (hash changed,
   version unchanged)".

   Repositories that patch a module after every update set
   `ZERODEP_EXPECTED_LOCAL` to that module list. The script then moves those
   `locally-modified` rows out of the manual list and accepts them as the
   expected end state after patch re-application (ztrade uses this).
3. **Update**: the plan is applied one directory at a time with
   `zerodep update --no-deps <names...>`. Naming the modules and skipping
   dependency expansion means even a CLI that predates `newer-than-upstream`
   cannot pull a protected dependency down.
4. **Verify**: `zerodep status --json` runs again. The step fails when a
   target is not `up-to-date` or when any locked version decreased. Modules
   that were `missing` are exempt, because a reinstall records the upstream
   version.
5. **PR**: `peter-evans/create-pull-request` commits when at least one module
   is updatable and opens (or updates) a PR with the `dependencies` and
   `zerodep` labels. The step summary lists every skipped module and every
   version discrepancy, so a downgrade cannot disappear into a green run.

The workflow uses a fixed branch name (`zerodep-update`). If a PR from a
previous run is still open, `create-pull-request` updates the same PR
(branch content + PR body) rather than creating a duplicate.

## Deploying to a project

1. Add `[tool.zerodep] vendor-dir` to `pyproject.toml` (see above).
   **This is required** — without it, `zerodep status` scans CWD and
   will silently report nothing installed.
2. Copy `templates/workflows/zerodep-update.yml` to `.github/workflows/` and
   `templates/scripts/zerodep_guard.py` to `.github/scripts/`. If the vendor
   tree is not at the repository root, replace `.` in the Inspect step with
   that directory (or list several directories).
3. Ensure the repo has `dependencies` and `zerodep` labels (see
   [repo-setup](../../repo-setup/) for the label taxonomy).

No per-workflow customization is needed — the CLI reads the vendor
directory from `pyproject.toml`.

### CI checks on the auto-PR

PRs created by the default `GITHUB_TOKEN` do **not** trigger
`on: pull_request` workflows. If you need CI checks on the auto-PR,
configure `create-pull-request` to use a GitHub App token or PAT
instead. See the [create-pull-request docs](https://github.com/peter-evans/create-pull-request/blob/main/docs/concepts-guidelines.md#triggering-further-workflow-runs) for details.

## CLI flags for scripting

```bash
zerodep status --json            # {"modules": [...], "counts": {...}, "lock": bool}
zerodep update --no-deps a b     # update only the named modules
zerodep update --all --dry-run   # preview without writing
```

Every row carries `installed_version`, `latest_version`, and `state`. The
states that matter to CI are `outdated` (including a same-version content
change), `missing`, `newer-than-upstream`, and `version-uncomparable`.

`zerodep outdated --exit-code` is safe as a gate: it does not fail for
`newer-than-upstream` or `version-uncomparable`, because replacing those
needs `--force`. The template uses `status` instead, because it exposes the
version fields the guard compares.

## Handling renamed modules

If a module has been renamed upstream (e.g. `jsonc` → `jsonx`), `zerodep
outdated` reports it as `renamed → <new_name>`. The workflow PR will flag
this, but the rename requires manual intervention — update your import
paths, remove the old file, and `zerodep add <new_name>`.
