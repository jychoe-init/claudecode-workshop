#!/usr/bin/env python3
"""스킬 폴더 하나를 정적으로 검사한다. 코치가 파일을 만든 직후(만들기 단계)와 validate_kit.py 가 같이 쓴다.

  python3 tools/check_skill.py .claude/skills/<이름> [--sections N]

검사 항목
  1. SKILL.md 가 있고 머리 부분(--- 사이)이 `키: 값` 줄로 읽힌다. 허용 키만 쓴다. description 이 있다.
  2. 본문이 template.md 를 가리키면 template.md 가 있고, `##` 섹션 수가 --sections 와 같다(주면).
  3. 자동 삽입 줄(`!`...``)은 명령 하나다: `$(`, 중첩 백틱, `;`, `&&`, `||`, `|`, `>` 를 쓰지 않는다.
     (이런 줄은 실행 전 권한 검사에서 "Quoted text in this command can't be checked" 로 막혀 스킬이 빈 결과를 낸다)
  4. 자동 삽입 줄이 tools/ 의 스크립트를 부르면 그 파일이 있고, 머리 부분 allowed-tools 또는 .claude/settings.json allow 에
     그 명령의 Bash 규칙이 있다(없으면 첫 실행이 "permission check failed" 로 멈춘다).
  5. effort 값이 있으면 low/medium/high/max 중 하나다.

종료 코드 0 = 전부 통과. 출력은 `OK|FAIL 항목 -- 비고` 줄 목록(코치가 그대로 보여 준다).
"""
import json
import re
import sys
from pathlib import Path

ALLOWED_KEYS = {"name", "description", "argument-hint", "disable-model-invocation", "user-invocable", "allowed-tools",
                "model", "context", "agent", "effort", "hooks", "paths"}
BAD_IN_INJECTION = ["$(", ";", "&&", "||", "|", ">"]
INJ_RE = re.compile(r"^!`([^`]*)`\s*$")


def parse_frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None, "머리 부분(---)이 없음"
    fm = {}
    for i, line in enumerate(m.group(1).splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line or line.startswith((" ", "\t")):
            return None, f"{i}행이 `키: 값` 모양이 아님: {line[:40]!r}"
        k, v = line.split(":", 1)
        fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm, ""


def main(argv):
    if not argv:
        print(__doc__); return 2
    skill = Path(argv[0])
    sections = int(argv[argv.index("--sections") + 1]) if "--sections" in argv else None
    root = skill.resolve()
    while root != root.parent and not (root / ".claude").is_dir():
        root = root.parent
    results = []

    def rec(ok, item, note=""):
        results.append((ok, item, note))

    sk = skill / "SKILL.md"
    if not sk.exists():
        rec(False, "SKILL.md 존재", f"{sk} 없음")
        return report(results)
    text = sk.read_text(encoding="utf-8")
    fm, err = parse_frontmatter(text)
    if fm is None:
        rec(False, "머리 부분 읽기", err)
        return report(results)
    rec(True, "머리 부분 읽기", f"{len(fm)}개 설정 줄")
    extra = set(fm) - ALLOWED_KEYS
    rec(not extra, "허용된 설정 줄만", f"모르는 키: {sorted(extra)}" if extra else "")
    rec(bool(fm.get("description")), "description 있음", fm.get("description", "")[:60])
    if "effort" in fm:
        rec(fm["effort"] in {"low", "medium", "high", "max"}, "effort 값", fm["effort"])

    body = text[text.find("\n---\n") + 5:]
    if "${CLAUDE_SKILL_DIR}/template.md" in body:
        tpl = skill / "template.md"
        if not tpl.exists():
            rec(False, "template.md 존재", "본문이 가리키는데 파일이 없음")
        else:
            form = tpl.read_text(encoding="utf-8").split("\n---\n", 1)[0]  # '---' 뒤는 예시 부분
            n = sum(1 for ln in form.splitlines() if ln.startswith("## "))
            if sections is None:
                rec(True, "template.md 섹션 수", f"## {n}개")
            else:
                rec(n == sections, "template.md 섹션 수 = 정한 수", f"## {n}개, 정한 수 {sections}")

    allow = set()
    at = fm.get("allowed-tools", "")
    allow.update(x.strip() for x in at.split(",") if x.strip())
    settings = root / ".claude/settings.json"
    if settings.exists():
        try:
            allow.update(json.loads(settings.read_text()).get("permissions", {}).get("allow", []))
        except Exception as e:  # noqa
            rec(False, "settings.json 읽기", str(e)[:60])

    inj = [INJ_RE.match(ln) for ln in body.splitlines()]
    inj = [m.group(1) for m in inj if m]
    for cmd in inj:
        bad = [b for b in BAD_IN_INJECTION if b in cmd] + (["백틱 중첩"] if "`" in cmd else [])
        rec(not bad, f"자동 삽입 줄은 명령 하나: `{cmd[:50]}`", f"쓰면 안 되는 것: {bad}" if bad else "")
        m = re.match(r"^(python3|bash)\s+(tools/\S+)", cmd)
        if m:
            script = root / m.group(2)
            rec(script.exists(), f"스크립트 존재 {m.group(2)}", "" if script.exists() else "파일 없음")
            prefix = f"Bash({m.group(1)} {m.group(2)}"
            ok = any(a.startswith(prefix) for a in allow)
            rec(ok, f"사전 승인 규칙 {prefix} *)", "allowed-tools 또는 settings allow 에 있음" if ok else "없음 → 첫 실행이 멈춤")
    if not inj:
        rec(True, "자동 삽입 줄", "없음")
    return report(results)


def report(results):
    for ok, item, note in results:
        print(f"{'OK  ' if ok else 'FAIL'} {item}" + (f" -- {note}" if note else ""))
    fails = sum(1 for ok, _, _ in results if not ok)
    print(f"{'통과' if not fails else '실패'} {len(results) - fails}/{len(results)}")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
