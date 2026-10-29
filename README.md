# MyPixelCardGame（里程碑 v2）

像素风卡牌爬塔游戏的**设计文档 + 卡池数据仓库**（里程碑 v2）。

- 本仓库只承载 `docs/`：DDD 战斗内核设计（`docs/ddd/`）、工作流与规范（`docs/meta/`）、卡池 JSON 唯一权威源（`docs/json/`）、校验脚本（`docs/tools/`）。
- **9 大派系**（源于九源质）→ **22 家族**（源质分组序，在册 9 个）→ **英雄层**：英雄有自己的玩法与技能树，同时可用家族公共技能。家族即旧里程碑的职业（22 途径一一对应），职业概念以家族形态存续。
- IP 为占位符（派系·壹…玖 / 英雄·壹…玖），命名专项后续再定。
- 实现不在本仓库：由 Godot 技术方案按 `docs/json/schema/` + `docs/ddd/` 重建。
- `C:\Projects\self\CardGame`（旧里程碑）是**只读参考源**——含诡秘之主 IP 与 22 途径全量，不要在其中做任何修改。

## 目录

```
docs/
├─ ddd/            战斗内核 DDD 设计（权威正源，纯内容）
│  ├─ README.md    总览 + 20 条核心不变量
│  ├─ contexts/    战斗/编队/效果/战场/编目 五上下文
│  └─ params/      效果/执行/编队 参数取值域
├─ meta/           流程·规范·映射表（WORKFLOW / SCHEMA / 骨架重议 / 待办 / 迁移映射表 / glossary）
├─ json/           卡池数据唯一权威源（manifest + global + faction_01..09 + family_01..22 + hero_01..09 + schema）
└─ tools/          数据校验脚本（纯 Python，唯一门禁）
```

## 快速校验

```bash
PYTHONIOENCODING=utf-8 python docs/tools/validate.py
PYTHONIOENCODING=utf-8 python docs/tools/validate_schema.py   # 需 jsonschema
PYTHONIOENCODING=utf-8 python docs/tools/check_enum_sync.py
PYTHONIOENCODING=utf-8 python docs/tools/check_glossary.py
```
