# -*- coding: utf-8 -*-
"""Page Object for the calculation history panel."""

from typing import List, Tuple

from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait

CALC_PKG = "com.sec.android.app.popupcalculator"


class HistoryPage:
    LIST_VIEW = f"{CALC_PKG}:id/calc_history_list_view"
    ITEM_FORMULA = f"{CALC_PKG}:id/calc_history_item_formula"
    ITEM_RESULT = f"{CALC_PKG}:id/calc_history_item_result"
    CLEAR_BTN = f"{CALC_PKG}:id/calc_history_btn_clear"

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    def is_open(self) -> bool:
        elements = self.driver.find_elements(AppiumBy.ID, self.LIST_VIEW)
        return bool(elements) and elements[0].is_displayed()

    def get_entries(self) -> List[Tuple[str, str]]:
        """Return [(formula_text, result_text), ...] for each history row.

        Confirmed on-device: rows are in chronological order (oldest first,
        most recent last), not most-recent-first. Only currently-rendered
        rows are returned -- older entries scrolled out of the (RecyclerView)
        viewport are not included unless scrolled into view first.
        """
        formulas = [e.text.strip() for e in self.driver.find_elements(AppiumBy.ID, self.ITEM_FORMULA)]
        results = [e.text.strip() for e in self.driver.find_elements(AppiumBy.ID, self.ITEM_RESULT)]
        return list(zip(formulas, results))

    def clear_history(self) -> "HistoryPage":
        self.driver.find_element(AppiumBy.ID, self.CLEAR_BTN).click()
        return self

    def close(self) -> "HistoryPage":
        """History is a slide-down panel over the keypad; back returns to it.

        Confirmed on-device: the panel can dismiss itself on its own (e.g.
        right after clearing it to empty), so only press back if it's still
        actually open -- otherwise this over-navigates out of the app.
        """
        if self.is_open():
            self.driver.back()
        return self
