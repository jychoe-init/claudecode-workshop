# 블록2 Stop 훅

`hooks-block2.json`의 `Stop` 이벤트에는 두 핸들러가 있다.

- `http` 핸들러는 `http://127.0.0.1:8787/standup`으로 세션 종료 정보를 보내 로컬 Slack 모의 서버에서 확인한다.
- `command` 핸들러는 `tools/usage_log.sh`를 실행해 세션 ID, 권한 모드, effort, 마지막 응답 길이를 `usage.csv`에 기록한다.

공식 Hooks 문서에 따르면 Stop 훅 입력에는 `last_assistant_message`가 포함된다.

강사용: 실제 Slack은 Webhook이 `text` 필드를 요구하므로 http 핸들러 대신 `tools/slack_post.sh` command 핸들러를 쓴다.
