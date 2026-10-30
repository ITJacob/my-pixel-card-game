# 回归报告 hero_06（family_13 monster，灵感/命运双极）

日期：2026-10-30｜机筛：`review_scan.py --hero 06`（校准后基线 2 warns）

## ① 扫描基线

2 warns（R11×1 R4×1）。四门禁全绿。

## ② 命中表

| 命中 | 判定 |
|---|---|
| R11 h06_fate_revelation 被动写 fate_value | 豁免 |
| R4 sd tide_high duration 30tick 挂 on_turn_start | 豁免 |

## ③ 修复记录

无数据改动。豁免理由：

- R11：monster 是 fate_value 的**唯一登记写入方**（维度写入供源系设计本体，「命运值推高 → 赐福乘区」闭环的源头）。
- R4：tide_high/low 双相位循环（低潮挨打攒运 / 高潮 ×1.5），回合轮转触发是机制本体。

## ④ 门禁复核

四脚本全绿；残余 2 warn 为登记豁免。

## ⑤ 定稿确认

hero_06 组机制层定稿（2 豁免）。—— 2026-10-30，commit 本次。
