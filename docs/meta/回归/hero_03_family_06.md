# 回归报告 hero_03（family_06 arbiter，法令规则槽）

日期：2026-10-30｜机筛：`review_scan.py --hero 03`

## ① 扫描基线

8 warns（R11×4 R4×1 R6×3）。四门禁全绿。

## ② 命中表

| 命中 | 判定 |
|---|---|
| R11 h03_authority_shift / rank_jurisdiction / rank_decree / legal_memory 被动写 order | 豁免（批量） |
| R4 sd decree duration 30tick 挂 on_turn_start | 豁免 |
| R6 sd castigated / rank_jurisdiction / rank_decree 常驻伤害乘区 | 豁免（批量） |

## ③ 修复记录

无数据改动。豁免理由：

- R11×4：四卡是**秩序度写入供源**（ddd 登记的 dimHook order 供源路径，「律令 ×1.5」的源头），属设计本体而非违规消费。
- R4：decree 的回合宣示（on_turn_start 重申律令）是机制本体，30tick=6 回合为该设计的正常时长。
- R6×3：castigated 为按施法者过滤乘区（带审批档注记）；rank_jurisdiction/rank_decree 是位格环境常驻乘区（共享内核参数 §1.4 登记口径）。平衡期统一复核。

## ④ 门禁复核

四脚本全绿；残余 8 warn 均为登记豁免。

## ⑤ 定稿确认

hero_03 组机制层定稿（8 豁免）。—— 2026-10-30，commit 本次。
