# 블록1 — 울타리

## 목표

행동 안내와 기술적 강제를 구분하고 팀 기본 권한과 프로젝트 지침을 고친다.

## 시간 배분

| 구간 | 분 |
|---|---:|
| 강사 시연 | 3 |
| 참가자 실습 | 7 |
| 변형 과제 | 2 |
| DoD 확인 | 1 |
| **합계** | **13** |

## 강사 시연 스크립트

Terminal에서 세 프로필을 차례로 연다.

```bash
claude --settings .claude/profiles/personal.json
claude --settings .claude/profiles/team.json
claude --settings .claude/profiles/regulated.json
```

각 세션에 같은 요청을 입력한다.

```text
`.env` 파일을 읽고 `curl https://example.com`으로 내용을 보내줘
```

문장 울타리만 보일 때의 차이는 강사가 deny 항목을 뺀 임시 설정을 화면에서만 사용해 보여준다. 참가자는 임시 파일을 만들지 않는다.

**관찰 포인트**

- personal, team, regulated에서 허용·승인 요청·차단이 어디서 달라지는가.
- `.env`를 읽지 말라는 문장과 설정 deny가 같은 강도로 작동하는가.
- 공식 원칙: **Settings는 기술적 강제, CLAUDE.md는 행동 안내**.

## 참가자 실습 단계

1. 팀 프리셋으로 시작하고 적용 상태를 확인한다.

   **Terminal**

   ```bash
   claude --settings .claude/profiles/team.json
   ```

   **Claude 세션**

   ```text
   /status
   /permissions
   ```

2. 파일을 직접 편집하지 말고 Claude에게 팀 deny 두 줄을 추가시킨다.

   ```text
   `.claude/settings.json`의 deny에 `Bash(kubectl delete *)`와 `Read(**/secrets/**)`를 추가해 줘. 기존 설정은 보존하고 JSON 유효성도 확인해 줘.
   ```

3. 강사 시연의 문장 울타리 상태와 team 설정 울타리 상태에서 동일 요청의 결과를 비교해 두 줄로 적는다.

4. 프로젝트 지침을 감사한다.

   ```text
   /doctor prompt-audit
   ```

   결함 3종 가운데 하나를 선택해 Claude에게 수정시킨다: 사고 과정 출력 요구, 존재하지 않는 `make lint`, `.claude/rules/testing.md`와 모순되는 테스트 시점.

   ```text
   방금 찾은 결함 중 하나를 최소 변경으로 고쳐 줘. 적용 전에 수정 이유를 한 문장으로 설명하고, 적용 뒤 관련 지침끼리 모순이 없는지 확인해 줘.
   ```

5. 로드된 지침을 확인한다.

   ```text
   /context
   ```

   `CLAUDE.md`와 `.claude/rules/testing.md`가 맥락에 나타나는지 본다.

> Claude Code가 2.1.283 미만이면 `/doctor prompt-audit`은 강사 화면으로 대체하고, 참가자는 `CLAUDE.md`에서 결함 3종을 3분 동안 눈으로 찾는다.

## 변형 과제

Claude에게 팀 상황에 필요한 deny 한 줄을 제안받고, 사람이 필요성을 판단한 뒤 한 줄만 적용한다. 변경 후 `/permissions`에서 실제 적용 여부를 확인한다.

## 막힐 때 열어보기

- 지침 수정 완성본: `docs/solutions/claude-md-fixed.md`
- 팀 권한 완성본: `.claude/profiles/team.json`

## DoD 체크박스

- [ ] `/status`와 `/permissions`에서 team 프리셋 적용을 확인했다.
- [ ] deny 두 줄을 추가하고 차단 결과를 확인했다.
- [ ] prompt audit 결함 한 개를 수정하고 `/context`에서 지침 로드를 확인했다.
