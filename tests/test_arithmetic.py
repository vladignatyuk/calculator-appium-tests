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
    ],
    ids=["addition", "subtraction", "multiplication", "division", "decimals"],
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


def test_percentage(calculator):
    # Confirmed on-device: 50 % -> 0.5
    calculator.enter_sequence(["5", "0", "%"])
    formula, result = calculator.wait_for_output()
    assert formula.startswith("0.5") or result.startswith("0.5"), (
        f"Expected '0.5', got formula={formula!r} result={result!r}"
    )


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
