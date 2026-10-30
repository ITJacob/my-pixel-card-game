# 回归报告 hero_02（family_04 assassin，镜映借序）

日期：2026-10-30｜机筛：`review_scan.py --hero 02`

## ① 扫描基线

4 warns（R1×1 R6×3）。四门禁全绿。

## ② 命中表

| 命中 | 判定 |
|---|---|
| R1 axis charm 无读层卡 | **修复** |
| R6 sd witch_form / form_shadow / form_mist 常驻伤害乘区 | 豁免（批量） |

## ③ 修复记录

1. `h02_lure_step`：axis `charm` → `mirror`。该卡产 borrowed_step（借序链，镜映家族签名面），孤立的 charm 轴标签与魅惑轴链（charm_axis，读者在 plague/mirror 轴）错位；归位后轴内产读闭环，charm 轴悬空消除。

豁免理由：witch_form/form_shadow/form_mist 为形态/身份常驻减伤 0.9（轻减档），乘区审批档已注记，平衡期统一复核。

## ④ 门禁复核

四脚本全绿；残余 3 warn 为登记豁免。

## ⑤ 定稿确认

hero_02 组机制层定稿（1 修复 + 3 豁免）。—— 2026-10-30，commit 本次。
