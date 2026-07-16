# -*- coding: utf-8 -*-
"""Page Object for the main Samsung Calculator keypad screen."""

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

CALC_PKG = "com.sec.android.app.popupcalculator"

# Samsung's accessibility layer wraps the raw displayed value with extra
# words, e.g.:
#   "10 Calculation result"          -> 10
#   "Minus 2 Calculation result"     -> -2
#   "Calculator input field 12"      -> 12
#   "Calculator input field"         -> "" (empty field)
_SUFFIXES = (" Calculation result",)
_PREFIXES = ("Calculator input field",)


def normalize_display_text(raw):
    """Strip Samsung's accessibility prefix/suffix wording down to the raw value."""
    text = raw.strip()
    for suffix in _SUFFIXES:
        if text.endswith(suffix):
            text = text[: -len(suffix)].strip()
    for prefix in _PREFIXES:
        if text.startswith(prefix):
            text = text[len(prefix):].strip()
    text = text.replace("Minus", "-").replace("minus", "-")
    text = text.replace("- ", "-")
    return text.strip()


class CalculatorPage:
    """Locators + actions for the keypad screen (the app's default screen)."""

    PKG = CALC_PKG

    FORMULA_FIELD = f"{CALC_PKG}:id/calc_edt_formula"
    RESULT_FIELD = f"{CALC_PKG}:id/calc_tv_result"
    BACKSPACE_BTN = f"{CALC_PKG}:id/calc_handle_btn_delete"
    HISTORY_BTN = f"{CALC_PKG}:id/calc_handle_btn_history"
    CONVERTER_BTN = f"{CALC_PKG}:id/calc_handle_btn_converter"

    _DIGIT_IDS = {str(d): f"{CALC_PKG}:id/calc_keypad_btn_0{d}" for d in range(10)}
    _OP_IDS = {
        "+": f"{CALC_PKG}:id/calc_keypad_btn_add",
        "-": f"{CALC_PKG}:id/calc_keypad_btn_sub",
        "*": f"{CALC_PKG}:id/calc_keypad_btn_mul",
        "/": f"{CALC_PKG}:id/calc_keypad_btn_div",
        ".": f"{CALC_PKG}:id/calc_keypad_btn_dot",
        "=": f"{CALC_PKG}:id/calc_keypad_btn_equal",
        "%": f"{CALC_PKG}:id/calc_keypad_btn_percentage",
        "+/-": f"{CALC_PKG}:id/calc_keypad_btn_plusminus",
        "()": f"{CALC_PKG}:id/calc_keypad_btn_parenthesis",
        "C": f"{CALC_PKG}:id/calc_keypad_btn_clear",
    }

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    # --- lifecycle / navigation ---
    def launch(self):
        # Force a clean process restart so every test starts on the keypad
        # screen, even if a previous test left the app on history/converter
        # (e.g. because it failed before navigating back).
        self.driver.terminate_app(self.PKG)
        self.driver.activate_app(self.PKG)
        self.wait.until(EC.presence_of_element_located((AppiumBy.ID, self._DIGIT_IDS["7"])))
        return self

    def open_history(self):
        self.driver.find_element(AppiumBy.ID, self.HISTORY_BTN).click()
        return self

    def open_converter(self):
        self.driver.find_element(AppiumBy.ID, self.CONVERTER_BTN).click()
        return self

    # --- input ---
    def press(self, key):
        """Press a single key: digit '0'-'9', an operator, '.', '=', '%', '+/-', '()' or 'C'."""
        if key in self._DIGIT_IDS:
            locator = self._DIGIT_IDS[key]
        elif key in self._OP_IDS:
            locator = self._OP_IDS[key]
        else:
            raise ValueError(f"Unknown key: {key!r}")
        self.driver.find_element(AppiumBy.ID, locator).click()
        return self

    def enter_sequence(self, sequence):
        """Press a sequence of keys, e.g. ['7', '+', '3', '=']."""
        for key in sequence:
            self.press(key)
        return self

    def backspace(self):
        self.driver.find_element(AppiumBy.ID, self.BACKSPACE_BTN).click()
        return self

    def clear(self):
        self.press("C")
        return self

    # --- reading state ---
    def get_formula_text(self):
        raw = self.driver.find_element(AppiumBy.ID, self.FORMULA_FIELD).text.strip()
        return normalize_display_text(raw)

    def get_result_text(self):
        raw = self.driver.find_element(AppiumBy.ID, self.RESULT_FIELD).text.strip()
        return normalize_display_text(raw)

    def wait_for_output(self):
        """Wait until either the formula or result field has non-empty text, then return both."""
        self.wait.until(lambda d: self.get_formula_text() or self.get_result_text())
        return self.get_formula_text(), self.get_result_text()
