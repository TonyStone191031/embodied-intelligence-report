# v0.2 LaTeX 工作区

这是 v0.2 及以后报告正文的 LaTeX 主源目录。当前已完成 `01~27` 全部章节的迁移；`00` Markdown 文件仍作为 v0.1 过渡版导航，不作为 LaTeX 正文装配单元。`frontmatter/` 中的版本说明替代了旧入口文件的导出说明。

## 源文件边界

从 v0.2 起，正文只在本目录的 `.tex` 文件中维护，不再手工同步维护同一正文的 Markdown 副本。章节由 `chapters/manifest.tex` 装配，该清单由迁移脚本生成；迁移完成后的公式、图表和排版修正应直接落在 LaTeX 源中。

规划、研究笔记、论文卡、企业卡和数据资产仍按项目规范使用 Markdown、CSV 等格式；它们不是正文的第二份 LaTeX 源。

## 编译

在仓库根目录执行：

```powershell
python code/export/export_latex.py --version v0.2 --source current
```

冻结后从版本源构建：

```powershell
python code/export/export_latex.py --version v0.2 --source frozen
```

如果本机已经安装 TeX Live、XeLaTeX 和 latexmk，也可以直接在本目录执行：

```powershell
latexmk -xelatex -halt-on-error -file-line-error main.tex
```

编译中间文件统一写入 `tmp/latex-build/v0.2/`，最终 PDF 写入 `output/exports/v0.2/`。

工具链、字体和版本记录见同目录的 `toolchain.md`；工作规范见 `docs/planning/latex工作规范.md`。
