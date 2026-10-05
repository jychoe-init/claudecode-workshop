"""lab_api 단위 테스트: python3 infra/tests/test_lab_api.py"""
import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lambda"))
import lab_api  # noqa: E402

T1, T2 = "lab-a1b2c3d4", "lab-zz99yy88"
H = lambda t: {"Authorization": f"Bearer {t}"}  # noqa: E731
NOW = dt.datetime(2026, 10, 20, 9, 0, tzinfo=dt.timezone.utc)
fails = 0


def check(name, cond, note=""):
    global fails
    fails += 0 if cond else 1
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {note}")


store = lab_api.MemoryStore(tokens={T1, T2})

# 인증
check("헤더 없음 → 401", lab_api.handle("GET", "/v1/me", {}, None, store, NOW)[0] == 401)
check("형식 틀린 토큰 → 401", lab_api.handle("GET", "/v1/me", H("lab-SHORT"), None, store, NOW)[0] == 401)
check("미등록 토큰 → 403", lab_api.handle("GET", "/v1/me", H("lab-00000000"), None, store, NOW)[0] == 403)
check("/v1 밖 경로 → 404", lab_api.handle("GET", "/docs", H(T1), None, store, NOW)[0] == 404)

# 결정성·격리
s1, me1 = lab_api.handle("GET", "/v1/me", H(T1), None, store, NOW)
s2, me1b = lab_api.handle("GET", "/v1/me", H(T1), None, store, NOW)
_, me2 = lab_api.handle("GET", "/v1/me", H(T2), None, store, NOW)
check("/v1/me 200", s1 == 200, me1.get("team"))
check("같은 토큰 → 같은 팀·구성원", me1 == me1b)
check("다른 토큰 → 다른 데이터", me1["team"] != me2["team"] or me1["members"] != me2["members"])
check("token_hint 앞 4자리만", me1["token_hint"] == "lab-…")
check("구성원 4~5명, 중복 없음", 4 <= len(me1["members"]) <= 5 and len({m["employee"] for m in me1["members"]}) == len(me1["members"]))

# 조회
s, lv = lab_api.handle("GET", "/v1/leave", H(T1), None, store, NOW)
check("/v1/leave 잔여 = annual - used", s == 200 and all(b["remaining"] == b["annual"] - b["used"] for b in lv["balances"]))
emp = lv["balances"][0]["employee"]
s, one = lab_api.handle("GET", f"/v1/leave/{emp}", H(T1), None, store, NOW)
check("/v1/leave/{직원} 200", s == 200 and one["employee"] == emp)
check("남의 팀 직원 → 404", lab_api.handle("GET", "/v1/leave/nobody", H(T1), None, store, NOW)[0] == 404)
s, dp = lab_api.handle("GET", "/v1/deploys", H(T1), None, store, NOW)
check("/v1/deploys 4~6건, 필드 5개", s == 200 and 4 <= len(dp["deploys"]) <= 6 and set(dp["deploys"][0]) == {"service", "version", "status", "deployed_at", "deployed_by"})

# 신청
rem = one["remaining"]
post = lambda b: lab_api.handle("POST", "/v1/leave/requests", H(T1), json.dumps(b), store, NOW)  # noqa: E731
check("정상 신청 → 201 pending", post({"employee": emp, "date": "2026-10-30", "days": 1})[0] == 201)
check("잔여만큼 신청 → 201 (앞 신청이 쌓이지 않음)", post({"employee": emp, "date": "2026-10-31", "days": rem})[0] == 201)
check("잔여 초과 → 409", post({"employee": emp, "date": "2026-10-31", "days": rem + 1})[0] == 409, f"잔여 {rem}")
check("날짜 형식 → 400", post({"employee": emp, "date": "10/30", "days": 1})[0] == 400)
check("days 0 → 400", post({"employee": emp, "date": "2026-10-30", "days": 0})[0] == 400)
check("본문 깨짐 → 400", lab_api.handle("POST", "/v1/leave/requests", H(T1), "{", store, NOW)[0] == 400)
s, reqs = lab_api.handle("GET", "/v1/leave/requests", H(T1), None, store, NOW)
check("신청 목록: 넣은 2건, 최근 순", s == 200 and [r["days"] for r in reqs["requests"]] == [rem, 1])
check("다른 토큰에는 안 보임", lab_api.handle("GET", "/v1/leave/requests", H(T2), None, store, NOW)[1]["requests"] == [])
many = lab_api.MemoryStore(tokens={T1})
for _ in range(lab_api.REQUESTS_SHOWN + 5):
    lab_api.handle("POST", "/v1/leave/requests", H(T1), json.dumps({"employee": emp, "date": "2026-10-30", "days": 1}), many, NOW)
check(f"목록은 최근 {lab_api.REQUESTS_SHOWN}건만", len(lab_api.handle("GET", "/v1/leave/requests", H(T1), None, many, NOW)[1]["requests"]) == lab_api.REQUESTS_SHOWN)
check("GET /v1/leave/requests 에 POST 외 메서드 → 404/405", lab_api.handle("DELETE", "/v1/leave", H(T1), None, store, NOW)[0] in (404, 405))

# 레이트리밋
fresh = lab_api.MemoryStore(tokens={T2})
codes = [lab_api.handle("GET", "/v1/me", H(T2), None, fresh, NOW)[0] for _ in range(lab_api.RATE_LIMIT_PER_MIN + 2)]
check(f"{lab_api.RATE_LIMIT_PER_MIN}회 후 429", codes[:lab_api.RATE_LIMIT_PER_MIN].count(200) == lab_api.RATE_LIMIT_PER_MIN and codes[-1] == 429)
later = NOW + dt.timedelta(minutes=1)
check("다음 분에는 다시 200", lab_api.handle("GET", "/v1/me", H(T2), None, fresh, later)[0] == 200)

# 보낸 메일·일정 (Graph 필드 이름)
ms = lab_api.MemoryStore(tokens={T1, T2})
s, mail = lab_api.handle("GET", "/v1/mail/sent", H(T1), None, ms, NOW)
msgs = mail["value"]
check("/v1/mail/sent 200, 6통", s == 200 and len(msgs) == 6)
check("메일 필드 = Graph message", all({"id", "subject", "sentDateTime", "from", "toRecipients", "bodyPreview",
                                        "importance"} <= set(m) for m in msgs))
check("메일은 지난 7일 안, 미래 없음", all(NOW - dt.timedelta(days=7) <= dt.datetime.fromisoformat(
    m["sentDateTime"].replace("Z", "+00:00")) < NOW for m in msgs))
check("메일 수신자는 내 팀 구성원", all(r["emailAddress"]["name"] in {x["employee"] for x in me1["members"]}
                                  for m in msgs for r in m["toRecipients"]))
check("메일 본문에 채워지지 않은 {} 없음", not any("{" in m["subject"] + m["bodyPreview"] for m in msgs))
check("같은 토큰·같은 날 → 같은 메일", mail == lab_api.handle("GET", "/v1/mail/sent", H(T1), None, ms, NOW)[1])
check("다른 토큰 → 다른 메일", mail != lab_api.handle("GET", "/v1/mail/sent", H(T2), None, ms, NOW)[1])
s, cal = lab_api.handle("GET", "/v1/calendar", H(T1), None, ms, NOW)
evs = cal["value"]
check("/v1/calendar 200, 지난 일정·다가올 일정 둘 다", s == 200 and any(
    e["start"]["dateTime"] < "2026-10-20" for e in evs) and any(e["start"]["dateTime"] > "2026-10-21" for e in evs))
check("일정 필드 = Graph event", all({"id", "subject", "start", "end", "location", "organizer", "attendees"} <= set(e)
                                    and e["start"]["timeZone"] == "Asia/Seoul" and e["end"]["dateTime"] > e["start"]["dateTime"]
                                    for e in evs))
check("일정 참석자 중복 없음", all(len({a["emailAddress"]["name"] for a in e["attendees"]}) == len(e["attendees"]) for e in evs))
check("POST /v1/mail/sent → 405", lab_api.handle("POST", "/v1/mail/sent", H(T1), "{}", ms, NOW)[0] == 405)
check("미등록 토큰은 메일도 403", lab_api.handle("GET", "/v1/mail/sent", H("lab-00000000"), None, ms, NOW)[0] == 403)

# 제거된 경로는 404
check("/v1/notify 는 404", lab_api.handle("POST", "/v1/notify", H(T1), "{}", lab_api.MemoryStore(tokens={T1}), NOW)[0] == 404)
check("/v1/slack/link 는 404", lab_api.handle("POST", "/v1/slack/link", H(T1), "{}", lab_api.MemoryStore(tokens={T1}), NOW)[0] == 404)

print(f"\nFAIL {fails}")
sys.exit(1 if fails else 0)
