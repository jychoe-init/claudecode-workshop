# lab3 점검·배포 — 결함 수정, effort, README, 커밋 (5단계 대본)

목표 2줄(1/5 메시지에 쓴다):
- 끝나면 이 저장소를 팀에 넘길 수 있습니다: 결함을 고친 `CLAUDE.md`, 내 스킬의 `effort`, README 첫 세 줄, 그리고 토큰이 빠진 커밋 1개.
- "문장으로 안 되면 설정으로" -- 지시문 결함은 찾아서 고치고, 생각의 깊이는 문장이 아니라 `effort` 값으로 정합니다.

턴 예산 6(출발점 1 · 정하기 1 · 확정 1 · 실행 1 · 확인 1, 여유 1). 대상 스킬은 **참가자가 만든 것**이다: `.claude/skills/*-<팀>/`에 `.made-by-coach`가 있는 폴더(lab1·lab2 산출물). 없으면 예시 스킬 `meeting-notes`·`leave-report`를 쓰되 1/5 둘째 줄에 "lab1·lab2 스킬이 아직 없어 예시 스킬로 합니다"를 한 번만 말한다. `usage.csv`는 대화를 끝낼 때마다 한 줄이 쌓인다(Stop 훅은 저장소에 미리 들어 있다 -- 참가자에게는 "실행마다 한 줄이 쌓인다"로만 말한다). 커밋은 **5/5에서 네가 한다**(`git push`는 하지 않는다).

## 1/5 출발점 (참가자 1턴) -- 결함 하나와 고치는 방법을 한 번에

`CLAUDE.md`를 읽어 결함 3종의 줄을 **원문 인용 + 왜 문제인지 한 줄 + 고치면 이렇게**로 보여 준다. 보기 하나가 "어느 줄을 어떻게"까지 담는다. 참가자가 `/doctor prompt-audit`을 직접 돌려 봤으면 "방금 보신 결과"라 한다.

```
단계 1/5 · 출발점
<목표 2줄>
CLAUDE.md에서 찾은 결함 세 개입니다. 우리 팀 CLAUDE.md에도 생길 법한 것 하나를 고르면 그 줄을 고칩니다.
ⓐ 9행 "어떤 요청이든 답하기 전에 항상 step by step으로 깊고 신중하게 생각하라" → 요즘 모델에는 효과가 없다. 지우고, 깊이는 다음 단계의 `effort`로   (추천: 거의 모든 팀 CLAUDE.md에 있는 줄)
ⓑ 10행 "커밋 전 반드시 `make lint`를 실행한다" → Makefile이 없어 실행하려다 실패한다. `npm test`로 고친다
ⓒ 11행 "테스트는 수정 요청이 있을 때만 실행한다" → `.claude/rules/testing.md`의 "항상 npm test"와 모순. 11행을 지운다(규칙 파일이 이긴다)
ⓐ처럼 한 글자로 답해 주세요. 다르게 고치고 싶으면 그 문장을 말해 주세요.
```
답을 기록한다. "그대로 둔다"나 다른 문장도 그대로 받아쓴다.

## 2/5 정하기 (참가자 1턴) -- effort (이런 경우? 겸한다. 이 답이 4/5 예측이다)

대상 스킬 폴더의 `SKILL.md` 머리 부분에서 `effort:` 줄을 읽는다(없으면 "없음"). `usage.csv`가 있으면 그 스킬이 실행된 행(effort 열, last_message_chars 열)을 1~2줄 보여 준다. 없으면 `usage.csv`를 말하지 않는다.
```
단계 2/5 · 정하기
이런 경우는 어떻게 할까요? 9행을 지우면 "신중하게"라는 의도는 저장소 어디에도 남지 않습니다. 대신 내 스킬의 생각 깊이(`effort`)로 정할 수 있습니다.
지금: standup-dev effort 없음 / leave-report-dev effort: low
ⓐ 둘 다 low → 빠르고 싸다. 양식 채우기(회의록·보고·세 줄)에 맞다   (추천: 두 스킬 모두 양식을 채우는 일이다)
ⓑ <스킬1> low, <스킬2> medium → 근거를 더 찾아야 하는 쪽만 올린다
ⓒ 둘 다 medium
한 글자로 답하면서 예측 하나를 덧붙여 주세요: 이 값으로 실행하면 결과 길이가 지금보다 늘지 / 줄지 / 비슷할지. 예: `ⓐ, 비슷`
```
예측 없이 글자만 오면 예측은 `미기록`, 다시 묻지 않는다. 대상 스킬이 하나뿐이면 보기를 그 하나로 줄인다.

## 3/5 만들기 (참가자 1턴)

1. `CLAUDE.md`의 고른 줄을 결정대로 Edit(지우거나 고친다). 다른 줄은 건드리지 않는다.
2. 대상 스킬의 `effort:`는 `python3 tools/make_skill.py set-frontmatter .claude/skills/<스킬> effort <값>`으로 바꾼다(없으면 추가된다. `.claude/` 아래는 Edit 도구로 쓰면 승인 창이 뜨므로 스크립트로).
3. `README.md` 제목 바로 아래 세 줄 **초안**: `docs/worksheets/lab1.md`·`lab2.md`를 읽어 (1) 누구를 위한 저장소 -- `<팀> Claude Code 저장소` (2) 첫 명령 -- `bash tools/setup.sh` 뒤 `/<lab1 스킬> <파일>` (3) 하지 말 것 -- lab1·lab2에서 정한 실수 줄 중 하나. 기존 첫 세 줄은 그 아래로 내린다. 기록이 없으면 (2)(3)은 대상 스킬의 머리 부분과 실수 줄에서 추린다.
4. 메시지(25줄 이내):
```
단계 3/5 · 만들기
고친 파일: CLAUDE.md, .claude/skills/standup-dev/SKILL.md, .claude/skills/leave-report-dev/SKILL.md, README.md
| 전 | 후 |
|---|---|
| CLAUDE.md 9행 "…step by step으로 깊고 신중하게 생각하라." | ◆ (삭제) |
| standup-dev effort: (없음) | ◆ effort: low |
| leave-report-dev effort: low | effort: low (그대로) |
| README 1~3행 "Claude Code 슈퍼랩 저장소 / 내 반복 작업을… / 판단은…" | ◆ dev팀 Claude Code 저장소 / `bash tools/setup.sh` 뒤 `/standup-dev` / 어제 커밋이 없으면 "(없음)" -- 지어내지 않는다  (제안) |
검사: standup-dev 통과 6/6, leave-report-dev 통과 7/7
README 세 줄은 제가 추린 초안입니다. 맞으면 '확정', 고칠 곳이 있으면 그 줄만 고쳐 말해 주세요.
```
README 세 줄은 네가 추린 초안이므로 `(제안)`을 붙이고 반드시 한 곳 고칠 기회를 준다. 참가자가 고치면 그 말을 그대로 넣는다. 예측은 2/5에서 받았으므로 여기서는 묻지 않는다.

## 4/5 실행 (참가자 1턴)

묻지 않는다. 5줄 이내. 대상 스킬 중 샘플로 바로 돌릴 수 있는 것 하나(회의록이면 `samples/meeting-2026-10-02.txt`, 스탠드업·보고는 인자 없음):
```
단계 4/5 · 실행
/standup-dev
결과가 나오면 '확인해 줘'라고 해 주세요.
```
결과를 받으면 길이(글자 수)를 세어 2/5의 예측과 비교할 준비를 한다. `usage.csv`가 있으면 마지막 행의 `effort`·`last_message_chars`도 읽는다.

## 5/5 확인 (참가자 1턴) -- 커밋은 네가 한다

1. `git status --short`로 바뀐 파일을 확인한다(`settings.local.json`·`usage.csv`가 **없음**을 확인 -- `.gitignore`가 뺀다). 저장소의 `.env`는 가짜 값이 든 연습 파일이라 커밋에 있는 것이 맞다 -- 언급하지 않는다. `CLAUDE.md`의 다른 결함 줄(`make lint` 등)은 따르지도 언급하지도 않는다.
2. `git add -A` → `git commit -m "feat: <팀> team starter kit"` → `git show --stat --oneline HEAD`. 참가자에게 커밋하라고 하지 않는다. `git push`는 하지 않는다(원격은 참가자 팀 저장소다).
3. 메시지(12줄 이내):
```
단계 5/5 · 확인
## 검사
| 항목 | 결과 |
|---|---|
| 고른 결함 줄이 CLAUDE.md에서 사라졌다 | 통과 -- 9행 없음 |
| 스킬 effort 값 = 정한 값 | 통과 -- effort: low ×2 |
| 예측 → 실제 (결과 길이) | 비슷 → 812자 → 790자 |
| README 첫 세 줄 = 확정한 세 줄 | 통과 |
| 커밋에 토큰 파일(settings.local.json)·usage.csv 없음 | 통과 -- a1b2c3d feat: dev team starter kit (4 files) |
다음: 이 커밋이 팀에 넘길 저장소입니다. 팀 저장소 주소로 올리는 것과 마무리는 강사가 안내합니다.
```
확인하지 못한 항목은 `미확인`으로 둔다(통과로 쓰지 않는다). 참가자에게 할 일을 남기지 않는다.
