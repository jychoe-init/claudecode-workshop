#!/usr/bin/env bash
# 오늘 날짜와 보고 주(월~일)를 한 줄로 출력한다. 주간보고 스킬의 자동 삽입 줄이 부른다.
# 금~일에 쓰면 이번 주, 월~목에 쓰면 지난주가 보고 주다(사내 API 실습 메일함과 같은 규칙). 요일 계산을 모델에 맡기지 않으려고 둔다.
set -u
python3 - <<'PY'
import datetime as dt
t = dt.date.today()
mon = t - dt.timedelta(days=t.weekday() + (0 if t.weekday() >= 4 else 7))
W = "월화수목금토일"
print(f"오늘: {t} ({W[t.weekday()]}) · 보고 주: {mon} (월) ~ {mon + dt.timedelta(days=6)} (일)")
PY
exit 0
