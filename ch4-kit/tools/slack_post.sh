#!/usr/bin/env bash
set -u

if [[ -z "${SLACK_WEBHOOK_URL:-}" ]]; then
  echo "SLACK_WEBHOOK_URL이 없어 Slack 전송을 건너뜁니다."
  exit 0
fi

payload=$(cat)
if command -v jq >/dev/null 2>&1; then
  slack_payload=$(printf '%s' "$payload" | jq -c '{text: (.last_assistant_message // "")}')
else
  slack_payload=$(PAYLOAD="$payload" python3 - <<'PY'
import json
import os
try:
    data = json.loads(os.environ["PAYLOAD"])
except (json.JSONDecodeError, TypeError):
    data = {}
print(json.dumps({"text": data.get("last_assistant_message") or ""}, ensure_ascii=False))
PY
)
fi
curl -fsS -X POST -H 'Content-Type: application/json' --data "$slack_payload" "$SLACK_WEBHOOK_URL"
