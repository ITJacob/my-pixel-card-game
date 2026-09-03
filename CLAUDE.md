# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

像素风 Roguelike 卡牌对战游戏，Godot 4.7.2 .NET (C#) 开发，目标平台 Steam。当前处于 **Phase 1（单机原型）**阶段——本仓库是脚手架，`src/` 下尚无实际代码，README 中的目录结构描述的是**预期布局**，不是现状。

## 常用命令

```bash
# 构建 C# 项目（根目录执行，生成 MyGame.sln 后也可用 IDE 构建）
dotnet build

# 运行游戏：用 Godot 4.7.2 .NET 编辑器打开 project.godot，按 F5
# （必须构建成功后编辑器才能加载 C# 脚本）

# 从原项目同步设计稿到 docs/（只读参考，不在本项目修改）
./sync_docs.ps1 <原项目路径>   # Windows
./sync_docs.sh <原项目路径>    # macOS/Linux
```

测试框架尚未搭建。Core 层设计要求可单元测试，添加测试时应建独立的 .NET 测试项目（如 `MyGame.Tests`）引用 `src/Core`，不依赖 Godot 运行时。

## 核心架构约束（必须遵守）

**严格分层：`src/Core/`（纯逻辑）与 `src/Godot/`（引擎交互）完全隔离。**

Core 层（`src/Core/`）硬性规则：
- **禁止 `using Godot;`** —— 零引擎依赖的纯 .NET 类库
- **纯函数式状态变更** —— 状态类（如 `CombatState`）的 `ProcessAction(action)` 返回**新状态对象**而非原地修改（为 Phase 3 网络同步预留）
- **所有状态类必须支持 JSON 序列化**
- 命名空间为 `MyGame.Core.*`（如 `MyGame.Core.Combat`、`MyGame.Core.Effects`）

Godot 层（`src/Godot/`）职责：
- 输入翻译：玩家操作 → Core 层的 Action 对象
- 状态渲染：Core 返回的新 GameState → 更新场景节点
- 动画/特效调度，**不参与逻辑判断**

出牌数据流：`CardView` 点击 → 生成 `PlayCardAction` → `BattleManager` 调用 `CombatState.ProcessAction()` → 接收新状态 → 更新节点与动画。

详细架构与接口设计（`ICardEffect`、`EffectContext`、`CombatState` 示例）见 `docs-project/ARCHITECTURE.md`。

## 代码规范

- 语言：C# / .NET 8，根命名空间 `MyGame`
- 接口加 `I` 前缀（如 `ICardEffect`）；属性用 `{ get; set; }`；集合用 `List<T>`
- Godot C# 脚本：继承节点的类必须是 `partial`；生命周期方法 PascalCase（`_Ready()`、`_Process(double delta)`——注意是 double 不是 float）；信号用 `[Signal] delegate ...EventHandler` 模式
- 本项目大量逻辑从 TypeScript 原项目迁移，翻译对照表见 `docs-project/TS_TO_CSHARP.md`

## 渲染与美术（改 UI/场景时需注意）

- 视口 640×360，Integer Scaling 放大，`stretch/mode="viewport"` + `scale_mode="integer"`
- 纹理导入必须 **Filter: Nearest、Repeat: Disabled、Mipmaps: Disable**（像素风硬边，禁止抗锯齿模糊）
- 美术资源固定 32 色调色板、1px 黑色描边、左上 45° 光源；像素特效**禁止 AI 逐帧生成**，用 Tween/粒子/Shader 实现
- 完整规范见 `docs-project/ART_PIPELINE.md`

## 目录约定

- `docs/` —— 从原项目同步的设计稿，**只读**，不修改（改动会被 sync_docs 覆盖）
- `docs-project/` —— 本项目文档：ARCHITECTURE.md（架构）、TS_TO_CSHARP.md（迁移对照）、ART_PIPELINE.md（美术流程）、NETWORK_PLAN.md（联网路线图）
- `assets/sprites/` —— 像素图（cards/characters/ui 分类）；`tools/` —— 自动化脚本（如像素图批处理）

## 网络对战预留（Phase 3，现在不实现）

架构已按 Host-Client 权威服务器模型预留：Host 运行 Core 逻辑，Client 只发输入收状态。当前阶段**不写任何网络代码**，但写 Core 层时必须保持「输入 → 新状态 → 渲染」的纯函数结构，不得引入破坏该结构的就地状态修改。消息协议草案见 `docs-project/NETWORK_PLAN.md`。
