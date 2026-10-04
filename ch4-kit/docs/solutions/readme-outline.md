# README 첫 화면 윤곽

아래 세 줄은 참가자가 먼저 정합니다.

1. `[누구를 위한 킷인지 한 줄]`
2. `[처음 실행할 명령 한 줄]`
3. `[절대 하지 말아야 할 일 한 줄]`

그다음 Claude에게 기존 세 줄을 유지하면서 아래 구조를 채우게 합니다.

```markdown
# 팀 스타터 킷

[참가자가 정한 첫 화면 세 줄]

## 요구 환경
- Claude Code 버전
- Node.js와 Python 3
- 배부 토큰(`LAB_TOKEN`)

## 시작
- clone
- setup
- claude
- /status

## 랩
- lab1: 반복 작업을 스킬로
- lab2: API 결과를 보고하고 전송
- lab3: 저장 지시문과 effort를 점검하고 공유

## 디렉터리 지도
- .claude/skills/
- .claude/settings.json
- tools/
- docs/
```
