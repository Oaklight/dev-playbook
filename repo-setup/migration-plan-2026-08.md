# GitHub Label Migration Plan — August 2026

Generated from audit of 32 Oaklight-owned repos. Reference taxonomy:
`dev-playbook/repo-setup/patterns/01-github-labels.md`

## Base labels (applied to ALL repos)

**CREATE** (if not already present):
- `refactor` (#f59e0b) — Code refactoring, no behavior change
- `performance` (#ff6600) — Performance optimization
- `architecture` (#5319e7) — Architectural improvements
- `research` (#d4c5f9) — Investigation, specification research
- `security` (#e11d48) — Security vulnerability
- `discussion` (#c084fc) — Design discussion, RFC
- `priority:critical` (#b91c1c) — Security/data-loss, fix immediately
- `priority:high` (#dc2626) — Blocks other work
- `priority:medium` (#f97316) — Should fix soon
- `priority:low` (#fca5a5) — Nice to have

**KEEP** (already standard across all repos):
- `bug` (#d73a4a), `enhancement` (#a2eeef), `documentation` (#0075ca)

**DELETE** (from all repos that have them):
- `good first issue`, `help wanted`, `invalid`, `wontfix`, `duplicate`, `question`

---

## Tier 1 — Complex migrations (open issues need relabeling)

### llm-rosetta (Oaklight/llm-rosetta) — HEAVIEST

**area:* labels (one per converter type):**
| Label | Color | Description |
|-------|-------|-------------|
| `area:openai-chat` | #0891b2 | OpenAI Chat Completions converter |
| `area:openai-responses` | #2563eb | OpenAI Responses API converter |
| `area:open-responses` | #7c3aed | Open Responses format (community standard) |
| `area:anthropic` | #059669 | Anthropic Messages API converter |
| `area:google-gemini` | #64748b | Google Gemini converter |
| `area:gateway` | #be123c | Gateway proxy |
| `area:core` | #0075ca | Core conversion infrastructure |

**UPDATE:** `refactor` color #E8D44D → #f59e0b

**UPDATE:** `architecture` color #5319E7 already matches; `research` color
#D4C5F9 already matches; `deferred` keep as status label (#d4c5f9 → update
if needed); `performance` color #FF6600 already matches

**DELETE (legacy):** `dependencies`, `github_actions`, `type-safety`, `phase-1`,
`phase-2`, `phase-3`, `phase-4`, `P0`, `P1`, `P2`, `P3`, `spec compliance`,
`python`, `python:uv`,
`openai_chat`, `openai_responses`, `anthropic`, `google_gemini`, `openresponses`

**RELABEL (27 open issues affected):**
- Converter labels → area:* mapping:
  - `openai_chat` → `area:openai-chat`
  - `openai_responses` → `area:openai-responses`
  - `openresponses` → `area:open-responses`
  - `anthropic` → `area:anthropic`
  - `google_gemini` → `area:google-gemini`
  - `gateway` → `area:gateway`
- Priority: `P1` → `priority:high`, `P2` → `priority:medium`, `P3` → `priority:low`
- `architecture`, `performance`, `research`, `deferred` — KEEP (now standard type/status labels)
- `spec compliance` → drop or relabel to `research`

---

### toolregistry-hub (Oaklight/toolregistry-hub) — 8 open issues

**area:* labels:**
| Label | Color | Description |
|-------|-------|-------------|
| `area:websearch` | #0891b2 | Web search engines (brave, tavily, searxng, etc.) |
| `area:fetch` | #2563eb | Web content fetching and extraction |
| `area:bash` | #7c3aed | Bash tool (bashtool/) |
| `area:file-ops` | #059669 | File operations, search, reader, path_info |
| `area:utilities` | #64748b | Calculator, datetime, weather, unit converter, think, cron, todo |
| `area:server` | #be123c | Server, registry, routing |
| `area:infra` | #0075ca | CI, build, packaging, Docker |

**DELETE (legacy):** `P0`, `P1`, `P2`, `mcp-v2`, `phase:6`, `phase:7`,
`independent`, `breaking-change`, `upstream-compat`, `new-tool`

**RELABEL:**
- #165/#164/#163/#162: `new-tool` + `independent` → `enhancement` + appropriate `area:*`
- #161: `P2` → `priority:medium`, `new-tool` → `enhancement` + `area:*`, drop `independent`
- #150: `P1` → `priority:high`, drop `upstream-compat`
- #144: `P2` → `priority:medium`
- #68: `P1` → `priority:high`

---

### toolregistry (Oaklight/ToolRegistry) — 5 open issues

**area:* labels:**
| Label | Color | Description |
|-------|-------|-------------|
| `area:registry` | #0891b2 | Tool registry, discovery, registration |
| `area:schema` | #2563eb | Tool schema, parameter models, type system |
| `area:execution` | #7c3aed | Executor backends (inline, process, thread) |
| `area:integrations` | #059669 | API standards (MCP, OpenAPI, LangChain, native) |
| `area:llm` | #64748b | LLM tool-calling, content blocks, rosetta shim |
| `area:server` | #be123c | Server (legacy, now toolregistry-server) |

**DELETE (legacy):** `P0`, `P1`, `P2`, `P3`, `mcp-v2`, `phase:6`, `phase:7`,
`independent`, `breaking-change`, `dependencies`, `testing`, `rosetta-compat`, `ptc`

**RELABEL:**
- #236: `P1` → `priority:high`, `rosetta-compat` → drop or `area:core`
- #77: `P2` → `priority:medium`
- #72: `P2` → `priority:medium`, drop `independent`
- #164: `question` → `discussion`
- #178: `ptc` → `enhancement` + `area:core`

---

### toolregistry-server (Oaklight/toolregistry-server) — 3 open issues

**area:* labels:**
| Label | Color | Description |
|-------|-------|-------------|
| `area:adapters` | #0891b2 | Protocol adapters (MCP, OpenAPI) |
| `area:auth` | #2563eb | Authentication, identity, token verification |
| `area:routing` | #7c3aed | Route table, registry builder, session management |
| `area:cli` | #059669 | CLI, configuration, app bootstrap |

**DELETE (legacy):** `P0`, `P1`, `P2`, `upstream-compat`

**RELABEL:**
- #51/#50: `P1` → `priority:high`, drop `upstream-compat`
- #24: `P1` → `priority:high`

---

### tinyleaf (Oaklight/tinyleaf) — 10 open issues

**area:* labels:**
| Label | Color | Description |
|-------|-------|-------------|
| `area:compiler` | #0891b2 | LaTeX compilation pipeline |
| `area:server` | #2563eb | HTTP server & handlers |
| `area:git` | #7c3aed | git_ops / repo integration |
| `area:cli` | #059669 | Command-line interface |
| `area:frontend` | #64748b | Static assets, JS/CSS preview UI |

**UPDATE:** `refactor` color #fbca04 → #f59e0b

**DELETE (legacy):** `P0`, `P1`, `P2`, `P3`

**RELABEL:**
- #30, #29, #28, #27, #26, #25: `P3` → `priority:low`
- #23, #22, #21, #20: `P2` → `priority:medium`

---

### weilink (Oaklight/weilink) — 2 open issues

**area:* labels:**
| Label | Color | Description |
|-------|-------|-------------|
| `area:protocol` | #0891b2 | iLink Bot protocol layer |
| `area:server` | #2563eb | Server/runtime core |
| `area:admin` | #7c3aed | Admin UI/API |
| `area:integrations` | #059669 | Claude Code / Codex / OpenCode integrations |
| `area:crypto` | #64748b | AES/H2H crypto layer |

**UPDATE:** `refactor` color #C5DEF5 → #f59e0b

**DELETE (legacy):** `P0`, `P1`, `P2`, `P3`, `protocol`, `needs-investigation`

**RELABEL:**
- #20: `protocol` → `area:protocol`, `P3` → `priority:low`, drop `needs-investigation`
- #19: same mapping

---

### webui-lite (Oaklight/webui-lite) — 7 open issues

**area:* labels:**
| Label | Color | Description |
|-------|-------|-------------|
| `area:frontend` | #0891b2 | Static UI, JavaScript, CSS |
| `area:providers` | #2563eb | LLM provider integrations (rosetta, openai, agentabi) |
| `area:routers` | #7c3aed | Chat, history, settings API routes |
| `area:context` | #059669 | Context management, sliding window |
| `area:storage` | #64748b | Database, config persistence |

**DELETE (legacy):** `ui`, `design`, `backend`, `frontend`, `config`, `streaming`,
`architecture`, `provider`, `priority: high`, `priority: low`, `priority: medium`

**RELABEL:**
- `ui` + `frontend` → `area:frontend`
- `backend` → drop (covered by `area:routers` / `area:storage`)
- `provider` → `area:providers`
- `config` → `area:storage`
- `streaming`, `architecture` → drop (now standard type labels)
- `priority: high/medium/low` (with spaces) → `priority:high/medium/low` (no spaces)

---

### zerodep (Oaklight/zerodep) — 3 open issues

**area:* labels:**
| Label | Color | Description |
|-------|-------|-------------|
| `area:modules` | #0891b2 | Individual zero-dependency modules |
| `area:registry` | #2563eb | Module registry and manifest |
| `area:build` | #7c3aed | Build system, packaging, benchmarks |

**DELETE (legacy):** `P1`, `P2`, `P3`, `P4`, `refactoring`, `style`,
`dependencies`, `python`

**RELABEL:**
- #113: `P4` → `priority:low`
- #112: `P3` → `priority:low`
- #87: `P3` → `priority:low`

---

## Tier 2 — Medium complexity (custom labels to delete, no relabeling)

### argo-proxy (Oaklight/argo-proxy)

**area:* labels:**
| Label | Color | Description |
|-------|-------|-------------|
| `area:transport` | #0891b2 | Request proxying, bridge, transport layer |
| `area:models` | #2563eb | Model registry, upstream mapping, routing |
| `area:config` | #7c3aed | Configuration, validation, interactive setup |
| `area:cli` | #059669 | CLI interface, display |

**DELETE (legacy):** `v3.0.0`

**RELABEL:** none (no open issues affected)

---

### llm-comply (Oaklight/llm-comply)

**area:* labels:**
| Label | Color | Description |
|-------|-------|-------------|
| `area:specs` | #0891b2 | Compliance spec definitions and test suites per provider |
| `area:runner` | #2563eb | Test runner, validators, HTTP client |
| `area:web` | #7c3aed | Web dashboard, CLI display |

**DELETE (legacy):** none beyond GitHub defaults

**RELABEL:** none (no open issues)

---

## Tier 3 — Simple (GitHub defaults only, no custom labels)

These repos only need: delete 6 GitHub defaults + create base labels + create area:* labels.

### With area:* labels

| Repo | area:* labels |
|------|---------------|
| **codecell** | `area:runtime`(#0891b2) Core execution runtime; `area:python`(#2563eb) Python-cell; `area:bash`(#7c3aed) Bash-cell |
| **talpa** | `area:core`(#0891b2) Agent orchestration, config, tool loop, events; `area:tui`(#2563eb) CLI/REPL front-end |
| **matrixd** | `area:core`(#0891b2) Client/config/policy; `area:delivery`(#2563eb) Delivery backends; `area:servers`(#7c3aed) REST/MCP interfaces |
| **agentabi** | `area:providers`(#0891b2) Provider integrations (claude, codex, gemini, opencode, pi); `area:middleware`(#2563eb) Logging/timeout/usage middleware |
| **llama-wrangler** | `area:monitoring`(#0891b2) GPU/system monitoring; `area:model-management`(#2563eb) Model/llama process lifecycle; `area:web-ui`(#7c3aed) HTTP server, static dashboard |
| **tello_renewal** | `area:core`(#0891b2) Renewal engine; `area:web`(#2563eb) Playwright automation; `area:cli`(#7c3aed) CLI; `area:notification`(#059669) Email delivery |
| **asr2clip** | `area:engines`(#0891b2) ASR backends; `area:audio`(#2563eb) Audio/VAD pipeline; `area:daemon`(#7c3aed) Daemon lifecycle |
| **nps-ctl** | `area:cli`(#0891b2) CLI commands; `area:tunnel`(#2563eb) Tunnel/cluster core; `area:deploy`(#7c3aed) Deployment logic |
| **veilrender** | `area:browser`(#0891b2) Browser lifecycle, CDP proxy; `area:routes`(#2563eb) Render, screenshot, dashboard, health routes; `area:storage`(#7c3aed) Cache, S3, content storage |
| **ffp-manager** | `area:eticket`(#0891b2) E-ticket parsing and route analysis; `area:alliances`(#2563eb) Airline alliances and FFP programs; `area:app`(#7c3aed) Web app, dashboard, API |
| **autossh-tunnel-dockerized** | `area:web`(#0891b2) Web UI; `area:ws-server`(#2563eb) WebSocket server; `area:cli`(#7c3aed) CLI; `area:docs`(#059669) Documentation |

### Without area:* labels (too small or single-purpose)

| Repo | Reason |
|------|--------|
| **bashtool** | Single-file tool |
| **pythontool** | Single-purpose package |
| **heartbeat** | GitHub Actions workflow only |
| **ctxweave** | Pre-alpha, no modules yet |
| **matrix-skill** | Single-purpose skill package |
| **meteorlake-power-ctl** | Single-script utility |
| **searxng-bm25-reranker** | Single-purpose library |
| **texlive** | Docker build repo |
| **rdp_vm** | Docker config repo |
| **composerize-minimal** | Thin wrapper repo |
| **openvino-meteor-lake-ai-inference** | Documentation/benchmark repo |

---

## Execution order

1. **Tier 3 (no area, simple)** — 11 repos, mechanical: delete defaults + create base labels
2. **Tier 3 (with area)** — 11 repos, same + create area labels
3. **Tier 2** — 2 repos, minor extra cleanup
4. **Tier 1** — 8 repos, relabel open issues first, then delete old labels

Within Tier 1, do llm-rosetta **last** (most complex, 27 open issues).

## Script usage

```bash
cd ~/projects/dev-playbook/repo-setup

# For each repo, create a project-specific labels.yml combining base + area:
cat templates/labels-base.yml > /tmp/labels.yml
# Append area:* labels for the specific project...

# Sync (creates + updates, does NOT delete yet):
./sync-labels.sh Oaklight/<repo> /tmp/labels.yml

# After relabeling open issues, delete unlisted labels:
./sync-labels.sh Oaklight/<repo> /tmp/labels.yml --delete-unlisted
```
