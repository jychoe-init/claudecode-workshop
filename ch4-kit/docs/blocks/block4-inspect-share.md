# 블록4 — 점검·배포

## 목표

effort·스킬 로드·사용 기록을 점검하고 새 팀원이 이해할 프로젝트 형태로 커밋한다.

## 시간 배분

| 구간 | 분 |
|---|---:|
| 강사 시연 | 2 |
| 참가자 실습 | 6 |
| 변형 과제 | 1 |
| DoD 확인 | 1 |
| **합계** | **10** |

## 강사 시연 스크립트

Claude 세션에서 현재 effort를 확인한다.

```text
/effort status
```

`.claude/skills/pr-desc/SKILL.md`, `.claude/skills/meeting-notes/SKILL.md`, `.claude/skills/weekly-report/SKILL.md`의 effort 필드와 각 출력 끝 `(effort: …)`을 대조한다.

```text
/skill-doctor
```

**관찰 포인트**

- 세션 effort와 스킬별 effort가 언제 달라지는가.
- 참조형 스킬을 끄기 전·후 같은 리뷰 요청의 체크 범위가 어떻게 달라지는가.
- 사용 기록은 품질 판정이 아니라 다음 개선을 위한 관찰 자료다.

## 참가자 실습 단계

1. `/effort status`와 `/skill-doctor`를 실행해 경고를 읽는다.
2. 파일을 직접 편집하지 말고 Claude에게 프로젝트 로컬 설정에서 `review-checklist`의 `skillOverrides` 값을 `off`로 설정하게 한다. 다른 로컬 설정은 보존한다.
3. 같은 요청을 실행하고 차이를 두 줄로 메모한다.

   ```text
   이 변경을 리뷰해줘
   ```

4. Claude에게 방금 추가한 override만 되돌리게 한 뒤 같은 요청으로 자동 로드를 확인한다.
5. 블록2 훅이 남긴 사용 기록을 확인한다.

   **Terminal**

   ```bash
   cat usage.csv
   ```

6. Claude에게 README를 다시 쓰게 한다.

   ```text
   `.claude` 전체를 훑어 새 팀원이 5분 안에 이해할 `README.md`를 다시 써줘. 스킬별 사용 예시 한 줄을 포함하고 실제 파일과 명령만 써줘.
   ```

7. `.gitignore`에 프로젝트 로컬 설정이 포함돼 커밋에서 제외되는지 확인한 뒤, 오늘 만든 설정·훅·스킬 변경을 팀에 공유할 커밋으로 만든다(저장소는 준비 단계에서 클론한 `claudecode-workshop`이므로 `git init`은 필요 없다. 팀 저장소에 올리려면 `git remote`를 팀 원격으로 바꾼다).

   **Terminal**

   ```bash
   git status --short && git add -A && git commit -m "feat: team starter kit (settings, hooks, skills)" && git log --oneline | head -3
   ```

### 공유 방식

| 방식 | 언제 쓰나 | 이 실습의 범위 |
|---|---|---|
| 프로젝트 커밋 | 한 저장소 팀이 함께 사용할 때 | 지금 수행 |
| 플러그인 패키지 | 여러 저장소에 같은 스킬을 배포할 때 | 매니페스트 구조만 소개 |
| Managed 배포 | 조직이 정책과 설정을 중앙 관리할 때 | 운영 선택지로 소개 |

심화 탐색 명령은 `claude plugin eval`, `/goal`, 헤드리스 `claude -p`다.

## 변형 과제

재작성된 `README.md`를 처음 보는 동료 관점에서 읽고, 시작 명령이나 스킬 예시 중 부족한 한 곳을 판단한 뒤 Claude에게 고치게 한다.

## 막힐 때 열어보기

- 현재 킷 안내: `README.md`
- 스킬 목록: `.claude/skills/`
- 프리셋 설명: `.claude/profiles/README.md`
- 사용 기록 훅: `tools/usage_log.sh`

## DoD 체크박스

- [ ] 스킬 on/off 전·후 같은 리뷰 요청의 차이를 두 줄로 남겼다.
- [ ] `usage.csv`와 스킬 effort를 확인했다.
- [ ] 새 README를 만들고 프로젝트 로컬 설정을 제외한 커밋을 완료했다.
