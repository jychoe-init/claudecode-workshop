#!/usr/bin/env python3
"""API.md의 표·예시를 외부 의존성 없이 참가자용 단일 HTML로 만든다."""
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def inline(text):
    code = []
    def keep(match):
        code.append('<code>' + html.escape(match.group(1).replace('\\|', '|')) + '</code>')
        return f'@@CODE{len(code)-1}@@'
    text = re.sub(r'`([^`]+)`', keep, text)
    text = html.escape(text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    for i, fragment in enumerate(code):
        text = text.replace(f'@@CODE{i}@@', fragment)
    return text


def render(source):
    lines = source.splitlines()
    out, toc = [], []
    n = 0
    while n < len(lines):
        line = lines[n]
        if not line.strip():
            n += 1
            continue
        if line.startswith('```'):
            language = line[3:]
            block = []
            n += 1
            while n < len(lines) and not lines[n].startswith('```'):
                block.append(lines[n])
                n += 1
            out.append('<pre><code data-language="' + html.escape(language) + '">' + html.escape('\n'.join(block)) + '</code></pre>')
        elif line.startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            title = line[level:].strip()
            anchor = f'section-{len(toc)+1}' if level == 2 else ''
            if level == 2:
                toc.append((anchor, title))
            out.append(f'<h{level} id="{anchor}">{inline(title)}</h{level}>' if anchor else f'<h{level}>{inline(title)}</h{level}>')
        elif line.startswith('|'):
            rows = []
            while n < len(lines) and lines[n].startswith('|'):
                if not re.match(r'^\|[\s:|\-]+\|$', lines[n]):
                    rows.append(re.split(r'(?<!\\)\|', lines[n].strip('|')))
                n += 1
            out.append('<div class="table-scroll" tabindex="0"><table>')
            for i, row in enumerate(rows):
                tag = 'th' if i == 0 else 'td'
                out.append('<tr>' + ''.join(f'<{tag}>{inline(cell.strip())}</{tag}>' for cell in row) + '</tr>')
            out.append('</table></div>')
            continue
        elif line.startswith('- '):
            out.append('<ul>')
            while n < len(lines) and lines[n].startswith('- '):
                out.append('<li>' + inline(lines[n][2:]) + '</li>')
                n += 1
            out.append('</ul>')
            continue
        else:
            para = [line]
            while n+1 < len(lines) and lines[n+1].strip() and not lines[n+1].startswith(('#', '|', '- ', '```')):
                n += 1
                para.append(lines[n])
            out.append('<p>' + inline(' '.join(para)) + '</p>')
        n += 1
    nav = ''.join(f'<a href="#{anchor}">{html.escape(title)}</a>' for anchor, title in toc)
    return nav, '\n'.join(out)


def main():
    nav, body = render((ROOT/'API.md').read_text())
    page = '''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>superlab HR Mock API · 2026-10-06</title>
<style>
:root{color-scheme:light dark;--bg:#fafbfc;--fg:#19212b;--muted:#556577;--line:#dbe1e8;--accent:#185da3;--code:#eef2f6}
@media(prefers-color-scheme:dark){:root{--bg:#151a21;--fg:#e1e7ee;--muted:#acb8c6;--line:#35404e;--accent:#8cbbf0;--code:#202a36}}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.75 -apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Noto Sans KR",sans-serif}
header,main,footer{max-width:1060px;margin:auto;padding:24px}header{border-bottom:1px solid var(--line)}header p{margin:0;color:var(--muted);font-size:14px}.brand{color:var(--accent);font-weight:800;letter-spacing:.04em}
nav{display:flex;flex-wrap:wrap;gap:8px 18px;margin-top:18px}nav a{font-size:13px}a{color:var(--accent)}h1{font-size:30px;line-height:1.35;margin:24px 0}h2{font-size:23px;border-top:1px solid var(--line);padding-top:28px;margin-top:48px}h3{font-size:18px;margin-top:32px}p,ul{margin:18px 0}li{margin:8px 0}code{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:13px;overflow-wrap:anywhere}p code,li code,td code{background:var(--code);padding:2px 4px;border-radius:3px}
pre{background:var(--code);padding:18px;border:1px solid var(--line);border-radius:6px;overflow:auto;line-height:1.6;max-height:650px}pre code{overflow-wrap:normal}.table-scroll{overflow:auto;max-width:100%;border:1px solid var(--line);border-radius:6px}table{border-collapse:collapse;width:100%;min-width:630px;font-size:14px}th,td{text-align:left;padding:11px 14px;border-bottom:1px solid var(--line);vertical-align:top}th{background:var(--code)}tr:last-child td{border-bottom:0}footer{color:var(--muted);font-size:13px;border-top:1px solid var(--line)}:focus-visible{outline:3px solid var(--accent);outline-offset:3px}
@media(max-width:600px){header,main,footer{padding:18px}h1{font-size:25px}h2{font-size:21px}body{font-size:15px}pre{padding:12px}}
</style></head><body>
<header><div class="brand">superlab / API</div><p>120명 조직 · 휴가 이력 · MCP 실습 · 버전 2026-10-06</p><nav aria-label="문서 목차">'''+nav+'''</nav></header>
<main>'''+body+'''</main><footer>기본 주소는 현재 페이지의 호스트입니다. 인증 토큰은 배포된 실습 안내에서 확인하세요. · 원본: infra/API.md</footer>
</body></html>'''
    (ROOT/'site/index.html').write_text(page)
    print('Generated infra/site/index.html from infra/API.md')


if __name__ == '__main__':
    main()
