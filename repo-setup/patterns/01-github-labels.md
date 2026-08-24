# 01 — GitHub label taxonomy

## Why a shared label system?

Each repo accumulates its own label soup over time — `P0`/`P1`/`P2` in one,
`phase:6`/`phase:7` in another, GitHub defaults nobody uses (`invalid`,
`wontfix`) in all of them. Cross-repo triage becomes harder than it needs to
be: same concept, different names, different colors.

This pattern defines a single label taxonomy used across all active repos. The
system was developed in [mansio](https://github.com/Oaklight/mansio) and
proven effective there.

## Taxonomy

### Type labels (what kind of work)

These describe *what* the issue/PR is. Every issue should have exactly one.

| Label | Color | Description |
|-------|-------|-------------|
| `bug` | `#d73a4a` | Something isn't working |
| `enhancement` | `#a2eeef` | New feature or request |
| `documentation` | `#0075ca` | Improvements or additions to documentation |
| `refactor` | `#f59e0b` | Code refactoring, no behavior change |
| `security` | `#e11d48` | Security vulnerability |
| `discussion` | `#c084fc` | Design discussion, RFC |

### Priority labels (how urgent)

Optional. Use when triage needs to signal urgency. Colors follow a warm
gradient: dark red → red → orange → light pink.

| Label | Color | Description |
|-------|-------|-------------|
| `priority:critical` | `#b91c1c` | Security/data-loss, fix immediately |
| `priority:high` | `#dc2626` | Blocks other work |
| `priority:medium` | `#f97316` | Should fix soon |
| `priority:low` | `#fca5a5` | Nice to have |

### Area labels (which subsystem)

Project-specific. Each repo defines its own `area:*` labels based on its
module structure. Use teal/blue/green/purple tones to visually distinguish
from type (warm tones) and priority (red tones).

Convention:
- Prefix: `area:`
- Lowercase, hyphen-separated
- Color family: cool tones (`#0891b2`, `#2563eb`, `#7c3aed`, `#059669`, etc.)
- Description: short phrase describing the subsystem scope

### Status labels (optional)

Only add these if the project uses GitHub Issues as a lightweight task board
*without* GitHub Projects. Most repos should NOT need these — use GitHub
Projects board columns instead.

| Label | Color | Description |
|-------|-------|-------------|
| `blocked` | `#b91c1c` | Waiting on external dependency |
| `deferred` | `#d4c5f9` | Intentionally postponed |

## What to remove

### GitHub defaults to delete

These labels are auto-created by GitHub but rarely used in practice. Remove
them to keep the label list clean:

| Label | Why remove |
|-------|------------|
| `good first issue` | Not accepting external contributors for most repos |
| `help wanted` | Same — rarely used |
| `invalid` | Just close the issue with a comment |
| `wontfix` | Just close the issue with a comment |
| `question` | Use `discussion` instead, or use GitHub Discussions |
| `duplicate` | Just close with "duplicate of #N" comment |

### Project-specific labels to retire

Any label that served a one-time planning purpose (phase tracking, migration
milestones, version targets) should be removed once the work is done. These
belong in GitHub Milestones, not labels.

Common patterns to clean up:
- `phase:*`, `phase-*` — use Milestones
- `P0`/`P1`/`P2`/`P3`/`P4` — replaced by `priority:*`
- `independent` — no longer needed
- `mcp-v2`, `v3.0.0` — use Milestones
- `new-tool` — use `enhancement` + `area:*`
- `testing`, `style`, `performance` — fold into `refactor` or `enhancement`
- `breaking-change` — note in PR title/description instead
- `dependencies`, `github_actions`, `python`, `python:uv` — Dependabot auto-labels, remove if not using Dependabot

## Base labels config

This YAML defines the standard label set. Save as `.github/labels.yml` in
each repo, then extend with project-specific `area:*` labels.

```yaml
# .github/labels.yml
# Standard label taxonomy — see dev-playbook/repo-setup/01-github-labels.md

# === Type labels ===
- name: bug
  color: "d73a4a"
  description: "Something isn't working"

- name: enhancement
  color: "a2eeef"
  description: "New feature or request"

- name: documentation
  color: "0075ca"
  description: "Improvements or additions to documentation"

- name: refactor
  color: "f59e0b"
  description: "Code refactoring, no behavior change"

- name: security
  color: "e11d48"
  description: "Security vulnerability"

- name: discussion
  color: "c084fc"
  description: "Design discussion, RFC"

# === Priority labels ===
- name: "priority:critical"
  color: "b91c1c"
  description: "Security/data-loss, fix immediately"

- name: "priority:high"
  color: "dc2626"
  description: "Blocks other work"

- name: "priority:medium"
  color: "f97316"
  description: "Should fix soon"

- name: "priority:low"
  color: "fca5a5"
  description: "Nice to have"

# === Area labels (project-specific — add yours below) ===
# - name: "area:core"
#   color: "0891b2"
#   description: "Core library"
```

## Per-project area labels

Recommended `area:*` labels for each active project. The migration operator
should add these to the project's `.github/labels.yml` after the base labels.

### mansio

Already migrated — this is the reference implementation. No changes needed.

| Label | Color | Description |
|-------|-------|-------------|
| `area:backend` | `#0891b2` | Storage backends (sqlite/memory/maildir/nats) |
| `area:frontend` | `#2563eb` | HTTP/SSE/IRC frontends |
| `area:admin` | `#7c3aed` | Admin panel |
| `area:sdk` | `#059669` | piazza-client SDK |
| `area:auth` | `#be123c` | Tokens, ACL, permissions |
| `area:docs` | `#0075ca` | Documentation |

### toolregistry

| Label | Color | Description |
|-------|-------|-------------|
| `area:core` | `#0891b2` | Core registry, tool protocol, discovery |
| `area:mcp` | `#2563eb` | MCP server/client integration |
| `area:cli` | `#7c3aed` | CLI interface |
| `area:typing` | `#059669` | Type system, schema validation |

**Delete:** `P0`, `P1`, `P2`, `P3`, `independent`, `mcp-v2`, `phase:6`,
`phase:7`, `ptc`, `rosetta-compat`, `testing`, `breaking-change`,
`dependencies`, `good first issue`, `help wanted`, `invalid`, `wontfix`,
`duplicate`, `question`

### toolregistry-hub

| Label | Color | Description |
|-------|-------|-------------|
| `area:websearch` | `#0891b2` | Web search engines |
| `area:fetch` | `#2563eb` | Content fetching and extraction |
| `area:tools` | `#7c3aed` | Basic tools (calculator, datetime, weather, etc.) |
| `area:server` | `#059669` | Server, registry, routing |
| `area:infra` | `#64748b` | CI, build, packaging, Docker |

**Delete:** `P0`, `P1`, `P2`, `independent`, `mcp-v2`, `phase:6`, `phase:7`,
`new-tool`, `breaking-change`, `upstream-compat`, `good first issue`,
`help wanted`, `invalid`, `wontfix`, `duplicate`, `question`

### toolregistry-server

Check current labels first — likely similar cleanup to toolregistry-hub.

| Label | Color | Description |
|-------|-------|-------------|
| `area:server` | `#0891b2` | Server runtime, process management |
| `area:config` | `#2563eb` | Configuration, settings |

**Delete:** any `P*`, `phase:*`, `independent`, `mcp-v2`, and GitHub defaults
per the standard cleanup list.

### llm-rosetta

| Label | Color | Description |
|-------|-------|-------------|
| `area:openai` | `#0891b2` | OpenAI converter (chat + responses) |
| `area:anthropic` | `#2563eb` | Anthropic converter |
| `area:gemini` | `#7c3aed` | Google Gemini converter |
| `area:gateway` | `#059669` | Gateway proxy |
| `area:core` | `#64748b` | Core conversion infrastructure |

**Delete:** `P0`, `P1`, `P2`, `P3`, `anthropic`, `openai_chat`,
`openai_responses`, `google_gemini`, `openresponses` (replaced by `area:*`),
`phase-1`, `phase-2`, `phase-3`, `phase-4`, `architecture`, `deferred`,
`performance`, `research`, `spec compliance`, `type-safety`, `dependencies`,
`github_actions`, `python`, `python:uv`, `good first issue`, `help wanted`,
`invalid`, `wontfix`, `duplicate`, `question`

**Note:** `refactor` already exists (as `refactor` with color `#E8D44D`) —
update its color to `#f59e0b` for consistency.

### zerodep

| Label | Color | Description |
|-------|-------|-------------|
| `area:modules` | `#0891b2` | Individual zero-dependency modules |
| `area:registry` | `#2563eb` | Module registry and manifest |
| `area:build` | `#7c3aed` | Build system, packaging, benchmarks |

**Delete:** `P1`, `P2`, `P3`, `P4`, `refactoring` (create `refactor`
instead), `style`, `dependencies`, `python`, `good first issue`,
`help wanted`, `invalid`, `wontfix`, `duplicate`, `question`

### argo-proxy

| Label | Color | Description |
|-------|-------|-------------|
| `area:proxy` | `#0891b2` | Proxy core, request handling |
| `area:routing` | `#2563eb` | Routing, load balancing, model mapping |
| `area:config` | `#7c3aed` | Configuration, provider setup |

**Delete:** `v3.0.0`, `good first issue`, `help wanted`, `invalid`,
`wontfix`, `duplicate`, `question`

### veilrender

| Label | Color | Description |
|-------|-------|-------------|
| `area:renderer` | `#0891b2` | Core rendering engine |
| `area:api` | `#2563eb` | HTTP API, server interface |

**Delete:** `good first issue`, `help wanted`, `invalid`, `wontfix`,
`duplicate`, `question`

### bashtool / pythontool / codecell

Small single-purpose tools — no `area:*` labels needed.

**Delete:** GitHub defaults per the standard cleanup list.

### Other active projects

For repos not listed above, the migration operator should:

1. Check current labels with `gh label list --repo Oaklight/<repo>`
2. Delete GitHub defaults per the standard cleanup list
3. Delete any project-specific legacy labels (`P*`, `phase:*`, etc.)
4. Create base labels (type + priority)
5. Design `area:*` labels based on the project's module structure — only add
   them if the project has 2+ distinct subsystems

## Sync script

Save as `repo-setup/sync-labels.sh` in dev-playbook. Run per-repo:

```bash
./sync-labels.sh Oaklight/toolregistry /path/to/labels.yml [--delete-unlisted]
```

The script creates/updates labels from the YAML and optionally deletes labels
not in the config.

## Migration checklist

For each repo, the migration operator should follow these steps in order:

1. **Audit** — `gh label list --repo Oaklight/<repo>` — note current labels
2. **Check references** — `gh issue list --repo Oaklight/<repo> --state open --json number,labels`
   — check if any open issues use labels that are about to be deleted. If so,
   re-label them first (e.g., `P0` → `priority:critical`)
3. **Create base labels** — run sync script with the base labels config
4. **Create area labels** — run sync script with project-specific area labels
5. **Re-label open issues** — update any open issues that used old labels
6. **Delete old labels** — remove retired labels (this does NOT affect closed
   issues — the label simply disappears from them)
7. **Verify** — `gh label list --repo Oaklight/<repo>` — confirm final state
8. **Commit** — if `.github/labels.yml` was added to the repo, commit it

## Color reference

Quick visual reference for the color palette:

```
Type:     bug=#d73a4a  enhancement=#a2eeef  documentation=#0075ca
          refactor=#f59e0b  security=#e11d48  discussion=#c084fc

Priority: critical=#b91c1c  high=#dc2626  medium=#f97316  low=#fca5a5

Area:     Pick from cool tones:
          #0891b2  #2563eb  #7c3aed  #059669  #64748b  #be123c  #0075ca
```
