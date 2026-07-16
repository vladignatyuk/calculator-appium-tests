# -*- coding: utf-8 -*-
"""Coverage for the calculation history panel."""

from pages.history_page import HistoryPage


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
