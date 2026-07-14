# v0.3 LaTeX 工作区

这是 v0.3 的 LaTeX 主源目录，也是 v0.2 以后报告正文的唯一编辑源。v0.3 详细大纲已于 2026-07-13 获用户批准；第 1--38 章初稿、六个索引型附录和独立 References 已于 2026-07-14 完成全书装配。当前成果是初稿，不是冻结版本；后续仍按当前版本工作台补充深度、来源和资产。

本文件只保存工作区命令和环境事实。权威任务路由见 [`AGENTS.md`](../../../../AGENTS.md)，长期 LaTeX 规则见[《项目工作规范》第 11 节](../../../planning/项目工作规范.md#11-latex-正文工作流v02)，当前批次见[《当前版本工作台》](../../../planning/current/当前版本工作台.md)。

## 源文件边界

从 v0.2 起，正文只在本目录的 `.tex` 文件中维护，不再手工同步维护同一正文的 Markdown 副本。v0.3 章节由 `chapters-v0.3/manifest.tex` 装配；迁移完成后的公式、图表和排版修正应直接落在 LaTeX 源中。`chapters/manifest.tex` 仅属于旧结构，不再参与 v0.3 的 `main.tex` 构建。

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

编译中间文件统一写入 `tmp/latex-build/v0.3/`，最终 PDF 写入 `output/exports/v0.3/`。当前使用项目级 MiKTeX 根目录；XeLaTeX、Biber、GB/T 7714 样式和优先章节构建已经验证。当前 MiKTeX 缺少 `latexmk` 所需的 Perl；分步构建方式、字体搜索路径和复现配置见 `toolchain.md`。

工具链、字体和版本记录见同目录的 `toolchain.md`。

第 6、23 章的独立正式验收入口为 `priority-main.tex`；Z0--Z4c 入口仅用于批次回归，全书权威入口是 `main.tex`。

所有入口使用主 `references/references.bib`。在 Perl 恢复前，按 `toolchain.md` 记录的 XeLaTeX `-no-pdf`、Biber、两轮 XeLaTeX 和 `xdvipdfmx` 分步链路构建；不得把当前不可用的 `latexmk` 命令写成已通过。
