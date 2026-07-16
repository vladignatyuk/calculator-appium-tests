# -*- coding: utf-8 -*-
"""Page Object for the calculation history panel."""

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait

CALC_PKG = "com.sec.android.app.popupcalculator"


class HistoryPage:
    LIST_VIEW = f"{CALC_PKG}:id/calc_history_list_view"
    ITEM_FORMULA = f"{CALC_PKG}:id/calc_history_item_formula"
    ITEM_RESULT = f"{CALC_PKG}:id/calc_history_item_result"
    CLEAR_BTN = f"{CALC_PKG}:id/calc_history_btn_clear"

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    def is_open(self):
        elements = self.driver.find_elements(AppiumBy.ID, self.LIST_VIEW)
        return bool(elements) and elements[0].is_displayed()

    def get_entries(self):
        """Return [(formula_text, result_text), ...] for each history row, most recent first."""
        formulas = [e.text.strip() for e in self.driver.find_elements(AppiumBy.ID, self.ITEM_FORMULA)]
        results = [e.text.strip() for e in self.driver.find_elements(AppiumBy.ID, self.ITEM_RESULT)]
        return list(zip(formulas, results))

    def clear_history(self):
        self.driver.find_element(AppiumBy.ID, self.CLEAR_BTN).click()
        return self

    def close(self):
        """History is a slide-down panel over the keypad; back returns to it."""
        self.driver.back()
        return self
