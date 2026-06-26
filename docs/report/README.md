# 报告目录说明

## 目录用途

`docs/report/` 用于维护《具身智能行业和技术发展调研报告》的正文、当前工作版本与历史冻结版本。

## 目录结构

```text
docs/report/
  current/               # 当前正在维护的工作版本
  versions/              # 已冻结的历史版本
    v0.0/
      figures/
      tables/
      snippets/
```

## 工作规则

1. 当前写作与修订，优先发生在 `current/`。
2. 某个版本确认完成后，再整理并冻结到 `versions/<version>/`。
3. 不直接覆盖已经冻结的旧版本目录。
4. 若某个图、表、代码片段仅服务于某一冻结版本，应同步整理到该版本目录下。
5. 可跨版本复用的原始资产继续放在 `assets/`、`code/`、`data/` 中。

## 关键文件

- 当前版本总入口：
  [00-具身智能行业和技术发展调研报告-v0.0](D:/Projects/embodied-intelligence-report/docs/report/current/00-具身智能行业和技术发展调研报告-v0.0.md)
- 项目工作规范：
  [项目工作规范](D:/Projects/embodied-intelligence-report/docs/planning/项目工作规范.md)
- 更新日志：
  [CHANGELOG](D:/Projects/embodied-intelligence-report/CHANGELOG.md)
