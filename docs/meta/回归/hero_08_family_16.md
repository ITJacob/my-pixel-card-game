# 回归报告 hero_08（family_16 sailor，元素天灾/风暴连锁）

日期：2026-10-30｜机筛：`review_scan.py --hero 08`

## ① 扫描基线

3 warns（R3×1 R6×2）。四门禁全绿。

## ② 命中表

| 命中 | 判定 |
|---|---|
| R3 sd tide_call 叠层无读档出口 | **修复** |
| R6 sd scale_veil 常驻伤害乘区 | 豁免 |
| R6 sd tide_call 常驻伤害乘区 | 豁免 |

## ③ 修复记录

1. `faction_08 sd tide_call`：**删 `maxStacks:3 / stackPolicy:refresh`**。唯一挂载点（h08 英雄域注入）不传 stacks，乘区为平值 ×1.1——叠层语义从未生效，属迁移 vestige；删除后语义不变，R3 消除。

豁免理由：

- scale_veil：身份常驻减伤 0.9（轻减档），「并入参数化减伤母版」已注记，平衡期复核。
- tide_call：战吼常驻增益 ×1.1（浅乘区，crossPathway 枢纽计数语义保留在挂载侧）。

## ④ 门禁复核

四脚本全绿；`review_scan.py --hero 08` 残余 2 warn 均为登记豁免。

## ⑤ 定稿确认

hero_08 组机制层定稿（1 修复 + 2 豁免）。—— 2026-10-30，commit 本次。
