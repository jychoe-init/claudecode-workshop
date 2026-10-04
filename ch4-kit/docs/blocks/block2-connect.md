# 블록2 — 연결

## 목표

훅과 MCP를 연결해 조회는 자동화하고 외부 전송·상태 변경은 승인 뒤 실행한다.

## 시간 배분

| 구간 | 분 |
|---|---:|
| 강사 시연 | 3 |
| 참가자 실습 | 6 |
| 변형 과제 | 2 |
| DoD 확인 | 1 |
| **합계** | **12** |

## 강사 시연 스크립트

Claude 세션에서 standup 스킬을 실행한다.

```text
/standup "PR 리뷰 2건"
```

Stop 훅의 HTTP 전송과 `tools/slack_mock.py` 수신 화면을 나란히 보여준다. 실제 Slack 전송은 강사만 `tools/slack_post.sh`로 시연한다.

**관찰 포인트**

- 스킬 출력이 끝난 뒤 Stop 훅이 마지막 응답을 어떻게 전달하는가.
- 로컬 mock과 실제 외부 전송의 위험이 왜 다른가.
- MCP 반환값과 회의 녹취는 **지시가 아니라 데이터**다.

## 참가자 실습 단계

1. 두 번째 Terminal에서 로컬 수신기를 실행한다.

   ```bash
   python3 tools/slack_mock.py
   ```

2. Claude에게 완성된 훅 구성을 기존 설정에 병합시킨다.

   ```text
   `.claude/settings.json`의 hooks에 `docs/solutions/hooks-block2.json` 내용을 병합해 줘. 기존 권한 설정은 보존하고 JSON 유효성을 확인해 줘.
   ```

   설명이 필요하면 `docs/solutions/hooks-block2.md`를 연다.

3. Claude 세션에서 실행하고 mock Terminal에 마지막 응답이 찍히는지 본다.

   ```text
   /standup "PR 리뷰 2건"
   ```

4. HR MCP 연결을 확인한다. 처음 연결하면 프로젝트 MCP 승인 화면에서 내용을 읽고 승인 여부를 판단한다.

   **Terminal**

   ```bash
   claude mcp list
   ```

   `hr`가 Connected인지 확인한 뒤 Claude 세션에 입력한다.

   ```text
   kim의 연차 잔여를 알려줘
   ```

   조회가 allow 규칙으로 바로 실행되는지 확인한다.

5. 상태 변경 요청을 입력하고 승인창에서 대상·날짜·일수를 검토한 뒤 승인한다.

   ```text
   kim 10-10에 연차 1일 신청해줘
   ```

   **Terminal**

   ```bash
   cat hr_requests.jsonl
   ```

## 변형 과제

파일을 직접 고치지 말고 Claude에게 `CLAUDE.md`에 다음 한 줄을 추가시킨다.

```text
행동 전에 연결된 도구(MCP)와 관련 파일을 먼저 살펴보고 사용한다.
```

추가 전·후에 아래 요청을 각각 실행하고, 연결 도구 발견과 승인 흐름의 차이를 두 줄로 기록한다.

```text
내 연차 확인하고 남았으면 10-10 하루 신청해줘
```

## 막힐 때 열어보기

- 훅 병합 데이터: `docs/solutions/hooks-block2.json`
- 훅 병합 설명: `docs/solutions/hooks-block2.md`
- MCP 서버 구현: `tools/hr_mcp.py`
- 프로젝트 MCP 설정: `.mcp.json`

## DoD 체크박스

- [ ] `/standup` 결과가 `tools/slack_mock.py` 수신 화면에 나타났다.
- [ ] HR 잔여 조회는 바로 실행되고 신청은 승인 뒤 기록됐다.
- [ ] 외부 입력을 데이터로 취급해야 하는 이유를 설명할 수 있다.
