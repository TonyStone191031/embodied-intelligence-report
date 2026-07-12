from __future__ import annotations

import unittest

from common import is_formula_like_block
from docx_math_upgrade import build_formula_omml, is_cases_formula, latex_to_word_linear
from render_assets import render_formula_to_lines
from lxml import etree


class LatexToWordLinearTests(unittest.TestCase):
    def test_fraction_accepts_unbraced_text_command_as_denominator(self) -> None:
        converted = latex_to_word_linear(
            r"\frac{\text{data infrastructure}}\text{narrative heat}"
        )

        self.assertEqual(converted, "(data infrastructure)/(narrative heat)")

    def test_fraction_without_denominator_still_fails(self) -> None:
        with self.assertRaises(ValueError):
            latex_to_word_linear(r"\frac{a}")

    def test_formula_like_text_block_is_detected(self) -> None:
        self.assertTrue(is_formula_like_block(r"\mathcal{S}_{act} = \{x, y\}"))
        self.assertFalse(is_formula_like_block("while robot_alive: controller.read()"))

    def test_pdf_formula_lines_share_the_linear_converter(self) -> None:
        self.assertEqual(render_formula_to_lines(r"\mathcal{S}_{act} = \{x, y\}"), ["S_(act) = {x, y}"])

    def test_cases_formula_becomes_an_omml_matrix_with_a_left_brace(self) -> None:
        formula = r"""\mathbb{I}_{\text{mainline}}(x)=
\begin{cases}
1, & x\ \text{physical loop}\\
0, & x\ \text{hotword only}
\end{cases}"""
        node = build_formula_omml(formula)
        xml = etree.tostring(node, encoding="unicode")
        self.assertTrue(is_cases_formula(formula))
        self.assertIn('m:begChr m:val="{"', xml)
        self.assertIn("<m:mr>", xml)


if __name__ == "__main__":
    unittest.main()
