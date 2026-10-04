"""Lambda Function URL 핸들러. CloudFront 뒤에서만 받는다(비밀 헤더 검사)."""
import base64
import json
import os
import time

import boto3

import lab_api

TABLE = os.environ["TABLE_NAME"]
ORIGIN_SECRET = os.environ.get("ORIGIN_SECRET", "")
_ddb = boto3.resource("dynamodb").Table(TABLE)


class DynamoStore:
    def token_exists(self, token: str) -> bool:
        item = _ddb.get_item(Key={"pk": f"TOKEN#{token}", "sk": "META"}).get("Item")
        if not item:
            return False
        exp = item.get("expires_at")
        return not exp or str(exp) >= time.strftime("%Y-%m-%d")

    def incr_rate(self, token: str, minute_key: str) -> int:
        r = _ddb.update_item(
            Key={"pk": f"RATE#{token}", "sk": minute_key},
            UpdateExpression="ADD #c :one SET #ttl = if_not_exists(#ttl, :ttl)",
            ExpressionAttributeNames={"#c": "count", "#ttl": "ttl"},
            ExpressionAttributeValues={":one": 1, ":ttl": int(time.time()) + 300},
            ReturnValues="UPDATED_NEW",
        )
        return int(r["Attributes"]["count"])

    def put_request(self, token: str, item: dict) -> None:
        _ddb.put_item(Item={"pk": f"REQ#{token}", "sk": item["requested_at"], **item,
                            "ttl": int(time.time()) + 30 * 86400})

    def list_requests(self, token: str) -> list:
        r = _ddb.query(KeyConditionExpression="pk = :pk", ExpressionAttributeValues={":pk": f"REQ#{token}"})
        out = []
        for it in r.get("Items", []):
            d = {k: v for k, v in it.items() if k not in ("pk", "sk", "ttl")}
            if "days" in d:
                d["days"] = float(d["days"]) if float(d["days"]) % 1 else int(d["days"])
            out.append(d)
        return out


_store = DynamoStore()


def _json(status: int, body: dict) -> dict:
    return {"statusCode": status, "headers": {"content-type": "application/json; charset=utf-8",
                                               "cache-control": "no-store"},
            "body": json.dumps(body, ensure_ascii=False)}


def handler(event, context):
    headers = {k.lower(): v for k, v in (event.get("headers") or {}).items()}
    if ORIGIN_SECRET and headers.get("x-lab-origin") != ORIGIN_SECRET:
        return _json(403, {"error": "forbidden", "message": "CloudFront 주소로 호출하세요."})
    ctx = event.get("requestContext", {}).get("http", {})
    method = ctx.get("method", "GET")
    path = event.get("rawPath", "/")
    body = event.get("body")
    if body and event.get("isBase64Encoded"):
        body = base64.b64decode(body).decode("utf-8", "replace")
    status, payload = lab_api.handle(method, path, headers, body, _store)
    tok = lab_api.extract_token(headers)
    print(json.dumps({"token": lab_api.mask(tok or ""), "method": method, "path": path, "status": status}))
    return _json(status, payload)
