# VLA 论文清单 v0.0

更新时间：2026-07-01

## 1. 用途

本清单不是简单罗列 VLA 论文，而是为后续 `11-VLA 与机器人基础模型.md`、`18-代表性论文与模型谱系梳理.md` 的增量维护提供路线入口。后续新增论文时，应先判断它更接近哪一段主线，再决定是否新建论文卡、是否回写正文、是否更新 `data/processed/论文谱系时间线-v0.0.csv`。

## 2. 当前主线划分

### 2.1 从统一序列建模到早期机器人 foundation 路线

1. [RT-1 论文卡](D:/Projects/embodied-intelligence-report/research/papers/RT-1-论文卡-v0.0.md)
2. [RT-2 论文卡](D:/Projects/embodied-intelligence-report/research/papers/RT-2-论文卡-v0.0.md)
3. [PaLM-E 论文卡](D:/Projects/embodied-intelligence-report/research/papers/PaLM-E-论文卡-v0.0.md)

这一段的核心问题是：机器人控制是否可以被重新组织成多模态序列建模问题，以及 web-scale 知识能否迁移到动作相关接口。

### 2.2 开源化与公共基线形成

1. [OpenVLA 论文卡](D:/Projects/embodied-intelligence-report/research/papers/OpenVLA-论文卡-v0.0.md)

这一段的重点，不只是模型本身，而是 VLA 是否开始具备公共验证、复现和生态扩散条件。

### 2.3 生成式动作头与动作表示扩展

1. [Diffusion Policy 论文卡](D:/Projects/embodied-intelligence-report/research/papers/Diffusion-Policy-论文卡-v0.0.md)

这一段解决的是“动作如何表示”问题，提醒后续 VLA 更新时不要只看 backbone，也要看 action head、chunking 和实时性代价。

### 2.4 平台型基础模型与生态闭环

1. [GR00T N1 论文卡](D:/Projects/embodied-intelligence-report/research/papers/GR00T-N1-论文卡-v0.0.md)

这一段的关键，是把模型放回平台、仿真、合成数据和部署栈一体化理解，而不是只比较论文指标。

## 3. 更新规则

后续新增论文时，优先回答四个问题：

1. 它是在改进输入输出接口，还是改进动作生成头，还是改进平台闭环。
2. 它更偏研究上限，还是偏工程基线。
3. 它是否改变第 11 章对 VLA 路线主矛盾的判断。
4. 它是否需要进入 `论文谱系时间线-v0.0.csv`。

## 4. 后续待补对象

1. SmolVLA
2. Gemini Robotics / Gemini Robotics-ER
3. Helix
4. 后续 2026 年新一轮开源 VLA 或 on-device VLA 路线
