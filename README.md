# workhour-mcp

Turn your **git history into timesheet drafts** and file them from the command line —
in **Claude Code** (`/workhour:fill-workhour`) or **Codex CLI** (MCP tools) — with a
**two-step confirmation** so nothing is written until you say so.

This repo is a **self-hostable template**. The plugin ships **no secrets and no hard-coded
hosts** — you point it at a gateway you run. A `docker compose up` brings up the gateway
plus a **sandbox backend with fake data**, so you can try the whole flow in one command
without any real database.

```
Claude Code / Codex  ──HTTP──►  gateway (:8765)  ──►  ai-service (your backend)
   plugin / MCP config           auth + identity        projects, timesheet, DB
                                  + forward              (sandbox mock included)
```

## What you get

| Tool (MCP) | Purpose |
|---|---|
| `save_workhour` | File one entry — **preview first, confirm to write** |
| `query_timesheet` | Query entries by person / project / date range |
| `query_project` | Look up projects |
| `compute_statistics` | Summaries & grouping |
| `generate_weekly_report` | Weekly report from your entries |
| `sql_query` | Natural-language → SQL (complex analysis) |
| `kb_outline` / `kb_keyword_search` / `kb_semantic_search` / `kb_read_section` | Knowledge-base retrieval |

Plus a Claude Code slash command **`/workhour:fill-workhour <range>`** that reads the current
repo's git log, drafts hours per day, and files them after you confirm.

## Quick start (60 seconds, sandbox)

```bash
# 1. Run the gateway + sandbox backend
cd server
cp .env.example .env
# edit .env: set MCP_GATEWAY_TOKEN to a strong random value (openssl rand -hex 32)
docker compose up -d --build

# 2. Point the plugin at your gateway (env vars the plugin reads)
export WORKHOUR_GATEWAY_URL="http://localhost:8765/mcp"
export WORKHOUR_GATEWAY_TOKEN="<the MCP_GATEWAY_TOKEN you just set>"
export WORKHOUR_ENTITY_ID="sandbox-user"     # your identity; any string in sandbox

# 3. Install the plugin in Claude Code
claude plugin marketplace add <owner>/workhour-mcp     # this GitHub repo
claude plugin install workhour
# fully restart Claude Code, then: /mcp should show workhour-gateway connected
```

Try it: open any git repo in Claude Code and run `/workhour:fill-workhour 上周`.
Walk to the preview and **stop** — nothing is written until you say “确认”.

## Going to production

Swap the sandbox for your real backend — see **[docs/SELF-HOSTING.md](docs/SELF-HOSTING.md)**.
In short: implement two internal endpoints (`/api/internal/auth/mcp-token` and
`/api/internal/tools/{tool}`) in your own service, then set the gateway's
`AI_SERVICE_URL` to it. The mock in `server/mock-ai-service/main.py` is the contract.

## Docs

- **[SELF-HOSTING.md](docs/SELF-HOSTING.md)** — deploy your own gateway + backend
- **[CODEX.md](docs/CODEX.md)** — use the tools from Codex CLI
- **[INTERNAL-ONBOARDING.md](docs/INTERNAL-ONBOARDING.md)** — one-pager for teammates on a shared gateway
- **[OFFICIAL-MARKETPLACE-CHECKLIST.md](docs/OFFICIAL-MARKETPLACE-CHECKLIST.md)** — submitting to the Anthropic official marketplace

## Security

- The plugin contains **no secrets**. The gateway token and your identity come from
  **environment variables** (`WORKHOUR_GATEWAY_TOKEN`, `WORKHOUR_ENTITY_ID`).
- **Never** expose a gateway that sits in front of a real database to the public internet
  with only the shared-token model. See [SELF-HOSTING.md → Threat model](docs/SELF-HOSTING.md).

## License

MIT — see [LICENSE](LICENSE).
