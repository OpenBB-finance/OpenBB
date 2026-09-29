"""Tests for the USAspending award search filters."""

import asyncio

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_government_us.treasury.models.usaspending_award_search import (
    UsSpendingAwardSearchFetcher,
)
from openbb_government_us.treasury.utils import award_filters, usaspending


def _capture(monkeypatch, results=None, autocomplete=None):
    """Patch the award POST, answering autocomplete probes separately."""
    captured: dict = {}

    async def _fake(path, payload, **kwargs):
        if "autocomplete" in path:
            return {"results": autocomplete or []}
        captured["payload"] = payload
        return {
            "results": results
            if results is not None
            else [{"generated_internal_id": "X"}]
        }

    monkeypatch.setattr(usaspending, "post_usaspending", _fake)
    return captured


class TestCodeLists:
    """Tests for the fixed contract code lists."""

    def test_every_list_is_populated(self):
        """Each code list carries codes and human labels."""
        for field, codes in award_filters.CODE_LISTS.items():
            assert codes, field
            assert all(isinstance(k, str) and v for k, v in codes.items()), field

    def test_extent_competed_matches_the_source_groups(self):
        """Extent competed carries the nine codes the source publishes."""
        assert set(award_filters.EXTENT_COMPETED) == {
            "A",
            "D",
            "F",
            "CDOCiv",
            "E Civ",
            "B",
            "C",
            "G",
            "NDOCiv",
        }

    def test_set_aside_uses_the_live_buy_indian_code(self):
        """'BI' is carried, not the retired 'BICiv' variant."""
        assert "BI" in award_filters.SET_ASIDE
        assert "BICiv" not in award_filters.SET_ASIDE

    def test_set_aside_carries_the_sole_source_variants(self):
        """The sole-source codes absent from the source's group list are kept."""
        assert "EDWOSBSS" in award_filters.SET_ASIDE
        assert "WOSBSS" in award_filters.SET_ASIDE

    def test_code_options_pair_labels_with_codes(self):
        """Widget options render the label with its code."""
        options = award_filters.code_options("contract_pricing")
        assert {"label": "Firm Fixed Price (J)", "value": "J"} in options


class TestSplitAndValidate:
    """Tests for code parsing and validation."""

    def test_split_codes(self):
        """A comma-separated list splits into stripped entries."""
        assert award_filters.split_codes(" A , B ,, C ") == ["A", "B", "C"]
        assert award_filters.split_codes(None) == []
        assert award_filters.split_codes("") == []

    def test_validate_accepts_known_codes(self):
        """Known codes pass through unchanged."""
        assert award_filters.validate_codes("extent_competed", "A,D") == ["A", "D"]

    def test_validate_rejects_an_unknown_code(self):
        """An unknown code raises rather than silently returning no rows."""
        with pytest.raises(OpenBBError, match="Invalid extent_competed code"):
            award_filters.validate_codes("extent_competed", "ZZZ")

    def test_validate_error_lists_the_valid_codes(self):
        """The error names the valid codes so the caller can correct it."""
        with pytest.raises(OpenBBError, match="Full and Open Competition"):
            award_filters.validate_codes("extent_competed", "ZZZ")

    def test_reference_validation_accepts_a_match(self, monkeypatch):
        """A code the source recognizes passes."""
        _capture(monkeypatch, autocomplete=[{"product_or_service_code": "R425"}])
        assert asyncio.run(award_filters.validate_reference_codes("psc", "R425")) == [
            "R425"
        ]

    def test_reference_validation_rejects_a_miss(self, monkeypatch):
        """A code the source does not recognize raises with suggestions."""
        _capture(monkeypatch, autocomplete=[{"product_or_service_code": "R425"}])
        with pytest.raises(OpenBBError, match="Did you mean one of: R425"):
            asyncio.run(award_filters.validate_reference_codes("psc", "ZZZZ"))

    def test_reference_validation_reports_no_matches(self, monkeypatch):
        """A code matching nothing says so plainly."""
        _capture(monkeypatch, autocomplete=[])
        with pytest.raises(OpenBBError, match="matched nothing"):
            asyncio.run(award_filters.validate_reference_codes("naics", "999999"))

    def test_reference_validation_skips_an_empty_value(self, monkeypatch):
        """No value makes no request."""
        assert asyncio.run(award_filters.validate_reference_codes("psc", None)) == []

    def test_def_code_options(self, monkeypatch):
        """DEFC options pair each code with its title."""

        async def _fake(path, **kwargs):
            return {
                "codes": [
                    {"code": "Z", "title": "Infrastructure"},
                    {"code": "Q", "public_law": "Non-emergency"},
                    {"code": None, "title": "dropped"},
                ]
            }

        monkeypatch.setattr(usaspending, "get_usaspending", _fake)
        options = asyncio.run(award_filters.def_code_options())
        assert options == [
            {"label": "Z - Infrastructure", "value": "Z"},
            {"label": "Q - Non-emergency", "value": "Q"},
        ]


class TestAwardSearchFilterMapping:
    """Tests that each param maps onto the right API filter."""

    def test_maps_the_contract_code_filters(self, monkeypatch):
        """The three contract filters map to their API keys."""
        captured = _capture(monkeypatch)
        query = UsSpendingAwardSearchFetcher.transform_query(
            {"contract_pricing": "J,M", "set_aside": "SBA", "extent_competed": "A"}
        )
        asyncio.run(UsSpendingAwardSearchFetcher.aextract_data(query, None))
        filters = captured["payload"]["filters"]
        assert filters["contract_pricing_type_codes"] == ["J", "M"]
        assert filters["set_aside_type_codes"] == ["SBA"]
        assert filters["extent_competed_type_codes"] == ["A"]

    def test_maps_award_number_description_and_defc(self, monkeypatch):
        """Award number, description, and DEFC map to their API keys."""
        captured = _capture(monkeypatch)
        query = UsSpendingAwardSearchFetcher.transform_query(
            {
                "award_number": "SPE30018FLGFZ,X1",
                "description": "helicopter",
                "defc": "Z,L",
            }
        )
        asyncio.run(UsSpendingAwardSearchFetcher.aextract_data(query, None))
        filters = captured["payload"]["filters"]
        assert filters["award_ids"] == ["SPE30018FLGFZ", "X1"]
        assert filters["description"] == "helicopter"
        assert filters["def_codes"] == ["Z", "L"]

    def test_maps_the_reference_validated_filters(self, monkeypatch):
        """NAICS, PSC, and assistance listing map to their API keys."""
        captured = _capture(
            monkeypatch,
            autocomplete=[
                {"naics": "541519"},
                {"product_or_service_code": "R425"},
                {"program_number": "10.331"},
            ],
        )
        query = UsSpendingAwardSearchFetcher.transform_query(
            {"naics": "541519", "psc": "R425", "assistance_listing": "10.331"}
        )
        asyncio.run(UsSpendingAwardSearchFetcher.aextract_data(query, None))
        filters = captured["payload"]["filters"]
        assert filters["naics_codes"] == ["541519"]
        assert filters["psc_codes"] == ["R425"]
        assert filters["program_numbers"] == ["10.331"]

    def test_omits_every_absent_filter(self, monkeypatch):
        """Unset filters are not sent at all."""
        captured = _capture(monkeypatch)
        query = UsSpendingAwardSearchFetcher.transform_query({})
        asyncio.run(UsSpendingAwardSearchFetcher.aextract_data(query, None))
        assert set(captured["payload"]["filters"]) == {
            "award_type_codes",
            "time_period",
        }

    def test_blank_filters_normalize_to_none(self):
        """Whitespace-only filter values are dropped."""
        query = UsSpendingAwardSearchFetcher.transform_query(
            {"award_number": "  ", "description": "", "naics": "  "}
        )
        assert query.award_number is None
        assert query.description is None
        assert query.naics is None

    def test_an_invalid_code_raises_before_the_request(self, monkeypatch):
        """A bad code fails loudly instead of returning an empty result."""
        captured = _capture(monkeypatch)
        query = UsSpendingAwardSearchFetcher.transform_query({"set_aside": "NOPE"})
        with pytest.raises(OpenBBError, match="Invalid set_aside code"):
            asyncio.run(UsSpendingAwardSearchFetcher.aextract_data(query, None))
        assert "payload" not in captured
