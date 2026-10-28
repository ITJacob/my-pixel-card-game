# -*- coding: utf-8 -*-
"""共享状态注册表加载：扫描 *.statuses.json，产出 (pid, label, statusDef) 流。

v2 派系私有状态已并入 faction_NN.skills.json 顶层 statusDefs[]；
*.statuses.json 只剩跨派系公共注册表 common.statuses.json。
本 loader 只认 *.statuses.json（common 用）；派系顶层 statusDefs 由消费方直接读派系文件。
"""
import io, os, glob, json

HERE = os.path.dirname(os.path.abspath(__file__))
JSON_DIR = os.path.join(os.path.dirname(HERE), "json")

STATUS_SCHEMA = os.path.join(JSON_DIR, "schema", "skills.schema.json")
_statusdef_schema = None


def status_def_schema():
    """复用 skills.schema.json 的 $defs/statusDef 作为 *.statuses.json 每项的校验基准。"""
    global _statusdef_schema
    if _statusdef_schema is None:
        sch = json.load(io.open(STATUS_SCHEMA, encoding="utf-8"))
        _statusdef_schema = sch.get("$defs", {}).get("statusDef")
    return _statusdef_schema


def iter_status_defs():
    """Yield (pid, label, def_dict) for every statusDef across *.statuses.json。"""
    for f in sorted(glob.glob(os.path.join(JSON_DIR, "*.statuses.json"))):
        pid = os.path.basename(f).replace(".statuses.json", "")
        label = os.path.basename(f)
        try:
            d = json.load(io.open(f, encoding="utf-8"))
        except Exception:
            continue
        for sd in d.get("statusDefs") or []:
            yield (pid, label, sd)


def load_common_ids():
    """返回 common.statuses.json 中声明的 id 集合。"""
    p = os.path.join(JSON_DIR, "common.statuses.json")
    if not os.path.exists(p):
        return set()
    try:
        d = json.load(io.open(p, encoding="utf-8"))
    except Exception:
        return set()
    return set(s["id"] for s in d.get("statusDefs") or [])
