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

1. v0.2 manifest 记录的 TeX Live 2026 路径 `C:/texlive/2026` 已不存在；v0.3 当前使用 MiKTeX 24.4 的 XeTeX 3.141592653-2.6-0.999996 与 Biber 2.20。
2. 项目级 MiKTeX 配置、数据、安装根和字体缓存位于 `tmp/miktex/v0.3/`；`code/export/export_latex.py` 已能自动注入这些根目录。
3. 双试点入口已完成 XeLaTeX 三遍与 Biber：Y1 为 18 页，Y2 为 23 页；GB/T 7714—2015 References、中文、公式、代码和矢量图均可输出。
4. 当前构建日志保留两类非阻塞警告：FangSong 无粗体字形时回退，以及源码锚点/宽比较表的少量 overfull/underfull box。
5. Codex 普通沙箱无法读取 Windows 用户字体目录；自动化会话需要受控提升权限。普通本机用户环境不受此沙箱边界影响。

## 首次可用性验收

- `latexmk -xelatex -halt-on-error -file-line-error` 可运行。
- Biber 可运行，`gb7714-2015` 样式可加载。
- 仿宋、黑体和等宽代码字体可找到。
- 基线/试点 PDF 构建成功；正式冻结时 manifest 再记录真实工具版本和输出哈希。
- `latex_quality_check.py`、页面渲染和文本残留扫描通过。
