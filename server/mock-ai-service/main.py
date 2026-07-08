"""Mock ai-service —— 沙箱后端，仅用于本地演示 / 官方 market 评审。

实现网关会调用的两类内部端点，返回**假数据**，不连任何真实数据库：
    POST /api/internal/auth/mcp-token         → 换发假 JWT + 身份
    POST /api/internal/tools/{tool_name}      → 各工具的假返回

⚠️ 生产请把网关的 AI_SERVICE_URL 指向真实 ai-service，而非本 mock。
真实实现负责：项目名→ID 解析、权限校验、dry_run 强制、写库、审计。
"""

from __future__ import annotations

import logging
from datetime import date as _date

from fastapi import FastAPI, Request

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mock-ai-service")

app = FastAPI(title="workhour mock ai-service")

# ---- 沙箱假数据 ---------------------------------------------------------

_PROJECTS = [
    {"projectId": "P1001", "projectName": "安居华富北", "status": "进行中"},
    {"projectId": "P1002", "projectName": "工时管理系统", "status": "进行中"},
    {"projectId": "P1003", "projectName": "AI 助手服务", "status": "进行中"},
]

_SANDBOX_TIMESHEET = [
    {"date": "2026-07-01", "projectName": "工时管理系统", "duration": 8.0,
     "description": "重构参数解析层"},
    {"date": "2026-07-02", "projectName": "AI 助手服务", "duration": 6.5,
     "description": "接入 MCP 网关"},
]


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/internal/auth/mcp-token")
async def mcp_token(payload: dict):
    """按 entity_id 换发假 JWT。真实实现应校验 api_key 并签发短期 JWT。"""
    entity_id = payload.get("entity_id", "")
    logger.info("mcp-token issue entity_id=%s", entity_id)
    return {
        "token": f"sandbox-jwt-for-{entity_id or 'anonymous'}",
        "userId": entity_id or "sandbox-user",
        "entityType": "employee",
    }


def _resolve_project(project_id: str) -> dict:
    for p in _PROJECTS:
        if project_id in (p["projectId"], p["projectName"]):
            return p
    # 未匹配则当作新项目名，回一个占位 ID
    return {"projectId": "P9999", "projectName": project_id or "未知项目"}


async def _save_workhour(params: dict, user_id: str) -> dict:
    proj = _resolve_project(params.get("project_id", ""))
    record = {
        "userId": user_id,
        "projectId": proj["projectId"],
        "projectName": proj["projectName"],
        "workhourDate": params.get("date"),
        "duration": params.get("duration"),
        "description": params.get("description", ""),
    }
    if params.get("dry_run", True):
        return {"mode": "preview", "dry_run": True,
                "message": "预览（未写库）。确认后将写入以下记录：",
                "preview": record}
    return {"mode": "committed", "dry_run": False,
            "message": "填报成功（沙箱）",
            "recordId": "sandbox-" + (params.get("date") or "x"),
            "saved": record}


async def _query_timesheet(params: dict, user_id: str) -> dict:
    return {"userId": user_id, "count": len(_SANDBOX_TIMESHEET),
            "records": _SANDBOX_TIMESHEET}


async def _query_project(params: dict, user_id: str) -> dict:
    kw = params.get("keyword", "")
    pid = params.get("project_id", "")
    rows = _PROJECTS
    if kw:
        rows = [p for p in rows if kw in p["projectName"]]
    if pid:
        rows = [p for p in rows if p["projectId"] == pid]
    return {"count": len(rows), "projects": rows}


async def _compute_statistics(params: dict, user_id: str) -> dict:
    total = sum(r["duration"] for r in _SANDBOX_TIMESHEET)
    return {"scope": params.get("scope") or "self", "totalHours": total,
            "byProject": [{"projectName": "工时管理系统", "hours": 8.0},
                          {"projectName": "AI 助手服务", "hours": 6.5}]}


async def _generate_weekly_report(params: dict, user_id: str) -> dict:
    return {"weekly_report": "本周完成参数解析层重构与 MCP 网关接入，"
                             "累计工时 14.5h，进展顺利。（沙箱示例）"}


async def _sql_query(params: dict, user_id: str) -> dict:
    return {"question": params.get("question", ""),
            "sql": "SELECT project_name, SUM(duration) FROM timesheet "
                   "GROUP BY project_name  -- 沙箱示例，未真正执行",
            "rows": [{"project_name": "工时管理系统", "hours": 8.0},
                     {"project_name": "AI 助手服务", "hours": 6.5}]}


async def _kb_outline(params: dict, user_id: str) -> dict:
    return {"outline": [
        {"file": "考勤制度.md", "sections": ["工时填报规范", "加班认定"]},
        {"file": "项目管理.md", "sections": ["项目立项", "工时归集"]},
    ]}


async def _kb_search(params: dict, user_id: str) -> dict:
    return {"query": params.get("query", ""), "hits": [
        {"file": "考勤制度.md", "section": "工时填报规范",
         "snippet": "每日工时应据实填报，单条 0.5~10 小时……（沙箱）"},
    ]}


async def _kb_read_section(params: dict, user_id: str) -> dict:
    return {"file": params.get("file"), "section": params.get("section"),
            "content": "（沙箱示例章节正文）工时按项目归集，月末汇总核对。"}


_DISPATCH = {
    "save_workhour": _save_workhour,
    "query_timesheet": _query_timesheet,
    "query_project": _query_project,
    "compute_statistics": _compute_statistics,
    "generate_weekly_report": _generate_weekly_report,
    "sql_query": _sql_query,
    "kb_outline": _kb_outline,
    "kb_keyword_search": _kb_search,
    "kb_semantic_search": _kb_search,
    "kb_read_section": _kb_read_section,
}


@app.post("/api/internal/tools/{tool_name}")
async def internal_tool(tool_name: str, params: dict, request: Request):
    user_id = request.headers.get("X-User-ID", "sandbox-user")
    handler = _DISPATCH.get(tool_name)
    if handler is None:
        return {"error": f"unknown tool: {tool_name}"}
    logger.info("tool=%s user=%s", tool_name, user_id)
    return await handler(params, user_id)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
