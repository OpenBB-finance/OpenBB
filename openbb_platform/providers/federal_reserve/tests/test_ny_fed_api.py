"""Unit tests for the NY Federal Reserve API utilities."""

# ruff: noqa: I001

from unittest.mock import AsyncMock

import pytest

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_federal_reserve.utils import ny_fed_api
from openbb_federal_reserve.utils.ny_fed_api import (
    SomaHoldings,
    _get_endpoints,
    fetch_data,
    get_nearest_date,
)


class TestGetEndpoints:
    """Tests for ``_get_endpoints``."""

    def test_returns_full_mapping_when_category_none(self):
        """No category returns the complete endpoint mapping."""
        endpoints = _get_endpoints()
        assert "soma_holdings" in endpoints
        assert "primary_dealer_statistics" in endpoints

    def test_returns_single_category(self):
        """A category key returns only that category's endpoints."""
        soma = _get_endpoints(category="soma_holdings")
        assert soma["summary"].endswith("/soma/summary.json")

    def test_ambs_security_is_translated(self):
        """A non-empty ``ambs_security`` is mapped through ``AMBS_SECURITIES``."""
        endpoints = _get_endpoints(ambs_security="tba")
        assert "securities=TBA" in endpoints["agency_mbs_operations"]["search"]

    def test_is_previous_selects_previous_guide_sheet(self):
        """``is_previous=True`` resolves the guide sheet to the ``previous`` release."""
        endpoints = _get_endpoints(is_previous=True)
        assert endpoints["guide_sheets"].endswith("/previous.json")

    def test_default_guide_sheet_is_latest(self):
        """Without ``is_previous`` the guide sheet resolves to ``latest``."""
        endpoints = _get_endpoints()
        assert endpoints["guide_sheets"].endswith("/latest.json")


class TestFetchData:
    """Tests for ``fetch_data``."""

    @pytest.mark.asyncio
    async def test_returns_response(self, monkeypatch):
        """A successful request returns the JSON payload."""
        monkeypatch.setattr(
            ny_fed_api, "amake_request", AsyncMock(return_value={"ok": True})
        )
        assert await fetch_data("https://example.com") == {"ok": True}

    @pytest.mark.asyncio
    async def test_reraises_on_error(self, monkeypatch):
        """A request exception is re-raised unchanged."""
        monkeypatch.setattr(
            ny_fed_api, "amake_request", AsyncMock(side_effect=ValueError("boom"))
        )
        with pytest.raises(ValueError, match="boom"):
            await fetch_data("https://example.com")


class TestGetNearestDate:
    """Tests for ``get_nearest_date``."""

    def test_picks_closest_date(self):
        """The closest date to the target is returned in ISO format."""
        dates = ["2022-01-05", "2022-02-22", "2022-03-15"]
        assert get_nearest_date(dates, "2022-02-20") == "2022-02-22"

    def test_picks_later_date_when_closer(self):
        """A target closer to a later date returns that later date."""
        dates = ["2022-01-05", "2022-02-22", "2022-03-15"]
        assert get_nearest_date(dates, "2022-03-10") == "2022-03-15"


class TestSomaHoldings:
    """Tests for the ``SomaHoldings`` SOMA endpoint wrapper."""

    def test_repr_returns_docstring(self):
        """``__repr__`` returns the class docstring."""
        assert SomaHoldings().__repr__() == str(SomaHoldings.__doc__)

    def _patch_fetch(self, monkeypatch, mapping):
        """Patch ``fetch_data`` to dispatch by substring match on the URL."""

        async def _fake(url, *args, **kwargs):
            for needle, payload in mapping.items():
                if needle in url:
                    return payload
            raise AssertionError(f"unexpected url: {url}")

        monkeypatch.setattr(ny_fed_api, "fetch_data", _fake)

    @pytest.mark.asyncio
    async def test_get_as_of_dates(self, monkeypatch):
        """``get_as_of_dates`` returns the list of as-of dates."""
        self._patch_fetch(
            monkeypatch,
            {"/soma/asofdates/list.json": {"soma": {"asOfDates": ["2024-01-03"]}}},
        )
        assert await SomaHoldings().get_as_of_dates() == ["2024-01-03"]

    @pytest.mark.asyncio
    async def test_get_as_of_dates_empty_raises(self, monkeypatch):
        """An empty as-of date list raises ``OpenBBError``."""
        self._patch_fetch(
            monkeypatch, {"/soma/asofdates/list.json": {"soma": {"asOfDates": []}}}
        )
        with pytest.raises(OpenBBError, match="Error requesting dates"):
            await SomaHoldings().get_as_of_dates()

    @pytest.mark.asyncio
    async def test_get_release_log_agency(self, monkeypatch):
        """``get_release_log`` returns the agency release log by default."""
        self._patch_fetch(
            monkeypatch,
            {"/soma/agency/get/release_log.json": {"soma": {"dates": [{"d": 1}]}}},
        )
        assert await SomaHoldings().get_release_log() == [{"d": 1}]

    @pytest.mark.asyncio
    async def test_get_release_log_treasury(self, monkeypatch):
        """``get_release_log(treasury=True)`` uses the Treasury release endpoint."""
        self._patch_fetch(
            monkeypatch,
            {"/soma/tsy/get/release_log.json": {"soma": {"dates": [{"d": 2}]}}},
        )
        assert await SomaHoldings().get_release_log(treasury=True) == [{"d": 2}]

    @pytest.mark.asyncio
    async def test_get_release_log_empty_raises(self, monkeypatch):
        """An empty release log raises ``OpenBBError``."""
        self._patch_fetch(
            monkeypatch,
            {"/soma/agency/get/release_log.json": {"soma": {"dates": []}}},
        )
        with pytest.raises(OpenBBError, match="No data found"):
            await SomaHoldings().get_release_log()

    @pytest.mark.asyncio
    async def test_get_summary(self, monkeypatch):
        """``get_summary`` returns the weekly summary list."""
        self._patch_fetch(
            monkeypatch, {"/soma/summary.json": {"soma": {"summary": [{"s": 1}]}}}
        )
        assert await SomaHoldings().get_summary() == [{"s": 1}]

    @pytest.mark.asyncio
    async def test_get_summary_empty_raises(self, monkeypatch):
        """An empty summary raises ``EmptyDataError``."""
        self._patch_fetch(
            monkeypatch, {"/soma/summary.json": {"soma": {"summary": []}}}
        )
        with pytest.raises(EmptyDataError, match="returned empty"):
            await SomaHoldings().get_summary()

    @pytest.mark.asyncio
    async def test_get_agency_holdings_latest(self, monkeypatch):
        """With no arguments, agency holdings default to the latest as-of date."""
        self._patch_fetch(
            monkeypatch,
            {
                "/soma/asofdates/list.json": {"soma": {"asOfDates": ["2024-01-03"]}},
                "/soma/agency/get/asof/": {"soma": {"holdings": [{"h": 1}]}},
            },
        )
        assert await SomaHoldings().get_agency_holdings() == [{"h": 1}]

    @pytest.mark.asyncio
    async def test_get_agency_holdings_as_of_uses_nearest(self, monkeypatch):
        """A given ``as_of`` snaps to the nearest valid as-of date."""
        captured: list[str] = []

        async def _fake(url, *args, **kwargs):
            captured.append(url)
            if "/soma/asofdates/list.json" in url:
                return {"soma": {"asOfDates": ["2024-01-03", "2024-01-10"]}}
            return {"soma": {"holdings": [{"h": 2}]}}

        monkeypatch.setattr(ny_fed_api, "fetch_data", _fake)
        out = await SomaHoldings().get_agency_holdings(as_of="2024-01-09")
        assert out == [{"h": 2}]
        assert any("2024-01-10" in u for u in captured)

    @pytest.mark.asyncio
    async def test_get_agency_holdings_wam(self, monkeypatch):
        """``wam=True`` returns a single-element list from the agency debts endpoint."""
        self._patch_fetch(
            monkeypatch,
            {
                "/soma/asofdates/list.json": {"soma": {"asOfDates": ["2024-01-03"]}},
                "/soma/agency/wam/": {"soma": {"wam": 5.0}},
            },
        )
        out = await SomaHoldings().get_agency_holdings(wam=True)
        assert out == [{"wam": 5.0}]

    @pytest.mark.asyncio
    async def test_get_agency_holdings_holding_type(self, monkeypatch):
        """A valid ``holding_type`` targets the holding-type endpoint."""
        captured: list[str] = []

        async def _fake(url, *args, **kwargs):
            captured.append(url)
            if "/soma/asofdates/list.json" in url:
                return {"soma": {"asOfDates": ["2024-01-03"]}}
            return {"soma": {"holdings": [{"h": 3}]}}

        monkeypatch.setattr(ny_fed_api, "fetch_data", _fake)
        out = await SomaHoldings().get_agency_holdings(holding_type="mbs")
        assert out == [{"h": 3}]
        assert any("/mbs/asof/" in u for u in captured)

    @pytest.mark.asyncio
    async def test_get_agency_holdings_invalid_holding_type(self, monkeypatch):
        """An unknown agency ``holding_type`` raises ``OpenBBError``."""
        self._patch_fetch(
            monkeypatch,
            {"/soma/asofdates/list.json": {"soma": {"asOfDates": ["2024-01-03"]}}},
        )
        with pytest.raises(OpenBBError, match="Invalid choice"):
            await SomaHoldings().get_agency_holdings(holding_type="bogus")

    @pytest.mark.asyncio
    async def test_get_agency_holdings_cusip(self, monkeypatch):
        """A ``cusip`` targets the cusip endpoint."""
        captured: list[str] = []

        async def _fake(url, *args, **kwargs):
            captured.append(url)
            if "/soma/asofdates/list.json" in url:
                return {"soma": {"asOfDates": ["2024-01-03"]}}
            return {"soma": {"holdings": [{"h": 4}]}}

        monkeypatch.setattr(ny_fed_api, "fetch_data", _fake)
        out = await SomaHoldings().get_agency_holdings(cusip="3138LMCK7")
        assert out == [{"h": 4}]
        assert any("/get/cusip/3138LMCK7.json" in u for u in captured)

    @pytest.mark.asyncio
    async def test_get_agency_holdings_empty_raises(self, monkeypatch):
        """Empty agency holdings raise ``EmptyDataError``."""
        self._patch_fetch(
            monkeypatch,
            {
                "/soma/asofdates/list.json": {"soma": {"asOfDates": ["2024-01-03"]}},
                "/soma/agency/get/asof/": {"soma": {"holdings": []}},
            },
        )
        with pytest.raises(EmptyDataError):
            await SomaHoldings().get_agency_holdings()

    @pytest.mark.asyncio
    async def test_get_treasury_holdings_as_of_uses_nearest(self, monkeypatch):
        """A given ``as_of`` snaps to the nearest valid as-of date in the URL."""
        captured: list[str] = []

        async def _fake(url, *args, **kwargs):
            captured.append(url)
            if "/soma/asofdates/list.json" in url:
                return {"soma": {"asOfDates": ["2024-01-03", "2024-01-10"]}}
            return {"soma": {"holdings": [{"t": 2}]}}

        monkeypatch.setattr(ny_fed_api, "fetch_data", _fake)
        out = await SomaHoldings().get_treasury_holdings(
            as_of="2024-01-04", holding_type="bills"
        )
        assert out == [{"t": 2}]
        assert any("2024-01-03" in u for u in captured)

    @pytest.mark.asyncio
    async def test_get_treasury_holdings_wam(self, monkeypatch):
        """``wam=True`` returns a single-element list from the treasury debts endpoint."""
        self._patch_fetch(
            monkeypatch,
            {
                "/soma/asofdates/list.json": {"soma": {"asOfDates": ["2024-01-03"]}},
                "/soma/tsy/wam/": {"soma": {"wam": 9.0}},
            },
        )
        out = await SomaHoldings().get_treasury_holdings(wam=True)
        assert out == [{"wam": 9.0}]

    @pytest.mark.asyncio
    async def test_get_treasury_holdings_holding_type(self, monkeypatch):
        """A valid treasury ``holding_type`` targets the holding-type endpoint."""
        captured: list[str] = []

        async def _fake(url, *args, **kwargs):
            captured.append(url)
            if "/soma/asofdates/list.json" in url:
                return {"soma": {"asOfDates": ["2024-01-03"]}}
            return {"soma": {"holdings": [{"t": 3}]}}

        monkeypatch.setattr(ny_fed_api, "fetch_data", _fake)
        out = await SomaHoldings().get_treasury_holdings(holding_type="tips")
        assert out == [{"t": 3}]
        assert any("/tips/asof/" in u for u in captured)

    @pytest.mark.asyncio
    async def test_get_treasury_holdings_invalid_holding_type(self, monkeypatch):
        """An unknown treasury ``holding_type`` raises ``OpenBBError``."""
        self._patch_fetch(
            monkeypatch,
            {"/soma/asofdates/list.json": {"soma": {"asOfDates": ["2024-01-03"]}}},
        )
        with pytest.raises(OpenBBError, match="Invalid choice"):
            await SomaHoldings().get_treasury_holdings(holding_type="bogus")

    @pytest.mark.asyncio
    async def test_get_treasury_holdings_monthly(self, monkeypatch):
        """``monthly=True`` targets the monthly endpoint."""
        captured: list[str] = []

        async def _fake(url, *args, **kwargs):
            captured.append(url)
            if "/soma/asofdates/list.json" in url:
                return {"soma": {"asOfDates": ["2024-01-03"]}}
            return {"soma": {"holdings": [{"t": 4}]}}

        monkeypatch.setattr(ny_fed_api, "fetch_data", _fake)
        out = await SomaHoldings().get_treasury_holdings(monthly=True)
        assert out == [{"t": 4}]
        assert any("/soma/tsy/get/monthly.json" in u for u in captured)

    @pytest.mark.asyncio
    async def test_get_treasury_holdings_cusip(self, monkeypatch):
        """A ``cusip`` targets the treasury cusip endpoint."""
        captured: list[str] = []

        async def _fake(url, *args, **kwargs):
            captured.append(url)
            if "/soma/asofdates/list.json" in url:
                return {"soma": {"asOfDates": ["2024-01-03"]}}
            return {"soma": {"holdings": [{"t": 5}]}}

        monkeypatch.setattr(ny_fed_api, "fetch_data", _fake)
        out = await SomaHoldings().get_treasury_holdings(cusip="912810FH6")
        assert out == [{"t": 5}]
        assert any("/soma/tsy/get/cusip/912810FH6.json" in u for u in captured)

    @pytest.mark.asyncio
    async def test_get_treasury_holdings_empty_raises(self, monkeypatch):
        """Empty treasury holdings raise ``EmptyDataError``."""
        self._patch_fetch(
            monkeypatch,
            {
                "/soma/asofdates/list.json": {"soma": {"asOfDates": ["2024-01-03"]}},
                "/tips/asof/": {"soma": {"holdings": []}},
            },
        )
        with pytest.raises(EmptyDataError):
            await SomaHoldings().get_treasury_holdings(holding_type="tips")
