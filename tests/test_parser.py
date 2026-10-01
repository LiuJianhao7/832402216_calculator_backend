import sys
import unittest
from decimal import Decimal
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from parser import (
    DivisionByZeroExpressionError,
    InvalidExpressionError,
    evaluate_expression,
)


class ParserTests(unittest.TestCase):
    def test_valid_expressions(self):
        cases = {
            "12+8": Decimal("20"),
            "10-3*2": Decimal("4"),
            "(1+2)*3": Decimal("9"),
            "10/4": Decimal("2.5"),
            "-5+8": Decimal("3"),
            "3*-2": Decimal("-6"),
            "+.5 + 1.25": Decimal("1.75"),
            "2 × (3 + 4)": Decimal("14"),
        }
        for expression, expected in cases.items():
            with self.subTest(expression=expression):
                self.assertEqual(evaluate_expression(expression), expected)

    def test_division_by_zero(self):
        with self.assertRaises(DivisionByZeroExpressionError):
            evaluate_expression("1/(2-2)")

    def test_invalid_expressions(self):
        for expression in ["", "1+", "(1+2", "2..3+1", "abc+1"]:
            with self.subTest(expression=expression):
                with self.assertRaises(InvalidExpressionError):
                    evaluate_expression(expression)


if __name__ == "__main__":
    unittest.main()
