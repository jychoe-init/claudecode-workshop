#!/usr/bin/env bash
# 어제(최근 1일) 커밋을 한 줄씩 출력한다. standup 스킬의 자동 삽입 줄이 부른다.
# git 저장소가 아니거나 커밋이 없어도 exit 0 으로 안내 문장만 낸다.
set -u
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "(git 저장소 아님: 커밋 없음)"
  exit 0
fi
out=$(git log --oneline --since="1 day ago" 2>/dev/null)
if [ -n "$out" ]; then
  printf '%s\n' "$out"
else
  echo "(커밋 없음)"
fi
exit 0
