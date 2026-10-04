# 팀 스타터 킷

이 저장소는 팀 공통 개발 흐름을 연습하기 위한 최소 Node.js 프로젝트다.
검사는 `npm test`로 실행한다.
재사용 가능한 스킬은 `.claude/skills/`에 둔다.
커밋 메시지는 Conventional Commits 형식을 따른다.
사용 모델은 `sonnet`이다.

모든 응답 전에 항상 단계별로(step by step) 신중하게 생각한 과정을 먼저 출력하라.
커밋 전 반드시 `make lint`를 실행한다.
테스트는 수정 요청이 있을 때만 실행한다.
`.env` 파일은 절대 읽지 마라.

<!-- 강사용: 결함 ① 구모델용 사고 과정 출력 지시, ② 존재하지 않는 make lint 명령 참조, ③ .claude/rules/testing.md의 항상 테스트 규칙과 모순 -->
