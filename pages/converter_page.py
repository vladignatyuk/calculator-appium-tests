# -*- coding: utf-8 -*-
"""Page Object for the unit converter screen (ruler icon)."""

import re

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

CALC_PKG = "com.sec.android.app.popupcalculator"

# The Spinner containers (converter_pager_spinner_1/_2) have no text of their
# own -- the actually-displayed unit name lives in a nested child view with
# this (shared) resource-id, so it must be looked up scoped to each spinner.
_SELECTED_ITEM_ID = f"{CALC_PKG}:id/converter_spinner_selected_item"

# The input fields' accessibility text wraps the numeric value with extra
# wording, e.g. "Second number for conversion 4046.8564224 Square meters" or
# "First number for conversion 1". Pull out just the number.
_NUMERIC_RE = re.compile(r"[-+]?\d[\d,]*\.?\d*")


def extract_numeric(text):
    match = _NUMERIC_RE.search(text)
    if not match:
        return ""
    return match.group(0).replace(",", "")


class ConverterPage:
    TAB_TITLE = f"{CALC_PKG}:id/converter_tab_item_title"
    SPINNER_1 = f"{CALC_PKG}:id/converter_pager_spinner_1"
    SPINNER_2 = f"{CALC_PKG}:id/converter_pager_spinner_2"
    INPUT_1 = f"{CALC_PKG}:id/converter_pager_edt_1"
    INPUT_2 = f"{CALC_PKG}:id/converter_pager_edt_2"
    BACK_BTN = f"{CALC_PKG}:id/converter_btn_back"

    DOT_BTN = f"{CALC_PKG}:id/converter_keypad_btn_dot"
    CLEAR_BTN = f"{CALC_PKG}:id/converter_keypad_btn_clear"
    BACKSPACE_BTN = f"{CALC_PKG}:id/converter_keypad_btn_backspace"
    _DIGIT_IDS = {str(d): f"{CALC_PKG}:id/converter_keypad_btn_0{d}" for d in range(10)}

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    def wait_loaded(self):
        self.wait.until(EC.presence_of_element_located((AppiumBy.ID, self.INPUT_1)))
        return self

    def active_tab_title(self):
        return self.driver.find_element(AppiumBy.ID, self.TAB_TITLE).text.strip()

    def _spinner_text(self, spinner_locator):
        spinner = self.driver.find_element(AppiumBy.ID, spinner_locator)
        selected = spinner.find_element(AppiumBy.ID, _SELECTED_ITEM_ID)
        return selected.text.strip()

    def unit_1(self):
        return self._spinner_text(self.SPINNER_1)

    def unit_2(self):
        return self._spinner_text(self.SPINNER_2)

    def type_value(self, value):
        """Type digits/dot into the active (source) field via the converter's own keypad."""
        for ch in str(value):
            if ch == ".":
                self.driver.find_element(AppiumBy.ID, self.DOT_BTN).click()
            else:
                self.driver.find_element(AppiumBy.ID, self._DIGIT_IDS[ch]).click()
        return self

    def clear_value(self):
        self.driver.find_element(AppiumBy.ID, self.CLEAR_BTN).click()
        return self

    def backspace(self):
        self.driver.find_element(AppiumBy.ID, self.BACKSPACE_BTN).click()
        return self

    def get_source_value(self):
        raw = self.driver.find_element(AppiumBy.ID, self.INPUT_1).text.strip()
        return extract_numeric(raw)

    def get_converted_value(self):
        raw = self.driver.find_element(AppiumBy.ID, self.INPUT_2).text.strip()
        return extract_numeric(raw)

    def go_back(self):
        self.driver.find_element(AppiumBy.ID, self.BACK_BTN).click()
        return self
