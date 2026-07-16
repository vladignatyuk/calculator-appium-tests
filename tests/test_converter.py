# -*- coding: utf-8 -*-
"""Coverage for the unit converter (ruler icon)."""

import pytest

from pages.converter_page import ConverterPage


def test_converter_default_area_units(calculator):
    # Confirmed on-device: default tab is Area, default units Acres / Square Meters.
    calculator.open_converter()
    converter = ConverterPage(calculator.driver).wait_loaded()

    assert converter.active_tab_title().lower() == "area", (
        f"Expected default tab 'Area', got {converter.active_tab_title()!r}"
    )
    assert "acre" in converter.unit_1().lower(), f"Expected 'Acres', got {converter.unit_1()!r}"
    assert "square meter" in converter.unit_2().lower(), (
        f"Expected 'Square Meters', got {converter.unit_2()!r}"
    )

    converter.go_back()


def test_converter_produces_output_value(calculator):
    # Confirmed on-device: default Area conversion is Acres -> Square Meters,
    # 1 Acre = 4046.8564224 Square Meters.
    calculator.open_converter()
    converter = ConverterPage(calculator.driver).wait_loaded()

    converter.clear_value()
    converter.type_value("1")

    converted = converter.get_converted_value()
    assert converted, "Expected a converted value to appear in the second field"
    assert float(converted) == pytest.approx(4046.8564224), (
        f"Expected ~4046.8564224 (1 Acre in Square Meters), got {converted!r}"
    )

    converter.go_back()
