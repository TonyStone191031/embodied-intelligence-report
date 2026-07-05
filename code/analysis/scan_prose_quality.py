from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


CHINESE_RE = re.compile(r"[\u4e00-\u9fff]")
LATIN_WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9_./+-]*")
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
ONLY_LINK_RE = re.compile(r"^\s*\[[^\]]+\]\(([^)]+)\)\s*$")
TABLE_LINE_RE = re.compile(r"^\s*\|.*\|\s*$")
TABLE_ALIGN_RE = re.compile(r"^\s*\|?[:\- ]+\|[:\-| ]+\s*$")
ORDERED_LIST_RE = re.compile(r"^\s*\d+\.\s+")
UNORDERED_LIST_RE = re.compile(r"^\s*[-*+]\s+")
INLINE_MATH_RE = re.compile(r"\\\(.+?\\\)|\\\[.+?\\\]|\$[^$]+\$", re.DOTALL)
ACRONYM_RE = re.compile(r"^[A-Z]{1,6}(?:-\d+)?$")
MIXED_OK_RE = re.compile(
    r"^(?:RT-\d+|VLA|VLM|LLM|RL|SLAM|MPC|LQR|PID|RRT|A\*|SE|SO|JEPA|ACT|QT-Opt|DOI|URL|API|ROS|GPU)$"
)
PROPER_NOUN_OK_RE = re.compile(
    r"^(?:NVIDIA|Google|DeepMind|Boston|Dynamics|Figure|Tesla|Optimus|Spot|Habitat|MuJoCo|Gazebo|Omniverse|Isaac|Apptronik|Agility|Sanctuary|UBTECH|Skydio)$"
)


def is_link_label_mostly_english(label: str) -> bool:
    cleaned = label.strip("《》“”\"' ")
    if "《" in label or "》" in label:
        return False
    if CHINESE_RE.search(cleaned):
        return False
    latin_words = LATIN_WORD_RE.findall(cleaned)
    if not latin_words:
        return False
    if "|" in cleaned:
        return True
    if len(latin_words) == 1 and len(cleaned) <= 20:
        return False
    if len(latin_words) <= 2 and len(cleaned) <= 16:
        return False
    return True


def strip_links(line: str) -> str:
    return LINK_RE.sub("", line)


def strip_inline_code(line: str) -> str:
    parts = line.split("`")
    if len(parts) == 1:
        return line
    kept: list[str] = []
    for index, part in enumerate(parts):
        if index % 2 == 0:
            kept.append(part)
    return "".join(kept)


def strip_inline_math(line: str) -> str:
    return INLINE_MATH_RE.sub("", line)


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def looks_like_display_math(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if stripped in {"\\[", "\\]"}:
        return True
    math_markers = ("\\frac", "\\text{", "\\bigl", "\\bigr", "\\qquad", "\\quad", "^", "_", "\\mid")
    return stripped.startswith("\\") or sum(marker in stripped for marker in math_markers) >= 2


def count_meaningful_latin_words(text: str) -> list[str]:
    words = LATIN_WORD_RE.findall(text)
    kept: list[str] = []
    for word in words:
        normalized = word.strip(".,;:()[]{}")
        if ACRONYM_RE.match(normalized):
            continue
        if MIXED_OK_RE.match(normalized):
            continue
        if PROPER_NOUN_OK_RE.match(normalized):
            continue
        kept.append(normalized)
    return kept


def iter_markdown_lines(path: Path):
    in_fence = False
    fence_lang = ""
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = raw_line.strip()
        if stripped.startswith("```"):
            if in_fence:
                in_fence = False
                fence_lang = ""
            else:
                in_fence = True
                fence_lang = stripped[3:].strip().lower()
            continue
        if in_fence:
            continue
        if not stripped:
            continue
        if stripped.startswith("#") or stripped.startswith(">"):
            continue
        if TABLE_LINE_RE.match(raw_line) or TABLE_ALIGN_RE.match(raw_line):
            continue
        if ORDERED_LIST_RE.match(raw_line) or UNORDERED_LIST_RE.match(raw_line):
            continue
        yield line_number, raw_line, stripped


def detect_issues(line: str) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    if looks_like_display_math(line):
        return issues
    no_code = strip_inline_code(line)
    no_math = strip_inline_math(no_code)
    no_links = strip_links(no_math)
    if not CHINESE_RE.search(no_code):
        return issues

    latin_words = count_meaningful_latin_words(no_links)
    english_links = [
        {"label": label, "target": target}
        for label, target in LINK_RE.findall(no_code)
        if is_link_label_mostly_english(label)
    ]

    if english_links:
        issues.append(
            {
                "type": "english_link_label",
                "detail": ", ".join(item["label"] for item in english_links[:3]),
            }
        )

    trailing_match = re.search(r"(\[[^\]]+\]\([^)]+\))\s*$", no_code)
    if trailing_match and english_links:
        issues.append(
            {
                "type": "english_link_at_line_end",
                "detail": trailing_match.group(1),
            }
        )

    only_link = ONLY_LINK_RE.match(no_code)
    if only_link:
        issues.append(
            {
                "type": "standalone_link_line",
                "detail": only_link.group(1),
            }
        )

    if len(latin_words) >= 4:
        issues.append(
            {
                "type": "heavy_mixed_language",
                "detail": " ".join(latin_words[:8]),
            }
        )
    elif len(latin_words) >= 2 and any(item["label"] for item in english_links):
        issues.append(
            {
                "type": "mixed_language_with_source_tail",
                "detail": " ".join(latin_words[:8]),
            }
        )

    return issues


def scan_directory(root: Path) -> dict:
    findings: dict[str, list[dict[str, object]]] = defaultdict(list)
    counter = Counter()

    for path in sorted(root.glob("*.md")):
        for line_number, raw_line, stripped in iter_markdown_lines(path):
            issues = detect_issues(stripped)
            if not issues:
                continue
            for issue in issues:
                counter[issue["type"]] += 1
                findings[path.name].append(
                    {
                        "line": line_number,
                        "type": issue["type"],
                        "detail": issue["detail"],
                        "text": normalize_space(stripped),
                    }
                )

    return {
        "root": str(root),
        "summary": dict(counter),
        "files": findings,
    }


def build_markdown_report(result: dict, sample_limit: int) -> str:
    lines: list[str] = []
    lines.append("# 正文语言与引用写法扫描报告")
    lines.append("")
    lines.append(f"- 扫描目录：`{result['root']}`")
    lines.append("")
    lines.append("## 汇总")
    lines.append("")
    for issue_type, count in sorted(result["summary"].items()):
        lines.append(f"- `{issue_type}`：{count}")
    lines.append("")
    lines.append("## 分文件样例")
    lines.append("")

    for file_name in sorted(result["files"]):
        entries = result["files"][file_name]
        by_type = Counter(item["type"] for item in entries)
        stats = ", ".join(f"{key}={value}" for key, value in sorted(by_type.items()))
        lines.append(f"### {file_name}")
        lines.append("")
        lines.append(f"- 问题统计：{stats}")
        lines.append("")
        for entry in entries[:sample_limit]:
            lines.append(
                f"- L{entry['line']} | `{entry['type']}` | {entry['text']}"
            )
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan markdown prose for mixed-language and citation-style issues.")
    parser.add_argument(
        "--root",
        default="docs/report/current",
        help="Directory that contains markdown chapter files.",
    )
    parser.add_argument(
        "--output",
        help="Optional markdown output path.",
    )
    parser.add_argument(
        "--sample-limit",
        type=int,
        default=12,
        help="Maximum number of sample lines to keep per file.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print JSON instead of markdown.",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    result = scan_directory(root)

    if args.json:
        payload = json.dumps(result, ensure_ascii=False, indent=2)
    else:
        payload = build_markdown_report(result, sample_limit=args.sample_limit)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(payload, encoding="utf-8")
    else:
        print(payload)


if __name__ == "__main__":
    main()
