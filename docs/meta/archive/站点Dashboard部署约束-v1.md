# 站点 Dashboard 部署约束 · v1（架构同步版 · 2026-11-20）
**结论** 唯一推荐入库源目录 `site-src/`；红线：`_site/` 是生成产物，禁止手改／手拷／入库，站点只能改「源 + 生成器」。

> **执行状态（务必先读）**：§一「`site-src/` 改名」、§二–§三「迁移范围／引用点」、§六 的「现行链路契约文本」已落地（改名方案文本仍未执行）。现行链路仍是 `site/`（三份源 `dashboard.md` / `figures.html` / `concept-map.json`）→ `docs/tools/build_wiki.py` → `_site/`，`CLAUDE.md`「站点发布契约」已于 2026-11-20 同步为 `site/` 三份源，并补「单页唯一玩法页、无详情页」红线。§四已按 2026-11-20 主人裁定的「单页就地展开 + 互斥手风琴」重写并落地：6 个概念详情页撤销，`CORE` 派生 1 页、`CACHE` bump 至 `wiki-v3`。三处遗留死链／旧注释已清理，四门禁全部 EXIT 0。下文凡标「现行」者以 `build_wiki.py` 为准；未新建 v2。
## 一、目录（唯一推荐）
- 不取 `site/`：与 `_site/` 一字之差，而 `build_wiki.py` 的 `Site.write()`（现行 `:321`）有 `shutil.rmtree(OUT)`；用户原话「丢到 site 那边」已混淆二者，Windows／glob 误指风险不可接受，收益为零。
- 不取 `wiki/`：根目录实测不存在，`:20` 的 `WIKI` 是未使用死常量，复用会继承「主题资源目录」语义包袱。
- **取 `site-src/`**：与 `_site/` 无字符串包含关系；`git check-ignore` 实测 `site/`、`site-src/`、`wiki/` 均不忽略，取抗混淆最优；现在改名仅动 1 个常量 + 文档路径。原写「等 6 页铺开后再改要动全部链接」——6 个详情页已撤销，单页架构下站内玩法链接只剩 1 条，改名成本反而更低。
- 若坚持 `site/`（非推荐）三护栏缺一不可：生成器禁裸 `'site'` 字面量且 `OUT` 只认 `_site`；CLAUDE.md 明写「`site/` 源、`_site/` 产物」；`.gitignore` 保持精确 `_site/`，禁写 `*_site*`。**现行实现正是此分支**：`build_wiki.py:22` 常量 `SITE_SRC = ROOT/'site'`、`:8` 文件头已明写「`site/` 源、`_site/` 产物」、`.gitignore` 末行精确 `_site/`；三条护栏已全数补齐（见 §六）。
## 二、迁移范围（若执行 §一 改名；现行未执行）
- 只迁三份 → `site-src/`，**按现行文件名**：`dashboard.md`（极简概要）、`figures.html`（5 `<figure>`／10 `<svg>` 宽竖双版）、`concept-map.json`（6 概念 / 26 锚点 / 10 篇 pages）。原文所记 `战场玩法.md` / `战场玩法.html` / `概念地图.json` 是 11-17 版旧名。
- `docs/ddd/**`／`docs/json/**` 一字不动、路径不动：`check_enum_sync.py:59-68` 按 `docs/ddd/params/*.md` 的 `## 标题` 取表，正源移动即门禁红。
- `concept-map.json` 内容不改（`refs.doc` 是相对 ROOT 的 `docs/ddd/...`，`pages` 是站内页路径）；`load_figures()` 按 `<h2>` 切片、缺失即抛错（不再静默跳过 10 图）。**已清理**：`site/dashboard.md:5` 原写 `图解：[战场玩法.html]`（指向已改名文件的死链），现已改指 `figures.html`；`parse_dashboard()` 会跳过 `图解：` 行，重建前后产物 sha256 一致。代价：指针表离开 `docs/meta/` 后设计侧改章节须跨目录同步，靠 §六 写死。
## 三、引用点同步清单（行号已按 2026-11-20 现行生成器校准）
> 下表原为「执行 §一 改名」时的改动清单，行号取自 11-17 版生成器（约 420 行）；现行 `build_wiki.py` 已重构为 691 行。第三列改为**现行状态**，避免按旧行号定位踩空。

| 现行位置 | 符号 | 现行状态 / 若改名须改 |
|---|---|---|
| `build_wiki.py:19,22` | `DOCS`／`SITE_SRC` | 死常量 `WIKI` 已删；`SITE_SRC = ROOT/'site'`（改名只需动这一处 + 文档路径） |
| `build_wiki.py:507` | `parse_dashboard(SITE_SRC/'dashboard.md')` | 已脱离 `DOCS`；`load_md` 定义在 `:385` |
| `build_wiki.py:419–444,508` | `load_figures()` | 已按 `<h2>` 显式映射切片；缺失即抛 `ConceptMapError`（`:425–426`），并断言 5 figure / 10 svg / 5 tall |
| `build_wiki.py:294–302,219,345–347` | `sw_core()`／`SW_JS.CACHE`／`Site.write()` | 已按 §四改造；`details_html` 函数已不存在，站内链接统一走 `site_link(cur, target)`（`:389–393`），与 `shell().rel()` 同口径、BASE 感知 |
| `concept_map.py:20` | `MAP_PATH` | 已指向 `site/concept-map.json`；`load_map(path=MAP_PATH)` 允许调用方注入，无硬编码 prefix |
| `pages.yml:4`／`build_wiki.py:4,8` | 「输入 docs/」「site/ 下三份玩法页专属源」注释 | 生成器文件头已同步；`pages.yml:4` 注释已改为「docs/ddd + docs/json + site/ 三份玩法页源」 |
| `CLAUDE.md:30–37` | 「站点发布契约」整节 | **已同步（2026-11-20）**：旧路径全改指 `site/dashboard.md` / `site/figures.html` / `site/concept-map.json`，并补唯一链路 + 单页抽屉红线；L32 原 `_site/` 禁令保留 |
| `pages.yml:42`／`.gitignore:4`／`archive/站点融合规划-v1.md` | upload `path:_site`／`_site/`／历史旧路径 | **不改**；v1 为历史留痕，本文登记替代关系 |
## 四、单页就地展开 → sw.js 与离线（现行，已落地）
**架构变更**：6 个概念详情页已撤销，6 抽屉 + 5 图解 + 26 处正源全部内联在 `rules/战场玩法.html` 一页。因此 `CORE` 里不再有 6 条详情页 URL，也不再有「dashboard ↔ 详情页」互链。

- ① `sw_core(pages)`（`build_wiki.py:294–302`）由 `self.pages` 动态派生：骨架 **3 项**（`index.html` / `style.css` / `manifest.webmanifest`）+ `DASH_PATH` **1 页** = **4 项**。禁手写 URL，改名／删页会立刻反映到清单；`main():673–678` 另有断言 `CORE ⊆ 生成文件集`，不满足即 `BUILD FAILED`。
- ② `caches.addAll(CORE)` 原子：任一 URL 404 → install 整体失败 → SW 不激活 → 离线归零。原 v1 写「骨架 4 项 + 全部玩法页」是笔误（骨架实为 3 项）；单页架构下应写「3 + 1」。
- ③ `CACHE` 已 bump 至 **`wiki-v3`**（`SW_JS` 模板 `:219`）。从 v2 升到 v3 是必须的：6 个详情页被删、dashboard 主内容从 9.5 KB 变 73 KB，同名缓存下 `activate` 的 `ks.filter(k => k !== CACHE)` 清不掉旧缓存，cache-first 会让用户永远停在旧的 6 卡导航盘页。
- ④ 口径：首页 + dashboard 单页（含 6 抽屉 / 5 图 / 26 处内联正源）装完即可离线；「完整原文 →」指向 10 篇 `design/` 页，首访需联网，`concept_map.check_pages()` 保证不出现死链。
- ⑤ 构建期门禁（`:657–671`）：6 抽屉 / 26 refs / 26 报告锚点 / 26 正源块 / 26 条「完整原文 →」链接，五项不等即中止；验收另断言 `rules/concepts/` 目录不存在。

**2026-11-20 实测**：`CACHE=wiki-v3`；`CORE` 共 4 项（骨架 3 + `rules/战场玩法.html`）；`concept_map.py --check` 26/26 唯一命中；生成 96 页 / EXIT 0。详见《站点Dashboard视觉规格-v1》§七／§八。
## 五、WIKI_BASE 子路径
- `BASE`（`build_wiki.py:38`）由 `WIKI_BASE` 环境变量注入；`shell().rel()`（`:355–356`）与 `site_link()`（`:389–393`）**同口径**处理，两者都返回 `BASE/target` 或 `prefix + target`。`SW_REGISTER`（`:244–247`）、`CORE`（相对 sw.js）、首页入口卡（`:541`）均为相对路径。原文所记 `details_html(prefix='../')` 函数已不存在。
- `BASE=''`（当前 Pages 项目页）：`rel()` 与 `'../'` 一致，**不断链**；`BASE` 非空且格式不符（无前导 `/`／带尾斜杠／与实际子路径不符）时，`../` 解析错位 → dashboard 内 26 条「完整原文 →」断链。原写「或新页层级 ≠ 一层」已不适用：详情页撤销后，全部链接都从 `rules/战场玩法.html` 这一层出发。
- 约束：BASE 固定 `/<子路径>`（一个前导斜杠、无尾斜杠）且与 Pages 实际子路径一致；**站内链接一律经 `rel()` / `site_link()` 生成**，`site/*.html` 禁写相对 href；dashboard 内原文链接由 `site_link(DASH_PATH, page)` 生成；`CORE` 保持相对 sw.js，随子路径天然生效。
## 六、写进 CLAUDE.md「站点发布契约」首条（现行链路**已落地**；改名方案未执行）
> **状态（2026-11-20 更新）**：下方「现行链路文本」已写入 `CLAUDE.md`「站点发布契约」，同时把整节旧路径改为 `site/` 三份源并补单页抽屉红线；`site-src/` 改名方案文本**仍未执行**，仅作备选留档。主人仍未下达改名指令。

按 §一 改名方案的可粘贴文本（改名执行后才用）：
> `_site/` 由 `docs/tools/build_wiki.py` 的 `shutil.rmtree` 全量重建、`.gitignore` 末行忽略、不入库：**禁止手改、禁止手拷文件进去、禁止当作页面源**；任何直接改动下次 push main 由 `.github/workflows/pages.yml` 覆盖即丢。站点唯一链路：`site-src/`（源）→ `build_wiki.py`（生成器）→ `_site/`（产物）→ Pages；`site-src/` 是源、`_site/` 是产物，不得混写。

**现行链路文本（2026-11-20 已写入 `CLAUDE.md`，与下方内容等价）**：
> `_site/` 由 `docs/tools/build_wiki.py` 的 `shutil.rmtree` 全量重建、`.gitignore` 末行忽略、不入库：**禁止手改、禁止手拷文件进去、禁止当作页面源**；任何直接改动下次 push main 由 `.github/workflows/pages.yml` 覆盖即丢。站点唯一链路：`site/`（源：`dashboard.md` / `figures.html` / `concept-map.json`）→ `build_wiki.py`（生成器）→ `_site/`（产物）→ Pages；`site/` 是源、`_site/` 是产物，不得混写。`rules/战场玩法.html` 是唯一玩法页，6 个概念以 `details.drawer[name="concept"]` 就地互斥展开，不设详情页。

- 同节补：改三份源后跑 `python docs/tools/build_wiki.py`；改 DDD 章节标题／删章节／加概念仍须同步 `site/concept-map.json`；单独校验用 `python docs/tools/concept_map.py --check`。
## 七、门禁与 CI
- 四门禁（`validate.py`／`validate_schema.py`／`check_enum_sync.py`／`check_glossary.py`）**不受影响**：只读 `docs/json/**`、`docs/json/schema/`、`docs/meta/glossary.json`、`docs/ddd/params/*.md`，三份源均不在输入集。
- **若执行 §一 改名**：`pages.yml:35` 锚点 step 依赖 `concept_map.MAP_PATH`，常量不改即报「概念地图缺失」直接红；`:38` Build wiki 两处源路径不改则 md 抛 FileNotFoundError、图源缺失抛 `ConceptMapError`；`:42` upload `path:_site` 不受影响。
- **现行 CI（已接线）**：`pages.yml:34–35` 已有独立 step `python docs/tools/concept_map.py --check`，`MAP_PATH` 指 `site/concept-map.json`，本地实测 26/26 唯一命中；`:37–38` Build wiki 生成 96 页；`:40–42` upload `_site`。`pages.yml:4` 注释已同步为「docs/ddd + docs/json + site/ 三份玩法页源」。
## 八、待实测项（生成验收阶段）
> 前 3 行原按「6 详情页 + site-src 改名」撰写，已按单页架构更正；改名验收本身**仍未执行**。

| 验证问题 | 预期结论 | 一句话验证方法 | 现行状态 |
|---|---|---|---|
| 三份源能被 CI checkout 并读到（现行 `site/`） | 能 | Actions `ls site/` + 本地跑生成器出 **96 页**（单页架构，无 +6） | 本地已验：96 页 / EXIT 0 |
| `CORE` 动态派生覆盖玩法页且 install 成功 | 能 | 断言 `sw.js` 的 CORE 4 项每项在 `_site/` 存在；构建期已有 `CORE ⊆ 生成文件集` 断言 | 已落地：`wiki-v3` / CORE 4 项 |
| BASE 子路径下 26 条「完整原文 →」不断 | 不断 | `WIKI_BASE=/<repo>` 生成后比对 `site_link()` 与 `rel()` 前缀 | 待实测 |
| 概念抽屉互斥与 375px 零横滑 | 生效／零横滑 | 375px iframe 读 DOM：点两个抽屉后 `open=1`，`scrollWidth=clientWidth` | 已验：`state=010000` / 375=375 |
| 四门禁仍全绿 | 全绿 | 依次跑四脚本 exit 均 0 | **已验（2026-11-20）**：571 卡 / 76 文件 / 枚举 6 组 / 词典 69 类，四脚本 EXIT 0 |
| `site/` → `site-src/` 改名后 CI 可读 | 能 | Actions `ls site-src/` + 生成器常量改一处 | **未执行**（§一 推荐方案，等指令） |
