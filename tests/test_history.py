# -*- coding: utf-8 -*-
"""Coverage for the calculation history panel."""

from pages.history_page import HistoryPage


def _ensure_history_cleared(calculator):
    """Clear history if there's anything to clear.

    Confirmed on-device: opening history while it's already empty doesn't
    render the panel at all (no CLEAR_BTN to click), so clear_history()
    would fail with NoSuchElementException if called unconditionally.
    """
    calculator.open_history()
    history = HistoryPage(calculator.driver)
    if history.is_open():
        history.clear_history()
    history.close()


def test_calculation_appears_in_history(calculator):
    calculator.enter_sequence(["7", "+", "3", "="])
    calculator.wait_for_output()

    calculator.open_history()
    history = HistoryPage(calculator.driver)
    entries = history.get_entries()

    assert any("10" in result or "10" in formula for formula, result in entries), (
        f"Expected an entry containing '10' in history, got {entries!r}"
    )

    history.close()


def test_clear_history_empties_list(calculator):
    calculator.enter_sequence(["1", "+", "1", "="])
    calculator.wait_for_output()

    calculator.open_history()
    history = HistoryPage(calculator.driver)
    history.clear_history()

    assert history.get_entries() == [], "Expected history to be empty after clearing"

    history.close()


def test_history_entries_appear_in_chronological_order(calculator):
    # History persists across app restarts, so start from a known-empty list.
    _ensure_history_cleared(calculator)

    calculator.enter_sequence(["1", "+", "1", "="])
    calculator.wait_for_output()
    calculator.clear()
    calculator.enter_sequence(["2", "+", "2", "="])
    calculator.wait_for_output()

    calculator.open_history()
    history = HistoryPage(calculator.driver)
    entries = history.get_entries()
    history.close()

    formulas = [formula.replace(" ", "") for formula, _ in entries]
    assert formulas == ["1+1", "2+2"], (
        f"Expected entries oldest-first (1+1 before 2+2), got {entries!r}"
    )


def test_repeated_equals_adds_a_separate_history_entry(calculator):
    _ensure_history_cleared(calculator)

    calculator.enter_sequence(["5", "+", "3", "="])
    calculator.wait_for_output()
    calculator.press("=")
    calculator.wait_for_output()

    calculator.open_history()
    history = HistoryPage(calculator.driver)
    entries = history.get_entries()
    history.close()

    formulas = [formula.replace(" ", "") for formula, _ in entries]
    assert formulas == ["5+3", "8+3"], (
        f"Expected the repeated '=' to add its own entry, got {entries!r}"
    )


def test_error_calculation_is_not_recorded_in_history(calculator):
    _ensure_history_cleared(calculator)

    calculator.enter_sequence(["5", "/", "0", "="])
    calculator.wait_for_output()

    calculator.open_history()
    history = HistoryPage(calculator.driver)
    entries = history.get_entries()
    history.close()

    assert entries == [], f"Expected a failed calculation not to be recorded, got {entries!r}"
