---
description: 주간보고 초안을 팀 템플릿으로 작성
disable-model-invocation: true
effort: low
argument-hint: "[이번 주 한 일 메모 또는 파일 경로]"
---

`${CLAUDE_SKILL_DIR}/template.md`의 구조와 제한을 따라 주간보고를 작성한다.

`$ARGUMENTS`가 존재하는 파일 경로면 Read로 읽고, 파일이 아니면 입력 메모로 취급한다. 원문에 없는 성과나 수치를 만들지 않는다. 날짜는 보고 주의 시작일을 사용한다.

한국어 마크다운 보고서만 출력한다.
