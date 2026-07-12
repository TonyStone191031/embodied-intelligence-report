# v0.2 LaTeX 工具链记录

本文件记录当前 Windows 构建环境，用于复现 v0.2 PDF。路径是本机工具链位置，不应被正文或版本源引用。

## 工具

- TeX 发行版：TeX Live 2026
- 安装根目录：`C:/texlive/2026`
- XeLaTeX：TeX Live 2026，XeTeX 3.141592653-2.6-0.999998
- latexmk：4.88，2026-03-09
- Biber：2.21
- tlmgr：revision 79591，2026-07-05
- 构建入口：`python code/export/run_export.py --version v0.2 --source current`
- LaTeX 直接构建：`python code/export/export_latex.py --version v0.2 --source current`

## 字体

- 正文与中文主字体：仿宋 `FangSong`
- 无衬线字体：黑体 `SimHei`
- 等宽字体：仿宋 `FangSong`
- 仿宋字体文件：Windows `simfang.ttf`

## 关键宏包

`ctexbook`、`amsmath`、`amssymb`、`mathtools`、`graphicx`、`booktabs`、`longtable`、`tabularx`、`xltabular`、`adjustbox`、`listings`、`hyperref`、`biblatex`、`newunicodechar`。

## 构建与质量记录

- 章节源：`docs/report/latex/current/`
- 构建中间文件：`tmp/latex-build/v0.2/`
- 发布 PDF：`output/exports/v0.2/embodied-intelligence-report-v0.2.pdf`
- 构建清单：`output/exports/v0.2/latex-build-manifest.json`
- 质量检查：横向溢出 `Overfull \\hbox = 0`；原始 LaTeX 控制序列 `0`；本机绝对路径残留 `0`。
- 允许保留的提示：少量 `Underfull \\hbox` 仅作为断行提示记录，不得伴随横向溢出或内容缺失。
