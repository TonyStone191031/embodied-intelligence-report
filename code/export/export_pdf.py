from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image as RLImage
from reportlab.platypus import PageBreak, Paragraph, Preformatted, SimpleDocTemplate, Spacer, Table, TableStyle

from common import (
    WINDOWS_CONSOLAS,
    WINDOWS_SIMFANG,
    build_config,
    choose_writable_output_path,
    normalize_links,
    parse_args_with_version,
    read_text,
    resolve_repo_target,
)
from render_assets import render_formula_to_lines, render_mermaid_to_png, stable_render_path


TABLE_DIVIDER_RE = re.compile(r"^\|\s*---")
LOCAL_TABLE_LINK_RE = re.compile(r"^见[:：]?\s*\[(?P<label>[^\]]+)\]\((?P<target>[^)]+)\)[。.]?$")
SOURCE_LINE_RE = re.compile(r"^源文件：`(?P<target>[^`]+)`")
FRONT_MATTER_H2 = {"版本说明", "结构说明", "章节索引", "配套文件", "入口文件职责补充说明"}


def register_fonts() -> tuple[str, str]:
    font_name = "Helvetica"
    mono_font = "Courier"
    if WINDOWS_SIMFANG.exists():
        font_name = "SimFang"
        if font_name not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(font_name, str(WINDOWS_SIMFANG)))
    if WINDOWS_CONSOLAS.exists():
        mono_font = "Consolas"
        if mono_font not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(mono_font, str(WINDOWS_CONSOLAS)))
    return font_name, mono_font


def make_styles(font_name: str, mono_font: str):
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            alignment=TA_CENTER,
            fontName=font_name,
            fontSize=18,
            spaceAfter=10,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ReportBody",
            parent=styles["BodyText"],
            fontName=font_name,
            fontSize=10.5,
            alignment=TA_LEFT,
            leading=15,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ReportH1",
            parent=styles["Heading1"],
            fontName=font_name,
            fontSize=15,
            leading=19,
            spaceBefore=8,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ReportH2",
            parent=styles["Heading2"],
            fontName=font_name,
            fontSize=12.5,
            leading=16,
            spaceBefore=6,
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ReportH3",
            parent=styles["Heading3"],
            fontName=font_name,
            fontSize=11.5,
            leading=14,
            spaceBefore=4,
            spaceAfter=3,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ReportCode",
            parent=styles["Code"],
            fontName=mono_font,
            fontSize=9.3,
            leading=13,
            alignment=TA_LEFT,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ReportFormula",
            parent=styles["Code"],
            fontName=mono_font,
            fontSize=10.6,
            leading=14,
            alignment=TA_CENTER,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="FrontMatterLabel",
            parent=styles["Heading2"],
            fontName=font_name,
            fontSize=12.8,
            leading=16,
            alignment=TA_LEFT,
            spaceBefore=7,
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="TableCell",
            parent=styles["BodyText"],
            fontName=font_name,
            fontSize=8.8,
            leading=12,
            alignment=TA_LEFT,
        )
    )
    return styles


def pick_existing_output(path: Path) -> Path:
    regenerated = path.with_name(f"{path.stem}-regenerated{path.suffix}")
    if regenerated.exists() and (not path.exists() or regenerated.stat().st_mtime >= path.stat().st_mtime):
        return regenerated
    return path


def export_pdf_via_word(docx_path: Path, pdf_path: Path) -> bool:
    if not sys.platform.startswith("win"):
        return False
    if not docx_path.exists():
        return False

    src = str(docx_path.resolve()).replace("'", "''")
    dst = str(pdf_path.resolve()).replace("'", "''")
    cmd = [
        "powershell",
        "-NoProfile",
        "-NonInteractive",
        "-Command",
        (
            "$ErrorActionPreference='Stop'; "
            f"$src='{src}'; "
            f"$dst='{dst}'; "
            "$word = New-Object -ComObject Word.Application; "
            "$word.Visible = $false; "
            "$word.DisplayAlerts = 0; "
            "try { "
            "if (Test-Path -LiteralPath $dst) { Remove-Item -LiteralPath $dst -Force }; "
            "$doc = $word.Documents.Open($src, $false, $true); "
            "$doc.Fields.Update(); "
            "foreach ($toc in $doc.TablesOfContents) { $toc.Update() }; "
            "$doc.ExportAsFixedFormat($dst, 17); "
            "$doc.Close($false) "
            "} finally { "
            "$word.Quit() | Out-Null "
            "}"
        ),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if result.returncode == 0 and pdf_path.exists():
        return True

    error_text = (result.stderr or result.stdout or "").strip()
    if error_text:
        print(f"Word PDF export failed, falling back to ReportLab: {error_text}", file=sys.stderr)
    return False


def escape_pdf_text(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def parse_table(lines: list[str], start: int) -> tuple[list[list[str]], int]:
    rows: list[list[str]] = []
    i = start
    while i < len(lines):
        line = lines[i]
        if not line.strip().startswith("|"):
            break
        if TABLE_DIVIDER_RE.match(line.strip()):
            i += 1
            continue
        cells = [escape_pdf_text(normalize_links(cell.strip())) for cell in line.strip().strip("|").split("|")]
        rows.append(cells)
        i += 1
    return rows, i


def extract_table_from_markdown(path) -> list[list[str]]:
    lines = read_text(path).splitlines()
    for idx, line in enumerate(lines):
        if line.strip().startswith("|"):
            rows, _ = parse_table(lines, idx)
            if rows:
                return rows
    return []


def estimate_col_widths(rows: list[list[str]], total_width: float) -> list[float]:
    col_count = max(len(row) for row in rows)
    weights = [1.0] * col_count
    for row in rows:
        for idx in range(col_count):
            cell = row[idx] if idx < len(row) else ""
            line_len = max((len(part) for part in cell.splitlines()), default=0)
            weights[idx] = max(weights[idx], min(max(line_len, 6), 26))
    total = sum(weights)
    return [total_width * weight / total for weight in weights]


def add_table(story: list, rows: list[list[str]], font_name: str, styles, available_width: float) -> None:
    if not rows:
        return
    wrapped_rows = []
    for row in rows:
        wrapped_rows.append([Paragraph(escape_pdf_text(cell), styles["TableCell"]) for cell in row])
    table = Table(wrapped_rows, repeatRows=1, colWidths=estimate_col_widths(rows, available_width))
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9E2F3")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("FONTNAME", (0, 0), (-1, 0), font_name),
                ("FONTNAME", (0, 1), (-1, -1), font_name),
                ("FONTSIZE", (0, 0), (-1, -1), 8.8),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("WORDWRAP", (0, 0), (-1, -1), "CJK"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 4 * mm))


def render_markdown_to_pdf(markdown_text: str, output_path, config) -> None:
    font_name, mono_font = register_fonts()
    styles = make_styles(font_name, mono_font)
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=18 * mm,
        bottomMargin=16 * mm,
        title=f"具身智能行业和技术发展调研报告 {config.version}",
        author="Codex",
    )
    available_width = A4[0] - doc.leftMargin - doc.rightMargin

    lines = markdown_text.splitlines()
    story: list = []
    in_code = False
    code_kind = ""
    code_lines: list[str] = []
    i = 0
    in_front_matter = True

    def footer(canvas, _doc):
        canvas.saveState()
        canvas.setFont(font_name, 8)
        canvas.drawCentredString(A4[0] / 2, 10 * mm, f"具身智能行业和技术发展调研报告 {config.version} | page {canvas.getPageNumber()}")
        canvas.restoreState()

    while i < len(lines):
        stripped = lines[i].strip()

        if stripped.startswith("```"):
            if in_code:
                if code_kind == "math":
                    story.append(Preformatted("\n".join(render_formula_to_lines("\n".join(code_lines))), styles["ReportFormula"]))
                elif code_kind == "mermaid":
                    pass
                else:
                    story.append(Preformatted("\n".join(code_lines), styles["ReportCode"]))
                story.append(Spacer(1, 3 * mm))
                code_lines = []
                in_code = False
                code_kind = ""
            else:
                in_code = True
                code_kind = stripped.strip("`").strip()
            i += 1
            continue

        if in_code:
            code_lines.append(lines[i].rstrip())
            i += 1
            continue

        if not stripped or stripped.startswith("<!--"):
            i += 1
            continue

        if stripped == "---":
            story.append(PageBreak())
            i += 1
            continue

        if stripped == r"\[":
            math_lines: list[str] = []
            i += 1
            while i < len(lines) and lines[i].strip() != r"\]":
                math_lines.append(lines[i].rstrip())
                i += 1
            if i < len(lines) and lines[i].strip() == r"\]":
                i += 1
            story.append(Preformatted("\n".join(render_formula_to_lines("\n".join(math_lines))), styles["ReportFormula"]))
            story.append(Spacer(1, 3 * mm))
            continue

        if stripped.startswith("|"):
            rows, next_i = parse_table(lines, i)
            add_table(story, rows, font_name, styles, available_width)
            i = next_i
            continue

        if stripped.startswith("# "):
            text = normalize_links(stripped[2:].strip())
            if "调研报告-v" in text:
                story.append(Paragraph(escape_pdf_text(text), styles["ReportTitle"]))
            else:
                in_front_matter = False
                story.append(Paragraph(escape_pdf_text(text), styles["ReportH1"]))
            story.append(Spacer(1, 3 * mm))
            i += 1
            continue

        if stripped.startswith("## "):
            heading_text = normalize_links(stripped[3:].strip())
            heading_style = "FrontMatterLabel" if in_front_matter and heading_text in FRONT_MATTER_H2 else "ReportH2"
            story.append(Paragraph(escape_pdf_text(heading_text), styles[heading_style]))
            i += 1
            continue

        if stripped.startswith("### "):
            story.append(Paragraph(escape_pdf_text(normalize_links(stripped[4:].strip())), styles["ReportH3"]))
            i += 1
            continue

        source_match = SOURCE_LINE_RE.match(stripped)
        if source_match:
            target = source_match.group("target")
            source_path = resolve_repo_target(target)
            if source_path and source_path.suffix.lower() == ".mmd" and source_path.exists():
                rendered = stable_render_path(config.rendered_assets_dir, "diagrams", str(source_path), "png")
                render_mermaid_to_png(source_path, rendered)
                with PILImage.open(rendered) as im:
                    width_px, height_px = im.size
                max_width = 165 * mm
                max_height = 110 * mm
                scale = min(max_width / width_px, max_height / height_px)
                img = RLImage(str(rendered), width=width_px * scale, height=height_px * scale)
                img.hAlign = "CENTER"
                story.append(img)
                story.append(Spacer(1, 4 * mm))
            i += 1
            continue

        table_link_match = LOCAL_TABLE_LINK_RE.match(stripped)
        if table_link_match:
            target = table_link_match.group("target")
            table_path = resolve_repo_target(target)
            if table_path and table_path.exists():
                rows = extract_table_from_markdown(table_path)
                add_table(story, rows, font_name, styles, available_width)
            i += 1
            continue

        if re.match(r"^\d+\.\s+", stripped):
            text = re.sub(r"^\d+\.\s+", "", stripped)
            story.append(Paragraph(escape_pdf_text(normalize_links(text)), styles["ReportBody"]))
            i += 1
            continue

        if stripped.startswith("- "):
            story.append(Paragraph(escape_pdf_text("- " + normalize_links(stripped[2:].strip())), styles["ReportBody"]))
            i += 1
            continue

        if stripped.startswith("> "):
            story.append(Paragraph(escape_pdf_text(normalize_links(stripped[2:].strip())), styles["Italic"]))
            i += 1
            continue

        paragraph_lines = [escape_pdf_text(normalize_links(stripped))]
        i += 1
        while i < len(lines):
            peek = lines[i].strip()
            if (
                not peek
                or peek.startswith("#")
                or peek.startswith("```")
                or peek == r"\["
                or peek.startswith("|")
                or peek == "---"
                or peek.startswith("- ")
                or peek.startswith("> ")
                or re.match(r"^\d+\.\s+", peek)
                or SOURCE_LINE_RE.match(peek)
                or LOCAL_TABLE_LINK_RE.match(peek)
            ):
                break
            paragraph_lines.append(escape_pdf_text(normalize_links(peek)))
            i += 1
        story.append(Paragraph("<br/>".join(paragraph_lines), styles["ReportBody"]))

    doc.build(story, onFirstPage=footer, onLaterPages=footer)


def main() -> None:
    args = parse_args_with_version()
    config = build_config(args.version, args.source)
    output_path = choose_writable_output_path(config.pdf_path)
    docx_path = pick_existing_output(config.docx_path)

    if export_pdf_via_word(docx_path, output_path):
        print(f"PDF written via Word: {output_path}")
        return

    markdown_text = read_text(config.bundle_path)
    render_markdown_to_pdf(markdown_text, output_path, config)
    print(f"PDF written via fallback renderer: {output_path}")


if __name__ == "__main__":
    main()
