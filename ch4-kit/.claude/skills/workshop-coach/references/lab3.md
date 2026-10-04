# lab3 점검·배포 — 저장 지시문 감사, effort 예측, README, 커밋

## 목표 (3줄)
- 끝나면 킷이 팀에 넘길 상태가 된다: 결함을 고친 `CLAUDE.md`, 내 스킬의 `effort:`, 사용 기록 `usage.csv`, 새 팀원용 `README.md`, 그리고 토큰·로컬 설정이 빠진 커밋 1개.
- "문장으로 안 되면 설정으로"가 이 랩의 한 문장이다. 지시문 결함은 감사로 찾고, 사고 깊이는 문장이 아니라 `effort`로 정한다.
- Part A에서 본 것 중 쓰이는 것: Hook(command), `.gitignore`와 로컬 설정(A1), `/doctor`.

강사 시연 뒤 참가자는 `/doctor prompt-audit`을 직접 실행한다(2.1.283 이상). 결함 3종: 구모델용 "항상 step by step으로 깊고 신중하게 생각하라" 지시 / 존재하지 않는 `make lint` 참조 / `.claude/rules/testing.md`와 모순되는 테스트 시점.

모든 결정은 SKILL.md "질문의 모양"대로 묻는다: **지금 상태(`CLAUDE.md`·참가자 스킬·`README.md`에서 읽어 인용) → 파일에 들어갈 보기 2~3개, 하나에 (추천) → 질문 하나.** 정할 것이 둘이면 하위 결정으로 나눠 한 메시지에 하나씩.

## 결정 1/3 · 우리 팀에서도 생길 법한 결함과 고칠 방향
정해지는 것: `CLAUDE.md`의 어느 줄을 어떻게 바꾸는가.

### 1a 어느 결함
지금(코치가 `CLAUDE.md`를 읽어 결함 3종의 줄을 행 번호와 함께 인용): "step by step으로 깊고 신중하게" 줄 / `make lint` 줄 / "수정 요청이 있을 때만" 테스트 줄.

| 보기 | 내용 | 결과 |
|---|---|---|
| ⓐ 구모델용 사고 지시 | "항상 step by step으로 깊고 신중하게 생각하라" | 요즘 모델에는 효과가 없고, 사고 깊이는 `effort`가 정한다 **(추천: 거의 모든 팀 CLAUDE.md에 들어 있는 줄이고 결정 2와 바로 이어진다)** |
| ⓑ 없는 명령 참조 | `make lint` (Makefile 없음) | Claude가 없는 명령을 실행하려다 실패한다 |
| ⓒ 규칙과 모순 | "수정 요청이 있을 때만 테스트" vs `rules/testing.md`의 "항상 `npm test`" | 둘 중 어느 쪽을 따를지 매번 달라진다 |

질문: "셋 중 우리 팀 CLAUDE.md에도 들어갈 법한 것은 어느 것인가요?"

### 1b 어떻게 고칠까
| 보기 | 내용 | 결과 |
|---|---|---|
| ⓐ 삭제 | 그 줄을 지운다 | 가장 단순. 그 문장이 하던 일(있다면)이 사라진다 |
| ⓑ 설정으로 이동 | 줄을 지우고 "신중히"는 스킬 `effort:`로, "읽지 마라"는 `permissions.deny`로 | 문장은 사라지고 강제가 남는다 **(추천: 1a에서 ⓐ를 골랐으면 — 결정 2에서 `effort`로 옮긴다)** |
| ⓒ 수정 | 사실과 맞게 고친다(예: `make lint` → `npm test`) | 안내는 안내로 남는다 **(추천: 1a에서 ⓑ·ⓒ를 골랐으면)** |

질문: "삭제 / 설정 이동 / 수정 — 어느 것으로 할까요?" 답 뒤 한 번: "이유는 어느 쪽에 가깝나요? ⓐ 그 문장이 하던 일이 없어서 ⓑ 문장보다 설정이 확실해서 ⓒ 다른 이유"
반례: "'신중하게 생각하라' 문장을 지우면 답이 가벼워질까 걱정되나요? 그렇다면 그 걱정은 `effort`로 옮겨야 합니다. 어느 스킬에 어느 값으로요?"

## 결정 2/3 · 내 스킬의 effort와 비용 예측
정해지는 것: lab1·lab2 스킬 frontmatter의 `effort:` 줄.

지금(코치가 참가자의 lab1·lab2 스킬 `SKILL.md` frontmatter를 읽어 인용): `effort: low`가 있는지, 없는지.

| 보기 | 내용 | 결과 |
|---|---|---|
| ⓐ `effort: low` | 두 스킬 모두 | 빠르고 싸다. 정리·양식 채우기(회의록, 보고)에 맞다. 추론이 필요한 판단은 얕아질 수 있다 **(추천: 두 스킬 모두 양식을 채우는 작업이다)** |
| ⓑ `effort: medium` | 근거를 찾아야 하는 스킬에만 | diff·로그 분석처럼 근거를 찾아야 하는 작업. 시간·비용이 늘어난다 |
| ⓒ 지정 안 함 | 줄을 지운다 | 세션 `/effort` 값이 그대로 적용된다. 스킬마다 다르게 하고 싶으면 지정해야 한다 |

적용 범위: 스킬 `effort:`는 그 스킬이 활성일 때만, `/effort`는 세션 전체, `settings.json`은 기본값.

질문: "lab1 스킬과 lab2 스킬의 `effort:`는 어느 것으로 할까요? 둘이 다르면 각각 말해 주세요." (예측 "effort를 바꿔 재실행하면 `usage.csv`의 `effort`·`last_message_chars` 열이 어떻게 달라질까"는 예측 단계에서 따로 묻는다)
반례: "`medium`을 고르셨는데 그 스킬의 금지 줄이 '지어내지 말 것'이라면, 추론을 더 해서 얻는 것이 무엇인가요? 근거를 더 찾는 작업인지, 양식을 채우는 작업인지 구분해 보세요."

## 결정 3/3 · README 첫 화면 세 줄 + 커밋 제외 + 공유 경로
정해지는 것: `README.md` 상단 세 줄(3a, 참가자가 직접 씀), `.gitignore` 항목(3b), 팀 공유 방식(3c).

### 3a README 세 줄
지금(코치가 `README.md` 첫 10줄을 읽어 인용).

| 보기 | 내용 | 결과 |
|---|---|---|
| ⓐ 누구·첫 명령·금지 | `<팀> Claude Code 킷` / `bash tools/setup.sh 후 claude` / `<하지 말 것 하나>` | 새 팀원이 5초 안에 시작한다 **(추천: 세 줄이 각각 대상·행동·경계다)** |
| ⓑ 누구·스킬 목록·연락 | `<팀> 킷` / `/<내스킬1>, /<내스킬2>` / `문의: <이름>` | 무엇을 할 수 있는지 먼저 보인다. 시작 명령은 아래로 내려간다 |

질문: "세 줄의 뼈대는 ⓐ로 할까요, ⓑ로 할까요? 그 다음 각 줄의 실제 문장을 하나씩 받겠습니다." → 뼈대를 고르면 줄마다 한 번씩 묻고 참가자 문장을 그대로 받아쓴다. "니가 정해"면 참가자 팀 이름과 스킬 이름을 넣은 세 줄을 추천으로 보여 준다.

### 3b 커밋에서 뺄 파일
지금(코치가 `.gitignore`와 `git status --short`를 읽어 인용).

| 보기 | 내용 | 결과 |
|---|---|---|
| ⓐ 토큰·사용 기록 | `.claude/settings.local.json`(**토큰이 들어 있다**), `usage.csv`, `*_requests.jsonl` | 비밀과 개인 기록이 팀 저장소에 안 간다 **(추천: 이 셋은 어느 팀이든 빼야 한다)** |
| ⓑ ⓐ + `reports/` | 위 셋 + `reports/` | 보고 이력을 각자만 가진다. 팀이 이력을 공유하려면 넣지 않는다 |

질문: "ⓐ로 할까요, `reports/`까지 뺄까요?"
반례: "`settings.local.json`을 `.gitignore`에 넣었다고 안심하기 전에, 이미 추적 중인 파일은 `.gitignore`가 막지 못합니다. `git status`에서 그 파일이 보이는지 확인하셨나요?"

### 3c 공유 경로
| 보기 | 내용 | 결과 |
|---|---|---|
| ⓐ 프로젝트 커밋 | 지금 하는 것 | 한 저장소에서 함께 일하는 팀. 원격을 팀 저장소로 바꾸면 끝 **(추천: 오늘 커밋이 그대로 팀 킷이 된다)** |
| ⓑ 플러그인 | skills·hooks·agents를 묶어 배포 | 여러 저장소·여러 팀. 버전 관리가 생긴다 |
| ⓒ Managed | 조직 정책을 중앙에서 강제 | 개발자가 바꿀 수 없는 울타리 |

질문: "우리 팀은 셋 중 어느 경로인가요?"

## 직접 작성 (코치는 안내만)
- `CLAUDE.md` 한 줄 수정(결정 1). Claude에게 시키려면 일반 요청으로: "방금 찾은 결함 중 <X>를 최소 변경으로 고쳐 줘. 적용 전에 이유를 한 문장으로."
- lab1·lab2 스킬 frontmatter에 `effort:` 직접 입력(결정 2).
- `.claude/settings.json` Stop 훅 배열에 `{"type": "command", "command": "$CLAUDE_PROJECT_DIR/tools/usage_log.sh"}` 추가 — 힌트 ②가 형태.
- `README.md` 상단에 세 줄을 **직접** 쓴 뒤, 나머지는 Claude에게: "이 세 줄은 그대로 두고 `.claude/`·`tools/`·`docs/worksheets/`를 훑어 나머지 README를 써 줘. 실제 파일과 명령만."
- `.gitignore` 확인·추가 → `git status --short` → `git add -A` → `git commit -m "feat: team starter kit"`.

## 힌트 3단계 (작성 단계)
- ① 어디: "`effort:`는 각 스킬 `SKILL.md`의 frontmatter(`---` 사이)에 한 줄. 훅은 `.claude/settings.json`의 `hooks.Stop[0].hooks` 배열. README 세 줄은 `# 제목` 바로 아래. `.gitignore`는 킷 루트."
- ② 형태: command 핸들러 예시 `{"type": "command", "command": "$CLAUDE_PROJECT_DIR/tools/example.sh"}`; README 세 줄 가상 예 "결제팀 Claude Code 킷 / `bash tools/setup.sh` 후 `claude` / `.env`는 절대 커밋하지 않는다".
- ③ 한 줄: 참가자 스킬 이름을 넣은 `effort: <값>` 줄과, 참가자가 말한 세 줄을 README 형식으로.

## 예측 2개 (실행 직전)
- A: "effort를 바꾼 뒤 같은 입력으로 재실행하면 `usage.csv`의 `effort` 열과 `last_message_chars` 열은 어떻게 변할까요?" (effort 열은 바꾼 값, 글자 수는 보통 low에서 줄어든다 — 반례: 양식이 고정된 스킬은 거의 같다)
- B: "`git status --short`에 `.claude/settings.local.json`이 보일까요?" (기대: 안 보임. 보이면 `.gitignore` 누락 또는 이미 추적 중)

실행 안내: 스킬 재실행 → `tail -n 2 usage.csv` → `/skill-doctor` → `git status --short` → 커밋 → `git log --oneline | head -1`.

## 검사 항목 (결과 확인)
| 항목 | 방법 |
|---|---|
| `/doctor prompt-audit` 재실행에서 결정 1의 결함이 사라졌다 | 참가자 보고(코치는 실행 불가) |
| lab1·lab2 스킬 `effort:` 값이 결정 2와 같다 | 파일 읽기 |
| `usage.csv`에 새 행이 있고 `effort` 열이 결정 2 값이다 | `python3 -c` 또는 Read로 마지막 2행 |
| `README.md` 상단 세 줄이 참가자가 말한 그대로다 | 워크시트 대조 |
| `git status --short`에 제외 파일이 없고, `git log -1`이 참가자 커밋이다 | `git status`, `git log` 실행 |
| 커밋에 `settings.local.json`·`usage.csv`가 없다 | `git show --stat HEAD`는 allowed-tools에 없으므로 참가자에게 실행을 안내하고 결과를 받음 |
| 예측 A·B 비교 | 참가자 보고 |

추적표 열: `CLAUDE.md` 수정 줄 ↔ 결정 1 / `effort:` 줄 ↔ 결정 2 / README 세 줄·`.gitignore` ↔ 결정 3.

## 반성 질문
"팀에 공유하면 가장 먼저 불평이 나올 설정 한 줄은 무엇이고, 그래도 유지할 이유는 무엇인가요?"

## 다음 한 걸음 (예)
"원격을 팀 저장소로 바꾸면(`git remote set-url origin …`) 이 커밋이 그대로 팀 킷입니다. 플러그인으로 묶는 방법은 마무리 자료의 공유 경로 표를 보세요."
