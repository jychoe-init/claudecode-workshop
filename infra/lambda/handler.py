"""Lambda Function URL 핸들러. CloudFront 뒤에서만 받는다(비밀 헤더 검사).

Slack 봇 토큰은 SSM SecureString(SLACK_TOKEN_PARAM)에서 콜드스타트 때 한 번 읽는다. 없으면 Slack 기능만 503.
"""
import base64
import json
import os
import time
import urllib.error
import urllib.request

import boto3

import lab_api

TABLE = os.environ["TABLE_NAME"]
ORIGIN_SECRET = os.environ.get("ORIGIN_SECRET", "")
SLACK_TOKEN_PARAM = os.environ.get("SLACK_TOKEN_PARAM", "")
_ddb = boto3.resource("dynamodb").Table(TABLE)


def _load_slack_token():
    if not SLACK_TOKEN_PARAM:
        return ""
    try:
        return boto3.client("ssm").get_parameter(Name=SLACK_TOKEN_PARAM, WithDecryption=True)["Parameter"]["Value"]
    except Exception as e:  # noqa: BLE001 - 파라미터 미설정은 정상 상태(Slack 미연동)
        print(json.dumps({"slack_token": "unavailable", "reason": type(e).__name__}))
        return ""


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

    def get_link(self, token: str):
        item = _ddb.get_item(Key={"pk": f"TOKEN#{token}", "sk": "SLACK"}).get("Item")
        return {k: v for k, v in item.items() if k not in ("pk", "sk")} if item else None

    def put_link(self, token: str, link: dict) -> None:
        _ddb.put_item(Item={"pk": f"TOKEN#{token}", "sk": "SLACK", **link})


class SlackNotifier:
    def __init__(self, bot_token: str):
        self.tok = bot_token

    def _call(self, method: str, payload: dict) -> dict:
        req = urllib.request.Request(f"https://slack.com/api/{method}", data=json.dumps(payload).encode(),
                                     headers={"Authorization": f"Bearer {self.tok}",
                                              "Content-Type": "application/json; charset=utf-8"})
        try:
            with urllib.request.urlopen(req, timeout=6) as r:
                return json.loads(r.read())
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            return {"ok": False, "error": f"transport:{type(e).__name__}"}

    def lookup_user(self, email: str):
        r = self._call("users.lookupByEmail", {"email": email})
        return r.get("user", {}).get("id") if r.get("ok") else None

    def send_dm(self, slack_user_id: str, text: str) -> dict:
        opened = self._call("conversations.open", {"users": slack_user_id})
        if not opened.get("ok"):
            return {"ok": False, "error": opened.get("error", "open_failed")}
        ch = opened["channel"]["id"]
        posted = self._call("chat.postMessage", {"channel": ch, "text": text, "mrkdwn": True})
        return {"ok": bool(posted.get("ok")), "channel": ch, "error": posted.get("error", "")}


_store = DynamoStore()
_slack_token = _load_slack_token()
_notifier = SlackNotifier(_slack_token) if _slack_token else None


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
    status, payload = lab_api.handle(method, path, headers, body, _store, notifier=_notifier)
    tok = lab_api.extract_token(headers)
    print(json.dumps({"token": lab_api.mask(tok or ""), "method": method, "path": path, "status": status}))
    return _json(status, payload)
