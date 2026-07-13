# v0.3 LaTeX 工具链状态

本文件记录 v0.3 当前 Windows 构建环境和待恢复事项。路径只属于本机工具链，不得进入正文。

## 目标工具链

- XeLaTeX + `latexmk` + Biber
- GB/T 7714—2015 `biblatex` 样式
- 正文与中文主字体：仿宋 `FangSong`
- 无衬线字体：黑体 `SimHei`
- 构建入口：`python code/export/run_export.py --version v0.3 --source current --format latex`
- 中间目录：`tmp/latex-build/v0.3/`
- 输出目录：`output/exports/v0.3/`

## 2026-07-13 当前状态

1. v0.2 成功 manifest 记录的 TeX Live 2026 路径 `C:/texlive/2026` 当前不存在。
2. 系统只发现 `D:/Program Files/MiKTeX/`，但该安装未完成首次初始化，当前无法构建或使用其 Poppler 工具。
3. 不得把当前状态记录为“构建成功”。v0.3 第一次正文试点前必须恢复可用的 XeLaTeX、latexmk 和 Biber，并记录实际版本、路径和宏包状态。
4. 工具链恢复后先编译未改正文的 v0.3 基线，再进行 GB/T 7714 样式试编译，确认中文参考文献、DOI、URL 和代码仓库条目排版正常。

## 首次可用性验收

- `latexmk -xelatex -halt-on-error -file-line-error` 可运行。
- Biber 可运行，`gb7714-2015` 样式可加载。
- 仿宋、黑体和等宽代码字体可找到。
- 基线 PDF 构建成功，manifest 记录真实工具版本和输出哈希。
- `latex_quality_check.py`、页面渲染和文本残留扫描通过。
