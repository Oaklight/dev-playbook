# 09 — Strip AI co-author trailers from PR commits

AI coding tools (Claude, Cursor, Copilot, Codex, etc.) often append
`Co-authored-by` trailers to commit messages. This workflow automatically
strips them from PR commits to keep git history clean.

## How it works

The workflow template is at
[`templates/workflows/strip-ai-coauthor.yml`](../templates/workflows/strip-ai-coauthor.yml).

Two jobs handle same-repo and fork PRs differently:

### Same-repo PRs (`strip-ai-coauthor`)

1. Checks out the PR branch with full history.
2. Scans all commits in the PR range for `Co-authored-by` lines matching
   known AI agents.
3. If found, rewrites the commits with `git filter-branch` to remove those
   lines, preserving human co-author trailers.
4. Force-pushes the cleaned branch back — this triggers a new `synchronize`
   event, but since the rewritten commits are clean, the second run is a
   no-op.

### Fork PRs (`check-fork-pr`)

Can't push to external forks, so the job just fails with instructions for
the contributor to rewrite their commit messages manually.

## Detected agents

The regex matches these names in `Co-authored-by` lines (case-insensitive):

| Pattern | Covers |
|---------|--------|
| `claude` | Anthropic Claude |
| `cursor` | Cursor IDE, cursor-agent |
| `codex` | OpenAI Codex CLI |
| `copilot` | GitHub Copilot |
| `devin` | Devin AI |
| `aider` | Aider |
| `cline` | Cline |
| `windsurf` | Windsurf / Codeium |
| `gemini` | Google Gemini |
| `opencode` | OpenCode |

To add a new agent, append it to the `AI_PATTERN` regex in the workflow.

## Edge cases

- **Human co-authors are preserved.** Only lines matching the AI pattern are
  stripped; other `Co-authored-by` trailers remain untouched.
- **Name collisions.** A human named exactly "Claude" (not "Claudette",
  "Claudia", etc.) would be falsely matched. Adjust the pattern if this
  applies to your team.
- **Clean PRs skip rewriting.** If no AI trailers are found, the job exits
  early without touching any commits.
- **Force-push loop.** The rewrite triggers a `synchronize` event, but the
  second run finds no AI trailers and exits cleanly.

## Adoption

Copy the template and you're done — no secrets or configuration needed
beyond the default `GITHUB_TOKEN`:

```bash
cp templates/workflows/strip-ai-coauthor.yml \
   /path/to/your-repo/.github/workflows/
```
