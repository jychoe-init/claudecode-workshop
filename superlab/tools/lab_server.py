#!/usr/bin/env python3
"""로컬 실습 서버 — 공용 사내 API와 같은 응답을 127.0.0.1 에서 낸다.

실행: python3 tools/lab_server.py            (127.0.0.1:8787)
- /v1/*   사내 API (infra/lambda/lab_api.py 와 동일 로직). 토큰은 형식만 맞으면 통과.
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
STORE = lab_api.MemoryStore(tokens=None)


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

    def _dispatch(self, method: str, body):
        status, payload = lab_api.handle(method, self.path.split("?")[0], dict(self.headers), body, STORE)
        self._send(status, json.dumps(payload, ensure_ascii=False).encode())

    def do_GET(self):
        if self.path == "/":
            return self._send(200, "lab server 실행 중 — /v1/me 부터 시작하세요.\n".encode(),
                              "text/plain; charset=utf-8")
        self._dispatch("GET", None)

    def do_POST(self):
        self._dispatch("POST", self._body())

    def log_message(self, fmt, *args):
        return


if __name__ == "__main__":
    print(f"lab server: http://{HOST}:{PORT}  (API /v1/*)", flush=True)
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
