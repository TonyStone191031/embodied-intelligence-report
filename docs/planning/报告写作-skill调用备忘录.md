# 报告写作-skill调用备忘录

## 1. 目的

这份备忘录用于回答一个执行层问题：在《具身智能行业和技术发展调研报告》写作过程中，什么时候应该调用什么 skill。

它不是安装清单，而是写作和调研工作流手册。

## 2. 已安装 skills 清单

### 2.1 研究与取证

1. `academic-research-suite`
2. `jupyter-notebook`
3. `pdf`
4. `playwright`
5. `screenshot`

### 2.2 写作与结构化输出

1. `writing-plans`
2. `writing-skills`
3. `brainstorming`
4. `verification-before-completion`
5. `paper-spine-audit`

### 2.3 技能集合入口

1. `using-superpowers`

## 3. 调用时机速查

### 3.1 还没开始写，先确定该写什么

优先调用：

1. `writing-plans`
2. `brainstorming`

适用场景：

1. 把“大报告”拆成章节与子任务。
2. 给某一章设计结构、图表需求和引用需求。
3. 判断这一章应该先写理论、工程、企业还是应用。

### 3.2 需要系统查论文和学术脉络

优先调用：

1. `academic-research-suite`
2. `pdf`

适用场景：

1. 梳理某个技术方向的发展脉络。
2. 做代表性论文清单、时间线和对比表。
3. 从论文 PDF 中抽取关键方法、实验设置和结论。

### 3.3 需要查官网、博客、GitHub、产品发布

优先调用：

1. `playwright`
2. `screenshot`

配合使用：

1. `web`

适用场景：

1. 抓企业官网、博客、发布页、GitHub README。
2. 保存图示、截图、发布时间、产品说明。
3. 对需要精确留证的网页做结构化抓取。

### 3.4 需要整理一章的正式正文

优先调用：

1. `writing-skills`

配合使用：

1. `writing-plans`
2. `academic-research-suite`

适用场景：

1. 把研究笔记转成正式章节。
2. 统一文风、结构和术语。
3. 将“事实、解释、评价”三层写清楚。

### 3.5 需要补盲点、找缺口、扩大覆盖面

优先调用：

1. `brainstorming`

适用场景：

1. 怀疑某章覆盖不够全。
2. 想补充被忽略的技术路线、企业、数据集或争议点。
3. 想生成多个可选的分析框架后再择优。

### 3.6 需要像审论文一样审查长文质量

优先调用：

1. `paper-spine-audit`
2. `verification-before-completion`

适用场景：

1. 检查论证链是否完整。
2. 检查章节是否只有材料堆砌、缺少中心判断。
3. 检查引用、改写、结构和结论是否一致。

## 4. 章节级推荐工作流

每一章建议按下面顺序推进：

1. `writing-plans`
   - 先定本章目标、结构、问题清单、图表清单。
2. `academic-research-suite`
   - 补齐论文、综述、官方资料、关键事实。
   - 默认把它视为“章节正文开始前”的核心研究环节，而不是可有可无的补充步骤。
3. `playwright` / `screenshot` / `pdf`
   - 补图、补官网证据、补白皮书与 PDF 依据。
4. `writing-skills`
   - 输出正式章节草稿。
5. `paper-spine-audit`
   - 做结构与论证质量审阅。
6. `verification-before-completion`
   - 做交付前最终检查。

### 4.1 本项目当前的强制执行解释

对《具身智能行业和技术发展调研报告》这类长篇研究型报告，章节级流程不应理解为“推荐动作”，而应尽量理解为默认工作顺序：

1. 没有做 `academic-research-suite` 支撑的系统研究，不应直接把章节写成正式正文
2. 没有经过 `paper-spine-audit` 式检查的章节，只能视为草稿，不应轻易视为完成
3. `writing-skills` 的作用是把研究材料转化为正式文本，而不是替代研究本身

### 4.2 `academic-research-suite` 在本项目中的具体作用

在本项目中，`academic-research-suite` 不只是“查几篇论文”，而应承担下列任务：

1. 明确该章的核心研究问题与子问题
2. 梳理该章涉及的代表性论文脉络、路线分化与时间演进
3. 区分主流共识、仍有争议的结论与尚未解决的问题
4. 为后续正文准备“事实 - 推断 - 评价”三层材料
5. 明确哪些地方需要后续补图、配表或代码片段

### 4.3 `paper-spine-audit` 在本项目中的具体作用

在本项目中，`paper-spine-audit` 应主要用于检查以下问题：

1. 这一章是不是只有概念介绍，没有真正展开技术、工程与争议
2. 这一章的中心论点是否明确，论证链是否完整
3. 是否存在“有结论、少证据”或“有材料、无判断”的失衡
4. 是否遗漏了本章应覆盖的重要路线、代表系统或关键限制条件
5. 这一章是否更像科普综述，而不是学习和研究用途的长篇报告正文

## 5. 本项目中的优先使用规则

### 5.1 写“大纲和计划”时

优先用：

1. `writing-plans`
2. `brainstorming`

### 5.2 写“技术综述”时

优先用：

1. `academic-research-suite`
2. `pdf`
3. `writing-skills`
4. `paper-spine-audit`

### 5.3 写“企业与产业章节”时

优先用：

1. `playwright`
2. `screenshot`
3. `web`
4. `writing-skills`

### 5.4 写“最终判断与总结”时

优先用：

1. `brainstorming`
2. `paper-spine-audit`
3. `verification-before-completion`

### 5.5 写“报告前几章（导读、定义、框架、主线回顾）”时

不要因为这些章节看起来偏“导论”就降低研究强度。

优先用：

1. `academic-research-suite`
2. `writing-plans`
3. `writing-skills`
4. `paper-spine-audit`

重点要求：

1. 不只写定义，还要写边界、争议与后文接口
2. 不只写历史，还要写对当前具身智能路线理解的启发
3. 不只写分类，还要写为什么这种分类方式对后续技术与产业分析重要

## 6. 简化记忆法

可以直接记成下面这套：

1. 想清楚写什么：`writing-plans`
2. 不确定漏了什么：`brainstorming`
3. 系统查论文：`academic-research-suite`
4. 处理 PDF：`pdf`
5. 抓官网和截图：`playwright` + `screenshot`
6. 正式成文：`writing-skills`
7. 像审论文一样审稿：`paper-spine-audit`
8. 交稿前检查：`verification-before-completion`

## 7. 维护建议

1. 每新增一个 skill，都同步更新本文件。
2. 如果某个 skill 在实际使用中“不好用”或“适用范围变了”，直接在本文件修订。
3. 后续如果项目需要自建本地 workflow 或项目专属 skill，再把它们补到这里，而不是混在安装记录里。
