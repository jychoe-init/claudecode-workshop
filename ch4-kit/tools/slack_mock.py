#!/usr/bin/env python3
"""로컬 Slack 웹훅 모의 서버다.

실행법: python3 tools/slack_mock.py
"""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HOST = "127.0.0.1"
PORT = 8787
LOG_PATH = Path(__file__).resolve().parent.parent / "received.log"


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/":
            self.send_error(404)
            return
        body = "Slack mock 실행 중\n".encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length) or b"{}")
        except (ValueError, json.JSONDecodeError):
            # 상태 줄은 latin-1로 인코딩되므로 사유는 ASCII로 쓴다.
            self.send_error(400, "Bad JSON")
            return
        event = payload.get("hook_event_name", "unknown")
        message = payload.get("last_assistant_message", payload.get("text", ""))
        line = f"[Slack mock] #standup ← {event}: {message}"
        print(line, flush=True)
        with LOG_PATH.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
        body = b"{}"
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    print(f"Slack mock: http://{HOST}:{PORT}", flush=True)
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
