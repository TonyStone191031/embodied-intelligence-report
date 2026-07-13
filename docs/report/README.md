# 报告目录说明

本文件只说明 `docs/report/` 的本地用途和入口。权威规则与任务路由见 [`AGENTS.md`](../../AGENTS.md) 和[《项目工作规范》](../planning/项目工作规范.md)。

## 目录用途

`docs/report/` 用于维护《具身智能行业和技术发展调研报告》的正文、当前工作版本与历史冻结版本。

## 目录结构

```text
docs/report/
  current/               # v0.1 及此前的 Markdown 历史/兼容源
  latex/current/         # v0.2+ 当前唯一正文编辑源
  versions/              # 已冻结的历史版本
    v0.0/
      figures/
      tables/
      snippets/
```

## 工作规则

1. v0.1 及此前的 Markdown 工作遵循 `current/`；v0.2+ 当前写作与修订只发生在 `latex/current/`。
2. 某个版本确认完成后，再整理并冻结到 `versions/<version>/`。
3. 不直接覆盖已经冻结的旧版本目录。
4. 若某个图、表、代码片段仅服务于某一冻结版本，应同步整理到该版本目录下。
5. 可跨版本复用的原始资产继续放在 `assets/`、`code/`、`data/` 中。

## 关键文件

- v0.3 LaTeX 入口：[`latex/current/main.tex`](latex/current/main.tex)
- v0.3 工作区说明：[`latex/current/README.md`](latex/current/README.md)
- 项目工作规范：
  [项目工作规范](../planning/项目工作规范.md)
- 更新日志：
  [CHANGELOG](../../CHANGELOG.md)
