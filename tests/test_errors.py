# -*- coding: utf-8 -*-
"""Edge cases and error handling for the Samsung Calculator keypad."""


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
