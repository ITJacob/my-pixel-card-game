# hero_04_c（family_09 时隙·行商）机制层回归报告（2026-11-08）

## 扫描基线

review_scan R1–R11（基线 2026-11-08）；hero_04_c 组 1 warn。

## 命中表

| R# | 位置 | 命中 | 处置 |
|---|---|---|---|
| R6 | family_08 power_refine | 常驻伤害乘区 | 承袭豁免（hero_04/hero_04_b 同卡同理由） |

## 修复记录

- h04c_book_early 抢先预订：snapshot 原语补 `fields` 必填（["phase","hp","gauge.current"]）、去多余 target——schema 复验通过。

## 门禁复核

validate 0 err / validate_schema 0 err（50 文件）/ enum sync OK / glossary OK。

## 定稿确认

1 warn 为 family_08 链承袭；新卡零新增。**hero_04_c 定稿。**
