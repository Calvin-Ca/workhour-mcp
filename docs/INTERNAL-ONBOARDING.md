# 内网同事接入（一页纸）

面向：公司内网、连同一个**共享网关**的同事。管理员已部署好网关，你只需三步。

前提：机器在研发内网，能访问网关。**网关地址（`WORKHOUR_GATEWAY_URL`）与令牌（`WORKHOUR_GATEWAY_TOKEN`）向管理员索取** —— 本文不写死内网地址。

---

## Claude Code

### 1. 设 3 个环境变量（每人一次）

**Mac / Linux（zsh）**：
```bash
cat >> ~/.zshrc <<'EOF'
export WORKHOUR_GATEWAY_URL="<管理员给的网关地址，形如 http://HOST:8765/mcp>"
export WORKHOUR_GATEWAY_TOKEN="<管理员给的网关令牌>"
export WORKHOUR_ENTITY_ID="<你的钉钉 userid，一串数字>"
EOF
source ~/.zshrc
```

**Windows（PowerShell）**：
```powershell
[Environment]::SetEnvironmentVariable("WORKHOUR_GATEWAY_URL","<网关地址，形如 http://HOST:8765/mcp>","User")
[Environment]::SetEnvironmentVariable("WORKHOUR_GATEWAY_TOKEN","<网关令牌>","User")
[Environment]::SetEnvironmentVariable("WORKHOUR_ENTITY_ID","<你的钉钉 userid>","User")
```

> `WORKHOUR_ENTITY_ID` 是数字 userid（形如 `52351731171085063`），不是手机号/姓名。
> 不知道就找管理员查你的 userid（钉钉后台或用户表）。

### 2. 装插件

```bash
claude plugin marketplace add <公开 GitHub repo，或内网 GitLab 地址>
claude plugin install workhour
```

### 3. 彻底重启 Claude Code（不是 /clear，是退出进程再开）

Windows 上要**开新终端**再启动 `claude`（变量才生效）。

**验证**：`claude plugin list` 看到 `workhour@workhour-mcp ✔`；Claude Code 里 `/mcp`
看到 `workhour-gateway` 是 connected + authenticated。

### 用

进你要填工时的代码仓库目录，开 Claude Code：
```
/workhour:fill-workhour 上周
```
核对草稿 → 指定项目 → 看预览 → 说「确认」才写库。

---

## Codex CLI

Codex 没有 `/plugin` 和 `/workhour:fill-workhour`，只能用底层 MCP 工具。
按 [CODEX.md](CODEX.md) 配 `~/.codex/config.toml`（用同一个网关 URL / 令牌 / 你的
entity_id），然后在 Codex 里让它调 `save_workhour` 等工具。

---

## 常见问题

| 现象 | 解决 |
|------|------|
| `/mcp` 里网关不是 connected | 确认能连网关端口；确认三个 env 都设了并重启了终端+Claude |
| 写库报 401 / 换不到 token | `WORKHOUR_ENTITY_ID` 没配或填错（必须是数字 userid）；`echo $WORKHOUR_ENTITY_ID` 验证 |
| 命令菜单没有 fill-workhour | 装完没**彻底重启**；`claude plugin list` 确认已装 |
| 项目名没解析成 ID | 用系统里的准确项目名 |
