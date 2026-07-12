from __future__ import annotations

import argparse
from pathlib import Path

from common import REPORT_ROOT
from markdown_to_latex import convert_markdown


PILOT_PREFIXES = ("01-", "05-", "20-")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Migrate the v0.2 LaTeX pilot chapters")
    parser.add_argument("--source", choices=("current",), default="current")
    parser.add_argument("--version", default="v0.2")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source_dir = REPORT_ROOT / args.source
    latex_dir = REPORT_ROOT / "latex" / "current"
    chapter_dir = latex_dir / "chapters"
    figures_dir = latex_dir / "figures"
    for prefix in PILOT_PREFIXES:
        matches = sorted(source_dir.glob(f"{prefix}*.md"))
        if len(matches) != 1:
            raise FileNotFoundError(f"Expected one chapter for {prefix}, found {len(matches)}")
        source = matches[0]
        target = chapter_dir / f"{source.stem}.tex"
        convert_markdown(source, target, figures_dir)
        print(f"Migrated: {source.name} -> {target.name}")


if __name__ == "__main__":
    main()
