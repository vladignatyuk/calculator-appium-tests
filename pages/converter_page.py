# -*- coding: utf-8 -*-
"""Page Object for the unit converter screen (ruler icon)."""

import re
from typing import Union

from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webdriver import WebDriver
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

# Negative converted values (e.g. Fahrenheit -> Celsius below 32F) are shown
# with a typographic minus sign (U+2212), not an ASCII hyphen -- normalize it
# first or the regex above silently drops the sign and returns a positive
# number for a negative value.
_UNICODE_MINUS = "−"


def extract_numeric(text: str) -> str:
    text = text.replace(_UNICODE_MINUS, "-")
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

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    def wait_loaded(self) -> "ConverterPage":
        self.wait.until(EC.presence_of_element_located((AppiumBy.ID, self.INPUT_1)))
        return self

    def active_tab_title(self) -> str:
        """Return the name of the currently-selected category tab.

        Confirmed on-device: TAB_TITLE matches all 5 tab-strip entries (Area,
        Length, Temperature, Volume, Mass), so grabbing the first match
        always returns "Area" regardless of which tab is actually selected.
        The selected one is instead identifiable via its content-desc, which
        ends with "Selected" (e.g. "Temperature Tab 3 of 9 Selected").
        """
        for tab in self.driver.find_elements(AppiumBy.ID, self.TAB_TITLE):
            desc = (tab.get_attribute("content-desc") or "").strip()
            if desc.endswith("Selected"):
                return tab.text.strip()
        return self.driver.find_element(AppiumBy.ID, self.TAB_TITLE).text.strip()

    def select_category(self, name: str) -> "ConverterPage":
        """Switch to a converter category tab by its visible name, e.g. 'Temperature'."""
        for tab in self.driver.find_elements(AppiumBy.ID, self.TAB_TITLE):
            if tab.text.strip().lower() == name.lower():
                tab.click()
                return self
        raise ValueError(f"Unknown converter category: {name!r}")

    def _spinner_text(self, spinner_locator: str) -> str:
        spinner = self.driver.find_element(AppiumBy.ID, spinner_locator)
        selected = spinner.find_element(AppiumBy.ID, _SELECTED_ITEM_ID)
        return selected.text.strip()

    def unit_1(self) -> str:
        return self._spinner_text(self.SPINNER_1)

    def unit_2(self) -> str:
        return self._spinner_text(self.SPINNER_2)

    def type_value(self, value: Union[str, int, float]) -> "ConverterPage":
        """Type digits/dot into the active (source) field via the converter's own keypad."""
        for ch in str(value):
            if ch == ".":
                self.driver.find_element(AppiumBy.ID, self.DOT_BTN).click()
            else:
                self.driver.find_element(AppiumBy.ID, self._DIGIT_IDS[ch]).click()
        return self

    def clear_value(self) -> "ConverterPage":
        self.driver.find_element(AppiumBy.ID, self.CLEAR_BTN).click()
        return self

    def backspace(self) -> "ConverterPage":
        self.driver.find_element(AppiumBy.ID, self.BACKSPACE_BTN).click()
        return self

    def get_source_value(self) -> str:
        raw = self.driver.find_element(AppiumBy.ID, self.INPUT_1).text.strip()
        return extract_numeric(raw)

    def get_converted_value(self) -> str:
        raw = self.driver.find_element(AppiumBy.ID, self.INPUT_2).text.strip()
        return extract_numeric(raw)

    def go_back(self) -> "ConverterPage":
        self.driver.find_element(AppiumBy.ID, self.BACK_BTN).click()
        return self
