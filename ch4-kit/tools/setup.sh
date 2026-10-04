#!/usr/bin/env bash
# 슈퍼랩 준비 스크립트 — 킷 폴더(ch4-kit) 안에서 한 번 실행한다.
# 1) Claude Code 버전(2.1.283 이상)·node·python3 확인
# 2) Git 이력 확인 — 클론한 저장소의 커밋이 블록2 /standup의 git log 주입과
#    블록3 /pr-desc의 diff 주입에 쓰인다. 클론이 아닌 복사본이면 초기화해 커밋 2개를 만든다.
set -u

need=2.1.283
ver=$(claude --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
if [[ -z "$ver" ]]; then
  echo "claude 명령을 찾지 못했습니다. Claude Code 설치와 PATH를 확인하세요."
elif [[ "$(printf '%s\n%s\n' "$need" "$ver" | sort -V | head -1)" != "$need" ]]; then
  echo "Claude Code $ver — 블록1의 /doctor prompt-audit 에는 $need 이상이 필요합니다. 업데이트 후 진행하세요."
else
  echo "Claude Code $ver 확인"
fi
node --version >/dev/null 2>&1 && echo "node $(node --version) 확인" || echo "node 없음: Node.js 18 이상을 설치하세요."
python3 --version >/dev/null 2>&1 && echo "$(python3 --version) 확인" || echo "python3 없음: 블록2 도구(hr_mcp.py, slack_mock.py)에 필요합니다."
command -v jq >/dev/null 2>&1 && echo "jq 확인" || echo "jq 없음(선택): 훅 스크립트는 python3로 대체 동작합니다."

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Git 저장소 확인: 커밋 $(git rev-list --count HEAD 2>/dev/null || echo 0)개 (최근: $(git log -1 --pretty=%s 2>/dev/null))"
else
  git init -q
  git config user.name  >/dev/null 2>&1 || git config user.name  "lab"
  git config user.email >/dev/null 2>&1 || git config user.email "lab@example.com"
  git add -A -- . ':!samples'
  git commit -q -m "chore: team starter kit scaffold"
  git add -A samples
  git commit -q -m "feat: add meeting and weekly-report samples"
  echo "Git 초기화 완료: 커밋 2개"
fi

npm test 2>/dev/null | tail -1
echo "준비 완료. 이제 'claude'를 실행하고 /status 로 설정 소스를 확인하세요."
