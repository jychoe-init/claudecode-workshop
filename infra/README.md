# 워크샵 공용 사내 API (infra)

Claude Code 워크샵 lab2(연결)에서 70명이 함께 쓰는 가짜 HR·배포 API. 참가자 토큰마다 다른 팀 데이터가 보인다.

```
참가자 → CloudFront ─ /          → S3 (문서 페이지 site/index.html)
                    └ /v1/*      → CloudFront Function(토큰 형식 검사) → Lambda URL → DynamoDB
```

## 엔드포인트 (`Authorization: Bearer lab-xxxxxxxx`)

| 메서드·경로 | 설명 |
|---|---|
| `GET /v1/me` | 내 토큰의 팀·구성원 |
| `GET /v1/leave` · `GET /v1/leave/{직원}` | 팀/개인 연차 현황 (토큰 해시로 결정 생성) |
| `GET /v1/leave/requests` · `POST /v1/leave/requests` | 내 신청 목록 / 신청 `{"employee","date","days"}` → 201 pending (토큰별 격리) |
| `GET /v1/deploys` | 서비스별 배포 상태 (개발 트랙) |

제한: 토큰당 분당 60회(429). 오류 코드는 `site/index.html` 참조. 로그에는 토큰 앞 4자리만 남는다.

## 파일

| 경로 | 역할 |
|---|---|
| `template.yaml` | CloudFormation (CloudFront·CF Function·Lambda URL·DynamoDB·S3·OAC) |
| `lambda/lab_api.py` | API 코어. `ch4-kit/tools/lab_api.py`와 **같은 파일**(로컬 대체 서버가 공유) |
| `lambda/handler.py` | Function URL 핸들러, DynamoDB Store |
| `scripts/make_tokens.py` | 토큰 생성 + DynamoDB 등록. CSV는 저장소 밖 |
| `site/index.html` | 참가자용 API 문서 페이지 |
| `tests/test_lab_api.py` | 코어 단위 테스트 |

## 배포

```bash
PROFILE=my-isen-profile REGION=us-east-1 PREFIX=ccw-lab
aws sso login --profile $PROFILE
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

CloudFront 배포 완료까지 5~10분. `BaseUrl` 출력값을 `ch4-kit/tools/hr_fetch.py`의 `DEFAULT_BASE`와 `ch4-kit/README.md`에 넣는다.

## 토큰

```bash
python3 infra/scripts/make_tokens.py --count 80 --expires 2026-11-30 --table $PREFIX-api \
  --out ~/Downloads/ccw-tokens.csv --profile $PROFILE --region $REGION
```

CSV(`seq,token,expires_at`)를 참가자 번호별로 배부한다. 저장소에는 넣지 않는다. 만료일이 지나면 403.

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
