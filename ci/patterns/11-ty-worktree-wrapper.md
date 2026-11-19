# 11 — Run `ty` from a git worktree

`ty` resolves imports through the active Python environment. When that
environment holds an editable install of the project from **another
checkout** (the usual case: you installed from the main checkout, then work in
a `git worktree`), `ty` type-checks the worktree's tests against the other
checkout's sources. A symbol that exists only in the worktree is reported as
missing, and the result differs from CI, where the editable install points at
the checkout under test.

## Reproduce

```bash
# checkout A: packages/foo/src/foo, tests/, editable install of A
uv venv venv && uv pip install -e A/packages/foo ty
git -C A worktree add ../B -b feat
# in B: add `def new()` to foo, and a test that calls `foo.new()`
cd B && ty check
# error[unresolved-attribute]: Module `foo` has no member `new`
```

`ty` was 0.0.54 in this run. The error disappears when B's `src` directory is
searched first.

## Fix A: static config (when the layout is fixed)

If the repository has one or a few known source roots, declare them. ty
resolves the paths from the project root, so every worktree gets its own:

```toml
[tool.ty.environment]
extra-paths = ["packages/foo/src"]
```

In the reproduction above this alone makes the worktree check pass. Prefer it
when it is enough.

## Fix B: the wrapper (when roots are discovered or the environment varies)

[`templates/scripts/dev/run_ty.py`](../templates/scripts/dev/run_ty.py) runs
`ty check` with this checkout's source roots on `--extra-search-path` and the
active environment on `--python`. Extra arguments go to `ty check`; the exit
status is `ty`'s.

- **Source roots** are discovered: every directory named `src` up to three
  levels below the repository root that holds a Python package or module
  (`src`, `packages/*/src`, ...). Hidden directories, virtual environments,
  `node_modules`, `build` and `dist` are skipped. Set `RUN_TY_SEARCH_PATHS` to a
  `os.pathsep`-separated list (relative to the repository root) to replace the
  discovery.
- **Environment**: `$VIRTUAL_ENV`, then `$CONDA_PREFIX`, then the wrapper's own
  `sys.prefix`. It warns when none of the first two is set.
- **Repository root**: the nearest ancestor with `.git` (a file in a worktree),
  else the nearest with `pyproject.toml`. The wrapper runs `ty` from there, so
  it behaves the same from any subdirectory.
- With no `src` directory found it still runs `ty check --python <env>` and
  says so.

| File | Copy to |
|------|---------|
| [`templates/scripts/dev/run_ty.py`](../templates/scripts/dev/run_ty.py) | `scripts/dev/run_ty.py` |
| [`templates/tests/test_run_ty.py`](../templates/tests/test_run_ty.py) | `tests/test_run_ty.py` |

The tests do not run `ty`; they stub the subprocess call. The test file
resolves the script as `<repo>/scripts/dev/run_ty.py`.

In the same reproduction, `python scripts/dev/run_ty.py` passes from the
repository root and from `tests/`.

### Pre-commit hook

Point the local `ty` hook at the wrapper so a commit made in any worktree gives
the CI result (see [01 — Pre-commit setup](01-pre-commit-setup.md)):

```yaml
      - id: ty
        name: ty check
        entry: python scripts/dev/run_ty.py
        language: system
        pass_filenames: false
        require_serial: true
        types: [python]
```

## When you do not need either

Repositories with a root-level `src/` layout may not show the problem. In
Oaklight/toolregistry-server and Oaklight/toolregistry-hub, `ty check src/` run
in a worktree resolved the worktree's own package even though the editable
install pointed at another checkout (checked with a deliberately mistyped call
into a new function; both repositories pass), so neither needs a wrapper.
`ty` appears (inference, not checked in its source) to add the project's
`src` directory to its first-party search path. The reproduced failing case is
a nested layout such as `packages/*/src`, where no `src` sits at the repository
root.

Source: Oaklight/llm-rosetta#1622.
