#!/usr/bin/env python3
"""참가자 토큰을 만들어 DynamoDB에 등록하고, 배부용 CSV를 저장소 밖에 쓴다.

사용:
  python3 infra/scripts/make_tokens.py --count 80 --expires 2026-11-30 \
      --table ccw-lab-api --out ~/Downloads/ccw-tokens.csv [--profile my-isen-profile] [--dry-run]

- 토큰: lab- + 소문자·숫자 8자 (secrets 모듈). 저장소 안에는 절대 쓰지 않는다.
- DynamoDB: pk=TOKEN#<token>, sk=META, seq, expires_at. --dry-run 이면 CSV만.
"""
import argparse
import csv
import secrets
import string
import subprocess
import json
from pathlib import Path

ALPHABET = string.ascii_lowercase + string.digits


def make_token() -> str:
    return "lab-" + "".join(secrets.choice(ALPHABET) for _ in range(8))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=80)
    ap.add_argument("--expires", required=True, help="YYYY-MM-DD")
    ap.add_argument("--table", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--profile")
    ap.add_argument("--region", default="us-east-1")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    out = Path(a.out).expanduser()
    if "claudecode-workshop" in str(out.resolve()) or "superlab" in str(out.resolve()):
        raise SystemExit("CSV는 저장소 밖에 저장하세요.")

    tokens = [make_token() for _ in range(a.count)]
    assert len(set(tokens)) == len(tokens)
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["seq", "token", "expires_at"])
        for i, t in enumerate(tokens, 1):
            w.writerow([f"{i:03d}", t, a.expires])
    print(f"CSV {out} ({len(tokens)}개)")
    if a.dry_run:
        return

    base = ["aws", "dynamodb", "batch-write-item", "--region", a.region]
    if a.profile:
        base += ["--profile", a.profile]
    for i in range(0, len(tokens), 25):
        chunk = tokens[i:i + 25]
        items = [{"PutRequest": {"Item": {"pk": {"S": f"TOKEN#{t}"}, "sk": {"S": "META"},
                                          "seq": {"N": str(i + j + 1)}, "expires_at": {"S": a.expires}}}}
                 for j, t in enumerate(chunk)]
        req = json.dumps({a.table: items})
        r = subprocess.run(base + ["--request-items", req], capture_output=True, text=True)
        if r.returncode:
            raise SystemExit(r.stderr)
        un = json.loads(r.stdout or "{}").get("UnprocessedItems", {})
        if un:
            raise SystemExit(f"미처리 항목 있음: {un}")
    print(f"DynamoDB {a.table} 에 {len(tokens)}개 등록")


if __name__ == "__main__":
    main()
