---
description: 팀 연차 현황을 조회해 팀 공유용 보고로 정리합니다.
disable-model-invocation: true
argument-hint: "[비고 한 줄, 생략 가능]"
effort: low
---
<!-- 바꿀 곳(결정 3): 아래 주입 명령의 사전 승인을 어디에 둘지 정합니다. 이 frontmatter에 `allowed-tools: Bash(python3 tools/hr_fetch.py *)` 한 줄을 넣거나,
     .claude/settings.json permissions.allow에 같은 규칙을 넣습니다. 둘 다 없으면 첫 실행이 중단됩니다(승인 창 없음). -->

!`python3 tools/hr_fetch.py leave`
<!-- 바꿀 곳: 바로 위 조회 종류를 leave 또는 deploys로 바꿉니다. -->

주입된 JSON의 `balances`만 사용해 팀 연차 현황을 만드세요.

<!-- 바꿀 곳: 표 또는 줄 목록 중 팀이 읽기 좋은 형식을 고릅니다. -->
마크다운으로 출력하세요.
- 첫 줄은 `## 팀 연차 현황 (as_of 날짜)` 제목입니다.
- 다음 줄부터 `직원 | 역할 | 잔여 | 사용` 순서의 표를 만듭니다.
- 잔여 연차가 3일 이하이면 잔여 일수를 **굵게** 강조합니다.
- 인자가 있으면 보고서 끝에 비고로 덧붙입니다: `$ARGUMENTS`

<!-- 바꿀 곳: 보고서가 만들면 안 되는 내용을 구체적으로 적습니다. -->
금지:
- JSON에 없는 직원·수치를 만들지 않습니다.
- 오류 JSON(`error` 필드)이면 원인과 `LAB_API_BASE` 안내만 출력합니다.

(effort: ${CLAUDE_EFFORT})
