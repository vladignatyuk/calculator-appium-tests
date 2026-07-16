# -*- coding: utf-8 -*-
"""Edge cases and error handling for the Samsung Calculator keypad."""

import pytest

pytestmark = pytest.mark.negative


def test_divide_by_zero_shows_error(calculator):
    # Confirmed on-device: shows a "cannot divide by zero" style message.
    calculator.enter_sequence(["5", "/", "0", "="])
    formula, result = calculator.wait_for_output()
    combined = f"{formula} {result}".lower()
    assert "divide" in combined and ("zero" in combined or "0" in combined), (
        f"Expected a divide-by-zero error, got formula={formula!r} result={result!r}"
    )


def test_long_number_does_not_crash(calculator):
    digits = list("123456789012345678")
    calculator.enter_sequence(digits)
    formula, result = calculator.wait_for_output()
    assert formula or result, "Expected calculator to display something for a long number without crashing"


def test_repeated_operator_uses_latest(calculator):
    """Pressing an operator right after another shouldn't crash the app.

    NOTE: exact resulting value depends on how Samsung Calculator resolves
    "5 + - 3" internally (treats it as 5 + (-3) on most OneUI versions).
    Adjust the expected value below if your first run shows otherwise.
    """
    calculator.enter_sequence(["5", "+", "-", "3", "="])
    formula, result = calculator.wait_for_output()
    assert formula.startswith("2") or result.startswith("2"), (
        f"Expected '2' (5 + (-3)), got formula={formula!r} result={result!r}"
    )


def test_zero_divided_by_zero_shows_error(calculator):
    # Confirmed on-device: same "cannot divide by zero" style message as 5/0.
    calculator.enter_sequence(["0", "/", "0", "="])
    formula, result = calculator.wait_for_output()
    combined = f"{formula} {result}".lower()
    assert "divide" in combined and "0" in combined, (
        f"Expected a divide-by-zero error for 0/0, got formula={formula!r} result={result!r}"
    )


def test_negative_dividend_divided_by_zero_shows_error(calculator):
    calculator.enter_sequence(["5", "+/-", "/", "0", "="])
    formula, result = calculator.wait_for_output()
    combined = f"{formula} {result}".lower()
    assert "divide" in combined and "0" in combined, (
        f"Expected a divide-by-zero error for -5/0, got formula={formula!r} result={result!r}"
    )


@pytest.mark.boundary
def test_backspace_on_empty_display_does_not_crash(calculator):
    calculator.backspace()
    formula, result = calculator.get_formula_text(), calculator.get_result_text()
    assert formula in ("", "0") and result in ("", "0"), (
        f"Expected backspace on an empty display to stay empty, got formula={formula!r} result={result!r}"
    )


@pytest.mark.boundary
def test_clear_on_already_empty_display_does_not_crash(calculator):
    calculator.clear()
    formula, result = calculator.get_formula_text(), calculator.get_result_text()
    assert formula in ("", "0") and result in ("", "0"), (
        f"Expected clear on an already-empty display to stay empty, got formula={formula!r} result={result!r}"
    )


@pytest.mark.boundary
def test_double_decimal_point_is_ignored(calculator):
    # Confirmed on-device: a second '.' press in the same number is a no-op.
    calculator.enter_sequence(["5", ".", ".", "5"])
    formula = calculator.get_formula_text()
    assert formula == "5.5", f"Expected the extra '.' to be ignored, got {formula!r}"


def test_overflow_multiplication_uses_scientific_notation(calculator):
    # Confirmed on-device: results too large for the display switch to
    # scientific notation instead of crashing or truncating silently.
    digits = list("999999999")
    calculator.enter_sequence(digits + ["*"] + digits + ["="])
    formula, result = calculator.wait_for_output()
    combined = f"{formula}{result}"
    assert "E" in combined, (
        f"Expected scientific notation for an overflowing product, got formula={formula!r} result={result!r}"
    )


def test_operator_pressed_before_any_operand_does_not_crash(calculator):
    # Confirmed on-device: a leading operator with nothing typed yet is a
    # no-op -- entry effectively starts fresh from the next digit.
    calculator.enter_sequence(["+", "5", "="])
    formula, result = calculator.wait_for_output()
    assert formula.startswith("5") or result.startswith("5"), (
        f"Expected a leading '+' to be harmless, got formula={formula!r} result={result!r}"
    )


@pytest.mark.boundary
def test_equals_on_empty_display_does_not_crash(calculator):
    calculator.press("=")
    formula, result = calculator.get_formula_text(), calculator.get_result_text()
    assert formula in ("", "0") and result in ("", "0"), (
        f"Expected '=' on an empty display to stay empty, got formula={formula!r} result={result!r}"
    )


def test_unclosed_parenthesis_does_not_crash(calculator):
    # Confirmed on-device: an unclosed "(" is tolerated -- '=' evaluates the
    # expression as if it had been closed, rather than erroring or hanging.
    calculator.enter_sequence(["()", "2", "+", "3", "="])
    formula, result = calculator.wait_for_output()
    assert formula.startswith("5") or result.startswith("5"), (
        f"Expected an unclosed paren to still evaluate to '5', got formula={formula!r} result={result!r}"
    )
