from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "output" / "structured-asset-overview-v0.0.md"

CSV_FILES = [
    ROOT / "data" / "processed" / "图表资产清单-v0.0.csv",
    ROOT / "data" / "processed" / "论文谱系时间线-v0.0.csv",
    ROOT / "data" / "processed" / "产业信号日志模板-v0.0.csv",
    ROOT / "data" / "processed" / "场景ROI粗估模板-v0.0.csv",
]


def read_csv_rows(path: Path) -> tuple[list[str], list[list[str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.reader(fh)
        rows = list(reader)
    if not rows:
        return [], []
    return rows[0], rows[1:]


def section_from_csv(path: Path) -> str:
    headers, rows = read_csv_rows(path)
    lines: list[str] = []
    lines.append(f"## {path.name}")
    lines.append("")
    lines.append(f"- 列数：`{len(headers)}`")
    lines.append(f"- 数据行数：`{len(rows)}`")
    lines.append("")
    lines.append("### 字段")
    lines.append("")
    for header in headers:
        lines.append(f"- `{header}`")
    lines.append("")
    lines.append("### 前 5 行预览")
    lines.append("")
    if not headers:
        lines.append("空文件。")
        lines.append("")
        return "\n".join(lines)

    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for row in rows[:5]:
        padded = row + [""] * (len(headers) - len(row))
        lines.append("| " + " | ".join(padded[: len(headers)]) + " |")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    lines: list[str] = []
    lines.append("# 结构化资产总览 v0.0")
    lines.append("")
    lines.append("本文件由脚本自动生成，用于快速浏览当前关键结构化资产。")
    lines.append("")
    for path in CSV_FILES:
        lines.append(section_from_csv(path))
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    print(f"Wrote report to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
