# CLAUDE.md

本仓库是 MyPixelCardGame 里程碑 v2：**设计文档 + 卡池数据的唯一权威源**，实现由 Godot 方案另行重建（不在本仓库）。

## 铁律

1. **CardGame 仓库（`C:\Projects\self\CardGame`）是只读参考源**——旧里程碑含诡秘之主 IP 与 22 途径全量；取数对照可以，**绝不写入**。
2. IP 占位符期：派系「派系·壹…玖」、英雄「英雄·壹…玖」、卡 id 用 code name；**全库禁出现旧 IP 专名**（诡秘/源堡/序列/愚者/魔药/教会/塔罗等）。
3. `docs/ddd/` 保持纯内容：只描述最终模型，不写拍板过程、不写实现细节（无代码类型名）、不写数值锚点（随英雄迁移登记）。
4. 改 JSON 结构先改 `docs/json/schema/skills.schema.json` 再改数据；改完跑四个校验脚本全绿才算合规。
5. lore/flavor 字段在命名专项前**不回流**；卡面只留 name/describe（机制描述，禁设计过程）。

## 架构大图（v2）

- **9 派系源于九源质 → 22 家族（源质分组序）→ 英雄**：每家族先 1 英雄；英雄 = 一条轴的玩法 + 技能树；家族 = 公共技能池 + 英雄容器；派系 = 蓝本池 + 家族容器。家族即旧里程碑的职业（22 途径一一对应）。
- **整场战斗一聚合**（Combat），纯函数契约（同种子同输入 ⇒ 逐位相同）；进度条回合制，**无手牌概念**。
- **32 原语 + 16 触发点封闭集**（INV-17/18），权威源是 schema 的 effect.oneOf；新增须先登记 SCHEMA.md。
- 装备两槽（武器耐久 / 护具护甲池）、规则槽 Rules[3]、界域压制栈、召唤 cap——机制细节见 `docs/ddd/`。
- 20 条核心不变量（INV-1..20）在 `docs/ddd/README.md`，是所有设计的约束边界。

## 文档地图

```
docs/ddd/    战斗内核设计（权威正源；contexts/ 五上下文 + params/ 三参数 + README 不变量）
docs/meta/   WORKFLOW（五环节+环节⑥）/ SCHEMA（JSON 结构规范）/ 骨架重议 / 待办 / 迁移映射表 / glossary
docs/json/   卡池唯一权威源：manifest.json + global.skills.json + faction_NN.skills.json ×9 + family_NN.skills.json ×22 + hero_NN.skills.json ×9 + schema/
docs/tools/  validate（语义）/ validate_schema（结构）/ check_enum_sync（枚举对账）/ check_glossary（词典）
```

## 迁移工作流

1. 从 CardGame 参考源挑轴取卡（旧途径/卡 id 记入 `docs/meta/迁移映射表.md`，含改动类型：直迁/改数值/合并/重写）。
2. 去 IP 改写：name/describe 机制化表述，删 lore/flavor，清 sequenceName 前缀。
3. 按 schema 落对应层级文件（家族公共卡 → family_NN，英雄独自卡 → hero_NN，跨派系复用 → global；faction_NN 只留派系蓝本池）。
4. 四脚本全绿后提交；每英雄迁移一个 commit。

## Git 方式

- 中文路径用 `git -c core.quotePath=false ...`；commit message 中文 + conventional 前缀，避免反引号（用单引号或 -F）。
- 只 commit；push 需主人明确要求。
