"""Tests for the USAspending award search model."""

import asyncio
from datetime import date, timedelta

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_government_us.treasury.models.usaspending_award_search import (
    AWARD_TYPE_CODES,
    UsSpendingAwardSearchData,
    UsSpendingAwardSearchFetcher,
    UsSpendingAwardSearchQueryParams,
)
from openbb_government_us.treasury.utils import usaspending


def _capture_post(monkeypatch, results):
    """Patch post_usaspending to record its path and payload, return canned rows."""
    captured: dict = {}

    async def _fake(path, payload, **kwargs):
        captured["path"] = path
        captured["payload"] = payload
        return {"results": results, "page_metadata": {"hasNext": False}}

    monkeypatch.setattr(usaspending, "post_usaspending", _fake)
    return captured


def _award_row(**overrides) -> dict:
    """Build a spending_by_award result row with overridable defaults."""
    row = {
        "internal_id": 307885715,
        "Award ID": "HT940216C0001",
        "Recipient Name": "HUMANA GOVERNMENT BUSINESS INC",
        "Recipient UEI": "ABC123",
        "Award Amount": 51269205263.03,
        "Total Outlays": 0.0,
        "Description": "IGF::OT::IGF",
        "Contract Award Type": "DEFINITIVE CONTRACT",
        "Awarding Agency": "Department of Defense",
        "Awarding Sub Agency": "Defense Health Agency",
        "Start Date": "2016-08-01",
        "End Date": "2025-12-31",
        "recipient_id": "1068e466-707d-6b6f-367f-0255fab79b8c-C",
        "generated_internal_id": "CONT_AWD_HT940216C0001_9700_-NONE-_-NONE-",
    }
    row.update(overrides)
    return row


class TestUsSpendingAwardSearchQueryParams:
    """Tests for the award-search query params."""

    def test_defaults(self):
        """The default query searches contracts with no text filters."""
        query = UsSpendingAwardSearchFetcher.transform_query({})
        assert query.award_group == "contracts"
        assert query.sort == "Award Amount"
        assert query.order == "desc"
        assert query.limit == 100
        assert query.keywords is None

    def test_optional_text_filters_strip_to_none(self):
        """Blank keyword, recipient, and agency filters normalize to None."""
        query = UsSpendingAwardSearchQueryParams(
            keywords="  ", recipient="", agency="  Department of Defense  "
        )
        assert query.keywords is None
        assert query.recipient is None
        assert query.agency == "Department of Defense"

    def test_explicit_none_text_filters_pass_through(self):
        """An explicitly unset text filter stays None rather than being stripped."""
        query = UsSpendingAwardSearchQueryParams(
            keywords=None, recipient=None, defc=None
        )
        assert query.keywords is None
        assert query.recipient is None
        assert query.defc is None

    def test_limit_is_capped(self):
        """A limit above the source cap of 100 is rejected."""
        with pytest.raises(ValueError, match="less than or equal to 100"):
            UsSpendingAwardSearchQueryParams(limit=500)

    def test_award_type_codes_cover_every_group(self):
        """Every award group maps to a non-empty list of type codes."""
        assert set(AWARD_TYPE_CODES) == {
            "contracts",
            "idvs",
            "grants",
            "direct_payments",
            "loans",
            "other_assistance",
        }
        assert all(codes for codes in AWARD_TYPE_CODES.values())


class TestUsSpendingAwardSearchFetcher:
    """Tests for the award-search fetcher."""

    def test_extract_builds_the_default_contract_payload(self, monkeypatch):
        """The default search sends contract codes and a trailing-365-day window."""
        captured = _capture_post(monkeypatch, [_award_row()])
        query = UsSpendingAwardSearchFetcher.transform_query({})
        asyncio.run(UsSpendingAwardSearchFetcher.aextract_data(query, None))
        assert captured["path"] == "search/spending_by_award/"
        payload = captured["payload"]
        assert payload["filters"]["award_type_codes"] == ["A", "B", "C", "D"]
        window = payload["filters"]["time_period"][0]
        assert window["start_date"] == str(date.today() - timedelta(days=365))
        assert "Contract Award Type" in payload["fields"]
        assert payload["sort"] == "Award Amount"
        assert payload["limit"] == 100
        assert "keywords" not in payload["filters"]

    def test_extract_applies_every_filter(self, monkeypatch):
        """Keyword, recipient, agency, and amount filters map into the payload."""
        captured = _capture_post(monkeypatch, [_award_row()])
        query = UsSpendingAwardSearchFetcher.transform_query(
            {
                "award_group": "grants",
                "keywords": "medicaid, health",
                "recipient": "California",
                "agency": "Department of Health and Human Services",
                "min_amount": 1000000,
                "max_amount": 5000000,
            }
        )
        asyncio.run(UsSpendingAwardSearchFetcher.aextract_data(query, None))
        filters = captured["payload"]["filters"]
        assert filters["award_type_codes"] == ["02", "03", "04", "05"]
        assert filters["keywords"] == ["medicaid", "health"]
        assert filters["recipient_search_text"] == ["California"]
        assert filters["agencies"] == [
            {
                "type": "awarding",
                "tier": "toptier",
                "name": "Department of Health and Human Services",
            }
        ]
        assert filters["award_amounts"] == [
            {"lower_bound": 1000000, "upper_bound": 5000000}
        ]
        assert "Award Type" in captured["payload"]["fields"]

    def test_extract_empty_raises(self, monkeypatch):
        """No matching awards raises EmptyDataError."""
        _capture_post(monkeypatch, [])
        query = UsSpendingAwardSearchFetcher.transform_query({})
        with pytest.raises(EmptyDataError, match="No awards matched"):
            asyncio.run(UsSpendingAwardSearchFetcher.aextract_data(query, None))

    def test_transform_maps_fields_and_parses_dates(self):
        """Source fields map to the unified schema with dates parsed."""
        query = UsSpendingAwardSearchFetcher.transform_query({})
        data = UsSpendingAwardSearchFetcher.transform_data(query, [_award_row()])
        assert len(data) == 1
        row = data[0]
        assert row.award_id == "CONT_AWD_HT940216C0001_9700_-NONE-_-NONE-"
        assert row.award_number == "HT940216C0001"
        assert row.recipient_name == "HUMANA GOVERNMENT BUSINESS INC"
        assert row.award_type == "DEFINITIVE CONTRACT"
        assert row.award_amount == 51269205263.03
        assert row.start_date == date(2016, 8, 1)
        assert row.end_date == date(2025, 12, 31)
        assert row.internal_id == 307885715

    def test_transform_maps_assistance_award_type(self):
        """An assistance row's 'Award Type' maps to the unified award_type."""
        query = UsSpendingAwardSearchFetcher.transform_query({"award_group": "grants"})
        row = _award_row()
        del row["Contract Award Type"]
        row["Award Type"] = "BLOCK GRANT (A)"
        data = UsSpendingAwardSearchFetcher.transform_data(query, [row])
        assert data[0].award_type == "BLOCK GRANT (A)"

    def test_transform_drops_rows_without_an_award_id(self):
        """A row missing the generated award id is dropped."""
        query = UsSpendingAwardSearchFetcher.transform_query({})
        row = _award_row()
        del row["generated_internal_id"]
        assert UsSpendingAwardSearchFetcher.transform_data(query, [row]) == []

    def test_award_id_column_drives_the_drilldown(self):
        """The award_id column emits into the shared award_id group on click."""
        cfg = UsSpendingAwardSearchData.model_fields["award_id"].json_schema_extra[
            "x-widget_config"
        ]
        assert cfg["renderFn"] == "cellOnClick"
        assert cfg["renderFnParams"]["groupByParamName"] == "award_id"
