from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from common import build_config, ensure_output_dir, parse_args_with_version


SCRIPTS = [
    "build_report_bundle.py",
    "export_docx.py",
    "export_pdf.py",
]


def run_script(script_name: str, version: str, source: str) -> None:
    script_path = Path(__file__).resolve().parent / script_name
    cmd = [sys.executable, str(script_path), "--version", version, "--source", source]
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)


def pick_actual_output(path: Path) -> Path:
    regenerated = path.with_name(f"{path.stem}-regenerated{path.suffix}")
    if regenerated.exists() and (not path.exists() or regenerated.stat().st_mtime >= path.stat().st_mtime):
        return regenerated
    return path


def main() -> None:
    args = parse_args_with_version(default_source="frozen")
    config = build_config(args.version, args.source)
    ensure_output_dir(config.output_dir)

    for script_name in SCRIPTS:
        run_script(script_name, config.version, config.source)

    print("")
    print("Export complete:")
    print(f"  Bundle: {config.bundle_path}")
    print(f"  Manifest: {config.manifest_path}")
    print(f"  DOCX: {pick_actual_output(config.docx_path)}")
    print(f"  PDF: {pick_actual_output(config.pdf_path)}")


if __name__ == "__main__":
    main()
