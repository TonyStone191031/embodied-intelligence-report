from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "processed" / "图表资产清单-v0.0.csv"
OUTPUT_PATH = ROOT / "output" / "asset-registry-check-v0.0.md"


@dataclass
class AssetRow:
    asset_id: str
    chapter: str
    asset_type: str
    title: str
    source_path: str
    status: str
    next_action: str

    @property
    def resolved_path(self) -> Path:
        return ROOT / self.source_path

    @property
    def exists(self) -> bool:
        return self.resolved_path.exists()


def load_rows() -> list[AssetRow]:
    rows: list[AssetRow] = []
    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            rows.append(
                AssetRow(
                    asset_id=row["asset_id"].strip(),
                    chapter=row["chapter"].strip(),
                    asset_type=row["asset_type"].strip(),
                    title=row["title"].strip(),
                    source_path=row["source_path"].strip(),
                    status=row["status"].strip(),
                    next_action=row["next_action"].strip(),
                )
            )
    return rows


def build_report(rows: list[AssetRow]) -> str:
    total = len(rows)
    existing = sum(1 for row in rows if row.exists)
    missing = total - existing

    lines: list[str] = []
    lines.append("# 图表资产清单校验报告 v0.0")
    lines.append("")
    lines.append("## 汇总")
    lines.append("")
    lines.append(f"- 清单总数：`{total}`")
    lines.append(f"- 路径存在：`{existing}`")
    lines.append(f"- 路径缺失：`{missing}`")
    lines.append("")
    lines.append("## 明细")
    lines.append("")
    lines.append("| asset_id | chapter | type | title | path_exists | source_path |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for row in rows:
        exists_text = "yes" if row.exists else "no"
        lines.append(
            f"| {row.asset_id} | {row.chapter} | {row.asset_type} | "
            f"{row.title} | {exists_text} | `{row.source_path}` |"
        )

    lines.append("")
    lines.append("## 缺失项")
    lines.append("")
    missing_rows = [row for row in rows if not row.exists]
    if not missing_rows:
        lines.append("当前清单中的源路径均存在。")
    else:
        for row in missing_rows:
            lines.append(
                f"- `{row.asset_id}` `{row.title}` 缺少源文件：`{row.source_path}`"
            )

    lines.append("")
    lines.append("## 说明")
    lines.append("")
    lines.append(
        "本报告只校验清单路径是否存在，不校验正文挂载状态、图表语义质量或版本一致性。"
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    rows = load_rows()
    report = build_report(rows)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(report, encoding="utf-8")
    print(f"Wrote report to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
