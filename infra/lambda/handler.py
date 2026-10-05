"""HTTP API payload 2.0 Lambda 핸들러. CloudFront 뒤에서만 받는다(비밀 헤더 검사)."""
import base64
import json
import os
import time
from decimal import Decimal

import boto3

import lab_api

TABLE = os.environ["TABLE_NAME"]
ORIGIN_SECRET = os.environ.get("ORIGIN_SECRET", "")
_ddb = boto3.resource("dynamodb").Table(TABLE)


def to_dynamo(value):
    if isinstance(value, float):
        return Decimal(str(value))
    if isinstance(value, dict):
        return {k: to_dynamo(v) for k, v in value.items()}
    if isinstance(value, list):
        return [to_dynamo(v) for v in value]
    return value


def from_dynamo(value):
    if isinstance(value, Decimal):
        return int(value) if value == value.to_integral_value() else float(value)
    if isinstance(value, dict):
        return {k: from_dynamo(v) for k, v in value.items()}
    if isinstance(value, list):
        return [from_dynamo(v) for v in value]
    return value


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
        _ddb.put_item(Item=to_dynamo({"pk": f"REQ#{token}", "sk": item["requested_at"] + "#" + item["request_id"], **item,
                                    "ttl": int(time.time()) + 30 * 86400}),
                      ConditionExpression="attribute_not_exists(pk) AND attribute_not_exists(sk)")

    def list_requests(self, token: str, limit: int = 20) -> list:
        out, cursor = [], None
        limit = min(limit, 500)
        while len(out) < limit:
            kwargs = {"KeyConditionExpression": "pk = :pk", "ExpressionAttributeValues": {":pk": f"REQ#{token}"},
                      "ScanIndexForward": False, "Limit": limit - len(out), "ConsistentRead": True}
            if cursor:
                kwargs["ExclusiveStartKey"] = cursor
            response = _ddb.query(**kwargs)
            out.extend(from_dynamo({k: v for k, v in item.items() if k not in ("pk", "sk", "ttl")})
                       for item in response.get("Items", []))
            cursor = response.get("LastEvaluatedKey")
            if not cursor:
                break
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
    if event.get("rawQueryString"):
        path += "?" + event["rawQueryString"]
    body = event.get("body")
    if body and event.get("isBase64Encoded"):
        body = base64.b64decode(body).decode("utf-8", "replace")
    status, payload = lab_api.handle(method, path, headers, body, _store)
    tok = lab_api.extract_token(headers)
    print(json.dumps({"token": lab_api.mask(tok or ""), "method": method, "path": event.get("rawPath", "/"), "status": status}))
    return _json(status, payload)
