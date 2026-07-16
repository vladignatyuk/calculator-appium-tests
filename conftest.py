# -*- coding: utf-8 -*-
"""Shared pytest fixtures: Appium session lifecycle + a ready-to-use Calculator page."""

import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options

from pages.calculator_page import CalculatorPage, CALC_PKG

# Real device serial from `adb devices`. Change this to match your own device.
DEVICE_UDID = "RZCX11XCA4T"

APPIUM_SERVER_URL = "http://127.0.0.1:4723/wd/hub"


def _build_driver():
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.udid = DEVICE_UDID
    options.device_name = "Galaxy A54"
    options.no_reset = True
    options.new_command_timeout = 120
    return webdriver.Remote(APPIUM_SERVER_URL, options=options)


@pytest.fixture
def driver():
    """Raw Appium driver, for tests that want it directly."""
    drv = _build_driver()
    yield drv
    drv.quit()


@pytest.fixture
def calculator(driver):
    """A CalculatorPage on a freshly launched, cleared keypad screen."""
    page = CalculatorPage(driver).launch()
    page.clear()
    return page
