# Claude Code 슈퍼랩 저장소

내 반복 작업을 스킬로 만들고(lab1), 요청문을 다듬는 내 도구를 만들고(lab2), 그 도구로 다듬은 요청문으로 사내 휴가 신청 스킬을 만들어 팀에 넘기는(lab3) 워크샵 저장소입니다.
lab1은 결정은 참가자가, 파일은 코치(`/workshop-coach`)가 만듭니다. lab2·lab3는 코치 없이 참가자가 직접 만듭니다. 랩 안내는 `docs/labs/`에 있습니다.
토큰과 로컬 설정은 저장소에 올리지 않습니다. 실습 데이터(`.env`, `samples/`, HR 연차 데이터)는 모두 임의 생성 값입니다.

## 요구 환경

- Claude Code 2.1.283 이상, 모델 Claude Opus 5.5(저장소 설정)
- Node.js
- Python 3
- 공통 토큰(`LAB_TOKEN`)과 공용 API 주소(`LAB_API_BASE`) -- 배포된 LAB 안내서에서 확인합니다

## 시작

```bash
git clone https://github.com/jychoe-init/claudecode-workshop.git ~/claude-lab
cd ~/claude-lab/superlab
LAB_TOKEN=<LAB 안내서의 토큰> LAB_API_BASE=<LAB 안내서의 주소> bash tools/setup.sh
claude
```

두 자리에는 배포된 LAB 안내서(참가자용 HTML)의 값을 넣습니다. 토큰과 주소는 이 저장소에 적지 않습니다. `setup.sh`는 두 값을 커밋되지 않는 파일 `.claude/settings.local.json`에 저장하고, 주간보고·사내 API 조회가 이 값을 씁니다.

Claude Code에서 프로젝트 설정과 HR 시스템 연결을 확인합니다(저장소 폴더 신뢰 대화상자는 승인합니다).

```text
/status
/mcp
```

## 세 랩

| 랩 | 한 줄 목표 | 시작 |
|---|---|---|
| lab1 · 반복작업 | `/이름 파일경로` 한 번으로 우리 팀 양식의 결과가 나오는 스킬을 만듭니다. | `/workshop-coach lab1` |
| lab2 · 도구 만들기 | 강사가 준 프롬프트 한 장을 붙여, 요청문을 진단하고 묻고 다시 쓰는 스킬 `prompt-coach`를 내가 만듭니다. 샘플 3종으로 시험합니다. | `docs/labs/lab2.md` |
| lab3 · 요청문부터 직접 | 휴가 신청 스킬의 요청문을 내가 쓰고 `/prompt-coach`로 다듬어 `leave-request`를 만듭니다(조회는 승인 없이, 신청은 승인 창). 세 번 실행하고 토큰 없는 커밋으로 팀에 넘깁니다. | `docs/labs/lab3.md` |

첫 랩은 아래 명령으로 시작합니다.

```text
/workshop-coach lab1
```

## 디렉터리 지도

| 위치 | 역할 |
|---|---|
| `CLAUDE.md`, `.claude/rules/` | 팀 공통 안내와 파일별 규칙 |
| `.claude/settings.json` | 승인 규칙(조회는 승인 없이, 신청은 승인 창)과 실행 기록 훅 |
| `.claude/settings.local.json` | 토큰·API 주소·팀 이름 -- `setup.sh`가 저장, 커밋되지 않음 |
| `.claude/skills/` | 반복 작업 스킬과 워크샵 코치 |
| `.mcp.json`, `tools/hr_mcp.py` | HR 시스템 연결(MCP `hr`) -- 조회 도구와 신청 도구. lab1(메일·일정)과 lab3(연차)가 쓴다 |
| `tools/lab_server.py` | 공용 API가 꺼졌을 때 쓰는 로컬 대체 서버 |
| `tools/usage_log.sh` | 실행 기록 훅 |
| `docs/labs/` | 랩 안내문. `lab2-prompt.md`는 lab2에서 붙이는 프롬프트, `lab2-samples/`는 시험 입력 |
| `docs/references/` | Opus 5.5 프롬프트 작성 요지(공식 가이드 발췌) |
| `docs/worksheets/` | lab1 결정 기록 -- 코치가 받아 적는다 |
| `docs/prompts/` | lab3에서 다듬은 내 요청문, `examples/`는 보기 |
| `docs/solutions/` | 막힐 때 확인하는 완성본 |
| `samples/`, `src/` | 실습 입력과 코드 |

## 스킬

| 스킬 | 워크샵 안 역할 | 사용 예 |
|---|---|---|
| `meeting-notes` | lab1 출발점 a 회의록 | `/meeting-notes samples/meeting-2026-10-02.txt` |
| `weekly-report` | lab1 출발점 b 주간보고 (메일·일정) | `/weekly-report` |
| `standup` | lab1 출발점 c 스탠드업 | `/standup "오늘 한 일"` |
| `weekly-report-dev` | lab1 출발점 d 개발자 주간보고 (커밋) | `/weekly-report-dev "막힌 것"` |
| `review-checklist` | 참조형 스킬 본보기 | 변경 리뷰 요청 |
| `prompt-coach` | **lab2에서 내가 만든다** -- 요청문 진단·질문·다시 쓰기 | `/prompt-coach "내 초안"` |
| `leave-request` | **lab3에서 내가 만든다** -- 팀 연차 현황과 신청 | `/leave-request` |
| `workshop-coach` | lab1의 코치 -- 묻고, 정한 것을 파일로 만들고, 확인한다 | `/workshop-coach lab1` |

## 공용 API와 로컬 대체

공용 API 주소와 토큰: 배포된 LAB 안내서에서 확인합니다. `bash tools/setup.sh`가 두 값을 `.claude/settings.local.json`의 `env`에 저장합니다.

공용 API를 쓸 수 없으면 로컬 서버를 켜고, 저장된 주소를 로컬 주소로 바꾼 뒤 Claude Code를 다시 시작합니다. MCP `hr`가 로컬 서버를 부르므로 스킬은 그대로 동작합니다.

```bash
python3 tools/lab_server.py &
LAB_API_BASE=http://127.0.0.1:8787 bash tools/setup.sh
claude
```

공용 API로 되돌릴 때는 배포된 LAB 안내서의 주소로 같은 명령을 다시 실행합니다.
