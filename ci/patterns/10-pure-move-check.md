# 10 — Pure-move check for refactor PRs

A refactor that only moves code (splitting a module, relocating methods into
mixins) should change no definition. A reviewer cannot see a dropped
`@classmethod` or a lost module-level `logger` in a large move, so a tool
compares the two sides by AST and a CI job runs it on refactor PRs.

The tool is stdlib-only and works on any Python repository.

## Files

| File | Copy to |
|------|---------|
| [`templates/scripts/dev/check_move.py`](../templates/scripts/dev/check_move.py) | `scripts/dev/check_move.py` |
| [`templates/tests/test_check_move.py`](../templates/tests/test_check_move.py) | `tests/test_check_move.py` |
| [`templates/workflows/pure-move.yml`](../templates/workflows/pure-move.yml) | `.github/workflows/pure-move.yml` |

The test file resolves the script as `<repo>/scripts/dev/check_move.py`, so
keep that relative layout. It builds tiny temporary git repos and needs `git`
and `pytest` only.

## Usage

```bash
python scripts/dev/check_move.py origin/main              # head defaults to HEAD
python scripts/dev/check_move.py origin/main --markdown   # paste into the PR body
```

For every `.py` file that differs between the merge base and the head (any
path containing a `_vendor/` directory is skipped), the tool collects each
function, method, class and class-level or module-level assignment, keyed by
qualified name (`Class.method`). A def is compared as a whole: decorators,
arguments, annotations, body and docstring count. Comments and formatting do
not, because the AST does not carry them. The base side is the merge base, so
commits that landed on the base branch after the head branched do not show up
as removals.

| Category | Meaning | Fails |
|----------|---------|-------|
| `unchanged`, `moved-identical` | Same def, same or another file or class | no |
| `moved-with-diff` | The pair exists but the AST differs | yes |
| `missing` | In the base, not in the head | yes |
| `added` | In the head only (new glue code is normal) | no |
| `type-checking` | Added inside `if TYPE_CHECKING:` | no |
| `import-hoisted` | A function-local import became a module-level import of the same name | no |
| `logger-name` | `getLogger(__name__)` became `getLogger("<old module name>")` | no |
| `undefined-global` | A moved function reads a module-level name its new module does not define (a lost `logger` or constant), found with `symtable` | yes |
| `decorator-census` | The count of `@staticmethod`, `@classmethod` or `@property` differs over the changed files | yes |

A class is compared by its decorators, keywords and docstring only, because a
split into mixins changes its bases.

Exit status: 0 clean, 1 a failing category is not allowed, 2 usage or parse
error.

### Accepting an intended difference

List it in a file of `qualified.name  reason` lines (`#` starts a comment) and
pass it with `--allow FILE`. Use `undefined-global:<name>` or
`decorator-census:<decorator>` for those two checks. The CI template reads
`.github/pure-move-allow.txt` when the file exists.

## CI job

The workflow runs for PRs whose title starts with `refactor` and for PRs
labelled `pure-move`, and writes the report to the job summary. Two details
matter:

- `fetch-depth: 0`: the tool needs the merge base of the PR and its base branch.
- `shell: bash` on the step: the default Actions shell is `bash -e` without
  `pipefail`, so `check_move.py ... | tee -a "$GITHUB_STEP_SUMMARY"` would
  return `tee`'s status and a failed check would pass. `shell: bash` runs
  `bash -eo pipefail`.

To add the job to an existing `ci.yml` instead of a separate workflow, copy the
`pure-move` job, keep the `if:` condition, and add
`github.event_name == 'pull_request' &&` in front of it when the workflow also
runs on `push`. A job inside a workflow with the default `pull_request` types
does not re-run when a PR is retitled or labelled; the standalone template adds
`edited`, `labeled` and `unlabeled` for that reason.

## Limits

- It compares Python definitions only. A moved non-Python file, a changed
  import list or a changed call site is outside its scope.
- It proves the *definitions* are unchanged, not that every caller still
  resolves; run the type checker and the tests as usual.

Source: Oaklight/llm-rosetta#1623.
