# -*- coding: utf-8 -*-
"""按 JSON Schema 校验技能池全库 + 跨字段一致性检查。

用法:
    python docs/tools/validate_schema.py            # 校验 manifest + 9 份派系文件 + common 状态表
    python docs/tools/validate_schema.py --max 20   # 每文件最多打印 20 条错误

依赖: jsonschema（可选）
    pip install jsonschema
未安装时只执行不依赖它的跨字段检查（第二部分）。

与 docs/tools/validate.py 的分工:
    validate.py        —— 语义/枚举/引用完整性校验（原语与参数取值域、状态 id 存在性、
                          rarity↔sequence 映射、界域租金等）
    validate_schema.py —— 结构校验（字段是否存在、类型是否正确、有无未知字段）
                          + 跨字段一致性（id 前缀↔scope↔派系号、manifest 对齐）
两者都应为 0 错误才视为合规。

v2 派系制：卡 id 形态 ^(f|h)NN_<slug>（NN=派系号）；axis 为自由字符串（无顶层 axes 声明表）。
"""
import io, os, re, sys, glob, json

HERE = os.path.dirname(os.path.abspath(__file__))          # docs/tools/
JSON_DIR = os.path.join(os.path.dirname(HERE), "json")      # docs/json/
SCHEMA_DIR = os.path.join(JSON_DIR, "schema")               # docs/json/schema/

try:
    from jsonschema import Draft202012Validator
    from referencing import Registry, Resource
    from referencing.jsonschema import DRAFT202012
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

try:
    from status_loader import iter_status_defs
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from status_loader import iter_status_defs


def load(name):
    return json.load(io.open(os.path.join(SCHEMA_DIR, name), encoding="utf-8"))


def build_registry(*schemas):
    """把各 schema 按 $id 注册进同一 Registry，支撑跨文件 $ref
    （statuses.schema.json 的 statusDefs 条目引用 skills.schema.json#/$defs/statusDef，
    statusDef 的结构唯一源仍在 skills.schema.json，不存副本）。"""
    reg = Registry()
    for s in schemas:
        res = Resource.from_contents(s, default_specification=DRAFT202012)
        reg = reg.with_resource(s["$id"], res)
    return reg


def schema_check(schema, instance, label, errors, max_errors, registry=None):
    """结构校验；按 JSON 指针排序输出，便于定位。"""
    if not HAS_JSONSCHEMA:
        errors.append("%s: 跳过（未安装 jsonschema，pip install jsonschema）" % label)
        return
    v = Draft202012Validator(schema, registry=registry) if registry else Draft202012Validator(schema)
    n = 0
    for err in sorted(v.iter_errors(instance), key=lambda e: list(e.absolute_path)):
        n += 1
        if n > max_errors:
            errors.append("%s: ... 另有错误未列出（超过 %d 条上限）" % (label, max_errors))
            break
        loc = "/" + "/".join(str(p) for p in err.absolute_path) if err.absolute_path else "(root)"
        errors.append("%s %s: %s" % (label, loc, err.message[:220]))


def cross_check(docs, manifest, errors, warns):
    """schema 表达不了的跨字段约束。"""
    # 1) 卡片 id 前缀规则：^(f|h)NN_<slug>（NN=派系号两位数字）
    #    f 前缀必须 scope=faction，h 前缀必须 scope=hero，且 NN 与所在派系文件号一致。
    id_re = re.compile(r"^([fh])(\d\d)_")
    for name, d in docs.items():
        fid = d.get("factionId")
        num = fid.split("_", 1)[1] if isinstance(fid, str) and "_" in fid else None
        for c in d.get("cards", []):
            cid = c.get("id", "")
            m = id_re.match(cid)
            if not m:
                errors.append("%s %s: id 前缀应为 f<NN>_<slug>（派系公共）或 h<NN>_<slug>（英雄独自）"
                              % (name, cid))
                continue
            exp_scope = "faction" if m.group(1) == "f" else "hero"
            if c.get("scope") is not None and c.get("scope") != exp_scope:
                errors.append("%s %s: id 前缀 %s_ 须 scope=%s（当前 %s）"
                              % (name, cid, m.group(1), exp_scope, c.get("scope")))
            if num is not None and m.group(2) != num:
                errors.append("%s %s: id 派系号 %s 与所在文件 factionId %s 不一致"
                              % (name, cid, m.group(2), fid))

    # 2) 状态 id 跨派系复用：同名必须同定义（单点定义，INV-C2）。
    #    同名但定义不一致一律告警，须拆分为独立 id，不设任何豁免白名单。
    seen = {}
    reused = set()
    # 收集所有 statusDef：派系顶层 statusDefs[]（v2 权威位）+ 卡内联（兼容）+ *.statuses.json（common）
    ext_defs = []  # (pid, where, sd)
    for name, d in docs.items():
        pid = d.get("factionId")
        for sd in d.get("statusDefs") or []:
            ext_defs.append((pid, "%s#statusDefs" % name, sd))
        for c in d.get("cards", []):
            for sd in c.get("statusDefs") or []:
                ext_defs.append((pid, "%s/%s" % (name, c.get("id")), sd))
    for spid, slabel, sd in iter_status_defs():
        ext_defs.append((spid, slabel, sd))
    for pid, where, sd in ext_defs:
        sid = sd.get("id")
        sig = json.dumps({k: sd.get(k) for k in
                          ("name", "category", "dispelable", "duration", "modifiers",
                           "maxStacks", "stackPolicy", "charges", "triggers", "effects")},
                         ensure_ascii=False, sort_keys=True)
        if sid in seen:
            old_sig, old_where, old_pid = seen[sid]
            if old_sig != sig:
                warns.append("%s %s: statusDef '%s' 与 %s 同名但定义不一致（须拆分为独立 id，禁止同名异义）" % (where, sid, sid, old_where))
            else:
                reused.add(sid)
        else:
            seen[sid] = (sig, where, pid)
    if reused:
        print("  · 跨派系复用状态 %d 个（同名同定义，视为共享状态，非错误）" % len(reused))

    if not manifest:
        return

    # 3) manifest ↔ 文件对齐
    m_by_id = {p["id"]: p for p in manifest.get("factions", [])}
    for pid, d in docs.items():
        if pid not in m_by_id:
            errors.append("manifest: 缺少派系条目 %s" % pid)
            continue
        p = m_by_id[pid]
        n = len(d.get("cards", []))
        if p.get("cardCount") != n:
            errors.append("manifest %s: cardCount %s != 实际 %d" % (pid, p.get("cardCount"), n))
        if p.get("file") != "%s.skills.json" % pid:
            errors.append("manifest %s: file 字段 %r 与 factionId 不匹配" % (pid, p.get("file")))

    for pid in m_by_id:
        if pid not in docs:
            errors.append("manifest: 派系 %s 在 manifest 中登记但缺文件" % pid)

    # 4) 稀有度映射（schema 无法表达 sequence → rarity 派生关系；manifest.rarityMap 是唯一机器可读基准）
    rev = {}
    for rar, seqs in (manifest.get("rarityMap") or {}).items():
        for s in seqs:
            rev[s] = rar
    for name, d in docs.items():
        for c in d.get("cards", []):
            exp = rev.get(c.get("sequence"))
            if exp and c.get("rarity") != exp:
                errors.append("%s %s: sequence %s 应为 %s，实为 %s"
                              % (name, c.get("id"), c.get("sequence"), exp, c.get("rarity")))

    # 5) *.statuses.json ↔ manifest：孤儿状态文件（前缀不是已登记派系、也不是 common）即错误。
    #    v2 派系私有状态已并入派系文件顶层 statusDefs[]，*.statuses.json 只剩 common。
    known = set(m_by_id) | {"common"}
    for f in sorted(glob.glob(os.path.join(JSON_DIR, "*.statuses.json"))):
        pid = os.path.basename(f)[: -len(".statuses.json")]
        if pid not in known:
            errors.append("manifest: 状态文件 %s 无对应派系（孤儿文件：派系未登记或已删未清理）"
                          % os.path.basename(f))


def main():
    max_errors = 15
    if "--max" in sys.argv:
        max_errors = int(sys.argv[sys.argv.index("--max") + 1])

    errors = []
    warns = []
    skills_schema = load("skills.schema.json")
    manifest_schema = load("manifest.schema.json")
    statuses_schema = load("statuses.schema.json")
    registry = build_registry(skills_schema, manifest_schema, statuses_schema) if HAS_JSONSCHEMA else None

    files = sorted(glob.glob(os.path.join(JSON_DIR, "*.skills.json")))
    docs = {}
    for f in files:
        d = json.load(io.open(f, encoding="utf-8"))
        docs[d.get("factionId", os.path.basename(f))] = d

    manifest = None
    mpath = os.path.join(JSON_DIR, "manifest.json")
    if os.path.exists(mpath):
        manifest = json.load(io.open(mpath, encoding="utf-8"))
        schema_check(manifest_schema, manifest, "manifest.json", errors, max_errors)

    for name in sorted(docs):
        schema_check(skills_schema, docs[name], name, errors, max_errors)

    # 校验 *.statuses.json 整文件（common）：文件级结构走 statuses.schema.json，
    # statusDefs 条目经跨文件 $ref 落到 skills.schema.json 的 $defs/statusDef（唯一源）
    for f in sorted(glob.glob(os.path.join(JSON_DIR, "*.statuses.json"))):
        try:
            d = json.load(io.open(f, encoding="utf-8"))
        except Exception as e:
            errors.append("%s: 解析失败 %s" % (os.path.basename(f), e))
            continue
        schema_check(statuses_schema, d, os.path.basename(f), errors, max_errors, registry)

    cross_check(docs, manifest, errors, warns)

    print("-" * 60)
    print("files:", len(docs), "| errors:", len(errors), "| warns:", len(warns))
    if errors:
        print("-" * 60)
        for e in errors:
            print("  E:", e)
    if warns:
        print("-" * 60)
        for w in warns:
            print("  W:", w)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
