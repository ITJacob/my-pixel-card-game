# TypeScript → C# 迁移速查表

> 两者都由 Anders Hejlsberg 设计，语法相似度 > 80%。迁移主要是「翻译」而非「重写」。

---

## 基础类型对照

| TypeScript | C# | 说明 |
|---|---|---|
| `number` | `int`, `float`, `double` | C# 数字类型更细分 |
| `string` | `string` | 完全一样 |
| `boolean` | `bool` | 名字不同 |
| `any` | `object` 或避免使用 | C# 强类型，尽量不用 |
| `undefined` | `null` (可空类型 `T?`) | C# 8.0+ 可空引用类型 |
| `Array<T>` / `T[]` | `List<T>` / `T[]` | 推荐 `List<T>` |
| `Record<K, V>` | `Dictionary<K, V>` | 键值对 |
| `Set<T>` | `HashSet<T>` | 唯一集合 |
| `Map<K, V>` | `Dictionary<K, V>` | 字典/映射 |
| `Date` | `DateTime` | 日期时间 |

---

## 语法对照

### 变量声明

```typescript
// TS
let count: number = 0;
const name: string = "Strike";
let maybe: number | null = null;
```

```csharp
// C#
int count = 0;
const string Name = "Strike";      // const 必须编译期确定
int? maybe = null;                  // 可空类型
```

### 类与接口

```typescript
// TS
interface ICard {
    name: string;
    cost: number;
    play(target: Character): void;
}

class Strike implements ICard {
    name = "Strike";
    cost = 1;

    play(target: Character): void {
        target.takeDamage(6);
    }
}
```

```csharp
// C#
public interface ICard {
    string Name { get; }
    int Cost { get; }
    void Play(Character target);
}

public class Strike : ICard {       // : 同时表示 extends 和 implements
    public string Name => "Strike";
    public int Cost => 1;

    public void Play(Character target) {
        target.TakeDamage(6);
    }
}
```

### 属性 (Getter/Setter)

```typescript
// TS
class Player {
    private _health: number = 100;

    get health(): number {
        return this._health;
    }

    set health(value: number) {
        this._health = Math.max(0, value);
    }
}
```

```csharp
// C#
public class Player {
    private int _health = 100;

    public int Health {
        get => _health;
        set => _health = Math.Max(0, value);
    }
}

// 或自动属性 (简单场景)
public int Health { get; set; } = 100;
```

### 异步编程

```typescript
// TS
async function loadDeck(): Promise<Card[]> {
    const res = await fetch('/api/deck');
    return res.json();
}

const [deck, enemies] = await Promise.all([
    loadDeck(), loadEnemies()
]);
```

```csharp
// C#
public async Task<List<Card>> LoadDeck() {
    var res = await _httpClient.GetAsync("/api/deck");
    return await res.Content.ReadFromJsonAsync<List<Card>>();
}

var results = await Task.WhenAll(LoadDeck(), LoadEnemies());
```

### 函数式操作 (LINQ)

```typescript
// TS
const expensive = deck
    .filter(c => c.cost > 2)
    .map(c => c.name)
    .reduce((sum, c) => sum + c.length, 0);
```

```csharp
// C# (using System.Linq)
var expensive = deck
    .Where(c => c.Cost > 2)           // filter
    .Select(c => c.Name)              // map
    .Sum(c => c.Length);              // reduce (特定场景)

// 通用 reduce → Aggregate
var total = deck
    .Select(c => c.Name)
    .Aggregate(0, (sum, name) => sum + name.Length);
```

**LINQ 速查**:

| TS | C# LINQ |
|---|---|
| `.map()` | `.Select()` |
| `.filter()` | `.Where()` |
| `.find()` | `.FirstOrDefault()` |
| `.reduce()` | `.Aggregate()` |
| `.some()` | `.Any()` |
| `.every()` | `.All()` |
| `.sort()` | `.OrderBy()` |
| `.includes()` | `.Contains()` |

### 模块导入

```typescript
// TS
import { Character } from './Character';
export class Player { ... }
```

```csharp
// C#
using MyGame.Core.Characters;    // 按命名空间导入，不按文件路径

namespace MyGame.Core {          // 文件通常只放一个类
    public class Player { ... }
}
```

---

## Godot C# 特有 API

| GDScript / TS 概念 | Godot C# | 说明 |
|---|---|---|
| `extends Node2D` | `public partial class MyNode : Node2D` | 必须加 `partial` |
| `@export var speed` | `[Export] public float Speed { get; set; }` | 特性语法 |
| `@onready var sprite = $Sprite2D` | `GetNode<Sprite2D>("Sprite2D")` | 无 `$` 语法糖 |
| `func _ready()` | `public override void _Ready()` | PascalCase + override |
| `func _process(delta)` | `public override void _Process(double delta)` | `double` 非 `float` |
| `signal player_died` | `[Signal] public delegate void PlayerDiedEventHandler()` | 事件委托 |
| `emit_signal(...)` | `EmitSignal(SignalName.PlayerDied)` | 类型安全 |
| `connect(...)` | `Pressed += OnPressed` | C# 事件订阅 |

---

## 常见陷阱

1. **访问修饰符**: C# 默认 `private`，必须显式写 `public`
2. **空值检查**: C# 8.0+ 启用可空引用类型后，`string?` 和 `string` 会被编译器区分
3. **值类型 vs 引用类型**: `struct` (值) 和 `class` (引用) 行为不同，注意拷贝语义
4. **字符串插值**: TS `` `Hello ${name}` `` → C# `$"Hello {name}"`
5. **相等判断**: TS `===` → C# `==` (值类型) 或 `ReferenceEquals()` (引用类型)
