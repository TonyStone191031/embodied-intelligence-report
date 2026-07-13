# `docs/planning/` 目录说明

## 目录职责

`docs/planning/` 用于维护本项目的规划层文档，而不是正文。

它分成三层：

1. 根目录：长期通用规范与导航文件
2. `current/`：当前活跃规划
3. `archive/vX.Y/`：历史版本规划归档

## 当前建议阅读顺序

1. [项目工作规范](D:/Projects/embodied-intelligence-report/docs/planning/项目工作规范.md)
2. [章节写作质量与证据资产规范](D:/Projects/embodied-intelligence-report/docs/planning/章节写作质量与证据资产规范.md)
3. [当前详细大纲](D:/Projects/embodied-intelligence-report/docs/planning/current/具身智能报告-当前详细大纲.md)
4. [当前版本修订计划](D:/Projects/embodied-intelligence-report/docs/planning/current/当前版本修订计划.md)
5. [当前工作清单](D:/Projects/embodied-intelligence-report/docs/planning/current/当前工作清单.md)
6. [v0.3 证据与资产规划](D:/Projects/embodied-intelligence-report/docs/planning/current/v0.3-证据与资产规划.md)

技能调用补充规则见[《项目工作规范》中的“skills 与质量门”](D:/Projects/embodied-intelligence-report/docs/planning/项目工作规范.md#10-skills-与质量门)：本项目规划和版本文件优先于 skill 默认流程；完整论文编排器默认不启动，按任务需要调用局部研究、引用和验证能力。

## 使用规则

1. 新的结构性正文工作，先更新 `current/具身智能报告-当前详细大纲.md`
2. 新的非结构性维护工作，先更新 `current/当前版本修订计划.md`
3. 每次开启新的正文批次前，先更新 `current/当前工作清单.md`
4. 某版本冻结后，把正文快照放入 `docs/report/versions/vX.Y/`，并把该版本特有的执行面板、方案稿和阶段性计划归档到 `archive/vX.Y/`
5. 冻结完成后，再把 `current/` 的入口、大纲、修订计划和工作清单切换到下一版本
6. 根目录不长期保留仅对单个版本有效的临时计划文件

## LaTeX 版本规则

1. `v0.1` 保留 Markdown 作为历史版本源，不进行原地迁移。
2. 从 `v0.2` 开始，正文唯一编辑源为 `docs/report/latex/current/`，采用 `main.tex` 加分章节 `.tex` 文件组织。
3. `docs/report/current/` 中的 Markdown 仅作为过渡/历史兼容源；不允许同时手工维护同一内容的 Markdown 与 LaTeX 两套正文。
4. LaTeX 冻结源存放在 `docs/report/versions/vX.Y/latex/`，最终 PDF 存放在 `output/exports/vX.Y/`。
5. PDF 为 LaTeX 主交付物；Word 仅作为可选兼容导出，不承诺复杂公式、长表格和图表与 PDF 完全一致。
