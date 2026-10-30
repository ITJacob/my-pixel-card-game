# 回归报告 hero_01（family_01 warrior，装备近战 + 契约点名）

日期：2026-10-30｜工艺：`meta/生成工作流.md` 层四｜机筛：`tools/review_scan.py --hero 01`

## ① 扫描基线

1 warn（R10×1）。四门禁全绿。

## ② 命中表

| 命中 | 判定 |
|---|---|
| R10 h01_unstoppable modify_stat +4 跳档 | 豁免 |

## ③ 修复记录

无数据改动。豁免理由：`h01_unstoppable` 的 +4 攻击是**耗层换效**——消耗 3 层 war_spirit（3 次产层成本）换 10tick 攻击 +4，且带防御 -1 代价，非裸跳档；符合锚点表「乘区/属性须带代价」精神。

## ④ 门禁复核

四脚本全绿；`review_scan.py --hero 01` 残余 1 warn 为登记豁免。

## ⑤ 定稿确认

hero_01 组机制层定稿（1 豁免）。—— 2026-10-30，commit 本次。
