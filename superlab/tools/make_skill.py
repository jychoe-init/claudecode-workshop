#!/usr/bin/env python3
"""코치가 정해진 내용으로 새 스킬 폴더를 만든다(만들기 단계). 참가자 손은 거치지 않는다.

Claude Code 는 `.claude/` 아래 파일을 Edit/Write 도구로 쓸 때 설정의 allow 와 무관하게 늘 승인 창을 띄운다(실측: 어떤 allow 패턴도 통하지 않음).
그래서 코치는 이 스크립트로 쓴다. 스크립트는 (1) `.claude/skills/<새이름>/` 만 만들고 (2) 예시 스킬 원본은 절대 고치지 않으며
(3) 무엇을 썼는지 스펙 JSON 이 기록(docs/worksheets/)에 남는다.

  python3 tools/make_skill.py build <spec.json>
      spec: {"from": ".claude/skills/meeting-notes",          # 복사할 출발점(templates/ 는 복사하지 않음). 새로 만들기면 docs/templates/skill-blank
             "to":   ".claude/skills/meeting-notes-cs",       # 새 폴더. .claude/skills/ 바로 아래, 소문자·숫자·하이픈
             "template_from": "templates/exec.md",             # 선택: 출발점의 미리 만든 양식을 template.md 로
             "files": {"SKILL.md": "...전체 내용...", "template.md": "...전체 내용..."}}   # 선택: 쓸 파일 전체 내용(복사 뒤 덮어씀)
  python3 tools/make_skill.py set-frontmatter <skill_dir> <key> <value>     # 코치가 만든 스킬의 머리 부분 한 줄 바꾸기(없으면 추가)
  python3 tools/make_skill.py replace-line <skill_dir> "<old>" "<new>"        # 코치가 만든 스킬 본문의 한 줄 교체(new 가 "" 이면 삭제) -- lab3 점검 결과 반영
  python3 tools/make_skill.py list                                           # 코치가 만든 스킬 목록

안전장치: `to` 가 이미 있고 이 스크립트가 만든 폴더(.made-by-coach 표식)가 아니면 거부. 예시 스킬 이름(PROTECTED)은 to 로 쓸 수 없다.
출력은 사람이 읽는 줄 + 마지막 줄 JSON(ok, 만든 파일). 실패는 exit 1.
"""
import json
import re
import shutil
import sys
from pathlib import Path

PROTECTED = {"meeting-notes", "weekly-report", "standup", "weekly-report-dev", "review-checklist", "workshop-coach"}
MARK = ".made-by-coach"
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,40}$")


def root_of(p):
    p = Path(p).resolve()
    while p != p.parent and not (p / ".claude").is_dir():
        p = p.parent
    return p


def fail(msg):
    print(f"FAIL {msg}")
    print(json.dumps({"ok": False, "error": msg}, ensure_ascii=False))
    return 1


def build(spec_path):
    root = root_of(Path.cwd())
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    src = (root / spec["from"]).resolve()
    dst = (root / spec["to"]).resolve()
    skills = (root / ".claude/skills").resolve()
    if dst.parent != skills:
        return fail(f"to 는 .claude/skills/ 바로 아래여야 함: {spec['to']}")
    if not NAME_RE.match(dst.name) or dst.name in PROTECTED:
        return fail(f"스킬 이름이 규칙에 맞지 않거나 예시 스킬 이름임: {dst.name}")
    if not (src / "SKILL.md").exists():
        return fail(f"출발점에 SKILL.md 가 없음: {spec['from']}")
    if dst.exists() and not (dst / MARK).exists():
        return fail(f"이미 있는 폴더이고 코치가 만든 것이 아님: {spec['to']}")
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("templates", "__pycache__", ".DS_Store"))
    written = []
    tf = spec.get("template_from")
    if tf:
        tsrc = src / tf
        if not tsrc.exists():
            return fail(f"미리 만든 양식이 없음: {spec['from']}/{tf}")
        (dst / "template.md").write_text(tsrc.read_text(encoding="utf-8"), encoding="utf-8")
        written.append("template.md (from " + tf + ")")
    for name, content in (spec.get("files") or {}).items():
        if "/" in name or name.startswith("."):
            return fail(f"files 키는 스킬 폴더 안의 파일 이름만: {name}")
        (dst / name).write_text(content if content.endswith("\n") else content + "\n", encoding="utf-8")
        written.append(name)
    (dst / MARK).write_text(json.dumps({"from": spec["from"], "spec": str(Path(spec_path))}, ensure_ascii=False) + "\n")
    print(f"OK   만든 폴더 {dst.relative_to(root)} (출발점 {spec['from']})")
    for w in written:
        print(f"OK   썼음 {w}")
    print(json.dumps({"ok": True, "dir": str(dst.relative_to(root)), "written": written}, ensure_ascii=False))
    return 0


def set_frontmatter(skill_dir, key, value):
    root = root_of(Path.cwd())
    d = (root / skill_dir).resolve()
    if not (d / MARK).exists():
        return fail(f"코치가 만든 스킬이 아님(표식 없음): {skill_dir}")
    if not re.match(r"^[a-z-]+$", key):
        return fail(f"키 이름이 이상함: {key}")
    p = d / "SKILL.md"
    text = p.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return fail("SKILL.md 머리 부분(---)이 없음")
    lines = m.group(1).splitlines()
    done = False
    for i, ln in enumerate(lines):
        if ln.split(":", 1)[0].strip() == key:
            lines[i] = f"{key}: {value}"; done = True
    if not done:
        lines.append(f"{key}: {value}")
    p.write_text("---\n" + "\n".join(lines) + "\n---\n" + text[m.end():], encoding="utf-8")
    print(f"OK   {skill_dir}/SKILL.md 머리 부분 {key}: {value}")
    print(json.dumps({"ok": True, "file": str(p.relative_to(root)), "key": key, "value": value}, ensure_ascii=False))
    return 0


def replace_line(skill_dir, old, new):
    """코치가 만든 스킬의 SKILL.md 본문에서 `old` 를 담은 줄 하나를 `new` 로 바꾼다. new 가 빈 문자열이면 그 줄을 지운다."""
    root = root_of(Path.cwd())
    d = (root / skill_dir).resolve()
    if not (d / MARK).exists():
        return fail(f"코치가 만든 스킬이 아님(표식 없음): {skill_dir}")
    if not old.strip():
        return fail("바꿀 줄(old)이 비어 있음")
    p = d / "SKILL.md"
    lines = p.read_text(encoding="utf-8").split("\n")
    hits = [i for i, ln in enumerate(lines) if old in ln]
    if len(hits) != 1:
        return fail(f"'{old}' 를 담은 줄이 {len(hits)}개 -- 정확히 한 줄이어야 함")
    i = hits[0]
    before = lines[i]
    if new.strip():
        lines[i] = new
    else:
        del lines[i]
    p.write_text("\n".join(lines), encoding="utf-8")
    print(f"OK   {skill_dir}/SKILL.md {i+1}행: {before!r} -> {new!r}")
    print(json.dumps({"ok": True, "file": str(p.relative_to(root)), "line": i + 1, "before": before, "after": new}, ensure_ascii=False))
    return 0


def list_made():
    root = root_of(Path.cwd())
    made = sorted(str(p.parent.relative_to(root)) for p in (root / ".claude/skills").glob("*/" + MARK))
    for m in made:
        print(m)
    print(json.dumps({"ok": True, "made": made}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__); sys.exit(2)
    if a[0] == "build" and len(a) == 2:
        sys.exit(build(a[1]))
    if a[0] == "set-frontmatter" and len(a) == 4:
        sys.exit(set_frontmatter(a[1], a[2], a[3]))
    if a[0] == "replace-line" and len(a) == 4:
        sys.exit(replace_line(a[1], a[2], a[3]))
    if a[0] == "list":
        sys.exit(list_made())
    print(__doc__); sys.exit(2)
