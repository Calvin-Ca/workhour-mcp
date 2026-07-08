# Self-hosting

The plugin talks to a **gateway** you run. The gateway authenticates the caller and
forwards tool calls to a **backend** (`ai-service`) that does the real work. This repo
ships a **sandbox backend** so you can run everything immediately; for production you
replace it with your own service that implements the same two endpoints.

## Architecture

```
client (Claude/Codex) ──HTTP──► gateway (:8765) ──HTTP──► ai-service (:8000)
  X-Gateway-Token (shared)        verify token             POST /api/internal/auth/mcp-token
  X-Entity-ID (who you are)       resolve identity ────────►   → { token, userId, entityType }
                                  forward with identity        POST /api/internal/tools/{tool}
                                                               → tool result JSON
```

## The backend contract

Your `ai-service` must implement two endpoints. The reference implementation with fake
data is `server/mock-ai-service/main.py` — read it as the spec.

### 1. `POST /api/internal/auth/mcp-token`

Request: `{ "entity_id": "<self-declared id>", "api_key": "<MCP_API_KEY>" }`
Response: `{ "token": "<JWT>", "userId": "<resolved user id>", "entityType": "<role>" }`

Verify `api_key`, map `entity_id` → a real user, and mint a **short-lived** JWT.

### 2. `POST /api/internal/tools/{tool_name}`

Headers: `X-User-ID`, `X-Entity-Type`, `X-Auth-Token` (the JWT from step 1).
Body: the tool params. Return the tool result as JSON.

Tools the gateway forwards: `save_workhour`, `query_timesheet`, `query_project`,
`compute_statistics`, `generate_weekly_report`, `sql_query`, `kb_outline`,
`kb_keyword_search`, `kb_semantic_search`, `kb_read_section`.

**`save_workhour` must honor `dry_run`**: `dry_run=true` returns a preview and writes
nothing; `dry_run=false` writes. The gateway maps the client's `confirm` flag to
`dry_run = not confirm`, so the two-step confirmation is enforced end-to-end.

## Deploy

```bash
cd server
cp .env.example .env          # set MCP_GATEWAY_TOKEN (openssl rand -hex 32)
# production: set AI_SERVICE_URL to your real backend and drop the mock service
docker compose up -d --build
curl -s localhost:8765/health/health   # → ok
```

To run **without** the sandbox, delete the `mock-ai-service` block from
`docker-compose.yml` and point `AI_SERVICE_URL` at your service.

## Threat model — read before exposing anything

The default auth is a **single shared `MCP_GATEWAY_TOKEN` + a client-declared
`X-Entity-ID`**. That means *anyone holding the token can act as any entity_id*.

- **Trusted network (intranet, VPN): acceptable.** Keep the gateway private; give the
  token only to teammates.
- **Public internet: NOT acceptable as-is.** Before any public exposure you must:
  - replace the shared token with **per-user credentials / OAuth**, and
  - derive identity from the **authenticated token, not a request header**, and
  - never place a real production database behind a publicly reachable gateway.

If you publish this plugin publicly (see OFFICIAL-MARKETPLACE-CHECKLIST.md), you are
publishing the **template**, not access to your data — users run their own gateway.

## Rotating / protecting the token

- Generate with `openssl rand -hex 32`; store in `.env` (git-ignored) or a secrets manager.
- **Never** commit it. The plugin's `.mcp.json` reads it from `WORKHOUR_GATEWAY_TOKEN` at
  runtime — it is never baked into the repo.
- Rotate by changing `MCP_GATEWAY_TOKEN` in `.env`, `docker compose up -d`, and updating
  each client's `WORKHOUR_GATEWAY_TOKEN`.
