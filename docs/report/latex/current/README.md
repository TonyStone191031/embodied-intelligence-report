# v0.3 LaTeX 工作区

这是 v0.3 的 LaTeX 主源目录，也是 v0.2 以后报告正文的唯一编辑源。v0.3 详细大纲已于 2026-07-13 获用户批准；第 6、23 章双试点已通过质量确认，其余章节仍按当前版本工作台分批迁移，未重写章节不得声明为 v0.3 完成稿。

本文件只保存工作区命令和环境事实。权威任务路由见 [`AGENTS.md`](../../../../AGENTS.md)，长期 LaTeX 规则见[《项目工作规范》第 11 节](../../../planning/项目工作规范.md#11-latex-正文工作流v02)，当前批次见[《当前版本工作台》](../../../planning/current/当前版本工作台.md)。

## 源文件边界

从 v0.2 起，正文只在本目录的 `.tex` 文件中维护，不再手工同步维护同一正文的 Markdown 副本。章节由 `chapters/manifest.tex` 装配，该清单由迁移脚本生成；迁移完成后的公式、图表和排版修正应直接落在 LaTeX 源中。

规划、研究笔记、论文卡、企业卡和数据资产仍按项目规范使用 Markdown、CSV 等格式；它们不是正文的第二份 LaTeX 源。v0.3 详细大纲和证据架构位于 `docs/planning/current/`。

## 编译

在仓库根目录执行：

```powershell
python code/export/export_latex.py --version v0.3 --source current
```

冻结后从版本源构建：

```powershell
python code/export/export_latex.py --version v0.3 --source frozen
```

如果本机已经安装 TeX Live、XeLaTeX 和 latexmk，也可以直接在本目录执行：

```powershell
latexmk -xelatex -halt-on-error -file-line-error main.tex
```

编译中间文件统一写入 `tmp/latex-build/v0.3/`，最终 PDF 写入 `output/exports/v0.3/`。当前使用项目级 MiKTeX 根目录；XeLaTeX、latexmk、Biber、GB/T 7714 样式和双试点构建已经验证。普通沙箱对 Windows 用户字体目录的访问限制及复现配置见 `toolchain.md`。

工具链、字体和版本记录见同目录的 `toolchain.md`。
