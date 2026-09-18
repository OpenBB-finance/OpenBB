"""Tests for the Montreal Exchange universe."""

from openbb_tmx.utils.mx import (
    INSTRUMENT_CLASSES,
    INTEREST_RATE_PRODUCTS,
    _parse_selectors,
)

PAGE = """
<select name="symbol" id="symbolOEQ">
  <option value="">Select</option>
  <option value="AC*">AC</option>
  <option value="BCE*">BCE</option>
</select>
<select name="symbol" id="symbolIRD">
  <option value="CGB*">CGB</option>
  <option value="LGB*">LGB</option>
</select>
<select name="symbol" id="symbolUNKNOWN">
  <option value="ZZ*">ZZ</option>
</select>
"""


class TestParseSelectors:
    """Reading the instrument selectors off the quotes page."""

    def test_parses_every_known_class(self):
        rows = _parse_selectors(PAGE)
        assert {r["symbol"] for r in rows} == {"AC", "BCE", "CGB", "LGB"}

    def test_unknown_selector_is_ignored(self):
        assert all(r["symbol"] != "ZZ" for r in _parse_selectors(PAGE))

    def test_blank_option_is_skipped(self):
        assert all(r["symbol"] for r in _parse_selectors(PAGE))

    def test_asset_class_is_labelled(self):
        rows = {r["symbol"]: r for r in _parse_selectors(PAGE)}
        assert rows["AC"]["asset_class"] == "equity_option"
        assert rows["CGB"]["asset_class"] == "interest_rate_derivative"

    def test_interest_rate_products_are_named(self):
        rows = {r["symbol"]: r for r in _parse_selectors(PAGE)}
        assert rows["CGB"]["name"] == INTEREST_RATE_PRODUCTS["CGB"]

    def test_quote_symbol_is_attached_for_futures(self):
        rows = {r["symbol"]: r for r in _parse_selectors(PAGE)}
        assert rows["CGB"]["quote_symbol"] == "/CGB"
        assert rows["AC"]["quote_symbol"] is None

    def test_empty_page(self):
        assert _parse_selectors("") == []

    def test_every_class_maps_to_a_label_and_type(self):
        assert all(len(v) == 3 for v in INSTRUMENT_CLASSES.values())

    def test_index_and_rate_selectors_classify_per_product(self):
        from openbb_tmx.utils.mx import _instrument_type

        assert _instrument_type("SXO", None) == "option"
        assert _instrument_type("OGB", None) == "option"
        assert _instrument_type("CGB", None) == "future"
        assert _instrument_type("SXF", None) == "future"
        assert _instrument_type("AC", "option") == "option"

    def test_unknown_product_has_no_name(self):
        rows = {r["symbol"]: r for r in _parse_selectors(PAGE)}
        assert rows["AC"]["name"] is None
        assert rows["CGB"]["name"] == INTEREST_RATE_PRODUCTS["CGB"]
