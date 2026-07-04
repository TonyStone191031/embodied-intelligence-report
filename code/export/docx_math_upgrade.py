from __future__ import annotations

import json
import re
import subprocess
import tempfile
from copy import deepcopy
from dataclasses import dataclass
import os
from pathlib import Path
import unicodedata

from lxml import etree


MATHML_NS = "http://www.w3.org/1998/Math/MathML"
WORD_MATH_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
WORD_MATH_TAG = f"{{{WORD_MATH_NS}}}oMath"
OFFICE_MML2OMML_CANDIDATES = [
    Path("C:/Program Files/Microsoft Office/root/Office16/MML2OMML.XSL"),
    Path("C:/Program Files/Microsoft Office/root/Office15/MML2OMML.XSL"),
]

SYMBOL_COMMANDS = {
    "alpha": "\u03b1",
    "approx": "\u2248",
    "ast": "*",
    "beta": "\u03b2",
    "cdot": "\u00b7",
    "delta": "\u03b4",
    "dots": "...",
    "ell": "l",
    "epsilon": "\u03b5",
    "eta": "\u03b7",
    "gamma": "\u03b3",
    "Gamma": "\u0393",
    "ge": "\u2265",
    "geq": "\u2265",
    "gg": ">>",
    "in": "\u2208",
    "kappa": "\u03ba",
    "lambda": "\u03bb",
    "Lambda": "\u039b",
    "ldots": "...",
    "le": "\u2264",
    "left": "",
    "leq": "\u2264",
    "lesssim": "\u2272",
    "lVert": "||",
    "mapsto": "\u21a6",
    "mathbb": "",
    "mathcal": "",
    "mathbf": "",
    "mathrm": "",
    "mid": "|",
    "mu": "\u03bc",
    "neq": "\u2260",
    "omega": "\u03c9",
    "Omega": "\u03a9",
    "phi": "\u03c6",
    "pi": "\u03c0",
    "Pi": "\u03a0",
    "psi": "\u03c8",
    "Psi": "\u03a8",
    "quad": " ",
    "qquad": " ",
    "rho": "\u03c1",
    "right": "",
    "rVert": "||",
    "sigma": "\u03c3",
    "Sigma": "\u03a3",
    "sim": "~",
    "succ": "\u227b",
    "tau": "\u03c4",
    "theta": "\u03b8",
    "Theta": "\u0398",
    "times": "\u00d7",
    "to": "\u2192",
    "rightarrow": "\u2192",
    "xi": "\u03be",
    "Xi": "\u039e",
}

ACCENT_COMMANDS = {
    "bar": "\u0304",
    "ddot": "\u0308",
    "dot": "\u0307",
    "hat": "\u0302",
    "tilde": "\u0303",
}

GROUP_TEXT_COMMANDS = {
    "mathbf",
    "mathbb",
    "mathcal",
    "mathrm",
    "mathsf",
    "operatorname",
    "text",
    "textrm",
}

RAW_PRE_REPLACEMENTS = {
    r"\not\approx": "\u2249",
    r"\not\in": "\u2209",
}


@dataclass(frozen=True)
class LinearFormulaSpec:
    placeholder: str
    original: str
    linear: str


def normalize_formula_block(lines: list[str]) -> str:
    cleaned = [line.rstrip() for line in lines]
    while cleaned and not cleaned[0].strip():
        cleaned.pop(0)
    while cleaned and not cleaned[-1].strip():
        cleaned.pop()
    return "\n".join(cleaned).strip()


def is_matrix_formula(formula_text: str) -> bool:
    return r"\begin{bmatrix}" in formula_text or r"\begin{matrix}" in formula_text


def register_linear_formula(formulas: list[LinearFormulaSpec], formula_text: str) -> str:
    placeholder = f"[[FORMULA_{len(formulas) + 1:04d}]]"
    formulas.append(
        LinearFormulaSpec(
            placeholder=placeholder,
            original=formula_text,
            linear=latex_to_word_linear(formula_text),
        )
    )
    return placeholder


def latex_to_word_linear(formula_text: str) -> str:
    text = formula_text.strip()
    for src, dst in RAW_PRE_REPLACEMENTS.items():
        text = text.replace(src, dst)
    text = _convert_latex_fragment(text)
    text = text.replace("\n", " ")
    text = text.replace("\t", " ")
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s+([,.;:)\]])", r"\1", text)
    text = re.sub(r"([(\[])\s+", r"\1", text)
    text = re.sub(r"\s+([+\-=/|])\s+", r" \1 ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def append_matrix_formula(paragraph, formula_text: str) -> None:
    omml = build_matrix_omml(formula_text)
    paragraph._element.append(deepcopy(omml))


def append_formula_omml(paragraph, formula_text: str) -> None:
    if is_matrix_formula(formula_text):
        append_matrix_formula(paragraph, formula_text)
        return
    omml = build_linear_omml(latex_to_word_linear(formula_text))
    paragraph._element.append(deepcopy(omml))


def upgrade_docx_linear_formulas(docx_path: Path, formulas: list[LinearFormulaSpec]) -> None:
    if not formulas:
        return

    manifest_fd, manifest_name = tempfile.mkstemp(prefix="docx-formulas-", suffix=".json")
    script_fd, script_name = tempfile.mkstemp(prefix="docx-formulas-", suffix=".ps1")
    os.close(manifest_fd)
    os.close(script_fd)
    manifest_path = Path(manifest_name)
    script_path = Path(script_name)

    try:
        manifest_path.write_text(
            json.dumps([formula.__dict__ for formula in formulas], ensure_ascii=False, indent=2),
            encoding="utf-8-sig",
        )
        script_path.write_text(_word_formula_upgrade_script(), encoding="utf-8-sig")
        command = [
            "powershell",
            "-NoProfile",
            "-NonInteractive",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(script_path),
            "-DocxPath",
            str(docx_path),
            "-ManifestPath",
            str(manifest_path),
        ]
        result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
        if result.returncode != 0:
            error_text = (result.stderr or result.stdout or "").strip()
            raise RuntimeError(f"Word formula upgrade failed: {error_text}")
    finally:
        try:
            manifest_path.unlink(missing_ok=True)
        except TypeError:
            if manifest_path.exists():
                manifest_path.unlink()
        try:
            script_path.unlink(missing_ok=True)
        except TypeError:
            if script_path.exists():
                script_path.unlink()


def build_matrix_omml(formula_text: str):
    prefix, rows, suffix, open_bracket, close_bracket = _parse_matrix_formula(formula_text)
    math = etree.Element(f"{{{MATHML_NS}}}math", nsmap={None: MATHML_NS})
    row = etree.SubElement(math, f"{{{MATHML_NS}}}mrow")
    _append_mathml_tokens(row, prefix)
    fenced = etree.SubElement(
        row,
        f"{{{MATHML_NS}}}mfenced",
        open=open_bracket,
        close=close_bracket,
    )
    table = etree.SubElement(fenced, f"{{{MATHML_NS}}}mtable")
    for cells in rows:
        mtr = etree.SubElement(table, f"{{{MATHML_NS}}}mtr")
        for cell_text in cells:
            mtd = etree.SubElement(mtr, f"{{{MATHML_NS}}}mtd")
            cell_row = etree.SubElement(mtd, f"{{{MATHML_NS}}}mrow")
            _append_mathml_tokens(cell_row, cell_text)
    _append_mathml_tokens(row, suffix)

    transform = etree.XSLT(etree.parse(str(_office_mml2omml_xsl())))
    result = transform(math)
    root = result.getroot()
    if root.tag != WORD_MATH_TAG:
        math_nodes = root.findall(f".//{WORD_MATH_TAG}")
        if not math_nodes:
            raise ValueError("Failed to build OMML matrix node.")
        root = math_nodes[0]
    return root


def build_linear_omml(linear_text: str):
    parser = _LinearMathParser(linear_text)
    content = parser.parse_sequence()
    math = etree.Element(f"{{{MATHML_NS}}}math", nsmap={None: MATHML_NS})
    math.append(content)
    transform = etree.XSLT(etree.parse(str(_office_mml2omml_xsl())))
    result = transform(math)
    root = result.getroot()
    if root.tag != WORD_MATH_TAG:
        math_nodes = root.findall(f".//{WORD_MATH_TAG}")
        if not math_nodes:
            raise ValueError("Failed to build OMML node from linear math.")
        root = math_nodes[0]
    return root


def _office_mml2omml_xsl() -> Path:
    for path in OFFICE_MML2OMML_CANDIDATES:
        if path.exists():
            return path
    raise FileNotFoundError("Microsoft Office MathML-to-OMML transform not found.")


def _parse_matrix_formula(formula_text: str) -> tuple[str, list[list[str]], str, str, str]:
    if r"\begin{bmatrix}" in formula_text:
        begin = r"\begin{bmatrix}"
        end = r"\end{bmatrix}"
        open_bracket, close_bracket = "[", "]"
    elif r"\begin{matrix}" in formula_text:
        begin = r"\begin{matrix}"
        end = r"\end{matrix}"
        open_bracket, close_bracket = "", ""
    else:
        raise ValueError("Unsupported matrix environment.")

    prefix, remainder = formula_text.split(begin, 1)
    body, suffix = remainder.split(end, 1)
    rows = []
    for raw_row in re.split(r"\\\\", body):
        stripped = raw_row.strip()
        if not stripped:
            continue
        rows.append([cell.strip() for cell in stripped.split("&")])
    if not rows:
        raise ValueError("Matrix body is empty.")
    return prefix.strip(), rows, suffix.strip(), open_bracket, close_bracket


def _append_mathml_tokens(parent, latex_text: str) -> None:
    text = latex_to_word_linear(latex_text)
    tokens = re.findall(r"[A-Za-z]+|[0-9]+|[\u0370-\u03ff]+|[^\s]", text)
    for token in tokens:
        if not token:
            continue
        if re.fullmatch(r"[0-9]+", token):
            tag = "mn"
        elif re.fullmatch(r"[A-Za-z\u0370-\u03ff]+", token):
            tag = "mi"
        else:
            tag = "mo"
        element = etree.SubElement(parent, f"{{{MATHML_NS}}}{tag}")
        element.text = token


class _LinearMathParser:
    def __init__(self, text: str) -> None:
        self.text = text
        self.index = 0

    def parse_sequence(self, stop_chars: set[str] | None = None):
        row = etree.Element(f"{{{MATHML_NS}}}mrow")
        while self.index < len(self.text):
            self._skip_spaces()
            if self.index >= len(self.text):
                break
            if stop_chars and self.text[self.index] in stop_chars:
                break
            atom = self._parse_atom()
            if atom is None:
                self.index += 1
                continue
            row.append(atom)
        return row

    def _parse_atom(self):
        self._skip_spaces()
        if self.index >= len(self.text):
            return None

        if self.text.startswith("sqrt(", self.index):
            self.index += 5
            content = self._parse_delimited_content("(", ")", include_delimiters=False)
            node = etree.Element(f"{{{MATHML_NS}}}msqrt")
            node.append(content)
            return self._parse_postfix(node)

        char = self.text[self.index]
        if char == "(":
            self.index += 1
            content = self._parse_delimited_content("(", ")", include_delimiters=True)
            return self._parse_fraction_or_postfix(content)
        if char == "[":
            self.index += 1
            content = self._parse_delimited_content("[", "]", include_delimiters=True)
            return self._parse_fraction_or_postfix(content)
        if char == "{":
            self.index += 1
            content = self._parse_delimited_content("{", "}", include_delimiters=False)
            return self._parse_fraction_or_postfix(content)

        if char in "+-=|,:;":
            self.index += 1
            return self._make_operator(char)
        if self.text.startswith(">>", self.index):
            self.index += 2
            return self._make_operator(">>")
        if self.text.startswith("||", self.index):
            self.index += 2
            group = etree.Element(f"{{{MATHML_NS}}}mrow")
            group.append(self._make_operator("|"))
            group.append(self._make_operator("|"))
            return group

        token = self._read_token()
        if not token:
            return None
        node = self._make_identifier_or_number(token)
        return self._parse_fraction_or_postfix(node)

    def _parse_fraction_or_postfix(self, node):
        current = self._parse_postfix(node)
        self._skip_spaces()
        if self.index < len(self.text) and self.text[self.index] == "/":
            self.index += 1
            denominator = self._parse_atom()
            frac = etree.Element(f"{{{MATHML_NS}}}mfrac")
            frac.append(current)
            frac.append(denominator if denominator is not None else self._make_identifier_or_number("1"))
            return frac
        return current

    def _parse_postfix(self, node):
        sub_node = None
        sup_node = None
        while True:
            self._skip_spaces()
            if self.index >= len(self.text):
                break
            marker = self.text[self.index]
            if marker not in {"_", "^"}:
                break
            self.index += 1
            script = self._parse_script_argument()
            if marker == "_":
                sub_node = script
            else:
                sup_node = script
        if sub_node is None and sup_node is None:
            return node
        if sub_node is not None and sup_node is not None:
            wrapper = etree.Element(f"{{{MATHML_NS}}}msubsup")
            wrapper.append(node)
            wrapper.append(sub_node)
            wrapper.append(sup_node)
            return wrapper
        if sub_node is not None:
            wrapper = etree.Element(f"{{{MATHML_NS}}}msub")
            wrapper.append(node)
            wrapper.append(sub_node)
            return wrapper
        wrapper = etree.Element(f"{{{MATHML_NS}}}msup")
        wrapper.append(node)
        wrapper.append(sup_node)
        return wrapper

    def _parse_script_argument(self):
        self._skip_spaces()
        if self.index >= len(self.text):
            return self._make_identifier_or_number("?")
        char = self.text[self.index]
        if char == "(":
            self.index += 1
            return self._parse_delimited_content("(", ")", include_delimiters=False)
        if char == "[":
            self.index += 1
            return self._parse_delimited_content("[", "]", include_delimiters=False)
        if char == "{":
            self.index += 1
            return self._parse_delimited_content("{", "}", include_delimiters=False)
        token = self._read_token()
        return self._make_identifier_or_number(token or "?")

    def _parse_delimited_content(self, open_char: str, close_char: str, include_delimiters: bool):
        row = etree.Element(f"{{{MATHML_NS}}}mrow")
        if include_delimiters:
            row.append(self._make_operator(open_char))
        content = self.parse_sequence(stop_chars={close_char})
        for child in list(content):
            row.append(child)
        if self.index < len(self.text) and self.text[self.index] == close_char:
            self.index += 1
        if include_delimiters:
            row.append(self._make_operator(close_char))
        return row

    def _read_token(self) -> str:
        if self.index >= len(self.text):
            return ""

        char = self.text[self.index]
        if char.isdigit():
            start = self.index
            while self.index < len(self.text) and self.text[self.index].isdigit():
                self.index += 1
            return self.text[start:self.index]

        if _is_identifier_char(char):
            start = self.index
            self.index += 1
            while self.index < len(self.text) and _is_identifier_char(self.text[self.index]):
                self.index += 1
            return self.text[start:self.index]

        self.index += 1
        return char

    def _make_identifier_or_number(self, token: str):
        if token == "sum":
            return self._make_operator("\u2211")
        if token == "prod":
            return self._make_operator("\u220f")
        if token.isdigit():
            node = etree.Element(f"{{{MATHML_NS}}}mn")
            node.text = token
            return node
        if token in {"|", "||", ">>", "\u2264", "\u2265", "\u2208", "\u2248", "\u2272", "\u2192", "\u21a6", "\u00d7", "\u00b7"}:
            return self._make_operator(token)
        node = etree.Element(f"{{{MATHML_NS}}}mi")
        node.text = token
        return node

    def _make_operator(self, token: str):
        node = etree.Element(f"{{{MATHML_NS}}}mo")
        node.text = token
        return node

    def _skip_spaces(self) -> None:
        while self.index < len(self.text) and self.text[self.index].isspace():
            self.index += 1


def _is_identifier_char(char: str) -> bool:
    category = unicodedata.category(char)
    return category[0] in {"L", "N", "M"}


def _convert_latex_fragment(text: str) -> str:
    pieces: list[str] = []
    index = 0
    while index < len(text):
        char = text[index]
        if char == "\\":
            command, next_index = _read_command(text, index + 1)
            if not command:
                pieces.append("\\")
                index += 1
                continue
            if command in GROUP_TEXT_COMMANDS:
                group, index = _read_required_group(text, next_index)
                pieces.append(_convert_latex_fragment(group))
                continue
            if command in ACCENT_COMMANDS:
                token, index = _read_token_for_accent(text, next_index)
                pieces.append(_apply_accent(_convert_latex_fragment(token), ACCENT_COMMANDS[command]))
                continue
            if command == "frac":
                numerator, cursor = _read_required_group(text, next_index)
                denominator, index = _read_required_group(text, cursor)
                pieces.append(f"({_convert_latex_fragment(numerator)})/({_convert_latex_fragment(denominator)})")
                continue
            if command == "sqrt":
                radicand, index = _read_required_group(text, next_index, allow_optional_brackets=True)
                pieces.append(f"sqrt({_convert_latex_fragment(radicand)})")
                continue
            if command == "begin":
                group, index = _read_required_group(text, next_index)
                pieces.append(group)
                continue
            if command == "end":
                _, index = _read_required_group(text, next_index)
                continue
            if command == "\\":
                pieces.append(" ; ")
                index = next_index
                continue
            pieces.append(SYMBOL_COMMANDS.get(command, command))
            index = next_index
            continue
        if char in {"^", "_"}:
            token, index = _read_script_token(text, index + 1)
            pieces.append(char + _format_script_token(_convert_latex_fragment(token)))
            continue
        if char == "{":
            group, index = _read_group(text, index)
            pieces.append(_convert_latex_fragment(group))
            continue
        if char == "}":
            index += 1
            continue
        if char == "&":
            pieces.append(" ")
            index += 1
            continue
        pieces.append(char)
        index += 1
    return "".join(pieces)


def _read_command(text: str, index: int) -> tuple[str, int]:
    if index >= len(text):
        return "", index
    if text[index].isalpha():
        cursor = index
        while cursor < len(text) and text[cursor].isalpha():
            cursor += 1
        return text[index:cursor], cursor
    return text[index], index + 1


def _read_group(text: str, index: int) -> tuple[str, int]:
    if index >= len(text) or text[index] != "{":
        raise ValueError("Expected '{' while reading LaTeX group.")
    depth = 1
    cursor = index + 1
    start = cursor
    while cursor < len(text) and depth > 0:
        if text[cursor] == "{":
            depth += 1
        elif text[cursor] == "}":
            depth -= 1
        cursor += 1
    if depth != 0:
        raise ValueError("Unbalanced LaTeX braces.")
    return text[start : cursor - 1], cursor


def _read_bracket_group(text: str, index: int) -> tuple[str, int]:
    if index >= len(text) or text[index] != "[":
        raise ValueError("Expected '[' while reading optional group.")
    depth = 1
    cursor = index + 1
    start = cursor
    while cursor < len(text) and depth > 0:
        if text[cursor] == "[":
            depth += 1
        elif text[cursor] == "]":
            depth -= 1
        cursor += 1
    if depth != 0:
        raise ValueError("Unbalanced optional group.")
    return text[start : cursor - 1], cursor


def _skip_spaces(text: str, index: int) -> int:
    cursor = index
    while cursor < len(text) and text[cursor].isspace():
        cursor += 1
    return cursor


def _read_required_group(text: str, index: int, allow_optional_brackets: bool = False) -> tuple[str, int]:
    cursor = _skip_spaces(text, index)
    if allow_optional_brackets and cursor < len(text) and text[cursor] == "[":
        _, cursor = _read_bracket_group(text, cursor)
        cursor = _skip_spaces(text, cursor)
    if cursor >= len(text) or text[cursor] != "{":
        raise ValueError("Expected braced group after LaTeX command.")
    return _read_group(text, cursor)


def _read_token_for_accent(text: str, index: int) -> tuple[str, int]:
    cursor = _skip_spaces(text, index)
    if cursor < len(text) and text[cursor] == "{":
        return _read_group(text, cursor)
    if cursor < len(text) and text[cursor] == "\\":
        command, next_cursor = _read_command(text, cursor + 1)
        return "\\" + command, next_cursor
    if cursor < len(text):
        return text[cursor], cursor + 1
    return "", cursor


def _read_script_token(text: str, index: int) -> tuple[str, int]:
    cursor = _skip_spaces(text, index)
    if cursor >= len(text):
        return "", cursor
    if text[cursor] == "{":
        return _read_group(text, cursor)
    if text[cursor] == "\\":
        command, next_cursor = _read_command(text, cursor + 1)
        if command in GROUP_TEXT_COMMANDS:
            group, end_cursor = _read_required_group(text, next_cursor)
            return _convert_latex_fragment(group), end_cursor
        if command in SYMBOL_COMMANDS:
            return SYMBOL_COMMANDS[command], next_cursor
        return command, next_cursor
    return text[cursor], cursor + 1


def _format_script_token(token: str) -> str:
    value = token.strip()
    if re.fullmatch(r"[A-Za-z0-9\u0370-\u03ff*]", value):
        return value
    return f"({value})"


def _apply_accent(text: str, accent: str) -> str:
    value = text.strip()
    if not value:
        return value
    if len(value) == 1:
        return value + accent
    return value + accent


def _word_formula_upgrade_script() -> str:
    return r"""
param(
    [Parameter(Mandatory = $true)][string]$DocxPath,
    [Parameter(Mandatory = $true)][string]$ManifestPath
)

$ErrorActionPreference = 'Stop'
$word = $null
$doc = $null

try {
    $items = Get-Content -LiteralPath $ManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $doc = $word.Documents.Open((Resolve-Path $DocxPath).Path, $false, $false)

    $lookup = @{}
    $remaining = New-Object 'System.Collections.Generic.HashSet[string]'
    foreach ($item in $items) {
        $lookup[$item.placeholder] = $item.linear
        [void]$remaining.Add($item.placeholder)
    }

    foreach ($paragraph in $doc.Paragraphs) {
        $paragraphText = $paragraph.Range.Text
        if ($null -eq $paragraphText) {
            continue
        }
        $key = $paragraphText.Trim()
        if ($lookup.ContainsKey($key)) {
            $range = $paragraph.Range
            $range.End = $range.End - 1
            $eqRange = $doc.OMaths.Add($range)
            $eqRange.Text = $lookup[$key]
            $eqRange.OMaths.Item(1).BuildUp() | Out-Null
            [void]$remaining.Remove($key)
        }
    }

    if ($remaining.Count -gt 0) {
        $missing = (($remaining | Sort-Object) -join ', ')
        throw "Formula placeholder not found: $missing"
    }

    $doc.Fields.Update() | Out-Null
    foreach ($toc in $doc.TablesOfContents) {
        $toc.Update() | Out-Null
    }
    $doc.Save()
}
finally {
    if ($doc -ne $null) {
        $doc.Close($false)
    }
    if ($word -ne $null) {
        $word.Quit() | Out-Null
    }
}
"""
