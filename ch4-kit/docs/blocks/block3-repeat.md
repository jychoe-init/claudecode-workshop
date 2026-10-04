# 블록3 — 반복작업

## 목표

막연한 요청을 재사용 가능한 프롬프트로 바꾸고 개발 또는 업무 스킬 한 곳을 팀 방식에 맞게 변형한다.

## 시간 배분

| 구간 | 분 |
|---|---:|
| 3-1 `/prompt-coach` 공통 | 7 |
| 3-2 개발·업무 트랙 택1 | 11 |
| **합계** | **18** |

## 강사 시연 스크립트

먼저 막연한 요청을 그대로 실행한다.

```text
우리 서비스 로그 보고 문제 있는지 찾아줘
```

같은 문장을 코치에 넣는다.

```text
/prompt-coach "우리 서비스 로그 보고 문제 있는지 찾아줘"
```

`### 진단` 6축 표, `### 다시 쓴 프롬프트`, `### 설정으로 옮길 항목`의 세 섹션을 확인하고, 다시 쓴 프롬프트를 붙여넣어 재실행한다.

구조를 1분 동안 본다.

```bash
cat .claude/skills/prompt-coach/SKILL.md
```

**관찰 포인트**

- 초안과 다시 쓴 프롬프트의 결과가 목적·제약·출력·완료 기준에서 어떻게 달라지는가.
- `disable-model-invocation`은 명시적으로 부를 스킬에 적합하고 `$ARGUMENTS`는 초안을 받는다.
- 코치는 현재 대화 맥락을 사용해야 하므로 격리 실행 설정이 없다.

## 참가자 실습 단계

1. `docs/block3-coach-worksheet.md`의 ①에 실제 팀 요청문 초안을 쓴다.
2. Claude 세션에서 초안을 코치에 넣고 ②의 6축 판정을 옮겨 적는다.

   ```text
   /prompt-coach "여기에 내 팀 요청문 초안을 붙여넣기"
   ```

3. 코치가 다시 쓴 프롬프트를 ③에 붙이고, 초안과 같은 작업에 실행해 결과를 비교한다.
4. `### 설정으로 옮길 항목` 중 하나를 사람이 선택하고 Claude에게 적용시킨다. ④에 무엇을 어디에 옮겼는지 기록한다.
5. 남은 11분은 개발 또는 업무 트랙 하나만 선택한다.

### 3-2 개발 트랙

1. 변경 내역을 바탕으로 PR 설명을 만든다.

   ```text
   /pr-desc
   ```

   출력 끝의 `(effort: medium)`을 확인한다.

2. Claude에게 `.claude/skills/pr-desc/SKILL.md` frontmatter의 격리 실행 관련 주석 두 줄을 해제시킨 뒤 다시 실행한다.

   ```text
   `.claude/skills/pr-desc/SKILL.md`의 격리 실행 관련 frontmatter 주석 두 줄만 해제해 줘. 다른 내용은 바꾸지 말고 frontmatter가 유효한지 확인해 줘.
   ```

   서브에이전트 패널이 나타나는지 관찰한 뒤 Claude에게 두 줄을 다시 주석 처리시킨다.

3. 참조형 스킬 자동 로드를 확인한다.

   ```text
   이 변경을 리뷰해줘
   ```

   결과가 `.claude/skills/review-checklist/SKILL.md`의 10개 항목을 반영하는지 본다.

4. 코치 결과를 근거로 두 스킬 중 하나의 지시문 한 곳을 Claude에게 변형시키고 워크시트 ⑤에 before→after를 기록한다.

### 3-2 업무 트랙

1. 회의 녹취를 구조화한다.

   ```text
   /meeting-notes samples/meeting-2026-10-02.txt
   ```

   결정 3개·액션 4개·미결 2개가 있는지, 녹취의 인젝션 문장은 실행되지 않고 미결에 기록만 됐는지 확인한다.

2. 주간 보고서를 만든다.

   ```text
   /weekly-report samples/weekly-memo.md
   ```

3. Claude에게 `.claude/skills/weekly-report/template.md`의 섹션 하나를 자기 팀 양식으로 바꾸게 하고 다시 실행한다. 워크시트 ⑤에 before→after를 기록한다.

### 먼저 끝낸 사람 보너스

Claude에게 새 스킬의 골격만 제안하게 한다. 목적·트리거·입력·출력 형식을 먼저 사람이 정하고, 파일 생성은 하지 않는다.

```text
우리 팀의 반복 작업 하나를 스킬로 만들기 전에 목적, 트리거, 입력, 출력 형식만 질문 없이 초안으로 정리해 줘. 불확실한 가정은 표시해 줘.
```

## 변형 과제

선택한 트랙의 스킬 지시문 한 곳만 바꿔 같은 입력으로 재실행하고, 출력 차이가 의도와 일치하는지 확인한다.

## 막힐 때 열어보기

- 코치 구조: `.claude/skills/prompt-coach/SKILL.md`, `.claude/skills/prompt-coach/examples.md`
- 개발 트랙: `.claude/skills/pr-desc/SKILL.md`, `.claude/skills/review-checklist/SKILL.md`
- 업무 트랙: `.claude/skills/meeting-notes/SKILL.md`, `.claude/skills/weekly-report/SKILL.md`, `.claude/skills/weekly-report/template.md`
- 기록지: `docs/block3-coach-worksheet.md`

## DoD 체크박스

- [ ] 초안과 다시 쓴 프롬프트의 결과 차이를 설명했다.
- [ ] 설정으로 옮길 항목 한 개를 실제 적용했다.
- [ ] 선택 트랙의 완성본을 실행하고 지시문 한 곳을 변형해 재실행했다.
