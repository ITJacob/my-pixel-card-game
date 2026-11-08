# hero_06_b（family_13 星钥·开门人）机制层回归报告（2026-11-08）

## 扫描基线

review_scan R1–R11（基线 2026-11-08）；hero_06_b 组 5 warn + hero_06 组连带 3 warn（family_13 新 defs 入链）。

## 命中表

| R# | 位置 | 命中 | 处置 |
|---|---|---|---|
| R1 | gate 轴 ×2（hero_06/06_b） | 轴无产/读层卡 | **豁免**：gate 轴是「在场」机制非层数引擎——产=开门三卡挂 star_gate（presence 写入），读=j06_gate_tongue 的 caster_status_exists（presence 读）。R1 启发式只认层数型原语，presence 机制天然不命中。 |
| R3 | family_13 star_key | 叠层无读档出口 | **豁免**：star_key 消费口明确且多卡——万能钥（has_status ≥2 挂钥势）、钥惠（all_of 内含 has_status 耗 1）、星门全开（stacksDelta −99 倾尽）。R3 的跨卡消费探测未覆盖 all_of 嵌套写法。 |
| R4 | family_13 tide_high | duration 30 挂回合触发点 | **豁免**：与 hero_06 既有豁免同卡同理由（2026-11-01 基线在册）。 |
| R9 | family_13 on_battle_start 集中 | 8 张 → 修 | **已修**：门的语言 hook 改 on_turn_start，回落至 7 张阈值内。 |
| R11 | j06_fate_revelation | 被动写战场量表 fate_value | **豁免**：与 hero_06 既有豁免同卡同理由（fate_value 写入方为 monster 家族，该卡为在册既有卡）。 |

## 修复记录

- j06_gate_tongue：hook on_battle_start → on_turn_start（R9 集中度回落至 7，触发逻辑不变——实际生效靠 triggers 的 on_deal_damage）。

## 门禁复核

validate 0 err / validate_schema 0 err（43 文件）/ enum sync OK / glossary OK。

## 定稿确认

组内 review_scan 剩余 5 warn 全部豁免在案（3 条为 hero_06 组连带同卡同理由）；hero_01_b 产卡经四脚本全绿。**hero_06_b 定稿。**
