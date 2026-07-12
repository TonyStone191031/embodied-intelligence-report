from __future__ import annotations

import argparse
import re
from pathlib import Path

from common import ROOT, read_text
from render_assets import render_mermaid_to_png


HEADING_COMMANDS = {1: "part", 2: "chapter", 3: "section", 4: "subsection"}
FENCE_RE = re.compile(r"^```(?P<kind>[^`]*)$")
LINK_RE = re.compile(r"(?P<image>!)?\[(?P<label>[^\]]*)\]\((?P<target>[^)]+)\)")
INLINE_RE = re.compile(
    r"(?P<math>\\\(.*?\\\))|(?P<code>`[^`]*`)|(?P<link>!?\[[^\]]*\]\([^)]+\))"
)
SOURCE_RE = re.compile(r"^源文件：`(?P<target>[^`]+)`$")


def escape_text(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in value)


def escape_url(value: str) -> str:
    return value.replace("\\", "/").replace("%", r"\%").replace("#", r"\#").replace("&", r"\&")


def local_target(target: str) -> Path | None:
    cleaned = target.strip().strip("<>").replace("\\", "/")
    if re.match(r"^[A-Za-z]:/", cleaned):
        path = Path(cleaned)
    elif cleaned.startswith(("assets/", "docs/", "research/", "data/")):
        path = ROOT / cleaned
    else:
        return None
    return path if path.exists() else None


def is_math_code(value: str) -> bool:
    return bool(
        re.search(r"\\[A-Za-z]+", value)
        or re.search(r"(?:_|\^|π|Δ|≈|×|\b(?:SO|SE)\(\d+\)|\b[A-Za-z]\([^)]*\))", value)
    )


def normalize_math_symbols(value: str) -> str:
    return value.replace("π", r"\pi ").replace("Δ", r"\Delta ").replace("≈", r"\approx ").replace("×", r"\times ")


def inline_code(value: str) -> str:
    value = value.strip("`")
    if is_math_code(value):
        style = r"\scriptstyle " if len(value) > 48 else ""
        return rf"\({style}{normalize_math_symbols(value)}\)"
    if "/" in value or "\\" in value:
        return rf"\path{{{value.replace('\\', '/') }}}"
    return rf"\texttt{{\detokenize{{{value}}}}}"


def render_link(match: re.Match[str]) -> str:
    label = match.group("label")
    target = match.group("target").strip()
    if match.group("image"):
        return rf"\textit{{{escape_text(label or Path(target).name)}}}"
    if target.lower().startswith(("http://", "https://")):
        return rf"\href{{{escape_url(target)}}}{{{render_inline(label)}}}"
    # Local paths are intentionally not emitted into the PDF. They are machine-specific.
    return render_inline(label)


def render_inline(value: str) -> str:
    parts: list[str] = []
    cursor = 0
    for match in INLINE_RE.finditer(value):
        if match.start() > cursor:
            parts.append(escape_text(value[cursor : match.start()]))
        if match.group("math"):
            math = normalize_math_symbols(match.group("math"))
            if len(math) > 52:
                math = rf"\(\scriptstyle {math[2:-2]}\)"
            parts.append(math)
        elif match.group("code"):
            parts.append(inline_code(match.group("code")))
        else:
            link_match = LINK_RE.fullmatch(match.group("link"))
            parts.append(render_link(link_match) if link_match else escape_text(match.group("link")))
        cursor = match.end()
    parts.append(escape_text(value[cursor:]))
    return "".join(parts)


def split_table_row(line: str) -> list[str]:
    value = line.strip().strip("|")
    return [cell.strip() for cell in value.split("|")]


def is_table_divider(line: str) -> bool:
    return bool(re.fullmatch(r"\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?", line.strip()))


def render_table(rows: list[list[str]]) -> str:
    if not rows:
        return ""
    rows = [row for row in rows if row and not is_table_divider("|".join(row))]
    if not rows:
        return ""
    columns = max(len(row) for row in rows)
    spec = "".join("Y" for _ in range(columns))
    output = [r"\begingroup", r"\small", rf"\begin{{xltabular}}{{\textwidth}}{{{spec}}}", r"\toprule"]
    header = rows[0] + [""] * (columns - len(rows[0]))
    output.append(" & ".join(render_inline(cell) for cell in header) + r" \\")
    output.extend([r"\midrule", r"\endfirsthead", r"\toprule"])
    output.append(" & ".join(render_inline(cell) for cell in header) + r" \\")
    output.extend([r"\midrule", r"\endhead"])
    for row in rows[1:]:
        padded = row + [""] * (columns - len(row))
        output.append(" & ".join(render_inline(cell) for cell in padded) + r" \\")
    output.extend([r"\bottomrule", r"\end{xltabular}", r"\endgroup", ""])
    return "\n".join(output)


def table_from_markdown(path: Path) -> str:
    lines = read_text(path).splitlines()
    rows: list[list[str]] = []
    for line in lines:
        if line.strip().startswith("|"):
            rows.append(split_table_row(line))
        elif rows:
            break
    return render_table(rows)


def render_figure(source: Path, figures_dir: Path) -> str:
    figures_dir.mkdir(parents=True, exist_ok=True)
    output = figures_dir / f"{source.stem}.png"
    render_mermaid_to_png(source, output)
    return "\n".join(
        [
            r"\begin{figure}[htbp]",
            r"\centering",
            rf"\includegraphics[width=0.9\textwidth,height=0.72\textheight,keepaspectratio]{{figures/{output.name}}}",
            rf"\caption{{{escape_text(source.stem)}}}",
            rf"\label{{fig:{source.stem}}}",
            r"\end{figure}",
            "",
        ]
    )


def render_fenced_block(kind: str, content: list[str], pending_source: Path | None, figures_dir: Path) -> str:
    normalized_kind = kind.strip().lower()
    if normalized_kind == "mermaid" and pending_source and pending_source.exists():
        return render_figure(pending_source, figures_dir)
    if normalized_kind in {"math", "latex"}:
        return render_display_math(content)
    if normalized_kind in {"", "text", "plaintext", "yaml"}:
        return "\n".join([r"\begin{lstlisting}", *content, r"\end{lstlisting}", ""])
    language = normalized_kind or "text"
    return "\n".join([rf"\begin{{lstlisting}}[language={language}]", *content, r"\end{lstlisting}", ""])


def split_long_text(text: str, width: int = 22) -> list[str]:
    return [text[index : index + width] for index in range(0, len(text), width)]


def normalize_cases_math(text: str) -> str:
    match = re.search(r"\\begin\{cases\}(?P<body>.*?)\\end\{cases\}", text, flags=re.DOTALL)
    if not match:
        return text
    rows = []
    for raw_row in match.group("body").split(r"\\"):
        row = raw_row.strip()
        if not row:
            continue
        if "&" not in row:
            rows.append(row)
            continue
        left, right = row.split("&", 1)
        text_match = re.search(r"\\text\{([^{}]{23,})\}", right)
        if text_match:
            prefix = right[: text_match.start()]
            wrapped = r"\substack{" + r"\\".join(rf"\text{{{part}}}" for part in split_long_text(text_match.group(1))) + "}"
            right = prefix + wrapped + right[text_match.end() :]
        rows.append(f"{left.strip()} & {right.strip()}")
    body = r"\\".join(rows)
    return text[: match.start("body")] + "\n" + body + "\n" + text[match.end("body") :]


def render_display_math(content: list[str]) -> str:
    text = normalize_math_symbols(normalize_cases_math("\n".join(content)))
    if r"\begin{cases}" in text:
        size = r"\small"
    else:
        size = r"\scriptsize" if len(text) > 90 else (r"\footnotesize" if len(text) > 55 else "")
    lines: list[str] = []
    if size:
        lines.insert(0, r"\begingroup")
        lines.append(size)
    lines.append(r"\begin{equation*}")
    lines.extend([text, r"\end{equation*}"])
    if size:
        lines.append(r"\endgroup")
    lines.append("")
    return "\n".join(lines)


def render_heading(level: int, title: str) -> str:
    """Keep the report's explicit outline numbering and populate the TOC."""
    command = HEADING_COMMANDS[level]
    rendered = render_inline(title)
    toc_title = escape_text(title)
    return "\n".join(
        [
            rf"\{command}*{{{rendered}}}",
            rf"\addcontentsline{{toc}}{{{command}}}{{{toc_title}}}",
            rf"\markboth{{{toc_title}}}{{{toc_title}}}" if level <= 2 else "",
            "",
        ]
    )


def is_structural_line(line: str) -> bool:
    stripped = line.strip()
    return bool(
        not stripped
        or stripped.startswith("#")
        or stripped.startswith("```")
        or stripped == r"\["
        or stripped.startswith("|")
        or stripped == "---"
        or stripped.startswith(("- ", "* "))
        or re.match(r"^\d+\.\s+", stripped)
        or SOURCE_RE.match(stripped)
    )


def standalone_table_link(line: str) -> Path | None:
    match = LINK_RE.fullmatch(line.strip().removeprefix("见：").removeprefix("见 ").strip("。"))
    if not match:
        return None
    target = match.group("target")
    if "/tables/" not in target.replace("\\", "/"):
        return None
    return local_target(target)


def convert_markdown(markdown_path: Path, output_path: Path, figures_dir: Path) -> None:
    lines = read_text(markdown_path).splitlines()
    output: list[str] = [f"% Generated from {markdown_path.name}; edit the LaTeX source after migration.", ""]
    pending_source: Path | None = None
    i = 0

    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()
        if not stripped:
            i += 1
            continue

        heading = re.match(r"^(#{1,4})\s+(.+)$", stripped)
        if heading:
            level = len(heading.group(1))
            output.append(render_heading(level, heading.group(2).strip()))
            i += 1
            continue

        fence = FENCE_RE.match(stripped)
        if fence:
            kind = fence.group("kind")
            content: list[str] = []
            i += 1
            while i < len(lines) and lines[i].strip() != "```":
                content.append(lines[i])
                i += 1
            if i < len(lines):
                i += 1
            output.append(render_fenced_block(kind, content, pending_source, figures_dir))
            continue

        if stripped == r"\[":
            content: list[str] = []
            i += 1
            while i < len(lines) and lines[i].strip() != r"\]":
                content.append(lines[i])
                i += 1
            if i < len(lines):
                i += 1
            output.append(render_display_math(content))
            continue

        source_match = SOURCE_RE.match(stripped)
        if source_match:
            pending_source = local_target(source_match.group("target"))
            display = source_match.group("target").replace("\\", "/")
            output.append(rf"\noindent\textit{{源文件：\texttt{{\detokenize{{{display}}}}}}}")
            lookahead = i + 1
            while lookahead < len(lines) and not lines[lookahead].strip():
                lookahead += 1
            if pending_source and (lookahead >= len(lines) or not lines[lookahead].strip().startswith("```mermaid")):
                output.append(render_figure(pending_source, figures_dir))
                pending_source = None
            output.append("")
            i += 1
            continue

        if stripped.startswith("|"):
            rows: list[list[str]] = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(split_table_row(lines[i]))
                i += 1
            output.append(render_table(rows))
            continue

        table_path = standalone_table_link(stripped)
        if table_path:
            output.append(table_from_markdown(table_path))
            i += 1
            continue

        if stripped.startswith(("- ", "* ")):
            items: list[str] = []
            while i < len(lines) and lines[i].strip().startswith(("- ", "* ")):
                items.append(lines[i].strip()[2:])
                i += 1
            output.extend([r"\begin{itemize}", *[rf"\item {render_inline(item)}" for item in items], r"\end{itemize}", ""])
            continue

        if re.match(r"^\d+\.\s+", stripped):
            items = []
            while i < len(lines):
                match = re.match(r"^\d+\.\s+(.+)$", lines[i].strip())
                if not match:
                    break
                items.append(match.group(1))
                i += 1
            output.extend([r"\begin{enumerate}", *[rf"\item {render_inline(item)}" for item in items], r"\end{enumerate}", ""])
            continue

        if stripped == "---":
            output.extend([r"\bigskip", ""])
            i += 1
            continue

        paragraph_lines = [stripped]
        i += 1
        while i < len(lines) and not is_structural_line(lines[i]):
            paragraph_lines.append(lines[i].strip())
            i += 1
        output.append(render_inline(" ".join(paragraph_lines)))
        output.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(output), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert one Markdown chapter to a LaTeX chapter source")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--figures-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    convert_markdown(args.input, args.output, args.figures_dir)
    print(f"LaTeX chapter written: {args.output}")


if __name__ == "__main__":
    main()
