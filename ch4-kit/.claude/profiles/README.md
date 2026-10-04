# 설정 프리셋

| 프리셋 | defaultMode | 허용 | 차단 | 쓰는 자리 | 블록1에서 관찰할 차이 |
|---|---|---|---|---|---|
| `personal` | `acceptEdits` | npm·git 작업과 편집 자동 수락 | `.env` 읽기·편집 | 개인 실습 | 편집은 바로 진행되지만 비밀 파일은 막힌다 |
| `team` | 기본값 | 테스트와 읽기 전용 git, HR 조회 | `.env`, 삭제·외부 전송 | 일반 팀 저장소 | 편집·push·HR 요청은 확인을 요구한다 |
| `regulated` | `auto` | 팀 프리셋과 동일 | 팀 차단 항목과 kubectl·AWS·Docker, 작업 폴더 외부 복사 | 통제된 환경 | 모든 셸 명령을 분류하고 강한 울타리를 적용한다 |

다음처럼 원하는 프리셋을 지정해 Claude Code를 시작한다.

```bash
claude --settings .claude/profiles/<name>.json
```

`autoMode`는 User·Managed·`--settings` 경로에서만 읽힌다.
