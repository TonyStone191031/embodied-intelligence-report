"""Render the non-Mermaid teaching figures used by the v0.3 pilot chapters."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


BLUE = "#0077BB"
CYAN = "#33BBEE"
TEAL = "#009988"
ORANGE = "#EE7733"
RED = "#CC3311"
MAGENTA = "#EE3377"
GREY = "#666666"


@dataclass(frozen=True)
class FigureSpec:
    filename: str
    renderer: Callable[[], Figure]


def configure_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Microsoft YaHei", "SimHei", "DejaVu Sans"],
            "font.size": 9,
            "axes.titlesize": 11,
            "axes.labelsize": 9,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.unicode_minus": False,
            "savefig.bbox": "tight",
        }
    )


def normal_pdf(x: np.ndarray, mean: float, sigma: float) -> np.ndarray:
    return np.exp(-0.5 * ((x - mean) / sigma) ** 2) / (
        sigma * np.sqrt(2.0 * np.pi)
    )


def render_regression() -> Figure:
    fig, ax = plt.subplots(figsize=(6.9, 3.5), constrained_layout=True)
    x = np.linspace(-2.0, 2.0, 800)
    left = 0.5 * normal_pdf(x, -0.9, 0.22)
    right = 0.5 * normal_pdf(x, 0.9, 0.22)
    target = left + right
    ax.fill_between(x, target, color=CYAN, alpha=0.35)
    ax.plot(x, target, color=BLUE, linewidth=2.2, label="示范动作的双峰条件分布")
    ax.axvline(-0.9, color=TEAL, linestyle="--", linewidth=1.5)
    ax.axvline(0.9, color=TEAL, linestyle="--", linewidth=1.5)
    ax.axvline(0.0, color=RED, linewidth=2.0, label="MSE 最优均值")
    ax.annotate(
        "向左绕行",
        xy=(-0.9, target.max()),
        xytext=(-1.45, target.max() * 1.14),
        arrowprops={"arrowstyle": "->", "color": TEAL},
    )
    ax.annotate(
        "向右绕行",
        xy=(0.9, target.max()),
        xytext=(1.05, target.max() * 1.14),
        arrowprops={"arrowstyle": "->", "color": TEAL},
    )
    ax.annotate(
        "均值可能撞向障碍",
        xy=(0.0, target.max() * 0.04),
        xytext=(-0.48, target.max() * 0.48),
        color=RED,
        arrowprops={"arrowstyle": "->", "color": RED},
    )
    ax.set(xlabel="一维动作 $a$", ylabel=r"条件概率密度 $p(a\mid o)$")
    ax.set_yticks([])
    ax.legend(loc="upper right", frameon=False)
    ax.set_title("逐维回归为何会把多峰动作平均掉")
    return fig


def render_quantization() -> Figure:
    fig, ax = plt.subplots(figsize=(6.9, 3.7), constrained_layout=True)
    bins = 8
    x = np.linspace(-1.0, 1.0, 1000, endpoint=False)
    token = np.floor((x + 1.0) * bins / 2.0).astype(int)
    token = np.clip(token, 0, bins - 1)
    decoded = -1.0 + (2.0 * token + 1.0) / bins
    ax.step(x, decoded, where="post", color=BLUE, linewidth=2.0, label=r"解码中心 $\hat a$")
    ax.plot(x, x, color=GREY, linestyle="--", linewidth=1.2, label=r"无损映射 $\hat a=a$")
    sample = 0.37
    sample_token = int(np.floor((sample + 1.0) * bins / 2.0))
    sample_decoded = -1.0 + (2.0 * sample_token + 1.0) / bins
    ax.plot([sample, sample], [sample, sample_decoded], color=RED, linewidth=2.3)
    ax.scatter([sample], [sample], color=GREY, zorder=4)
    ax.scatter([sample], [sample_decoded], color=RED, zorder=4)
    ax.annotate(
        f"量化误差 {sample_decoded - sample:+.3f}",
        xy=(sample, (sample + sample_decoded) / 2),
        xytext=(0.46, -0.05),
        arrowprops={"arrowstyle": "->", "color": RED},
        color=RED,
    )
    for boundary in np.linspace(-1, 1, bins + 1):
        ax.axvline(boundary, color="#DDDDDD", linewidth=0.7, zorder=0)
    ax.set(
        xlabel="归一化连续动作 $a$",
        ylabel=r"token 解码后的动作 $\hat a$",
        xlim=(-1.02, 1.02),
        ylim=(-1.08, 1.08),
    )
    ax.set_title("均匀动作 token：分箱、中心解码与量化误差")
    ax.legend(loc="upper left", frameon=False)
    return fig


def render_diffusion() -> Figure:
    fig, axes = plt.subplots(1, 2, figsize=(6.9, 3.6), constrained_layout=True)
    rng = np.random.default_rng(7)
    tau = np.linspace(1.0, 0.0, 9)
    initial = rng.normal(0.0, 1.0, 12)
    targets = np.where(initial < 0, -1.0, 1.0)
    for start, target in zip(initial, targets, strict=True):
        path = target + (start - target) * tau + 0.09 * np.sin(np.pi * tau) * np.sign(start)
        axes[0].plot(np.arange(len(tau)), path, color=BLUE if target < 0 else ORANGE, alpha=0.62)
    axes[0].scatter(np.zeros_like(initial), initial, color=GREY, s=18, zorder=3, label="高斯噪声")
    axes[0].scatter(
        np.full_like(targets, len(tau) - 1),
        targets,
        c=[BLUE if value < 0 else ORANGE for value in targets],
        s=22,
        zorder=3,
        label="动作模式",
    )
    axes[0].set(
        xlabel="反向去噪步 $k$",
        ylabel="动作样本",
        title="推理：噪声逐步收敛到不同动作模式",
    )
    axes[0].legend(frameon=False, loc="upper right")

    clean = np.array([-1.0, 1.0])
    for value, color in zip(clean, [BLUE, ORANGE], strict=True):
        eps = 1.15
        alpha_bar = np.linspace(1.0, 0.0, 80)
        noised = np.sqrt(alpha_bar) * value + np.sqrt(1.0 - alpha_bar) * eps
        axes[1].plot(1.0 - alpha_bar, noised, color=color, linewidth=2.0)
    axes[1].annotate("已知训练动作", xy=(0.0, -1.0), xytext=(0.16, -0.58), arrowprops={"arrowstyle": "->"})
    axes[1].annotate("接近高斯噪声", xy=(1.0, 1.15), xytext=(0.58, 1.33), arrowprops={"arrowstyle": "->"})
    axes[1].set(
        xlabel="前向加噪强度",
        ylabel=r"$A^\tau$",
        title="训练：从干净动作构造带噪样本",
    )
    fig.suptitle("Diffusion action：训练加噪与推理去噪不是同一方向", fontsize=12)
    return fig


def render_flow_matching() -> Figure:
    fig, axes = plt.subplots(1, 2, figsize=(6.9, 3.6), constrained_layout=True)
    tau = np.linspace(0.0, 1.0, 80)
    starts = np.array([-1.7, -0.8, -0.25, 0.25, 0.8, 1.7])
    targets = np.where(starts < 0, -1.0, 1.0)
    for start, target in zip(starts, targets, strict=True):
        path = (1.0 - tau) * start + tau * target
        axes[0].plot(tau, path, color=BLUE if target < 0 else ORANGE, linewidth=1.8)
        for index in (20, 45, 68):
            axes[0].annotate(
                "",
                xy=(tau[index + 2], path[index + 2]),
                xytext=(tau[index], path[index]),
                arrowprops={"arrowstyle": "->", "color": BLUE if target < 0 else ORANGE},
            )
    axes[0].set(
        xlabel=r"连续时间 $\tau$",
        ylabel=r"动作状态 $A^\tau$",
        title=r"训练目标：在路径上学习速度 $u_\tau$",
    )

    steps = 10
    dt = 1.0 / steps
    values = [-1.55, 0.62]
    colors = [BLUE, ORANGE]
    for value, color in zip(values, colors, strict=True):
        current = value
        target = -1.0 if value < 0 else 1.0
        history = [current]
        for _ in range(steps):
            velocity = target - current
            current = current + dt * velocity
            history.append(current)
        axes[1].plot(range(steps + 1), history, marker="o", markersize=3, color=color)
    axes[1].set(
        xlabel="Euler 积分步",
        ylabel="动作估计",
        title="推理：重复评估速度场并数值积分",
    )
    axes[1].text(5.1, 0.02, "不是一次前向传播", color=RED, ha="center")
    fig.suptitle("Flow matching action：学习速度场，再沿 ODE 生成动作块", fontsize=12)
    return fig


def add_box(ax: Axes, xy: tuple[float, float], width: float, height: float, text: str, color: str) -> None:
    box = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle="round,pad=0.02,rounding_size=0.02",
        linewidth=1.2,
        edgecolor=color,
        facecolor=f"{color}18",
    )
    ax.add_patch(box)
    ax.text(xy[0] + width / 2, xy[1] + height / 2, text, ha="center", va="center", fontsize=8.5)


def add_arrow(ax: Axes, start: tuple[float, float], end: tuple[float, float], color: str = GREY) -> None:
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=11, linewidth=1.2, color=color))


def render_octo() -> Figure:
    fig, ax = plt.subplots(figsize=(6.9, 4.6), constrained_layout=True)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    add_box(ax, (0.03, 0.70), 0.17, 0.12, "语言指令\n/目标图像", TEAL)
    add_box(ax, (0.03, 0.48), 0.17, 0.12, "相机历史\n+ 本体状态", BLUE)
    add_box(ax, (0.25, 0.70), 0.18, 0.12, "任务编码器\nTask tokens", TEAL)
    add_box(ax, (0.25, 0.48), 0.18, 0.12, "视觉/状态编码器\nObservation tokens", BLUE)
    add_box(ax, (0.49, 0.54), 0.22, 0.22, "Octo Transformer\n块级注意力\n(block-wise attention)", MAGENTA)
    add_box(ax, (0.77, 0.65), 0.19, 0.12, "Readout tokens\n+ diffusion head", ORANGE)
    add_box(ax, (0.77, 0.43), 0.19, 0.12, "连续动作块\n" + r"$A_{t:t+H-1}$", RED)
    add_arrow(ax, (0.20, 0.76), (0.25, 0.76), TEAL)
    add_arrow(ax, (0.20, 0.54), (0.25, 0.54), BLUE)
    add_arrow(ax, (0.43, 0.76), (0.49, 0.69), TEAL)
    add_arrow(ax, (0.43, 0.54), (0.49, 0.60), BLUE)
    add_arrow(ax, (0.71, 0.65), (0.77, 0.71), MAGENTA)
    add_arrow(ax, (0.865, 0.65), (0.865, 0.55), ORANGE)

    ax.plot([0.04, 0.96], [0.33, 0.33], color="#BBBBBB", linewidth=1.0)
    ax.text(0.03, 0.29, "目标域微调：保留主干接口，替换或增加 token group / action head", fontsize=9, weight="bold")
    add_box(ax, (0.09, 0.08), 0.21, 0.12, "新传感器\n新增 token group", CYAN)
    add_box(ax, (0.40, 0.08), 0.21, 0.12, "预训练 Octo 主干\n参数初始化", MAGENTA)
    add_box(ax, (0.71, 0.08), 0.21, 0.12, "新动作空间\n新 diffusion head", ORANGE)
    add_arrow(ax, (0.30, 0.14), (0.40, 0.14), CYAN)
    add_arrow(ax, (0.61, 0.14), (0.71, 0.14), MAGENTA)
    ax.set_title("Octo 的模块化主干与新观测/动作空间适配（依据原论文 Fig. 2 改绘）", pad=10)
    return fig


def render_contact_friction() -> Figure:
    fig, axes = plt.subplots(1, 2, figsize=(6.9, 3.7), constrained_layout=True)
    ax = axes[0]
    ax.axhline(0, color=GREY, linewidth=2.0)
    ax.add_patch(plt.Rectangle((-0.9, 0.42), 0.55, 0.28, facecolor="#D7EAF5", edgecolor=BLUE))
    ax.add_patch(plt.Rectangle((0.35, 0.0), 0.55, 0.28, facecolor="#FCE2D8", edgecolor=ORANGE))
    ax.annotate("间隙 " + r"$\phi>0$" + "\n法向力 " + r"$\lambda_n=0$", xy=(-0.62, 0.39), xytext=(-0.62, -0.42), ha="center", arrowprops={"arrowstyle": "<->"})
    ax.annotate("接触 " + r"$\phi=0$" + "\n可有 " + r"$\lambda_n>0$", xy=(0.62, 0.28), xytext=(0.62, 0.63), ha="center", arrowprops={"arrowstyle": "->", "color": RED})
    ax.set(xlim=(-1.05, 1.05), ylim=(-0.58, 0.86), title="互补条件排除两种不可能状态")
    ax.axis("off")

    ax = axes[1]
    normal = np.linspace(0, 2.2, 100)
    mu = 0.55
    ax.fill_between(normal, -mu * normal, mu * normal, color=CYAN, alpha=0.35, label="可行摩擦锥")
    ax.plot(normal, mu * normal, color=BLUE, linewidth=1.8)
    ax.plot(normal, -mu * normal, color=BLUE, linewidth=1.8)
    ax.scatter([1.45, 1.45, 1.2], [0.22, mu * 1.45, 0.98], c=[TEAL, ORANGE, RED], zorder=4)
    ax.annotate("粘着", xy=(1.45, 0.22), xytext=(0.62, 0.12), arrowprops={"arrowstyle": "->"})
    ax.annotate("滑动边界", xy=(1.45, mu * 1.45), xytext=(0.78, 1.02), arrowprops={"arrowstyle": "->"})
    ax.annotate("不可行", xy=(1.2, 0.98), xytext=(1.58, 1.12), color=RED, arrowprops={"arrowstyle": "->", "color": RED})
    ax.axhline(0, color="#BBBBBB", linewidth=0.8)
    ax.set(xlabel=r"法向力 $\lambda_n$", ylabel=r"切向力 $\lambda_t$", xlim=(0, 2.25), ylim=(-1.25, 1.25), title=r"$|\lambda_t|\leq\mu\lambda_n$ 的二维截面")
    return fig


def render_impedance_admittance() -> Figure:
    fig, ax = plt.subplots(figsize=(6.9, 3.8), constrained_layout=True)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.03, 0.82, "阻抗：位移误差 → 期望交互力/力矩", fontsize=10, weight="bold")
    add_box(ax, (0.05, 0.58), 0.18, 0.13, r"$e,\dot e$" + "\n位姿误差", BLUE)
    add_box(ax, (0.34, 0.58), 0.25, 0.13, r"$F_c=-K_de-D_d\dot e$" + "\n虚拟弹簧--阻尼", MAGENTA)
    add_box(ax, (0.70, 0.58), 0.24, 0.13, r"$\tau=J^\top F_c$" + "\n力矩接口", RED)
    add_arrow(ax, (0.23, 0.645), (0.34, 0.645), BLUE)
    add_arrow(ax, (0.59, 0.645), (0.70, 0.645), MAGENTA)

    ax.text(0.03, 0.38, "导纳：测得交互力 → 新的位置/速度命令", fontsize=10, weight="bold")
    add_box(ax, (0.05, 0.13), 0.18, 0.13, r"$F_{ext}$" + "\n力传感器", ORANGE)
    add_box(ax, (0.34, 0.13), 0.25, 0.13, r"$M_d\ddot x+D_d\dot x+K_dx=F$" + "\n虚拟动力学积分", TEAL)
    add_box(ax, (0.70, 0.13), 0.24, 0.13, r"$x_d$ 或 $\dot x_d$" + "\n位置/速度内环", BLUE)
    add_arrow(ax, (0.23, 0.195), (0.34, 0.195), ORANGE)
    add_arrow(ax, (0.59, 0.195), (0.70, 0.195), TEAL)
    ax.text(0.50, 0.48, "接口不同，稳定性仍共同受环境刚度、采样延迟和内环带宽影响", ha="center", color=GREY)
    return fig


def figure_specs() -> tuple[FigureSpec, ...]:
    return (
        FigureSpec("v0.3-23-回归多峰平均", render_regression),
        FigureSpec("v0.3-23-动作token量化", render_quantization),
        FigureSpec("v0.3-23-扩散动作生成", render_diffusion),
        FigureSpec("v0.3-23-流匹配动作生成", render_flow_matching),
        FigureSpec("v0.3-23-Octo模块化架构", render_octo),
        FigureSpec("v0.3-06-接触互补与摩擦锥", render_contact_friction),
        FigureSpec("v0.3-06-阻抗与导纳接口", render_impedance_admittance),
    )


def render_all(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    configure_style()
    for spec in figure_specs():
        figure = spec.renderer()
        figure.savefig(output_dir / f"{spec.filename}.png", dpi=300)
        figure.savefig(output_dir / f"{spec.filename}.pdf")
        plt.close(figure)


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[2]
    default_output = repo_root / "docs" / "report" / "latex" / "current" / "figures"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=default_output)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    render_all(args.output_dir.resolve())


if __name__ == "__main__":
    main()
