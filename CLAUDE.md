# CLAUDE.md

本仓库是 MyPixelCardGame 里程碑 v2：**设计文档 + 卡池数据的唯一权威源**，实现由 Godot 方案另行重建（不在本仓库）。

## 铁律

1. **CardGame 仓库（`D:/Projects/CardGame`）是只读参考源**——旧里程碑含旧 IP 与 22 条旧职业轴全量；取数对照可以，**绝不写入**。
2. IP 占位符期：派系「派系·壹…玖」、英雄「英雄·壹…玖」、卡 id 用 code name；**全库禁出现旧 IP 专名**（诡秘/源堡/序列/愚者/魔药/教会/塔罗等）。
3. `docs/ddd/` 保持纯内容：只描述最终模型，不写拍板过程、不写实现细节（无代码类型名）、不写数值锚点（随英雄迁移登记）。
4. 改 JSON 结构先改 `docs/json/schema/skills.schema.json` 再改数据；改完跑四个校验脚本全绿才算合规。
5. lore/flavor 字段在命名专项前**不回流**；卡面只留 name/describe（机制描述，禁设计过程）。

## 架构大图（v2）

- **9 派系源于九源质 → 22 家族（源质分组序）→ 英雄**：每家族先 1 英雄；英雄 = 一条轴的玩法 + 技能树；家族 = 公共技能池 + 私有蓝本池 + 英雄容器；派系 = 家族容器 + 家族间共享蓝本池（当前为空）。家族即旧里程碑的职业（22 途径一一对应）。
- **整场战斗一聚合**（Combat），纯函数契约（同种子同输入 ⇒ 逐位相同）；进度条回合制，**无手牌概念**。
- **32 原语 + 16 触发点封闭集**（INV-17/18），权威源是 schema 的 effect.oneOf；新增须先登记 SCHEMA.md。
- 装备两槽（武器耐久 / 护具护甲池）、规则槽 Rules[3]、界域压制栈、召唤 cap——机制细节见 `docs/ddd/`。
- 29 条核心不变量（INV-1..29）在 `docs/ddd/README.md`，是所有设计的约束边界。

## 文档地图

```
docs/ddd/    战斗内核设计（权威正源；contexts/ 六上下文 + params/ 七参数 + README 不变量）
docs/meta/   WORKFLOW（五环节+环节⑥）/ 生成工作流（分层产卡层〇–层四）/ SCHEMA（JSON 结构规范）/ 派系基调（基准总表+通则索引）+ 派系/faction_NN ×9（一系一档）/ 骨架重议 / 待办 / 迁移映射表 / glossary
docs/json/   卡池唯一权威源：manifest.json + global.skills.json + faction_NN.skills.json ×9 + family_NN.skills.json ×22 + hero_NN.skills.json（9 主体 + 变体共 44）+ schema/
docs/tools/  validate（语义）/ validate_schema（结构）/ check_enum_sync（枚举对账）/ check_glossary（词典）/ review_scan（机制层机筛 warn 级）/ build_wiki（站点生成）/ concept_map（概念地图锚点）
```

## 站点发布契约

- `_site/` 是 `docs/tools/build_wiki.py` 的生成产物，不入库、**禁止手改**；push main 由 `.github/workflows/pages.yml` 全量重建并部署 Pages。
- 站点唯一链路：`site/`（源）→ `docs/tools/build_wiki.py`（生成器）→ `_site/`（产物）→ Pages；`site/` 是源、`_site/` 是产物，不得混写。三份玩法源为 `site/dashboard.md`（极简概要）、`site/figures.html`（5 张 SVG 图源）、`site/concept-map.json`（概念地图指针）。
- `site/concept-map.json` 是「概要 ↔ 正源」的唯一指针表：只登记 `doc + section`，**不复制规则文字**。`rules/战场玩法.html` 是唯一玩法页，6 个概念以 `details.drawer[name="concept"]` 就地互斥展开（同时只开一个），不设详情页；正源在构建期从 DDD 的 `## 章节` 切片注入抽屉内。
- 改 `docs/ddd/**` 章节**内容**后网页端自动同步，无需手工改网页；改章节标题、删章节、新增概念时，必须同步更新 `site/concept-map.json`，否则构建直接失败并点名位置。
- 改完 `docs/ddd/**`、`docs/json/**`、`site/dashboard.md`、`site/concept-map.json` 后跑 `python docs/tools/build_wiki.py`（内含锚点校验）；单独校验用 `python docs/tools/concept_map.py --check`。
- 新增 DDD 正源须同时加入 `build_wiki.py` 的 `md_pages` 白名单，并在 `site/concept-map.json` 的 `pages` 登记站点页路径；`check_pages` 会拦死链。
- 概要正文 `site/dashboard.md` 保持极简（无过程、无日期、无备注）；详细解释只从正源切片，不在概要里复写。

## 迁移工作流

1. 从 CardGame 参考源挑轴取卡（旧途径/卡 id 记入 `docs/meta/迁移映射表.md`，含改动类型：直迁/改数值/合并/重写）。
2. 去 IP 改写：name/describe 机制化表述，删 lore/flavor，清 sequenceName 前缀。
3. 按 schema 落对应层级文件（英雄私有卡 hNN_（≤6）→ hero_NN，家族公共卡 jNN_ → family_NN，派系公共卡 fNN_ → faction_NN，家族独占蓝本 → family_NN 五池，跨派系复用 → global）。
4. 四脚本全绿后提交；每英雄迁移一个 commit。

## Git 方式

- 中文路径用 `git -c core.quotePath=false ...`；commit message 中文 + conventional 前缀，避免反引号（用单引号或 -F）。
- 只 commit；push 需主人明确要求。
