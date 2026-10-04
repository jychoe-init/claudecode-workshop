---
description: 일일 스탠드업 초안 생성. 어제 커밋과 오늘 할 일을 Slack용 마크다운으로 정리
disable-model-invocation: true
argument-hint: "[오늘 할 일]"
---

다음은 어제의 커밋이다.

!`git log --oneline --since="1 day ago" 2>/dev/null || echo "(커밋 없음)"`

Slack에 바로 붙여넣을 수 있는 마크다운만 출력한다.

### 어제
- 위 커밋을 작업 단위로 요약한다. 커밋이 없으면 `- 커밋 없음`으로 쓴다.

### 오늘
- `$ARGUMENTS`가 있으면 내용을 항목으로 정리한다.
- 인자가 없으면 어제 커밋 흐름에서 이어질 만한 오늘 할 일을 추천한다.

### 블로커
- 명시된 블로커가 없으면 `- 없음`으로 쓴다.
