# Using the tools from Codex CLI

Codex has **no plugin system**, so `/plugin` and the `/workhour:fill-workhour` slash
command are Claude-Code-only. But the gateway is a standard MCP server, so Codex can use
the **tools** (`save_workhour`, `query_timesheet`, …) directly.

Configure in `~/.codex/config.toml`.

## Option A — stdio→HTTP bridge (works on every Codex version)

Codex historically launches MCP servers as local processes (stdio). Bridge to the remote
HTTP gateway with [`mcp-remote`](https://www.npmjs.com/package/mcp-remote):

```toml
[mcp_servers.workhour-gateway]
command = "npx"
args = [
  "-y", "mcp-remote",
  "http://YOUR-GATEWAY-HOST:8765/mcp",
  "--header", "X-Gateway-Token:${WORKHOUR_GATEWAY_TOKEN}",
  "--header", "X-Entity-ID:${WORKHOUR_ENTITY_ID}",
]

[mcp_servers.workhour-gateway.env]
WORKHOUR_GATEWAY_TOKEN = "<your gateway token>"
WORKHOUR_ENTITY_ID = "<your identity>"
```

> If `--header` env interpolation isn't honored by your `mcp-remote` version, put the
> literal values in the `--header` args instead. Keep the file readable only by you
> (`chmod 600 ~/.codex/config.toml`) since it then contains the token.

## Option B — native HTTP transport (newer Codex only)

If your Codex build supports streamable-HTTP MCP servers natively, configure the URL and
headers directly (no `mcp-remote`). Transport support varies by version — **verify on your
build**; if the tools don't show up, fall back to Option A.

## Verify

Start Codex and run `/mcp` (or the equivalent list command). You should see
`workhour-gateway` and its tools. Ask: “file 4 hours today on project 工时管理系统” — the
model should call `save_workhour` and show you a preview first.

There is no git-history slash command in Codex; drive `save_workhour` conversationally,
or ask Codex to read `git log` itself and propose entries.
