# 工作流（五环节 + 环节⑥）

> 里程碑 v2 工作流定义：设定 → 机制 → JSON → 分析 → 重设计 五环节迭代，周期性骨架重议（环节⑥）。

## 五环节

| 环节 | 名称 | 产出 | 门槛 |
|---|---|---|---|
| ① | 设定补全 | 世界观/派系/英雄设定稿 | 主人拍板入档 |
| ② | 机制落地 | 原语/触发点/规则扩容提案（`meta/骨架重议.md` 登记） | 环节⑥ Gate 通过 + SCHEMA.md 登记 |
| ③ | 技能池 JSON | `docs/json/faction_NN.skills.json` 卡面 | schema（结构）+ validate（语义）+ check_enum_sync + check_glossary 四脚本全绿 + review_scan 该英雄组 0 warn |
| ④ | 分析评分 | 结构评分与蓝图兑现报告 | 评分只诊断结构，不作平衡依据（脚本随需要重建） |
| ⑤ | 重设计迭代 | 逐英雄/逐轴改卡 | 四脚本全绿 + 分数不回落 |

## 环节⑥：骨架重议

- 命题撞车（两条玩法骨架塌成一条）时**先换骨架**，不在既有骨架内硬叠机制。
- 机制扩容请求与拍板记录统一登记 `meta/骨架重议.md`。
- 新机制准入纪律：先登记 SCHEMA.md §5 封闭集清单（原语/触发点）→ 改 schema → 全链（DDD 参数篇 + glossary + 校验脚本）同步 → 数据才可用。

## 英雄迁移工艺（2026-10-28 首轮 9 英雄验证沉淀）

> 适用后续同派系第二英雄 / 落选旧职业轴玩法入档。

1. **取数登记**：从 CardGame 参考源（只读）选轴取卡，逐卡登记 `meta/迁移映射表.md`（新 id ↔ 旧途径/旧卡 id ↔ 改动类型）；每英雄一个 commit。
2. **改 id**：卡 id 形态 `fNN_<slug>`（派系公共，落 faction_NN 文件）/ `hNN_<slug>`（英雄独自，落 hero_NN 文件）；公共技能 5–8 张（原职业通用段）。
3. **剥字段**：删 lore/flavor/sequenceName/art/conversionNotes/frameworkFlags/sharedAcross/upgradeLadder/variants/secondaryTargets/role。
4. **闭包收集**：状态按卡引用闭包（含状态二级引用）；单位蓝本按 `unitId`/`unitDef` 键；界域/区域按卡面 `domain`/`zone` 对象的 `def` 键（注意不是 `zoneId`）。
5. **去 IP**：状态/卡文本统一改通用术语，旧设定专名与旧职业名清为通用词；**跨系枢纽（crossPathway / occult_seal 等读层）不继承**，死引用整段剔除。
6. **common 提入**：跨派系通用状态（burn/guard/thorns/charm/free_cast/silence 等）提入 `global.skills.json` 顶层 statusDefs，权威定义以参考源 common 为准，common 没有的从 owner 途径取。
7. **describe 对齐**：describe 的元素声称必须与效果结构可解析元素一致（四选一/随机派发卡尤其注意），validator 会抓。
8. **门禁**：四脚本全绿后才算迁完；映射表、manifest cardCount、待办同步勾选。

## 生成工作流

- 第二英雄及后续新内容的产卡走分层流水线（层〇命题蓝图 → 层一机制骨架 → 层二数值定档 → 层三卡面落地 → 层四回归验收），见 `meta/生成工作流.md`；本文的迁移工艺是其层三/层四在迁移场景下的特例。

## 迁移记录

- 2026-10-28：首轮 9 英雄全部迁移完成（853 → 266 卡），映射表 9 节齐全。工艺见上节，后续迁移照此执行。
