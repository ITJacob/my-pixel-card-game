# hero_02_b（family_05 战祸·猎团长）机制层回归报告（2026-11-08）

## 扫描基线

review_scan R1–R11（基线 2026-11-08）；hero_02_b 组 3 warn。

## 命中表

| R# | 位置 | 命中 | 处置 |
|---|---|---|---|
| R6 | family_04 witch_form / form_shadow / form_mist | 常驻伤害乘区 | 承袭豁免（hero_02 同卡同理由，2026-11-01 清单在册） |

## 修复记录

- h02b_pincer 围猎：按标记选靶的嵌套 targetSpec 不合法（damage.target 只收 effectTarget）——重构为「全体伤害 + 全体猎物标记续网 20tick + conflict≥6 加档 + 集众清零」，describe 同步。schema 复验通过。

## 门禁复核

validate 0 err / validate_schema 0 err（45 文件）/ enum sync OK / glossary OK。

## 定稿确认

3 warn 全为 family_04 链承袭（豁免随卡不随英雄）；新 6 卡 + j02_集结号 **零新增**。**hero_02_b 定稿。**
