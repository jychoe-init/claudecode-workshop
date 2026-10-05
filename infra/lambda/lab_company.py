"""superlab의 결정적 Mock 회사·조직·휴가 데이터. 시간에 따른 상태는 조회 시 계산한다."""
from __future__ import annotations

import calendar
import copy
import datetime as dt
import random
from functools import lru_cache

KST = dt.timezone(dt.timedelta(hours=9))
MY_TEAM = "growth"
YEARS = (2025, 2026)
DIVISIONS = {"executive": "경영진", "product": "제품개발부문", "business": "사업부문", "corporate": "경영지원부문"}
TEAMS = [
    ("ceo-office", "대표이사실", "executive", 1),
    ("platform", "플랫폼팀", "product", 11), ("payments", "결제팀", "product", 9),
    ("frontend", "프론트엔드팀", "product", 8), ("data", "데이터팀", "product", 10),
    ("growth", "그로스팀", "product", 8),
    ("planning", "사업기획팀", "business", 8), ("sales1", "영업1팀", "business", 10),
    ("sales2", "영업2팀", "business", 8), ("marketing", "마케팅팀", "business", 8),
    ("cs", "고객지원팀", "business", 12),
    ("hr", "인사팀", "corporate", 7), ("finance", "재무팀", "corporate", 7),
    ("legal", "법무팀", "corporate", 4), ("general", "총무팀", "corporate", 5),
]
OFFICES = {
    "hq": {"code": "hq", "name": "서울 본사", "address": "서울특별시 강남구 테헤란로 152, 슈퍼랩 오피스 12층", "zip": "06236"},
    "pangyo": {"code": "pangyo", "name": "판교 연구소", "address": "경기도 성남시 분당구 판교역로 166, 슈퍼랩 오피스 8층", "zip": "13529"},
    "busan": {"code": "busan", "name": "부산지사", "address": "부산광역시 해운대구 센텀중앙로 90, 슈퍼랩 오피스 6층", "zip": "48059"},
}
# 워크샵의 고정 업무 달력. 2025 노동절도 민간 사업장 유급휴일로 제외한다.
HOLIDAY_DATA = {
    2025: {"01-01": "신정", "01-27": "임시공휴일", "01-28": "설날 연휴", "01-29": "설날", "01-30": "설날 연휴",
           "03-01": "삼일절", "03-03": "삼일절 대체공휴일", "05-01": "근로자의 날", "05-05": "어린이날·부처님오신날",
           "05-06": "대체공휴일", "06-03": "대통령 선거일", "06-06": "현충일", "08-15": "광복절", "10-03": "개천절",
           "10-05": "추석 연휴", "10-06": "추석", "10-07": "추석 연휴", "10-08": "추석 대체공휴일", "10-09": "한글날", "12-25": "성탄절"},
    2026: {"01-01": "신정", "02-16": "설날 연휴", "02-17": "설날", "02-18": "설날 연휴", "03-01": "삼일절",
           "03-02": "삼일절 대체공휴일", "05-01": "노동절", "05-05": "어린이날", "05-24": "부처님오신날",
           "05-25": "부처님오신날 대체공휴일", "06-03": "전국동시지방선거일", "06-06": "현충일", "07-17": "제헌절",
           "08-15": "광복절", "08-17": "광복절 대체공휴일", "09-24": "추석 연휴", "09-25": "추석", "09-26": "추석 연휴",
           "10-03": "개천절", "10-05": "개천절 대체공휴일", "10-09": "한글날", "12-25": "성탄절"},
    # 육아휴직 종료일(2027-05-31)까지 일수 계산에 필요한 업무 달력.
    2027: {"01-01": "신정", "02-06": "설날 연휴", "02-07": "설날", "02-08": "설날 연휴", "02-09": "설날 대체공휴일",
           "03-01": "삼일절", "05-01": "노동절", "05-05": "어린이날", "05-13": "부처님오신날"},
}
LEAVE_TYPES = {
    "annual": ("연차", True, 1), "half_am": ("오전 반차", True, .5),
    "half_pm": ("오후 반차", True, .5), "quarter": ("반반차", True, .25),
    "sick": ("병가", False, 1), "official": ("공가", False, 1),
    "family_event": ("경조휴가", False, 1), "refresh": ("리프레시 휴가", False, 1), "parental": ("육아휴직", False, 1),
}
STATUS_LABELS = {"approved": "승인", "pending": "승인 대기", "rejected": "반려", "cancelled": "취소"}
ROLE_LABELS = {"backend": "백엔드 개발", "frontend": "프론트엔드 개발", "data": "데이터 분석", "pm": "프로덕트 매니저",
               "qa": "품질 관리", "sre": "서비스 운영", "planning": "사업기획", "sales": "영업", "marketing": "마케팅",
               "cs": "고객지원", "hr": "인사", "finance": "재무", "legal": "법무", "general": "총무",
               "ceo": "대표이사", "division_head": "부문장", "secretary": "비서실장"}
SURNAMES = [("김", "kim"), ("이", "lee"), ("박", "park"), ("최", "choi"), ("정", "jung"), ("강", "kang"),
            ("조", "cho"), ("윤", "yoon"), ("장", "jang"), ("임", "lim"), ("한", "han"), ("오", "oh"),
            ("서", "seo"), ("신", "shin"), ("권", "kwon"), ("황", "hwang"), ("안", "ahn"), ("송", "song")]
GIVEN = [("민준", "minjun"), ("서연", "seoyeon"), ("지호", "jiho"), ("수빈", "subin"), ("지우", "jiwoo"),
         ("현우", "hyunwoo"), ("하린", "harin"), ("도윤", "doyoon"), ("서아", "seoa"), ("유진", "yujin"),
         ("지훈", "jihoon"), ("수현", "suhyun"), ("예린", "yerin"), ("준서", "junseo"), ("은서", "eunseo"),
         ("태현", "taehyun"), ("채원", "chaewon"), ("시우", "siwoo"), ("하은", "haeun"), ("지민", "jimin")]
GROWTH_NAMES = [("김민준", "minjun", "kim"), ("이지은", "jieun", "lee"), ("박서준", "seojun", "park"),
                ("최수빈", "subin", "choi"), ("정하린", "harin", "jung"), ("강도윤", "doyoon", "kang"),
                ("윤서아", "seoa", "yoon"), ("한유진", "yujin", "han")]


def rng(key):
    return random.Random(f"superlab-2026:{key}")


def today_at(now):
    return now.astimezone(KST).date()


def iso_date(value):
    return dt.date.fromisoformat(value) if isinstance(value, str) else value


def business_day(day):
    day = iso_date(day)
    return day.weekday() < 5 and day.strftime("%m-%d") not in HOLIDAY_DATA.get(day.year, {})


@lru_cache(maxsize=8192)
def business_dates(start, end):
    start, end = iso_date(start), iso_date(end)
    return tuple(start + dt.timedelta(days=n) for n in range(max(0, (end - start).days + 1))
                 if business_day(start + dt.timedelta(days=n)))


def end_for(start, days):
    """신청 시작일은 보존하고, 그날 이후의 영업일에 일수를 배분한다."""
    day = iso_date(start)
    left = days
    while True:
        if business_day(day):
            left -= min(1, left)
        if left <= 0:
            return day.isoformat()
        day += dt.timedelta(days=1)


def units(record):
    left = record["days"]
    for day in business_dates(record["start"], record["end"]):
        if left <= 0:
            break
        amount = min(1, left)
        yield day, amount
        left -= amount


@lru_cache(maxsize=1)
def company_employees():
    """캐시 내부 사전은 변경하지 않고 공개 응답에는 복사본을 반환한다."""
    out, names, emails = [], {g[0] for g in GROWTH_NAMES} | {"김지훈", "남궁하늘", "알렉산드라 페트로바"}, set()

    def add(team, division, idx, boss=False, ceo=False, head=False):
        serial = len(out) + 1
        r = rng(f"employee:{division}:{team}:{idx}")
        while True:
            surname, roman_s = r.choice(SURNAMES)
            given, roman_g = r.choice(GIVEN)
            name = surname + given
            if name not in names:
                break
        if team == "growth":
            name, roman_g, roman_s = GROWTH_NAMES[idx]
        elif team in ("platform", "sales1") and idx == 1:
            name, roman_g, roman_s = "김지훈", "jihoon", "kim"
        elif team == "platform" and idx == 10:
            name, roman_g, roman_s = "알렉산드라 페트로바", "alexandra", "petrova"
        elif team == "marketing" and idx == 7:
            name, roman_g, roman_s = "남궁하늘", "haneul", "namgung"
        names.add(name)
        joined = dt.date(r.randint(2014, 2023), r.randint(1, 12), r.randint(1, 25)).isoformat()
        employment, contract_end, last_day = "regular", None, None
        if ceo:
            joined = "2010-03-02"
        if team == "growth" and idx == 6:
            joined = "2026-08-03"
        if team == "marketing" and idx == 7:
            joined, employment, contract_end = "2026-07-01", "intern", "2026-12-31"
        if team == "hr" and idx == 6:
            joined, employment, contract_end = "2025-04-01", "contract", "2027-03-31"
        if team == "cs" and idx == 11:
            last_day = "2026-10-30"
        if team == "sales2" and idx == 7:
            last_day = "2026-09-30"
        if team == "general" and idx == 2:
            joined = "2021-03-02"  # 2026 근속 5년 리프레시
        tenure = 2026 - int(joined[:4])
        grade = "사원" if tenure < 2 else "주임" if tenure < 4 else "대리" if tenure < 7 else "과장" if tenure < 10 else "차장"
        title = "대표이사" if ceo else ("상무" if division == "product" else "이사") if head else "부장" if boss else grade
        if joined[:4] == "2026":
            title = "사원"
        if team == "growth" and idx == 0:
            title = "과장"
        role = "ceo" if ceo else "division_head" if head else "secretary" if team == "ceo-office" else (
            r.choice(["backend", "qa", "sre"]) if team in ("platform", "payments") else
            "frontend" if team == "frontend" else "data" if team == "data" else
            ["pm", "data", "frontend", "backend", "qa", "marketing", "data", "pm"][idx] if team == "growth" else
            "sales" if team in ("sales1", "sales2") else team)
        office = "pangyo" if division == "product" else "busan" if team == "sales2" and idx >= 5 else "hq"
        localpart, n = f"{roman_g}.{roman_s}", 1
        email = localpart + "@superlab.example"
        while email in emails:
            n += 1
            email = f"{localpart}{n}@superlab.example"
        emails.add(email)
        out.append({"id": f"SL{joined[2:4]}{serial:03d}", "name": name,
                    "name_en": f"{roman_g.title()} {roman_s.title()}", "email": email, "extension": str(2000 + serial),
                    "division": division, "division_name": DIVISIONS[division], "team": team,
                    "team_name": next((t[1] for t in TEAMS if t[0] == team), None), "title": title,
                    "position": "대표이사" if ceo else "부문장" if head else "비서실장" if team == "ceo-office" else "팀장" if boss else "팀원",
                    "role": role, "role_label": ROLE_LABELS[role], "employment_type": employment,
                    "joined_on": joined, "contract_end": contract_end, "last_day": last_day,
                    "manager_id": None, "manager": None, "office": OFFICES[office],
                    "home_area": r.choice(["부산광역시 해운대구", "부산광역시 수영구"]) if office == "busan" else
                        r.choice(["서울특별시 강남구", "서울특별시 송파구", "서울특별시 마포구", "성남시 분당구", "수원시 영통구", "용인시 수지구"]),
                    "work_type": "office" if role in ("cs", "general", "secretary") else r.choice(["office", "hybrid", "remote"])})

    add(None, "executive", 0, ceo=True)
    for div in ("product", "business", "corporate"):
        add(None, div, 0, head=True)
    for team, _, division, count in TEAMS:
        for i in range(count):
            add(team, division, i, boss=(i == 0 and team != "legal"))
    for e in out[1:]:
        manager = (next((m for m in out if m["team"] == e["team"] and m["position"] == "팀장"), None)
                   if e["position"] == "팀원" else None)
        if manager is None:
            manager = next((m for m in out if m["division"] == e["division"] and m["position"] == "부문장" and m is not e), out[0])
        e["manager_id"], e["manager"] = manager["id"], manager["name"]
    return tuple(out)


@lru_cache(maxsize=1)
def employee_index():
    return {e["id"]: e for e in company_employees()}


def team_members(team):
    return [e for e in company_employees() if e["team"] == team]


def years_of_service(e, day):
    joined = iso_date(e["joined_on"])
    return max(0, day.year - joined.year - ((day.month, day.day) < (joined.month, joined.day)))


def annual_at(e, day):
    joined = iso_date(e["joined_on"])
    if day < joined:
        return 0, "monthly"
    years = years_of_service(e, day)
    if years < 1:
        months = (day.year - joined.year) * 12 + day.month - joined.month - (day.day < joined.day)
        return min(11, max(0, months)), "monthly"
    return min(25, 15 + max(0, (years - 1) // 2)), "yearly"


def _stamp(day, hour=9):
    return dt.datetime.combine(iso_date(day), dt.time(hour), KST).isoformat()


def record_view(raw, now):
    if dt.datetime.fromisoformat(raw["requested_at"]) > now:
        return None
    r = dict(raw)
    if raw["cancelled_at"] and dt.datetime.fromisoformat(raw["cancelled_at"]) <= now:
        r["status"] = "cancelled"
    elif raw["decided_at"] and dt.datetime.fromisoformat(raw["decided_at"]) <= now:
        r["status"] = raw["status"] if raw["status"] != "cancelled" else "approved"
    else:
        r["status"], r["decided_at"] = "pending", None
    if r["status"] != "cancelled":
        r["cancelled_at"] = None
    if r["status"] != "rejected":
        r["rejection_reason"] = None
    r["status_label"] = STATUS_LABELS[r["status"]]
    today = today_at(now).isoformat()
    r["when"] = "past" if r["end"] < today else "upcoming" if r["start"] > today else "ongoing"
    return r


@lru_cache(maxsize=512)
def carried_over(employee_id, year):
    # 기록이 제공되기 전인 2024 잔여는 0으로 고정한다.
    if year <= 2025:
        return 0
    e = employee_index()[employee_id]
    end = dt.date(year - 1, 12, 31)
    records = employee_records(employee_id, year - 1)
    spent = sum(r["days"] for r in records if r["deducted"] and r["status"] == "approved")
    total = annual_at(e, end)[0] + carried_over(employee_id, year - 1)
    return min(3, max(0, total - spent))


@lru_cache(maxsize=512)
def employee_records(employee_id, year):
    e = employee_index()[employee_id]
    joined = iso_date(e["joined_on"])
    if year not in YEARS or joined.year > year:
        return ()
    r = rng(f"leave:{employee_id}:{year}")
    out = []
    occupied = set()
    carry = carried_over(employee_id, year)
    last = min(e["last_day"] or f"{year}-12-31", e["contract_end"] or f"{year}-12-31", f"{year}-12-31")

    def add(start, days=1, kind="annual", reason="개인 일정", requested=None, decided=None, status="approved", end=None, cancelled=None):
        start = f"{year}-{start}" if len(start) == 5 else start
        finish = end or end_for(start, days)
        dates = business_dates(start, finish)
        if not dates or start < e["joined_on"] or finish > last and kind != "parental":
            return False
        if any(d in occupied for d in dates):
            return False
        request_day = iso_date(requested) if requested else max(joined, iso_date(start) - dt.timedelta(days=14))
        decision_day = iso_date(decided) if decided else request_day + dt.timedelta(days=1)
        if decision_day > iso_date(start) and status != "pending":
            decision_day = iso_date(start)
        if LEAVE_TYPES[kind][1]:
            # 신청 시점까지 승인/대기 상태인 신청 전체를 예약하여 월 발생량 초과를 막는다.
            at_request = dt.datetime.combine(request_day, dt.time(18), KST)
            reserved = sum(x["days"] for raw in out if raw["deducted"]
                           for x in [record_view(raw, at_request)] if x and x["status"] in ("approved", "pending"))
            if reserved + days > annual_at(e, request_day)[0] + carry:
                return False
        out.append({"id": f"LV-{year}-{employee_id}-{len(out)+1:03d}", "employee_id": employee_id,
                    "employee": e["name"], "team": e["team"], "type": kind, "type_label": LEAVE_TYPES[kind][0],
                    "deducted": LEAVE_TYPES[kind][1], "start": start, "end": finish, "days": days,
                    "status": status, "reason": reason, "requested_at": _stamp(request_day),
                    "decided_at": _stamp(decision_day, 14), "approver_id": e["manager_id"], "approver": e["manager"],
                    "rejection_reason": "팀 일정과 중복되어 대체 날짜 협의가 필요합니다." if status == "rejected" else None,
                    "cancelled_at": _stamp(cancelled, 16) if cancelled else None})
        # 반려·취소 기록도 같은 날의 자동 생성 중복을 피한다.
        occupied.update(dates)
        return True

    growth_i = next((i for i, g in enumerate(GROWTH_NAMES) if g[0] == e["name"]), -1) if e["team"] == "growth" else -1
    parental = e["team"] == "data" and e == team_members("data")[5] and year == 2026
    if parental:
        start, end = "2026-06-01", "2027-05-31"
        add(start, len(business_dates(start, end)), "parental", "자녀 돌봄 육아휴직", requested="2026-05-04", end=end)
    if year == 2026 and growth_i == 6:
        add("09-18", .5, "half_pm", "개인 일정", requested="2026-09-10")
        return tuple(out)
    if year == 2026 and growth_i == 1:
        # 10/2까지 전량 소진. 발생량이 늘어나는 근속 기념일 이후에 채운다.
        target = annual_at(e, dt.date(2026, 10, 2))[0] + carry
        for day in business_dates("2026-07-01", "2026-10-02"):
            if sum(x["days"] for x in out) >= target:
                break
            add(day.isoformat(), requested=day.isoformat(), decided=day.isoformat(), reason="연차 사용 계획")
        return tuple(out)
    # 합의된 교육 상황을 먼저 배치하고, 나머지 기록이 예산을 침범하지 않게 한다.
    if year == 2026 and growth_i == 2:
        add("10-06", 3, reason="가족 여행", requested="2026-09-14")
    if year == 2026 and growth_i == 3:
        add("10-26", 3, reason="가을 휴가", requested="2026-10-01", decided="2026-10-23")
    if year == 2026 and growth_i == 4:
        add("10-14", 1, reason="개인 일정", requested="2026-10-01", decided="2026-10-02", status="rejected")
    if year == 2026 and e["team"] == "platform" and team_members("platform").index(e) < 7:
        add("05-04", reason="징검다리 휴가")
    if year == 2026 and e["team"] == "cs" and e["last_day"]:
        add("10-26", 5, reason="퇴사 전 연차 사용", requested="2026-10-01")
    if year == 2026 and growth_i == 5:
        add("03-16")
        add("05-04")
        add("09-11", .5, "half_pm")
        return tuple(out)
    # 여름 3~5일 + 징검다리 + 단일/반차/반반차. 신청일 순서와 최종 예산 모두 검증한다.
    if joined < dt.date(year, 1, 1) and not parental:
        summer = dt.date(year, 7, 13) + dt.timedelta(days=r.randrange(0, 40))
        while not business_day(summer):
            summer += dt.timedelta(days=1)
        add(summer.isoformat(), r.randint(3, 5), reason="여름휴가")
    bridges = ["02-19", "02-20", "05-04", "06-04", "06-05", "09-23", "10-02", "10-06", "12-24", "12-31"] if year == 2026 else ["05-02", "06-05", "10-02", "10-10", "12-24"]
    candidates = [(d, 1, "annual", "징검다리 휴가") for d in r.sample(bridges, min(3, len(bridges)))]
    for _ in range(r.randint(5, 9)):
        day = dt.date(year, r.randint(1, 11), r.randint(1, 27))
        kind = r.choice(["annual", "annual", "half_am", "half_pm", "quarter"])
        candidates.append((day.isoformat(), LEAVE_TYPES[kind][2], kind, "개인 일정"))
    for start, days, kind, reason in sorted(candidates):
        add(start, days, kind, reason)
    if joined < dt.date(year, 1, 1):
        add("04-16", 1, "official", "정기 건강검진")
        if r.randrange(3) == 0:
            add("03-19", 2, "sick", "건강 회복")
        if r.randrange(7) == 0:
            reason, days = r.choice([("본인 결혼", 5), ("조부모상", 3), ("배우자 출산", 10)])
            add("11-09", days, "family_event", reason)
        if (year - joined.year) > 0 and (year - joined.year) % 5 == 0:
            start = max(dt.date(year, 4, 6), joined.replace(year=year))
            add(start.isoformat(), 5, "refresh", "근속 기념 리프레시", requested=start.isoformat())
        if r.randrange(8) == 0:
            add("09-08", 1, reason="개인 일정 변경", status="cancelled", cancelled=f"{year}-09-04")
        if r.randrange(9) == 0:
            add("11-20", 1, status="rejected")
    # 모든 신청 시점의 예약량을 다시 검사한다. 먼저 심은 교육 상황을 유지하고 일반 기록만 줄인다.
    while True:
        violation = None
        for raw in sorted(out, key=lambda x: x["requested_at"]):
            instant = dt.datetime.fromisoformat(raw["requested_at"]) + dt.timedelta(hours=9)
            visible = [v for x in out if x["deducted"] for v in [record_view(x, instant)] if v and v["status"] in ("pending", "approved")]
            if sum(x["days"] for x in visible) > annual_at(e, today_at(instant))[0] + carry:
                violation = visible
                break
        if not violation:
            break
        removable = next((x for x in reversed(out) if x["id"] in {v["id"] for v in violation} and x["reason"] in ("개인 일정", "징검다리 휴가", "여름휴가")), None)
        if removable is None:
            raise ValueError(f"leave budget exceeded: {employee_id}/{year}")
        out.remove(removable)
    return tuple(out)


def employee_status(e, now):
    today = today_at(now).isoformat()
    end = min(x for x in (e["last_day"], e["contract_end"], "9999-12-31") if x)
    if end < today:
        return "resigned"
    for year in YEARS:
        for raw in employee_records(e["id"], year):
            v = record_view(raw, now)
            if v and v["status"] == "approved" and v["type"] == "parental" and v["start"] <= today <= v["end"]:
                return "on_leave"
    return "leaving" if e["last_day"] and today >= e["last_day"][:8] + "01" else "active"


def employee_view(e, now):
    return {**copy.deepcopy(e), "status": employee_status(e, now)}


def records_for(year, now):
    # 연도를 가로지르는 육아휴직도 요청 연도의 날짜 범위에 포함한다.
    return [v for e in company_employees() for y in YEARS if y <= year for raw in employee_records(e["id"], y)
            if raw["start"] <= f"{year}-12-31" and raw["end"] >= f"{year}-01-01"
            for v in [record_view(raw, now)] if v]


def balance(e, now, year=None):
    today = today_at(now)
    year = year or today.year
    cutoff = min(today, dt.date(year, 12, 31))
    effective = min(cutoff, iso_date(e["last_day"] or "9999-12-31"), iso_date(e["contract_end"] or "9999-12-31"))
    annual, accrual = annual_at(e, effective)
    carry = carried_over(e["id"], year) if year <= 2027 else 0
    history, used, scheduled, pending, other = [], 0, 0, 0, {}
    for y in YEARS:
        for raw in employee_records(e["id"], y):
            if raw["start"] > f"{year}-12-31" or raw["end"] < f"{year}-01-01":
                continue
            v = record_view(raw, now)
            if not v:
                continue
            history.append({k: v[k] for k in ("start", "end", "days", "type", "status")})
            for day, amount in units(v):
                if day.year != year:
                    continue
                if v["status"] == "pending" and v["deducted"]:
                    pending += amount
                elif v["status"] == "approved":
                    if v["deducted"]:
                        if day <= cutoff:
                            used += amount
                        else:
                            scheduled += amount
                    elif day <= cutoff:
                        other[v["type"]] = other.get(v["type"], 0) + amount
    total = annual + carry
    remaining = total - used - scheduled - pending
    return {"employee": e["name"], "employee_id": e["id"], "team": e["team"], "team_name": e["team_name"],
            "role": e["role"], "role_label": e["role_label"], "title": e["title"], "position": e["position"],
            "annual": annual, "carried_over": carry, "total": total, "used": used, "scheduled": scheduled,
            "pending": pending, "remaining": remaining, "expiring": max(0, remaining - 3),
            "expires_on": f"{year}-12-31", "usage_rate": round(used / total * 100, 2) if total else 0,
            "other_used": other, "accrual": accrual, "history": sorted(history, key=lambda h: h["start"])}


def policy():
    return {"name": "superlab 연차·휴가 정책", "timezone": "Asia/Seoul", "supported_years": list(YEARS),
            "annual": {"base": 15, "bonus_from_year": 3, "bonus_every_years": 2, "maximum": 25,
                       "first_year": "입사일 기준 만근 월마다 1일, 최대 11일", "carry_limit": 3},
            "types": [{"type": k, "label": v[0], "deducted": v[1], "unit": v[2]} for k, v in LEAVE_TYPES.items()],
            "family_event_days": {"본인 결혼": 5, "조부모상": 3, "배우자 출산": 10},
            "refresh": "근속 5년 단위 5영업일", "expires_on": "12-31",
            "formulas": {"total": "annual + carried_over", "remaining": "total - used - scheduled - pending",
                         "expiring": "max(0, remaining - 3)", "usage_rate": "used / total * 100 (total=0이면 0)"},
            "live_requests_affect_balance": False,
            "note": "워크샵 Mock 정책. 2025 이월은 0, 2026 이월은 2025년 말 잔여에서 계산. 근속은 조회일 기준이며 실제 인사 규정 해석용이 아닙니다."}
