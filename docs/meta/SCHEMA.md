# JSON 结构规范（v2 三层作用域）

> `docs/json/schema/skills.schema.json` 是结构权威（改结构先改 schema）。卡型四型、32 原语、16 触发点为封闭集。

## 1. 文件布局（三层作用域）

```
docs/json/
├─ manifest.json            索引：9 派系 id/name/文件/卡数 + rarityMap 校验基准
├─ schema/skills.schema.json
├─ global.skills.json       全域级（唯一）：跨派系复用内容
├─ faction_NN.skills.json   派系级 ×9（NN=01..09）：派系公共卡 + 派系私有蓝本池
└─ hero_NN.skills.json      英雄级 ×9：英雄独自卡 + 英雄元信息
```

- 三个层级各一个文件根（schema 根 oneOf 按 `level` 字段分派到 fileRootGlobal / fileRootFaction / fileRootHero）。
- 每个文件统一**五池**格式：`cards` / `statusDefs` / `unitDefs` / `zoneDefs` / `domainDefs`，均为数组、可空。
- manifest 只登记 faction 文件条目（`cardCount` 只数派系公共卡）；`hero_NN.skills.json` 与 `global.skills.json` 按文件名约定发现，**不在 manifest 登记**（避免同步面）。validate_schema 校验 hero 文件 ↔ faction 文件配对。

## 2. 各层文件根

**global.skills.json**（只收跨派系复用内容；id 无前缀约束）：

| 字段 | 类型 | 说明 |
|---|---|---|
| level | const "global" | 层级标记 |
| name | string | 文件显示名（「全域」） |
| cards / statusDefs / unitDefs / zoneDefs / domainDefs | 数组 | 五池，均可空 |

**faction_NN.skills.json**：

| 字段 | 类型 | 说明 |
|---|---|---|
| level | const "faction" | 层级标记 |
| factionId / factionName | string | `faction_01..09` 封闭 / 派系中文名 |
| cards | card[] | 仅派系公共卡（id `fNN_` 前缀，NN=文件序号） |
| statusDefs / unitDefs / zoneDefs / domainDefs | 数组 | 派系私有蓝本池 |

**hero_NN.skills.json**：

| 字段 | 类型 | 说明 |
|---|---|---|
| level | const "hero" | 层级标记 |
| heroId / heroName | string | `hero_01..09` / 英雄中文名（与文件名序号一致） |
| faction | string | 所属派系 id（须 `faction_01..09` 与文件名序号一致） |
| playstyle | string | 玩法骨架一句话（一条轴的玩法声明） |
| cards | card[] | 仅该英雄独自卡（id `hNN_` 前缀） |
| statusDefs / unitDefs / zoneDefs / domainDefs | 数组 | 留空占位（`[]`） |

- 派系公共 passive 的 `initialEquip` 目标：global 文件或**同派系文件组**（faction_NN + hero_NN）内的 kind=equipment 卡——允许跨本文件引用（如 faction 卡引用 hero 文件里的开局武器）。
- 已删除字段：卡 `scope`/`heroId`（归属由所在文件定）、faction 文件 `sharedSkillIds`/`heroes`（含 `skillTree`/`uniqueSkillIds`，全库无消费者）。

## 3. $extends 声明式继承

- 五池内任意条目（卡/状态/单位/区域/界域定义）可带 `"$extends": "<父定义id>"`。
- **解析序**：hero 文件 → 同派系 faction 文件 → global；faction 文件 → global。父定义在同名池内按序查找。**禁同层跨文件**（hero_01 不能 extends hero_02 的条目）。
- **物化规则**（引擎/工具加载时合并）：逐字段浅合并，子字段存在即覆写；`tags` 取父∪子并集（继承语义核心：扩展带父级 tag 供效果查询）；嵌套对象整体替换，不做深合并。
- 校验（validate_schema `check_extends`）：父必须存在且解析序合规（含循环检测）；合并后物化条目重新过结构校验，不得产生 schema 违规。

## 4. 卡（card）

- `kind`：active / passive / equipment / summon。
  - active → 必填 cost/reach/target；passive → 必填 hook；equipment → 必填 cost + equipment 载荷（slot=weapon|armor）；summon → 必填 cost + summon 载荷（一卡一单位）。
- `effects`：效果树（原语叶子 + sequence/repeat/if 算子）；equipment/summon 的 effects 为可选战吼。
- `id`：`^[a-z][a-z0-9_]*$`；前缀约束按文件层级由 cross_check 执行（faction 文件 `fNN_` / hero 文件 `hNN_`，NN=文件序号；global 无前缀约束）。
- 文本面：name / describe（机制描述，禁设计过程）；lore/flavor 命名专项前不回流。
- 无 sequenceName / sourceFile 等旧里程碑字段。

## 5. 封闭集登记

- 原语 32 个：封闭集 = schema `effect.oneOf`（35 分支 = 3 算子 + 32 原语叶子）；参数取值域见 `ddd/params/效果参数.md` 原语表。新增先登记再改 schema。
- 触发点 16 个：on_battle_start / on_turn_start / on_turn_end / on_apply / on_remove / on_tick / on_phase_change / on_spawn / on_death / on_kill / on_attack / on_equipment_equip / on_active_skill / on_take_damage / on_deal_damage / on_status_gain。
- 元素 / 资源池 / 装备槽 / 状态类别取值域见 ddd params 三篇。

## 6. 已知待修清单

（暂无——迁移期随发现登记于此）
