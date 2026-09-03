# 技术架构说明

## 核心原则

**Godot 节点只负责视觉表现，所有游戏逻辑在纯 C# Core 层运行。**  
（参考: Slay the Spire 2 的 Godot + C# 架构）

---

## 分层架构

```
┌─────────────────────────────────────┐
│         Godot 引擎层                │
│  (Node2D, Control, Sprite2D...)    │
│                                     │
│  src/Godot/                         │
│  ├── Scenes/      (.tscn 场景)     │
│  ├── Scripts/     (继承 Node 的 C#) │
│  └── Resources/   (.tres 配置)     │
└──────────────┬──────────────────────┘
               │ 数据传递 (DTO/事件)
               ▼
┌─────────────────────────────────────┐
│         Core 逻辑层                 │
│  (纯 .NET, 不引用 Godot)           │
│                                     │
│  src/Core/                          │
│  ├── Cards/                         │
│  ├── Effects/                       │
│  ├── Combat/                        │
│  ├── Characters/                    │
│  └── Map/                           │
└─────────────────────────────────────┘
```

### Core 层设计约束

1. **零 Godot 依赖**: `src/Core/` 下的任何文件都不能 `using Godot;`
2. **可单元测试**: 能在普通 .NET 控制台项目里跑测试
3. **纯函数优先**: 状态变更通过返回新对象实现，便于网络同步
4. **序列化友好**: 所有状态类支持 JSON 序列化（为网络对战做准备）

### Godot 层职责

1. **输入翻译**: 把玩家点击/拖拽翻译成 Core 层的 Action 对象
2. **状态渲染**: 把 Core 层的 GameState 翻译成场景节点变化
3. **动画调度**: Tween、粒子、Shader 效果，但不参与逻辑判断
4. **资源管理**: 加载 .tres 配置，实例化场景

---

## 数据流示例 (出牌流程)

```
玩家点击卡牌
    │
    ▼
CardView.cs (Godot 层)
    │  验证: 是否玩家回合? 能量是否足够?
    ▼
生成 PlayCardAction { CardId, TargetId }
    │
    ▼
BattleManager.cs (Godot 层)
    │  调用 Core.CombatState.ProcessAction(action)
    ▼
CombatState.cs (Core 层)
    │  纯逻辑计算:
    │  - 扣除能量
    │  - 执行卡牌效果
    │  - 检查敌人死亡
    │  - 生成新 GameState
    ▼
返回 GameState (新状态对象)
    │
    ▼
BattleManager.cs 接收新状态
    │  更新 Godot 节点:
    │  - 敌人 HP 标签
    │  - 播放伤害动画
    │  - 手牌区移除已打出卡牌
    ▼
视觉效果呈现给玩家
```

---

## 关键接口设计

### ICardEffect (效果系统)

```csharp
// src/Core/Effects/ICardEffect.cs
namespace MyGame.Core.Effects;

public interface ICardEffect {
    string Description { get; }           // 用于 UI 显示
    void Apply(EffectContext ctx);        // 执行效果
}

public class EffectContext {
    public Character Source { get; set; }
    public Character Target { get; set; }
    public CombatState Combat { get; set; }
}
```

### CombatState (战斗状态机)

```csharp
// src/Core/Combat/CombatState.cs
namespace MyGame.Core.Combat;

public class CombatState {
    public TurnPhase Phase { get; private set; }
    public Player Player { get; private set; }
    public List<Enemy> Enemies { get; private set; }
    public int TurnNumber { get; private set; }

    // 纯函数: 接收 Action，返回新状态
    public CombatState ProcessAction(PlayerAction action) {
        // ... 逻辑计算 ...
        return new CombatState { /* 新状态 */ };
    }
}
```

---

## 网络对战预留设计

Phase 3 接入 Steam P2P 时，架构不需要大改：

```
单机模式:
  Input → Core.ProcessAction → New State → Godot 渲染

网络模式 (Host):
  Client Input (via Steam P2P) → Core.ProcessAction → New State → Broadcast → Godot 渲染

网络模式 (Client):
  Local Input → Send to Host → Wait for State Sync → Godot 渲染
```

**关键**: Core 层完全不变，只在 Godot 层增加网络收发逻辑。
