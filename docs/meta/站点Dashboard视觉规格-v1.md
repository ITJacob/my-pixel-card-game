# 站点 Dashboard 视觉规格 · v1（架构同步版 · 2026-11-20）

> **架构变更记要**：本规格原按「6 张概念卡导航盘 → 6 个详情页」撰写。主人裁定改为**单页就地展开 + 互斥手风琴**：6 个概念全部内联在 `rules/战场玩法.html` 一页，`<details name="concept">` 原生互斥、同时只开一个；6 个详情页与返回条／面包屑已撤销。下文涉及架构的条目已逐项同步，视觉方向（深炭 60/30/10、radius 8、纸卡图解保留浅米、零横滑、safe-area）不变。对应实现见 `docs/tools/build_wiki.py` 的 `CSS` 与 `build_dashboard()`；本次只同步文档，未新建 v2，避免留两份互相冲突的规格。

## 一、风格定位
- 风格锚点：深炭面板里的「图纸柜抽屉标签」——等权折叠抽屉；不像游戏主菜单，不像稀有度卡面。
- 形状语言：新增元素统一圆角矩形 radius 8，禁圆形按钮 / 尖角标签 / 硬边切角；纸卡 figure 的 radius 10 与 SVG 内 rx 属纸卡载体、被容器边界隔离，不计入 UI 形状语言，也不得反向外溢。
- 色彩预算 60/30/10：主色深炭 60%（--bg #16181d / --panel #1d2026）；辅色中性灰阶 30%（--line #2c313a / --fg #d7dae0 / --mut #8b919c）；点缀 10% = 琥珀 --ac #e0a94e + 石板蓝 --ac2 #7fb4d8 合计，点缀超 15% 即画面吵、主色低于 50% 即失去基调。
- 琥珀/石板蓝分工（已按两层抽屉重划）：琥珀只给 h1、外层抽屉 `[open]` 态的 '▾'／概念名／2px 底线、内层 `details.concept>summary`；石板蓝只给抽屉内 `h3`、「完整原文→」链接与 `.concept-ref h3`。**折叠态 summary 全灰阶、无点缀色**；展开体内两种点缀不并列——琥珀只在抽屉标签层，石板蓝只在内容层。已无卡序号 01–06（6 概念并列非序列）、无返回链接、无面包屑、无详情页 h2/h3。
- 禁止项：① SVG 纸卡的红 #8c2f2f / 绿 #3f6b52 / 黄铜 #a87c3c 不得外溢到深炭 UI；② 禁 .r-* 稀有度色 / .badge / 渐变 / 半透明米色叠加 / 浅色投影进入本页；③ 禁跳转式返回条、面包屑、悬浮圆形返回按钮与概念间「上一/下一」翻页（详情页已撤销）；④ 6 抽屉之外仅允许「未定」缺口小节，且不得长得像第 7 张卡：无卡片底 / 无边框 / 无序号 / 无琥珀 / 无石板蓝，14px --mut 标题 + 12.5px --mut 正文 + 上 1px --line 分隔、距第 6 抽屉 ≥24px；其余入口、分组标题、说明块一律禁。
- 口径：按 CSS px / 375pt 视口，不套 1080p 游戏 UI 的 24px 基准；正文 ≥14px，摘要 / 图注 / 元数据 ≥12.5px 且不得承载唯一信息。
## 二、首屏与密度（375×812 硬断言）
- **6 个概念抽屉必须在首屏一屏内全部可见**（默认全折叠、无需滚动、无需展开）——否则首屏退化成长列表，dashboard 失效。本规格最关键一条。展开后内容就地追加，`name="concept"` 保证同时只开一个，页面不会叠成 6 份长卷。
- 首屏自上而下：状态栏安全区 → sticky 侧栏约 65px → h1 22px + 一行引导语 13px → 6 抽屉单列（首屏内全见）→「未定」次级文本小节；6 概念平级无主次，抽屉 summary 单行横排：'▸' 箭头 14px（最左）/ 概念名 17px 600 / 右对齐元数据 12.5px「概要 N 条 · 正源 N 处」，层级只由字号与位置建立，不靠颜色；**不编号**。
- 灰度测试：去色后仍读出「h1 > 概念名 > 元数据 > 箭头」四级明度；6 抽屉填黑后剪影完全一致 = 等权，不得靠配色把某张做成「推荐」，「未定」小节去色后不得读作第 7 个矩形卡；截图缩到 50% 仍须读出概念名。展开态靠箭头形状（▸/▾）+ 2px 底线 + 明度差异辨识，不只靠颜色。
## 三、抽屉尺寸与触摸目标
| 项 | 数值 |
|---|---|
| 网格 | `.concept-grid` 1 列 × 6 行，gap 8px；375px 下内容宽 335（左右 20×2），抽屉宽 335px |
| 抽屉高 | `details.drawer>summary` min-height 56px 单行信息条、内容不撑破；整条 `<summary>` 即点击区 ≈56×335px（≥44px 下限）；抽屉间 gap 8px 恰为误触缝下限，不得再小 |
| summary 内 | padding 10px 14px（移动端 10px 12px），flex-row / flex-wrap / align-center；箭头 14px --mut（最左）→ 概念名 17px 600 --fg（`min-width:0` 不撑破 335px）→ 元数据 12.5px --mut 右对齐；`details.drawer` 自带 --panel 底 / --line 边 / radius 8，不另设色 |
| 间距与触摸 | 网格距 h1 16px；6 抽屉下沿 ≤ 首屏可用高 −24px；所有可点元素 min-height 44px（56px 外层 summary 与 44px 内层 summary 满足）；`:hover/:active` 仅换背景 --line #2c313a，无位移 / 缩放 / 阴影 / 动画 |
| 互斥 | 6 个 `<details class="drawer" name="concept">` 共用 name，浏览器原生手风琴：点开新的自动收起旧的，无 JS、无跳转；内层 26 个 `details.concept` 不设 name，可多开 |
| 断言 | 6×56 + 5×8 + h1 38 + 引导 23 + 网格距 16 + main padding-top 16 ≈469px，+ aside 65 + safe-top 44 ≈578px < 首屏可用 778px（812 − home 34），6 抽屉一屏全见成立、余量 ≈200px。2026-11-20 实测折叠态 `asideH=65 / summaryH=56 / open=0 / scrollW=375 = clientW` |
## 四、抽屉内部：就地展开与图解
- **已无详情页**：`rules/concepts/*.html` 6 页、`main.concept-page`、sticky 返回条「← 战场玩法」、面包屑「战场玩法 / 01 场地」与 `top:calc(61px + env(safe-area-inset-top))` 规则一并撤销；所有内容内联在 `rules/战场玩法.html`，阅读路径零跳转，也不再需要滚动位置恢复。
- 抽屉内顺序固定「极简概要 → 图解 → DDD 正源（逐节折叠）」：概要走 `site/dashboard.md` 切片，图解走 `site/figures.html` 按概念名映射，正源由 `site/concept-map.json` 26 个锚点在构建期切片注入。
- 图解**沿用浅米纸卡**，SVG 保持原字节：`figure.diagram` 保留 #f3eee3 底 / #d8d0be 边 / radius 10 / figcaption #6c6357，一字不改；约 60 处硬编码 fill/stroke 深色化会与 `site/figures.html` 图源分叉成两套矢量，禁止。
- 不打架靠**空间隔离 + 明度硬断层**：折叠态首屏 0 张米色；米卡只出现在展开抽屉内；米底 L≈93 与深炭 L≈9 直接硬边相接，中间禁任何过渡色；抽屉内 padding 12–14px 叠加 main 20px，纸卡左右 ≥32px 深炭留白，不得贴齐屏幕边；figcaption 仍留在纸卡内。
- 手机只渲染 `svg.tall`、`width:100%;height:auto`；≥761px 显示宽版。单位概念正源无图 → **缺失 / 未接线**，禁挪用其它概念图或临时补画（保持 5 张图源唯一出处）。
## 五、折叠展开与零横滑 / safe-area
- 两层原生 `<details>`、**默认全折叠**：外层 6 个 `details.drawer[name="concept"]` 互斥（同时只开一个），内层每抽屉按正源章节分块共 26 个 `details.concept`（可多开）。26 锚点由 `site/concept-map.json` / `concept_map.py` 注入，不新增 JS（离线仅内联展开内容可读，原文下钻页首访需联网）。
- 折叠态 summary ≥44px（外层实测 56px、内层 44px）、`::before '▸'` --mut；展开态 '▾' 转 --ac + summary 底 2px --ac 线 + 概念名转 --ac，`.drawer-body` 背景降一档至 #191c21（既有色板，不新增色）——状态差异靠箭头形状 + 明度 + 2px 线，不只靠颜色。展开区正源原文保留日期括注与 INV 编号、13.5px，表格 `table-layout:fixed` 12px + `overflow-wrap:anywhere`。
- 零横滑：断言页面级 `documentElement.scrollWidth ≤ clientWidth`（实测折叠态与展开态均 375/375）；禁固定 px `min-width` / `white-space:nowrap` / 页面级横滑；svg 全部 `max-width:100%`；表格容器 `overflow-x:auto` 允许保留（其余 95 页卡表兼容），但 `.concept-ref table` 必须 `display:table;table-layout:fixed` + `overflow-wrap:anywhere`，375px 下不得溢出；`.ref-head` 的 flex-wrap 保留。
- safe-area：`viewport-fit=cover` 与左右 / 底部 inset 保留；`aside` 已补 `padding-top:calc(10px + env(safe-area-inset-top))`（PWA 状态栏不再压住 sticky 导航）；用 `.dashboard` 局部类把 main 左右 padding 提到 20px（≥375×5%=18.75px），不动全局 14px；`.concept-page` 随详情页一并删除。
## 六、CSS 留 / 删 / 改
| 判定 | 规则与接线点 |
|---|---|
| 留 | :root 六色变量（唯一色源）；aside / .nav-toggle / .nav-inner 移动端 sticky + 44px + inset；`figure.diagram` 三条；`details.concept` 全组；`.concept-ref` / `.ref-head`；`main{min-width:0}` / `overflow-wrap:anywhere` / `-webkit-text-size-adjust:100%`；blockquote 3px --ac 左边框；`.grid` / `.card` 留给其余 95 页（全站 96 页含 dashboard） |
| 留（偏差） | 全局 `table{display:block;overflow-x:auto}` 保留，删它会波及 95 页卡表、风险大于收益；`.concept-ref table` 的 `display:table;table-layout:fixed` 选择器优先级更高、不得被覆盖；验收只以页面级 `scrollWidth` 断言为准，不以删该规则为准 |
| 改 | 新增 `.dashboard` / `.concept-grid` / `details.drawer` + `.drawer-name` / `.drawer-meta` / `.drawer-body` / `.ref-list-head` / `.dash-gap` / `.concept-summary`；**不得复用 `.grid`**——须独立控制列数、8px gap 与 56px 抽屉高，不被其余 95 页的 `auto-fill minmax(220px,1fr)` 与 @media 规则带偏；@media 内显式给 `.concept-grid` 保 1 列，`figure.diagram` 与 `svg.tall` 切换规则原样保留供抽屉内复用；改动一律落 `docs/tools/build_wiki.py` 内联样式表，直改 `_site/style.css` 会在下次 push 被全量覆盖 |
| 删 | `.concept-card` / `.back-link` / `.crumb` / `.concept-page` 四组旧类及 `CONCEPTS_DIR` / `CONCEPT_SLUGS` / `concept_slug()` / `build_concept_page()` / `concept_paths` 全部清零；构建期断言 `rules/concepts/` 目录不存在 |
## 七、三列对照（规格项 | 资产文件 | 接线点）
| 规格项 | 资产文件 | 接线点 |
|---|---|---|
| 6 个概念抽屉（互斥） | `_site/rules/战场玩法.html`（生成自 `docs/tools/build_wiki.py`） | `details.drawer[name="concept"]` + `.concept-grid` 单列；`.drawer-name` 概念名 / `.drawer-meta`「概要 N 条 · 正源 N 处」 |
| 6 个详情页 | **已撤销**，`rules/concepts/` 不存在 | 验收断言目录不存在；`sw_core()` 不再派生详情页 URL |
| 5 张图解（宽+竖双版） | `site/figures.html`（图源，SVG 原字节） | `load_figures()` 按「概念名 → figure」显式映射，禁游标顺序消费（否则 6 抽屉全拿场地图）；`figure.diagram` / `svg.tall` 媒体切换 |
| 单位概念图解 | **缺失** | **未接线**：单位抽屉恒 0 图、不 fallback，禁挪用 / 补画 |
| 26 个正源折叠块 | `site/concept-map.json` + `docs/tools/concept_map.py` | 构建期 `slice_section()` 切片内联；每抽屉 `details.concept` 默认全折叠；CI `concept_map.py --check` 26/26，`check_pages()` 拦死链 |
| 构建期门禁 | `docs/tools/build_wiki.py` `main()` L657–678 | 6 抽屉 / 26 refs / 26 报告锚点 / 26 正源块 / 26 条「完整原文 →」链接，五项不等即 `BUILD FAILED`；另断言 `CORE ⊆ 生成文件集` |
| 离线首访 | `build_wiki.py` 的 `SW_JS` 模板（经 `Site.write()` 写出；**勿手改** `_site/sw.js`） | `CORE` 由 `sw_core(self.pages)` 动态派生 = 骨架 3 项 + dashboard 1 页 = **4 项**；`CACHE='wiki-v3'`（bump 自 v2）；构建期断言 `CORE ⊆ 生成文件集`；口径：首页 + dashboard 单页（含 26 处内联正源）可离线，10 篇 design 原文下钻页首访需联网 |

## 八、验收留痕与未执行项
- **2026-11-20 实测（Edge 无头 + 375px iframe 读真实 DOM）**：`concept_map.py --check` 26/26 唯一命中；生成 96 页 / EXIT 0；折叠态 `scrollW=375 / clientW=375`、`asideH=65`、`summaryH=56`、6 抽屉 `open=0`、5 图 / 5 竖版 SVG；点 #1 再点 #2 → `open=1 / state=010000`，互斥手风琴生效，展开后仍 375/375 零横滑；CSS 静态断言无 `min-width:≥100px`、无 `white-space:nowrap`、`table-layout:fixed` 保留、旧类残留 0。视觉自审把「未定」从 18px 石板蓝 h2 降为 14px --mut + 上 1px 分隔线，退回次级注记。
- 截图须用 375px iframe 包一层；直接开无头窗口会被 Windows 最小窗口宽度撑到约 500px，产生假裁切。
- **未执行（等主人指令）**：① 源目录 `site/` → `site-src/` 改名（见《站点Dashboard部署约束-v1》§一）；②「未定」缺口是否对公开 Pages 可见；③ 本轮站点改动未 commit / 未 push，线上 Pages 需 push main 由 Actions 重建。
- **已同步（2026-11-20 A 组）**：`CLAUDE.md`「站点发布契约」整节路径、`site/dashboard.md:5` 死链、`pages.yml:4` 与融合规划 L88 旧注释全部清理；四门禁 EXIT 0；重建前后 `rules/战场玩法.html` sha256 一致。
