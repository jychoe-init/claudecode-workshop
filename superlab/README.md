# Claude Code 슈퍼랩 저장소

내 반복 작업을 스킬로 만들고(lab1), 사내 API를 스킬로 자동화하고(lab2), 내 지시 프롬프트와 저장소 지시문을 점검해 팀에 넘기는(lab3) 워크샵 저장소입니다.
결정은 참가자가 하고, 파일은 코치(`/workshop-coach`)가 만듭니다. 랩 안내는 `docs/labs/`에 있습니다 -- 목표, 파일 구조, 5단계, 코치 없이 직접 만들 때.
토큰과 로컬 설정은 저장소에 올리지 않습니다.

## 요구 환경

- Claude Code 2.1.283 이상
- Node.js
- Python 3
- 공통 토큰(`LAB_TOKEN`)과 공용 API 주소(`LAB_API_BASE`) -- 아래 시작 명령에 들어 있습니다

## 시작

```bash
git clone https://github.com/jychoe-init/claudecode-workshop.git ~/claude-lab
cd ~/claude-lab/superlab
LAB_TOKEN=lab-1ar52p7g LAB_API_BASE=https://dapdz4klovswq.cloudfront.net bash tools/setup.sh
claude
```

`setup.sh`는 토큰과 API 주소를 커밋되지 않는 파일 `.claude/settings.local.json`에 저장합니다. lab2의 사내 API 조회가 이 두 값을 씁니다.

Claude Code에서 프로젝트와 설정을 확인합니다.

```text
/status
```

## 세 랩

| 랩 | 한 줄 목표 | 시작 |
|---|---|---|
| lab1 · 반복작업 | `/이름 파일경로` 한 번으로 우리 팀 양식의 결과가 나오는 스킬을 만듭니다. | `/workshop-coach lab1` |
| lab2 · 연결 | 사내 API를 조회해 팀 양식의 보고로 정리하는 스킬을 만듭니다(조회는 승인 없이, 바꾸기는 승인). | `/workshop-coach lab2` |
| lab3 · 점검 | 평소 쓰는 지시 프롬프트를 다시 쓰고, `CLAUDE.md`·내 스킬을 `/doctor prompt-audit`으로 점검해 고치고, effort를 정해 커밋합니다. 평소 쓰는 지시 프롬프트 1개를 준비해 오세요. | `/workshop-coach lab3` |

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
| `.mcp.json`, `tools/hr_mcp.py` | 강사 시연용 HR MCP |
| `tools/hr_fetch.py`, `tools/lab_server.py` | API 조회와 로컬 대체 서버 |
| `tools/usage_log.sh` | effort와 응답 길이 기록 |
| `docs/labs/` | 랩 안내문(목표 · 파일 구조 · 5단계 · 코치 없이 직접 만들 때) |
| `docs/worksheets/` | 내 결정과 이유 기록 -- 코치가 받아 적는다 |
| `docs/prompts/` | lab3에서 다시 쓴 내 지시 프롬프트, `examples/`는 보기 셋 |
| `docs/solutions/` | 막힐 때 확인하는 완성본 |
| `samples/`, `src/` | 실습 입력과 코드 |

## 스킬

| 스킬 | 워크샵 안 역할 | 사용 예 |
|---|---|---|
| `meeting-notes` | lab1 출발점 a 회의록 | `/meeting-notes samples/meeting-2026-10-02.txt` |
| `weekly-report` | lab1 출발점 b 주간보고 | `/weekly-report samples/weekly-memo.md` |
| `standup` | lab1 출발점 c 스탠드업 | `/standup "오늘 한 일"` |
| `pr-desc` | lab1 출발점 d PR 설명 | `/pr-desc` |
| `review-checklist` | 참조형 스킬 본보기 | 변경 리뷰 요청 |
| `leave-report` | lab2 출발점 -- 조회 결과를 양식으로 정리하는 본보기 | `/leave-report` |
| `prompt-coach` | 지시 프롬프트 진단·다시 쓰기 (lab3의 기준) | `/prompt-coach "내 초안"` |
| `workshop-coach` | 세 랩의 코치 -- 묻고, 정한 것을 파일로 만들고, 확인한다 | `/workshop-coach lab1` |

## 공용 API와 로컬 대체

공용 API 문서: [워크샵 사내 API](https://dapdz4klovswq.cloudfront.net/)

공용 API를 쓸 수 없으면 로컬 서버를 켜고, 저장된 주소를 로컬 주소로 바꾼 뒤 Claude Code를 다시 시작합니다. 공용 주소로 되돌릴 때는 시작 절의 `setup.sh` 줄을 다시 실행합니다.

```bash
python3 tools/lab_server.py
LAB_API_BASE=http://127.0.0.1:8787 bash tools/setup.sh
claude
```
