from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from common import ROOT


TEXLIVE_BIN_CANDIDATES = (
    Path("C:/texlive/2026/bin/windows"),
    Path("C:/texlive/2025/bin/windows"),
)
TEXLIVE_PERL_CANDIDATES = (
    Path("C:/texlive/2026/tlpkg/tlperl/bin"),
    Path("C:/texlive/2025/tlpkg/tlperl/bin"),
)


def latex_source_dir(version: str, source: str) -> Path:
    if source == "current":
        path = ROOT / "docs" / "report" / "latex" / "current"
    elif source == "frozen":
        path = ROOT / "docs" / "report" / "versions" / version / "latex"
    else:
        raise ValueError("source must be current or frozen")
    if not path.exists():
        raise FileNotFoundError(f"LaTeX source directory not found: {path}")
    return path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def find_latexmk() -> tuple[str, Path | None]:
    discovered = shutil.which("latexmk")
    if discovered:
        return discovered, None
    for candidate in TEXLIVE_BIN_CANDIDATES:
        executable = candidate / "latexmk.exe"
        if executable.exists():
            return str(executable), candidate
    raise SystemExit(
        "latexmk was not found. Install TeX Live with XeLaTeX and latexmk, "
        "then rerun this command."
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a LaTeX report with XeLaTeX")
    parser.add_argument("--version", required=True)
    parser.add_argument("--source", choices=("current", "frozen"), default="current")
    return parser.parse_args()


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
        sys.stderr.reconfigure(errors="replace")
    args = parse_args()
    source_dir = latex_source_dir(args.version, args.source)
    main_file = source_dir / "main.tex"
    if not main_file.exists():
        raise FileNotFoundError(f"LaTeX main file not found: {main_file}")

    latexmk, texlive_bin = find_latexmk()

    build_dir = ROOT / "tmp" / "latex-build" / args.version
    build_dir.mkdir(parents=True, exist_ok=True)
    output_dir = ROOT / "output" / "exports" / args.version
    output_dir.mkdir(parents=True, exist_ok=True)
    output_pdf = output_dir / f"embodied-intelligence-report-{args.version}.pdf"
    manifest_path = output_dir / "latex-build-manifest.json"

    command = [
        latexmk,
        "-xelatex",
        "-g",
        "-halt-on-error",
        "-file-line-error",
        f"-outdir={build_dir}",
        "main.tex",
    ]
    environment = os.environ.copy()
    if texlive_bin:
        perl_bin = next((path for path in TEXLIVE_PERL_CANDIDATES if path.exists()), None)
        path_entries = [str(texlive_bin)]
        if perl_bin:
            path_entries.append(str(perl_bin))
        path_entries.append(environment.get("PATH", ""))
        environment["PATH"] = os.pathsep.join(path_entries)
    result = subprocess.run(
        command,
        cwd=source_dir,
        env=environment,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    log_path = build_dir / "main.log"
    manifest = {
        "version": args.version,
        "source": args.source,
        "source_dir": source_dir.relative_to(ROOT).as_posix(),
        "main_file": main_file.relative_to(ROOT).as_posix(),
        "command": command,
        "latexmk": latexmk,
        "returncode": result.returncode,
        "built_at_utc": datetime.now(timezone.utc).isoformat(),
        "log": log_path.relative_to(ROOT).as_posix() if log_path.exists() else None,
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        raise SystemExit(f"LaTeX build failed; see {log_path}")

    built_pdf = build_dir / "main.pdf"
    if not built_pdf.exists():
        raise FileNotFoundError(f"LaTeX build completed without PDF: {built_pdf}")
    shutil.copy2(built_pdf, output_pdf)
    manifest["output_pdf"] = output_pdf.relative_to(ROOT).as_posix()
    manifest["output_sha256"] = sha256(output_pdf)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"LaTeX PDF written: {output_pdf}")
    print(f"Build manifest written: {manifest_path}")


if __name__ == "__main__":
    main()
