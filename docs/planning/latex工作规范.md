# LaTeX 工作规范

本文件是 v0.2 及以后报告正文排版源的专用规范；长期通用的项目版本和研究流程仍以 `项目工作规范.md` 为准。

## 1. 唯一正文源

- `v0.1` 继续使用冻结 Markdown，保持历史可复现性。
- 从 `v0.2` 开始，正文唯一编辑源为 `docs/report/latex/current/`。
- 不同时手工维护同一正文的 Markdown 和 LaTeX 两套内容。
- 规划文件、研究笔记、论文卡、企业卡和资料索引仍使用 Markdown。

## 2. 目录结构

```text
docs/report/latex/current/
  main.tex
  preamble.tex
  metadata.tex
  chapters/
  frontmatter/
  backmatter/
  references/references.bib
  latexmkrc

docs/report/versions/vX.Y/latex/
  # 版本冻结时复制 current 的完整 LaTeX 源

tmp/latex-build/vX.Y/
  # 编译中间文件，必须被 .gitignore 忽略
```

`main.tex` 是唯一主入口；章节按文件拆分，并通过 `\\input` 或 `\\include` 组装。Overleaf 风格的主文件加分章节组织适用于本项目，但本地仓库必须保证无需在线服务即可编译。

## 3. 标题层级与分页

- Markdown `#` 对应报告的 27 个部分，映射为带 `\\clearpage` 的 `\\reportpart`；每个部分必须从新页开始。
- Markdown `##` 对应部分内部的数字章节，映射为连续排版的 `\\section*`，不得因为数字序号自动新建页面。
- Markdown `###` 和 `####` 分别映射为 `\\subsection*` 和 `\\subsubsection*`，不得通过标题命令自动新建页面。
- `\\clearpage` 仅由 `\\reportpart` 统一负责；正文章节源文件不得另外随意加入 `\\newpage`、`\\clearpage` 或 `\\cleardoublepage`。

## 4. 内容与资产

- 章节标题映射为 `\\part`、`\\chapter`、`\\section`、`\\subsection`。
- 公式直接使用 LaTeX 数学环境，不经过 Markdown、Word OMML 或 PDF fallback 转换。
- 长表格优先使用 `longtable`/`xltabular`，避免缩小到不可读。
- 图片使用 `graphicx`，流程图和 Mermaid 源先渲染为 PNG、SVG 或 PDF 再插入。
- 代码块使用 `listings`，默认不依赖外部 Pygments 服务。
- 链接先使用 `hyperref`、`url`；论文引用逐步迁移到 `references/references.bib` 和 Biber。

## 5. 编译与发布

- 优先使用 TeX Live、XeLaTeX、`latexmk` 和 Biber。
- 统一通过 `code/export/run_export.py` 调用 LaTeX 构建，不复制版本专属导出脚本。
- PDF 是主交付物；Word 是可选兼容产物，复杂公式和图表以 PDF 为准。
- 最终文件放在 `output/exports/vX.Y/`；中间文件放在 `tmp/latex-build/vX.Y/`。

## 6. 质量门

每次编译和冻结必须检查：

1. `latexmk -xelatex -halt-on-error -file-line-error` 成功。
2. 无未解决交叉引用、严重 `Overfull \\hbox`、图片越界、长表格溢出和空白页。
3. 公式、矩阵、`cases`、长表格、流程图、中文字体和目录完成页面渲染抽样。
4. PDF 文本中无原始 LaTeX 控制序列残留。
5. 版本 manifest 记录编译器、字体、宏包、源文件清单和检查结果。
