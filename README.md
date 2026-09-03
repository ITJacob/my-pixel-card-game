# MyPixelCardGame

一款像素风 Roguelike 卡牌对战游戏，使用 Godot 4 + C# 开发，目标平台 Steam。

> **当前阶段**: Phase 1 — 单机原型开发  
> **引擎**: Godot 4.7.2 .NET (C#)  
> **渲染**: 像素风 (640×360 Viewport + Integer Scaling)

---

## 📁 目录结构

```
MyPixelCardGame/
├── project.godot              # Godot 项目入口
├── MyGame.csproj              # C# 项目配置
├── MyGame.sln                 # Visual Studio 解决方案
├── .gitignore                 # Godot + C# 专用忽略规则
├── sync_docs.sh               # macOS/Linux: 从原项目同步设计稿
├── sync_docs.ps1              # Windows: 从原项目同步设计稿
│
├── docs/                      # 设计稿（从原项目同步，只读参考）
│   ├── card-design.md
│   ├── combat-flow.md
│   └── ui-mockups/
│
├── src/
│   ├── Core/                  # 纯 C# 游戏逻辑（不引用 Godot）
│   │   ├── Cards/             # 卡牌数据与效果
│   │   ├── Effects/           # 效果接口与实现
│   │   ├── Combat/            # 战斗状态机
│   │   ├── Characters/        # 角色/敌人基础状态
│   │   └── Map/               # Roguelike 地图节点
│   │
│   └── Godot/                 # 与引擎交互层
│       ├── Scenes/            # .tscn 场景文件
│       │   ├── Card.tscn
│       │   ├── Battle.tscn
│       │   └── MainMenu.tscn
│       ├── Scripts/           # 继承 Node 的 C# 脚本
│       │   ├── CardView.cs
│       │   ├── BattleManager.cs
│       │   └── HandArea.cs
│       └── Resources/         # .tres 数据配置
│           └── Cards/
│
├── assets/
│   ├── sprites/               # 像素图（角色、卡牌、UI）
│   │   ├── cards/
│   │   ├── characters/
│   │   └── ui/
│   ├── audio/                 # 音效与音乐
│   └── fonts/                 # 像素字体
│
└── docs-project/              # 本项目专属文档
    ├── ART_PIPELINE.md        # 美术资源制作流程
    ├── ARCHITECTURE.md        # 技术架构说明
    ├── TS_TO_CSHARP.md        # TS → C# 迁移速查
    └── NETWORK_PLAN.md        # 网络对战开发路线图
```

**分层原则**:
- `src/Core/` → 纯 .NET 类库，包含所有游戏规则逻辑，**不引用任何 Godot 命名空间**
- `src/Godot/` → 负责「把 Core 数据翻译成 Godot 节点」，处理输入、动画、渲染
- `docs/` → 从原项目同步的设计稿，**只读参考**，不在本项目中修改

---

## 🤖 AI 协作开发工作流

### 开发环境配置

1. **Godot 编辑器** → 场景搭建、节点编辑、运行调试
2. **VS Code / Cursor** → 代码编写（安装插件: C# Dev Kit + Godot Tools）
3. **Godot 外部编辑器设置**:
   ```
   编辑器 → 编辑器设置 → 文本编辑器 → 外部
   → 启用「使用外部编辑器」
   → 执行路径: /Applications/Cursor.app/Contents/MacOS/Cursor
   → 连接端口: 6005
   ```

### 与 AI 配合的 Prompt 模板

#### 场景 A: 根据设计文档生成 Core 逻辑
```
我正在开发一个 Godot 4 卡牌游戏，使用 C#。

以下是设计文档中的战斗规则：
[paste from docs/combat-flow.md]

请在 src/Core/Combat/ 下实现 CombatState 类，要求：
1. 使用状态机管理回合流程（PlayerTurn → EnemyTurn → EndRound）
2. 抽牌逻辑：从 Deck 抽 5 张，手牌上限 10
3. 能量系统：每回合重置为 3
4. 不引用任何 Godot 命名空间
5. 为每个 public 方法写单元测试友好的签名
```

#### 场景 B: TS 逻辑转 C#
```
以下是我原项目的 TypeScript 代码，请转换为 C#：
[paste TS code]

要求：
1. 保持原有类结构和逻辑不变
2. 使用 C# 属性 { get; set; } 替代 TS 的 public 字段
3. 使用 List<T> 替代 TS 数组
4. 接口名加 I 前缀（如 ICardEffect）
5. 添加适当的命名空间 MyGame.Core.Effects
```

#### 场景 C: 修复 Godot C# 脚本
```
以下 Godot C# 脚本报错：
[paste code + error message]

场景结构：
- 根节点: Control (Card.tscn)
- 子节点: TextureRect (Artwork), Label (NameLabel)

请修复问题并解释原因。
```

#### 场景 D: 生成 Godot 场景脚本
```
我有一个 Godot 场景文件：
[paste .tscn content]

请写一个配套的 C# 脚本，实现：
1. 鼠标悬停时放大 1.1 倍（Tween 动画）
2. 点击时发出 CardClicked 信号，携带卡牌 ID
3. 通过 [Export] 暴露 CardData 属性
```

### AI 辅助边界

| ✅ AI 擅长 | ❌ AI 不擅长 |
|---|---|
| TS → C# 语法翻译 | 设计游戏整体架构 |
| 写具体功能的脚本 | 调试复杂物理/渲染问题 |
| 解释报错和修复 Bug | 优化性能（需理解 Godot 渲染流程） |
| 生成样板代码（UI 布局、数据类） | 创意和玩法设计 |
| 根据 .tscn 写配套 C# 脚本 | 跨文件重构（需人工把关） |

---

## 🚀 快速开始

```bash
# 1. 克隆仓库
git clone <your-repo-url>
cd MyPixelCardGame

# 2. 同步设计稿（修改脚本中的路径后执行）
./sync_docs.sh /path/to/your-old-project

# 3. 用 Godot Mono 编辑器打开 project.godot
# 4. 在 VS Code 中打开项目根目录
# 5. 运行: dotnet build
```

---

## 📌 开发阶段规划

| 阶段 | 目标 | 网络 | 美术 |
|---|---|---|---|
| **Phase 1** | 单机可玩原型（1 职业 + 5 敌人） | 无 | 核心卡牌 + 1 个角色 |
| **Phase 2** | 本地双人（轮流操作验证逻辑） | 无 | 完整 UI + 特效 |
| **Phase 3** | Steam P2P 1v1 对战 | GodotSteam | 对手角色 + 表情 |
| **Phase 4** | 发售与内容迭代 | 维护 | 新职业/活动卡牌 |

---

## 🎨 美术风格锚点

- **分辨率**: 640×360 (16:9) → 整数倍放大到 1920×1080
- **卡牌立绘**: 128×192 像素
- **调色板**: 固定 32 色（见 ART_PIPELINE.md）
- **字体**: Pixelify Sans (Google Fonts, 免费商用)
- **渲染**: Viewport Stretch + Nearest Filter + 无抗锯齿

---

## 📄 文档索引

- [ART_PIPELINE.md](docs-project/ART_PIPELINE.md) — AI 像素美术生产流程
- [ARCHITECTURE.md](docs-project/ARCHITECTURE.md) — Core/Godot 分层架构
- [TS_TO_CSHARP.md](docs-project/TS_TO_CSHARP.md) — TypeScript → C# 概念映射
- [NETWORK_PLAN.md](docs-project/NETWORK_PLAN.md) — Steam P2P 接入路线图
