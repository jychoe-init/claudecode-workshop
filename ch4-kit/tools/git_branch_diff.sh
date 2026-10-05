#!/usr/bin/env bash
# 비교 대상 브랜치(기본 main)와 현재 브랜치 사이의 변경 통계와 커밋 목록을 출력한다. pr-desc 스킬의 자동 삽입 줄이 부른다.
# 사용: bash tools/git_branch_diff.sh [base]
# git 저장소가 아니거나 비교 대상이 없어도 exit 0 으로 안내 문장만 낸다.
set -u
base=${1:-main}
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "(git 저장소 아님: diff 없음)"
  exit 0
fi
echo "## 변경 통계 ($base...HEAD)"
if ! git diff --stat "$base...HEAD" 2>/dev/null; then
  git diff --stat HEAD~1 2>/dev/null || echo "(diff 없음)"
fi
echo
echo "## 커밋 ($base..HEAD)"
logs=$(git log --oneline "$base..HEAD" 2>/dev/null | head -20)
if [ -n "$logs" ]; then
  printf '%s\n' "$logs"
else
  echo "(커밋 없음)"
fi
exit 0
