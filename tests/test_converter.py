# -*- coding: utf-8 -*-
"""Coverage for the unit converter (ruler icon).

Tests take the `converter` fixture (see conftest.py): it opens the
converter from the keypad and, on teardown, always restores the 'Area'
category regardless of whether the test passed -- category selection
persists across app restarts, so a test that fails mid-switch must not be
allowed to leak that state into later tests/runs.
"""

import pytest


@pytest.mark.smoke
def test_converter_default_area_units(converter):
    # Confirmed on-device: default tab is Area, default units Acres / Square Meters.
    assert converter.active_tab_title().lower() == "area", (
        f"Expected default tab 'Area', got {converter.active_tab_title()!r}"
    )
    assert "acre" in converter.unit_1().lower(), f"Expected 'Acres', got {converter.unit_1()!r}"
    assert "square meter" in converter.unit_2().lower(), (
        f"Expected 'Square Meters', got {converter.unit_2()!r}"
    )


@pytest.mark.smoke
def test_converter_produces_output_value(converter):
    # Confirmed on-device: default Area conversion is Acres -> Square Meters,
    # 1 Acre = 4046.8564224 Square Meters.
    converter.clear_value()
    converter.type_value("1")

    converted = converter.get_converted_value()
    assert converted, "Expected a converted value to appear in the second field"
    assert float(converted) == pytest.approx(4046.8564224), (
        f"Expected ~4046.8564224 (1 Acre in Square Meters), got {converted!r}"
    )


def test_converter_switch_category_updates_units(converter):
    # Confirmed on-device: switching tabs changes both units and the
    # conversion in effect. 100 Fahrenheit = 37.7777777778 Celsius.
    converter.select_category("Temperature")
    converter.wait_loaded()

    assert converter.active_tab_title().lower() == "temperature", (
        f"Expected active tab 'Temperature', got {converter.active_tab_title()!r}"
    )
    assert "fahrenheit" in converter.unit_1().lower(), f"Expected 'Fahrenheit', got {converter.unit_1()!r}"
    assert "celsius" in converter.unit_2().lower(), f"Expected 'Celsius', got {converter.unit_2()!r}"

    converter.clear_value()
    converter.type_value("100")
    converted = converter.get_converted_value()
    assert float(converted) == pytest.approx(37.7777777778, rel=1e-6), (
        f"Expected ~37.7777777778 (100F in Celsius), got {converted!r}"
    )


@pytest.mark.negative
def test_converter_handles_negative_converted_value(converter):
    # Confirmed on-device: negative results are shown with a typographic
    # minus sign (U+2212, not ASCII '-'); this is a real edge case, not
    # just a locator issue -- see extract_numeric() in converter_page.py.
    converter.select_category("Temperature")
    converter.wait_loaded()

    converter.clear_value()
    converter.type_value("0")  # 0 Fahrenheit -> negative Celsius
    converted = converter.get_converted_value()
    assert converted.startswith("-"), f"Expected a negative Celsius value, got {converted!r}"
    assert float(converted) == pytest.approx(-17.7777777778, rel=1e-6), (
        f"Expected ~-17.7777777778 (0F in Celsius), got {converted!r}"
    )


def test_converter_backspace_removes_last_digit(converter):
    converter.clear_value()
    converter.type_value("123")
    converter.backspace()

    assert converter.get_source_value() == "12", (
        f"Expected '12' after backspace, got {converter.get_source_value()!r}"
    )


@pytest.mark.boundary
def test_converter_backspace_on_single_digit_empties_field(converter):
    # Boundary between "has content" and "empty", same as the keypad's.
    converter.clear_value()
    converter.type_value("7")
    converter.backspace()

    assert converter.get_source_value() == "", (
        f"Expected an empty source field after backspacing the only digit, got {converter.get_source_value()!r}"
    )
    assert converter.get_converted_value() == "", (
        f"Expected an empty converted field too, got {converter.get_converted_value()!r}"
    )


def test_converter_accepts_decimal_input(converter):
    # Confirmed on-device: 1.5 Acres = 6070.2846336 Square Meters.
    converter.clear_value()
    converter.type_value("1.5")

    assert converter.get_source_value() == "1.5", (
        f"Expected the source field to keep '1.5', got {converter.get_source_value()!r}"
    )
    converted = converter.get_converted_value()
    assert float(converted) == pytest.approx(6070.2846336), (
        f"Expected ~6070.2846336 (1.5 Acres in Square Meters), got {converted!r}"
    )


def test_converter_clear_empties_both_fields(converter):
    converter.clear_value()
    converter.type_value("42")
    converter.clear_value()

    assert converter.get_source_value() == "", "Expected the source field to be empty after clearing"
    assert converter.get_converted_value() == "", "Expected the converted field to be empty after clearing"
