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


def configure_miktex_environment(
    environment: dict[str, str], latexmk: str, version: str
) -> dict[str, str]:
    """Point MiKTeX at the disposable project-local user tree when available.

    MiKTeX keeps user configuration, data, and on-the-fly packages outside the
    repository by default.  That is inconvenient for reproducible report
    builds and, in restricted environments, can fail before XeLaTeX starts.
    The project-local tree is opt-in by existence: normal user installations
    continue to use their standard MiKTeX roots when the directory is absent.
    """
    latexmk_path = Path(latexmk)
    if "miktex" not in str(latexmk_path).lower():
        return environment

    project_root = ROOT / "tmp" / "miktex" / version
    required = {
        "MIKTEX_USERCONFIG": project_root / "config",
        "MIKTEX_USERDATA": project_root / "data",
        "MIKTEX_USERINSTALL": project_root / "install",
    }
    if not all(path.exists() for path in required.values()):
        return environment

    for key, path in required.items():
        environment[key] = str(path)

    # The system TEXMF tree is needed for binaries and fonts.  Keep the
    # project user-install tree first so package versions are coherent.
    miktex_system_root = latexmk_path.parent.parent.parent.parent
    roots = [
        required["MIKTEX_USERINSTALL"],
        project_root / "user-roots",
        miktex_system_root,
    ]
    environment["MIKTEX_USERROOTS"] = os.pathsep.join(
        str(path) for path in roots if path.exists()
    )
    environment["PATH"] = os.pathsep.join(
        [str(latexmk_path.parent), environment.get("PATH", "")]
    )
    return environment


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
    environment = configure_miktex_environment(environment, latexmk, args.version)
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
        "miktex_user_roots": {
            key: environment[key]
            for key in (
                "MIKTEX_USERCONFIG",
                "MIKTEX_USERDATA",
                "MIKTEX_USERINSTALL",
                "MIKTEX_USERROOTS",
            )
            if key in environment
        },
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
