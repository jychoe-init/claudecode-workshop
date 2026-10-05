#!/usr/bin/env bash
set -u

payload=$(cat)
if command -v jq >/dev/null 2>&1; then
  file_path=$(printf '%s' "$payload" | jq -r '.tool_input.file_path // empty')
else
  file_path=$(PAYLOAD="$payload" python3 - <<'PY'
import json
import os
try:
    print(json.loads(os.environ["PAYLOAD"]).get("tool_input", {}).get("file_path", ""))
except (json.JSONDecodeError, TypeError):
    print("")
PY
)
fi

project_dir=${CLAUDE_PROJECT_DIR:-$PWD}
printf '%s edited: %s\n' "$(date '+%H:%M:%S')" "$file_path" >> "$project_dir/.hook.log"

case "$file_path" in
  *.js|*.mjs)
    check_path=$file_path
    if [[ "$check_path" != /* ]]; then
      check_path="$project_dir/$check_path"
    fi
    if ! err=$(node --check "$check_path" 2>&1); then
      printf '구문 오류가 감지되었습니다. 수정해 주세요: %s\n' "$err" >&2
      exit 2
    fi
    ;;
esac
exit 0
