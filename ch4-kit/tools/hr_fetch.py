#!/usr/bin/env python3
"""사내 API 조회 전용 클라이언트 — 스킬 첫 줄에서 `!`python3 tools/hr_fetch.py leave`` 로 주입한다.

사용: python3 tools/hr_fetch.py me | leave | leave <직원> | requests | deploys
환경: LAB_TOKEN (필수, .claude/settings.local.json 의 env), LAB_API_BASE (선택, 기본은 공용 주소)
이 스크립트는 GET 만 한다. 변경(신청)은 하지 않는다 — 조회 전용이어야 allow 로 둘 수 있다.
"""
import json
import os
import sys
import urllib.error
import urllib.request

DEFAULT_BASE = "https://REPLACE-AFTER-DEPLOY.cloudfront.net"  # Stage 2 배포 후 실제 주소로 바뀐다
PATHS = {"me": "/v1/me", "leave": "/v1/leave", "requests": "/v1/leave/requests", "deploys": "/v1/deploys"}


def main(argv):
    if not argv or argv[0] not in PATHS:
        print(json.dumps({"error": "usage", "message": "me | leave | leave <직원> | requests | deploys"}, ensure_ascii=False))
        return 2
    path = PATHS[argv[0]]
    if argv[0] == "leave" and len(argv) > 1:
        path = f"/v1/leave/{argv[1]}"
    token = os.environ.get("LAB_TOKEN", "")
    base = os.environ.get("LAB_API_BASE", DEFAULT_BASE).rstrip("/")
    if not token:
        print(json.dumps({"error": "no_token", "message": "LAB_TOKEN 이 없습니다. bash tools/setup.sh 로 토큰을 등록하세요."}, ensure_ascii=False))
        return 2
    req = urllib.request.Request(base + path, headers={"Authorization": f"Bearer {token}", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            print(r.read().decode("utf-8"))
            return 0
    except urllib.error.HTTPError as e:
        print(e.read().decode("utf-8", "replace") or json.dumps({"error": f"http_{e.code}"}))
        return 1
    except (urllib.error.URLError, TimeoutError) as e:
        print(json.dumps({"error": "unreachable", "message": f"{base} 에 연결하지 못했습니다. LAB_API_BASE=http://127.0.0.1:8787 로 바꾸고 python3 tools/lab_server.py 를 켜세요.", "detail": str(e)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
