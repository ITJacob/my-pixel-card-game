# -*- coding: utf-8 -*-
"""按 JSON Schema 校验技能池全库 + 跨字段一致性检查。

用法:
    python docs/tools/validate_schema.py            # 校验 manifest + global + 9 派系 + 9 英雄文件
    python docs/tools/validate_schema.py --max 20   # 每文件最多打印 20 条错误

依赖: jsonschema（可选）
    pip install jsonschema
未安装时只执行不依赖它的跨字段检查（第二部分）。

与 docs/tools/validate.py 的分工:
    validate.py        —— 语义/枚举/引用完整性校验（原语与参数取值域、状态 id 存在性、
                          rarity↔sequence 映射、界域租金等）
    validate_schema.py —— 结构校验（字段是否存在、类型是否正确、有无未知字段）
                          + 跨字段一致性（id 前缀↔文件层级/序号、manifest 对齐、
                          $extends 解析合规与物化后结构复核）
两者都应为 0 错误才视为合规。

四层作用域：global.skills.json（全域）/ faction_NN.skills.json（派系）/ family_NN.skills.json
（家族）/ hero_NN.skills.json（英雄）；根 oneOf 按 level 分派。hero/family/global 文件按文件名约定
发现，不在 manifest 登记（manifest 仍只登记 faction）。
"""
import io
import os
import re
import sys
import glob
import json

HERE = os.path.dirname(os.path.abspath(__file__))          # docs/tools/
JSON_DIR = os.path.join(os.path.dirname(HERE), "json")      # docs/json/
SCHEMA_DIR = os.path.join(JSON_DIR, "schema")               # docs/json/schema/

try:
    from jsonschema import Draft202012Validator
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

try:
    import status_loader
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import status_loader


def load(name):
    return json.load(io.open(os.path.join(SCHEMA_DIR, name), encoding="utf-8"))


def schema_check(schema, instance, label, errors, max_errors):
    """结构校验；按 JSON 指针排序输出，便于定位。"""
    if not HAS_JSONSCHEMA:
        errors.append("%s: 跳过（未安装 jsonschema，pip install jsonschema）" % label)
        return
    v = Draft202012Validator(schema)
    n = 0
    for err in sorted(v.iter_errors(instance), key=lambda e: list(e.absolute_path)):
        n += 1
        if n > max_errors:
            errors.append("%s: ... 另有错误未列出（超过 %d 条上限）" % (label, max_errors))
            break
        loc = "/" + "/".join(str(p) for p in err.absolute_path) if err.absolute_path else "(root)"
        errors.append("%s %s: %s" % (label, loc, err.message[:220]))


def check_extends(docs, skills_schema, errors):
    """$extends 三层继承校验：

    1) 父定义必须存在且解析序合规（本文件 → 同派系 faction → global；禁同层跨文件）；
    2) 物化后条目重新过对应池条目的结构校验（浅合并/tags 并集不得产生 schema 违规）。
       条目内 #/$defs 引用需要完整 schema 上下文，故把物化条目包进 dummy 文件根再整体验证。"""
    defs = skills_schema.get("$defs", {})
    ext_errors = []
    wrappers = {  # 各池条目 → 最小合法 hero 文件根包裹
        "cards": lambda it: {"level": "hero", "heroId": "hero_99", "heroName": "物化复核",
                             "faction": "faction_01", "playstyle": "物化复核",
                             "cards": [it], "statusDefs": [], "unitDefs": [],
                             "zoneDefs": [], "domainDefs": []},
    }
    for pool in status_loader.POOLS:
        if pool != "cards":
            def _mk(it, _pool=pool):
                w = wrappers["cards"](None)
                w["cards"] = []
                w[_pool] = [it]
                return w
            wrappers[pool] = _mk

    for fname in sorted(docs):
        doc = docs[fname]
        for pool in status_loader.POOLS:
            # 先跑一遍解析（收集父缺失/同层/循环），拿物化结果
            merged = status_loader.materialize(fname, pool, ext_errors)
            if not HAS_JSONSCHEMA:
                continue
            raw_by_id = {it.get("id"): it for it in doc.get(pool) or []
                         if isinstance(it, dict)}
            for iid, item in merged.items():
                raw = raw_by_id.get(iid)
                if not raw or "$extends" not in raw:
                    continue
                v = Draft202012Validator(skills_schema)
                hits = []
                for err in v.iter_errors(wrappers[pool](item)):
                    # 根 oneOf 会同时带上未命中分支的噪音，下钻到具体违规叶子
                    leaves = _leaf_errors(err)
                    hits.extend(e for e in leaves
                                if list(e.absolute_path)[:1] == [pool])
                    if not leaves and list(err.absolute_path)[:1] == [pool]:
                        hits.append(err)
                for err in hits:
                    loc = "/" + "/".join(str(p) for p in err.absolute_path) or "(root)"
                    ext_errors.append("%s %s %s: 物化后违反结构 %s: %s"
                                      % (fname, pool, iid, loc, err.message[:200]))
    errors.extend(ext_errors)


def _leaf_errors(err):
    """jsonschema oneOf/anyOf 错误递归取叶子（带具体路径的底层违规）。"""
    if err.context:
        out = []
        for c in err.context:
            out.extend(_leaf_errors(c))
        return out
    return [err]


def cross_check(docs, manifest, errors, warns):
    """schema 表达不了的跨字段约束。"""
    # 1) 卡 id 前缀规则（按文件层级）：
    #    family 文件 → ^j<NN>_<slug>，NN=文件 faction 号（同派系家族组共享 j 号，j 释义为家族）；
    #    hero 文件 → ^h<NN>_<slug>，NN=heroId 序号；
    #    faction 文件 cards 恒为空不校验前缀；global 文件 → 无前缀约束。
    #    f<NN>_ 预留给 faction 级卡：出现于其他任何层级即报错（faction 文件 cards 为空，暂不产生合法用例）。
    #    文件名 ↔ 内字段一致性（family_NN ↔ familyId/faction、hero_NN ↔ heroId/faction/family）同此检查。
    j_re = re.compile(r"^j(\d\d)_[a-z0-9_]+$")
    h_re = re.compile(r"^h(\d\d)_[a-z0-9_]+$")
    reserved_f_re = re.compile(r"^f\d\d_[a-z0-9_]+$")
    fac_ids = {d.get("factionId") for d in docs.values() if d.get("level") == "faction"}
    fam_by_id = {d.get("familyId"): d for d in docs.values() if d.get("level") == "family"}
    for name, d in docs.items():
        lvl = d.get("level")
        num = None
        if lvl == "family":
            # 文件名 ↔ familyId 配对 + faction 指向存在性
            nnum = name[len("family_"):len("family_") + 2]
            if d.get("familyId") != "family_%s" % nnum:
                errors.append("%s: familyId %s 与文件名序号 %s 不一致"
                              % (name, d.get("familyId"), nnum))
            if d.get("faction") not in fac_ids:
                errors.append("%s: faction 字段 %s 无对应 faction 文件" % (name, d.get("faction")))
            num = (d.get("faction") or "").split("_", 1)[1] if "_" in (d.get("faction") or "") else None
            id_pat = j_re
        elif lvl == "hero":
            num = (d.get("heroId") or "").split("_", 1)[1] if "_" in (d.get("heroId") or "") else None
            id_pat = h_re
            # 文件名 ↔ 内字段配对：hero_01.skills.json 的 heroId 必须 hero_01、faction 必须 faction_01
            fnum = name[len("hero_"):len("hero_") + 2]
            if d.get("heroId") != "hero_%s" % fnum:
                errors.append("%s: heroId %s 与文件名序号 %s 不一致"
                              % (name, d.get("heroId"), fnum))
            if d.get("faction") != "faction_%s" % fnum:
                errors.append("%s: faction 字段 %s 与文件名序号 %s 不一致（须 faction_%s）"
                              % (name, d.get("faction"), fnum, fnum))
            # family 字段：必须指向存在的 family 文件，且该 family 与本英雄同派系
            fam = fam_by_id.get(d.get("family"))
            if fam is None:
                errors.append("%s: family 字段 %s 无对应 family 文件" % (name, d.get("family")))
            elif fam.get("faction") != d.get("faction"):
                errors.append("%s: family %s 属于 %s，与 hero faction %s 不一致"
                              % (name, d.get("family"), fam.get("faction"), d.get("faction")))
        else:
            id_pat = None
        for c in d.get("cards", []):
            cid = c.get("id", "")
            # f<NN>_ 预留给 faction 级卡：出现在 faction 以外层级即报错
            if lvl != "faction" and reserved_f_re.match(cid):
                errors.append("%s %s: f<NN>_ 前缀预留给 faction 级卡，%s 文件不得使用" % (name, cid, lvl))
            if id_pat is None:
                continue
            m = id_pat.match(cid)
            if not m:
                errors.append("%s %s: id 前缀应为 %s（当前 %s）"
                              % (name, cid,
                                 "j<NN>_<slug>" if lvl == "family" else "h<NN>_<slug>", cid))
                continue
            if num is not None and m.group(1) != num:
                errors.append("%s %s: id 序号 %s 与文件 %s 序号 %s 不一致"
                              % (name, cid, m.group(1), lvl, num))

    # 2) 状态 id 跨文件复用：同名必须同定义（单点定义，INV-C2）。
    #    同名但定义不一致一律告警，须拆分为独立 id，不设任何豁免白名单。
    seen = {}
    reused = set()
    # 收集所有 statusDef：三层文件顶层 statusDefs[]（物化后）+ 卡内联（兼容）
    ext_defs = []  # (pid, where, sd)
    for name, d in docs.items():
        pid = d.get("factionId") or d.get("heroId") or d.get("level") or name
        for iid, sd in status_loader.materialize(name, "statusDefs").items():
            ext_defs.append((pid, "%s#statusDefs" % name, sd))
        for c in d.get("cards", []):
            for sd in c.get("statusDefs") or []:
                ext_defs.append((pid, "%s/%s" % (name, c.get("id")), sd))
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
        print("  · 跨文件复用状态 %d 个（同名同定义，视为共享状态，非错误）" % len(reused))

    if not manifest:
        return

    # 3) manifest ↔ faction 文件对齐（global/family/hero 按文件名约定发现，不在 manifest 登记）
    #    cardCount 口径：派系卡数 = 该派系在册 family 文件 cards 之和（faction 文件 cards 恒空）
    m_by_id = {p["id"]: p for p in manifest.get("factions", [])}
    fac_docs = {d.get("factionId"): d for d in docs.values() if d.get("level") == "faction"}
    fam_cards = {}
    for d in docs.values():
        if d.get("level") == "family":
            fam_cards[d.get("faction")] = fam_cards.get(d.get("faction"), 0) + len(d.get("cards") or [])
    for pid, d in fac_docs.items():
        if pid not in m_by_id:
            errors.append("manifest: 缺少派系条目 %s" % pid)
            continue
        p = m_by_id[pid]
        n = fam_cards.get(pid, 0)
        if p.get("cardCount") != n:
            errors.append("manifest %s: cardCount %s != 在册家族卡数之和 %d" % (pid, p.get("cardCount"), n))
        if p.get("file") != "%s.skills.json" % pid:
            errors.append("manifest %s: file 字段 %r 与 factionId 不匹配" % (pid, p.get("file")))

    for pid in m_by_id:
        if pid not in fac_docs:
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

    # 5) hero 文件 ↔ faction 文件存在性配对：hero_NN 必须有对应 faction_NN（NN=01..09）
    hero_nums = sorted(name[len("hero_"):len("hero_") + 2]
                       for name, d in docs.items() if d.get("level") == "hero")
    fac_nums = sorted((d.get("factionId") or "").split("_", 1)[1]
                      for d in docs.values() if d.get("level") == "faction")
    for n in hero_nums:
        if n not in fac_nums:
            errors.append("hero_%s: 缺对应派系文件 faction_%s.skills.json" % (n, n))


def main():
    max_errors = 15
    if "--max" in sys.argv:
        max_errors = int(sys.argv[sys.argv.index("--max") + 1])

    errors = []
    warns = []
    skills_schema = load("skills.schema.json")
    manifest_schema = load("manifest.schema.json")

    docs = status_loader.load_docs()

    manifest = None
    mpath = os.path.join(JSON_DIR, "manifest.json")
    if os.path.exists(mpath):
        manifest = json.load(io.open(mpath, encoding="utf-8"))
        schema_check(manifest_schema, manifest, "manifest.json", errors, max_errors)

    for name in sorted(docs):
        schema_check(skills_schema, docs[name], name, errors, max_errors)

    # $extends：解析序/同层禁令/循环 + 物化后结构复核
    check_extends(docs, skills_schema, errors)

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
