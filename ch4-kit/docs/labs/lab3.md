# Lab 3 — 점검하고 팀에 넘기기

## 목표
- 저장된 지시문의 결함 하나를 고칩니다.
- 스킬 effort를 정하고 사용 기록의 변화를 확인합니다.
- 토큰과 로컬 기록을 제외한 커밋을 만듭니다.

## 시작 명령

```text
/workshop-coach lab3
```

## 1. 저장 지시문 감사

**참가자가 하는 일**
- `/doctor prompt-audit`을 실행합니다.
- 지적된 항목 중 우리 팀에서도 생길 만한 것 하나를 고릅니다.
- 삭제, 설정 이동, 문장 수정 중 한 방향을 정합니다.

**Claude에게 일반 요청으로 시키는 일**
- 선택한 결함만 최소 변경으로 고치게 합니다.
- 감사 명령을 다시 실행해 그 결함이 사라졌는지 확인하게 합니다.

## 2. effort와 사용 기록

**참가자가 하는 일**
- lab1과 lab2 스킬에 `low` 또는 `medium`을 정하고 이유를 적습니다.
- Stop 훅에 `tools/usage_log.sh` command 핸들러를 추가합니다.

**Claude에게 일반 요청으로 시키는 일**
- frontmatter YAML과 Stop 훅 JSON을 검사하게 합니다.
- `/skill-doctor`로 스킬 구성을 점검하게 합니다.

실행 전에 두 가지를 적습니다.
1. 같은 입력을 다시 실행하면 `usage.csv`의 `effort`와 `last_message_chars`가 어떻게 달라질지 예측합니다.
2. `git status`에 `settings.local.json`이 보일지 예측합니다.

```bash
tail -n 2 usage.csv
git status --short
```

## 3. README와 커밋

**참가자가 하는 일**
- `README.md` 첫 화면 세 줄을 직접 씁니다: 독자, 첫 명령, 하지 말아야 할 일.
- `settings.local.json`, `usage.csv`, `*_requests.jsonl`이 커밋에서 제외되는지 확인합니다.

**Claude에게 일반 요청으로 시키는 일**
- 첫 세 줄을 보존하고 `.claude/` 구조를 읽어 README의 나머지를 채우게 합니다.
- 커밋 직전에 제외 파일이 없는지 확인하게 합니다.

```bash
git add -A
git commit -m "feat: team starter kit"
git log --oneline | head -1
```

## 완료 기준
- [ ] `lab3a` 결함 하나를 고치고 스킬 effort를 정한 뒤 `usage.csv`의 새 행을 확인했습니다.
- [ ] `lab3b` README 첫 세 줄이 커밋에 들어갔고 토큰과 로컬 설정은 들어가지 않았습니다.

힐트가 필요하면 그냥 말하세요
