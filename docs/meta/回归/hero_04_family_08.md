# 回归报告 hero_04（family_08 seer，提线傀儡/秘偶换位）

日期：2026-10-30｜机筛：`review_scan.py --hero 04`（校准后基线 4 warns）

## ① 扫描基线

4 warns（R1×1 R3×1 R6×2）。四门禁全绿。

## ② 命中表

| 命中 | 判定 |
|---|---|
| R1 axis miracle 无读层卡 | **修复** |
| R3 sd clairvoyance 叠层无读档出口 | **修复** |
| R6 sd power_refine / fate_gap 常驻伤害乘区 | 豁免（批量） |

## ③ 修复记录

1. `h04_spirit_shelter` axis `miracle` → `trick`；`j04_power_refine` axis `miracle` → `trick`。miracle 轴在选材后只剩单卡且产读不闭合，两张卡机制（灵界规避 / 途径增伤引擎）均属 trick 杂项段，归位后 miracle 轴悬空消除。
2. `faction_04 sd clairvoyance`：删 `maxStacks:3 / stackPolicy:refresh`。挂载点（占星开启灵视等）不传 stacks，叠层语义从未生效（同 hero_08 tide_call 先例）。

豁免理由：power_refine（途径过滤 ×1.3）、fate_gap（行动条 >70 过滤 ×1.3）为条件过滤常驻乘区，属身份/协同引擎，平衡期统一复核。

## ④ 门禁复核

四脚本全绿；残余 2 warn 为登记豁免。

## ⑤ 定稿确认

hero_04 组机制层定稿（2 修复 + 2 豁免）。—— 2026-10-30，commit 本次。
