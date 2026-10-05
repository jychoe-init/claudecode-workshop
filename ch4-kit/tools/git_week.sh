#!/usr/bin/env bash
# 보고 주(tools/report_week.sh)를 첫 줄에, 그 주의 커밋을 "날짜 메시지" 한 줄씩 출력한다.
# weekly-report-dev 스킬의 자동 삽입 줄이 부른다. git 저장소가 아니거나 커밋이 없어도 exit 0 으로 안내 문장만 낸다.
set -u
here=$(cd "$(dirname "$0")" && pwd)
bash "$here/report_week.sh"
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "(git 저장소 아님: 커밋 없음)"
  exit 0
fi
read -r mon next < <(python3 -c 'import datetime as d; y=d.date.today()-d.timedelta(days=1); m=y-d.timedelta(days=y.weekday()); print(m, m+d.timedelta(days=7))')
out=$(git log --since="$mon 00:00:00" --until="$next 00:00:00" --date=short --pretty='%cd %s' 2>/dev/null)
if [ -n "$out" ]; then
  printf '%s\n' "$out"
else
  echo "(커밋 없음)"
fi
exit 0
