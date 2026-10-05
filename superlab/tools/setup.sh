#!/usr/bin/env bash
# 슈퍼랩 준비 스크립트 — 슈퍼랩 저장소 폴더(superlab) 안에서 한 번 실행한다.
# 1) Claude Code 버전(2.1.283 이상)·node·python3 확인
# 2) Git 이력 확인 (클론한 커밋이 /standup·/weekly-report-dev 의 재료)
# 3) 토큰(LAB_TOKEN)과 API 주소(LAB_API_BASE)를 .claude/settings.local.json 에 저장 — 커밋되지 않는 파일. 팀 이름은 lab1 첫 답에서 코치가 받는다
#    값은 배포된 LAB 안내서에서 확인한다. LAB_TOKEN=… LAB_API_BASE=… bash tools/setup.sh 로 주면 묻지 않고 저장한다
set -u

LOCAL=".claude/settings.local.json"

need=2.1.283
ver=$(claude --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
if [[ -z "$ver" ]]; then
  echo "claude 명령을 찾지 못했습니다. Claude Code 설치와 PATH를 확인하세요."
elif [[ "$(printf '%s\n%s\n' "$need" "$ver" | sort -V | head -1)" != "$need" ]]; then
  echo "Claude Code $ver -- $need 이상을 권장합니다. 낮으면 'claude update'로 올리세요."
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
existing=$(python3 - "$LOCAL" <<'PY' 2>/dev/null
import json, sys
try:
    print(json.load(open(sys.argv[1])).get("env", {}).get("LAB_TOKEN", ""))
except Exception:
    print("")
PY
)
if [[ -n "$existing" && -z "${LAB_TOKEN:-}" ]]; then
  echo "토큰 등록됨: ${existing:0:4}… (바꾸려면 $LOCAL 의 env.LAB_TOKEN 을 수정)"
else
  token="${LAB_TOKEN:-}"
  [[ -n "$token" ]] || read -r -p "LAB 안내서의 토큰(lab-xxxxxxxx)을 입력하세요 [건너뛰기: Enter]: " token
  if [[ "$token" =~ ^lab-[a-z0-9]{8}$ ]]; then
    LAB_TOKEN="$token" python3 - "$LOCAL" <<'PY'
import json, os, sys
p = sys.argv[1]
try:
    d = json.load(open(p))
except Exception:
    d = {}
d.setdefault("env", {})["LAB_TOKEN"] = os.environ["LAB_TOKEN"]
json.dump(d, open(p, "w"), ensure_ascii=False, indent=2)
PY
    echo "토큰 저장: $LOCAL (커밋 제외 파일)"
  elif [[ -n "$token" ]]; then
    echo "형식이 다릅니다(lab- 뒤 소문자·숫자 8자). 나중에 다시 실행하세요."
  else
    echo "토큰을 건너뛰었습니다. 랩 시작 전에 다시 실행하세요(회의록 출발점만 없이도 됩니다)."
  fi
fi

# ---- API 주소 등록 (주소는 배포된 LAB 안내서에서 확인한다. 저장소에 올리지 않는다) ----
base=$(python3 - "$LOCAL" <<'PY' 2>/dev/null
import json, sys
try:
    print(json.load(open(sys.argv[1])).get("env", {}).get("LAB_API_BASE", ""))
except Exception:
    print("")
PY
)
if [[ -n "$base" && -z "${LAB_API_BASE:-}" ]]; then
  echo "API 주소 등록됨: $base (바꾸려면 $LOCAL 의 env.LAB_API_BASE 를 수정)"
else
  base="${LAB_API_BASE:-}"
  [[ -n "$base" ]] || read -r -p "LAB 안내서의 API 주소(https://….cloudfront.net)를 입력하세요 [건너뛰기: Enter]: " base
  base="${base%/}"
  if [[ "$base" =~ ^https://[a-z0-9.-]+$ || "$base" =~ ^http://127\.0\.0\.1:[0-9]+$ ]]; then
    LAB_API_BASE="$base" python3 - "$LOCAL" <<'PY'
import json, os, sys
p = sys.argv[1]
try:
    d = json.load(open(p))
except Exception:
    d = {}
base = os.environ["LAB_API_BASE"]
d.setdefault("env", {})["LAB_API_BASE"] = base
# hr_mcp.py(MCP hr)와 로컬 대체 서버가 이 도메인·주소로 API를 부르므로 샌드박스에서 허용해야 한다
domains = d.setdefault("sandbox", {}).setdefault("network", {}).setdefault("allowedDomains", [])
host = base.split("://", 1)[1].split(":")[0]
if host not in domains:
    domains.append(host)
json.dump(d, open(p, "w"), ensure_ascii=False, indent=2)
PY
    echo "API 주소 저장: $LOCAL (커밋 제외 파일)"
  elif [[ -n "$base" ]]; then
    echo "형식이 다릅니다(https://… 또는 로컬 http://127.0.0.1:포트). 나중에 다시 실행하세요."
  else
    echo "API 주소를 건너뛰었습니다. 랩 시작 전에 다시 실행하세요(회의록 출발점만 없이도 됩니다)."
  fi
fi

npm test 2>/dev/null | tail -1

echo "준비 완료. 이제 'claude'를 실행하고 /status 로 설정 소스를 확인한 뒤 /workshop-coach lab1 로 시작하세요."
