# Diffusion Policy 论文卡 v0.0

更新时间：2026-07-01

## 1. 基本信息

- 论文名称：Diffusion Policy: Visuomotor Policy Learning via Action Diffusion
- 年份：2023
- 所属主线：生成式策略 / 动作扩散建模 / 机器人操作
- 对应章节：11、18

## 2. 问题设定

Diffusion Policy 试图回答：如果动作分布高度多峰、示教轨迹存在多种合理解法，传统回归式策略容易平均化失真，那么能否用 diffusion 直接建模动作分布，从而提升复杂操作的稳定性与灵活性。

## 3. 输入输出接口

- 输入：视觉观测、机器人状态、任务条件
- 输出：通过去噪过程生成的动作序列
- 接口类型：条件扩散式动作生成

## 4. 数据与训练

- 数据来源：示教与操作轨迹
- 训练方式：条件扩散/去噪学习
- 评测方式：真实或仿真操作任务成功率、鲁棒性与多模态动作生成质量

## 5. 论文在谱系中的角色

Diffusion Policy 的地位在于，它把生成式建模从图像生成清晰迁移到了动作建模，使机器人策略不再只能做均值回归。这对后续 VLA、chunking、flow matching 等路线都很有影响。

## 6. 工程与部署含义

1. 更适合处理多解任务和复杂示教分布。
2. 有助于理解为什么后续很多动作头不再是简单回归器。

## 7. 局限与后续问题

1. 推理时延与实时性压力比轻量回归头更大。
2. 低层闭环控制和高频执行预算仍是落地瓶颈。

## 8. 后续跟踪点

1. 与 VLA 统一架构如何结合。
2. diffusion 是否会被 flow matching 或更高效生成式动作头部分替代。

## 9. 参考链接

- Project: [Diffusion Policy](https://diffusion-policy.cs.columbia.edu/)
- Paper: [Diffusion Policy](https://arxiv.org/abs/2303.04137)
