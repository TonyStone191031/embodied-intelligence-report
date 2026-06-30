# 结构化资产总览 v0.0

本文件由脚本自动生成，用于快速浏览当前关键结构化资产。

## 图表资产清单-v0.0.csv

- 列数：`7`
- 数据行数：`28`

### 字段

- `asset_id`
- `chapter`
- `asset_type`
- `title`
- `source_path`
- `status`
- `next_action`

### 前 5 行预览

| asset_id | chapter | asset_type | title | source_path | status | next_action |
| --- | --- | --- | --- | --- | --- | --- |
| fig-08-01 | 08 | diagram | 系统分层接口图 | assets/diagrams/08-系统分层接口图.mmd | 已建源文件并已挂正文 | 后续可评估是否转高保真图 |
| fig-09-01 | 09 | diagram | 感知到动作的状态漏斗图 | assets/diagrams/09-感知到动作的状态漏斗图.mmd | 已建源文件 | 继续复核正文说明 |
| fig-10-01 | 10 | diagram | 世界模型关系图 | assets/diagrams/10-世界模型关系图.mmd | 已建源文件 | 继续复核正文说明 |
| fig-11-01 | 11 | diagram | VLA统一接口图 | assets/diagrams/11-VLA统一接口图.mmd | 已建源文件并已挂正文 | 后续可扩成模型对照图 |
| fig-14-01 | 14 | diagram | sim2real失效模式图 | assets/diagrams/14-sim2real失效模式图.mmd | 已建源文件并已挂正文 | 后续可配评测矩阵 |

## 论文谱系时间线-v0.0.csv

- 列数：`7`
- 数据行数：`11`

### 字段

- `year`
- `paper`
- `route`
- `layer`
- `role`
- `chapter`
- `source_note`

### 前 5 行预览

| year | paper | route | layer | role | chapter | source_note |
| --- | --- | --- | --- | --- | --- | --- |
| 2022 | SayCan | language_planning | planning | 把语言规划与技能可供性结合 | 12 | 章节中已引用 |
| 2022 | Code as Policies | programmatic_planning | planning | 把语言输出约束到可执行程序接口 | 12 | 章节中已引用 |
| 2022 | RT-1 | vla_foundation | model | 早期机器人 transformer 路线代表 | 11 | 章节中已引用 |
| 2023 | DreamerV3 | world_model | model | 世界模型与潜空间规划路线的重要代表 | 10 | 后续应继续补章节交叉引用 |
| 2023 | PaLM-E | embodied_multimodal | model | 把多模态基础模型叙事推进到具身接口 | 21 | 章节中已引用 |

## 产业信号日志模板-v0.0.csv

- 列数：`7`
- 数据行数：`4`

### 字段

- `time`
- `signal_type`
- `event`
- `impact_layer`
- `impact_chapter`
- `judgment_action`
- `notes`

### 前 5 行预览

| time | signal_type | event | impact_layer | impact_chapter | judgment_action | notes |
| --- | --- | --- | --- | --- | --- | --- |
| 例如2026Q3 | 融资/估值 | 某公司完成新融资 | 情绪层/资源层 | 21|22|24 | 记录即可/待观察 | 暂不直接上修技术判断 |
| 例如2026Q3 | 基础设施/平台 | 某平台发布新训练或部署接口 | 能力底座层 | 11|14|19|24 | 可局部回调判断 | 看是否改变公共接口 |
| 例如2026Q3 | 真实部署 | 出现高可信客户现场案例 | 交付层 | 20|21|22|23|24 | 可上修对应企业或场景判断 | 需记录证据强度 |
| 例如2026Q3 | 标准/政策 | 新规改变场景准入或安全责任 | 制度边界层 | 16|23|24|26 | 触发章节复审 | 优先记录行为边界变化 |

## 场景ROI粗估模板-v0.0.csv

- 列数：`7`
- 数据行数：`6`

### 字段

- `scene`
- `task_unit`
- `labor_cost_pattern`
- `error_cost`
- `deployment_and_maintenance_cost`
- `value_density`
- `initial_conclusion`

### 前 5 行预览

| scene | task_unit | labor_cost_pattern | error_cost | deployment_and_maintenance_cost | value_density | initial_conclusion |
| --- | --- | --- | --- | --- | --- | --- |
| 制造 | 例如上下料/分拣/工位协作 | 高频重复可量化 | 中 | 中 | 高 | 适合优先验证 |
| 仓储物流 | 例如搬运/分拣/补货 | 高频节拍明确 | 中 | 中 | 高 | 适合优先验证 |
| 巡检 | 例如例行巡检/危险环境检查 | 人工替代价值较高 | 中 | 中 | 中高 | 适合半自主先切入 |
| 农业 | 例如采摘/喷洒/巡田 | 季节性且环境变化大 | 中 | 中高 | 中 | 需任务单元化后判断 |
| 家庭服务 | 例如收纳/清洁/搬运 | 单次价值密度偏低 | 高 | 高 | 低到中 | 更适合作为长期研发目标 |
