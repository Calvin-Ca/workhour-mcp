---
description: 设置本人钉钉 userid（写入 Claude Code 配置，免去终端环境变量）
argument-hint: [你的钉钉 userid，一串数字]
---

# 角色：设置工时填报身份（WORKHOUR_ENTITY_ID）

把用户的钉钉 userid 写进 `~/.claude/settings.json` 的 `env.WORKHOUR_ENTITY_ID`，
让 `workhour-gateway` 连接时带上正确身份。**保留该文件其它所有配置，只改这一个键。**

## 步骤

1. 取 `$ARGUMENTS` 作为 userid。若为空，提示用户「请提供一串数字的钉钉 userid」并停止。

2. 用下面这条命令一次性完成「校验纯数字 + 安全合并写入」（`$ARGUMENTS` 会被替换成用户输入）：

   ```bash
   python3 - "$ARGUMENTS" <<'PY'
   import json, os, re, sys
   uid = (sys.argv[1] if len(sys.argv) > 1 else "").strip()
   if not re.fullmatch(r"\d{4,}", uid):
       print("ERROR: userid 必须是纯数字（钉钉 userid），收到: %r" % uid); sys.exit(1)
   p = os.path.expanduser("~/.claude/settings.json")
   try:
       with open(p, encoding="utf-8") as f:
           cfg = json.load(f)
   except FileNotFoundError:
       cfg = {}
   cfg.setdefault("env", {})["WORKHOUR_ENTITY_ID"] = uid
   os.makedirs(os.path.dirname(p), exist_ok=True)
   with open(p, "w", encoding="utf-8") as f:
       json.dump(cfg, f, ensure_ascii=False, indent=2)
   print("OK: 已写入 WORKHOUR_ENTITY_ID =", uid, "->", p)
   PY
   ```

3. 命令打印 `ERROR` → 把原因如实告诉用户，不要继续。打印 `OK` → 进入第 4 步。

4. 一字不改地告诉用户这两句：
   - 「已写入配置。请**彻底退出 Claude Code 再重开**（不是 /clear），MCP 才会带新身份重连。」
   - 「重开后输入 `/mcp`，看到 `workhour-gateway` 是 connected + authenticated 即成功。」

铁律：
- 只写 `env.WORKHOUR_ENTITY_ID` 这一个键，保留文件里其它所有配置。
- userid 必须是纯数字，否则拒绝写入并说明原因。
- 绝不把该文件改成非法 JSON（用上面的 python 合并，别手动拼接）。
