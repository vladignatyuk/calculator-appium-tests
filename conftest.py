# -*- coding: utf-8 -*-
"""Shared pytest fixtures: Appium session lifecycle + ready-to-use page objects."""

import os
import re
import time
from pathlib import Path
from typing import Generator

import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.webdriver import WebDriver

from pages.calculator_page import CalculatorPage
from pages.converter_page import ConverterPage

# Device serial from `adb devices` and the Appium server URL are both
# overridable via env vars, so the suite can run on a different machine or
# device without editing source (e.g. CALC_DEVICE_UDID=ABC123 pytest).
DEVICE_UDID = os.environ.get("CALC_DEVICE_UDID", "RZCX11XCA4T")
APPIUM_SERVER_URL = os.environ.get("CALC_APPIUM_SERVER_URL", "http://127.0.0.1:4723/wd/hub")

ARTIFACTS_DIR = Path(__file__).parent / "artifacts"


def _build_driver() -> WebDriver:
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
def driver() -> Generator[WebDriver, None, None]:
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
def calculator(driver: WebDriver) -> CalculatorPage:
    """A CalculatorPage on a freshly launched, cleared keypad screen."""
    page = CalculatorPage(driver).launch()
    page.clear()
    return page


@pytest.fixture
def converter(calculator: CalculatorPage) -> Generator[ConverterPage, None, None]:
    """A ConverterPage opened from the keypad.

    Always restored to the default 'Area' category on teardown -- even if
    the test itself raises -- because category selection is an app-level
    preference that persists across process restarts. Without this, a test
    that fails partway through switching category (e.g. an assertion on the
    Temperature tab) would leave that category selected for every test/run
    afterwards, silently breaking test_converter_default_area_units.
    """
    calculator.open_converter()
    page = ConverterPage(calculator.driver).wait_loaded()
    yield page
    try:
        if page.active_tab_title().lower() != "area":
            page.select_category("Area")
    finally:
        page.go_back()


def _sanitize(nodeid: str) -> str:
    return re.sub(r"[^\w.-]", "_", nodeid)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """On failure, save a screenshot + the UI hierarchy dump for debugging.

    Standard practice for mobile E2E: a failure message alone rarely
    explains *why* a locator didn't match or a value was wrong on a device
    you don't have in front of you. Both files are named after the test so
    they're easy to match back to a specific failure.
    """
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or not report.failed:
        return

    drv = item.funcargs.get("driver")
    if drv is None:
        return

    ARTIFACTS_DIR.mkdir(exist_ok=True)
    base = ARTIFACTS_DIR / f"{_sanitize(item.nodeid)}_{time.strftime('%Y%m%d-%H%M%S')}"

    try:
        drv.get_screenshot_as_file(str(base) + ".png")
    except Exception as e:
        print(f"[conftest] Could not save failure screenshot: {e!r}")

    try:
        (base.with_suffix(".xml")).write_text(drv.page_source, encoding="utf-8")
    except Exception as e:
        print(f"[conftest] Could not save failure page source: {e!r}")
