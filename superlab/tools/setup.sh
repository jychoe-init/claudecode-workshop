#!/usr/bin/env bash
# 슈퍼랩 준비 스크립트 — 슈퍼랩 저장소 폴더(superlab) 안에서 한 번 실행한다.
# 1) Claude Code 버전(2.1.283 이상)·node·python3 확인
# 2) Git 이력 확인 (클론한 커밋이 /standup·/pr-desc 의 재료)
# 3) 토큰(LAB_TOKEN)과 공용 API 주소(LAB_API_BASE)를 .claude/settings.local.json 의 env 에 저장 — 커밋되지 않는 파일
#    두 값은 환경 변수로 주면 묻지 않고 저장한다:
#      LAB_TOKEN=lab-xxxxxxxx LAB_API_BASE=https://dapdz4klovswq.cloudfront.net bash tools/setup.sh
#    로컬 대체 서버로 바꿀 때도 같은 방법: LAB_API_BASE=http://127.0.0.1:8787 bash tools/setup.sh
set -u

LOCAL=".claude/settings.local.json"
PUBLIC_BASE="https://dapdz4klovswq.cloudfront.net"

# settings.local.json 의 env.<KEY> 를 읽고 쓴다 (python3 heredoc — 셸 정책상 python3 -c 를 쓰지 않는다)
read_env() {
  KEY="$1" python3 - "$LOCAL" <<'PY' 2>/dev/null
import json, os, sys
try:
    print(json.load(open(sys.argv[1])).get("env", {}).get(os.environ["KEY"], ""))
except Exception:
    print("")
PY
}
save_env() {
  KEY="$1" VALUE="$2" python3 - "$LOCAL" <<'PY'
import json, os, sys
p = sys.argv[1]
try:
    d = json.load(open(p))
except Exception:
    d = {}
d.setdefault("env", {})[os.environ["KEY"]] = os.environ["VALUE"]
json.dump(d, open(p, "w"), ensure_ascii=False, indent=2)
PY
}

need=2.1.283
ver=$(claude --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
if [[ -z "$ver" ]]; then
  echo "claude 명령을 찾지 못했습니다. Claude Code 설치와 PATH를 확인하세요."
elif [[ "$(printf '%s\n%s\n' "$need" "$ver" | sort -V | head -1)" != "$need" ]]; then
  echo "Claude Code $ver — lab3의 /doctor prompt-audit 에는 $need 이상이 필요합니다. 그 단계만 강사 화면으로 봅니다."
else
  echo "Claude Code $ver 확인"
fi
node --version >/dev/null 2>&1 && echo "node $(node --version) 확인" || echo "node 없음: Node.js 18 이상을 설치하세요."
python3 --version >/dev/null 2>&1 && echo "$(python3 --version) 확인" || echo "python3 없음: tools/ 스크립트에 필요합니다."
command -v jq >/dev/null 2>&1 && echo "jq 확인" || echo "jq 없음(선택): 훅 스크립트는 python3로 대체 동작합니다."

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Git 저장소 확인: 커밋 $(git rev-list --count HEAD 2>/dev/null || echo 0)개 (최근: $(git log -1 --pretty=%s 2>/dev/null))"
else
  git init -q
  git config user.name  >/dev/null 2>&1 || git config user.name  "lab"
  git config user.email >/dev/null 2>&1 || git config user.email "lab@example.com"
  git add -A -- . ':!samples' && git commit -q -m "chore: team starter kit scaffold"
  git add -A samples && git commit -q -m "feat: add meeting and weekly-report samples"
  echo "Git 초기화 완료: 커밋 2개"
fi

# ---- 토큰 등록 (settings.local.json 은 .gitignore 로 커밋 제외) ----
token_env="${LAB_TOKEN:-}"
existing=$(read_env LAB_TOKEN)
if [[ "$token_env" =~ ^lab-[a-z0-9]{8}$ ]]; then
  save_env LAB_TOKEN "$token_env"
  echo "토큰 저장: $LOCAL (커밋 제외 파일)"
elif [[ -n "$token_env" ]]; then
  echo "LAB_TOKEN 형식이 다릅니다(lab- 뒤 소문자·숫자 8자). 값을 확인해 다시 실행하세요."
elif [[ -n "$existing" ]]; then
  echo "토큰 등록됨: ${existing:0:4}… (바꾸려면 LAB_TOKEN=lab-xxxxxxxx bash tools/setup.sh)"
else
  read -r -p "배부받은 참가자 토큰(lab-xxxxxxxx)을 입력하세요 [건너뛰기: Enter]: " token
  if [[ "$token" =~ ^lab-[a-z0-9]{8}$ ]]; then
    save_env LAB_TOKEN "$token"
    echo "토큰 저장: $LOCAL (커밋 제외 파일)"
  elif [[ -n "$token" ]]; then
    echo "형식이 다릅니다(lab- 뒤 소문자·숫자 8자). 나중에 다시 실행하세요."
  else
    echo "토큰을 건너뛰었습니다. lab2 전에 다시 실행하세요."
  fi
fi

# ---- 공용 API 주소 등록 (lab2 의 tools/hr_fetch.py·hr_mcp.py 가 읽는다) ----
base_env="${LAB_API_BASE:-}"
existing_base=$(read_env LAB_API_BASE)
if [[ -n "$base_env" ]]; then
  save_env LAB_API_BASE "${base_env%/}"
  echo "API 주소 저장: $LOCAL (커밋 제외 파일)"
elif [[ -n "$existing_base" ]]; then
  echo "API 주소 등록됨: $existing_base (공용 주소로 되돌리려면 LAB_API_BASE=$PUBLIC_BASE bash tools/setup.sh)"
else
  save_env LAB_API_BASE "$PUBLIC_BASE"
  echo "API 주소 저장: $LOCAL (공용 주소 $PUBLIC_BASE)"
fi

npm test 2>/dev/null | tail -1

# ---- 팀 이름 등록 (코치가 내 스킬 이름 <출발점>-<팀> 에 쓴다. settings.local.json 은 커밋 제외) ----
team=$(read_env LAB_TEAM)
if [[ -n "$team" ]]; then
  echo "팀 이름 등록됨: $team (바꾸려면 $LOCAL 의 env.LAB_TEAM 을 수정)"
else
  read -r -p "팀 이름 한 단어(영문 소문자, 예: cs, pay, infra) [건너뛰기: Enter → team]: " team
  team=$(printf '%s' "$team" | tr 'A-Z' 'a-z' | tr -cd 'a-z0-9-')
  [[ -z "$team" ]] && team="team"
  save_env LAB_TEAM "$team"
  echo "팀 이름 저장: $team → 내 스킬은 meeting-notes-$team 처럼 이름이 붙습니다"
fi

echo "준비 완료. 이제 'claude'를 실행하고 /status 로 설정 소스를 확인한 뒤 /workshop-coach lab1 로 시작하세요."
