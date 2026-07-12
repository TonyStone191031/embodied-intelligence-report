from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
REPORT_ROOT = ROOT / "docs" / "report"
OUTPUT_ROOT = ROOT / "output" / "exports"
WINDOWS_SIMFANG = Path("C:/Windows/Fonts/simfang.ttf")
WINDOWS_CONSOLAS = Path("C:/Windows/Fonts/consola.ttf")
WINDOWS_SEGOE_SYMBOL = Path("C:/Windows/Fonts/seguisym.ttf")

CHAPTER_RE = re.compile(r"^(?P<num>\d{2})-(?P<title>.+)\.md$")
MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
INLINE_MATH_RE = re.compile(r"\\\((.+?)\\\)")
INLINE_CODE_RE = re.compile(r"`([^`]+)`")
FORMULA_BLOCK_COMMAND_RE = re.compile(
    r"\\(?:begin|end|frac|sqrt|mathbb|mathcal|mathbf|mathrm|operatorname|argmax|argmin|pi|theta|tau|lambda|sigma|sum|min|max)\b"
)

SUBSCRIPT_MAP = {
    "0": "₀",
    "1": "₁",
    "2": "₂",
    "3": "₃",
    "4": "₄",
    "5": "₅",
    "6": "₆",
    "7": "₇",
    "8": "₈",
    "9": "₉",
    "a": "ₐ",
    "e": "ₑ",
    "h": "ₕ",
    "i": "ᵢ",
    "j": "ⱼ",
    "k": "ₖ",
    "l": "ₗ",
    "m": "ₘ",
    "n": "ₙ",
    "o": "ₒ",
    "p": "ₚ",
    "r": "ᵣ",
    "s": "ₛ",
    "t": "ₜ",
    "u": "ᵤ",
    "v": "ᵥ",
    "x": "ₓ",
    "β": "ᵦ",
    "γ": "ᵧ",
    "ρ": "ᵨ",
    "φ": "ᵩ",
    "χ": "ᵪ",
}

SUPERSCRIPT_MAP = {
    "0": "⁰",
    "1": "¹",
    "2": "²",
    "3": "³",
    "4": "⁴",
    "5": "⁵",
    "6": "⁶",
    "7": "⁷",
    "8": "⁸",
    "9": "⁹",
    "+": "⁺",
    "-": "⁻",
    "=": "⁼",
    "(": "⁽",
    ")": "⁾",
    "n": "ⁿ",
    "i": "ⁱ",
    "T": "ᵀ",
}


@dataclass(frozen=True)
class ExportConfig:
    version: str
    source: str
    source_dir: Path
    output_dir: Path
    rendered_assets_dir: Path
    bundle_path: Path
    manifest_path: Path
    docx_path: Path
    pdf_path: Path


def build_config(version: str, source: str) -> ExportConfig:
    if source not in {"current", "frozen"}:
        raise ValueError("source must be one of: current, frozen")

    if source == "current":
        source_dir = REPORT_ROOT / "current"
    else:
        source_dir = REPORT_ROOT / "versions" / version

    if not source_dir.exists():
        raise FileNotFoundError(f"Report source directory not found: {source_dir}")

    output_dir = OUTPUT_ROOT / version
    stem = f"embodied-intelligence-report-{version}"
    return ExportConfig(
        version=version,
        source=source,
        source_dir=source_dir,
        output_dir=output_dir,
        rendered_assets_dir=output_dir / "rendered-assets",
        bundle_path=output_dir / "report-bundle.md",
        manifest_path=output_dir / "report-bundle.manifest.json",
        docx_path=output_dir / f"{stem}.docx",
        pdf_path=output_dir / f"{stem}.pdf",
    )


def ensure_output_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def chapter_sort_key(path: Path) -> tuple[int, str]:
    match = CHAPTER_RE.match(path.name)
    if not match:
        return (9999, path.name)
    return (int(match.group("num")), path.name)


def list_chapter_files(source_dir: Path) -> list[Path]:
    files = [path for path in source_dir.iterdir() if path.is_file() and CHAPTER_RE.match(path.name)]
    return sorted(files, key=chapter_sort_key)


def list_support_markdown_files(source_dir: Path, subdir: str) -> list[Path]:
    base = source_dir / subdir
    if not base.exists():
        return []
    files = [path for path in base.iterdir() if path.is_file() and path.suffix.lower() == ".md"]
    return sorted(files, key=lambda p: p.name)


def list_support_files(source_dir: Path, subdir: str) -> list[Path]:
    base = source_dir / subdir
    if not base.exists():
        return []
    files = [path for path in base.iterdir() if path.is_file()]
    return sorted(files, key=lambda p: p.name)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def choose_writable_output_path(path: Path) -> Path:
    if not path.exists():
        return path
    try:
        with path.open("ab"):
            return path
    except PermissionError:
        return path.with_name(f"{path.stem}-regenerated{path.suffix}")


def is_probably_local_target(target: str) -> bool:
    lower = target.lower()
    return (
        lower.startswith("d:/projects/")
        or lower.startswith("assets/")
        or lower.startswith("docs/")
        or lower.startswith("research/")
        or lower.startswith("data/")
        or lower.startswith("output/")
        or lower.startswith("/")
    )


def is_web_target(target: str) -> bool:
    lower = target.lower()
    return lower.startswith("http://") or lower.startswith("https://")


def resolve_repo_target(target: str) -> Path | None:
    cleaned = target.strip().strip("<>").replace("\\", "/")
    if re.match(r"^[A-Za-z]:/", cleaned):
        return Path(cleaned)
    if cleaned.startswith("/"):
        return Path(cleaned)
    if is_probably_local_target(cleaned):
        return ROOT / cleaned
    return None


def _subscript_or_literal(token: str) -> str:
    if token and token.isdigit() and all(char in SUBSCRIPT_MAP for char in token):
        return "".join(SUBSCRIPT_MAP[char] for char in token)
    return "_(" + token + ")"


def _superscript_or_literal(token: str) -> str:
    if token and all(char in SUPERSCRIPT_MAP for char in token):
        return "".join(SUPERSCRIPT_MAP[char] for char in token)
    return "^(" + token + ")"


def latex_to_readable(text: str) -> str:
    value = text.strip()
    value = value.replace(r"\left", "").replace(r"\right", "")

    macro_extractors = [
        (r"\\ddot\{([^{}]+)\}", lambda m: m.group(1) + "\u0308"),
        (r"\\dot\{([^{}]+)\}", lambda m: m.group(1) + "\u0307"),
        (r"\\hat\{([^{}]+)\}", lambda m: m.group(1) + "\u0302"),
        (r"\\bar\{([^{}]+)\}", lambda m: m.group(1) + "\u0304"),
        (r"\\mathbf\{([^{}]+)\}", lambda m: m.group(1)),
        (r"\\mathrm\{([^{}]+)\}", lambda m: m.group(1)),
        (r"\\text\{([^{}]+)\}", lambda m: m.group(1)),
    ]
    for pattern, repl in macro_extractors:
        value = re.sub(pattern, repl, value)

    replacements = {
        r"\tau": "τ",
        r"\theta": "θ",
        r"\phi": "φ",
        r"\alpha": "α",
        r"\beta": "β",
        r"\gamma": "γ",
        r"\lambda": "λ",
        r"\mu": "μ",
        r"\sigma": "σ",
        r"\pi": "π",
        r"\omega": "ω",
        r"\in": "∈",
        r"\mid": "|",
        r"\sim": "~",
        r"\cdot": "·",
        r"\times": "×",
        r"\leq": "≤",
        r"\le": "≤",
        r"\geq": "≥",
        r"\ge": "≥",
        r"\neq": "≠",
        r"\approx": "≈",
        r"\rightarrow": "→",
        r"\to": "→",
        r"\mapsto": "↦",
        r"\sum": "Σ",
        r"\max": "max",
        r"\min": "min",
        r"\log": "log",
        r"\argmax": "arg max",
        r"\argmin": "arg min",
        r"\mathbb{R}": "R",
        r"\quad": "    ",
        r"\qquad": "        ",
        r"\{": "{",
        r"\}": "}",
    }
    for src, dst in replacements.items():
        value = value.replace(src, dst)

    value = value.replace(r"\begin{bmatrix}", "[")
    value = value.replace(r"\end{bmatrix}", "]")
    value = value.replace(r"\begin{matrix}", "")
    value = value.replace(r"\end{matrix}", "")
    value = value.replace(r"\\", "\n")

    value = re.sub(r"\^\{([^{}]+)\}", lambda m: _superscript_or_literal(m.group(1)), value)
    value = re.sub(r"\^([A-Za-z0-9])", lambda m: SUPERSCRIPT_MAP.get(m.group(1), "^" + m.group(1)), value)
    value = re.sub(r"_\{([^{}]+)\}", lambda m: _subscript_or_literal(m.group(1)), value)
    value = re.sub(r"_([A-Za-z0-9βγρφχ])", lambda m: SUBSCRIPT_MAP.get(m.group(1), "_" + m.group(1)), value)
    value = re.sub(r"\\([A-Za-z]+)", r"\1", value)

    lines = []
    for raw_line in value.splitlines():
        line = re.sub(r"[ \t]+", " ", raw_line).strip()
        if line:
            lines.append(line)
    return "\n".join(lines).strip()


def is_formula_like_block(text: str) -> bool:
    return bool(FORMULA_BLOCK_COMMAND_RE.search(text))


def normalize_inline_math(text: str) -> str:
    return INLINE_MATH_RE.sub(lambda m: latex_to_readable(m.group(1)), text)


def normalize_inline_code(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        content = match.group(1)
        if "\\" in content or "{" in content or "}" in content:
            return latex_to_readable(content)
        return content

    return INLINE_CODE_RE.sub(repl, text)


def normalize_markup_text(text: str) -> str:
    text = normalize_inline_math(text)
    return normalize_inline_code(text)


def split_markdown_fragments(text: str) -> list[tuple[str, str, str | None]]:
    def image_repl(match: re.Match[str]) -> str:
        alt = match.group(1).strip()
        target = match.group(2).strip()
        label = alt or Path(target).name
        return f"[图片: {label}]"

    fragments: list[tuple[str, str, str | None]] = []
    sanitized = IMAGE_RE.sub(image_repl, text)
    cursor = 0
    for match in MARKDOWN_LINK_RE.finditer(sanitized):
        if match.start() > cursor:
            plain = normalize_markup_text(sanitized[cursor:match.start()])
            if plain:
                fragments.append(("text", plain, None))
        label = normalize_markup_text(match.group(1).strip())
        target = match.group(2).strip()
        if is_probably_local_target(target):
            if label:
                fragments.append(("text", label, None))
        else:
            fragments.append(("link", label, target))
        cursor = match.end()
    if cursor < len(sanitized):
        plain = normalize_markup_text(sanitized[cursor:])
        if plain:
            fragments.append(("text", plain, None))
    return fragments


def normalize_links(text: str, drop_local_paths: bool = True, show_external_targets: bool = False) -> str:
    parts: list[str] = []
    for kind, label, target in split_markdown_fragments(text):
        if kind == "text":
            parts.append(label)
        elif kind == "link":
            if show_external_targets and target:
                parts.append(f"{label} ({target})")
            else:
                parts.append(label)
    return "".join(parts)


def strip_trailing_blank_lines(lines: Iterable[str]) -> list[str]:
    result = list(lines)
    while result and not result[-1].strip():
        result.pop()
    return result


def parse_args_with_version(default_source: str = "current") -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True, help="report version, e.g. v0.0")
    parser.add_argument(
        "--source",
        default=default_source,
        choices=["current", "frozen"],
        help="export source: current or frozen",
    )
    return parser.parse_args()
