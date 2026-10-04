# Ch4 팀 스타터 킷

팀이 Claude Code의 울타리, 연결 도구, 반복 스킬, 점검·공유 흐름을 60분에 완성하는 실습 킷입니다.
완성본을 실행한 뒤 한 곳을 팀 상황에 맞게 바꾸고 DoD로 확인합니다.
판단은 사람이 먼저 하고 구현은 Claude에게 맡깁니다.

## 요구 환경

- Claude Code 2.1.283 이상 (`/doctor prompt-audit` 최소 버전)
- Node.js 18 이상, Python 3
- `jq` 권장

## 시작

```bash
git clone https://github.com/jychoe-init/claudecode-workshop.git ~/claude-lab
cd ~/claude-lab/ch4-kit
bash tools/setup.sh   # 버전·도구 점검 + Git 이력 확인 (한 번만)
claude
```

Claude 세션에서 `/status`를 실행해 프로젝트와 설정을 확인합니다.

## 디렉터리 지도

| 위치 | 역할 |
|---|---|
| `CLAUDE.md`, `.claude/rules/` | 팀 행동 안내와 경로별 규칙 |
| `.claude/settings.json`, `.claude/profiles/` | 권한·훅·실행 프리셋 |
| `.claude/skills/` | 반복 작업을 명령과 참조 지식으로 표준화 |
| `.mcp.json`, `tools/` | HR MCP와 로컬 훅 실습 도구 |
| `samples/`, `src/` | 회의·주간 메모와 코드 실습 재료 |
| `docs/blocks/`, `docs/solutions/` | 블록별 가이드와 막힐 때 보는 완성본 |

## 스킬 6종 + 내장 명령 1

| 스킬 | 한 줄 사용 예시 |
|---|---|
| standup | `/standup "PR 리뷰 2건"` |
| prompt-coach | `/prompt-coach "우리 서비스 로그 보고 문제 있는지 찾아줘"` |
| pr-desc | `/pr-desc` |
| review-checklist | `이 변경을 리뷰해줘` |
| meeting-notes | `/meeting-notes samples/meeting-2026-10-02.txt` |
| weekly-report | `/weekly-report samples/weekly-memo.md` |
| prompt-audit | `/doctor prompt-audit` |

## 프리셋 3종

| 프리셋 | 용도 |
|---|---|
| personal | 개인 실험용: 편집과 개발 명령을 넓게 허용 |
| team | 팀 기본값: 조회는 허용하고 편집·전송·신청은 승인 |
| regulated | 규제 환경: 외부 복사와 인프라 명령을 추가 차단 |

> 이 README는 블록4에서 Claude가 새 팀원이 5분 안에 이해하도록 다시 씁니다.
