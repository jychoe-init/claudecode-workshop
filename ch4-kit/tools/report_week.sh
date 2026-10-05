#!/usr/bin/env bash
# 오늘 날짜와 보고 주(어제가 속한 월~일)를 한 줄로 출력한다. 주간보고 스킬의 자동 삽입 줄이 부른다.
# 월요일에 쓰면 지난주, 금요일에 쓰면 이번 주가 보고 주다. 요일 계산을 모델에 맡기지 않으려고 둔다.
set -u
python3 - <<'PY'
import datetime as dt
t = dt.date.today()
mon = (t - dt.timedelta(days=1)) - dt.timedelta(days=(t - dt.timedelta(days=1)).weekday())
W = "월화수목금토일"
print(f"오늘: {t} ({W[t.weekday()]}) · 보고 주: {mon} (월) ~ {mon + dt.timedelta(days=6)} (일)")
PY
exit 0
