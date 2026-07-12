# 当前工作版本说明

## 用途

`docs/report/current/` 用于保留 v0.1 之后的 Markdown 过渡源和历史兼容资料；从 v0.2 起，报告正文的当前唯一编辑入口改为 `docs/report/latex/current/`。

## 当前状态

这里的 Markdown 内容来自 `v0.2` 在 `v0.1` 冻结版基础上的迁移起点，不再作为 v0.2 正文的第二份手工编辑源。v0.2 正文由 `docs/report/latex/current/main.tex` 和分章节 `.tex` 文件装配。

## 工作规则

1. v0.2+ 的正文写作、章节扩展和公式排版只在 `docs/report/latex/current/` 中进行。
2. 当前目录中的 Markdown 不应与 LaTeX 正文并行手工维护；如需重新迁移，必须明确记录迁移批次并重新执行全书质量检查。
3. 稳定的 LaTeX 版本冻结到 `docs/report/versions/<version>/latex/`，再从 frozen 源生成发布 PDF。
4. 规划、研究卡片、图表源和数据资产仍按项目规范维护，不因正文源切换而改变归档规则。

## 配套目录

- `figures/`：当前工作版本使用的图
- `tables/`：当前工作版本使用的表
- `snippets/`：当前工作版本使用的代码片段
