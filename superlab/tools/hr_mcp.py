#!/usr/bin/env python3
"""사내 API를 MCP 도구로 감싸는 stdio 서버. 준비 명령(setup.sh) 뒤 `/mcp`에 `hr`로 보인다 -- lab1(메일·일정)과 lab3(연차 조회·신청)이 쓴다.

등록은 `.mcp.json`에 있다(수동 등록: claude mcp add --scope project hr -- python3 tools/hr_mcp.py).
권한: `.claude/settings.json`에서 조회 `mcp__hr__get_*`는 allow, 변경 `mcp__hr__request_*`는 ask. 승인 우선순위는 deny → ask → allow라
스킬이 머리 부분에서 신청 도구를 미리 허락해도 승인 창은 남는다.
토큰은 환경 변수 LAB_TOKEN에서만 읽고 어디에도 출력하지 않는다. 오류는 isError 결과로 돌려준다(서버가 죽지 않는다).
"""

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_BASE = "https://REPLACE-AFTER-DEPLOY.cloudfront.net"

# 메일·일정은 Microsoft Graph 응답 형식({"value": [...]})을 그대로 넘긴다. 실제 Outlook MCP로 바꿔도 스킬이 같은 필드를 읽는다.
GRAPH_TOOLS = {"get_sent_mail": "/v1/mail/{}/sent", "get_events": "/v1/calendar/{}"}
MAILBOX_ARG = {"type": "object", "properties": {"mailbox": {
    "type": "string", "enum": ["planning", "sales", "cs", "hr"],
    "description": "실습 메일함(직무). planning 기획·운영(기본), sales 영업, cs CS, hr 인사"}}, "additionalProperties": False}

TOOLS = [
    {
        "name": "get_sent_mail",
        "description": "보고 주에 내가 보낸 메일 목록을 조회한다(Graph message: subject, sentDateTime, toRecipients, bodyPreview).",
        "inputSchema": MAILBOX_ARG,
    },
    {
        "name": "get_events",
        "description": "보고 주와 다가올 근무일의 내 일정을 조회한다(Graph event: subject, start, end, attendees).",
        "inputSchema": MAILBOX_ARG,
    },
    {
        "name": "get_team_leave",
        "description": "팀 전원의 연차 현황을 조회한다(팀 이름, 기준일, 직원별 역할·총 일수·사용·잔여).",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "get_leave_requests",
        "description": "연차 신청 내역을 조회한다(최근 20건, 신청 ID·직원·날짜·일수·상태). 같은 실습 토큰을 쓰는 다른 참가자의 신청도 함께 보인다.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "get_leave_balance",
        "description": "직원 한 명의 연차 현황을 조회한다.",
        "inputSchema": {
            "type": "object",
            "properties": {"employee": {"type": "string"}},
            "required": ["employee"],
            "additionalProperties": False,
        },
    },
    {
        "name": "request_leave",
        "description": "직원의 연차 사용을 신청한다.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "employee": {"type": "string"},
                "date": {"type": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}$"},
                "days": {"type": "number", "exclusiveMinimum": 0},
            },
            "required": ["employee", "date", "days"],
            "additionalProperties": False,
        },
    },
]


def text_result(text, is_error=False):
    result = {"content": [{"type": "text", "text": text}]}
    if is_error:
        result["isError"] = True
    return result


def api_request(method, path, payload=None):
    token = os.environ.get("LAB_TOKEN", "")
    if not token:
        return None, text_result("LAB_TOKEN이 없습니다. bash tools/setup.sh로 토큰을 등록하세요.", True)

    base = os.environ.get("LAB_API_BASE", DEFAULT_BASE).rstrip("/")
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(base + path, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        raw = error.read().decode("utf-8", "replace")
        return None, text_result(raw or f"HTTP {error.code}", True)
    except (urllib.error.URLError, TimeoutError) as error:
        return None, text_result(f"사내 API에 연결하지 못했습니다: {error}. LAB_API_BASE를 확인하세요.", True)

    try:
        return json.loads(raw), None
    except json.JSONDecodeError:
        return None, text_result(f"사내 API 응답이 JSON이 아닙니다: {raw}", True)


def call_tool(name, arguments):
    if name in GRAPH_TOOLS:
        mailbox = urllib.parse.quote(str(arguments.get("mailbox") or "planning"), safe="")
        data, error = api_request("GET", GRAPH_TOOLS[name].format(mailbox))
        if error:
            return error
        return text_result(json.dumps(data, ensure_ascii=False))

    if name == "get_team_leave":
        data, error = api_request("GET", "/v1/leave")
        if error:
            return error
        return text_result(json.dumps(data, ensure_ascii=False))

    if name == "get_leave_requests":
        data, error = api_request("GET", "/v1/leave/requests")
        if error:
            return error
        return text_result(json.dumps(data, ensure_ascii=False))

    if name == "get_leave_balance":
        employee = str(arguments.get("employee", ""))
        path = "/v1/leave/" + urllib.parse.quote(employee, safe="")
        data, error = api_request("GET", path)
        if error:
            return error
        return text_result(
            f"{data['employee']}님의 연차는 총 {data['annual']}일, 사용 {data['used']}일, "
            f"잔여 {data['remaining']}일입니다."
        )

    if name == "request_leave":
        payload = {
            "employee": arguments.get("employee"),
            "date": arguments.get("date"),
            "days": arguments.get("days"),
        }
        data, error = api_request("POST", "/v1/leave/requests", payload)
        if error:
            return error
        return text_result(
            f"{data['employee']}님의 {data['date']} 연차 {data['days']}일 신청을 접수했습니다. "
            f"신청 ID {data['request_id']}, 상태 {data['status']}."
        )

    return text_result(f"알 수 없는 도구입니다: {name}", True)


def response(message):
    method = message.get("method")
    request_id = message.get("id")
    if method == "notifications/initialized":
        return None
    if method == "initialize":
        params = message.get("params", {})
        result = {
            "protocolVersion": params.get("protocolVersion"),
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "hr", "version": "1.0.0"},
        }
    elif method == "ping":
        result = {}
    elif method == "tools/list":
        result = {"tools": TOOLS}
    elif method == "tools/call":
        params = message.get("params", {})
        result = call_tool(params.get("name", ""), params.get("arguments") or {})
    else:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def main():
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            message = json.loads(line)
            output = response(message)
        except (json.JSONDecodeError, TypeError, AttributeError) as error:
            output = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {error}"},
            }
        if output is not None:
            print(json.dumps(output, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
