# AI 像素美术提示词优化指南

> 针对像素风卡牌/技能图标生成，解决「同角色换姿势」的单调问题。  
> 适用工具: Sprite AI, PixelLab, Midjourney, Leonardo 等。

---

## 1. 问题诊断: 为什么生成的图很单调?

**典型 Prompt 结构:**
```
[主体: The Fool] + [动作: Divination/灵视/飞牌] + [风格约束]
```

**AI 的解读逻辑:**  
> *"画一个巫师(The Fool)，让他做 XX 动作"*

**结果:** 无论技能怎么换，都是同一个人换姿势。

**根本原因:** 默认让 AI 画「完整人物 + 动作说明」，而卡牌/技能图的本质是**「技能本身的视觉化」**，不是角色立绘。

---

## 2. 解法: 5 种卡面视觉类型

打破"必须画完整人物"的惯性，根据技能特性选择**最合适的视觉表现形式**。

| 类型 | 核心思路 | 适合技能 | 效果 |
|:---:|---|---|---|
| **A. 现象特写** | 不画人，只画技能造成的"视觉奇观" | 灵视、预知、精神穿刺 | 神秘感强，留白多 |
| **B. 道具/符号** | 物品为主体，神秘学符号环绕 | 飞牌、符咒、仪式 | 符号化，易识别 |
| **C. 环境切片** | 展示技能作用后的空间变化 | 透视、开门、传送 | 沉浸感，有叙事性 |
| **D. 身体局部** | 只画眼睛/手/影子 | 灵视、暗杀、触碰 | 聚焦，情绪强烈 |
| **E. 第一人称(POV)** | 玩家视角看技能效果 | 占卜、窥秘、灵视 | 代入感最强 |

---

## 3. 具体优化示例

以下示例以《诡秘之主》风格的「占卜家」途径技能为原型，展示同一技能用不同视觉类型的差异。

---

### 🔮 灵视 (Spirit Vision)

#### 版本 A: 现象特写 — "第三只眼"
```
Pixel art skill card, 128x192, close-up of a glowing ethereal eye
floating in darkness, iris reflecting hidden ghostly figures,
mystical purple and silver light rays, limited 32-color palette,
thick black outline, no character body, no text, transparent background
```
> **效果:** 不画人，只画一只发光的灵界之眼，瞳孔里倒映着幽灵。神秘感和"看见不该看的东西"的情绪直接拉满。

#### 版本 B: 环境切片 — "透视的墙壁"
```
Pixel art skill card, 128x192, cross-section view of a brick wall
becoming transparent glass, revealing shadowy figures behind it,
blue ethereal glow seeping through cracks, limited 32-color palette,
thick black outline, no text, transparent background
```
> **效果:** 画墙壁被透视的过程，而不是画使用技能的人。玩家一看就知道这是"看穿隐藏"。

#### 版本 C: 身体局部 — "发光的眼眶"
```
Pixel art skill card, 128x192, extreme close-up of half a face
in shadow, single eye glowing with spiral pattern, dark victorian
atmosphere, limited 32-color palette, thick black outline,
dramatic lighting, no text, transparent background
```
> **效果:** 只画半张脸和一只螺旋状发光的眼睛，克苏鲁氛围浓厚。

#### 版本 D: 第一人称 POV — "灵界视角"
```
Pixel art skill card, 128x192, first-person view looking through
tinted glasses at a room overlaid with ghostly silhouettes and
floating runes, everything tinted purple, limited 32-color palette,
thick black outline, no text, transparent background
```
> **效果:** 玩家代入感最强，仿佛自己正在使用灵视。

---

### 🃏 飞牌 (Card Throw / Flying Card)

#### 版本 A: 道具特写 — "卡牌如刃"
```
Pixel art skill card, 128x192, a single playing card spinning
mid-air like a blade, motion blur trail, sharp metallic edges,
speed lines, limited 32-color palette, thick black outline,
dynamic diagonal composition, no text, transparent background
```
> **效果:** 主体是一张旋转的卡牌本身，像飞刀一样带速度线。不需要人物。

#### 版本 B: 现象特写 — "卡牌风暴"
```
Pixel art skill card, 128x192, vortex of flying cards swirling
in a tornado pattern, sharp edges glinting, dark background,
limited 32-color palette, thick black outline, no text,
transparent background
```
> **效果:** 画卡牌龙卷风，表现范围攻击或连续投掷。

#### 版本 C: 环境切片 — "划破空间的轨迹"
```
Pixel art skill card, 128x192, dark room with a single card
flying across leaving a glowing golden trail, sliced curtains
and floating debris showing its path, limited 32-color palette,
thick black outline, no text, transparent background
```
> **效果:** 画卡牌飞过后的破坏痕迹，用结果反推技能的凌厉。

---

### 🌫️ 纸人替身 (Paper Doll Substitute)

#### 版本 A: 道具特写
```
Pixel art skill card, 128x192, a crumpled paper doll with drawn
face lying on cobblestone, a shadowy figure fading away from it,
ethereal smoke rising, limited 32-color palette, thick black outline,
no text, transparent background
```

#### 版本 B: 身体局部 — "残影"
```
Pixel art skill card, 128x192, silhouette of a man dissolving
into paper fragments from the feet up, only the upper body remains
solid, dark alley background, limited 32-color palette,
thick black outline, no text, transparent background
```

---

### 🎭 无面人 (Faceless)

#### 版本 A: 身体局部
```
Pixel art skill card, 128x192, close-up of a face melting and
reforming, features shifting like liquid wax, blank white eyes,
limited 32-color palette, thick black outline, horror atmosphere,
no text, transparent background
```

#### 版本 B: 现象特写 — "多重倒影"
```
Pixel art skill card, 128x192, a standing figure reflected in
three cracked mirrors, each mirror showing a different face,
dark victorian dressing room, limited 32-color palette,
thick black outline, no text, transparent background
```

---

## 4. 通用增强词库

把这些词按需组合进 Prompt，大幅增加画面丰富度。

### 4.1 构图与视角

| 关键词 | 效果 |
|---|---|
| `extreme close-up` | 极端特写，只保留核心元素，聚焦感强 |
| `first-person POV` | 第一人称视角，沉浸感强 |
| `overhead view` | 俯视，适合法阵/地图/仪式类技能 |
| `silhouette against moonlight` | 月光剪影，神秘感，轮廓清晰 |
| `Dutch angle` | 倾斜构图，不安/动态/战斗感 |
| `symmetrical composition` | 对称构图，适合仪式/神圣/庄严感 |
| `off-center subject` | 主体偏离中心，留白，艺术感 |
| `rule of thirds` | 三分法构图，视觉平衡 |

### 4.2 光影与氛围 (诡秘之主/维多利亚适配)

| 关键词 | 效果 |
|---|---|
| `gaslight and shadows` | 煤气灯与阴影，维多利亚时代氛围 |
| `ethereal purple glow` | 灵界紫光芒，神秘学感 |
| `ethereal green mist` | 灵界绿雾，诡异/死亡感 |
| `candlelight flicker` | 烛光摇曳，温暖但不安 |
| `bioluminescent mist` | 生物发光雾气，克苏鲁/深海感 |
| `steam and gears` | 蒸汽与齿轮，蒸汽朋克元素 |
| `moonlight through fog` | 月光穿透雾气，清冷神秘 |
| `single spotlight` | 单束聚光灯，舞台感，聚焦主体 |

### 4.3 动作与动态

| 关键词 | 效果 |
|---|---|
| `motion blur trails` | 动态模糊轨迹，速度感 |
| `impact frames` | 冲击定格，打击感强烈 |
| `particles dispersing` | 粒子飞散，魔法消散 |
| `liquid dripping` | 液体滴落，诡异/腐蚀感 |
| `cracks spreading` | 裂纹蔓延，破坏/封印解除 |
| `sparks flying` | 火花飞溅，金属碰撞/电击 |
| `smoke billowing` | 浓烟翻滚，爆炸/火灾 |
| `freezing frost spreading` | 霜冻蔓延，冰系技能 |

### 4.4 材质与纹理

| 关键词 | 效果 |
|---|---|
| `weathered parchment` | 风化羊皮纸，古老/神秘学 |
| `polished obsidian` | 抛光黑曜石，深邃/反射 |
| `tarnished silver` | 氧化银器，复古/时间感 |
| `velvet fabric` | 天鹅绒布料，奢华/神秘 |
| `rusted iron chains` | 生锈铁链，囚禁/束缚感 |
| `crystalline structure` | 晶体结构，魔法/纯净 |

---

## 5. 可套用的模板公式

```
Pixel art skill card, 128x192,
[视觉类型: close-up of / silhouette of / vortex of / first-person view of],
[核心意象: 具体物体或现象描述],
[情绪氛围: mysterious / aggressive / ethereal / ominous / serene],
[光影: gaslight shadows / ethereal purple glow / candlelight flicker],
[构图: diagonal / symmetrical / off-center / extreme close-up],
[动态: motion blur trails / particles dispersing / cracks spreading],
limited 32-color palette, thick black outline, no text,
transparent background, pixel perfect
```

### 实战: 用模板生成 3 种不同风格的"灵视"

**神秘学符号版:**
```
... close-up of an ancient crystal ball showing swirling mist
and shadowy figures inside, mysterious, candlelight flicker,
symmetrical composition, particles dispersing, ...
```

**身体异变版:**
```
... silhouette of a figure with a third eye opening on forehead,
ethereal purple glow leaking out, ominous, off-center,
cracks spreading across skin, ...
```

**空间扭曲版:**
```
... first-person view looking through a rippling mirror-like
portal, distorted reflection, mysterious, bioluminescent mist,
Dutch angle, liquid dripping from frame edges, ...
```

---

## 6. 《诡秘之主》专属视觉符号系统

利用小说本身的设定，将抽象概念转化为具体视觉元素。

| 小说概念 | 视觉符号转化 | 适用技能 |
|---|---|---|
| **灵界** | 灰雾、半透明幽灵、扭曲空间、非欧几何建筑、漂浮的岛屿 | 灵视、通灵、灵界穿梭 |
| **占卜家途径** | 水晶球、灵摆、塔罗牌、羽毛笔自动书写、燃烧的黄水晶 | 占卜、预知、解梦 |
| **小丑途径** | 笑脸面具、纸人替身、杂技般的肢体扭曲、火焰跳跃 | 纸人替身、火焰跳跃、伤害转移 |
| **无面人** | 融化的面孔、空白面具、多重倒影、不断变换的五官 | 伪装、变形、模仿 |
| **秘偶大师** | 提线木偶、银色丝线、被控制的影子、关节反转的人偶 | 秘偶操控、灵体之线 |
| **诡法师** | 迷雾中的巨大身影、无数分身、历史迷雾、复活重生 | 复活、历史投影、迷雾 |
| **古代学者** | 泛黄的卷轴、沙漏、破碎的时钟、从历史中走出的幻影 | 历史投影、知识窃取 |
| **奇迹师** | 许愿池、流星、十二光点、命运的丝线交织 | 许愿、重启、命运 |
| **诡秘侍者** | 灰雾之上的王座、无数祈祷声、灵界深处的宫殿 | 建立秘偶城市、灵界支配 |
| **愚者** | 灰雾、神秘宫殿、光门、时之虫、命运木马 | 愚弄、嫁接、诡秘 |

### 使用技巧

**不要描述"角色在做什么"，而是描述"技能呈现出的超自然现象"。**

AI 画"现象"比画"人物做动作"丰富得多，而且更符合卡牌作为"技能载体"的本质——玩家看到的是**技能本身的视觉化**，不是角色摆 Pose。

---

## 7. 工作流建议

1. **定风格锚点**: 先用模板生成 3-5 个核心技能，每个技能用 2-3 种视觉类型各出一张图。
2. **人工筛选**: 挑选最符合氛围的那张，锁定为该类技能的风格模板。
3. **批量生产**: 对同类型技能复用已验证的 Prompt 结构，只改核心意象描述。
4. **质量检查**: 所有 AI 出图必须经过 Aseprite 清理（调色板量化、描边补全、去杂散像素）。
5. **命名规范**: `skill_[途径]_[技能名]_[视觉类型缩写]_[尺寸].png`
   - 例: `skill_fool_spiritvision_closeup_128x192.png`

---

## 8. 快速参考卡

```
单调? → 不画完整人物 → 选 5 种视觉类型之一
没氛围? → 加光影词: gaslight / ethereal glow / candlelight
没动感? → 加动态词: motion blur / particles / cracks
没辨识度? → 加小说符号: 水晶球 / 纸人 / 面具 / 丝线
```
