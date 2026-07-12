from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from markdown_to_latex import convert_markdown, render_inline, render_table


class MarkdownToLatexTests(unittest.TestCase):
    def test_local_links_do_not_leak_machine_paths(self) -> None:
        rendered = render_inline("见 [表格](D:/Projects/embodied-intelligence-report/docs/report/current/tables/example.md)")
        self.assertNotIn("D:/Projects", rendered)
        self.assertIn("表格", rendered)

    def test_inline_math_and_code_are_distinguished(self) -> None:
        rendered = render_inline(r"位姿 \(T \in SE(3)\)，接口 `claim`。")
        self.assertIn(r"\(T \in SE(3)\)", rendered)
        self.assertIn(r"\texttt{\detokenize{claim}}", rendered)

    def test_table_has_single_long_table_environment(self) -> None:
        rendered = render_table([["字段", "含义"], ["task", "任务单元"]])
        self.assertEqual(rendered.count(r"\begin{xltabular}"), 1)
        self.assertEqual(rendered.count(r"\end{xltabular}"), 1)
        self.assertIn(r"\endfirsthead", rendered)

    def test_heading_levels_only_page_break_at_chapter_level(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            source = temp / "source.md"
            output = temp / "chapter.tex"
            source.write_text(
                "# 第一部分\n\n## 1. 章节\n\n### 1.1 小节\n",
                encoding="utf-8",
            )
            convert_markdown(source, output, temp / "figures")
            text = output.read_text(encoding="utf-8")
            self.assertIn(r"\reportpart{第一部分}", text)
            self.assertIn(r"\section*{1. 章节}", text)
            self.assertIn(r"\subsection*{1.1 小节}", text)
            self.assertNotIn(r"\part*{", text)
            self.assertNotIn(r"\chapter*{1. 章节}", text)

    def test_standalone_table_link_advances_input(self) -> None:
        table_path = next(Path("docs/report/current/tables").glob("05-*.md")).resolve().as_posix()
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            source = temp / "source.md"
            output = temp / "chapter.tex"
            source.write_text(f"# 测试章节\n\n见：[表格]({table_path})\n", encoding="utf-8")
            convert_markdown(source, output, temp / "figures")
            text = output.read_text(encoding="utf-8")
            self.assertEqual(text.count(r"\begin{xltabular}"), 1)


if __name__ == "__main__":
    unittest.main()
