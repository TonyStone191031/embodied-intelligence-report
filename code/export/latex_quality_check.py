from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from pathlib import Path

from common import ROOT


RAW_LATEX_RE = re.compile(r"\\(?:begin|end|frac|text|mathrm|mathbb|mathbf)\b")
LOCAL_PATH_RE = re.compile(r"(?:D:/Projects/|file:///|C:/Users/)", re.IGNORECASE)


def extract_pdf_text(pdf: Path) -> str:
    pdftotext = shutil.which("pdftotext")
    if pdftotext:
        result = subprocess.run([pdftotext, str(pdf), "-"], capture_output=True, text=True, encoding="utf-8", errors="replace")
        if result.returncode == 0:
            return result.stdout
    try:
        from pypdf import PdfReader

        return "\n".join(page.extract_text() or "" for page in PdfReader(str(pdf)).pages)
    except Exception as exc:
        raise RuntimeError("Neither pdftotext nor pypdf is available") from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check LaTeX source and PDF output")
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--pdf", type=Path)
    parser.add_argument("--log", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source_dir = args.source_dir if args.source_dir.is_absolute() else ROOT / args.source_dir
    source_text = "\n".join(path.read_text(encoding="utf-8") for path in source_dir.rglob("*.tex"))
    failures: list[str] = []
    if LOCAL_PATH_RE.search(source_text):
        failures.append("source contains a machine-specific local path")

    if args.log:
        log_path = args.log if args.log.is_absolute() else ROOT / args.log
        if log_path.exists():
            log_text = log_path.read_text(encoding="utf-8", errors="replace")
            overfull = len(re.findall(r"Overfull \\hbox", log_text))
            underfull = len(re.findall(r"Underfull \\hbox", log_text))
            print(f"layout warnings: overfull_hbox={overfull}, underfull_hbox={underfull}")
            if overfull:
                failures.append(f"LaTeX log contains {overfull} overfull hbox warning(s)")
            if re.search(r"Emergency stop|Fatal error", log_text):
                failures.append("LaTeX log contains a fatal error")

    if args.pdf:
        pdf_path = args.pdf if args.pdf.is_absolute() else ROOT / args.pdf
        text = extract_pdf_text(pdf_path)
        raw_count = len(RAW_LATEX_RE.findall(text))
        local_count = len(LOCAL_PATH_RE.findall(text))
        print(f"pdf raw-latex markers: {raw_count}")
        print(f"pdf local-path markers: {local_count}")
        if raw_count:
            failures.append("PDF text contains raw LaTeX commands")
        if local_count:
            failures.append("PDF text contains machine-specific paths")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        raise SystemExit(1)
    print("LaTeX quality checks passed")


if __name__ == "__main__":
    main()
