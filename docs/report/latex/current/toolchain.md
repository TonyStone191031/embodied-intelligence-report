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

## 2026-07-14 当前状态

1. v0.2 manifest 记录的 TeX Live 2026 路径 `C:/texlive/2026` 已不存在；v0.3 当前使用 MiKTeX 24.4 的 XeTeX 3.141592653-2.6-0.999996 与 Biber 2.20。
2. 项目级 MiKTeX 配置、数据、安装根和字体缓存位于 `tmp/miktex/v0.3/`；`code/export/export_latex.py` 已能自动注入这些根目录。
3. 双试点和 Z0--Z4c 批次入口均已通过；全书 `main.tex` 已装配第 1--38 章、附录 A--F 和独立 References，输出 193 页 v0.3 初稿。Biber 识别 124 个正文实际引用键；中文、公式、32 段代码、44 幅图、47 张表、两幅 CC BY 4.0 论文原图均可输出。
4. 当前 MiKTeX 的 `latexmk` 因缺少 Perl 不可用。全书使用等价分步链路：XeLaTeX `-no-pdf` → Biber → 两轮 XeLaTeX `-no-pdf` → `xdvipdfmx`；项目级包根优先，系统 TeX 与字体目录作为只读回退。Biber 调用需设置 `MIKTEX_ENABLE_INSTALLER=0`，避免包管理器检查造成停滞。
5. 2026-07-14 全书最终日志中未定义引用、重复标签、overfull/underfull box 均为 0；`latex_quality_check.py` 的原始 LaTeX 标记和本机路径残留为 0。仍存在 FangSong 无粗体字形时的字体替代警告，不影响内容与版面。
6. Codex 普通沙箱无法读取 Windows 用户字体目录；自动化会话需要受控提升权限。普通本机用户环境不受此沙箱边界影响。

## 首次可用性验收

- `latexmk` 当前不可用；恢复 Perl 后必须重新验证，恢复前使用上述分步链路。
- Biber 可运行，`gb7714-2015` 样式可加载。
- 仿宋、黑体和等宽代码字体可找到。
- 基线、批次入口与全书 PDF 构建成功；初稿 manifest 记录当前工具、页数和输出哈希，正式冻结时重新生成冻结 manifest。
- 全书引用闭合、文本残留扫描和封面、目录、第 6/23 章、附录、References 抽样已通过。冻结前仍需把正文从 193 页扩充到大纲目标，并把实际引用来源由 124 条提高到约 200 条以上，同时保持论断覆盖率。
