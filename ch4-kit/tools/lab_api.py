"""워크샵 사내 API 코어. Lambda 핸들러와 로컬 lab_server.py가 같은 함수를 쓴다.

- 토큰 `lab-xxxxxxxx`(소문자·숫자 8자)로 참가자를 식별한다.
- 조회 데이터(팀·구성원·연차·배포·보낸 메일·일정)는 토큰 해시로 결정적으로 만든다. 저장소가 없어도 같은 토큰은 같은 팀을 본다.
- 연차 신청과 호출 횟수만 Store에 쓴다. Store는 Lambda에서 DynamoDB, 로컬에서 메모리.
- 실습은 공통 토큰 하나를 함께 쓴다. 신청 목록에는 모두의 신청이 최근 순으로 보이고, 잔여 검사는 신청 한 건 기준이라 서로 막지 않는다.
- 로그에는 토큰 앞 4자리만 남긴다.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
from typing import Any, Optional, Protocol

TOKEN_RE = re.compile(r"^lab-[a-z0-9]{8}$")
RATE_LIMIT_PER_MIN = 3000  # 실습은 공통 토큰 하나를 70명이 함께 쓴다
REQUESTS_SHOWN = 20
API_VERSION = "2026-10-05"

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
    def list_requests(self, token: str) -> list[dict]: ...  # 최근 순 REQUESTS_SHOWN건


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


KST = dt.timezone(dt.timedelta(hours=9))
MAIL_TEMPLATES = [
    ("[{team}] {svc} {ver} 배포 완료 공유",
     "{svc} {ver} 배포를 마쳤습니다. 오류율이 {a}% → {b}%로 낮아졌습니다. 롤백 계획은 그대로 유지합니다."),
    ("{m}님, {svc} 장애 회고 일정 확인 부탁드립니다",
     "이번 주 {svc} 응답 지연(최대 {x}분) 회고를 금요일에 하려 합니다. 원인은 커넥션 풀 고갈로 보입니다."),
    ("[요청] {svc} 알람 임계치 변경 승인",
     "{svc} 응답시간 알람 임계치를 {p}ms → {q}ms로 올리려 합니다. 운영팀 승인이 필요합니다."),
    ("{team} 주간 회의록 공유",
     "이번 주 정례 회의에서 다음 분기 우선순위 3건을 확정했습니다. 담당자 배정은 다음 주 월요일까지 마칩니다."),
    ("{m}님 온보딩 계정 발급 완료",
     "신규 입사자 계정 발급과 저장소 권한 부여를 마쳤습니다. 보안 교육은 다음 주 화요일로 예약했습니다."),
    ("Re: 협력사 API 연동 일정",
     "협력사 테스트 환경이 다음 주 수요일에 열린다고 합니다. 연동 테스트는 그 뒤로 잡겠습니다. 일정이 밀리면 지원이 필요합니다."),
    ("[공유] 회귀 테스트 자동화 결과",
     "{svc} 회귀 테스트 {n}건을 자동화해 실행 시간이 {t1}분 → {t2}분으로 줄었습니다."),
    ("예산 승인 요청: 부하 테스트 환경",
     "다음 주 {svc} 부하 테스트 {k}개 시나리오를 돌리려면 임시 환경 비용 승인이 필요합니다."),
]
EVENT_TEMPLATES = [  # (제목, 오늘 기준 일 차이, 시작 시, 길이 분, 장소)
    ("{team} 주간 정례", -6, 10, 60, "회의실 A"),
    ("{svc} 장애 회고", -4, 14, 60, "온라인"),
    ("1:1 ({m})", -3, 16, 30, "온라인"),
    ("다음 분기 로드맵 리뷰", -1, 11, 90, "회의실 B"),
    ("{team} 주간 정례", 1, 10, 60, "회의실 A"),
    ("협력사 API 연동 킥오프", 2, 15, 60, "온라인"),
    ("{svc} 부하 테스트 리허설", 4, 13, 120, "회의실 C"),
]


def _addr(name: str, team: str) -> dict:
    return {"emailAddress": {"name": name, "address": f"{name}@{team}.example.com"}}


def _fill(text: str, token: str, key: str, team: str, members: list[dict]) -> str:
    h = _h(token, f"fill{key}")
    return text.format(team=team, svc=SERVICES[h % len(SERVICES)], m=members[(h >> 4) % len(members)]["employee"],
                       ver=f"v{1 + h % 9}.{h % 20}.{(h >> 4) % 10}", a=2 + h % 5, b=h % 2,
                       x=3 + h % 12, p=300 + 100 * (h % 4), q=800 + 100 * (h % 5),
                       n=10 + h % 30, t1=15 + h % 10, t2=8 + h % 5, k=2 + h % 3)


def mail_for(token: str, now: dt.datetime) -> list[dict]:
    """최근 6일간 보낸 메일 6통. Microsoft Graph message 리소스의 필드 이름을 따른다."""
    team = team_for(token)
    name, members = team["team"], team["members"]
    today = now.astimezone(KST).replace(hour=0, minute=0, second=0, microsecond=0)
    start = _h(token, "mail") % len(MAIL_TEMPLATES)
    out = []
    for j in range(6):  # 하루 전 ~ 엿새 전, 하루 한 통
        i = (start + j) % len(MAIL_TEMPLATES)
        subject, preview = MAIL_TEMPLATES[i]
        hs = _h(token, f"mail{i}")
        sent = today - dt.timedelta(days=j + 1) + dt.timedelta(hours=9 + hs % 9, minutes=hs % 60)
        out.append({
            "id": f"AAMk-{hs % 10**8:08d}",
            "subject": _fill(subject, token, f"m{i}", name, members),
            "sentDateTime": sent.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "from": _addr("me", name),
            "toRecipients": [_addr(members[hs % len(members)]["employee"], name)],
            "bodyPreview": _fill(preview, token, f"m{i}", name, members),
            "importance": "high" if subject.startswith(("[요청]", "예산")) else "normal",
        })
    return out


def events_for(token: str, now: dt.datetime) -> list[dict]:
    """오늘 기준 6일 전 ~ 4일 뒤 일정. Microsoft Graph event 리소스의 필드 이름을 따른다."""
    team = team_for(token)
    name, members = team["team"], team["members"]
    today = now.astimezone(KST).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
    out = []
    for i, (subject, day, hour, minutes, place) in enumerate(EVENT_TEMPLATES):
        hs = _h(token, f"event{i}")
        start = today + dt.timedelta(days=day, hours=hour)
        attendees = dict.fromkeys(members[(hs >> k) % len(members)]["employee"] for k in range(3))
        out.append({
            "id": f"AAMkE-{hs % 10**8:08d}",
            "subject": _fill(subject, token, f"e{i}", name, members),
            "start": {"dateTime": start.strftime("%Y-%m-%dT%H:%M:%S"), "timeZone": "Asia/Seoul"},
            "end": {"dateTime": (start + dt.timedelta(minutes=minutes)).strftime("%Y-%m-%dT%H:%M:%S"),
                    "timeZone": "Asia/Seoul"},
            "location": {"displayName": place},
            "organizer": _addr("me", name),
            "attendees": [{**_addr(a, name), "type": "required"} for a in attendees],
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
    if method == "GET" and parts == ["mail", "sent"]:
        return _resp(200, {"value": mail_for(token, now)})
    if method == "GET" and parts == ["calendar"]:
        return _resp(200, {"value": events_for(token, now)})
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
        if days > member["remaining"]:
            return _err(409, "insufficient_balance", f"잔여 {member['remaining']}일보다 많이 신청할 수 없습니다.")
        item = {"request_id": f"REQ-{_h(token + str(now.timestamp()), 'req') % 100000:05d}", "employee": emp,
                "date": str(date), "days": days, "status": "pending", "requested_at": now.isoformat()}
        store.put_request(token, item)
        return _resp(201, item)
    return _err(405 if parts in (["me"], ["leave"], ["deploys"], ["mail", "sent"], ["calendar"]) else 404, "not_found", "지원하지 않는 경로 또는 메서드입니다.")


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
        return self.requests.get(token, [])[::-1][:REQUESTS_SHOWN]
