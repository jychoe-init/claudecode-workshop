#!/usr/bin/env python3
"""로컬 실습 서버 — 공용 API와 같은 응답 + Slack 수신기.

실행: python3 tools/lab_server.py            (127.0.0.1:8787)
- /v1/*            사내 API (infra/lambda/lab_api.py 와 동일 로직). 토큰은 형식만 맞으면 통과.
- POST /v1/notify   Slack DM 대신 received.log 에 기록 (공용 API 가 막혔을 때 대체)
- POST /slack/<채널>  Stop 훅 수신. received.log 에 한 줄 기록.
공용 API가 막혔을 때 LAB_API_BASE=http://127.0.0.1:8787 로 바꾸면 스킬이 그대로 동작한다.
"""
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lab_api  # noqa: E402  (tools/lab_api.py — infra/lambda/lab_api.py 와 동일 파일)

HOST, PORT = "127.0.0.1", 8787
LOG_PATH = HERE.parent / "received.log"
STORE = lab_api.MemoryStore(tokens=None)
NOTIFIER = lab_api.LogNotifier(log_path=str(LOG_PATH))  # /v1/notify 는 Slack 대신 received.log 에 기록


class Handler(BaseHTTPRequestHandler):
    def _send(self, status, body: bytes, ctype="application/json; charset=utf-8"):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        n = int(self.headers.get("Content-Length", "0") or 0)
        return self.rfile.read(n).decode("utf-8", "replace") if n else ""

    def do_GET(self):
        if self.path == "/":
            return self._send(200, "lab server 실행 중 — /v1/me, /slack/<채널>\n".encode(), "text/plain; charset=utf-8")
        status, payload = lab_api.handle("GET", self.path.split("?")[0], dict(self.headers), None, STORE, notifier=NOTIFIER)
        self._send(status, json.dumps(payload, ensure_ascii=False).encode())

    def do_POST(self):
        body = self._body()
        if self.path.startswith("/slack/"):
            channel = self.path[len("/slack/"):] or "general"
            try:
                payload = json.loads(body or "{}")
            except json.JSONDecodeError:
                return self._send(400, b'{"error":"bad_json"}')
            text = payload.get("last_assistant_message") or payload.get("text") or ""
            line = f"[Slack mock] #{channel} <- {payload.get('hook_event_name', 'message')}: {text}"
            print(line, flush=True)
            with LOG_PATH.open("a", encoding="utf-8") as fh:
                fh.write(line + "\n")
            return self._send(200, b"{}")
        status, payload = lab_api.handle("POST", self.path.split("?")[0], dict(self.headers), body, STORE, notifier=NOTIFIER)
        self._send(status, json.dumps(payload, ensure_ascii=False).encode())

    def log_message(self, fmt, *args):
        return


if __name__ == "__main__":
    print(f"lab server: http://{HOST}:{PORT}  (API /v1/*, Slack mock /slack/<채널>)", flush=True)
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
