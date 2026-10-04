#!/usr/bin/env python3
"""사내 시스템을 MCP로 감싸는 최소 패턴을 보여 주는 stdio 서버다.

등록 명령: claude mcp add --scope project hr -- python3 tools/hr_mcp.py
"""

import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

BALANCES = {
    "kim": {"annual": 15, "used": 6},
    "lee": {"annual": 15, "used": 11},
    "park": {"annual": 12, "used": 0},
}

TOOLS = [
    {
        "name": "get_leave_balance",
        "description": "직원의 남은 연차를 조회한다.",
        "inputSchema": {
            "type": "object",
            "properties": {"employee": {"type": "string"}},
            "required": ["employee"],
            "additionalProperties": False,
        },
    },
    {
        "name": "request_leave",
        "description": "직원의 연차 사용을 요청한다.",
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


def leave_balance(employee):
    data = BALANCES.get(employee)
    if data is None:
        return None
    return data["annual"] - data["used"]


def call_tool(name, arguments):
    if name == "get_leave_balance":
        employee = arguments.get("employee", "")
        remaining = leave_balance(employee)
        if remaining is None:
            return text_result(f"직원을 찾을 수 없습니다: {employee}", True)
        data = BALANCES[employee]
        return text_result(
            f"{employee}님의 연차는 총 {data['annual']}일, 사용 {data['used']}일, 잔여 {remaining}일입니다."
        )

    if name == "request_leave":
        employee = arguments.get("employee", "")
        date = arguments.get("date", "")
        days = arguments.get("days")
        remaining = leave_balance(employee)
        if remaining is None:
            return text_result(f"직원을 찾을 수 없습니다: {employee}", True)
        if not isinstance(days, (int, float)) or isinstance(days, bool) or days <= 0:
            return text_result("days는 0보다 큰 숫자여야 합니다.", True)
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
            return text_result("date는 YYYY-MM-DD 형식이어야 합니다.", True)
        try:
            dt.date.fromisoformat(date)
        except ValueError:
            return text_result("유효한 날짜를 입력해 주세요.", True)
        if days > remaining:
            return text_result(f"잔여 연차 {remaining}일보다 많이 요청할 수 없습니다.", True)

        project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))
        record = {"employee": employee, "date": date, "days": days}
        with (project_dir / "hr_requests.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        return text_result(f"{employee}님의 {date} 연차 {days}일 요청을 접수했습니다.")

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
