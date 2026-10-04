---
description: 현재 브랜치 diff로 PR 제목·본문 초안 작성
disable-model-invocation: true
effort: medium
argument-hint: "[비교 대상 브랜치, 기본 main]"
# context: fork
# agent: Explore
---

비교 대상 브랜치와 현재 브랜치 사이의 변경 통계다.

!`git diff --stat ${0:-main}...HEAD 2>/dev/null || git diff --stat HEAD~1 2>/dev/null || echo "(diff 없음)"`

현재 브랜치의 최근 커밋이다.

!`git log --oneline ${0:-main}..HEAD 2>/dev/null | head -20`

위 정보로 다음 형식의 PR 초안을 작성한다.

## 제목

Conventional Commits 접두를 사용하고 전체 제목은 70자 이내로 쓴다.

## 변경 요약

실제 diff에 있는 변경만 간결하게 요약한다.

## 테스트

실행한 것으로 확인되는 테스트와 아직 필요한 테스트를 구분한다.

## 리뷰 포인트

리뷰어가 집중할 변경과 위험을 쓴다.

커밋 메시지를 그대로 옮기지 말 것. 변경하지 않은 파일을 언급하지 말 것.

마지막 줄에 `(effort: ${CLAUDE_EFFORT})`를 출력한다.

<!-- 위 YAML 주석 두 줄의 주석을 풀면 서브에이전트 패널에서 격리 실행을 관찰할 수 있다. -->
