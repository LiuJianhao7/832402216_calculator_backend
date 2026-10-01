"""Safe recursive-descent parser for calculator expressions.

Supported grammar::

    expression := term (("+" | "-") term)*
    term       := factor (("*" | "/") factor)*
    factor     := ("+" | "-") factor | primary
    primary    := number | "(" expression ")"

The parser never executes user input as Python code.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, localcontext


class ExpressionError(ValueError):
    """Base class for expression-related errors."""


class InvalidExpressionError(ExpressionError):
    """Raised when the expression is syntactically invalid."""


class DivisionByZeroExpressionError(ExpressionError):
    """Raised when division by zero is attempted."""


@dataclass
class Parser:
    """Parse and evaluate an arithmetic expression safely."""

    text: str
    max_length: int = 200

    def __post_init__(self) -> None:
        self.text = self.text.strip().replace("×", "*").replace("÷", "/")
        self.pos = 0
        if not self.text:
            raise InvalidExpressionError("Expression cannot be empty")
        if len(self.text) > self.max_length:
            raise InvalidExpressionError("Expression is too long")

    def parse(self) -> Decimal:
        """Return the evaluated value for the entire expression."""
        with localcontext() as context:
            context.prec = 28
            value = self._parse_expression()
            self._skip_spaces()
            if self.pos != len(self.text):
                raise InvalidExpressionError(
                    f"Unexpected character at position {self.pos + 1}"
                )
            return +value

    def _parse_expression(self) -> Decimal:
        value = self._parse_term()
        while True:
            self._skip_spaces()
            if self._match("+"):
                value += self._parse_term()
            elif self._match("-"):
                value -= self._parse_term()
            else:
                return value

    def _parse_term(self) -> Decimal:
        value = self._parse_factor()
        while True:
            self._skip_spaces()
            if self._match("*"):
                value *= self._parse_factor()
            elif self._match("/"):
                divisor = self._parse_factor()
                if divisor == 0:
                    raise DivisionByZeroExpressionError("Division by zero")
                value /= divisor
            else:
                return value

    def _parse_factor(self) -> Decimal:
        self._skip_spaces()
        if self._match("+"):
            return self._parse_factor()
        if self._match("-"):
            return -self._parse_factor()
        return self._parse_primary()

    def _parse_primary(self) -> Decimal:
        self._skip_spaces()
        if self._match("("):
            value = self._parse_expression()
            self._skip_spaces()
            if not self._match(")"):
                raise InvalidExpressionError("Missing closing parenthesis")
            return value
        return self._parse_number()

    def _parse_number(self) -> Decimal:
        self._skip_spaces()
        start = self.pos
        dot_count = 0
        digit_count = 0

        while self.pos < len(self.text):
            char = self.text[self.pos]
            if char.isdigit():
                digit_count += 1
                self.pos += 1
                continue
            if char == ".":
                dot_count += 1
                if dot_count > 1:
                    raise InvalidExpressionError("A number cannot contain two decimal points")
                self.pos += 1
                continue
            break

        token = self.text[start : self.pos]
        if digit_count == 0 or token == ".":
            if start >= len(self.text):
                raise InvalidExpressionError("Unexpected end of expression")
            raise InvalidExpressionError(
                f"Expected a number at position {start + 1}"
            )

        try:
            return Decimal(token)
        except InvalidOperation as exc:
            raise InvalidExpressionError("Invalid number") from exc

    def _skip_spaces(self) -> None:
        while self.pos < len(self.text) and self.text[self.pos].isspace():
            self.pos += 1

    def _match(self, expected: str) -> bool:
        if self.pos < len(self.text) and self.text[self.pos] == expected:
            self.pos += 1
            return True
        return False


def evaluate_expression(expression: str) -> Decimal:
    """Convenience function used by the service layer and tests."""
    if not isinstance(expression, str):
        raise InvalidExpressionError("Expression must be a string")
    return Parser(expression).parse()


def decimal_to_string(value: Decimal) -> str:
    """Format Decimal for stable display and storage without float artifacts."""
    if value == 0:
        return "0"

    normalized = value.normalize()
    text = format(normalized, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text
