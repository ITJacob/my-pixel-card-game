# -*- coding: utf-8 -*-
"""三层作用域定义加载：global / faction / hero 文件的五池统一入口。

文件布局（按文件名约定发现，manifest 不登记 global/hero）：
  global.skills.json       全域级（唯一）：跨派系复用内容
  faction_NN.skills.json   派系级（manifest.factions 登记）：派系公共卡 + 派系蓝本池
  hero_NN.skills.json      英雄级：英雄独自卡；NN 与 faction_NN 配对

引用/$extends 解析序（引擎与工具一致）：
  hero 文件   → 本文件 → 同派系 faction 文件 → global
  faction 文件 → 本文件 → global
  global 文件 → 本文件
禁同层跨文件 $extends（hero_01 不能 extends hero_02 / faction_01 的条目）。

$extends 物化规则（声明式，加载时合并）：
  逐字段浅合并，子字段存在即覆写；tags 取父∪子并集（继承语义核心）；
  嵌套对象整体替换，不做深合并。父定义在同名池内按解析序查找。
"""
import io
import os
import glob
import json

HERE = os.path.dirname(os.path.abspath(__file__))
JSON_DIR = os.path.join(os.path.dirname(HERE), "json")

POOLS = ("cards", "statusDefs", "unitDefs", "zoneDefs", "domainDefs")
DEF_FOR_POOL = {"cards": "card", "statusDefs": "statusDef",
                "unitDefs": "unitDef", "zoneDefs": "zoneDef", "domainDefs": "domainDef"}
GLOBAL_FILE = "global.skills.json"

_docs = None


def load_docs():
    """{filename: doc} 全量加载（进程内缓存）。含 global/faction/hero 全部 *.skills.json。"""
    global _docs
    if _docs is None:
        _docs = {}
        for f in sorted(glob.glob(os.path.join(JSON_DIR, "*.skills.json"))):
            name = os.path.basename(f)
            try:
                _docs[name] = json.load(io.open(f, encoding="utf-8"))
            except Exception:
                continue
    return _docs


def file_level(doc):
    return doc.get("level")


def chain_files(fname):
    """$extends/引用解析链（含本文件）：hero → 同派系 faction → global。"""
    doc = load_docs().get(fname)
    lvl = (doc or {}).get("level")
    if lvl == "hero":
        num = fname[len("hero_"):len("hero_") + 2]
        fac = "faction_%s.skills.json" % num
        return [fname, fac, GLOBAL_FILE] if fac in load_docs() else [fname, GLOBAL_FILE]
    if lvl == "faction":
        return [fname, GLOBAL_FILE]
    return [fname]


def _pool_table(fname, pool):
    """某文件某池的 {id: 条目}（未物化）。"""
    out = {}
    for it in (load_docs().get(fname) or {}).get(pool) or []:
        if isinstance(it, dict) and it.get("id"):
            out[it["id"]] = it
    return out


def merge_item(item, parent):
    """浅合并：子存在即覆写；tags 取并集；嵌套对象整体替换。"""
    merged = dict(parent)
    for k, v in item.items():
        if k == "$extends":
            continue
        if k == "tags" and isinstance(v, list) and isinstance(merged.get("tags"), list):
            seen, tags = set(), []
            for t in list(merged["tags"]) + list(v):
                if t not in seen:
                    seen.add(t)
                    tags.append(t)
            merged["tags"] = tags
        else:
            merged[k] = v
    return merged


def materialize(fname, pool, errors=None):
    """物化某文件某池：解析并合并 $extends。

    errors 为列表时收集「父缺失 / 禁同层跨文件 / 循环继承」；
    返回 {id: 物化条目}（父合并失败时退回未合并副本并继续）。
    """
    docs = load_docs()
    own = _pool_table(fname, pool)
    result = {}
    for iid, item in own.items():
        result[iid] = _resolve(fname, pool, iid, item, own, [], errors)
    return result


def _resolve(fname, pool, iid, item, own, stack, errors):
    ref = item.get("$extends")
    if not ref:
        return item
    if iid in stack:
        if errors is not None:
            errors.append("%s %s: $extends 循环继承（%s → %s）"
                          % (fname, iid, " → ".join(stack), iid))
        return item
    # 解析序：本文件池 → 链上后续文件同名池
    for cf in chain_files(fname):
        table = _pool_table(cf, pool)
        if cf == fname:
            table = own
        if ref in table and table[ref] is not item:
            parent = table[ref]
            if "$extends" in parent:
                parent = _resolve(cf, pool, ref, parent, table, stack + [iid], errors)
            return merge_item(item, parent)
    # 链上未找到：区分「同层跨文件」与「不存在」
    if errors is not None:
        docs = load_docs()
        hit = None
        for other, od in docs.items():
            if other == fname or od.get("level") != (docs.get(fname) or {}).get("level"):
                continue
            if ref in _pool_table(other, pool):
                hit = other
                break
        if hit:
            errors.append("%s %s: $extends '%s' 定义于同层文件 %s（禁同层跨文件继承）"
                          % (fname, iid, ref, hit))
        else:
            errors.append("%s %s: $extends '%s' 在解析链 %s 中不存在"
                          % (fname, iid, ref, " → ".join(chain_files(fname))))
    return item


def all_pool_ids(pool):
    """全库某池 id 集合（未物化，跨全部文件；供存在性检查）。"""
    out = set()
    for fname in load_docs():
        out |= set(_pool_table(fname, pool))
    return out


def iter_status_defs():
    """Yield (scope_key, label, statusDef)：全库 statusDef 流（物化后）。

    scope_key = global / faction_NN / hero_NN；label = 文件名。
    """
    docs = load_docs()
    for fname in sorted(docs):
        doc = docs[fname]
        key = doc.get("factionId") or doc.get("heroId") or doc.get("level") or fname
        for iid, sd in materialize(fname, "statusDefs").items():
            yield (key, fname, sd)
        for c in doc.get("cards") or []:
            for sd in c.get("statusDefs") or []:
                yield (key, fname, sd)
