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


# UiAutomator2 defaults (waitForIdleTimeout=10000, actionAcknowledgmentTimeout=3000)
# cap how long the server waits for the UI to report itself idle after each
# action -- in practice most taps settle in a few hundred ms, so the default
# ceiling is mostly wasted headroom. Confirmed on-device: 200ms trims that
# waste with zero dropped taps across repeated stress runs (25+ reps).
# Setting it to 0 (skip the idle check entirely) is ~5x faster still, but
# reliably drops taps under the same test -- not worth trading correctness
# for speed in a suite whose entire point is catching real UI bugs.
FAST_SETTINGS = {"waitForIdleTimeout": 200, "actionAcknowledgmentTimeout": 200}


@pytest.fixture(scope="session")
def driver():
    """Raw Appium driver, shared across the whole test run.

    Starting a UiAutomator2 session costs ~2-3s on its own; per-test
    isolation instead comes from the `calculator` fixture forcing a clean
    app relaunch, so there's no correctness reason to pay that cost once
    per test too.
    """
    drv = _build_driver()
    drv.update_settings(FAST_SETTINGS)
    yield drv
    drv.quit()


@pytest.fixture
def calculator(driver):
    """A CalculatorPage on a freshly launched, cleared keypad screen."""
    page = CalculatorPage(driver).launch()
    page.clear()
    return page
