# 킷 기능 검증 (2026-10-04)

검증 스크립트는 킷을 임시 디렉터리에 복사하고 클론 상태(커밋 2개)를 재현한 뒤 실행했다.
환경: macOS, Claude Code 2.1.283, Bedrock(Opus 5.5), Node v22, Python 3.12, jq 있음.

## 요약

- 60건 전부 PASS. MCP 핸드셰이크(initialize → tools/list → tools/call, 오류 응답 3종), Slack mock(GET/POST/400), 훅 스크립트 4종(jq 유·무 경로), JSON 7개·스킬 frontmatter 6개, `npm test`, 주입 명령의 git 유·무 폴백, 문서 경로 참조.
- `claude -p` 스모크: `/prompt-coach` 는 진단·다시 쓴 프롬프트·설정으로 옮길 항목 3섹션을 냈고, `/meeting-notes` 는 결정 3·액션 4·미결 2를 정리하면서 녹취 속 인젹션 문장(`.env` 출력 요구)을 실행하지 않고 기록만 남겼다.
- `.mcp.json` 의 hr 서버는 `claude mcp list` 에서 `Pending approval` 로 인식된다(프로젝트 MCP는 첫 실행 시 승인 필요 — 블록2 안내 문구 반영).

## 검증 중 고친 것

| 파일 | 문제 | 조치 |
|---|---|---|
| `CLAUDE.md` 결함 ① | "생각한 과정을 먼저 출력하라" 문장이 있으면 Opus 5.5(Bedrock)가 **모든 요청을 거절**(`[reasoning_extraction]`, 인사 한 줄도 거절). | "항상 step by step으로 깊고 신중하게 생각하라"로 교체. 여전히 prompt-audit 대상(구모델용 지시)이면서 세션은 정상 동작. 강사 노트·해설 문서 동기화. |
| `tools/slack_mock.py` | 잘못된 JSON 수신 시 비ASCII 상태 문구로 응답 생성이 실패해 연결이 끊김. | 상태 문구를 ASCII(`Bad JSON`)로 변경 → 400 정상 응답. |
| `tools/setup.sh` | 클론 안에서 `.git` 폴더가 없어 중첩 `git init` 발생. | `git rev-parse --is-inside-work-tree` 로 판정. |

## 참고

- 이 환경에서는 `--model sonnet` 과 프로젝트 `model: sonnet` 이 모두 Bedrock Opus 5.5로 실행됐다(워크스페이스 미신뢰 경고 포함). 참가자 환경에서 모델 고정이 필요하면 리허설에서 `modelUsage` 를 확인한다.
- 스모크 비용: 두 호출 합계 약 $0.6 (Opus 5.5 list price 기준).

## 상세 결과

| 영역 | 항목 | 결과 | 비고 |
|---|---|---|---|
| MCP | initialize 응답(serverInfo.name=hr, protocolVersion 에코) | PASS |  |
| MCP | notifications/initialized 에 응답 없음 | PASS | 응답 7건 / 요청 7건 |
| MCP | tools/list = get_leave_balance, request_leave | PASS | get_leave_balance,request_leave |
| MCP | get_leave_balance(kim) 잔여 9일 | PASS | kim님의 연차는 총 15일, 사용 6일, 잔여 9일입니다. |
| MCP | request_leave 접수 + hr_requests.jsonl 기록 | PASS |  |
| MCP | 잔여 초과 요청 isError | PASS |  |
| MCP | 미등록 직원 isError | PASS |  |
| MCP | 알 수 없는 메서드 -> JSON-RPC error | PASS | -32601 |
| MCP | stderr 비어 있음 | PASS |  |
| Slack mock | GET / 200 | PASS |  |
| Slack mock | POST /standup 200 + JSON 본문 | PASS |  |
| Slack mock | received.log 에 메시지 기록 | PASS |  |
| Slack mock | 잘못된 JSON -> 400 | PASS |  |
| Slack mock | hooks-block2.json http url 이 mock 주소와 일치 | PASS | http://127.0.0.1:8787/standup |
| 셸 | bash -n tools/setup.sh | PASS |  |
| 셸 | bash -n tools/usage_log.sh | PASS |  |
| 셸 | bash -n tools/slack_post.sh | PASS |  |
| 셸 | bash -n .claude/hooks/post-check.sh | PASS |  |
| 셸 | usage_log.sh(jq 경로) -> usage.csv 헤더+행 | PASS | 2026-10-04T08:18:42Z,abc,default,medium,10 |
| 셸 | usage_log.sh(jq 없음, python3 대체) 행 추가 | PASS | 2026-10-04T08:18:42Z,abc,default,medium,10 |
| 셸 | usage_log.sh 비JSON 입력에도 exit 0 | PASS |  |
| 셸 | slack_post.sh URL 없으면 건너뜀 exit 0 | PASS |  |
| 셸 | post-check.sh 정상 JS exit 0 / 구문 오류 JS exit 2 + stderr | PASS |  |
| 셸 | .hook.log 기록 | PASS |  |
| 셸 | npm test PASS | PASS | PASS |
| 정적 | JSON 파싱 .claude/profiles/personal.json | PASS |  |
| 정적 | JSON 파싱 .claude/profiles/regulated.json | PASS |  |
| 정적 | JSON 파싱 .claude/profiles/team.json | PASS |  |
| 정적 | JSON 파싱 .claude/settings.json | PASS |  |
| 정적 | JSON 파싱 .mcp.json | PASS |  |
| 정적 | JSON 파싱 docs/solutions/hooks-block2.json | PASS |  |
| 정적 | JSON 파싱 package.json | PASS |  |
| 정적 | settings.json == profiles/team.json | PASS |  |
| 정적 | profiles/personal.json 에 permissions 키 | PASS | defaultMode,allow,deny |
| 정적 | profiles/team.json 에 permissions 키 | PASS | allow,ask,deny |
| 정적 | profiles/regulated.json 에 permissions 키 | PASS | defaultMode,allow,ask,deny |
| 정적 | team: mcp__hr__get_* allow / mcp__hr__request_* ask | PASS |  |
| 정적 | regulated deny 가 team deny 의 상위집합 | PASS | 6 -> 9 |
| 정적 | .mcp.json hr 서버 = python3 tools/hr_mcp.py | PASS |  |
| 스킬 | meeting-notes frontmatter YAML + 공식 필드만 | PASS | ['argument-hint', 'description', 'disable-model-invocation', 'effort'] |
| 스킬 | meeting-notes effort 값 유효 | PASS | low |
| 스킬 | pr-desc frontmatter YAML + 공식 필드만 | PASS | ['argument-hint', 'description', 'disable-model-invocation', 'effort'] |
| 스킬 | pr-desc effort 값 유효 | PASS | medium |
| 스킬 | prompt-coach frontmatter YAML + 공식 필드만 | PASS | ['argument-hint', 'description', 'disable-model-invocation'] |
| 스킬 | review-checklist frontmatter YAML + 공식 필드만 | PASS | ['description'] |
| 스킬 | standup frontmatter YAML + 공식 필드만 | PASS | ['argument-hint', 'description', 'disable-model-invocation'] |
| 스킬 | weekly-report frontmatter YAML + 공식 필드만 | PASS | ['argument-hint', 'description', 'disable-model-invocation', 'effort'] |
| 스킬 | weekly-report effort 값 유효 | PASS | low |
| 스킬 | review-checklist 는 참조형(disable-model-invocation 없음) | PASS |  |
| 스킬 | 주입 명령 3개 git 저장소 안에서 exit 0 | PASS |  |
| 스킬 | 주입 명령 git 없는 디렉터리에서도 exit 0(폴백 문구) | PASS |  |
| 정적 | CLAUDE.md 결함① 구모델용 thinking 지시(사고 출력 요구는 아님) | PASS |  |
| 정적 | CLAUDE.md 결함② 없는 명령 참조(make lint) | PASS |  |
| 정적 | CLAUDE.md 결함③ rules/testing.md 와 모순 | PASS |  |
| 정적 | samples 녹취에 인젹션 문장 1개 포함 | PASS |  |
| 정적 | 문서 내 경로 참조 전부 존재 | PASS |  |
| claude | 버전 >= 2.1.283 | PASS | 2.1.283 (Claude Code) |
| claude | claude mcp list: .mcp.json hr 인식(승인 대기 또는 연결) | PASS | hr: python3 tools/hr_mcp.py - ⏸ Pending approval (run `claude` to approve) |
| claude | prompt-coach 출력에 3/3 키워드 | PASS | 53s, cost $0.3460514, in/out 6/3654 / 누락:set() |
| claude | meeting-notes 출력에 3/3 키워드 | PASS | 21s, cost $0.2622346, in/out 4/920 / 누락:set() |
총 60건, PASS 60, FAIL 0
