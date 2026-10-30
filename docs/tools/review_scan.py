# -*- coding: utf-8 -*-
"""机制层回归机筛（warn 级）：把 DESIGN_CHECKLIST 中机器可验的条目落成脚本。

与 validate.py 分工：validate 管枚举/引用/结构硬错误；本脚本管机制层启发式检查
（产读闭环、签名在场、叠层读档、越档粗检等），全部 warn 不阻断。
复用 status_loader 的加载 / $extends 物化 / 解析链。

用法：python review_scan.py [--hero NN | --family NN | --all]
输出：[R#] 位置: 命中 逐条 + 每组汇总；exit 恒 0（warn 工具，收敛由回归报告跟踪）。
"""
import io
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import status_loader as sl

JSON_DIR = sl.JSON_DIR

# ---- 家族主签名键表（源：docs/meta/家族身份卡.md §一；只登记在册 9 族）----
SIGNATURE = {
    "01": ['"element": "holy"', "guardTarget"],
    "04": ["translocate"],
    "06": ["write_rule_slot", "seal_effect"],
    "08": ["puppet_string"],
    "11": ["valueFrom", "cast_time_set"],
    "13": ["restore_snapshot", "advance_clock", '"dim": "fate_value"'],
    "14": ["moon_phase", '"unitType": "BEAST"'],
    "16": ['"element": "ice"', '"element": "lightning"'],
    "21": ['"element": "dark"', "companionBuff"],
}

WRITE_TYPES = {"mount_status", "modify_resource", "heal", "modify_stat",
               "grant_immunity", "modify_weapon", "apply"}
READ_COND = {"has_status", "has_equipped", "resource_compare", "stat_compare",
             "tag_chain", "has_status_tag", "caster_has_summon", "target_has_tag"}
READ_TYPES = {"modify_status", "dispel", "modify_skill"}
DAMAGE_TYPES = {"damage"}


def walk(node):
    """递归遍历 AST（effects/steps/then/else/condition 树），yield 所有 dict。"""
    if isinstance(node, dict):
        yield node
        for v in node.values():
            for x in walk(v):
                yield x
    elif isinstance(node, list):
        for it in node:
            for x in walk(it):
                yield x


def walk_effects(effects):
    return list(walk(effects or []))


def cond_kinds(nodes):
    return {n.get("kind") for n in nodes if isinstance(n.get("kind"), str)}


def group_files(hero_num):
    """hero 组 = hero + family + faction + global 四文件。"""
    docs = sl.load_docs()
    hf = "hero_%s.skills.json" % hero_num
    chain = sl.chain_files(hf)
    return [f for f in chain if f in docs]


def group_cards(files):
    docs = sl.load_docs()
    cards = []
    for f in files:
        lvl = sl.file_level(docs[f])
        if lvl in ("hero", "family"):
            for c in docs[f].get("cards") or []:
                cards.append((f, c))
    return cards


def group_defs(files):
    docs = sl.load_docs()
    out = {"statusDefs": [], "unitDefs": [], "zoneDefs": [], "domainDefs": []}
    for f in files:
        for pool in out:
            for iid, item in sl.materialize(f, pool).items():
                out[pool].append((f, iid, item))
    return out


def scan_group(num, files):
    warns = []
    docs = sl.load_docs()
    cards = group_cards(files)
    defs = group_defs(files)

    # hero 组号 → 家族号（签名表按家族登记）
    fam_num = num
    for f in files:
        if sl.file_level(docs[f]) == "hero":
            fam = docs[f].get("family") or ""
            if fam.startswith("family_"):
                fam_num = fam[len("family_"):]

    # 组内跨卡「消耗/读层」面：modify_status / consume 挂载 / has_status 比层数
    # 统计面 = 组内全部卡 + 全部 def（蓝本触发器也会消耗状态）
    consumed = set()
    all_nodes = []
    for _, c in cards:
        all_nodes += walk_effects(c.get("effects"))
        for t in (c.get("triggers") or []):
            all_nodes += walk_effects(t.get("effects"))
    for pool in defs.values():
        for _, iid, d in pool:
            all_nodes += walk_effects(d.get("effects"))
            all_nodes += walk_effects(d.get("triggers"))
            for k2 in ("stackThreshold", "thresholdTrigger"):
                all_nodes += walk_effects((d.get(k2) or {}).get("effects"))
    def _feed(nodes, sink):
        for n in nodes:
            if n.get("type") == "modify_status" and n.get("statusId"):
                sink.add(n["statusId"])
            if n.get("type") == "mount_status" and n.get("stackMode") == "consume" and n.get("statusId"):
                sink.add(n["statusId"])
            if n.get("kind") == "has_status" and (n.get("stacksAtLeast") is not None or n.get("cmp")):
                sink.add(n.get("id") or n.get("statusId"))
    _feed(all_nodes, consumed)
    # global 定义的消费面按全库计算（跨派系共享）
    global_consumed = set()
    for f2, d2 in docs.items():
        nodes = []
        for c2 in d2.get("cards") or []:
            nodes += walk_effects(c2.get("effects"))
            for t2 in (c2.get("triggers") or []):
                nodes += walk_effects(t2.get("effects"))
        for pool in sl.POOLS[1:]:
            for it in (d2.get(pool) or []):
                if isinstance(it, dict):
                    nodes += walk_effects(it.get("effects"))
                    nodes += walk_effects(it.get("triggers"))
                    for k2 in ("stackThreshold", "thresholdTrigger"):
                        nodes += walk_effects((it.get(k2) or {}).get("effects"))
        _feed(nodes, global_consumed)

    # R1 轴产读闭环
    by_axis = {}
    for f, c in cards:
        if not c.get("axis"):
            continue
        nodes = walk_effects(c.get("effects")) + walk_effects(
            [t.get("effects") for t in (c.get("triggers") or [])])
        kinds = {n.get("type") for n in nodes if isinstance(n.get("type"), str)} | cond_kinds(nodes)
        has_write = bool(kinds & WRITE_TYPES)
        has_read = bool((kinds & READ_TYPES) or (cond_kinds(nodes) & READ_COND))
        st = by_axis.setdefault(c["axis"], {"w": 0, "r": 0})
        st["w"] += 1 if has_write else 0
        st["r"] += 1 if has_read else 0
    for axis, st in sorted(by_axis.items()):
        if st["w"] == 0:
            warns.append(("R1", "axis %s: 轴无产层卡" % axis))
        if st["r"] == 0:
            warns.append(("R1", "axis %s: 轴无读层卡" % axis))

    # R2 家族签名在场
    sig = SIGNATURE.get(fam_num)
    if sig:
        blob = json.dumps([c for _, c in cards], ensure_ascii=False)
        blob += json.dumps([d for _, _, d in defs["statusDefs"]], ensure_ascii=False)
        if not any(k in blob for k in sig):
            warns.append(("R2", "family_%s 主签名键缺席: %s" % (num, "/".join(sig))))

    # R3 叠层状态须有读档
    for f, iid, sd in defs["statusDefs"]:
        ms = sd.get("maxStacks")
        if not isinstance(ms, int) or ms <= 1:
            continue
        mods = sd.get("modifiers") or {}
        stack_dot = isinstance(mods, dict) and bool({"dotOnTick", "healOnTick"} & set(mods.keys()))
        has_out = any(sd.get(k) for k in
                      ("stackThreshold", "statPerStack", "ramp", "phases", "formGroup",
                       "charges", "summonMapping")) or stack_dot
        scope_consumed = global_consumed if sl.file_level(docs[f]) == "global" else consumed
        if not has_out and iid not in scope_consumed:
            warns.append(("R3", "%s sd %s: 叠层无读档出口" % (f.split('.')[0], iid)))

    # R4 duration%5==0 且挂回合触发点（疑折回合遗物）
    for f, iid, sd in defs["statusDefs"]:
        d = sd.get("duration")
        if isinstance(d, int) and d > 0 and d % 5 == 0:
            evs = {t.get("event") for t in (sd.get("triggers") or [])}
            if evs & {"on_turn_start", "on_turn_end"}:
                warns.append(("R4", "%s sd %s: duration %dtick 挂回合触发点" % (f.split('.')[0], iid, d)))

    # R5 并列 chance if（应互斥嵌套链）
    for f, c in cards:
        def count_chance_if(effects):
            if not isinstance(effects, list):
                return 0
            n = 0
            for e in effects:
                if isinstance(e, dict) and e.get("op") == "if":
                    ks = cond_kinds(walk(e.get("condition")))
                    if "chance" in ks:
                        n += 1
            return n
        total = count_chance_if(c.get("effects"))
        for t in (c.get("triggers") or []):
            total += count_chance_if(t.get("effects"))
        if total >= 2:
            warns.append(("R5", "%s: 并列概率 if %d 处（应互斥嵌套链）" % (c.get("id"), total)))

    # R6 乘区纪律
    for f, iid, sd in defs["statusDefs"]:
        mods = sd.get("modifiers") or {}
        mkeys = set(mods.keys()) if isinstance(mods, dict) else set()
        if (mkeys & {"damage_mul", "damage_taken_mul"}) and sd.get("duration") is None \
                and not sd.get("charges"):
            warns.append(("R6", "%s sd %s: 常驻伤害乘区" % (f.split('.')[0], iid)))
    for f, c in cards:
        for n in walk_effects(c.get("effects")):
            if n.get("type") == "modify_damage" and n.get("duration") is None:
                warns.append(("R6", "%s: modify_damage 无 duration" % c.get("id")))
                break

    # R7 召唤载荷
    udefs = {iid: d for _, iid, d in defs["unitDefs"]}
    for f, c in cards:
        if c.get("kind") != "summon":
            continue
        uid = (c.get("summon") or {}).get("unitId")
        general = [n for n in walk_effects(c.get("effects"))
                   if n.get("type") in {"damage", "heal", "modify_stat", "mount_status", "dispel"}]
        if len(general) > 1:
            warns.append(("R7", "%s: 召唤卡通用原语段 %d 段，主载荷应入 unitDef" % (c.get("id"), len(general))))
        ud = udefs.get(uid) or {}
        if not uid:
            continue
        has_hp = bool(ud.get("base") or ud.get("hpRatio"))
        has_atk = bool(ud.get("base") or ud.get("atkRatio"))
        if not (has_hp and has_atk):
            warns.append(("R7", "%s: unitDef %s 基线不全" % (c.get("id"), uid)))

    # R8 on_battle_start 读战况（近似）
    for f, c in cards:
        hooks = set(c.get("hook") or []) if isinstance(c.get("hook"), list) else ({c.get("hook")} if c.get("hook") else set())
        if "on_battle_start" not in hooks:
            continue
        ks = cond_kinds(walk_effects(c.get("effects")))
        if "has_status" in ks:
            warns.append(("R8", "%s: on_battle_start 读 has_status（近似，人审定）" % c.get("id")))

    # R9 被动集中度（按组）与同效果复制
    ev_cards = {}
    mount_cards = {}
    for f, c in cards:
        if c.get("kind") != "passive":
            continue
        evs = set(c.get("hook") or []) if isinstance(c.get("hook"), list) else ({c.get("hook")} if c.get("hook") else set())
        for t in (c.get("triggers") or []):
            evs.add(t.get("event"))
        for ev in evs:
            ev_cards.setdefault(ev, set()).add(c.get("id"))
        for n in walk_effects(c.get("effects")):
            if n.get("type") == "mount_status" and n.get("statusId"):
                mount_cards.setdefault(n["statusId"], set()).add(c.get("id"))
    for ev, ids in ev_cards.items():
        if len(ids) >= 8:
            warns.append(("R9", "被动触发点 %s 集中 %d 张" % (ev, len(ids))))
    for sid, ids in mount_cards.items():
        if len(ids) >= 4:
            warns.append(("R9", "同状态 %s 被 %d 张被动挂载" % (sid, len(ids))))

    # R10 数值越档粗检
    for f, c in cards:
        if c.get("kind") != "active":
            continue
        energy = (c.get("cost") or {}).get("energy") or 0
        if not isinstance(energy, (int, float)) or energy <= 0:
            continue
        dmg = sum(n.get("value") for n in walk_effects(c.get("effects"))
                  if n.get("type") == "damage" and isinstance(n.get("value"), (int, float)))
        if dmg <= 0:
            continue
        req = ((c.get("target") or {}).get("request") or {})
        area = req.get("mode") == "area" or req.get("pickCount") == "all"
        limit = 1.2 * energy * 2 + 3
        if area:
            limit *= 2.5
        if dmg > limit:
            warns.append(("R10", "%s: 直伤合计 %s 超档（预算 %.1f%s）" % (c.get("id"), dmg, limit, "，群体" if area else "")))
        for n in walk_effects(c.get("effects")):
            if n.get("type") == "modify_stat" and n.get("stat") != "gauge.rate" \
                    and isinstance(n.get("value"), (int, float)) and abs(n["value"]) >= 3:
                warns.append(("R10", "%s: modify_stat %+d 跳档" % (c.get("id"), n["value"])))
                break

    # R11 被动消费共享量表
    for f, c in cards:
        if c.get("kind") != "passive":
            continue
        for n in walk_effects(c.get("effects")):
            if n.get("type") == "modify_resource" and n.get("resource") in ("lost", "order", "secrecy", "fate_value"):
                warns.append(("R11", "%s: 被动写战场量表 %s（须单独评审）" % (c.get("id"), n.get("resource"))))
                break

    return warns


def main():
    args = sys.argv[1:]
    docs = sl.load_docs()
    heroes = sorted(n for n in docs if n.startswith("hero_") and n.endswith(".skills.json"))
    groups = []
    if "--all" in args:
        groups = [(h[len("hero_"):len("hero_") + 2], h) for h in heroes]
    elif "--hero" in args:
        n = args[args.index("--hero") + 1]
        groups = [(n, "hero_%s.skills.json" % n)]
    elif "--family" in args:
        n = args[args.index("--family") + 1]
        groups = [(n, "family_%s.skills.json" % n)]
    else:
        print("用法: review_scan.py [--hero NN | --family NN | --all]")
        return 0
    total = 0
    for num, hf in groups:
        files = group_files(num)
        warns = scan_group(num, files)
        total += len(warns)
        print("== %s ==" % hf.replace(".skills.json", ""))
        for tag, msg in warns:
            print("  [%s] %s" % (tag, msg))
        cnt = {}
        for tag, _ in warns:
            cnt[tag] = cnt.get(tag, 0) + 1
        summary = " ".join("%s×%d" % (k, cnt[k]) for k in sorted(cnt)) or "0 warn"
        print("  -> %d warns (%s)" % (len(warns), summary))
    print("-" * 50)
    print("TOTAL warns:", total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
