| 영역 | 항목 | 결과 | 비고 |
|---|---|---|---|
| API | 토큰 없음 -> 401 | PASS |  |
| API | 형식 어긋난 토큰 -> 401 | PASS |  |
| API | GET /v1/me 200 + team/members | PASS | team=growth members=4 |
| API | 같은 토큰 -> 같은 팀(결정적) | PASS |  |
| API | GET /v1/leave balances | PASS |  |
| API | GET /v1/leave/seo 200 | PASS |  |
| API | 미등록 직원 -> 404 | PASS |  |
| API | GET /v1/deploys | PASS |  |
| API | POST /v1/leave/requests -> 201 pending | PASS |  |
| API | 신청이 내 목록에 보임 | PASS |  |
| API | 다른 토큰에는 안 보임(격리) | PASS |  |
| API | 잔여 초과 -> 409 | PASS |  |
| API | /v1/notify 는 404(전송 끝단 없음) | PASS |  |
| API | /v1/slack/link 는 404(전송 끝단 없음) | PASS |  |
| fetch | hr_fetch.py leave -> JSON balances, exit 0 | PASS | {"team": "growth", "as_of": "2026-10-05", "balances": [{"employee": "seo", "role": "frontend", "annu |
| fetch | hr_fetch.py deploys exit 0 | PASS |  |
| fetch | 토큰 없음 -> error no_token (JSON stdout, exit 0: 주입 줄이 끊기지 않게) | PASS |  |
| fetch | 연결 실패 -> error unreachable + lab_server 안내 (exit 0) | PASS |  |
| fetch | hr_fetch.py 는 GET 만(POST/data= 없음) | PASS |  |
| fetch | 인자 없음 -> usage, exit 2 | PASS |  |
| MCP | initialize serverInfo.name=hr, protocolVersion 에코 | PASS |  |
| MCP | notifications/initialized 에 응답 없음 | PASS | 응답 8건 / 요청 9건 |
| MCP | tools/list = get_leave_balance, request_leave (notify_me 없음) | PASS | get_leave_balance,request_leave |
| MCP | get_leave_balance(seo) 가 API 데이터로 답함 | PASS | seo님의 연차는 총 15일, 사용 11일, 잔여 4일입니다. |
| MCP | request_leave 접수(pending) | PASS | seo님의 2026-10-12 연차 1일 신청을 접수했습니다. 상태는 pending입니다. |
| MCP | 잔여 초과 요청 isError | PASS |  |
| MCP | 미등록 직원 isError | PASS |  |
| MCP | notify_me 호출 -> 알 수 없는 도구 isError | PASS |  |
| MCP | 알 수 없는 메서드 -> JSON-RPC error | PASS |  |
| MCP | stderr 비어 있음 | PASS |  |
| MCP | LAB_TOKEN 없음 -> isError + setup.sh 안내 | PASS |  |
| 셸 | bash -n tools/setup.sh | PASS |  |
| 셸 | bash -n tools/usage_log.sh | PASS |  |
| 셸 | bash -n .claude/hooks/post-check.sh | PASS |  |
| 셸 | setup.sh: 토큰 -> settings.local.json env.LAB_TOKEN | PASS | 준비 완료. 이제 'claude'를 실행하고 /status 로 설정 소스를 확인한 뒤 /workshop-coach lab1 로 시작하세요. |
| 셸 | setup.sh: Git 저장소 인식(커밋 2개), 중첩 .git 없음 | PASS |  |
| 셸 | setup.sh: Slack 질문 없음 | PASS |  |
| 셸 | setup.sh 재실행: 토큰 등록됨 표시(앞 4자리만) | PASS |  |
| 셸 | usage_log.sh(jq) -> usage.csv 헤더+행 | PASS | 2026-10-05T01:11:03Z,abc,default,medium,10 |
| 셸 | usage_log.sh(jq 없음, python3 대체) 행 추가 | PASS | 2026-10-05T01:11:03Z,abc,default,medium,10 |
| 셸 | usage_log.sh 비JSON 입력에도 exit 0 | PASS |  |
| 셸 | post-check.sh 정상 JS exit 0 / 구문 오류 JS exit 2 | PASS |  |
| 셸 | npm test PASS | PASS | PASS |
| 정적 | JSON 파싱 .claude/settings.json | PASS |  |
| 정적 | JSON 파싱 .mcp.json | PASS |  |
| 정적 | JSON 파싱 package.json | PASS |  |
| 설정 | settings.json 하나만(profiles/ 없음) | PASS |  |
| 설정 | mcp__hr__get_* allow / mcp__hr__request_* ask | PASS |  |
| 설정 | mcp__hr__notify_* 와 httpHookAllowedEnvVars 없음 | PASS |  |
| 설정 | deny 에 curl/wget/WebFetch/.env (스크립트 경로를 강제) | PASS |  |
| 설정 | Edit(reports/**) ask + Edit(docs/worksheets/**) allow, Edit(**) ask 없음(ask가 allow를 이김) | PASS |  |
| 설정 | hooks 에 Stop http 훅 없음 | PASS |  |
| 설정 | Bash(python3 -m json.tool *) allow (코치 검사 명령은 allowed-tools 턴 밖에서도 돌아야 함) | PASS |  |
| 설정 | sandbox.network.allowLocalBinding (샌드박스 켠 머신에서 로컬 서버 접근) | PASS |  |
| 설정 | .mcp.json hr = python3 tools/hr_mcp.py | PASS |  |
| 설정 | .gitignore: settings.local.json(토큰)·usage.csv·*_requests.jsonl | PASS |  |
| 설정 | tools/lab_api.py == infra/lambda/lab_api.py | PASS |  |
| 스킬 | 스킬 8종 | PASS | leave-report,meeting-notes,pr-desc,prompt-coach,review-checklist,standup,weekly-report,workshop-coach |
| 스킬 | leave-report frontmatter YAML + 공식 필드만 | PASS |  |
| 스킬 | leave-report effort 값 유효 | PASS | low |
| 스킬 | meeting-notes frontmatter YAML + 공식 필드만 | PASS |  |
| 스킬 | meeting-notes effort 값 유효 | PASS | low |
| 스킬 | pr-desc frontmatter YAML + 공식 필드만 | PASS |  |
| 스킬 | pr-desc effort 값 유효 | PASS | medium |
| 스킬 | prompt-coach frontmatter YAML + 공식 필드만 | PASS |  |
| 스킬 | review-checklist frontmatter YAML + 공식 필드만 | PASS |  |
| 스킬 | standup frontmatter YAML + 공식 필드만 | PASS |  |
| 스킬 | standup effort 값 유효 | PASS | low |
| 스킬 | weekly-report frontmatter YAML + 공식 필드만 | PASS |  |
| 스킬 | weekly-report effort 값 유효 | PASS | low |
| 스킬 | workshop-coach frontmatter YAML + 공식 필드만 | PASS |  |
| 스킬 | review-checklist 는 참조형(disable-model-invocation 없음) | PASS |  |
| 스킬 | meeting-notes: 바꿀 곳 표식 >= 3 + template.md | PASS | 표식 3 |
| 스킬 | weekly-report: 바꿀 곳 표식 >= 3 + template.md | PASS | 표식 3 |
| 스킬 | standup: 바꿀 곳 표식 >= 3 + template.md | PASS | 표식 3 |
| 스킬 | pr-desc: 바꿀 곳 표식 >= 3 + template.md | PASS | 표식 3 |
| 스킬 | leave-report: 바꿀 곳 표식 >= 3  | PASS | 표식 4 |
| 스킬 | leave-report 첫 줄이 hr_fetch.py leave 주입 | PASS |  |
| 스킬 | 새로 만들기(ⓔ) 빈 템플릿 docs/templates/skill-blank/{SKILL,template}.md | PASS |  |
| 스킬 | standup/pr-desc 주입 명령 3개 git 안에서 exit 0 | PASS |  |
| 스킬 | 주입 명령 git 없는 디렉터리에서도 exit 0(폴백) | PASS |  |
| 코치 | disable-model-invocation + argument-hint lab1|lab2|lab3 | PASS |  |
| 코치 | allowed-tools: Write 는 docs/worksheets/** 로만, Edit 없음 | PASS | Read, Write(docs/worksheets/**), Bash(python3 -m json.tool *), Bash(git status *), Bash(git diff *), Bash(git log *) |
| 코치 | SKILL.md 두 원칙(에셋 쓰지 않음·비교 기준은 워크시트) + 네 역할 | PASS |  |
| 코치 | references/lab1.md 절 9개 | PASS |  |
| 코치 | references/lab1.md 결정마다 선택지 결과 비교 표(| 결과 |) | PASS | 5 |
| 코치 | references/lab2.md 절 9개 | PASS |  |
| 코치 | references/lab2.md 결정마다 선택지 결과 비교 표(| 결과 |) | PASS | 5 |
| 코치 | references/lab3.md 절 9개 | PASS |  |
| 코치 | references/lab3.md 결정마다 선택지 결과 비교 표(| 결과 |) | PASS | 6 |
| 코치 | 워크시트 템플릿 docs/worksheets/_template.md (결정 3·예측·힌트 기록·확인·추적표·반성) | PASS |  |
| 문서 | docs/labs/lab1.md 에 /workshop-coach lab1 와 DoD lab1a/lab1b | PASS |  |
| 문서 | docs/labs/lab2.md 에 /workshop-coach lab2 와 DoD lab2a/lab2b | PASS |  |
| 문서 | docs/labs/lab3.md 에 /workshop-coach lab3 와 DoD lab3a/lab3b | PASS |  |
| 문서 | docs/blocks/ (구 4블록) 없음 | PASS |  |
| 문서 | 문서·reference 내 경로 참조 전부 존재 | PASS |  |
| 정적 | CLAUDE.md 결함① 구모델용 thinking 지시(사고 출력 요구 아님) | PASS |  |
| 정적 | CLAUDE.md 결함② make lint 참조(Makefile 없음) | PASS |  |
| 정적 | CLAUDE.md 결함③ rules/testing.md 와 모순 | PASS |  |
| 정적 | samples 녹취에 인젹션 문장 1개 | PASS |  |
| 정적 | Slack·notify·received.log·slack_mock·hooks-block2·profiles/·길 A/B 잔존 0 | PASS |  |
총 101건, PASS 101, FAIL 0
