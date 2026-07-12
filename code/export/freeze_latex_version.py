from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from common import ROOT


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Freeze the current LaTeX source as a report version")
    parser.add_argument("--version", required=True)
    parser.add_argument("--source", type=Path, default=Path("docs/report/latex/current"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source = args.source if args.source.is_absolute() else ROOT / args.source
    target = ROOT / "docs" / "report" / "versions" / args.version / "latex"
    if target.exists():
        raise SystemExit(f"Refusing to overwrite frozen LaTeX source: {target}")
    if not (source / "main.tex").exists():
        raise FileNotFoundError(f"LaTeX main file not found: {source / 'main.tex'}")
    shutil.copytree(source, target)
    manifest = {
        "version": args.version,
        "source": source.relative_to(ROOT).as_posix(),
        "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (target / "VERSION.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Frozen LaTeX source: {target}")


if __name__ == "__main__":
    main()
