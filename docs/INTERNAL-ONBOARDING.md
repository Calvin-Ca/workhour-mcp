# 内网同事接入（一页纸）

面向：公司内网、连同一个**共享网关**的同事。管理员已部署好网关、并把地址和令牌**内置进内网版插件**，所以你**只需设自己的钉钉 userid** 一个值。

前提：机器在研发内网，能访问内网 GitLab（装插件）和工时网关（写库）。具体地址向管理员索取——本文不写死内网地址。

---

## Claude Code（推荐，最省事）

### 1. 装插件

```bash
claude plugin marketplace add <管理员给的内网 GitLab marketplace 地址>
claude plugin install workhour
```

### 2. 彻底重启 Claude Code

**不是 `/clear`，是退出进程再重开**——插件命令启动时才加载。

### 3. 设置你的钉钉 userid（在 Claude Code 里一句话，不碰终端）

```
/workhour:set-id 你的钉钉userid
```

它会校验是纯数字后，把 id 安全写进 `~/.claude/settings.json`（不动其它配置）。
**网关地址和令牌插件已内置，你只需设这一个 userid。**

> `userid` 是一串**数字**（形如 `52351731171085063`），不是手机号/姓名。
> 不知道就找管理员查（钉钉后台或用户表）。

### 4. 再彻底重启一次

`/workhour:set-id` 写完配置后再退出重开一次，MCP 才会带新身份连网关。

### 5. 验证

`claude plugin list` 看到 `workhour@workhour-mcp ✔`；Claude Code 里 `/mcp`
看到 `workhour-gateway` 是 connected + authenticated。

### 用

进你要填工时的代码仓库目录，开 Claude Code：
```
/workhour:fill-workhour 上周
```
核对草稿 → 指定项目 → 看预览 → 说「确认」才写库。

---

## Codex CLI

Codex 没有 `/plugin`，也没有 `/workhour:set-id`、`/workhour:fill-workhour`，只能用底层 MCP 工具。
按 [CODEX.md](CODEX.md) 配 `~/.codex/config.toml`（网关 URL / 令牌 / 你的 userid 向管理员索取），
然后在 Codex 里让它调 `save_workhour` 等工具。

---

## 常见问题

| 现象 | 解决 |
|------|------|
| `/mcp` 里网关不是 connected | 确认能连网关；确认已 `/workhour:set-id` 并**彻底重启**过 |
| 写库报 401 / 换不到 token | userid 没设或填错，重跑 `/workhour:set-id 正确的userid`（纯数字）再重启 |
| 命令菜单没有 fill-workhour / set-id | 装完没**彻底重启**；`claude plugin list` 确认已装 |
| 项目名没解析成 ID | 用系统里的准确项目名 |
