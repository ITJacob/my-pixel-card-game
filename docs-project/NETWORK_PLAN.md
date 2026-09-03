# 网络对战开发路线图

> **当前阶段**: 仅做架构预留，不实现。  
> **目标**: Phase 3 (第 4 个月) 接入 Steam P2P 1v1 对战。

---

## 技术选型

| 方案 | 选择 | 理由 |
|---|---|---|
| 网络库 | **GodotSteam + Steam P2P** | 免费中继、NAT 穿透、杀戮尖塔 2 同款 |
| 架构 | **Host-Client (权威服务器)** | Host 运行 Core 逻辑，Client 只发输入收状态 |
| 序列化 | **JSON** | 卡牌游戏数据量小，JSON 可读性好，调试方便 |
| 同步频率 | **事件驱动** | 回合制不需要每帧同步，只在状态变化时发送 |

---

## 开发阶段

### Phase 1: 单机原型 (现在 - 第 2 个月)

**目标**: 1 职业 + 5 敌人，完整战斗循环

**网络相关工作**:
- [ ] Core 层设计成「输入 → 状态更新 → 渲染」的纯函数式结构
- [ ] 所有状态变更返回新对象（便于未来网络广播）
- [ ] 定义 `PlayerAction` 消息基类（为 P2P 消息预留）

**不做**:
- 任何网络代码
- 任何 Steam API 调用

---

### Phase 2: 本地双人 (第 3 个月)

**目标**: 同一台电脑两人轮流操作，验证 Core 逻辑无 Bug

**网络相关工作**:
- [ ] 抽象出 `IInputProvider` 接口
  ```csharp
  public interface IInputProvider {
      PlayerAction GetAction();
  }
  ```
- [ ] 实现 `LocalInputProvider`（本地玩家）
- [ ] 实现 `AIInputProvider`（机器人对手，用于测试）
- [ ] 验证 Core 层能处理「远程输入」而不感知来源

**不做**:
- 网络连接
- 多进程/多线程

---

### Phase 3: Steam P2P 接入 (第 4 个月)

**目标**: 两个玩家通过 Steam 匹配、进房间、完成一局对战

**实现清单**:

1. **接入 GodotSteam**
   - [ ] 下载 GodotSteam C# 兼容版本
   - [ ] 初始化 Steam (AppID 480 用于测试)
   - [ ] 实现创建 Lobby / 加入 Lobby / 搜索 Lobby

2. **P2P 连接**
   - [ ] 接受 P2P Session 请求
   - [ ] 建立双向数据通道
   - [ ] 心跳检测与断线重连

3. **消息协议**
   - [ ] 定义 `GameMessage` 基类
   - [ ] 实现 `PlayCardPayload`, `GameStateSync`, `TurnChange`
   - [ ] JSON 序列化/反序列化

4. **Host 权威逻辑**
   - [ ] Host 接收 Client 的 `PlayerAction`
   - [ ] Host 在 Core 层执行逻辑
   - [ ] Host 生成过滤后的 `GameState` 广播给双方
   - [ ] **手牌隐私**: Host 只发送玩家自己的手牌内容，对手只显示手牌数量

5. **Client 表现**
   - [ ] 发送本地输入到 Host
   - [ ] 接收状态同步并更新 Godot 节点
   - [ ] 等待 Host 确认期间显示「等待中」UI

---

### Phase 4: 发售与迭代 (第 5 个月+)

**目标**: 上 Steam，持续更新内容

**网络相关优化**:
- [ ] 断线重连机制（战斗中掉线可恢复）
- [ ] 投降/退出处理
- [ ] 排行榜与成就 (Steamworks)
- [ ] 如有竞技需求，考虑 Headless Dedicated Server

---

## 消息协议设计 (预留)

```csharp
public enum MessageType {
    PlayerAction,       // Client → Host: 玩家操作
    GameStateSync,      // Host → Client: 状态同步
    TurnChange,         // Host → Client: 回合切换
    CombatResult,       // Host → Client: 战斗结算详情
    Emote,              // 双向: 表情
    Surrender,          // Client → Host: 投降
    Ping,               // 双向: 心跳
}

public class GameMessage {
    public MessageType Type { get; set; }
    public JsonElement Payload { get; set; }
    public long Timestamp { get; set; }
}

// 出牌动作
public class PlayCardPayload {
    public string CardId { get; set; }
    public string TargetId { get; set; }
    public int TargetIndex { get; set; }
}
```

---

## 防作弊策略

| 阶段 | 策略 |
|---|---|
| 初期 | 信任 Host，依赖 Steam 举报系统 |
| 后期 (如有排位) | 核心逻辑迁移到 Headless Godot Server，Steam Game Server API 认证 |

**注意**: 独立游戏 1v1 休闲对战的作弊问题通常不严重，不要过早优化。
