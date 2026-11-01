# JSON 结构规范（v2 四层作用域）

> `docs/json/schema/skills.schema.json` 是结构权威（改结构先改 schema）。卡型四型、32 原语、16 触发点为封闭集。

## 1. 文件布局（四层作用域：派系 → 家族 → 英雄）

```
docs/json/
├─ manifest.json            索引：9 派系 id/name/文件/卡数 + rarityMap 校验基准
├─ schema/skills.schema.json
├─ global.skills.json       全域级（唯一）：跨派系复用内容
├─ faction_NN.skills.json   派系级 ×9（NN=01..09）：家族间共享蓝本池（当前为空；cards 恒空）
├─ family_NN.skills.json    家族级 ×22（NN=01..22）：家族公共卡 + 家族私有蓝本池 + 家族元信息
└─ hero_NN.skills.json      英雄级 ×9：英雄独自卡 + family 归属字段
```

- 四个层级各一个文件根（schema 根 oneOf 按 `level` 字段分派到 fileRootGlobal / fileRootFaction / fileRootFamily / fileRootHero）。
- 每个文件统一**五池**格式：`cards` / `statusDefs` / `unitDefs` / `zoneDefs` / `domainDefs`，均为数组、可空。
- **家族编号（源质分组序，封闭 22 个）**：01 warrior / 02 corpse_collector / 03 sleepless（faction_01）；04 assassin / 05 hunter（faction_02）；06 arbiter / 07 lawyer（faction_03）；08 seer / 09 apprentice / 10 thief（faction_04）；11 pryer / 12 savant（faction_05）；13 monster（faction_06）；14 apothecary / 15 planter（faction_07）；16 sailor / 17 chanter / 18 reader / 19 spectator / 20 supplicant（faction_08）；21 criminal / 22 prisoner（faction_09）。在册 9 族（01/04/06/08/11/13/14/16/21）承接首轮英雄；其余 13 族为未展开空壳（五池全空），第二英雄选材时填充。
- **manifest 只登记 faction 文件条目**。`cardCount` 口径：派系卡数 = 该派系在册 family 文件 cards 之和（faction 文件 cards 恒空，不再直接计数）；`family_NN` / `hero_NN` / `global` 按文件名约定发现，**不在 manifest 登记**（避免同步面）。validate_schema 校验 family ↔ faction、hero ↔ family/faction 配对。

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
| cards | card[] | **恒为空数组**——原派系公共卡已下沉 family 层（2026-10 结构变更） |
| statusDefs / unitDefs / zoneDefs / domainDefs | 数组 | 家族间共享蓝本池（同派系多家族共用才入；2026-11 家族私有蓝本池已归还 family 层，本池当前为空） |

**family_NN.skills.json**：

| 字段 | 类型 | 说明 |
|---|---|---|
| level | const "family" | 层级标记 |
| familyId / familyName | string | `family_01..22` 封闭 / 家族中文名（占位符期：家族·壹…家族·贰拾贰） |
| faction | string | 所属派系 id（须为存在的 faction 文件，经 cross_check 配对验证） |
| cards | card[] | 家族公共卡（id `jNN_` 前缀，NN=派系号；j 释义为家族） |
| statusDefs / unitDefs / zoneDefs / domainDefs | 数组 | 家族私有蓝本池（未展开家族恒空；2026-11 起家族独占定义一律入本层） |

- 家族文件 id 前缀口径：卡 id `j<NN>_` 的 NN = **文件 faction 号**（同派系家族组共享 j 号，如 family_04 与 family_05 同为 faction_02 组、均挂 j02_ 卡）；`familyId` 序号 = 文件名序号（源质分组序），与 j 号无对应关系。**f 前缀预留给 faction 级卡**（faction 文件 cards 恒空，暂无此类卡）。
- **hero_NN.skills.json**：

| 字段 | 类型 | 说明 |
|---|---|---|
| level | const "hero" | 层级标记 |
| heroId / heroName | string | `hero_01..09` / 英雄中文名（与文件名序号一致） |
| family | string | 所属家族 id（须为存在的 family 文件，且该 family 的 faction 与本文件 faction 一致） |
| faction | string | 所属派系 id（须 `faction_01..09` 与文件名序号一致） |
| playstyle | string | 玩法骨架一句话（一条轴的玩法声明） |
| cards | card[] | 仅该英雄独自卡（id `hNN_` 前缀） |
| statusDefs / unitDefs / zoneDefs / domainDefs | 数组 | 留空占位（`[]`） |

- 家族公共 passive 的 `initialEquip` 目标：global 文件或**同家族文件组**（family_NN + 其下 hero 文件）内的 kind=equipment 卡——允许跨本文件引用（如 family_01 卡引用 hero_01 文件里的开局武器 h01_standard_blade）。
- 已删除字段：卡 `scope`/`heroId`（归属由所在文件定）、faction 文件 `sharedSkillIds`/`heroes`（含 `skillTree`/`uniqueSkillIds`，全库无消费者）。

## 3. $extends 声明式继承

- 五池内任意条目（卡/状态/单位/区域/界域定义）可带 `"$extends": "<父定义id>"`。
- **解析序（四层链）**：hero 文件 → 本文件 → `family` 字段所指 family 文件 → 同派系 faction 文件 → global；family 文件 → 本文件 → `faction` 字段所指 faction 文件 → global；faction 文件 → 本文件 → global。父定义在同名池内按序查找。**禁同层跨文件**（hero_01 不能 extends hero_02 / family_01 的条目）。
- **物化规则**（引擎/工具加载时合并）：逐字段浅合并，子字段存在即覆写；`tags` 取父∪子并集（继承语义核心：扩展带父级 tag 供效果查询）；嵌套对象整体替换，不做深合并。
- 校验（validate_schema `check_extends`）：父必须存在且解析序合规（含循环检测）；合并后物化条目重新过结构校验，不得产生 schema 违规。

## 4. 卡（card）

- `kind`：active / passive / equipment / summon。
  - active → 必填 cost/reach/target；passive → 必填 hook；equipment → 必填 cost + equipment 载荷（slot=weapon|armor）；summon → 必填 cost + summon 载荷（一卡一单位）。
- `effects`：效果树（原语叶子 + sequence/repeat/if 算子）；equipment/summon 的 effects 为可选战吼。
- `id`：`^[a-z][a-z0-9_]*$`；前缀约束按文件层级由 cross_check 执行（family 文件 `jNN_` / hero 文件 `hNN_`；faction 文件 cards 恒空、global 无前缀约束，见 §2 口径；`fNN_` 预留给 faction 级卡，出现在其他层级即报错）。
- 文本面：name / describe（机制描述，禁设计过程）；lore/flavor 命名专项前不回流。
- 无 sequenceName / sourceFile 等旧里程碑字段。

## 5. 封闭集登记

- 原语 32 个：封闭集 = schema `effect.oneOf`（35 分支 = 3 算子 + 32 原语叶子）；参数取值域见 `ddd/params/效果参数.md` 原语表。新增先登记再改 schema。
- 触发点 16 个：on_battle_start / on_turn_start / on_turn_end / on_apply / on_remove / on_tick / on_phase_change / on_spawn / on_death / on_kill / on_attack / on_equipment_equip / on_active_skill / on_take_damage / on_deal_damage / on_status_gain。
- 元素 / 资源池 / 装备槽 / 状态类别取值域见 ddd params 三篇。

## 6. 已知待修清单

（暂无——迁移期随发现登记于此）
