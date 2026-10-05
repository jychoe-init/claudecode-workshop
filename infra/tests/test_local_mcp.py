"""실제 로컬 HTTP 서버와 MCP stdio를 검증한다. 포트 8787이 비어 있어야 한다."""
import json
import os
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = "http://127.0.0.1:8787"
TOKEN = "lab-test0001"
env = {**os.environ, "LAB_TOKEN": TOKEN, "LAB_API_BASE": BASE, "LAB_USER": "local-validation",
       "PYTHONDONTWRITEBYTECODE": "1"}
with socket.socket() as sock:
    sock.bind(("127.0.0.1", 8787))
server = subprocess.Popen([sys.executable, "-B", "tools/lab_server.py"], cwd=ROOT / "superlab",
                          env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
try:
    for _ in range(100):
        try:
            req = urllib.request.Request(BASE + "/v1/employees?limit=1&offset=1",
                                         headers={"Authorization": "Bearer " + TOKEN})
            with urllib.request.urlopen(req, timeout=1) as response:
                employees = json.load(response)
            break
        except OSError:
            if server.poll() is not None:
                raise RuntimeError("local server exited: " + server.stderr.read())
            time.sleep(.05)
    else:
        raise RuntimeError("local server did not start")
    assert len(employees["employees"]) == 1 and employees["offset"] == 1 and employees["total"] == 120
    messages = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {
            "name": "get_leave_balance", "arguments": {"employee": "김민준"}}},
        {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {
            "name": "get_team_leave", "arguments": {"limit": 1, "offset": 1}}},
        {"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {
            "name": "get_team_leave", "arguments": {"limit": "all"}}},
        {"jsonrpc": "2.0", "id": 6, "method": "tools/call", "params": {
            "name": "request_leave", "arguments": {"employee": "김민준", "date": "2026-10-03",
                                                 "days": .5, "type": "half_pm", "reason": "테스트"}}},
        {"jsonrpc": "2.0", "id": 7, "method": "tools/call", "params": {
            "name": "get_leave_requests", "arguments": {"requested_by": "local-validation", "limit": "all"}}},
        {"jsonrpc": "2.0", "id": 8, "method": "tools/call", "params": {
            "name": "request_leave", "arguments": {"employee": "이지은", "date": "2026-10-20", "days": 1}}},
        {"jsonrpc": "2.0", "id": 9, "method": "tools/call", "params": {
            "name": "get_sent_mail", "arguments": {"mailbox": "hr", "limit": 1}}},
        {"jsonrpc": "2.0", "id": 10, "method": "tools/call", "params": {
            "name": "get_events", "arguments": {"mailbox": "sales", "limit": "all"}}},
    ]
    run = subprocess.run([sys.executable, "-B", "tools/hr_mcp.py"], cwd=ROOT / "superlab", env=env,
                         input="".join(json.dumps(m, ensure_ascii=False) + "\n" for m in messages),
                         capture_output=True, text=True, timeout=30, check=True)
    assert not run.stderr, run.stderr
    results = {m["id"]: m["result"] for m in map(json.loads, run.stdout.splitlines())}
    assert len(results) == 10
    assert results[1]["serverInfo"]["name"] == "hr"
    assert results[1]["protocolVersion"] == "2025-06-18"
    assert len(results[2]["tools"]) == 6
    text = lambda i: results[i]["content"][0]["text"]
    assert "김민준 과장(그로스팀)" in text(3) and "사용 내역:" in text(3) and "2/19" in text(3)
    page = json.loads(text(4))
    assert len(page["balances"]) == 1 and page["balances"][0]["employee"] == "이지은" and page["next_offset"] == 2
    assert len(json.loads(text(5))["balances"]) == 8
    assert "0.5일" in text(6) and "REQ-" in text(6) and "경고:" in text(6)
    requests = json.loads(text(7))
    assert requests["total"] == 1 and requests["requests"][0]["days"] == .5
    assert requests["requests"][0]["requested_by"] == "local-validation"
    assert results[8]["isError"] and "insufficient_balance" in text(8)
    assert len(json.loads(text(9))["value"]) == 1
    assert len(json.loads(text(10))["value"]) == 7
    print("PASS local HTTP query + MCP initialize, six tools, Korean balance/dates, limit/all, half-day POST, author filter, warnings, insufficient balance, mail/calendar")
finally:
    server.terminate()
    try:
        server.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        server.kill()
        server.communicate()
