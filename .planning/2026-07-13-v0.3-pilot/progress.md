# 进度记录

## 2026-07-13

- 已确认用户批准 v0.3 详细大纲并授权启动双试点正文。
- 已完成仓库五份必读文件预读，并在首条进度更新中明确说明。
- 已读取 Academic Research Suite、PaperSpine 与 planning-with-files 的适用工作流；本任务采用局部研究、写作和引用审计，不另建与仓库冲突的完整论文交付树。
- 已在活跃大纲、修订计划和工作清单写入批准记录、试点范围、独立装配策略和验收门；阶段 1 完成。
- 正在执行阶段 2：证据与源码核验。
- 已核验第 6 章两篇经典原始论文的 DOI，以及 Franka 官方控制文档和 0.15.0 示例代码入口。
- VLA 合并检索首次发生后端网络错误，已记录并改为小批次检索。
- 已核验 RT-1、RT-2、PaLM-E、Diffusion Policy、Octo、OpenVLA 的原始论文与主要官方材料，并明确跨论文数值不可直接排行。
- 已直接核验 GR00T N1、Gemini Robotics、π0 与 FAST 的 arXiv 版本和核心架构边界。
- HEAD commit 查询因安全审查拒绝；不再绕行。采用稳定 tag，或把无 tag 仓库降级为路径导读并显式标注不可复现边界。
- 已完成两章试点 LaTeX、17 条试点文献库、两幅改绘流程图、两张比较表和三段代码/伪代码。
- 两幅图已完成原始分辨率目视检查，并把解析器漏边问题修正。
- 首次构建失败原因为 MiKTeX fresh installation；后续已通过项目级根目录初始化和依赖补齐恢复编译。
- `chktex` 也因同一 MiKTeX 初始化问题未运行；已改做引用闭合、括号平衡、裸链接/路径、套话和 `git diff --check` 静态检查。
- 最终静态盘点：2 章、14629 字符、14 个节级单元、17 个唯一引用键与 17 条 BibTeX 记录完全闭合；14 个公式环境、2 幅图、2 张表、3 个代码/伪代码环境；缺失资产与未平衡文件均为 0。
- 批次 Y 源稿已达到内容评审状态；双试点 PDF 页面抽样已完成，工具链不再作为阻塞项。
- 用户要求优先解决工具链；已将 MiKTeX 项目级初始化登记为当前工作清单中的 `in_progress` 维护任务。
- 只读探测确认：`xelatex`、`latexmk`、`biber`、`miktex` 均来自 `D:/Program Files/MiKTeX/miktex/bin/x64/`；MiKTeX 在创建 `C:/Users/zhuof/AppData/Roaming/MiKTeX/2.9` 时返回拒绝访问。
- 已建立 `tmp/miktex/v0.3/` 项目级 user config、user data、user install、user roots 和日志目录；`initexmf --report` 确认配置生效，并补齐 `biblatex`、`ctex`、`gbt7714`、`miktex-misc`、`dvips` 与 `miktex-dvips-bin-x64-2.9`。
- 提升权限的最小 XeLaTeX 冒烟测试已通过，生成 `tmp/miktex/v0.3/smoke-build-elevated/smoke.pdf`（1 页）。普通沙箱仍因 Windows 用户字体目录访问限制失败；双试点构建改用同一项目级配置并保留权限边界。
- 继续补齐版本依赖：`ltxbase`、`latex-tools`、`fontspec`、`xecjk`、hyperref 依赖、`logreq`、`biblatex-gb7714-2015`、`xstring` 等已安装到项目级根目录；重新生成 `xelatex.fmt` 后 ctex+FangSong 最小文档通过。
- 双试点在 `tmp/latex-build/v0.3-pilot-batch8/` 完成 XeLaTeX 三遍与 Biber；PDF 18 页、文本可提取、引用闭合，日志仅剩 FangSong 粗体回退与少量 overfull hbox 警告。
- 已更新 `code/export/export_latex.py`：检测到项目级 MiKTeX 时自动设置 `MIKTEX_USERCONFIG/USERDATA/USERINSTALL/USERROOTS`，并把项目安装根置于系统根前；`py_compile`、环境配置单测和 `git diff --check` 通过。
- 用户认可试点结构与风格，要求进一步拆细公式/模型讲解，并大幅增加论文原图或有明确教学用途的改绘图。
- 已重新完成本轮强制预读，并将子批次 Y2 写入正式修订计划、工作清单和过程计划。
- 已完成 Diffusion Policy、Octo、OpenVLA 和 $\pi_0$ 的候选图与原文图号初查；当前未找到可证明这些论文图可直接复用的授权，改用可追溯改绘。
- 已定义 7 类新视觉资产：第 23 章四种动作表示机制图 + Octo 架构图，第 6 章接触/摩擦与阻抗—导纳两幅辅助图。
- 桌面捆绑 Python 缺少 Matplotlib；已确认现有 Anaconda Python 包含 Matplotlib 3.8.4 和 NumPy 1.26.4，不需要网络安装依赖。
- 已新增单一可复现图像入口 `code/analysis/render_v03_pilot_figures.py`，成功生成 7 类 PNG+PDF 资产；渲染前已修正 Python 字符串中的数学转义警告。
- 已完成 Y2 两章细化：第 6 章增加虚功、功率平衡、二连杆力矩、接触模式、操作空间推导与阻抗/导纳接口；第 23 章增加 MSE 条件均值、量化误差/序列长度、扩散训练推理、Euler 流积分、模型模块分工和 Octo 架构拆解。
- 7 组新增图与原有 2 图均登记来源、改绘关系、许可判断和本地路径；因未找到明确可转载许可，不直接复制论文像素。
- Y2 试点完成 XeLaTeX 三遍与 Biber，输出 23 页 PDF；17 个引用键全部解析，最终日志无未定义引用、空 References 或 LaTeX 错误。
- 已按原始分辨率抽查接触/摩擦锥、阻抗/导纳、回归多峰、动作量化、扩散、流匹配和 Octo 架构页面；图中文字、公式、图注和分页可读。
