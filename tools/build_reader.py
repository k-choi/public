#!/usr/bin/env python3
"""Generate a self-contained reader index.html for 마지막 소유자,
mirroring the design system of the 오차 범위 reader."""
import html, re, sys, pathlib

SRC = pathlib.Path(sys.argv[1])          # manuscript dir
OUT = pathlib.Path(sys.argv[2])          # output index.html

TITLE = "마지막 소유자"
SUBTITLE = "사변적 가족소설 · 심리 서스펜스"
TAGLINE = "누가 마지막으로 그의 뜻을 소유하는가"
COLOPHON_LINE = "어느 뜻도 다른 뜻을 가리지 않았다."

def esc(s: str) -> str:
    return html.escape(s, quote=False)

def inline(s: str) -> str:
    """Escape, then turn `backtick spans` into subtle mono spans."""
    out, i, n = [], 0, len(s)
    while i < n:
        if s[i] == "`":
            j = s.find("`", i + 1)
            if j == -1:
                out.append(esc(s[i:])); break
            out.append('<span class="mono">' + esc(s[i+1:j]) + '</span>')
            i = j + 1
        else:
            k = s.find("`", i)
            if k == -1:
                out.append(esc(s[i:])); break
            out.append(esc(s[i:k])); i = k
    return "".join(out)

def parse_chapter(path: pathlib.Path):
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    # title from first H1
    title = ""
    body_start = 0
    for idx, ln in enumerate(lines):
        if ln.startswith("# "):
            raw = ln[2:].strip()
            m = re.match(r"^\d+\.\s*(.+)$", raw)
            title = m.group(1).strip() if m else raw
            body_start = idx + 1
            break
    # split remaining into blocks by blank lines
    blocks, cur = [], []
    for ln in lines[body_start:]:
        if ln.strip() == "":
            if cur:
                blocks.append("\n".join(cur)); cur = []
        else:
            cur.append(ln.rstrip())
    if cur:
        blocks.append("\n".join(cur))
    return title, blocks

def render_block(block: str) -> str:
    stripped = block.strip()
    if re.fullmatch(r"\*\s*\*\s*\*", stripped):
        return '<p class="sep" aria-hidden="true">＊</p>'
    # whole-block screen/document text: single backtick span spanning the block
    if stripped.startswith("`") and stripped.endswith("`") and stripped.count("`") == 2:
        return '<p class="screen">' + esc(stripped[1:-1].strip()) + "</p>"
    joined = block.replace("\n", " ")
    return "<p>" + inline(joined) + "</p>"

def main():
    files = sorted(SRC.glob("chapter_*.md"))
    chapters = []
    for f in files:
        title, blocks = parse_chapter(f)
        num = int(re.search(r"chapter_(\d+)", f.name).group(1))
        chapters.append((num, title, blocks))
    chapters.sort(key=lambda c: c[0])
    total = len(chapters)

    # TOC
    toc = ['  <nav class="toc">', "    <h2>Table of Contents</h2>"]
    for num, title, _ in chapters:
        toc.append(
            f'<a class="toc-row" href="#ch{num}"><span class="tr-idx">{num:02d}</span>'
            f'<span class="tr-title">{esc(title)}</span><span class="tr-leader"></span></a>'
        )
    toc.append("  </nav>")
    toc_html = "\n".join(toc)

    # chapters
    secs = []
    for num, title, blocks in chapters:
        s = [f'<section class="chapter" id="ch{num}">',
             f'  <header class="ch-open"><span class="ch-idx">{num:02d}'
             f'<span class="ch-tot"> / {total}</span></span>'
             f'<h2 class="ch-title">{esc(title)}</h2></header>']
        for b in blocks:
            s.append(render_block(b))
        s.append('  <p class="ch-foot"><a href="#top">↑ INDEX</a></p>')
        s.append("</section>")
        secs.append("\n".join(s))
    chapters_html = "\n".join(secs)

    page = TEMPLATE.format(
        title=esc(TITLE), subtitle=esc(SUBTITLE), tagline=esc(TAGLINE),
        total=total, toc=toc_html, chapters=chapters_html,
        colophon_line=esc(COLOPHON_LINE),
    )
    OUT.write_text(page, encoding="utf-8")
    print(f"wrote {OUT} ({len(page):,} bytes, {total} chapters)")

TEMPLATE = r"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{subtitle} · 전 {total}장">
<style>
:root{{
  --bg:#f4f5f4; --panel:#fbfbfa; --fg:#1a1d21; --muted:#666c73;
  --rule:#d7dbdd; --grid:rgba(26,29,33,.05); --accent:#2b6c7f; --accent-2:#1f5361;
  --serif:'Nanum Myeongjo','Noto Serif KR',NanumMyeongjo,AppleMyungjo,'Batang',serif;
  --mono:'SFMono-Regular',ui-monospace,'SF Mono','Cascadia Code','Roboto Mono',Menlo,monospace;
}}
@media (prefers-color-scheme:dark){{:root{{
  --bg:#0e1113; --panel:#14181b; --fg:#e4e2db; --muted:#868d94;
  --rule:#232a2e; --grid:rgba(228,226,219,.05); --accent:#5bb2c9; --accent-2:#7fc9dd;
}}}}
:root[data-theme="dark"]{{--bg:#0e1113;--panel:#14181b;--fg:#e4e2db;--muted:#868d94;--rule:#232a2e;--grid:rgba(228,226,219,.05);--accent:#5bb2c9;--accent-2:#7fc9dd;}}
:root[data-theme="light"]{{--bg:#f4f5f4;--panel:#fbfbfa;--fg:#1a1d21;--muted:#666c73;--rule:#d7dbdd;--grid:rgba(26,29,33,.05);--accent:#2b6c7f;--accent-2:#1f5361;}}
*{{box-sizing:border-box}}
html{{scroll-behavior:smooth}}
@media (prefers-reduced-motion:reduce){{html{{scroll-behavior:auto}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font-family:var(--serif);
  line-height:1.98;letter-spacing:.005em;word-break:keep-all;overflow-wrap:break-word;-webkit-text-size-adjust:100%;}}
a{{color:inherit}}
.bar{{position:sticky;top:0;z-index:20;display:flex;align-items:center;justify-content:space-between;
  padding:.55rem 1.1rem;background:color-mix(in srgb,var(--bg) 90%,transparent);backdrop-filter:blur(10px);
  border-bottom:1px solid var(--rule);font-family:var(--mono);font-size:.72rem;letter-spacing:.14em;}}
.bar .b-l{{color:var(--muted)}}.bar .b-l b{{color:var(--fg);font-weight:600}}
.bar a.home{{color:var(--muted);text-decoration:none}}
.bar a.home:hover{{color:var(--fg)}}
.bar .b-r{{display:flex;gap:.5rem;align-items:center}}
.bar button{{font:inherit;letter-spacing:.14em;color:var(--muted);background:transparent;border:1px solid var(--rule);
  border-radius:2px;padding:.28rem .6rem;cursor:pointer}}
.bar button:hover{{color:var(--fg);border-color:var(--muted)}}
.bar button:focus-visible{{outline:2px solid var(--accent);outline-offset:2px}}
.wrap{{max-width:39rem;margin:0 auto;padding:0 1.3rem}}
.grid-bg{{position:absolute;inset:0;pointer-events:none;
  background-image:linear-gradient(var(--grid) 1px,transparent 1px),linear-gradient(90deg,var(--grid) 1px,transparent 1px);
  background-size:26px 26px;mask-image:radial-gradient(ellipse 80% 70% at 50% 45%,#000 40%,transparent 100%);}}
.cover{{position:relative;min-height:88vh;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;padding:6vh 1.3rem}}
.cover .grid-bg{{z-index:0}}
.cover>*{{position:relative;z-index:1}}
.eyebrow{{font-family:var(--mono);font-size:.7rem;letter-spacing:.4em;color:var(--muted);text-transform:uppercase}}
.cover h1{{font-size:clamp(2.7rem,12vw,4.9rem);margin:.9rem 0 0;letter-spacing:.16em;font-weight:800;text-wrap:balance}}
.curvewrap{{width:min(340px,78vw);margin:2.2rem auto .4rem}}
.curvewrap svg{{display:block;width:100%;height:auto;overflow:visible}}
.edge{{fill:none;stroke:var(--fg);stroke-width:1.4;opacity:.5}}
.edge-open{{fill:none;stroke:var(--accent);stroke-width:1.6;stroke-dasharray:4 4;stroke-linecap:round}}
.node{{fill:var(--bg);stroke:var(--fg);stroke-width:1.5;opacity:.7}}
.core{{fill:var(--accent);stroke:none}}
.nopen{{fill:var(--bg);stroke:var(--accent);stroke-width:1.6}}
.nlab{{font-family:var(--mono);font-size:9px;letter-spacing:.14em;fill:var(--accent-2)}}
.nlab-open{{font-family:var(--mono);font-size:8px;letter-spacing:.1em;fill:var(--muted)}}
.cover .tagline{{font-family:var(--mono);font-size:.74rem;letter-spacing:.16em;color:var(--muted);margin-top:1.4rem;text-wrap:balance}}
.cover .meta{{font-family:var(--mono);font-size:.7rem;letter-spacing:.22em;color:var(--muted);margin-top:2.6rem;text-transform:uppercase}}
.scroll-cue{{font-family:var(--mono);font-size:.66rem;letter-spacing:.3em;color:var(--muted);margin-top:3.4rem;opacity:.8}}
.toc{{padding:5rem 0 3rem;border-top:1px solid var(--rule)}}
.toc>h2{{font-family:var(--mono);text-align:center;font-size:.74rem;letter-spacing:.42em;color:var(--muted);font-weight:500;text-transform:uppercase;margin:0 0 3rem}}
.toc-row{{display:flex;align-items:baseline;gap:.85rem;text-decoration:none;padding:.5rem .2rem;border-radius:3px}}
.toc-row:hover{{background:var(--panel)}}
.toc-row:focus-visible{{outline:2px solid var(--accent);outline-offset:-2px}}
.tr-idx{{font-family:var(--mono);font-size:.76rem;color:var(--muted);font-variant-numeric:tabular-nums;min-width:1.9rem}}
.tr-title{{flex:0 1 auto;color:var(--fg)}}
.tr-leader{{flex:1;border-bottom:1px dotted var(--rule);transform:translateY(-.28em)}}
.toc-row:hover .tr-idx{{color:var(--accent)}}
.chapter{{padding:9vh 0 5vh;border-top:1px solid var(--rule)}}
.ch-open{{display:flex;align-items:baseline;gap:1rem;margin:0 0 2.6rem}}
.ch-idx{{font-family:var(--mono);font-size:.82rem;letter-spacing:.1em;color:var(--accent);font-variant-numeric:tabular-nums;font-weight:600;white-space:nowrap}}
.ch-tot{{color:var(--muted);font-weight:400}}
.ch-title{{margin:0;font-size:1.6rem;font-weight:700;letter-spacing:.05em;text-wrap:balance;line-height:1.4}}
.chapter p{{margin:0 0 1.4rem;text-align:justify;font-size:1.02rem}}
.chapter p.sep{{text-align:center;color:var(--muted);letter-spacing:.6em;margin:2.6rem 0;font-size:.9rem}}
.chapter p.screen{{font-family:var(--mono);font-size:.84rem;line-height:1.7;letter-spacing:.02em;text-align:left;
  color:var(--accent-2);background:var(--panel);border:1px solid var(--rule);border-left:2px solid var(--accent);
  border-radius:2px;padding:.7rem .9rem;margin:1.7rem 0;word-break:break-all}}
.chapter .mono{{font-family:var(--mono);font-size:.9em;letter-spacing:.01em;color:var(--accent-2)}}
.ch-foot{{margin-top:3.2rem;text-align:center}}
.ch-foot a{{font-family:var(--mono);color:var(--muted);text-decoration:none;font-size:.7rem;letter-spacing:.28em}}
.ch-foot a:hover{{color:var(--accent)}}
.colophon{{position:relative;text-align:center;padding:8vh 1.3rem 12vh;border-top:1px solid var(--rule);overflow:hidden}}
.colophon .grid-bg{{z-index:0}}
.colophon .cx{{position:relative;z-index:1}}
.colophon .ct{{font-family:var(--mono);font-size:.72rem;letter-spacing:.24em;color:var(--muted);text-transform:uppercase}}
.colophon .cq{{margin-top:1.6rem;font-size:1.05rem;letter-spacing:.06em;color:var(--fg);line-height:1.9}}
::selection{{background:var(--accent);color:var(--bg)}}
</style>
</head>
<body id="top">
<div class="bar"><span class="b-l"><a class="home" href="../">◄ 서가</a> · <b>{title}</b></span><div class="b-r"><button id="themeBtn" aria-label="라이트/다크 전환">◐ THEME</button></div></div>

<section class="cover">
  <div class="grid-bg"></div>
  <span class="eyebrow">A Novel · 전 {total}장</span>
  <h1>{title}</h1>
  <div class="curvewrap"><svg viewBox="0 0 300 170" role="img" aria-label="한 노드로 수렴하는 통제 이전 도식, 미완료 절차 1건">
  <line class="edge" x1="150" y1="88" x2="46" y2="38"/>
  <line class="edge" x1="150" y1="88" x2="150" y2="26"/>
  <line class="edge" x1="150" y1="88" x2="252" y2="46"/>
  <line class="edge" x1="150" y1="88" x2="64" y2="132"/>
  <line class="edge" x1="150" y1="88" x2="250" y2="130"/>
  <path class="edge-open" id="openedge" d="M150 150 L150 108"/>
  <circle class="node" cx="46" cy="38" r="4"/>
  <circle class="node" cx="150" cy="26" r="4"/>
  <circle class="node" cx="252" cy="46" r="4"/>
  <circle class="node" cx="64" cy="132" r="4"/>
  <circle class="node" cx="250" cy="130" r="4"/>
  <circle class="nopen" cx="150" cy="150" r="4"/>
  <circle class="core" cx="150" cy="88" r="6.5"/>
  <text class="nlab" x="150" y="76" text-anchor="middle">SI-1</text>
  <text class="nlab-open" x="150" y="166" text-anchor="middle">미완료 1건</text>
</svg></div>
  <div class="tagline">{tagline}</div>
  <div class="meta">{subtitle}</div>
  <div class="scroll-cue">↓ 차례</div>
</section>

<div class="wrap">
{toc}

{chapters}
<section class="colophon">
  <div class="grid-bg"></div>
  <div class="cx">
    <div class="ct">{title} · 전 {total}장</div>
    <div class="cq">{colophon_line}</div>
  </div>
</section>
</div>
<script>
(function(){{
  var b=document.getElementById('themeBtn'),root=document.documentElement;
  b&&b.addEventListener('click',function(){{
    var c=root.getAttribute('data-theme'),
        d=c?c==='dark':matchMedia('(prefers-color-scheme: dark)').matches;
    root.setAttribute('data-theme',d?'light':'dark');
  }});
  var reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
  var p=document.getElementById('openedge');
  if(p&&!reduce){{try{{var L=p.getTotalLength();p.style.transition='none';
    p.style.strokeDashoffset=L;p.style.strokeDasharray=L;p.getBoundingClientRect();
    p.style.transition='stroke-dashoffset 1.4s ease-out';
    requestAnimationFrame(function(){{p.style.strokeDasharray='4 4';p.style.strokeDashoffset='0';}});
  }}catch(e){{}}}}
}})();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
