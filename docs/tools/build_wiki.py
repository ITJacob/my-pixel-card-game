# -*- coding: utf-8 -*-
"""GitHub Pages wiki 静态生成器。

输入：docs/ddd/** 设计正源 + docs/json/ 卡池数据 + site/ 下三份玩法页专属源
      （dashboard.md 概要 / figures.html 图解 / concept-map.json 概念地图指针）。
输出：_site/（纯静态 HTML，侧栏导航；PWA 可安装：manifest + service worker 离线缓存）。
用法：python docs/tools/build_wiki.py  （仓库根运行）
注意：site/ 是入库源、_site/ 是生成产物，两者不得混写；产物每次全量重建，禁止手改。
"""
import io
import json
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
DOCS = os.path.join(ROOT, 'docs')
JSON_DIR = os.path.join(DOCS, 'json')
OUT = os.path.join(ROOT, '_site')
SITE_SRC = os.path.join(ROOT, 'site')   # 玩法页专属源（入库），勿与产物 _site/ 混写

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from status_loader import load_docs  # noqa: E402
import concept_map  # noqa: E402

try:
    import markdown
    MD = markdown.Markdown(extensions=['tables', 'fenced_code', 'toc'])
except ImportError:  # 本地未装 markdown 库时的兜底（Actions 里 pip install）
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'markdown'])
    import markdown
    MD = markdown.Markdown(extensions=['tables', 'fenced_code', 'toc'])

SITE_TITLE = 'MyPixelCardGame · 设计 Wiki'
BASE = os.environ.get('WIKI_BASE', '')

DASH_PATH = 'rules/战场玩法.html'
# 概念不设独立详情页：6 个抽屉全部内联在 dashboard 一页，靠 name 属性原生互斥。


def md_html(text):
    MD.reset()
    return MD.convert(text)


def esc(s):
    return (s or '').replace('&', '&amp;').replace('<', '&lt;').replace(
        '>', '&gt;')


CSS = """
:root{--bg:#16181d;--panel:#1d2026;--line:#2c313a;--fg:#d7dae0;--mut:#8b919c;
--ac:#e0a94e;--ac2:#7fb4d8}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
font:15px/1.75 "Microsoft YaHei","PingFang SC",sans-serif;display:flex;min-height:100vh}
aside{width:240px;flex:0 0 240px;background:var(--panel);border-right:1px solid var(--line);
padding:18px 14px;position:sticky;top:0;height:100vh;overflow:auto}
aside .brand{color:var(--ac);font-weight:700;font-size:16px;text-decoration:none;display:block;margin-bottom:14px}
aside h4{color:var(--mut);font-size:12px;margin:16px 4px 6px;letter-spacing:.12em}
aside a{display:block;color:var(--fg);text-decoration:none;padding:3px 8px;border-radius:6px;font-size:13.5px}
aside a:hover{background:var(--line)}
main{flex:1;padding:28px 40px;max-width:980px}
main h1{color:var(--ac);border-bottom:1px solid var(--line);padding-bottom:.3em}
main h2{color:var(--ac2);margin-top:1.6em}
main h3{color:#c8cdd5}
a{color:var(--ac2)}
table{border-collapse:collapse;width:100%;margin:1em 0;font-size:13.5px}
th,td{border:1px solid var(--line);padding:6px 10px;text-align:left;vertical-align:top}
th{background:var(--panel);color:var(--ac)}
tr:nth-child(even) td{background:#191c21}
code{background:var(--panel);padding:1px 6px;border-radius:4px;font-size:13px}
blockquote{border-left:3px solid var(--ac);margin:1em 0;padding:.2em 1em;color:var(--mut);background:#191c21}
.badge{display:inline-block;background:var(--line);border-radius:4px;padding:0 6px;font-size:12px;color:var(--mut)}
.r-common{color:#9aa0a8}.r-uncommon{color:#6fbf73}.r-rare{color:#5aa9e6}.r-epic{color:#c586f0}.r-legendary{color:#e0a94e}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px;margin:1em 0}
.card{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:12px 14px}
.card h3{margin:0 0 6px;font-size:15px}
.mut{color:var(--mut);font-size:12.5px}
footer{color:var(--mut);font-size:12px;margin-top:40px;border-top:1px solid var(--line);padding-top:12px}
main{min-width:0}
table{display:block;overflow-x:auto}
body{-webkit-text-size-adjust:100%;overflow-wrap:anywhere}
/* 图解：纸卡容器，让浅色 SVG 在深底页面内保持原配色与可读性 */
figure.diagram{margin:18px 0;padding:14px 14px 8px;background:#f3eee3;
border:1px solid #d8d0be;border-radius:10px;color:#2b2620}
figure.diagram svg{display:block;width:100%;max-width:100%;height:auto}
figure.diagram svg.tall{display:none}
figure.diagram figcaption{font-size:12px;color:#6c6357;text-align:center;margin-top:6px}
/* 概念地图：概要小节的折叠展开区，内容由正源章节切片注入 */
details.concept{margin:16px 0 4px;border:1px solid var(--line);border-radius:8px;
background:var(--panel)}
details.concept>summary{cursor:pointer;display:flex;align-items:center;
min-height:44px;padding:10px 14px;list-style:none;color:var(--ac);font-size:14px}
details.concept>summary::-webkit-details-marker{display:none}
details.concept>summary::before{content:'▸';margin-right:9px;color:var(--mut)}
details.concept[open]>summary::before{content:'▾'}
details.concept>summary:hover{background:var(--line)}
.concept-body{padding:2px 14px 14px;border-top:1px solid var(--line)}
.concept-ref{margin-top:16px}
.ref-head{display:flex;flex-wrap:wrap;gap:6px 12px;justify-content:space-between;
font-size:12.5px;color:var(--mut);border-bottom:1px dashed var(--line);
padding-bottom:5px;margin-bottom:8px}
.concept-ref p,.concept-ref li{font-size:13.5px}
.concept-ref h3{font-size:14px;margin:12px 0 6px;color:var(--ac2)}
.concept-ref table{display:table;table-layout:fixed;font-size:12.5px}
.concept-ref th,.concept-ref td{overflow-wrap:anywhere}
.nav-toggle{display:none}
/* ===== 玩法 dashboard：6 个就地展开的概念抽屉（移动端优先） ===== */
.dashboard{padding-left:20px;padding-right:20px}
h1.dash-title{margin:0 0 4px}
p.dash-lead{font-size:13px;color:var(--mut);margin:0}
/* 独立网格类，绝不复用 .grid（会被其它 96 页的 @media 规则带偏） */
.concept-grid{display:grid;grid-template-columns:1fr;gap:8px;margin:16px 0 0}
details.drawer{border:1px solid var(--line);border-radius:8px;
background:var(--panel);overflow:hidden}
details.drawer>summary{cursor:pointer;display:flex;flex-wrap:wrap;
align-items:center;gap:2px 10px;min-height:56px;padding:10px 14px;list-style:none}
details.drawer>summary::-webkit-details-marker{display:none}
details.drawer>summary::before{content:'▸';font-size:14px;color:var(--mut);flex:none}
details.drawer[open]>summary::before{content:'▾';color:var(--ac)}
details.drawer[open]>summary{border-bottom:2px solid var(--ac)}
details.drawer>summary:hover,details.drawer>summary:active{background:var(--line)}
.drawer-name{font-size:17px;font-weight:600;color:var(--fg);min-width:0}
details.drawer[open]>summary .drawer-name{color:var(--ac)}
.drawer-meta{font-size:12.5px;color:var(--mut);margin-left:auto}
.drawer-body{padding:2px 14px 14px;background:#191c21}
.drawer-body h3{font-size:14px;margin:14px 0 6px;color:var(--ac2)}
.concept-summary{font-size:14px}
.concept-summary ul{padding-left:20px;margin:4px 0}
.concept-summary li{margin:4px 0}
.drawer-body figure.diagram{margin:12px 0 4px}
.ref-list-head{font-size:12.5px;color:var(--mut);margin:16px 0 8px;
padding-top:10px;border-top:1px solid var(--line)}
.drawer-body details.concept{margin:8px 0 0}
.drawer-body details.concept>summary{min-height:44px;font-size:13.5px}
.drawer-body .concept-body{padding:2px 12px 12px}
.dash-gap{margin-top:26px;border-top:1px solid var(--line);padding-top:12px}
.dash-gap h2{font-size:14px;font-weight:400;color:var(--mut);margin:0 0 6px}
.dash-gap ul,.dash-gap li{font-size:12.5px;color:var(--mut)}
@media (max-width:760px){
body{display:block;font-size:14px;
padding-left:env(safe-area-inset-left);padding-right:env(safe-area-inset-right)}
aside{position:sticky;top:0;z-index:20;width:auto;height:auto;flex:none;overflow:visible;
border-right:none;border-bottom:1px solid var(--line);
padding:10px calc(12px + env(safe-area-inset-right)) 10px calc(12px + env(safe-area-inset-left))}
aside .brand{display:inline-block;margin:0;font-size:14px;vertical-align:middle}
.nav-toggle{display:inline-block;vertical-align:middle;margin-left:10px;
background:var(--line);color:var(--fg);border:1px solid var(--line);border-radius:8px;
font:14px/1.2 inherit;padding:9px 12px;min-height:44px;cursor:pointer}
aside .nav-inner{display:none}
aside.nav-open .nav-inner{display:block;max-height:60vh;overflow:auto;
margin-top:10px;padding-top:8px;border-top:1px solid var(--line)}
aside .nav-inner h4{display:block;margin:12px 4px 4px}
aside .nav-inner a{display:block;padding:9px 10px;min-height:44px;
font-size:14px;border-radius:6px}
main{padding:16px 14px calc(28px + env(safe-area-inset-bottom));max-width:none}
table{font-size:12.5px}
.grid{grid-template-columns:1fr;gap:8px}
.card{padding:10px 12px}
main h1{font-size:22px}
main h2{font-size:18px}
figure.diagram{padding:10px 10px 8px}
figure.diagram svg:not(.tall){display:none}
figure.diagram svg.tall{display:block}
details.concept>summary{padding:11px 12px;font-size:14px}
.concept-body{padding:2px 10px 12px}
.concept-ref p,.concept-ref li{font-size:13.5px}
.concept-ref table{font-size:12px}
/* 375px 单列、零横滑、PWA 安全区；不新增固定 px min-width / 页面级横滑 */
.concept-grid{grid-template-columns:1fr;gap:8px}
.dashboard{padding-left:20px;padding-right:20px}
details.drawer>summary{padding:10px 12px}
.drawer-body{padding:2px 12px 12px}
aside{padding-top:calc(10px + env(safe-area-inset-top))}
}
"""


def rarity_class(r):
    return 'r-' + (r or 'common')


def card_table(cards, title=''):
    rows = []
    for c in cards:
        cost = c.get('cost') or {}
        cost_s = ' '.join(
            f'{k}:{v}' for k, v in cost.items() if v not in (None, 0))
        rows.append(
            '<tr><td><code>{id}</code></td><td>{name}<br><span class="mut">{kind}'
            '</span></td><td class="{rc}">{rarity}</td><td>{axis}</td>'
            '<td>{cost}</td><td>{desc}</td></tr>'.format(
                id=esc(c.get('id')), name=esc(c.get('name')),
                kind=esc(c.get('kind')), rc=rarity_class(c.get('rarity')),
                rarity=esc(c.get('rarity')), axis=esc(c.get('axis')),
                cost=esc(cost_s), desc=esc(c.get('describe'))))
    h = f'<h3>{esc(title)}</h3>' if title else ''
    return (h + '<table><tr><th>id</th><th>名称</th><th>稀有</th><th>轴</th>'
            '<th>费用</th><th>描述</th></tr>' + ''.join(rows) + '</table>')


def pool_table(items, cols, title=''):
    h = f'<h3>{esc(title)}</h3>' if title else ''
    head = ''.join(f'<th>{esc(c[1])}</th>' for c in cols)
    rows = []
    for it in items:
        rows.append('<tr>' + ''.join(
            f'<td>{esc(str(it.get(c[0], "") if not callable(c[0]) else c[0](it)))}</td>'
            for c in cols) + '</tr>')
    return h + '<table><tr>' + head + '</tr>' + ''.join(rows) + '</table>'


SW_JS = """/* wiki 离线缓存： precache 骨架 + 运行时缓存同源自举 */
/* __SW_CORE__ 由 Site.write() 按实际生成页动态注入；CACHE 版本随结构变更 bump */
const CACHE = 'wiki-v3';
const CORE = __SW_CORE__;
self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE)
    .then(c => c.addAll(CORE)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const u = new URL(e.request.url);
  if (e.request.method !== 'GET' || u.origin !== location.origin) return;
  e.respondWith(
    caches.match(e.request).then(hit => hit || fetch(e.request).then(res => {
      if (res.ok) {
        const copy = res.clone();
        caches.open(CACHE).then(c => c.put(e.request, copy));
      }
      return res;
    })));
});
"""

SW_REGISTER = """<script>
if ('serviceWorker' in navigator && location.protocol.startsWith('http'))
  navigator.serviceWorker.register('%ssw.js');
</script>"""

NAV_JS = """<script>
(function(){
  var b=document.querySelector('.nav-toggle'), a=document.querySelector('aside');
  if(!b||!a) return;
  function close(){a.classList.remove('nav-open');b.setAttribute('aria-expanded','false');}
  b.addEventListener('click',function(){
    var o=a.classList.toggle('nav-open');
    b.setAttribute('aria-expanded',o?'true':'false');
  });
  a.addEventListener('click',function(e){
    if(e.target && e.target.closest && e.target.closest('.nav-inner a')) close();
  });
  document.addEventListener('keydown',function(e){if(e.key==='Escape') close();});
})();
</script>"""


def _png(size, path):
    """纯 Python 生成图标：深底 + 琥珀圆环 + 蓝心（无第三方依赖）。"""
    import struct
    import zlib
    bg, ring, core = (22, 24, 29), (224, 169, 78), (127, 180, 216)
    cx = cy = size / 2
    r_out, r_in = size * 0.36, size * 0.16
    rows = []
    for y in range(size):
        row = bytearray([0])
        for x in range(size):
            d = ((x + .5 - cx) ** 2 + (y + .5 - cy) ** 2) ** .5
            c = core if d < r_in else (ring if d < r_out else bg)
            row += bytes(c)
        rows.append(bytes(row))
    raw = b''.join(rows)

    def chunk(tag, data):
        return (struct.pack('>I', len(data)) + tag + data
                + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff))

    png = (b'\x89PNG\r\n\x1a\n'
           + chunk(b'IHDR', struct.pack('>IIBBBBB', size, size, 8, 2, 0, 0, 0))
           + chunk(b'IDAT', zlib.compress(raw, 9))
           + chunk(b'IEND', b''))
    io.open(path, 'wb').write(png)


def sw_core(pages):
    """SW 预缓存清单：骨架 3 项 + 战场玩法页（概念已全部内联，无独立详情页）。

    由实际生成页动态派生，不手写 URL —— 改名/删页会立刻反映到清单，
    不会留下 addAll 404 导致 SW 整个 install 失败、离线归零的死链。
    """
    core = ['index.html', 'style.css', 'manifest.webmanifest']
    core += sorted(p for p in pages if p == DASH_PATH)
    return core


class Site:
    def __init__(self):
        self.pages = {}   # path -> (title, body_html)
        self.nav = []     # (group, [(title, path)])

    def add(self, path, title, body, group=None, nav_title=None):
        self.pages[path] = (title, body)
        if group:
            for g, items in self.nav:
                if g == group:
                    items.append((nav_title or title, path))
                    return
            self.nav.append((group, [(nav_title or title, path)]))

    def write(self):
        if os.path.exists(OUT):
            shutil.rmtree(OUT)
        os.makedirs(OUT)
        for path, (title, body) in self.pages.items():
            full = os.path.join(OUT, path)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            html = self.shell(path, title, body)
            io.open(full, 'w', encoding='utf-8').write(html)
        io.open(os.path.join(OUT, 'style.css'), 'w', encoding='utf-8').write(CSS)
        # PWA：manifest + service worker + 图标
        manifest = {
            "name": SITE_TITLE,
            "short_name": "设计Wiki",
            "start_url": ".",
            "scope": ".",
            "display": "standalone",
            "background_color": "#16181d",
            "theme_color": "#16181d",
            "icons": [
                {"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
                {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"},
            ],
        }
        io.open(os.path.join(OUT, 'manifest.webmanifest'), 'w',
                encoding='utf-8').write(json.dumps(manifest, ensure_ascii=False))
        io.open(os.path.join(OUT, 'sw.js'), 'w', encoding='utf-8').write(
            SW_JS.replace('__SW_CORE__',
                          json.dumps(sw_core(self.pages), ensure_ascii=False)))
        _png(192, os.path.join(OUT, 'icon-192.png'))
        _png(512, os.path.join(OUT, 'icon-512.png'))

    def shell(self, cur, title, body):
        # 相对路径：file:// 本地打开和 GitHub Pages 项目子路径下都能工作
        prefix = '../' * cur.count('/')

        def rel(p):
            return f'{BASE}/{p}' if BASE else prefix + p

        nav = []
        for g, items in self.nav:
            nav.append(f'<h4>{esc(g)}</h4>')
            for t, p in items:
                style = ' style="color:var(--ac);background:var(--line)"' if p == cur else ''
                nav.append(f'<a href="{rel(p)}"{style}>{esc(t)}</a>')
        nav_html = (f'<a class="brand" href="{rel("index.html")}">{SITE_TITLE}</a>'
                    '<button class="nav-toggle" type="button" aria-expanded="false" '
                    'aria-controls="nav-inner">目录</button>'
                    f'<div class="nav-inner" id="nav-inner">{"".join(nav)}</div>')
        main_cls = 'dashboard' if cur == DASH_PATH else ''
        main_tag = f'<main class="{main_cls}">' if main_cls else '<main>'
        return ('<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">'
                '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
                '<meta name="theme-color" content="#16181d">'
                '<meta name="apple-mobile-web-app-capable" content="yes">'
                '<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">'
                f'<title>{esc(title)} · {SITE_TITLE}</title>'
                f'<link rel="stylesheet" href="{rel("style.css")}">'
                f'<link rel="manifest" href="{rel("manifest.webmanifest")}">'
                f'<link rel="icon" type="image/png" href="{rel("icon-192.png")}">'
                '</head><body>'
                f'<aside id="nav">{nav_html}</aside>{main_tag}{body}'
                f'<footer>生成自 docs/ddd 正源 + site/ 玩法源 · push main 自动部署</footer>'
                '</main>' + NAV_JS + SW_REGISTER % prefix + '</body></html>')


def load_md(path):
    return io.open(path, encoding='utf-8').read()


def site_link(cur, target):
    """站内链接：与 Site.shell 的 rel() 完全同口径，WIKI_BASE 子路径下不断链。"""
    if BASE:
        return f'{BASE}/{target}'
    return '../' * cur.count('/') + target


def parse_dashboard(path):
    """极简概要源 → (一句话引导语, {概念标题: 该节正文 md})。"""
    text = load_md(path)
    parts = re.split(r'(?m)^(## .+)$', text)
    intro = ''
    for line in parts[0].splitlines():
        s = line.strip()
        if not s or s.startswith('# ') or s.startswith('图解：'):
            continue
        intro = s          # 只取第一句引导，其余说明块一概不堆到 dashboard
        break
    sections = {}
    for i in range(1, len(parts), 2):
        label = parts[i][3:].strip()
        body = parts[i + 1] if i + 1 < len(parts) else ''
        sections[label] = body.strip()
    return esc(intro), sections


def bullet_count(body_md):
    return sum(1 for l in body_md.splitlines() if l.strip().startswith('- '))


def load_figures(path):
    """图解正源按 ## 小节切片 → {概念标题: <figure class="diagram"> ...}。

    图源是唯一出处：宽/竖双版 SVG 原字节不动，仅给容器加纸卡 class；
    单位概念本就无图，保持「未接线」，不挪用其它概念图、不临时补画。
    """
    if not os.path.exists(path):
        raise concept_map.ConceptMapError('图解正源缺失：%s' % path)
    text = io.open(path, encoding='utf-8').read()
    out = {}
    segs = re.split(r'(<h2[^>]*>.*?</h2>)', text, flags=re.S)
    for i in range(1, len(segs), 2):
        label = re.sub(r'<[^>]+>', '', segs[i]).strip()
        label = re.sub(r'^[一二三四五六七八九十]+、\s*', '', label)
        seg = segs[i + 1] if i + 1 < len(segs) else ''
        m = re.search(r'<figure>.*?</figure>', seg, re.S)
        if m and label:
            out[label] = m.group(0).replace(
                '<figure>', '<figure class="diagram">', 1)
    n_svg = sum(f.count('<svg') for f in out.values())
    n_tall = sum(f.count('class="tall"') for f in out.values())
    if len(out) != 5 or n_svg != 10 or n_tall != 5:
        raise concept_map.ConceptMapError(
            '图解切片异常：%d 个 figure / %d 个 svg / %d 个竖版（期望 5/10/5）'
            % (len(out), n_svg, n_tall))
    return out


def build_dashboard(cmap, intro, sections, figs):
    """移动端优先的单页导航盘：6 个就地展开的概念抽屉 + 末尾「未定」。

    name="concept" 让浏览器原生互斥（同时只开一个），无 JS、无跳转；
    抽屉内按「极简概要 → 图解 → 逐节正源」渐进披露，全部内联，离线可读。
    """
    out = ['<h1 class="dash-title">战场玩法 · 概念导航</h1>',
           '<p class="dash-lead">%s</p>' % intro,
           '<div class="concept-grid">']
    for c in cmap['concepts']:
        h = c['heading']
        refs = c.get('refs') or []
        n_sum = bullet_count(sections.get(h, ''))
        out.append(
            '<details class="drawer" name="concept">'
            '<summary><span class="drawer-name">%s</span>'
            '<span class="drawer-meta">概要 %d 条 · 正源 %d 处</span></summary>'
            '<div class="drawer-body">' % (esc(h), n_sum, len(refs)))
        out.append('<h3>极简概要</h3>')
        out.append('<div class="concept-summary">%s</div>'
                   % md_html(sections.get(h, '')))
        fig = figs.get(h)
        if fig:
            out.append('<h3>图解</h3>')
            out.append(fig)
        out.append('<div class="ref-list-head">DDD 正源 · %d 处，逐节点开</div>'
                   % len(refs))
        for r in refs:
            doc, sec = r['doc'], r['section']
            title, body = concept_map.slice_section(doc, sec, ROOT)
            page = cmap['pages'].get(doc)
            link = ('<a href="%s">完整原文 →</a>' % site_link(DASH_PATH, page)
                    if page else '')
            short = esc(os.path.basename(doc)[:-3])
            head = ('<div class="ref-head"><span>%s · %s</span>%s</div>'
                    % (short, esc(title), link))
            out.append(
                '<details class="concept">'
                '<summary>%s · %s</summary>'
                '<div class="concept-body"><section class="concept-ref">%s%s'
                '</section></div></details>'
                % (short, esc(title), head, md_html(body)))
        out.append('</div></details>')
    out.append('</div>')
    if '未定' in sections:
        out.append('<div class="dash-gap"><h2>未定</h2>%s</div>'
                   % md_html(sections['未定']))
    return ''.join(out)


def main():
    site = Site()
    docs = load_docs()

    # 概念地图：发布期先校验全部锚点，断链或改名即中止并点名位置
    cmap = concept_map.load_map()
    report = concept_map.check(cmap, ROOT)
    print(concept_map.format_report(report))

    # 站点侧三份玩法页专属源（docs/ 下不留副本）
    intro, sections = parse_dashboard(os.path.join(SITE_SRC, 'dashboard.md'))
    figs = load_figures(os.path.join(SITE_SRC, 'figures.html'))

    # 导航首组「玩法」：dashboard 是唯一页，6 个概念抽屉全部就地展开
    site.add(DASH_PATH, '战场玩法（概念导航）',
             build_dashboard(cmap, intro, sections, figs),
             '玩法', nav_title='战场玩法')

    manifest = json.load(io.open(os.path.join(JSON_DIR, 'manifest.json'),
                                 encoding='utf-8'))
    fac_names = {f['id']: f['name'] for f in manifest['factions']}

    # ---------- 派系 / 家族 / 英雄数据页 ----------
    fam_doc = {}   # familyId -> family doc
    for name, doc in docs.items():
        if name.startswith('family_') and name.endswith('.skills.json'):
            fam_doc[doc.get('familyId')] = doc
    fac_doc = {}
    for name, doc in docs.items():
        if name.startswith('faction_') and name.endswith('.skills.json'):
            fac_doc[doc.get('factionId')] = doc

    # 派系总览首页
    fams_by_fac = {}
    for fid, fd in fam_doc.items():
        fams_by_fac.setdefault(fd.get('faction'), []).append(fd)
    hero_files = sorted(n for n in docs if n.startswith('hero_')
                        and n.endswith('.skills.json'))

    cards = []
    cards.append(f'<h1>{SITE_TITLE}</h1>')
    cards.append('<p>本库是 MyPixelCardGame v2 的唯一设计权威源：9 派系 × 22 家族 × '
                 f'{len(hero_files)} 英雄，卡池与机制文档即仓库 <code>docs/</code>。'
                 '全站由 <code>docs/tools/build_wiki.py</code> 生成。</p>')
    dash_href = site_link('index.html', DASH_PATH)
    cards.append('<div class="card"><h3><a href="%s">'
                 '战场玩法 · 概念导航</a></h3>'
                 '<div class="mut">6 个概念就地展开 · 一次只开一个</div>'
                 '<p>两方在定长队列里按行动条轮流出手。点开任一概念，'
                 '就地看概要、图解与 DDD 正源，不跳页。</p>'
                 '</div>' % dash_href)
    for fac in manifest['factions']:
        fid = fac['id']
        fams = sorted(fams_by_fac.get(fid, []), key=lambda x: x['familyId'])
        n_cards = sum(len(f.get('cards') or []) for f in fams)
        n_cards += len((fac_doc.get(fid) or {}).get('cards') or [])
        heroes = [h for h in hero_files
                  if docs[h].get('faction') == fid]
        fam_links = '、'.join(
            f'<a href="families/{f["familyId"]}.html">{esc(f.get("familyName",""))}'
            f'（{len(f.get("cards") or [])} 卡）</a>' for f in fams)
        hero_links = '、'.join(
            f'<a href="heroes/{h.replace(".skills.json","")}.html">'
            f'{esc(docs[h].get("heroName",""))}</a>' for h in heroes) or '—'
        fd = fac_doc.get(fid) or {}
        body = (f'<div class="card"><h3><a href="factions/{fid}.html">'
                f'{esc(fac["name"])}</a> <span class="badge">{fid}</span></h3>'
                f'<div class="mut">{n_cards} 家族公共卡 · {len(heroes)} 英雄</div>'
                f'<p>家族：{fam_links}</p><p>英雄：{hero_links}</p>'
                f'<p>{esc((fd.get("cards") and "派系公共卡：%d 张" % len(fd["cards"])) or "派系公共卡：0 张")}</p>'
                '</div>')
        cards.append(body)
    site.add('index.html', '首页', ''.join(cards))

    # 派系页：基调 md + 派系公共卡
    import glob as _glob
    tone_dir = os.path.join(DOCS, 'meta', '派系')
    tones = {os.path.basename(p): p for p in _glob.glob(os.path.join(tone_dir, '*.md'))}
    for fac in manifest['factions']:
        fid = fac['id']
        body = [f'<h1>派系 · {esc(fac["name"])} <span class="badge">{fid}</span></h1>']
        tone = next((p for n, p in tones.items() if n.startswith(fid)), None)
        if tone:
            body.append(md_html(load_md(tone)))
        fd = fac_doc.get(fid) or {}
        if fd.get('cards'):
            body.append(card_table(fd['cards'], '派系公共卡（f%s）' % fid[8:]))
        if fd.get('statusDefs') or fd.get('domainDefs') or fd.get('unitDefs'):
            body.append(pool_table(
                (fd.get('statusDefs') or []) + (fd.get('unitDefs') or [])
                + (fd.get('domainDefs') or []),
                [('id', 'id'), ('name', '名称'),
                 (lambda x: x.get('name') and '' or '', '')],
                '派系蓝本池'))
        site.add(f'factions/{fid}.html', f'派系·{fac["name"]}', ''.join(body),
                 '卡池')

    # 家族页：身份卡节（md 全文太长，挂链接）+ 家族卡
    idcard_path = os.path.join(DOCS, 'meta', '家族身份卡.md')
    idcard_html = md_html(load_md(idcard_path))
    for fid, fd in sorted(fam_doc.items()):
        body = [f'<h1>家族 · {esc(fd.get("familyName",""))} '
                f'<span class="badge">{fid}</span></h1>']
        body.append(f'<p>派系：<a href="../factions/{fd.get("faction")}.html">'
                    f'{esc(fac_names.get(fd.get("faction"), ""))}</a></p>')
        if fd.get('cards'):
            body.append(card_table(fd['cards'], '家族公共卡（j%s）'
                                   % fd.get('faction', '').split('_')[-1]))
        if fd.get('statusDefs') or fd.get('unitDefs'):
            body.append(pool_table(
                (fd.get('statusDefs') or []) + (fd.get('unitDefs') or []),
                [('id', 'id'), ('name', '名称'), ('note', '说明')], '家族蓝本池'))
        site.add(f'families/{fid}.html',
                 f'家族·{fd.get("familyName","")}', ''.join(body), '卡池')

    # 英雄页
    for h in hero_files:
        hd = docs[h]
        hid = h.replace('.skills.json', '')
        body = [f'<h1>{esc(hd.get("heroName",""))} <span class="badge">{hid}</span></h1>']
        body.append(f'<p>家族：<a href="../families/{hd.get("family")}.html">'
                    f'{esc((fam_doc.get(hd.get("family")) or {}).get("familyName",""))}'
                    f'</a> · 派系：<a href="../factions/{hd.get("faction")}.html">'
                    f'{esc(fac_names.get(hd.get("faction"), ""))}</a></p>')
        body.append(f'<blockquote>{esc(hd.get("playstyle",""))}</blockquote>')
        if hd.get('cards'):
            body.append(card_table(hd['cards'], '英雄私有卡（≤6）'))
        site.add(f'heroes/{hid}.html', hd.get('heroName', hid), ''.join(body),
                 '卡池')

    # ---------- 机制文档（md 树） ----------
    md_pages = [
        ('docs/meta/WORKFLOW.md', 'workflow/WORKFLOW.html', 'WORKFLOW 工作流'),
        ('docs/meta/生成工作流.md', 'workflow/生成工作流.html', '生成工作流（层〇–层四）'),
        ('docs/meta/派系基调.md', 'design/派系基调.html', '派系基准总表'),
        ('docs/meta/家族身份卡.md', 'design/家族身份卡.html', '家族身份卡（22）'),
        ('docs/meta/骨架重议.md', 'design/骨架重议.html', '骨架重议'),
        ('docs/meta/SCHEMA.md', 'design/SCHEMA.html', 'SCHEMA 结构规范'),
        ('docs/meta/待办.md', 'design/待办.html', '待办清单'),
        ('docs/meta/迁移映射表.md', 'design/迁移映射表.html', '迁移映射表'),
        ('docs/ddd/README.md', 'design/ddd-README.html', 'DDD 不变量总表'),
        ('docs/ddd/contexts/编目上下文.md', 'design/ctx-编目.html', '编目上下文'),
        ('docs/ddd/contexts/编队上下文.md', 'design/ctx-编队.html', '编队上下文'),
        ('docs/ddd/contexts/战场上下文.md', 'design/ctx-战场.html', '战场上下文'),
        ('docs/ddd/contexts/战斗上下文.md', 'design/ctx-战斗.html', '战斗上下文'),
        ('docs/ddd/contexts/效果上下文.md', 'design/ctx-效果.html', '效果上下文'),
        ('docs/ddd/params/共享内核参数.md', 'design/params-共享内核.html', '共享内核参数'),
        ('docs/ddd/params/效果参数.md', 'design/params-效果.html', '效果参数'),
        ('docs/ddd/params/编队参数.md', 'design/params-编队.html', '编队参数'),
        ('docs/ddd/params/召唤物参数.md', 'design/params-召唤物.html', '召唤物参数'),
        ('docs/ddd/params/执行参数.md', 'design/params-执行.html', '执行参数'),
    ]
    for rel, out_path, title in md_pages:
        src = os.path.join(ROOT, rel)
        if os.path.exists(src):
            site.add(out_path, title, md_html(load_md(src)), '机制文档')

    # 指针指向的站点页必须真的生成，否则展开区会出现死链
    concept_map.check_pages(cmap, site.pages)

    # 接线自检：6 个抽屉 + 26 个正源折叠块必须全部落在 dashboard 这一页
    if DASH_PATH not in site.pages:
        raise concept_map.ConceptMapError('战场玩法 dashboard 未生成')
    dash = site.pages[DASH_PATH][1]
    n_ref = sum(len(c.get('refs') or []) for c in cmap['concepts'])
    n_drawer = dash.count('<details class="drawer" name="concept">')
    n_details = dash.count('<details class="concept">')
    n_links = dash.count('完整原文 →')
    if (n_drawer != len(cmap['concepts']) or n_details != n_ref
            or n_details != len(report) or n_links != n_ref):
        raise concept_map.ConceptMapError(
            '单页接线不齐：%d 个概念 / %d 个抽屉 / %d 个 refs / '
            '%d 个报告锚点 / %d 个正源块 / %d 条原文链接'
            % (len(cmap['concepts']), n_drawer, n_ref, len(report),
               n_details, n_links))

    # SW 预缓存清单逐项必须真的生成：addAll 任一 404 会让 SW install 整体失败
    written = set(site.pages) | {'style.css', 'manifest.webmanifest'}
    sw_missing = [p for p in sw_core(site.pages) if p not in written]
    if sw_missing:
        raise concept_map.ConceptMapError(
            'sw.js 预缓存清单含未生成文件：%s' % '、'.join(sw_missing))

    site.write()
    n = len(site.pages)
    print('wiki built: %d pages -> %s' % (n, OUT))


if __name__ == '__main__':
    try:
        main()
    except concept_map.ConceptMapError as e:
        print('BUILD FAILED：%s' % e, file=sys.stderr)
        sys.exit(1)
