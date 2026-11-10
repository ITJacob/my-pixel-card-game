# -*- coding: utf-8 -*-
"""GitHub Pages wiki 静态生成器。

输入：docs/ 下全部设计文档（md）+ docs/json/ 卡池数据。
输出：_site/（纯静态 HTML，侧栏导航，无 JS 依赖）。
用法：python docs/tools/build_wiki.py  （仓库根运行；wiki/ 为主题资源目录）
"""
import io
import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
DOCS = os.path.join(ROOT, 'docs')
JSON_DIR = os.path.join(DOCS, 'json')
OUT = os.path.join(ROOT, '_site')
WIKI = os.path.join(ROOT, 'wiki')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from status_loader import load_docs  # noqa: E402

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
@media (max-width:760px){
body{display:block;font-size:14px}
aside{position:static;width:auto;height:auto;flex:none;border-right:none;border-bottom:1px solid var(--line);padding:12px 12px 8px}
aside .brand{display:inline-block;margin:0 12px 6px 0}
aside h4{display:inline-block;margin:6px 10px 2px 0;vertical-align:baseline}
aside a{display:inline-block;padding:3px 8px;margin:2px 2px;font-size:13px}
main{padding:16px 14px;max-width:none}
table{font-size:12.5px}
.grid{grid-template-columns:1fr 1fr;gap:8px}
.card{padding:10px 12px}
main h1{font-size:22px}
main h2{font-size:18px}
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

    def shell(self, cur, title, body):
        # 相对路径：file:// 本地打开和 GitHub Pages 项目子路径下都能工作
        prefix = '../' * cur.count('/')

        def rel(p):
            return f'{BASE}/{p}' if BASE else prefix + p

        nav = [f'<a class="brand" href="{rel("index.html")}">{SITE_TITLE}</a>']
        for g, items in self.nav:
            nav.append(f'<h4>{esc(g)}</h4>')
            for t, p in items:
                style = ' style="color:var(--ac);background:var(--line)"' if p == cur else ''
                nav.append(f'<a href="{rel(p)}"{style}>{esc(t)}</a>')
        return ('<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">'
                '<meta name="viewport" content="width=device-width,initial-scale=1">'
                f'<title>{esc(title)} · {SITE_TITLE}</title>'
                f'<link rel="stylesheet" href="{rel("style.css")}"></head><body>'
                f'<aside>{"".join(nav)}</aside><main>{body}'
                f'<footer>生成自仓库 docs/ 权威源 · push main 自动部署</footer>'
                '</main></body></html>')


def load_md(path):
    return io.open(path, encoding='utf-8').read()


def main():
    site = Site()
    docs = load_docs()

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

    # 身份卡锚点页单独挂出（太长，独立页已含）
    site.write()
    n = len(site.pages)
    print('wiki built: %d pages -> %s' % (n, OUT))


if __name__ == '__main__':
    main()
