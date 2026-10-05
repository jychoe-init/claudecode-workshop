# 워크샵 공용 사내 API (infra)

Claude Code 워크샵 lab2·lab3에서 참가자 120명이 함께 쓰는 superlab(주식회사 슈퍼랩) HR·배포·메일·일정 Mock API. 모든 토큰에서 같은 120명 조직과 그로스팀 데이터를 본다. API 버전은 `2026-10-06`이다.

```
참가자 → CloudFront ─ /          → S3 (문서 페이지 site/index.html)
                    └ /v1/*      → CloudFront Function(토큰 형식 검사) → API Gateway HTTP API → Lambda → DynamoDB
```

퍼블릭 Lambda Function URL은 계정 정책으로 막혀 있어서 HTTP API를 오리진으로 쓴다. CloudFront가 붙이는 비밀 헤더(`x-lab-origin`)가 없으면 Lambda가 403을 돌려주므로 API Gateway 주소로 직접 들어와도 막힌다.

## 참가자 권한

- 참가자에게는 AWS 자격증명이나 IAM 권한을 주지 않는다. 배포된 LAB 안내서에서 확인하는 공통 토큰 `lab-xxxxxxxx` 하나로 CloudFront `/v1/*` 엔드포인트만 호출한다.
- 조회 데이터는 `random.Random("superlab-2026:<키>")`로 생성한 결정적 테스트 데이터다. 회사는 토큰과 무관하게 하나이고, 내 팀은 그로스팀이다. 쓰기는 연차 신청(`REQ#<token>`, 30일 TTL)뿐이고, 잔여 검사는 신청 한 건 기준이라 여럿이 신청해도 서로 막지 않는다.
- Lambda 역할 권한은 이 테이블에 대한 `GetItem`/`PutItem`/`UpdateItem`/`Query`뿐이다.
- 비밀값(`OriginSecret`, 토큰 CSV)은 배포하거나 토큰을 만들 때 생성되고 저장소에는 남지 않는다. 테스트 코드의 토큰은 DynamoDB에 등록되지 않은 테스트 값이다.

## 엔드포인트 (`Authorization: Bearer <LAB_TOKEN>`)

전체 쿼리·응답 예시·필드 정의·오류·계산식은 [API.md](API.md)에 있다. 목록은 기본 20건(이력 100건)이며 `limit`, `offset`으로 나눈다. 전체가 필요하면 `limit=all`을 지정한다. 실시간 신청은 최근 500건 안에서 조회한다. 문서 HTML은 `python3 infra/scripts/build_api_docs.py`로 다시 만든다.

| 경로 | 설명 |
|---|---|
| `GET /v1/company`, `/v1/org`, `/v1/me` | 회사·조직·내 프로필(그로스팀 팀장) |
| `GET /v1/employees`, `/v1/employees/{직원}` | 소속·직무·고용·연락처·주소·연차 현황 |
| `GET /v1/holidays`, `/v1/leave/policy` | 업무 달력·연차 정책 |
| `GET /v1/leave`, `/v1/leave/{직원}` | 발생·이월·사용·예정·대기·잔여·사용 날짜 |
| `GET /v1/leave/history`, `/v1/leave/calendar`, `/v1/leave/stats` | 이력 필터·페이지, 날짜별 부재·경고, 사용률 집계 |
| `GET /v1/leave/requests`, `POST /v1/leave/requests` | 참가자 신청. 0.5일 지원, 잔여 초과 409, 조회 시 2분/10분 후 승인 표시 |
| `GET /v1/deploys` | 서비스 배포 상태, 제품개발부문 직원 이름 |
| `GET /v1/mail/{box}/sent`, `GET /v1/calendar/{box}` | planning·sales·cs·hr 팀의 메일 7통·일정 7건. box 생략 시 planning |

제한은 토큰당 분당 6000회, API Gateway 초당 200회·버스트 400이다. CORS는 제공하지 않는다. 실시간 신청은 참가자끼리 실습을 막지 않도록 연차 잔액·고정 이력에 반영하지 않는다. 로그는 토큰 앞 4자리만 남기며 쿼리의 참가자 표시값은 기록하지 않는다.

## 파일

| 경로 | 역할 |
|---|---|
| `template.yaml` | CloudFormation (CloudFront·CF Function·HTTP API·Lambda·DynamoDB·S3·OAC) |
| `lambda/lab_company.py` | 120명 조직·2025/2026 휴가 기록·업무 달력·연차 계산. `superlab/tools/lab_company.py`와 동일 |
| `lambda/lab_api.py` | API 코어. `superlab/tools/lab_api.py`와 **같은 파일**(로컬 대체 서버가 공유) |
| `lambda/handler.py` | HTTP API payload 2.0 핸들러, DynamoDB Store |
| `scripts/make_tokens.py` | 토큰 생성 + DynamoDB 등록. CSV는 저장소 밖 |
| `site/index.html` | 참가자용 API 문서 페이지 |
| `tests/test_lab_api.py` | 코어 단위 테스트 |

## 기존 스택 갱신

```bash
PROFILE=<your-profile> REGION=ap-northeast-2 PREFIX=ccw-lab
# AWS 프로파일 자격증명을 먼저 갱신한다.
BUCKET=$PREFIX-cfn-artifacts-$(aws sts get-caller-identity --profile "$PROFILE" --query Account --output text)
PYTHONDONTWRITEBYTECODE=1 python3 infra/tests/test_lab_api.py
aws cloudformation package --template-file infra/template.yaml --s3-bucket "$BUCKET" \
  --output-template-file /tmp/ccw-packaged.yaml --profile "$PROFILE" --region "$REGION"
# OriginSecret을 생략하면 CLI가 기존 스택 파라미터를 UsePreviousValue=true로 전달한다.
# 기존 스택 갱신 시 SECRET을 새로 생성하거나 OriginSecret=...으로 덮어쓰지 않는다.
aws cloudformation deploy --template-file /tmp/ccw-packaged.yaml --stack-name "$PREFIX" \
  --capabilities CAPABILITY_IAM --parameter-overrides StackPrefix="$PREFIX" \
  --profile "$PROFILE" --region "$REGION"
# 문서 업로드. 캐시가 남지 않게 CloudFront invalidation도 수행한다.
SITE_BUCKET=$(aws cloudformation describe-stacks --stack-name "$PREFIX" \
  --query "Stacks[0].Outputs[?OutputKey=='SiteBucket'].OutputValue" --output text --profile "$PROFILE" --region "$REGION")
aws s3 cp infra/site/index.html "s3://$SITE_BUCKET/index.html" \
  --content-type 'text/html; charset=utf-8' --profile "$PROFILE" --region "$REGION"
DISTRIBUTION_ID=$(aws cloudformation describe-stack-resource --stack-name "$PREFIX" --logical-resource-id Distribution \
  --query StackResourceDetail.PhysicalResourceId --output text --profile "$PROFILE" --region "$REGION")
aws cloudfront create-invalidation --distribution-id "$DISTRIBUTION_ID" --paths / /index.html --profile "$PROFILE"
```

배포 전 `infra/lambda` 안에는 배포할 `.py` 파일만 둔다(`__pycache__`를 패키지에 넣지 않는다). `lab_api.py`, `lab_company.py`는 `superlab/tools`와 바이트 단위로 같아야 한다. 배포 후 한글 직원 경로·쿼리 필터·0.5일 POST·실시간 목록을 실제 CloudFront 주소로 검증한다. 도메인·토큰·OriginSecret은 공개 저장소에 기록하지 않는다. `hr_mcp.py`의 `DEFAULT_BASE`는 `REPLACE-AFTER-DEPLOY`를 유지한다.

새 스택은 최초 생성 때만 OriginSecret을 별도로 공급한다. 기존 스택과 Lambda·CloudFront의 비밀 헤더를 함께 유지하는 위 갱신 절차와 구분한다.

## 토큰

```bash
python3 infra/scripts/make_tokens.py --count 1 --expires 2026-10-08 --table $PREFIX-api \
  --out ~/Downloads/ccw-tokens.csv --profile $PROFILE --region $REGION
```

공통 토큰 하나를 만든다. 참가자는 API 주소와 함께 배포된 LAB 안내서에서 확인한다. CSV는 저장소에 넣지 않는다. 만료일이 지나면 403.

## 운영 중 확인

```bash
aws logs tail /aws/lambda/$PREFIX-api --since 10m --profile $PROFILE --region $REGION   # token 앞 4자리·경로·상태
aws dynamodb scan --table-name $PREFIX-api --filter-expression 'begins_with(pk, :p)' \
  --expression-attribute-values '{":p":{"S":"REQ#"}}' --select COUNT --profile $PROFILE --region $REGION
```

## 삭제

```bash
aws s3 rm s3://$PREFIX-site-<account>/ --recursive --profile $PROFILE --region $REGION
aws cloudformation delete-stack --stack-name $PREFIX --profile $PROFILE --region $REGION
```
