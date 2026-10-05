# HR API 검증 — 버전 2026-10-06

이번 API·MCP·Lab3 문서 변경에 대해 실행한 검증이다. 숫자는 테스트 그룹 수이며 그룹 내부에서 120명·2025/2026년 기록·각 상태 전환 시점을 반복 검사했다.

| 범위 | 결과 | 확인 내용 |
|---|---|---|
| `python3 infra/tests/test_lab_api.py` | PASS — 14개, FAIL 0 | 결정성, 직원 120명, 사번·메일 고유성, 조직·특수 사례, 연차 계산·이월, 날짜별 합계, 신청·승인·취소 경계에서 잔여 ≥ 0 |
| 업무 달력·이력 | PASS | 주말·휴일 제외, 당일 사용/미래 예정 분리, 신청 전 기록 숨김, 반려·취소 상태, 그로스팀 교육 사례와 플랫폼팀 공백 |
| 페이지·필터 | PASS | 모든 목록의 기본/최대 limit, offset, 필터 후 total, next_offset, 빈 페이지, 오류값, 명시적 `limit=all`, 필터와 all 조합 |
| 직원·신청 | PASS | 한글 인코딩, 사번·메일 조회, 동명이인 409, POST 400/404/409/201, 0.5/0.25일, warnings, 실시간 신청의 잔액 비차감 |
| 신청 조회 | PASS | 토큰별 격리, 작성자·직원·팀·상태 필터, 최근 500건 범위, 2분/10분 승인 전환 |
| Lambda 어댑터 | PASS | raw query 전달, 재귀 float/Decimal 변환, 동일 시각 신청의 서로 다른 저장 키, DynamoDB Query 페이지 이어 받기 |
| `python3 infra/tests/test_local_mcp.py` | PASS | 실제 로컬 HTTP 서버·stdio initialize·tools/list 6개·한글 연차 문장과 사용 날짜·limit/all·반차 신청·작성자 헤더·경고·잔여 부족 |
| 메일·일정·배포 응답 | PASS | 메일함별 팀원·메일 일치, 조건부 승인/상대 날짜/AI 지시문, 치과 예약, 제품개발부문 deployed_by와 기존 5개 필드 |
| `npm test` (`superlab/`) | PASS | 기존 Node.js 검사 |
| 문서·예시 | PASS | 스킬 YAML, JSON 예시 파싱, 예시 수치와 고정 시각 API 응답 일치 |
| API 문서 화면 | PASS | Playwright: 1440/390px, 화면 넘침 없음, 목차 링크 유효, 표 8개의 열 수 일관, 런타임 오류 없음. 데스크톱·모바일 캡처 확인 |
| CloudFormation | PASS | `UPDATE_COMPLETE`. Lambda·연결 참조·호출 한도 변경, 리소스 교체 없음. 모든 파라미터에 `UsePreviousValue=true` 적용 |
| 실제 배포 API | PASS | me/leave/한글 직원/history/월 달력, 기본 20명·all 120명·offset 페이지, 0.5일 POST 201와 작성자 필터 GET 200 |
| 배포 코드·오리진 | PASS | Lambda의 handler/lab_api/lab_company 3개가 원본과 바이트 일치, Lambda/CloudFront 비밀 헤더 일치 |
| 실제 승인 전환·공개 문서 | PASS | 0.5일 신청이 2분 후 approved로 조회됨. CloudFront HTML이 로컬 생성물과 바이트 일치, invalidation Completed |
| 사본 동기화 | PASS | 원본 infra/lambda와 superlab/tools의 lab_api/lab_company 동일. 별도 실습 폴더의 API·회사 데이터·서버·MCP 4개도 동일 |

실제 응답 크기(UTF-8 JSON 본문): 직원 기본 20명 19,381바이트, `limit=all` 120명 114,873바이트, 그로스팀 연차 11,184바이트, 10월 달력 전체 74,068바이트. 실제 값과 크기는 조회 시각에 따라 달라진다.

Lab3 문서는 한국어 이름·발생/이월/예정/대기·사용 날짜·6개 MCP 도구·페이지 조회·신청 비차감 원칙에 맞췄다. Claude Code 대화형 세션에서의 참가자 전체 수행과 승인 창 동작, 120명 동시 부하 시험은 이번 검증 범위에 포함하지 않았다.
