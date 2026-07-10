# `docs/planning/` 目录说明

## 目录职责

`docs/planning/` 用于维护本项目的规划层文档，而不是正文。

它分成三层：

1. 根目录：长期通用规范与导航文件
2. `current/`：当前活跃规划
3. `archive/vX.Y/`：历史版本规划归档

## 当前建议阅读顺序

1. [项目工作规范](D:/Projects/embodied-intelligence-report/docs/planning/项目工作规范.md)
2. [当前详细大纲](D:/Projects/embodied-intelligence-report/docs/planning/current/具身智能报告-当前详细大纲.md)
3. [当前版本修订计划](D:/Projects/embodied-intelligence-report/docs/planning/current/当前版本修订计划.md)
4. [当前工作清单](D:/Projects/embodied-intelligence-report/docs/planning/current/当前工作清单.md)

## 使用规则

1. 新的结构性正文工作，先更新 `current/具身智能报告-当前详细大纲.md`
2. 新的非结构性维护工作，先更新 `current/当前版本修订计划.md`
3. 每次开启新的正文批次前，先更新 `current/当前工作清单.md`
4. 某版本冻结后，把正文快照放入 `docs/report/versions/vX.Y/`，并把该版本特有的执行面板、方案稿和阶段性计划归档到 `archive/vX.Y/`
5. 冻结完成后，再把 `current/` 的入口、大纲、修订计划和工作清单切换到下一版本
6. 根目录不长期保留仅对单个版本有效的临时计划文件
