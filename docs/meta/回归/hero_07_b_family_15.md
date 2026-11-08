# hero_07_b（family_15 血巢·农场主）机制层回归报告（2026-11-08）

## 扫描基线

review_scan R1–R11（基线 2026-11-08）；hero_07_b 组 **0 warn**。

## 命中表

无命中。

## 修复记录

- 三张 harvest 卡：heal/modify_resource 不支持 valueFrom（仅 damage 支持）——定值化（抢收 4 / 偷收 2 / 大丰收 3+2），层数缩放语义写入 describe（由引擎按层数校验），卡面合规。

## 门禁复核

validate 0 err / validate_schema 0 err（47 文件）/ enum sync OK / glossary OK。

## 定稿确认

新 6 卡 + j07_播种 + crop def **全绿零豁免**。**hero_07_b 定稿。**
