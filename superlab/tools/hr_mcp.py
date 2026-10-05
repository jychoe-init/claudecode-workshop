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
PAGE_ARGS = {
    "limit": {"anyOf": [{"type": "integer", "minimum": 1, "maximum": 100}, {"type": "string", "enum": ["all"]}],
              "description": "한 페이지 건수. 기본 20건, all은 필터에 맞는 전체(신청은 최근 500건 안에서)"},
    "offset": {"type": "integer", "minimum": 0, "description": "다음 페이지는 응답의 next_offset을 사용"},
}
MAILBOX_ARG = {"type": "object", "properties": {"mailbox": {
    "type": "string", "enum": ["planning", "sales", "cs", "hr"],
    "description": "실습 메일함(직무). planning 기획·운영(기본), sales 영업, cs CS, hr 인사"}, **PAGE_ARGS}, "additionalProperties": False}

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
        "description": "팀 전원의 연차 현황을 조회한다(그로스팀, 기준일, 직위·소속·발생·이월·사용·예정·승인 대기·잔여·날짜별 기록).",
        "inputSchema": {"type": "object", "properties": dict(PAGE_ARGS), "additionalProperties": False},
    },
    {
        "name": "get_leave_requests",
        "description": "최근 500건 안에서 연차 신청 내역을 필터·페이지 조회한다(기본 20건). next_offset이 있으면 다음 페이지가 있다. 같은 토큰을 쓰는 참가자들의 신청이 함께 보인다.",
        "inputSchema": {"type": "object", "properties": {**PAGE_ARGS,
            "employee": {"type": "string", "description": "직원 이름·사번·메일 아이디"},
            "status": {"type": "string", "enum": ["pending", "approved"]},
            "requested_by": {"type": "string", "maxLength": 30},
            "team": {"type": "string", "description": "팀 코드 또는 이름"}},
            "additionalProperties": False},
    },
    {
        "name": "get_leave_balance",
        "description": "직원 한 명의 연차 발생·이월·사용·예정·승인 대기·잔여와 사용 날짜를 조회한다.",
        "inputSchema": {
            "type": "object",
            "properties": {"employee": {"type": "string", "description": "직원 이름(예: 김민준), 사번, 영문 이름 또는 메일 아이디"}},
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
                "employee": {"type": "string", "description": "직원 이름(예: 김민준), 사번, 영문 이름 또는 메일 아이디"},
                "date": {"type": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}$"},
                "days": {"type": "number", "exclusiveMinimum": 0},
                "type": {"type": "string", "enum": ["annual", "half_am", "half_pm", "quarter", "sick", "official", "family_event", "refresh", "parental"], "description": "휴가 종류. 기본 annual, 반차 0.5일, 반반차 0.25일"},
                "reason": {"type": "string", "maxLength": 100},
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
    if os.environ.get("LAB_USER"):
        headers["X-Lab-User"] = os.environ["LAB_USER"]
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
    def query_path(path, keys):
        query = urllib.parse.urlencode({k: arguments[k] for k in keys if k in arguments})
        return path + ("?" + query if query else "")

    if name in GRAPH_TOOLS:
        mailbox = urllib.parse.quote(str(arguments.get("mailbox") or "planning"), safe="")
        data, error = api_request("GET", query_path(GRAPH_TOOLS[name].format(mailbox), PAGE_ARGS))
        if error:
            return error
        return text_result(json.dumps(data, ensure_ascii=False))

    if name == "get_team_leave":
        data, error = api_request("GET", query_path("/v1/leave", PAGE_ARGS))
        if error:
            return error
        return text_result(json.dumps(data, ensure_ascii=False))

    if name == "get_leave_requests":
        data, error = api_request("GET", query_path("/v1/leave/requests",
                                                  (*PAGE_ARGS, "employee", "status", "requested_by", "team")))
        if error:
            return error
        return text_result(json.dumps(data, ensure_ascii=False))

    if name == "get_leave_balance":
        employee = str(arguments.get("employee", ""))
        path = "/v1/leave/" + urllib.parse.quote(employee, safe="")
        data, error = api_request("GET", path)
        if error:
            return error
        labels = {"annual": "연차", "half_am": "오전 반차", "half_pm": "오후 반차", "quarter": "반반차"}
        # API와 같은 업무 달력으로 진행 중 기록도 기준일까지 날짜별로 나눈다.
        from lab_company import business_dates
        details = []
        for record in data.get("history", []):
            if record["status"] != "approved" or record["type"] not in labels:
                continue
            left = record["days"]
            for day in business_dates(record["start"], record["end"]):
                amount = min(1, left)
                left -= amount
                if amount > 0 and day.isoformat() <= data["as_of"]:
                    details.append(f"{day.month}/{day.day} {labels[record['type']]} {amount:g}일")
        usage = ", ".join(details) or "없음"
        return text_result(
            f"{data['employee']} {data['title']}({data['team_name'] or '팀 미소속'})의 올해 연차는 "
            f"총 {data['total']:g}일(발생 {data['annual']:g} + 이월 {data['carried_over']:g}), "
            f"사용 {data['used']:g}일 · 예정 {data['scheduled']:g}일 · 승인 대기 {data['pending']:g}일 · "
            f"잔여 {data['remaining']:g}일입니다. 사용 내역: {usage}"
        )

    if name == "request_leave":
        payload = {
            "employee": arguments.get("employee"),
            "date": arguments.get("date"),
            "days": arguments.get("days"),
        }
        for key in ("type", "reason"):
            if key in arguments:
                payload[key] = arguments[key]
        data, error = api_request("POST", "/v1/leave/requests", payload)
        if error:
            return error
        warnings = " ".join(w["message"] for w in data.get("warnings", []))
        return text_result(
            f"{data['employee']}님의 {data['date']} {data.get('type_label', '연차')} {data['days']}일 신청을 접수했습니다. "
            f"신청 ID {data['request_id']}, 상태 {data['status']}."
            + (f" 경고: {warnings}" if warnings else "")
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
            "serverInfo": {"name": "hr", "version": "2026-10-06"},
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
