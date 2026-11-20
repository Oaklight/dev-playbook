# 02 — Pull request workflow

Rules that decide how much review a PR needs and in what order PRs merge,
plus the template and the overlap tool that back them. They fit repositories
where one maintainer (or a small team) merges many PRs, including PRs prepared
with AI assistance.

## Files

| File | Copy to |
|------|---------|
| [`templates/pull_request_template.md`](../templates/pull_request_template.md) | `.github/pull_request_template.md` |
| [`templates/scripts/dev/pr_overlap.py`](../templates/scripts/dev/pr_overlap.py) | `scripts/dev/pr_overlap.py` |
| [`templates/tests/test_pr_overlap.py`](../templates/tests/test_pr_overlap.py) | `tests/test_pr_overlap.py` |

Add the "Pull requests" section below to the repository's `CONTRIBUTING.md`
and edit the bracketed parts. The template links to that section by name.

## Review tiers

The author ticks one risk tier in the template. When a PR spans tiers, it
takes the highest.

| Tier | Typical change | Review |
|------|----------------|--------|
| Pure move | Code moves with no logic edit | One reviewer checks only that the mechanical proof is credible. CI green plus the proof can merge. |
| Boundary or contract change | Imports, public API, config schema, wire format | One reviewer plus the maintainer. |
| Runtime-behaviour change | Logic that runs differently after the PR | One or two reviewers who read the logic. |
| Security-relevant | Auth, keys, credentials, sanitizing, network exposure | Always reviewed, ideally by someone other than the author's usual reviewer. |

For a pure move, the proof in the template is the move-check summary
([pattern 10](../../ci/patterns/10-pure-move-check.md)) and a passing type
check. Where those tools are not installed, the author gives the equivalent
evidence by hand.

## Who reviews what

Assign the reviewer by the path a PR touches, not by the author's choice. Keep
a table of path to area in `CONTRIBUTING.md`. Add a `CODEOWNERS` file only when
the area-to-person split can be verified from the repository; do not list an
owner you cannot name. Until then, name the maintainer as the person who
assigns the reviewer:

```markdown
| Paths | Area |
| --- | --- |
| `src/<pkg>/<core area>/` | <what it is> |
| `src/<pkg>/{auth,keys}/` | Security-relevant: credentials, auth |
| `src/<pkg>/_vendor/` | Vendored: re-vendor from upstream, never hand-edit |
| `.github/`, `scripts/`, `Makefile`, `pyproject.toml` | Build, CI, tooling |
```

### Required checks and skipped jobs

A job skipped by its `if:` condition (for example the pure-move job on a PR
without the `pure-move` label) reports as skipped, and branch protection counts
a skipped job as success. Listing such a job as a required check therefore does
not block a PR that does not run it, and it is safe to require; the check
only gates the PRs that opt in.

## Series and overlap

Before opening a PR, run the overlap check:

```bash
python scripts/dev/pr_overlap.py            # current branch against the default branch
python scripts/dev/pr_overlap.py --local    # also other local branches
python scripts/dev/pr_overlap.py --fail-on-overlap   # gate: 1 on overlap, 2 if unverified
```

It lists every open PR that touches the same files and excludes the branch's
own PR (by head ref name, by head commit, and by `$GITHUB_HEAD_REF`, so
`--head HEAD` or a SHA works too). It needs the `gh` CLI. The exit status
depends on the mode:

| Mode | Exit 0 | Exit 1 | Exit 2 |
|------|--------|--------|--------|
| Default (hook-safe) | Always, including overlap (printed as a WARNING) and a check that could not run (printed as "unverified") | never | never |
| `--fail-on-overlap` (gate) | The check ran and found no overlap | The check ran and found overlap | The check could not complete: `gh` or git failed, the JSON was bad, or the PR list hit its 200-PR limit |

A gate never passes on a check that did not finish. The tool warns when the PR
list reaches the limit, because `gh pr list` has no pagination. The base
defaults to `origin/HEAD`, then `origin/main`, then `origin/master`; `--base`
overrides it.

If a PR overlaps, merge a series one PR at a time and rebase the rest after
each merge.

## Small PRs

- One refactor or one concern per PR.
- Follow-on mechanical edits (generated-file regeneration, doc touch-ups) go
  after the PR they depend on. Do not open them as independent PRs.

## Requesting review

Request review only after CI is fully green. Do not skip a hook to get there:
if a hook fails locally and passes in CI, fix the local environment (for
`ty` in a worktree, see [pattern 11](../../ci/patterns/11-ty-worktree-wrapper.md)).
If you skipped any hook, name it and the reason in the template.

## Adapting

- Replace the lint, test and type-check lines in the template with the
  repository's real commands. Write the command, not "lint": a repository with
  several linters needs the exact one (for example `pre-commit run --all-files`).
  Do not ask for a diagnostic count unless a tool in the repository prints it.
- Delete the pure-move and overlap lines if the repository does not carry those
  tools.
- Keep the AI-disclosure line if the repository forbids AI `Co-authored-by`
  trailers (see [pattern 09](../../ci/patterns/09-strip-ai-coauthor.md)).

If the repository dismisses stale reviews, a new commit clears earlier
approvals. Re-request review after pushing review fixes.

Source: Oaklight/llm-rosetta#1624.
