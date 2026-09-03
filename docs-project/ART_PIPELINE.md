# 美术资源制作流程 (Art Pipeline)

> **核心原则**: 70% AI 生成概念 → 30% Aseprite 清理标准化  
> **风格定调先于生产**: 调色板/尺寸/描边/光源一旦确定，全程不变

---

## 1. 风格宪法（不可更改）

```
分辨率基准:
  - 卡牌立绘: 128×192 像素 (竖版)
  - 角色头像: 64×64 像素
  - 敌人 sprite: 96×96 像素
  - UI 图标: 16×16 像素
  - 战斗背景: 640×360 像素

网格与像素:
  - 严格对齐 1px 网格
  - 禁止抗锯齿 (Nearest Neighbor 唯一缩放方式)
  - 所有精灵边缘必须是硬边

调色板 (固定 32 色):
  - 主色 8 色 + 辅色 8 色 + 高光 8 色 + 阴影 8 色
  - 推荐预设: Lospec "Fantasy 32" 或 "Sweetie 16"
  - 所有 AI 生成图必须量化到此调色板

描边规则:
  - 所有角色/道具外轮廓: 1px 纯黑 (#000000) 描边
  - UI 元素外轮廓: 1px 深色描边 (非纯黑)

光源方向:
  - 统一: 左上 45°
  - 角色面部/装备高光必须在左上

风格关键词 (用于所有 AI Prompt):
  "16-bit RPG, thick readable silhouette, limited 32-color palette,
   1px black outline, top-left lighting, no anti-alias, pixel perfect"
```

---

## 2. AI 工具选择

| 工具 | 用途 | 备注 |
|---|---|---|
| **Sprite AI** | 角色立绘、道具图标 | 原生像素尺寸控制，直接生成像素网格 |
| **PixelLab** | 同风格批量变体 | 锁定调色板后生成系列图 |
| **Midjourney/Leonardo** | 概念参考图 | 仅用于 Phase 1 定风格，不直接用于生产 |
| **Aseprite** | 清理、调色板量化、修描边 | 行业标准，$20 一次性 |
| **LibreSprite** | Aseprite 免费替代品 | 功能略少但够用 |

---

## 3. 生产流程（单张卡牌）

```
Step 1: 概念生成 (AI)
  └─ Prompt 模板:
     "Pixel art trading card, 128x192, [具体内容描述],
      limited 32-color palette, thick black outline, top-left light,
      16-bit RPG style, no text, transparent background, pixel perfect"
  └─ 生成 4-8 张变体
  └─ 人工挑选 1 张最接近风格的

Step 2: 清理标准化 (Aseprite)
  ├─ 导入图片
  ├─ 调整画布到严格 128×192
  ├─ 量化到 32 色调色板 (Image → Color Mode → Indexed)
  ├─ 检查并补全 1px 黑色外描边
  ├─ 检查光源方向一致性
  ├─ 去除杂散像素 (孤立像素清理)
  └─ 导出为 PNG (透明背景)

Step 3: 质量检查清单
  ├─ [ ] 尺寸严格等于 128×192? (不是近似)
  ├─ [ ] 颜色数 ≤ 32? (用 Aseprite 调色板视图确认)
  ├─ [ ] 外轮廓有 1px 纯黑描边?
  ├─ [ ] 无抗锯齿模糊像素? (放大 800% 检查)
  ├─ [ ] 背景已去底? (透明 PNG)
  ├─ [ ] 光源方向正确? (左上 45°)
  └─ [ ] 命名规范: card_[类型]_[名称]_[尺寸].png

Step 4: 导入 Godot
  ├─ 拖入 assets/sprites/cards/
  ├─ 选中 → 导入面板设置:
  │   Filter: Nearest
  │   Repeat: Disabled
  │   Mipmaps: Disable
  └─ 点击「重新导入」
```

---

## 4. 资产优先级清单

### Tier 1: 核心战斗 (先做这些，游戏就能跑)

| 资产 | 尺寸 | 数量 | 生成策略 |
|---|---|---|---|
| 玩家角色立绘 | 128×192 | 1 | AI 生成 → Aseprite 清理 |
| 基础攻击牌 | 128×192 | 1 | 同上 |
| 基础防御牌 | 128×192 | 1 | 同上 |
| 第一个敌人 | 96×96 | 1 | 同上 |
| 战斗背景 | 640×360 | 1 | AI 生成场景，可略宽松 |

### Tier 2: UI 框架 (游戏可玩后补充)

| 资产 | 策略 |
|---|---|
| 卡牌底板/边框 | Aseprite 手绘 1 张 32×48 模板 → Godot 9-slice 拉伸适配所有尺寸 |
| 按钮、血条、能量球 | AI 生成概念 → Aseprite 画成 9-patch → Godot 拉伸 |
| 字体 | **不用 AI 生成!** 使用 Pixelify Sans (免费商用) |
| Buff/Debuff 图标 | AI 生成 16×16 静态小图标 |

### Tier 3: 扩展内容 (发售后迭代)

| 资产 | 策略 |
|---|---|
| 新职业角色 | 复用 Tier 1 的 Prompt 模板，只改描述 |
| 新敌人 | 批量生成时锁定同一风格参考图 |
| 新卡牌 | 复用同一底板，只换中间插画 |

---

## 5. 特效策略 (不用 AI 动画!)

像素风特效**禁止**用 AI 生成逐帧动画（帧间会抖动、风格漂移）。
改用以下 Godot 内置方案：

| 效果 | 实现方式 |
|---|---|
| 攻击轨迹 | Tween 移动卡牌 + ParticleSystem2D 拖尾 |
| 受伤闪白 | Shader: sprite 叠加白色，透明度闪烁 |
| 伤害数字 | Label + Tween 向上飘移 + 透明度渐变 |
| 卡牌打出光效 | 粒子爆发 (1-2 帧的闪光纹理) |
| 屏幕震动 | Camera2D 的 Shake 脚本 |
| Buff 光环 | 旋转的半透明精灵 + Tween 循环 |

---

## 6. 批量处理脚本

### Python 自动化后处理 (Pillow)

保存为 `tools/process_pixel_art.py`:

```python
from PIL import Image
import sys
from pathlib import Path

PALETTE_32 = [
    (26, 28, 44),    (93, 39, 93),    (177, 62, 83),   (239, 125, 87),
    (255, 205, 117), (113, 170, 52),  (52, 101, 36),   (44, 62, 80),
    # ... 补全你的 32 色
]

def quantize_to_palette(image, palette):
    """将图片量化到指定调色板"""
    flat_palette = [c for color in palette for c in color]
    flat_palette += [0] * (768 - len(flat_palette))  # 补到 256*3

    p_img = Image.new('P', (1, 1))
    p_img.putpalette(flat_palette)

    return image.quantize(palette=p_img)

def process_card(input_path, output_path, target_size=(128, 192)):
    img = Image.open(input_path).convert('RGB')

    # 1. 调整到目标尺寸 (Nearest = 硬边)
    img = img.resize(target_size, Image.NEAREST)

    # 2. 量化到 32 色
    img = quantize_to_palette(img, PALETTE_32)

    # 3. 保存
    img.save(output_path, 'PNG')
    print(f"✅ 处理完成: {output_path}")

if __name__ == "__main__":
    input_dir = Path("assets/sprites/cards/raw")
    output_dir = Path("assets/sprites/cards")
    output_dir.mkdir(parents=True, exist_ok=True)

    for img_path in input_dir.glob("*.png"):
        process_card(img_path, output_dir / img_path.name)
```

---

## 7. 免费资源速查

- **Lospec** (lospec.com/palette-list) — 像素调色板库
- **Pixelify Sans** (fonts.google.com) — 免费像素字体
- **OpenGameArt** (opengameart.org) — 免费像素素材参考
- **Aseprite** (aseprite.org) — 像素编辑器 ($20)
- **LibreSprite** (libresprite.github.io) — 免费替代品
