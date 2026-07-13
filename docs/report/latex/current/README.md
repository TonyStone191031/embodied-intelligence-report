# v0.3 LaTeX 工作区

这是 v0.3 的 LaTeX 主源目录，也是 v0.2 以后报告正文的唯一编辑源。当前章节文件仍保留 v0.2 冻结基线内容，供 v0.3 研究和迁移使用；在 v0.3 详细大纲获得明确批准前，不修改章节结构、不把旧正文声明为 v0.3 完成稿。

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

编译中间文件统一写入 `tmp/latex-build/v0.3/`，最终 PDF 写入 `output/exports/v0.3/`。当前机器的 TeX Live 2026 路径已缺失，首次 v0.3 构建前必须先按 `toolchain.md` 修复工具链。

工具链、字体和版本记录见同目录的 `toolchain.md`；工作规范见 `docs/planning/latex工作规范.md`。
