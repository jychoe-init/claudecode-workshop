#!/usr/bin/env bash
# 지난 작업일(오늘 전, 커밋이 있는 가장 최근 날짜)의 커밋을 한 줄씩 출력한다. standup 스킬의 자동 삽입 줄이 부른다.
# 주말·공휴일·휴가처럼 커밋이 없는 날은 건너뛴다. 최근 24시간이 아니라 날짜 기준이다.
# git 저장소가 아니거나 커밋이 없어도 exit 0 으로 안내 문장만 낸다.
set -u
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "(git 저장소 아님: 커밋 없음)"
  exit 0
fi
today=$(python3 -c 'import datetime as d; print(d.date.today())')
day=$(git log -1 --until="$today 00:00:00" --date=short --pretty=%cd 2>/dev/null)
if [ -z "$day" ]; then
  echo "(커밋 없음)"
  exit 0
fi
read -r label next < <(python3 -c "import datetime as d; x=d.date.fromisoformat('$day'); print(f'{x}({\"월화수목금토일\"[x.weekday()]})', x+d.timedelta(days=1))")
echo "지난 작업일: $label"
git log --since="$day 00:00:00" --until="$next 00:00:00" --oneline 2>/dev/null
exit 0
