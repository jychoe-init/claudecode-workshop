#!/usr/bin/env bash
set -u

payload=$(cat)
if command -v jq >/dev/null 2>&1; then
  session_id=$(printf '%s' "$payload" | jq -r '.session_id // ""')
  permission_mode=$(printf '%s' "$payload" | jq -r '.permission_mode // ""')
  effort=$(printf '%s' "$payload" | jq -r '.effort.level // ""')
  last_message_chars=$(printf '%s' "$payload" | jq -r '(.last_assistant_message // "") | length')
else
  values=$(PAYLOAD="$payload" python3 - <<'PY'
import json
import os
try:
    data = json.loads(os.environ["PAYLOAD"])
except (json.JSONDecodeError, TypeError):
    data = {}
message = data.get("last_assistant_message") or ""
print(data.get("session_id") or "")
print(data.get("permission_mode") or "")
print((data.get("effort") or {}).get("level") or "")
print(len(message))
PY
)
  session_id=$(printf '%s\n' "$values" | sed -n '1p')
  permission_mode=$(printf '%s\n' "$values" | sed -n '2p')
  effort=$(printf '%s\n' "$values" | sed -n '3p')
  last_message_chars=$(printf '%s\n' "$values" | sed -n '4p')
fi

project_dir=${CLAUDE_PROJECT_DIR:-$PWD}
log_file="$project_dir/usage.csv"
if [[ ! -f "$log_file" ]]; then
  printf 'timestamp,session_id,permission_mode,effort,last_message_chars\n' > "$log_file"
fi
printf '%s,%s,%s,%s,%s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$session_id" "$permission_mode" "$effort" "$last_message_chars" >> "$log_file"
exit 0
