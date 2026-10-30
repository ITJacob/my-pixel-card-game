# 回归报告 hero_09（family_21 criminal，污秽/恶欲通道）

日期：2026-10-30｜机筛：`review_scan.py --hero 09`（校准后基线 5 warns）

## ① 扫描基线

5 warns（R1×1 R3×1 R6×3）。四门禁全绿。

## ② 命中表

| 命中 | 判定 |
|---|---|
| R1 axis demon 无读层卡 | 豁免（工具盲区登记） |
| R3 sd grazing_slot 叠层无读档出口 | 豁免 |
| R6 sd weapon_mastery / lost_conscience / mental_duelist 常驻伤害乘区 | 豁免（批量） |

## ③ 修复记录

无数据改动。豁免理由：

- R1：demon 轴的读层在**召唤侧**——rite_mark 经 `summonMapping`（深渊召唤按层数映射强度）被读，review_scan R1 不扫 summon 载荷，属工具盲区（登记，后续工具迭代补扫）；机制本身闭合。
- R3：grazing_slot 为跨系枢纽状态，生产者/读者在未选途径，已登记待办 §四与骨架重议选材池。
- R6×3：三者为身份/权柄定向乘区（weapon_mastery 物理 1.15、lost_conscience 对 debuff 目标 1.15、mental_duelist 对三污染状态 1.25），平衡期统一复核。

## ④ 门禁复核

四脚本全绿；残余 5 warn 均为登记豁免。

## ⑤ 定稿确认

hero_09 组机制层定稿（5 豁免）。—— 2026-10-30，commit 本次。
