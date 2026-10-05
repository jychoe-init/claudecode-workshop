"""워크샵 사내 API 코어. Lambda 핸들러와 로컬 lab_server.py가 같은 함수를 쓴다.

- 토큰 `lab-xxxxxxxx`(소문자·숫자 8자)로 참가자를 식별한다.
- 조회 데이터(팀·구성원·연차·배포)는 토큰 해시로 결정적으로 만든다. 저장소가 없어도 같은 토큰은 같은 팀을 본다.
- 변경(연차 신청)과 호출 횟수만 Store에 쓴다. Store는 Lambda에서 DynamoDB, 로컬에서 메모리/JSON 파일.
- 로그에는 토큰 앞 4자리만 남긴다.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
from typing import Any, Optional, Protocol

TOKEN_RE = re.compile(r"^lab-[a-z0-9]{8}$")
RATE_LIMIT_PER_MIN = 60
API_VERSION = "2026-10-04"

TEAM_NAMES = ["payments", "checkout", "search", "catalog", "logistics", "crm", "data-platform", "infra",
              "mobile", "growth", "billing", "support-tools", "security", "hr-systems", "analytics",
              "notifications", "identity", "pricing", "fulfillment", "partner-api"]
FIRST_NAMES = ["kim", "lee", "park", "choi", "jung", "kang", "cho", "yoon", "jang", "lim", "han", "oh",
               "seo", "shin", "kwon", "hwang", "ahn", "song", "ryu", "hong"]
ROLES = ["backend", "frontend", "pm", "qa", "data", "sre"]
SERVICES = ["order-api", "web-front", "batch-settlement", "notification-worker", "search-indexer", "admin-console"]
DEPLOY_STATUS = ["healthy", "healthy", "healthy", "degraded", "rolling-back"]


class Store(Protocol):
    def token_exists(self, token: str) -> bool: ...
    def incr_rate(self, token: str, minute_key: str) -> int: ...
    def put_request(self, token: str, item: dict) -> None: ...
    def list_requests(self, token: str) -> list[dict]: ...


def mask(token: str) -> str:
    return (token or "")[:4] + "…"


def _h(token: str, salt: str) -> int:
    return int(hashlib.sha256(f"{salt}:{token}".encode()).hexdigest(), 16)


def team_for(token: str) -> dict:
    h = _h(token, "team")
    team = TEAM_NAMES[h % len(TEAM_NAMES)]
    n_members = 4 + (h >> 8) % 2  # 4~5명
    members, seen = [], set()
    i = 0
    while len(members) < n_members:
        name = FIRST_NAMES[(_h(token, f"m{i}")) % len(FIRST_NAMES)]
        i += 1
        if name in seen:
            continue
        seen.add(name)
        hm = _h(token, f"bal{name}")
        annual = 15 if hm % 3 else 12
        used = hm % (annual - 2)
        members.append({"employee": name, "role": ROLES[hm % len(ROLES)], "annual": annual, "used": used,
                        "remaining": annual - used})
    return {"team": team, "members": members}


def deploys_for(token: str) -> list[dict]:
    h = _h(token, "deploy")
    base = dt.datetime(2026, 10, 1, 9, 0, tzinfo=dt.timezone.utc)
    out = []
    for i, svc in enumerate(SERVICES[: 4 + h % 3]):
        hs = _h(token, f"svc{svc}")
        out.append({
            "service": svc,
            "version": f"v{1 + hs % 9}.{hs % 20}.{(hs >> 4) % 10}",
            "status": DEPLOY_STATUS[hs % len(DEPLOY_STATUS)],
            "deployed_at": (base + dt.timedelta(hours=i * 7 + hs % 5)).isoformat(),
            "deployed_by": FIRST_NAMES[hs % len(FIRST_NAMES)],
        })
    return out


def _resp(status: int, body: Any) -> tuple[int, dict]:
    return status, body


def _err(status: int, code: str, message: str) -> tuple[int, dict]:
    return status, {"error": code, "message": message}


def extract_token(headers: dict) -> Optional[str]:
    auth = ""
    for k, v in (headers or {}).items():
        if k.lower() == "authorization":
            auth = v or ""
            break
    if not auth.startswith("Bearer "):
        return None
    tok = auth[7:].strip()
    return tok if TOKEN_RE.match(tok) else None


def handle(method: str, path: str, headers: dict, body: Optional[str], store: Store,
           now: Optional[dt.datetime] = None) -> tuple[int, dict]:
    """(status, json_body). 경로는 /v1/... 만 받는다."""
    now = now or dt.datetime.now(dt.timezone.utc)
    path = path.rstrip("/") or "/"
    if not path.startswith("/v1/"):
        return _err(404, "not_found", "경로가 없습니다. /v1/me 부터 시작하세요.")

    token = extract_token(headers)
    if not token:
        return _err(401, "unauthorized", "Authorization: Bearer lab-xxxxxxxx 헤더가 필요합니다.")
    if not store.token_exists(token):
        return _err(403, "invalid_token", "등록되지 않은 토큰입니다. 배부받은 토큰을 확인하세요.")

    count = store.incr_rate(token, now.strftime("%Y%m%d%H%M"))
    if count > RATE_LIMIT_PER_MIN:
        return _err(429, "rate_limited", f"분당 {RATE_LIMIT_PER_MIN}회를 넘었습니다. 잠시 후 다시 시도하세요.")

    team = team_for(token)
    parts = path.split("/")[2:]  # ['me'] / ['leave'] / ['leave','kim'] / ['leave','requests'] / ['deploys']

    if method == "GET" and parts == ["me"]:
        return _resp(200, {"token_hint": mask(token), "team": team["team"],
                           "members": [{"employee": m["employee"], "role": m["role"]} for m in team["members"]],
                           "api_version": API_VERSION})
    if method == "GET" and parts == ["leave"]:
        return _resp(200, {"team": team["team"], "as_of": now.date().isoformat(), "balances": team["members"]})
    if method == "GET" and parts == ["leave", "requests"]:
        return _resp(200, {"team": team["team"], "requests": store.list_requests(token)})
    if method == "GET" and len(parts) == 2 and parts[0] == "leave":
        emp = parts[1]
        for m in team["members"]:
            if m["employee"] == emp:
                return _resp(200, {"team": team["team"], **m})
        return _err(404, "unknown_employee", f"{emp}은(는) {team['team']} 팀 구성원이 아닙니다.")
    if method == "GET" and parts == ["deploys"]:
        return _resp(200, {"team": team["team"], "deploys": deploys_for(token)})
    if method == "POST" and parts == ["leave", "requests"]:
        try:
            data = json.loads(body or "{}")
        except json.JSONDecodeError:
            return _err(400, "bad_json", "본문이 JSON이 아닙니다.")
        emp, date, days = data.get("employee"), data.get("date"), data.get("days")
        member = next((m for m in team["members"] if m["employee"] == emp), None)
        if member is None:
            return _err(404, "unknown_employee", f"{emp}은(는) {team['team']} 팀 구성원이 아닙니다.")
        if not isinstance(days, (int, float)) or isinstance(days, bool) or days <= 0:
            return _err(400, "bad_days", "days는 0보다 큰 숫자여야 합니다.")
        try:
            dt.date.fromisoformat(str(date))
        except (TypeError, ValueError):
            return _err(400, "bad_date", "date는 YYYY-MM-DD 형식이어야 합니다.")
        pending = sum(r["days"] for r in store.list_requests(token) if r["employee"] == emp and r["status"] == "pending")
        if days + pending > member["remaining"]:
            return _err(409, "insufficient_balance",
                        f"잔여 {member['remaining']}일(대기 중 {pending}일)보다 많이 신청할 수 없습니다.")
        item = {"request_id": f"REQ-{_h(token + str(now.timestamp()), 'req') % 100000:05d}", "employee": emp,
                "date": str(date), "days": days, "status": "pending", "requested_at": now.isoformat()}
        store.put_request(token, item)
        return _resp(201, item)
    return _err(405 if parts in (["me"], ["leave"], ["deploys"]) else 404, "not_found", "지원하지 않는 경로 또는 메서드입니다.")


class MemoryStore:
    """로컬 lab_server.py 와 테스트용. tokens 가 None 이면 형식만 맞으면 통과."""

    def __init__(self, tokens: Optional[set[str]] = None):
        self.tokens = tokens
        self.rate: dict[str, int] = {}
        self.requests: dict[str, list[dict]] = {}

    def token_exists(self, token: str) -> bool:
        return True if self.tokens is None else token in self.tokens

    def incr_rate(self, token: str, minute_key: str) -> int:
        k = f"{token}#{minute_key}"
        self.rate[k] = self.rate.get(k, 0) + 1
        return self.rate[k]

    def put_request(self, token: str, item: dict) -> None:
        self.requests.setdefault(token, []).append(item)

    def list_requests(self, token: str) -> list[dict]:
        return list(self.requests.get(token, []))
