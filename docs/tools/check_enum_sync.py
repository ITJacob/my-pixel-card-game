# -*- coding: utf-8 -*-
"""枚举一致性对账：ddd 参数篇（文本侧）↔ schema $defs / validate.py（机器侧）。

机器侧单一正源 = docs/json/schema/skills.schema.json（validate.py 运行时加载，不再自抄）。
本脚本盯的是文本侧与机器侧之间的漂移（atk_asc 类事故：ddd 已登记、schema/校验器漏同步）。

v2 对账组（按 ddd/ 实际篇幅裁剪）：
  - triggerEvent：ddd/params/执行参数.md 触发点表 ↔ validate.EVENTS / schema triggerEvent
  - primitive  ：ddd/params/效果参数.md 原语表 ↔ schema effect.oneOf（validate.PRIMS）
  - cardKind   ：ddd/params/编队参数.md 卡型表 ↔ schema card.kind
  - equipSlot  ：ddd/params/编队参数.md 装备槽表 ↔ schema equipmentSpec.slot / condition.slot

用法: python docs/tools/check_enum_sync.py   （只读；存在未登记漂移时 exit 1）
"""
import io, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))          # docs/tools/
DOCS = os.path.dirname(HERE)                                # docs/
sys.path.insert(0, HERE)
import validate  # noqa: E402  复用其 schema 加载结果与 EVENTS

# 有意分歧登记：文本侧与机器侧允许存在的差集，须注明理由
KNOWN = {}

def read(rel):
    return io.open(os.path.join(DOCS, rel), encoding="utf-8").read()

def section(txt, anchor, stop_re=r"\n##\s"):
    """取 anchor 所在行之后到下一个同级标题之间的文本。"""
    i = txt.index(anchor)
    m = re.search(stop_re, txt[i + len(anchor):])
    return txt[i:i + len(anchor) + (m.start() if m else len(txt))]

def table_first_col(txt, anchor):
    """anchor 之后第一个 Markdown 表格的第一列字面量集合。
    跳过头行与 |---| 分隔行；单元格支持 `code` 包裹与「a / b」合并行（拆分取全部）。"""
    i = txt.index(anchor)
    out = set()
    in_table = False
    for ln in txt[i:].splitlines()[1:]:
        s = ln.strip()
        if s.startswith("|") and s.endswith("|"):
            in_table = True
            cells = [c.strip() for c in s.strip("|").split("|")]
            first = cells[0]
            if not first or set(first) <= set("-: "):   # 空单元格或分隔行
                continue
            if first in ("触发点", "原语", "kind", "槽", "字段"):   # 表头
                continue
            for tok in first.split("/"):
                tok = tok.strip().strip("`")
                if tok:
                    out.add(tok)
        elif in_table and s:
            break
    return out

def ddd_triggers():
    return table_first_col(read("ddd/params/执行参数.md"), "## 触发点")

def ddd_primitives():
    return table_first_col(read("ddd/params/效果参数.md"), "| 原语 |")

def ddd_card_kinds():
    return table_first_col(read("ddd/params/编队参数.md"), "## 卡型")

def ddd_equip_slots():
    return table_first_col(read("ddd/params/编队参数.md"), "## 装备槽")

def compare(name, text_side, machine_side, text_label, machine_label, errors):
    only_text = sorted(text_side - machine_side)
    only_machine = sorted(machine_side - text_side)
    unexplained = [v for v in only_text + only_machine if (name, v) not in KNOWN]
    if unexplained:
        errors.append(name)
        print("DRIFT %s:" % name)
        for v in only_text:
            tag = "（已登记分歧）" if (name, v) in KNOWN else ""
            print("  仅 %s: %s %s" % (text_label, v, tag))
        for v in only_machine:
            tag = "（已登记分歧）" if (name, v) in KNOWN else ""
            print("  仅 %s: %s %s" % (machine_label, v, tag))
    else:
        known = [v for v in only_text + only_machine]
        suffix = "（登记分歧 %d 项）" % len(known) if known else ""
        print("OK    %s (%d)%s" % (name, len(machine_side & text_side), suffix))

def main():
    errors = []

    compare("triggerEvent", ddd_triggers(), validate.EVENTS, "ddd 执行参数 §触发点", "validate.EVENTS", errors)
    compare("triggerEvent", ddd_triggers(), set(validate.DEFS["triggerEvent"]["enum"]),
            "ddd 执行参数 §触发点", "schema", errors)
    compare("primitive", ddd_primitives(), validate.PRIMS, "ddd 效果参数 原语表", "schema effect.oneOf", errors)
    compare("cardKind", ddd_card_kinds(), set(validate.DEFS["card"]["properties"]["kind"]["enum"]),
            "ddd 编队参数 卡型表", "schema card.kind", errors)
    slots = ddd_equip_slots()
    compare("equipSlot", slots, set(validate.DEFS["equipmentSpec"]["properties"]["slot"]["enum"]),
            "ddd 编队参数 装备槽表", "schema equipmentSpec.slot", errors)
    compare("equipSlot", slots, set(validate.DEFS["condition"]["properties"]["slot"]["enum"]),
            "ddd 编队参数 装备槽表", "schema condition.slot", errors)

    print("-" * 60)
    if errors:
        print("漂移枚举 %d 组: %s" % (len(set(errors)), ", ".join(sorted(set(errors)))))
        print("处置：先在 ddd/params 对应参数篇登记，再改 schema，最后改数据。")
        return 1
    print("全部枚举组一致（有意分歧见 KNOWN 登记）")
    return 0

if __name__ == "__main__":
    sys.exit(main())
