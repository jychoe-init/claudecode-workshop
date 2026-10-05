# superlab HR Mock API — 2026-10-06

회사 이름은 `superlab`(주식회사 슈퍼랩)이다. 이 API는 참가자 120명이 각각 프런트엔드를 구성할 수 있는 테스트 데이터를 제공한다. 120명의 직원 명부·휴가 기록은 토큰과 무관하게 동일하며, 내 팀은 항상 `growth`(그로스팀), `/v1/me.me`는 팀장 김민준이다. 사번·메일은 고유하며 동명이인은 존재한다.

주소와 토큰은 배포된 실습 안내에서 받는다. 공개 저장소에는 실제 BaseUrl이나 토큰을 넣지 않는다. 클라이언트는 서버/MCP/로컬 프록시에서 호출한다. 브라우저 직접 호출용 CORS는 제공하지 않는다.

## 공통 계약

- 인증: `Authorization: Bearer <LAB_TOKEN>`. 미등록·만료 토큰은 403. CloudFront 경유 요청만 허용한다.
- JSON UTF-8, 날짜 `YYYY-MM-DD`, 시각 ISO 8601(시간대 포함). 날짜·연차·당일 사용 계산은 `Asia/Seoul` 기준이다.
- 데이터 연도는 2025·2026. `year` 기본값은 조회 시점의 연도, `month` 기본값은 조회 시점의 월이다. 지원 범위 밖은 400이다.
- 조직 코드는 아래 표 참조. `team`, `division` 필터는 코드 또는 한국어 이름, `all`을 받는다. 잘못된 필터값은 400. 여러 필터는 AND로 적용한다.
- 직원 지정은 사번, 한국어 이름, 영문 이름, 이메일 전체, 메일 아이디의 정확한 일치(영문 대소문자 무시)다. 여러 명이면 그로스팀을 우선하고, 여전히 여러 명이면 409와 `candidates`를 반환한다. 한글·공백·메일 경로 조각은 URL 인코딩한다.
- 레이트리밋은 토큰당 분당 6000회. API Gateway는 초당 200회, 버스트 400회다.
- 회사·연도별 원본은 고정 시드로 생성·캐시한다. 승인·취소·부재·퇴사 상태는 매 조회 시각에 계산한다. `requested_at`이 미래인 휴가 기록은 노출하지 않는다.
- 명부 인원은 고정 120명으로 퇴사·휴직 직원도 포함한다. 실제 근무 상태는 `status`, 날짜별 인원은 휴가 캘린더의 `headcount`로 구분한다.

## 엔드포인트와 쿼리

| 메서드·경로 | 쿼리 | 응답 |
|---|---|---|
| GET `/v1/company` | 없음 | `name`, `legal_name`, `employee_count`, `founded_on`, `industry`, `offices`, `timezone`, `data_type`, `api_version` |
| GET `/v1/org` | `limit`, `offset` | `company`, `employee_count`, `divisions[]` → `teams[]` |
| GET `/v1/me` | `limit`, `offset` | `token_hint`, `team`, `team_name`, `me`(직원 객체), `members[]`, `api_version` |
| GET `/v1/employees` | `team`, `division`, `status`, `role`, `q`, `limit`, `offset` | `employees[]`, `total`, `as_of`. `q`는 사번·이름·메일·소속·직위·직책 부분 검색 |
| GET `/v1/employees/{직원}` | 없음 | 직원 객체와 `leave_balance` |
| GET `/v1/holidays` | `year`, `limit`, `offset` | `year`, `holidays[]`의 `date`, `name`, `note` |
| GET `/v1/leave/policy` | 없음 | 연차 발생·이월·종류·계산식·실시간 신청 원칙 |
| GET `/v1/leave` | `team`(기본 growth, all 가능), `division`, `limit`, `offset` | `team`, `as_of`, `balances[]` |
| GET `/v1/leave/{직원}` | 없음 | `as_of`와 연차 현황 객체. 다른 팀 직원도 조회 가능 |
| GET `/v1/leave/history` | `year`, `team`, `division`, `employee`, `type`, `status`, `from`, `to`, `limit`, `offset` | `history[]`, `year`, `as_of`, 페이지 메타데이터. 기간 필터는 시작~종료 구간 겹침 |
| GET `/v1/leave/calendar` | `month=YYYY-MM`, `team`, `division`, `limit`, `offset` | `month`, `as_of`, `days[]`, `alerts[]` |
| GET `/v1/leave/stats` | `year`, `team`, `division`, `limit`, `offset` | `summary`, `by_month[]`, `by_type[]`, `by_team[]`, `company_average`, `as_of` |
| POST `/v1/leave/requests` | 없음 | 신청 본문을 받아 201 pending. 아래 신청 계약 참조 |
| GET `/v1/leave/requests` | `status=pending\|approved`, `employee`, `requested_by`, `team`, `limit`, `offset` | `team`, `requests[]`, `window_limit=500`, 페이지 메타데이터 |
| GET `/v1/deploys` | `limit`, `offset` | `team`, `deploys[]` |
| GET `/v1/mail/{box}/sent` | `limit`, `offset` | Graph message 형태 `value[]`(7통). `/v1/mail/sent`는 planning |
| GET `/v1/calendar/{box}` | `limit`, `offset` | Graph event 형태 `value[]`(7건). `/v1/calendar`는 planning |

## 제한 조회와 전체 조회

모든 목록은 `limit`, `offset`을 지원한다. 기본은 20건·숫자 최댓값은 100건이며, 휴가 이력(`/v1/leave/history`)만 기본 100건·숫자 최댓값 1000건이다. `limit`은 1 이상의 정수 또는 문자열 `all`, `offset`은 0 이상의 정수다. 잘못된 값은 400 `bad_query`다.

- `limit=10&offset=20`: 필터 결과의 21번째부터 최대 10건.
- `limit=all`: 필터 결과 전체. 기본값으로 사용하지 않으며, 전체가 필요할 때 명시한다.
- `limit=all&offset=20`: 필터 결과의 21번째부터 끝까지. offset은 그대로 적용한다.
- `team=all`은 소속 필터 해제이고, `limit=all`은 개수 제한 해제다. 전사 연차 전체는 `/v1/leave?team=all&limit=all`이다.
- 응답의 `total`은 필터 후 전체 개수, `limit`은 숫자 또는 `"all"`, `offset`은 시작 위치, `next_offset`은 다음 시작 위치다. 마지막 페이지 또는 all이면 next_offset은 null이다. 범위 밖 offset은 빈 목록을 반환한다.
- 실시간 신청은 최근 500건 안에서 필터한다. `limit=all`과 `total`도 이 범위에 한정되며 `window_limit=500`을 함께 반환한다. 신청 목록은 토큰별로 분리한다.

| 경로 | 페이지를 나누는 목록 |
|---|---|
| `/v1/org` | `divisions` |
| `/v1/me` | `members` |
| `/v1/employees` | `employees` |
| `/v1/holidays` | `holidays` |
| `/v1/leave` | `balances` |
| `/v1/leave/history` | `history` |
| `/v1/leave/calendar` | `days` |
| `/v1/leave/stats` | `by_team` |
| `/v1/leave/requests` | `requests` |
| `/v1/deploys` | `deploys` |
| `/v1/mail/{box}/sent` | `value` |
| `/v1/calendar/{box}` | `value` |

휴가 달력은 날짜 단위로 나누며 `alerts`는 반환된 날짜에 해당하는 경고만 포함한다. 달 전체는 `month=2026-10&limit=all`로 조회한다. 통계는 `by_team`만 페이지를 나누며 `summary`, `company_average`, 12개월 `by_month`, 9종 `by_type`은 항상 동일한 전체 집계다. 회사 개요·정책·직원 상세·개인 연차는 단일 객체이므로 페이지를 나누지 않는다. 직원·연차 목록은 생성된 사번 순, 이력은 시작일·기록 ID 내림차순, 실시간 신청은 최근 접수 순이다. 실시간 목록은 새 신청이 들어오면 offset 위치가 바뀔 수 있으므로 접수 ID로 중복을 구분한다.

```text
GET /v1/employees?limit=20&offset=0
GET /v1/employees?team=growth&limit=all
GET /v1/leave?team=all&limit=all
GET /v1/leave/history?team=growth&limit=10&offset=0
GET /v1/leave/calendar?month=2026-10&limit=all
GET /v1/leave/requests?requested_by=participant-01&limit=all
```

MCP 조회 도구도 `limit`, `offset`을 받고 응답의 페이지 정보를 유지한다. `get_leave_requests`에는 `employee`, `team`, `status`, `requested_by` 필터도 있다. 도구 개수는 기존 6개다.

## 조직

| 부문 코드 | 팀 코드·이름·인원 |
|---|---|
| executive / 경영진 | 대표이사 1명(team=null), ceo-office / 대표이사실 1명(비서실장) |
| product / 제품개발부문 | 부문장 1명(team=null), platform / 플랫폼 11, payments / 결제 9, frontend / 프론트엔드 8, data / 데이터 10, growth / 그로스 8 |
| business / 사업부문 | 부문장 1명(team=null), planning / 사업기획 8, sales1 / 영업1 10, sales2 / 영업2 8, marketing / 마케팅 8, cs / 고객지원 12 |
| corporate / 경영지원부문 | 부문장 1명(team=null), hr / 인사 7, finance / 재무 7, legal / 법무 4, general / 총무 5 |

조직 응답의 부문은 `code`, `name`, `headcount`, `head_id`, `head`, `teams`를 갖는다. 팀은 `code`, `name`, `headcount`, `leader_id`, `leader`, `leader_vacant`를 갖는다. 법무팀은 팀장 공석으로 leader가 null이며 부문장에게 보고한다.

## 직원 필드

| 필드 | 형식·의미 |
|---|---|
| `id` | 문자열. `SL{입사연도2자리}{3자리 순번}` |
| `name`, `name_en` | 한국어 표시 이름, 영문 이름. 김지훈 동명이인과 장문 이름 알렉산드라 페트로바 포함 |
| `email`, `extension` | `given.surname@superlab.example`, 중복 시 숫자 접미사. 내선은 문자열 |
| `division`, `division_name`, `team`, `team_name` | 부문·팀 코드와 표시 이름. 대표이사·부문장의 team/team_name은 null |
| `title`, `position` | 직위·직급(사원~부장, 이사·상무·대표이사), 직책(팀원·팀장·부문장·비서실장·대표이사) |
| `role`, `role_label` | 직무 코드·한국어 이름. backend, frontend, data, pm, qa, sre, planning, sales, marketing, cs, hr, finance, legal, general, ceo, division_head, secretary |
| `employment_type` | regular / contract / intern |
| `joined_on`, `contract_end`, `last_day` | 입사일, 계약 종료일(null 가능), 마지막 근무일(null 가능) |
| `manager_id`, `manager` | 보고 대상 사번·이름. 대표이사는 null |
| `office` | `code`(hq/pangyo/busan), `name`, `address`, `zip` 문자열 |
| `home_area` | 거주 시·구. 상세 거주지 주소는 제공하지 않음 |
| `work_type` | office / hybrid / remote |
| `status` | active / on_leave(승인된 육아휴직 기간) / leaving(퇴사 예정 월) / resigned(마지막 근무일 또는 계약 종료일 다음 날부터) |
| `leave_balance` | 아래 연차 현황 중 숫자·발생·만료·미차감 집계 필드. 직원 목록에는 history를 중복 포함하지 않음 |

## 연차 현황과 계산

| 필드 | 의미 |
|---|---|
| `employee`, `employee_id`, `team`, `team_name` | 직원 이름·사번·소속 |
| `role`, `role_label`, `title`, `position` | 직무·직위·직책 |
| `annual`, `accrual` | 조회 시점 발생 일수. monthly / yearly |
| `carried_over`, `total` | 전년도 이월, 발생+이월 |
| `used`, `scheduled`, `pending` | 승인된 차감 휴가 중 오늘까지 사용, 내일 이후 예정, 아직 승인 대기인 차감 일수 |
| `remaining`, `expiring`, `expires_on` | 사용할 수 있는 잔여, 이월 한도 초과분, 해당 연도 12월 31일 |
| `usage_rate` | used/total×100, 소수 둘째 자리 반올림. total=0이면 0 |
| `other_used` | 미차감 종류별 오늘까지 사용 일수. 예: `{"official":1,"sick":2}` |
| `history` | 해당 연도와 겹치는 신청된 기록의 간단 목록. `start`, `end`, `days`, `type`, `status` |

```text
근속연수 = 입사일 기준 만 나이 방식으로 계산
입사 1년 미만: annual = min(11, 입사일 기준 만근한 개월 수)
입사 1년 이상: annual = min(25, 15 + max(0, floor((근속연수 - 1) / 2)))
carried_over = min(3, 전년도 말 remaining)  # 2025는 0, 2026은 2025 기록으로 계산
 total = annual + carried_over
 remaining = total - used - scheduled - pending
 expiring = max(0, remaining - 3)
 usage_rate = used / total * 100
```

당일은 사용일에 포함한다. 여러 날의 승인 건은 영업일별로 분할하여 used/scheduled를 나눈다. pending은 기간이 지났어도 승인 전까지 따로 예약한다. 반려·취소는 잔액을 차감하지 않는다. 미차감 휴가는 other_used에만 합산한다. 미래 연도 통계는 해당 연도에 걸친 기록만 합산한다. 퇴사자의 발생 기준일은 마지막 근무일로 제한한다. 이는 워크샵 Mock 정책이며 실제 급여·법정 연차 산정 지침이 아니다.

## 휴가 이력 필드와 종류

| 필드 | 의미 |
|---|---|
| `id`, `employee_id`, `employee`, `team` | 기록 ID, 사번, 이름, 팀 코드 |
| `type`, `type_label`, `deducted` | 종류, 표시명, 연차 차감 여부(bool) |
| `start`, `end`, `days` | 시작·종료(양 끝 포함), 주말·업무 달력 휴일을 제외한 영업일수 |
| `status`, `status_label` | pending/approved/rejected/cancelled, 승인 대기/승인/반려/취소 |
| `reason`, `rejection_reason` | 사유, 반려 후에만 표시하는 반려 사유(그 외 null) |
| `requested_at`, `decided_at`, `cancelled_at` | 신청·결정·취소 시각. 결정 전/취소 전에는 해당 시각을 null로 표시 |
| `approver_id`, `approver` | 결재자 사번·이름, 대표이사 본인은 null |
| `when` | past(종료일<오늘), ongoing(기간에 오늘 포함), upcoming(시작일>오늘) |

| type | 표시명 | 연차 차감 | 일수 |
|---|---|---|---|
| annual | 연차 | 예 | 기본 1. 기존 호환으로 0.25 단위 신청도 가능 |
| half_am / half_pm | 오전/오후 반차 | 예 | 반드시 0.5 |
| quarter | 반반차 | 예 | 반드시 0.25 |
| sick | 병가 | 아니오 | 영업일수 |
| official | 공가 | 아니오 | 건강검진 등 |
| family_event | 경조휴가 | 아니오 | 기록은 결혼 5일·조부모상 3일·배우자 출산 10일 |
| refresh | 리프레시 휴가 | 아니오 | 기록은 근속 5년 단위 5일 |
| parental | 육아휴직 | 아니오 | 데이터팀 2026-06-01~2027-05-31 기록 포함 |

업무 달력은 `/v1/holidays`에서 확인한다. 2025-05-01도 회사 유급휴일로 제외한다. 2026-07-17은 휴일이며, 2026-09-28과 2026-06-08은 평일이다. 육아휴직의 전체 days에는 2027-05-31까지의 업무 달력을 적용하고 연도별 집계에는 해당 연도 날짜만 포함한다.

## 실시간 신청

```json
{"employee":"김민준","date":"2026-10-20","days":0.5,"type":"half_pm","reason":"개인 일정","requested_by":"participant-01"}
```

필수는 employee/date/days, type 기본 annual, reason 기본 빈 문자열(최대 100자), requested_by 기본 빈 문자열(최대 30자)이다. 본문 requested_by가 없으면 `X-Lab-User`를 사용한다. MCP는 `LAB_USER` 환경 변수를 이 헤더로 보낸다. 이는 참가자 식별용 표시값으로 인증·접근 통제를 대신하지 않는다.

- days는 유한 숫자, 0 초과 366 이하, 0.25 단위. 반차·반반차는 지정 일수만, 미차감 종류는 정수만 받는다. date는 2025~2026년의 유효한 날짜여야 하며, 계산된 종료일은 지원 업무 달력의 마지막 날인 2027-05-31을 넘을 수 없다.
- 퇴사자는 409 `employee_resigned`. 차감 종류가 현재 remaining보다 크면 409 `insufficient_balance`. 경조/리프레시 종류의 세부 자격·일수 제한은 실시간 신청에서 강제하지 않는다.
- 주말·휴일·과거·승인/대기 기록과 겹침은 각각 `weekend`, `holiday`, `past_date`, `overlap` 경고를 반환한다. 201 신청은 유지한다. 휴일 시작 날짜를 보존하고 다음 영업일부터 days를 배분하여 end를 계산한다.
- 201 응답은 `request_id=REQ-`+영문 대문자/숫자 6자리, `employee`, `employee_id`, `date`, `start`, `end`, `days`, `type`, `type_label`, `deducted`, `team`, `team_name`, `approver_id`, `approver`, `reason`, `requested_by`, `status`, `status_label`, `requested_at`, `decided_at`, `warnings[]`다. 경고는 `{code,message}` 객체다.
- 저장 상태는 pending. 조회 시 신청 후 2분(3일 이상은 10분)이 지나면 approved와 decided_at을 계산하여 반환한다. 예약 작업이나 실제 승인 처리는 없다.
- **실시간 신청은 잔액·고정 휴가 이력·캘린더·통계에 반영하지 않는다.** 참가자끼리 서로의 실습을 막지 않기 위해서다. 접수 ID로 실시간 신청 목록에서 확인한다. API로 신청 취소는 지원하지 않는다.

## 캘린더·통계

캘린더 `days[]`에는 date, is_business_day, holiday(null 가능), absentees[], teams[]가 있다. 부재자는 employee_id, employee, team, type, type_label, days(당일 1/0.5/0.25)를 갖는다. 승인 건만 포함한다. 팀 집계는 team, team_name, headcount(그날 재직 인원), absent_count(부재자 고유 인원), absence_rate(인원 비율 %)다. 반차도 부재 인원 1명으로 세며, 40% 이상이면 alerts에 date·팀 집계·message를 넣는다.

통계 summary/company_average/by_team의 집계는 headcount, annual, carried_over, total, used, scheduled, pending, remaining, expiring, usage_rate다. 회사 평균은 필터와 무관하게 120명 전체 used/total로 가중 계산한다. by_team에는 팀 미소속 임원(null)도 포함한다. by_month는 12개월 각각 month, used, scheduled, other_used, usage_rate, by_type은 type, type_label, deducted, used, scheduled, usage_rate를 갖는다. 월/차감 종류의 사용률 분모는 선택 범위의 total이며, 미차감 종류의 usage_rate는 null이다. pending은 summary에만 별도로 합산한다.

## 메일·일정·배포

메일함은 planning→사업기획팀, sales→영업2팀, cs→고객지원팀, hr→인사팀이다. from/organizer는 해당 팀장, toRecipients/attendees 및 본문의 담당자는 해당 팀 실명·메일을 사용한다. 보고 주는 금~일이면 이번 주, 월~목이면 지난주이며, 과거 일정 5건과 오늘 뒤 영업일 일정 2건을 제공한다. 조건부 승인·상대 날짜·전달 메일 속 AI 지시문, 참석자 없는 치과 예약을 실습 상황으로 유지한다.

메일은 id, subject, sentDateTime(UTC), from.emailAddress{name,address}, toRecipients[], bodyPreview, importance를 제공한다. 일정은 id, subject, start/end{dateTime,timeZone}, location.displayName, organizer.emailAddress, attendees[]{emailAddress,type}를 제공한다. 배포 항목은 기존 5개 필드 service, version, status, deployed_at, deployed_by만 제공하며 deployed_by는 제품개발부문 직원 이름이다.

## 오류

오류 형식은 `{"error":"코드","message":"설명"}`이다. ambiguous_employee는 candidates[], insufficient_balance는 remaining을 추가한다.

| HTTP | error | 의미 |
|---|---|---|
| 400 | bad_json | 잘못된 JSON 또는 객체가 아닌 본문 |
| 400 | bad_employee / bad_date / bad_days / bad_type | 필수 직원 식별자·날짜·일수·종류 오류 |
| 400 | bad_reason / bad_requested_by | 문자열 길이 또는 자료형 오류 |
| 400 | bad_query | 필터·페이지·연도·월 값 오류 |
| 401 | unauthorized | 토큰 헤더 없음·형식 오류 |
| 403 | invalid_token / forbidden | 토큰 미등록·만료 / CloudFront 외부 직접 호출 |
| 404 | unknown_employee / unknown_mailbox / not_found | 직원·메일함·경로 없음 |
| 405 | not_found | 알려진 리소스의 미지원 메서드 |
| 409 | ambiguous_employee / employee_resigned / insufficient_balance | 동명이인 / 퇴사 / 잔여 부족 |
| 429 | rate_limited | 토큰 분당 호출 제한 초과 |

API Gateway가 자체 스로틀로 반환하는 429는 위 코어 오류 형식과 다를 수 있다.

## 실제 생성 응답 예시

아래는 고정 조회 시각 `2026-10-06T18:00:00+09:00`으로 생성한 응답이다. 시각에 따라 수치는 달라지므로 실제 응답의 as_of와 숫자를 사용한다.

### 직원 상세

`GET /v1/employees/김민준`

```json
{
  "id": "SL15044",
  "name": "김민준",
  "name_en": "Minjun Kim",
  "email": "minjun.kim@superlab.example",
  "extension": "2044",
  "division": "product",
  "division_name": "제품개발부문",
  "team": "growth",
  "team_name": "그로스팀",
  "title": "과장",
  "position": "팀장",
  "role": "pm",
  "role_label": "프로덕트 매니저",
  "employment_type": "regular",
  "joined_on": "2015-06-15",
  "contract_end": null,
  "last_day": null,
  "manager_id": "SL22002",
  "manager": "이은서",
  "office": {
    "code": "pangyo",
    "name": "판교 연구소",
    "address": "경기도 성남시 분당구 판교역로 166, 슈퍼랩 오피스 8층",
    "zip": "13529"
  },
  "home_area": "서울특별시 송파구",
  "work_type": "office",
  "status": "active",
  "leave_balance": {
    "annual": 20,
    "carried_over": 3,
    "total": 23,
    "used": 9.5,
    "scheduled": 0,
    "pending": 0,
    "remaining": 13.5,
    "expiring": 10.5,
    "expires_on": "2026-12-31",
    "usage_rate": 41.3,
    "other_used": {
      "official": 1
    },
    "accrual": "yearly"
  }
}
```

### 개인 연차

`GET /v1/leave/김민준`

```json
{
  "as_of": "2026-10-06",
  "employee": "김민준",
  "employee_id": "SL15044",
  "team": "growth",
  "team_name": "그로스팀",
  "role": "pm",
  "role_label": "프로덕트 매니저",
  "title": "과장",
  "position": "팀장",
  "annual": 20,
  "carried_over": 3,
  "total": 23,
  "used": 9.5,
  "scheduled": 0,
  "pending": 0,
  "remaining": 13.5,
  "expiring": 10.5,
  "expires_on": "2026-12-31",
  "usage_rate": 41.3,
  "other_used": {
    "official": 1
  },
  "accrual": "yearly",
  "history": [
    {
      "start": "2026-02-04",
      "end": "2026-02-04",
      "days": 0.25,
      "type": "quarter",
      "status": "approved"
    },
    {
      "start": "2026-02-10",
      "end": "2026-02-10",
      "days": 0.5,
      "type": "half_am",
      "status": "approved"
    },
    {
      "start": "2026-02-19",
      "end": "2026-02-19",
      "days": 1,
      "type": "annual",
      "status": "approved"
    },
    {
      "start": "2026-04-16",
      "end": "2026-04-16",
      "days": 1,
      "type": "official",
      "status": "approved"
    },
    {
      "start": "2026-05-14",
      "end": "2026-05-14",
      "days": 0.5,
      "type": "half_am",
      "status": "approved"
    },
    {
      "start": "2026-06-08",
      "end": "2026-06-08",
      "days": 1,
      "type": "annual",
      "status": "approved"
    },
    {
      "start": "2026-07-02",
      "end": "2026-07-02",
      "days": 1,
      "type": "annual",
      "status": "approved"
    },
    {
      "start": "2026-07-20",
      "end": "2026-07-22",
      "days": 3,
      "type": "annual",
      "status": "approved"
    },
    {
      "start": "2026-07-24",
      "end": "2026-07-24",
      "days": 1,
      "type": "annual",
      "status": "approved"
    },
    {
      "start": "2026-09-23",
      "end": "2026-09-23",
      "days": 0.25,
      "type": "quarter",
      "status": "approved"
    },
    {
      "start": "2026-10-06",
      "end": "2026-10-06",
      "days": 1,
      "type": "annual",
      "status": "approved"
    }
  ]
}
```

### 휴가 이력 1건

`GET /v1/leave/history?team=growth&limit=1`

```json
{
  "year": 2026,
  "as_of": "2026-10-06T18:00:00+09:00",
  "history": [
    {
      "id": "LV-2026-SL18047-001",
      "employee_id": "SL18047",
      "employee": "최수빈",
      "team": "growth",
      "type": "annual",
      "type_label": "연차",
      "deducted": true,
      "start": "2026-10-26",
      "end": "2026-10-28",
      "days": 3,
      "status": "pending",
      "reason": "가을 휴가",
      "requested_at": "2026-10-01T09:00:00+09:00",
      "decided_at": null,
      "approver_id": "SL15044",
      "approver": "김민준",
      "rejection_reason": null,
      "cancelled_at": null,
      "status_label": "승인 대기",
      "when": "upcoming"
    }
  ],
  "total": 78,
  "limit": 1,
  "offset": 0,
  "next_offset": 1
}
```

### 반차 신청 결과

`POST /v1/leave/requests` → 201

```json
{
  "request_id": "REQ-VTNMJ7",
  "employee": "김민준",
  "employee_id": "SL15044",
  "date": "2026-10-20",
  "start": "2026-10-20",
  "end": "2026-10-20",
  "days": 0.5,
  "type": "half_pm",
  "type_label": "오후 반차",
  "deducted": true,
  "team": "growth",
  "team_name": "그로스팀",
  "approver_id": "SL22002",
  "approver": "이은서",
  "reason": "개인 일정",
  "requested_by": "participant-01",
  "status": "pending",
  "status_label": "승인 대기",
  "requested_at": "2026-10-06T18:00:00+09:00",
  "decided_at": null,
  "warnings": []
}
```
