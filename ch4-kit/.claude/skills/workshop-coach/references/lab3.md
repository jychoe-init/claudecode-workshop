# lab3 점검·배포 — 결함 수정, effort, README, 커밋 (5단계 대본)

목표 2줄(1/5 메시지에 쓴다):
- 끝나면 이 저장소를 팀에 넘길 수 있습니다: 결함을 고친 `CLAUDE.md`, 내 스킬 두 개의 `effort`, 비용 기록 `usage.csv`, README 첫 세 줄, 그리고 토큰이 빠진 커밋 1개.
- "문장으로 안 되면 설정으로" -- 지시문 결함은 감사로 찾고, 생각의 깊이는 문장이 아니라 `effort` 값으로 정합니다.

턴 예산 6. 참가자 스킬은 `.claude/skills/*-<팀>/`(lab1·lab2에서 만든 것). `usage.csv`는 실행마다 한 줄이 쌓인다(Stop 훅은 저장소에 미리 들어 있다 -- 참가자에게는 "실행마다 한 줄이 쌓인다"로만 말한다).

## 1/5 출발점 (참가자 1턴)

`CLAUDE.md`를 읽어 결함 3종의 줄을 **원문 인용 + 왜 문제인지 한 줄**로 보여 준다. 참가자가 `/doctor prompt-audit`을 직접 돌려 봤으면 "방금 보신 결과"라 한다.

```
단계 1/5 · 출발점
<목표 2줄>
CLAUDE.md에서 찾은 결함 세 개입니다.
ⓐ 9행 "어떤 요청이든 답하기 전에 항상 step by step으로 깊고 신중하게 생각하라" → 요즘 모델에는 효과가 없고, 깊이는 `effort`가 정한다   (추천: 거의 모든 팀 CLAUDE.md에 있는 줄이고 다음 단계와 이어진다)
ⓑ 10행 "커밋 전 반드시 `make lint`를 실행한다" → Makefile이 없어 실행하려다 실패한다
ⓒ 11행 "테스트는 수정 요청이 있을 때만 실행한다" → `.claude/rules/testing.md`의 "항상 npm test"와 모순
우리 팀 CLAUDE.md에도 생길 법한 것은 어느 것인가요?
```

## 2/5 정하기 (참가자 2~3턴)

### 첫 질문 -- 고치는 방법 (전/후 후보)
```
단계 2/5 · 정하기 (1번째)
지금: 어떤 요청이든 답하기 전에 항상 step by step으로 깊고 신중하게 생각하라.
어떻게 고칠까요?
ⓐ 줄을 지운다 → (없음)   (추천: 이 문장이 하던 일은 다음 단계의 effort 값이 대신한다)
ⓑ 설정으로 옮긴다 → 줄을 지우고 `effort`로 (ⓐ와 같되 기록에 "설정으로 이동"으로 남긴다)
ⓒ 문장을 고친다 → 예: "근거가 필요한 판단은 근거를 먼저 적는다"
```
ⓑ(make lint)면 ⓐ 삭제 / ⓒ `npm test`로 수정(추천). ⓒ(테스트 모순)면 ⓐ 11행 삭제(추천, rules가 이김) / ⓒ "항상 `npm test`"로 수정.

### 이런 경우? (랩당 1회, 첫 질문 뒤)
```
단계 2/5 · 정하기 (2번째)
이런 경우는 어떻게 할까요? 이 줄을 지우면 "신중하게"라는 의도는 저장소 어디에도 남지 않습니다.
ⓐ 내 스킬의 effort 값으로 남긴다 (다음 질문)   (추천)
ⓑ 남기지 않아도 된다
```

### 두 번째 결정 -- effort (이 답이 4/5 예측이다)
`usage.csv`를 Read로 읽어 lab1·lab2 스킬이 실행된 행(effort 열, last_message_chars 열)을 2~3줄 보여 준다. 없으면 "아직 기록이 없습니다"라고 한다.
```
단계 2/5 · 정하기 (3번째)
usage.csv 최근 행: … effort=low last_message_chars=812 (meeting-notes-cs) / … effort=low 640 (leave-report-cs)
내 스킬 두 개의 effort를 어디에 둘까요? 바꾸면 다음 실행에서 `effort` 열은 그 값으로, `last_message_chars`는 보통 low에서 줄어듭니다.
ⓐ 둘 다 low → 빠르고 싸다. 양식 채우기(회의록·보고)에 맞다   (추천: 두 스킬 모두 양식을 채우는 일이다)
ⓑ 회의록 low, 보고 medium → 근거를 더 찾아야 하는 쪽만 올린다
ⓒ 둘 다 medium
한 글자로 답하고, 바꾼 뒤 `last_message_chars`가 늘지 / 줄지 / 비슷할지 한 단어로 덧붙여 주세요.
```
(둘을 한 메시지에 묻는 유일한 예외 -- 예측이 결정에 붙어 있어서다. 참가자가 하나만 답하면 나머지는 기본값 low·"비슷"으로 두고 기록에 `그대로`.)

## 3/5 만들기 (참가자 1턴)

1. `CLAUDE.md`의 고른 줄을 결정대로 Edit(지우거나 고친다). 다른 줄은 건드리지 않는다.
2. 두 스킬의 `effort:`는 `python3 tools/make_skill.py set-frontmatter .claude/skills/<스킬> effort <값>`으로 바꾼다(없으면 추가된다. `.claude/` 아래는 Edit 도구로 쓰면 승인 창이 뜨므로 스크립트로).
3. `README.md` 제목 바로 아래 세 줄 **초안**: `docs/worksheets/lab1.md`·`lab2.md`를 읽어 (1) 누구를 위한 저장소 -- `<팀> Claude Code 저장소` (2) 첫 명령 -- `bash tools/setup.sh` 뒤 `/<lab1 스킬> <파일>` (3) 하지 말 것 -- lab1·lab2에서 정한 실수 줄 중 하나. 기존 첫 세 줄은 그 아래로 내린다.
4. 메시지:
```
단계 3/5 · 만들기
고친 파일: CLAUDE.md, .claude/skills/meeting-notes-cs/SKILL.md, .claude/skills/leave-report-cs/SKILL.md, README.md
| 전 | 후 |
|---|---|
| CLAUDE.md 9행 "…step by step으로 깊고 신중하게 생각하라." | ◆ (삭제) |
| meeting-notes-cs effort: (없음) | ◆ effort: low |
| leave-report-cs effort: low | effort: low (그대로) |
| README 1~3행 "Claude Code 슈퍼랩 저장소 / 내 반복 작업을… / 판단은…" | ◆ CS팀 Claude Code 저장소 / `bash tools/setup.sh` 뒤 `/meeting-notes-cs <녹취 파일>` / 담당자·기한이 없으면 '미정' -- 지어내지 않는다 |
◆ 9행: "ⓐ" / ◆ effort: "ⓐ" / ◆ README: 기록 lab1·lab2에서 추림 (제안)
README 세 줄 중 고칠 곳이 있나요? 없으면 '확정'.
```
README 세 줄은 네가 추린 초안이므로 `(제안)`을 붙이고 반드시 한 곳 고칠 기회를 준다. 참가자가 고치면 그 말을 그대로 넣는다.

## 4/5 실행 (참가자 1턴)

예측은 2/5에서 받았다. 바로 실행 안내:
```
단계 4/5 · 실행
/meeting-notes-cs samples/meeting-2026-10-02.txt
```
결과를 받으면 네가 `usage.csv` 마지막 2행을 Read로 읽어 `effort` 열과 `last_message_chars` 변화를 한 줄로 보여 주고, `git status --short`를 돌려 보여 준다(`settings.local.json`이 **없음**을 짚는다 -- `.gitignore`가 뺀다). 그리고:
```
단계 4/5 · 실행
git status: M CLAUDE.md, M README.md, ?? .claude/skills/meeting-notes-cs/ … (settings.local.json·usage.csv는 없음 -- 커밋에서 빠진다)
이대로 커밋할까요? "커밋해"라고 하시면 `git add -A && git commit -m "feat: <팀> team starter kit"`을 실행합니다.
```
"커밋해"면 `git add -A` → `git commit -m "feat: <팀> team starter kit"` → `git log --oneline -1`을 보여 준다. (`git push`는 하지 않는다 -- 원격은 참가자 팀 저장소다.)

## 5/5 확인 (참가자 1턴)

```
단계 5/5 · 확인
## 검사
| 항목 | 결과 | 증거 |
| 고른 결함 줄이 CLAUDE.md에서 사라졌다 | 통과 | 9행 없음 (`/doctor prompt-audit` 재실행은 참가자 확인) |
| 두 스킬 effort 값 = 정한 값 | 통과 | effort: low ×2 |
| usage.csv 새 행의 effort 열 = 정한 값, 예측 vs 실제 | low / "비슷" → 812→790 | |
| README 첫 세 줄 = 확정한 세 줄 | 통과 | |
| 커밋에 settings.local.json·usage.csv 없음 | 통과 | git show --stat HEAD |
## 추적표
| 파일 줄 | 참가자 말 | 이유 |
| CLAUDE.md 9행 삭제 | "ⓐ" | 깊이는 effort가 정한다 |
| effort: low ×2 | "ⓐ, 비슷" | 양식을 채우는 일 |
| README 1~3행 | "확정" (초안 제안) | 새 팀원이 5초 안에 시작 |
## 다음 한 걸음
원격을 팀 저장소로 바꾸면(`git remote set-url origin …`) 이 커밋이 그대로 팀 저장소입니다. 마무리: 체크리스트.
반성(선택): 팀에 공유하면 가장 먼저 불평이 나올 설정 한 줄은? 그래도 유지할 이유는?
```
