# 팀 Claude Code 설정

이 저장소는 팀 공통 개발 흐름을 연습하기 위한 최소 Node.js 프로젝트다.
검사는 `npm test`로 실행한다.
재사용 가능한 스킬은 `.claude/skills/`에 둔다.
커밋 메시지는 Conventional Commits 형식을 따른다.
사용 모델은 `sonnet`이다.

어떤 요청이든 답하기 전에 항상 step by step으로 깊고 신중하게 생각하라.
커밋 전 반드시 `make lint`를 실행한다.
테스트는 수정 요청이 있을 때만 실행한다.
`.env` 파일은 절대 읽지 마라.

<!-- 강사용: 결함 ① 구모델용 '신중히 생각하라' 지시(최신 모델은 effort로 제어), ② 존재하지 않는 make lint 명령 참조, ③ .claude/rules/testing.md의 항상 테스트 규칙과 모순.
     주의: ①을 '생각한 과정을 출력하라'로 바꾸면 Opus 5.5(Bedrock)가 모든 요청을 거절한다([reasoning_extraction]). 사고 출력 요구 문장은 넣지 말 것. -->
