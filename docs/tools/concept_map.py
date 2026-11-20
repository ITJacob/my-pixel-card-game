# -*- coding: utf-8 -*-
"""概念地图：概要与 DDD 正源之间的指针契约。

`site/concept-map.json` 只登记「概念 → 正源文件 + ## 章节」，不复制任何规则文字。
构建期按章节切片并注入 <details> 展开区；章节改名或删除会让构建直接失败并点名位置。
指针表已从 docs/meta/ 迁到站点侧入库目录 site/；DDD 正源仍在 docs/ddd/，一字不动。

用法：
    python docs/tools/concept_map.py --check        # 独立校验锚点，可进 CI
"""
import argparse
import hashlib
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
MAP_PATH = os.path.join(ROOT, 'site', 'concept-map.json')


class ConceptMapError(Exception):
    pass


def esc(s):
    return (s or '').replace('&', '&amp;').replace('<', '&lt;').replace(
        '>', '&gt;')


def load_map(path=MAP_PATH):
    if not os.path.exists(path):
        raise ConceptMapError('概念地图缺失：%s' % path)
    try:
        m = json.load(io.open(path, encoding='utf-8'))
    except Exception as e:
        raise ConceptMapError('概念地图 JSON 解析失败：%s' % e)
    if not isinstance(m.get('pages'), dict) or not isinstance(
            m.get('concepts'), list):
        raise ConceptMapError('概念地图结构错误：需要 pages 对象与 concepts 数组')
    return m


def slice_section(doc, section, root=ROOT):
    """抽 `## 标题`（含其下 ### 子节）到下一个 `## ` 之前，返回 (标题, 正文 md)。"""
    path = os.path.join(root, doc)
    if not os.path.exists(path):
        raise ConceptMapError('正源缺失：%s' % doc)
    lines = io.open(path, encoding='utf-8').read().splitlines()
    heads = [i for i, l in enumerate(lines) if l.startswith('## ')]
    hits = [i for i in heads if section in lines[i]]
    if not hits:
        raise ConceptMapError(
            '锚点断链：%s 中无 ## 标题包含「%s」' % (doc, section))
    if len(hits) > 1:
        raise ConceptMapError(
            '锚点歧义：%s 中「%s」命中 %d 个标题：%s' % (
                doc, section, len(hits),
                ' / '.join(lines[i][3:].strip() for i in hits)))
    start = hits[0]
    end = next((i for i in heads if i > start), len(lines))
    return lines[start][3:].strip(), '\n'.join(lines[start + 1:end]).strip()


def check(m, root=ROOT):
    """全部锚点必须存在且唯一；返回同步报告行。"""
    errors, seen, report = [], set(), []
    for c in m['concepts']:
        h = c.get('heading')
        if not h:
            errors.append('存在无 heading 的概念')
            continue
        if h in seen:
            errors.append('概念 heading 重复：%s' % h)
        seen.add(h)
        refs = c.get('refs') or []
        if not refs:
            errors.append('概念「%s」没有 refs' % h)
        for r in refs:
            doc, sec = r.get('doc'), r.get('section')
            if not doc or not sec:
                errors.append('概念「%s」存在缺 doc/section 的 ref' % h)
                continue
            if doc not in m['pages']:
                errors.append('概念「%s」引用的 %s 未在 pages 登记站点页' % (h, doc))
            try:
                title, body = slice_section(doc, sec, root)
            except ConceptMapError as e:
                errors.append('概念「%s」：%s' % (h, e))
                continue
            report.append((h, doc, sec, title,
                           hashlib.sha256(body.encode('utf-8')).hexdigest()[:8],
                           len(body)))
    if errors:
        raise ConceptMapError('概念地图校验失败（%d 项）：\n  - %s' % (
            len(errors), '\n  - '.join(errors)))
    return report


def check_pages(m, site_pages):
    """指针指向的站点页必须真的生成出来。"""
    missing = sorted({p for p in m['pages'].values() if p not in site_pages})
    if missing:
        raise ConceptMapError('概念地图指向的站点页未生成：\n  - %s'
                              % '\n  - '.join(missing))


def format_report(report):
    out = ['概念地图同步报告：%d 个锚点' % len(report)]
    cur = None
    for h, doc, sec, title, sha, n in report:
        if h != cur:
            out.append('  %s' % h)
            cur = h
        out.append('    %-20s %-16s %s  %4d 字' % (
            os.path.basename(doc)[:-3], sec, sha, n))
    return '\n'.join(out)


def details_html(heading, m, render, prefix='../'):
    """生成折叠展开区；render 为 md → html 的回调。"""
    c = next((x for x in m['concepts'] if x['heading'] == heading), None)
    if not c:
        return ''
    blocks = []
    for r in c['refs']:
        doc, sec = r['doc'], r['section']
        title, body = slice_section(doc, sec)
        page = m['pages'].get(doc)
        link = ('<a href="%s%s">完整原文 →</a>' % (prefix, page)
                if page else '')
        blocks.append(
            '<section class="concept-ref">'
            '<div class="ref-head"><span>%s · %s</span>%s</div>%s</section>'
            % (esc(os.path.basename(doc)[:-3]), esc(title), link,
               render(body)))
    sha = hashlib.sha256(''.join(blocks).encode('utf-8')).hexdigest()[:8]
    return ('<!-- concept-map:%s sha=%s -->\n' % (esc(heading), sha)
            + '<details class="concept">'
            + '<summary>展开详细规则 · %d 处正源</summary>' % len(blocks)
            + '<div class="concept-body">' + ''.join(blocks)
            + '</div></details>')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true', help='仅校验锚点')
    ap.add_argument('--map', default=MAP_PATH)
    a = ap.parse_args()
    print(format_report(check(load_map(a.map))))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except ConceptMapError as e:
        print('FAIL: %s' % e, file=sys.stderr)
        sys.exit(1)
