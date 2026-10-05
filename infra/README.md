# 워크샵 공용 사내 API (infra)

Claude Code 워크샵 lab2(연결)에서 70명이 함께 쓰는 가짜 HR·배포·메일·일정 API. 실습은 공통 토큰 하나를 함께 써서 모두 같은 팀 데이터를 본다.

```
참가자 → CloudFront ─ /          → S3 (문서 페이지 site/index.html)
                    └ /v1/*      → CloudFront Function(토큰 형식 검사) → API Gateway HTTP API → Lambda → DynamoDB
```

퍼블릭 Lambda Function URL은 계정 정책으로 막혀 있어서 HTTP API를 오리진으로 쓴다. CloudFront가 붙이는 비밀 헤더(`x-lab-origin`)가 없으면 Lambda가 403을 돌려주므로 API Gateway 주소로 직접 들어와도 막힌다.

## 참가자 권한

- 참가자에게는 AWS 자격증명이나 IAM 권한을 주지 않는다. 배포된 LAB 안내서에서 확인하는 공통 토큰 `lab-xxxxxxxx` 하나로 CloudFront `/v1/*` 엔드포인트만 호출한다.
- 조회 데이터는 토큰 해시로 만든 가짜 데이터다. 공통 토큰이라 모두 같은 팀 데이터를 본다. 쓰기는 연차 신청(`REQ#<token>`, 30일 TTL)뿐이고, 잔여 검사는 신청 한 건 기준이라 여럿이 신청해도 서로 막지 않는다.
- Lambda 역할 권한은 이 테이블에 대한 `GetItem`/`PutItem`/`UpdateItem`/`Query`뿐이다.
- 비밀값(`OriginSecret`, 토큰 CSV)은 배포하거나 토큰을 만들 때 생성되고 저장소에는 남지 않는다. 테스트 코드의 토큰은 DynamoDB에 등록되지 않은 가짜 값이다.

## 엔드포인트 (`Authorization: Bearer lab-xxxxxxxx`)

| 메서드·경로 | 설명 |
|---|---|
| `GET /v1/me` | 내 토큰의 팀·구성원 |
| `GET /v1/leave` · `GET /v1/leave/{직원}` | 팀/개인 연차 현황 (토큰 해시로 결정 생성) |
| `GET /v1/leave/requests` · `POST /v1/leave/requests` | 신청 목록(최근 20건, 공통 토큰이면 모두의 신청) / 신청 `{"employee","date","days"}` → 201 pending |
| `GET /v1/deploys` | 서비스별 배포 상태 (개발 트랙) |
| `GET /v1/mail/sent` | 최근 6일 보낸 메일 6통. Microsoft Graph message 형식 `{"value":[…]}` |
| `GET /v1/calendar` | 6일 전~4일 뒤 일정 7건. Microsoft Graph event 형식 `{"value":[…]}` |

제한: 토큰당 분당 3000회(429), API Gateway 초당 100회·버스트 200. 오류 코드는 `site/index.html` 참조. 로그에는 토큰 앞 4자리만 남는다.

## 파일

| 경로 | 역할 |
|---|---|
| `template.yaml` | CloudFormation (CloudFront·CF Function·HTTP API·Lambda·DynamoDB·S3·OAC) |
| `lambda/lab_api.py` | API 코어. `ch4-kit/tools/lab_api.py`와 **같은 파일**(로컬 대체 서버가 공유) |
| `lambda/handler.py` | Function URL 핸들러, DynamoDB Store |
| `scripts/make_tokens.py` | 토큰 생성 + DynamoDB 등록. CSV는 저장소 밖 |
| `site/index.html` | 참가자용 API 문서 페이지 |
| `tests/test_lab_api.py` | 코어 단위 테스트 |

## 배포

```bash
PROFILE=<your-profile> REGION=ap-northeast-2 PREFIX=ccw-lab
# 자격증명 갱신 (예: mwinit -o 후 Isengard 프로파일, 또는 aws sso login --profile $PROFILE)
BUCKET=$PREFIX-cfn-artifacts-$(aws sts get-caller-identity --profile $PROFILE --query Account --output text)
aws s3 mb s3://$BUCKET --profile $PROFILE --region $REGION 2>/dev/null || true
SECRET=$(python3 -c 'import secrets;print(secrets.token_urlsafe(24))')
aws cloudformation package --template-file infra/template.yaml --s3-bucket $BUCKET \
  --output-template-file /tmp/ccw-packaged.yaml --profile $PROFILE --region $REGION
aws cloudformation deploy --template-file /tmp/ccw-packaged.yaml --stack-name $PREFIX \
  --capabilities CAPABILITY_IAM --parameter-overrides OriginSecret=$SECRET StackPrefix=$PREFIX \
  --profile $PROFILE --region $REGION
aws cloudformation describe-stacks --stack-name $PREFIX --query 'Stacks[0].Outputs' --profile $PROFILE --region $REGION
# 문서 페이지 업로드
aws s3 cp infra/site/index.html s3://$(aws cloudformation describe-stacks --stack-name $PREFIX \
  --query "Stacks[0].Outputs[?OutputKey=='SiteBucket'].OutputValue" --output text --profile $PROFILE --region $REGION)/index.html \
  --content-type 'text/html; charset=utf-8' --profile $PROFILE --region $REGION
```

CloudFront 배포 완료까지 5~10분. 참가자는 `BaseUrl` 출력값과 공통 토큰을 배포된 LAB 안내서에서 확인한다. 공개 저장소(`hr_fetch.py`·`hr_mcp.py`의 `DEFAULT_BASE`, README)에는 넣지 않는다.

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
