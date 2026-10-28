# JSON 结构规范（v2 首版）

> `docs/json/schema/skills.schema.json` 是结构权威（改结构先改 schema）。卡型四型、32 原语、16 触发点为封闭集。

## 1. 文件布局

```
docs/json/
├─ manifest.json            索引：9 派系 id/name/文件/卡数 + rarityMap 校验基准
├─ schema/skills.schema.json
├─ faction_NN.skills.json   派系文件（NN=01..09）
└─ common.statuses.json     跨派系共享状态
```

## 2. 派系文件顶层结构

| 字段 | 类型 | 说明 |
|---|---|---|
| factionId | string | `faction_01..09` 封闭 |
| factionName | string | 占位「派系·壹…玖」 |
| sharedSkillIds | string[] | 派系公共技能池（卡 id） |
| heroes | object[] | 英雄块（见 §3） |
| cards | card[] | 全集；卡带 `scope` |
| statusDefs / unitDefs / zoneDefs / domainDefs | object[] | 蓝本池 |

## 3. 英雄块

| 字段 | 说明 |
|---|---|
| heroId / heroName | `hero_01…` / 占位「英雄·壹…玖」 |
| playstyle | 玩法骨架一句话（一条轴的玩法声明） |
| skillTree | 技能树入口卡 id（独自技能的分期解锁序） |
| uniqueSkillIds | 独自技能全集 |

## 4. 卡（card）

- `kind`：active / passive / equipment / summon。
  - active → 必填 cost/reach/target；passive → 必填 hook；equipment → 必填 cost + equipment 载荷（slot=weapon|armor）；summon → 必填 cost + summon 载荷（一卡一单位）。
- `scope`：`faction`（公共技能）/ `hero`（独自技能，带 `heroId` 归属）。
- `effects`：效果树（原语叶子 + sequence/repeat/if 算子）；equipment/summon 的 effects 为可选战吼。
- 文本面：name / describe（机制描述，禁设计过程）；lore/flavor 命名专项前不回流。
- 无 sequenceName / sourceFile 等旧里程碑字段。

## 5. 封闭集登记

- 原语 32 个：见 SCHEMA.md 原语表（= schema effect.oneOf）。新增先登记再改 schema。
- 触发点 16 个：on_battle_start / on_turn_start / on_turn_end / on_apply / on_remove / on_tick / on_phase_change / on_spawn / on_death / on_kill / on_attack / on_equipment_equip / on_active_skill / on_take_damage / on_deal_damage / on_status_gain。
- 元素 / 资源池 / 装备槽 / 状态类别取值域见 ddd params 三篇。

## 6. 已知待修清单

（暂无——迁移期随发现登记于此）
