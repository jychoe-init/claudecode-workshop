# Claude Code 팀 스타터 킷

내 반복 작업을 스킬로 만들고 사내 API에 연결한 뒤, 팀에 공유할 상태까지 점검하는 워크샵 킷입니다.
판단은 참가자가 하고 구현은 Claude에게 맡깁니다.
토큰과 로컬 설정은 저장소에 올리지 않습니다.

## 요구 환경

- Claude Code 2.1.283 이상
- Node.js
- Python 3
- 배부받은 `LAB_TOKEN`

## 시작

```bash
git clone https://github.com/jychoe-init/claudecode-workshop.git ~/claude-lab
cd ~/claude-lab/ch4-kit
bash tools/setup.sh
claude
```

Claude Code에서 프로젝트와 설정을 확인합니다.

```text
/status
```

## 세 랩

| 랩 | 한 줄 목표 | 시작 |
|---|---|---|
| lab1 · 반복작업 | 내 입력, 양식, 금지가 담긴 스킬을 만듭니다. | `/workshop-coach lab1` |
| lab2 · 연결 | 사내 API 데이터를 내 팀 양식의 보고로 정리하는 스킬을 만듭니다. | `/workshop-coach lab2` |
| lab3 · 점검·배포 | 지시문과 effort를 점검하고 안전한 커밋을 만듭니다. | `/workshop-coach lab3` |

첫 랩은 아래 명령으로 시작합니다.

```text
/workshop-coach lab1
```

## 디렉터리 지도

| 위치 | 역할 |
|---|---|
| `CLAUDE.md`, `.claude/rules/` | 팀 공통 안내와 파일별 규칙 |
| `.claude/settings.json` | 권한과 훅 설정 |
| `.claude/skills/` | 반복 작업 스킬과 워크샵 코치 |
| `.mcp.json`, `tools/hr_mcp.py` | 강사 시연용 HR MCP |
| `tools/hr_fetch.py`, `tools/lab_server.py` | API 조회와 로컬 대체 서버 |
| `tools/usage_log.sh` | effort와 응답 길이 기록 |
| `docs/labs/` | 참가자 안내문 |
| `docs/worksheets/` | 내 결정과 이유 기록 |
| `docs/solutions/` | 막힐 때 확인하는 완성본 |
| `samples/`, `src/` | 실습 입력과 코드 |

## 스킬

| 스킬 | 워크샵 안 역할 | 사용 예 |
|---|---|---|
| `meeting-notes` | lab1 출발점 ⓐ 회의록 | `/meeting-notes samples/meeting-2026-10-02.txt` |
| `weekly-report` | lab1 출발점 ⓑ 주간보고 | `/weekly-report samples/weekly-memo.md` |
| `standup` | lab1 출발점 ⓒ 스탠드업 | `/standup "오늘 한 일"` |
| `pr-desc` | lab1 출발점 ⓓ PR 설명 | `/pr-desc` |
| `review-checklist` | 참조형 스킬 본보기 | 변경 리뷰 요청 |
| `leave-report` | lab2 패턴 B 본보기 | `/leave-report` |
| `prompt-coach` | 스펙 점검 본보기 | `/prompt-coach "내 스펙"` |
| `workshop-coach` | 결정과 확인을 돕는 코치 | `/workshop-coach lab1` |

## 공용 API와 로컬 대체

공용 API 문서: [워크샵 사내 API](https://REPLACE-AFTER-DEPLOY.cloudfront.net/)

공용 API를 쓸 수 없으면 로컬 서버를 켜고 `LAB_API_BASE`를 바꿉니다.

```bash
python3 tools/lab_server.py
LAB_API_BASE=http://127.0.0.1:8787 claude
```
