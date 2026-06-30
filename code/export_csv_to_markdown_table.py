from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass
class ExportSpec:
    source: Path
    target: Path
    title: str
    intro: str


EXPORTS = [
    ExportSpec(
        source=ROOT / "data" / "processed" / "论文谱系时间线-v0.0.csv",
        target=ROOT / "docs" / "report" / "current" / "tables" / "18-论文谱系时间线表-脚本生成版.md",
        title="表 18-2 论文谱系时间线表（脚本生成版）",
        intro="本表由 `code/export_csv_to_markdown_table.py` 从 `data/processed/论文谱系时间线-v0.0.csv` 自动生成。",
    ),
    ExportSpec(
        source=ROOT / "data" / "processed" / "产业信号日志模板-v0.0.csv",
        target=ROOT / "docs" / "report" / "current" / "tables" / "24-产业信号日志模板-脚本生成版.md",
        title="表 24-2 产业信号日志模板（脚本生成版）",
        intro="本表由 `code/export_csv_to_markdown_table.py` 从 `data/processed/产业信号日志模板-v0.0.csv` 自动生成。",
    ),
    ExportSpec(
        source=ROOT / "data" / "processed" / "企业跟踪框架-v0.0.csv",
        target=ROOT / "docs" / "report" / "current" / "tables" / "20-企业统一分析模板-脚本生成版.md",
        title="表 20-1 企业统一分析模板（脚本生成版）",
        intro="本表由 `code/export_csv_to_markdown_table.py` 从 `data/processed/企业跟踪框架-v0.0.csv` 自动生成。",
    ),
    ExportSpec(
        source=ROOT / "data" / "processed" / "企业季度跟踪表-v0.0.csv",
        target=ROOT / "docs" / "report" / "current" / "tables" / "20-企业季度跟踪表模板-脚本生成版.md",
        title="表 20-2 企业季度跟踪表模板（脚本生成版）",
        intro="本表由 `code/export_csv_to_markdown_table.py` 从 `data/processed/企业季度跟踪表-v0.0.csv` 自动生成。",
    ),
    ExportSpec(
        source=ROOT / "data" / "processed" / "场景ROI粗估模板-v0.0.csv",
        target=ROOT / "docs" / "report" / "current" / "tables" / "23-场景ROI粗估模板-脚本生成版.md",
        title="表 23-2 场景 ROI 粗估模板（脚本生成版）",
        intro="本表由 `code/export_csv_to_markdown_table.py` 从 `data/processed/场景ROI粗估模板-v0.0.csv` 自动生成。",
    ),
]


def read_csv(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.reader(fh))


def to_markdown(rows: list[list[str]], title: str, intro: str) -> str:
    if not rows:
        return f"# {title}\n\n{intro}\n\n空表。\n"

    headers = rows[0]
    body = rows[1:]

    lines: list[str] = []
    lines.append(f"# {title}")
    lines.append("")
    lines.append(intro)
    lines.append("")
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for row in body:
        padded = row + [""] * (len(headers) - len(row))
        lines.append("| " + " | ".join(padded[: len(headers)]) + " |")
    lines.append("")
    return "\n".join(lines)


def export_one(spec: ExportSpec) -> None:
    rows = read_csv(spec.source)
    content = to_markdown(rows, spec.title, spec.intro)
    spec.target.parent.mkdir(parents=True, exist_ok=True)
    spec.target.write_text(content, encoding="utf-8")


def main() -> None:
    for spec in EXPORTS:
        export_one(spec)
        print(f"Exported: {spec.target}")


if __name__ == "__main__":
    main()
