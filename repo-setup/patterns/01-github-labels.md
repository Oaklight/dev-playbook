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
| `performance` | `#ff6600` | Performance optimization |
| `architecture` | `#5319e7` | Architectural improvements |
| `research` | `#d4c5f9` | Investigation, specification research |
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
- `testing`, `style` — fold into `refactor` or `enhancement`
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

- name: performance
  color: "ff6600"
  description: "Performance optimization"

- name: architecture
  color: "5319e7"
  description: "Architectural improvements"

- name: research
  color: "d4c5f9"
  description: "Investigation, specification research"

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
| `area:registry` | `#0891b2` | Tool registry, discovery, registration |
| `area:schema` | `#2563eb` | Tool schema, parameter models, type system |
| `area:execution` | `#7c3aed` | Executor backends (inline, process, thread) |
| `area:integrations` | `#059669` | API standards (MCP, OpenAPI, LangChain, native) |
| `area:llm` | `#64748b` | LLM tool-calling, content blocks, rosetta shim |
| `area:server` | `#be123c` | Server (legacy, now toolregistry-server) |

**Delete:** `P0`, `P1`, `P2`, `P3`, `independent`, `mcp-v2`, `phase:6`,
`phase:7`, `ptc`, `rosetta-compat`, `testing`, `breaking-change`,
`dependencies`, `good first issue`, `help wanted`, `invalid`, `wontfix`,
`duplicate`, `question`

### toolregistry-hub

| Label | Color | Description |
|-------|-------|-------------|
| `area:websearch` | `#0891b2` | Web search engines (brave, tavily, searxng, etc.) |
| `area:fetch` | `#2563eb` | Web content fetching and extraction |
| `area:bash` | `#7c3aed` | Bash tool (bashtool/) |
| `area:file-ops` | `#059669` | File operations, search, reader, path_info |
| `area:utilities` | `#64748b` | Calculator, datetime, weather, unit converter, think, cron, todo |
| `area:server` | `#be123c` | Server, registry, routing |
| `area:infra` | `#0075ca` | CI, build, packaging, Docker |

**Delete:** `P0`, `P1`, `P2`, `independent`, `mcp-v2`, `phase:6`, `phase:7`,
`new-tool`, `breaking-change`, `upstream-compat`, `good first issue`,
`help wanted`, `invalid`, `wontfix`, `duplicate`, `question`

### toolregistry-server

| Label | Color | Description |
|-------|-------|-------------|
| `area:adapters` | `#0891b2` | Protocol adapters (MCP, OpenAPI) |
| `area:auth` | `#2563eb` | Authentication, identity, token verification |
| `area:routing` | `#7c3aed` | Route table, registry builder, session management |
| `area:cli` | `#059669` | CLI, configuration, app bootstrap |

**Delete:** `P0`, `P1`, `P2`, `upstream-compat`, `good first issue`,
`help wanted`, `invalid`, `wontfix`, `duplicate`, `question`

### llm-rosetta

| Label | Color | Description |
|-------|-------|-------------|
| `area:openai-chat` | `#0891b2` | OpenAI Chat Completions converter |
| `area:openai-responses` | `#2563eb` | OpenAI Responses API converter |
| `area:open-responses` | `#7c3aed` | Open Responses format (community standard) |
| `area:anthropic` | `#059669` | Anthropic Messages API converter |
| `area:google-gemini` | `#64748b` | Google Gemini converter |
| `area:gateway` | `#be123c` | Gateway proxy |
| `area:core` | `#0075ca` | Core conversion infrastructure |

**Delete:** `P0`, `P1`, `P2`, `P3`, `anthropic`, `openai_chat`,
`openai_responses`, `google_gemini`, `openresponses` (replaced by `area:*`),
`phase-1`, `phase-2`, `phase-3`, `phase-4`, `spec compliance`, `type-safety`,
`dependencies`, `github_actions`, `python`, `python:uv`, `good first issue`,
`help wanted`, `invalid`, `wontfix`, `duplicate`, `question`

**Keep:** `architecture`, `performance`, `research`, `deferred` (now standard
type/status labels — update colors if needed)

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
| `area:transport` | `#0891b2` | Request proxying, bridge, transport layer |
| `area:models` | `#2563eb` | Model registry, upstream mapping, routing |
| `area:config` | `#7c3aed` | Configuration, validation, interactive setup |
| `area:cli` | `#059669` | CLI interface, display |

**Delete:** `v3.0.0`, `good first issue`, `help wanted`, `invalid`,
`wontfix`, `duplicate`, `question`

### veilrender

| Label | Color | Description |
|-------|-------|-------------|
| `area:browser` | `#0891b2` | Browser lifecycle, CDP proxy |
| `area:routes` | `#2563eb` | Render, screenshot, dashboard, health routes |
| `area:storage` | `#7c3aed` | Cache, S3, content storage |

**Delete:** `good first issue`, `help wanted`, `invalid`, `wontfix`,
`duplicate`, `question`

### llm-comply

| Label | Color | Description |
|-------|-------|-------------|
| `area:specs` | `#0891b2` | Compliance spec definitions and test suites per provider |
| `area:runner` | `#2563eb` | Test runner, validators, HTTP client |
| `area:web` | `#7c3aed` | Web dashboard, CLI display |

**Delete:** GitHub defaults per the standard cleanup list.

### codecell

| Label | Color | Description |
|-------|-------|-------------|
| `area:runtime` | `#0891b2` | Core execution runtime |
| `area:python` | `#2563eb` | Python-cell validation/execution |
| `area:bash` | `#7c3aed` | Bash-cell validation/execution |

**Delete:** GitHub defaults per the standard cleanup list.

### talpa

| Label | Color | Description |
|-------|-------|-------------|
| `area:core` | `#0891b2` | Agent orchestration, config, tool loop, events |
| `area:tui` | `#2563eb` | CLI/REPL front-end |

**Delete:** GitHub defaults per the standard cleanup list.

### matrixd

| Label | Color | Description |
|-------|-------|-------------|
| `area:core` | `#0891b2` | Client, config, policy |
| `area:delivery` | `#2563eb` | Delivery backends (exec, stdout, webhook) |
| `area:servers` | `#7c3aed` | REST/MCP server interfaces |

**Delete:** GitHub defaults per the standard cleanup list.

### agentabi

| Label | Color | Description |
|-------|-------|-------------|
| `area:providers` | `#0891b2` | Provider integrations (claude, codex, gemini, opencode, pi) |
| `area:middleware` | `#2563eb` | Logging, timeout, usage middleware |

**Delete:** GitHub defaults per the standard cleanup list.

### llama-wrangler

| Label | Color | Description |
|-------|-------|-------------|
| `area:monitoring` | `#0891b2` | GPU/system monitoring |
| `area:model-management` | `#2563eb` | Model/llama process lifecycle |
| `area:web-ui` | `#7c3aed` | HTTP server, static dashboard |

**Delete:** GitHub defaults per the standard cleanup list.

### tello_renewal

| Label | Color | Description |
|-------|-------|-------------|
| `area:core` | `#0891b2` | Renewal engine, models, services |
| `area:web` | `#2563eb` | Playwright-driven web automation |
| `area:cli` | `#7c3aed` | Command-line interface |
| `area:notification` | `#059669` | Email/notification delivery |

**Delete:** GitHub defaults per the standard cleanup list.

### asr2clip

| Label | Color | Description |
|-------|-------|-------------|
| `area:engines` | `#0891b2` | ASR engine backends (cloud/local) |
| `area:audio` | `#2563eb` | Audio capture, VAD pipeline |
| `area:daemon` | `#7c3aed` | Daemon lifecycle, config |

**Delete:** GitHub defaults per the standard cleanup list.

### nps-ctl

| Label | Color | Description |
|-------|-------|-------------|
| `area:cli` | `#0891b2` | CLI commands |
| `area:tunnel` | `#2563eb` | Tunnel, cluster, host management |
| `area:deploy` | `#7c3aed` | Deployment, SSH proxy |

**Delete:** GitHub defaults per the standard cleanup list.

### ffp-manager

| Label | Color | Description |
|-------|-------|-------------|
| `area:eticket` | `#0891b2` | E-ticket parsing and route analysis |
| `area:alliances` | `#2563eb` | Airline alliances and FFP programs |
| `area:app` | `#7c3aed` | Web app, dashboard, API |

**Delete:** GitHub defaults per the standard cleanup list.

### autossh-tunnel-dockerized

| Label | Color | Description |
|-------|-------|-------------|
| `area:web` | `#0891b2` | Web UI |
| `area:ws-server` | `#2563eb` | WebSocket server |
| `area:cli` | `#7c3aed` | CLI |
| `area:docs` | `#059669` | Documentation |

**Delete:** GitHub defaults per the standard cleanup list.

### Small / single-purpose repos (no area labels)

bashtool, pythontool, heartbeat, ctxweave, matrix-skill, meteorlake-power-ctl,
searxng-bm25-reranker, texlive, rdp_vm, composerize-minimal,
openvino-meteor-lake-ai-inference

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
          refactor=#f59e0b  performance=#ff6600  architecture=#5319e7
          research=#d4c5f9  security=#e11d48  discussion=#c084fc

Priority: critical=#b91c1c  high=#dc2626  medium=#f97316  low=#fca5a5

Area:     Pick from cool tones:
          #0891b2  #2563eb  #7c3aed  #059669  #64748b  #be123c  #0075ca
```
