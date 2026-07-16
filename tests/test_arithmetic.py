# -*- coding: utf-8 -*-
"""Basic arithmetic coverage for the Samsung Calculator keypad."""

import pytest


@pytest.mark.parametrize(
    "sequence, expected",
    [
        (["7", "+", "3", "="], "10"),
        (["1", "0", "-", "3", "="], "7"),
        (["6", "*", "7", "="], "42"),
        (["1", "0", "/", "2", "="], "5"),
        (["7", ".", "5", "+", "2", ".", "5", "="], "10"),
        (["5", "*", "0", "="], "0"),
        (["3", "-", "1", "0", "="], "-7"),
        (["1", "0", "/", "3", "="], "3.333"),
    ],
    ids=[
        "addition",
        "subtraction",
        "multiplication",
        "division",
        "decimals",
        "multiplication_by_zero",
        "subtraction_to_negative_result",
        "non_terminating_division",
    ],
)
def test_basic_operations(calculator, sequence, expected):
    calculator.enter_sequence(sequence)
    formula, result = calculator.wait_for_output()
    assert formula.startswith(expected) or result.startswith(expected), (
        f"Expected {expected!r}, got formula={formula!r} result={result!r}"
    )


def test_negative_number_with_sign_toggle(calculator):
    calculator.enter_sequence(["5", "+/-", "+", "3", "="])
    formula, result = calculator.wait_for_output()
    assert formula.startswith("-2") or result.startswith("-2"), (
        f"Expected '-2', got formula={formula!r} result={result!r}"
    )


@pytest.mark.parametrize(
    "sequence, expected",
    [
        (["5", "0", "%"], "0.5"),
        (["0", "%"], "0"),
    ],
    ids=["fifty_percent", "zero_percent"],
)
def test_percentage(calculator, sequence, expected):
    # Confirmed on-device: 50 % -> 0.5, 0 % -> 0.
    calculator.enter_sequence(sequence)
    formula, result = calculator.wait_for_output()
    assert formula.startswith(expected) or result.startswith(expected), (
        f"Expected {expected!r}, got formula={formula!r} result={result!r}"
    )


def test_percentage_within_expression(calculator):
    # Confirmed on-device: unlike standalone '%', a percentage used after an
    # operator is taken as a percentage OF the other operand: 10% of 200 is
    # 20, so 200 + 10% = 220 -- a distinct equivalence class from a bare '%'.
    calculator.enter_sequence(["2", "0", "0", "+", "1", "0", "%"])
    formula, result = calculator.wait_for_output()
    assert formula.startswith("220") or result.startswith("220"), (
        f"Expected '220' for 200+10%, got formula={formula!r} result={result!r}"
    )


def test_leading_decimal_point_prepends_zero(calculator):
    # Confirmed on-device: typing '.' before any digit prepends a leading 0.
    calculator.enter_sequence([".", "5"])
    formula = calculator.get_formula_text()
    assert formula == "0.5", f"Expected '0.5' for a leading decimal point, got {formula!r}"


def test_clear_resets_display(calculator):
    calculator.enter_sequence(["1", "2", "3"])
    calculator.clear()
    formula, result = calculator.get_formula_text(), calculator.get_result_text()
    assert formula in ("", "0") and result in ("", "0"), (
        f"Expected empty/zero display after clear, got formula={formula!r} result={result!r}"
    )


def test_backspace_removes_last_digit(calculator):
    calculator.enter_sequence(["1", "2", "3"])
    calculator.backspace()
    formula = calculator.get_formula_text()
    assert formula.startswith("12"), f"Expected '12' after backspace, got {formula!r}"


def test_backspace_on_single_digit_empties_display(calculator):
    # Boundary between "has content" and "empty": backspacing the last
    # remaining digit, not just trimming a multi-digit number.
    calculator.enter_sequence(["5"])
    calculator.backspace()
    formula, result = calculator.get_formula_text(), calculator.get_result_text()
    assert formula in ("", "0") and result in ("", "0"), (
        f"Expected empty display after backspacing the only digit, got formula={formula!r} result={result!r}"
    )


def test_parentheses_change_evaluation_order(calculator):
    # Confirmed on-device: "()" toggles open/close on each press.
    # (2+3)*4 = 20, vs. 2+3*4 = 14 without the parens.
    calculator.enter_sequence(["()", "2", "+", "3", "()", "*", "4", "="])
    formula, result = calculator.wait_for_output()
    assert formula.startswith("20") or result.startswith("20"), (
        f"Expected '20' for (2+3)*4, got formula={formula!r} result={result!r}"
    )


def test_repeated_equals_repeats_last_operation(calculator):
    # Confirmed on-device: pressing '=' again after a result re-applies the
    # last operation to the new total: 5+3=8, then '=' again -> 8+3=11.
    calculator.enter_sequence(["5", "+", "3", "="])
    calculator.wait_for_output()
    calculator.press("=")
    formula, result = calculator.wait_for_output()
    assert formula.startswith("11") or result.startswith("11"), (
        f"Expected '11' after repeating '+3', got formula={formula!r} result={result!r}"
    )


def test_double_sign_toggle_returns_to_original_value(calculator):
    calculator.enter_sequence(["5", "+/-", "+/-"])
    formula = calculator.get_formula_text()
    assert formula == "5", f"Expected '5' after toggling sign twice, got {formula!r}"


def test_leading_zeros_are_collapsed(calculator):
    calculator.enter_sequence(["0", "0", "7"])
    formula = calculator.get_formula_text()
    assert formula == "7", f"Expected leading zeros to collapse to '7', got {formula!r}"
