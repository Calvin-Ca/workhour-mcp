# 提交 Anthropic 官方 marketplace 清单

目标：把本插件登记到官方插件市场 `anthropics/claude-plugins-official`，让用户可
`/plugin marketplace add anthropics/claude-plugins-official` 后直接安装。

官方市场的用户默认期望「装完能用」。本插件依赖自建后端，因此定位必须讲清是
**可自托管模板 + 附带沙箱一键体验**，否则容易被打回。

## 准备（发布前必须全绿）

- [ ] **零密钥**：仓库全文 `git grep -nEi 'token|secret|api[_-]?key|password'` 无真实值；
      `.mcp.json` 仅用 `${WORKHOUR_GATEWAY_URL/TOKEN/ENTITY_ID}` 占位。
- [ ] **无内网痕迹**：无 `172.` / `192.168.` / 内网 GitLab 地址 / 内网主机名。
- [ ] **干净历史**：全新仓库（勿从内网仓库 fork）；若有历史，`git log -p | grep` 确认从未提交过令牌，
      否则用 `git filter-repo` 清除。
- [ ] **一键可体验**：`cd server && cp .env.example .env && docker compose up -d --build`
      后，Claude Code 能连上网关并跑通 `save_workhour` 预览（沙箱假数据）。
- [ ] **LICENSE** 存在（MIT）。
- [ ] **README** 首屏点明「self-hostable template」+ 60 秒 quick start。
- [ ] `plugin.json` 的 `homepage` 指向公开 repo；`version` 语义化。
- [ ] `.mcp.json` / `marketplace.json` / `plugin.json` JSON 合法（`python -m json.tool` 校验）。

## 提交流程

1. 先自建公开市场验证端到端：把本仓库推到公开 GitHub → 在干净机器上
   `claude plugin marketplace add <owner>/workhour-mcp && claude plugin install workhour`
   → 全流程跑通。
2. Fork `anthropics/claude-plugins-official`，按其 `marketplace.json` 结构把本插件登记为
   一个条目（`source` 指向本仓库），遵守其 README 的贡献/命名规范。
3. 提 PR，说明：用途、这是自托管模板、如何用沙箱一键体验、安全模型（共享令牌仅限可信网络）。
4. 按评审意见迭代。

## 双市场并行

- **自建公开市场**（本仓库 `.claude-plugin/marketplace.json`）：立即可用，无需评审，你完全可控。
- **官方市场**：过审后获得曝光。两者指向同一仓库、同一插件，用户二选一添加即可。

## 发布后

- [ ] 在真实内网网关上让同事按 [INTERNAL-ONBOARDING.md](INTERNAL-ONBOARDING.md) 接入。
- [ ] 记录支持入口（issues / 维护者）。
- [ ] 版本升级：改 `plugin.json` version → 打 tag → 用户 `claude plugin marketplace update` + 重装。
