"""Unit tests for the Federal Reserve Primary Dealer Fails model."""

# ruff: noqa: I001

from datetime import date as dateType
from unittest.mock import AsyncMock

import pytest

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_federal_reserve.models.primary_dealer_fails import (
    FederalReservePrimaryDealerFailsData,
    FederalReservePrimaryDealerFailsFetcher,
    FederalReservePrimaryDealerFailsQueryParams,
)

ALL_KEYIDS = [
    "PDFTD-CS",
    "PDFTR-CS",
    "PDFTD-FGEM",
    "PDFTR-FGEM",
    "PDFTD-FGM",
    "PDFTR-FGM",
    "PDFTD-OM",
    "PDFTR-OM",
    "PDFTD-UST",
    "PDFTR-UST",
    "PDFTD-USTET",
    "PDFTR-USTET",
]

EARLY_KEYIDS = [
    "PDFASUFDA",
    "PDFASUFRA",
    "PDFASFAFDA",
    "PDFASFAFRA",
    "PDFASMBFDA",
    "PDFASMBFRA",
]


def _rows(keyids, dates_values) -> list[dict]:
    """Return raw timeseries rows for the given keyids and (date, value) pairs."""
    out: list[dict] = []
    for keyid in keyids:
        for asofdate, value in dates_values:
            out.append({"asofdate": asofdate, "keyid": keyid, "value": value})
    return out


def _modern_rows() -> list[dict]:
    """Return a two-period modern dataset covering all current keyids."""
    return _rows(ALL_KEYIDS, [("2024-01-03", "100"), ("2024-01-10", "200")])


class TestQueryParams:
    """Tests for ``FederalReservePrimaryDealerFailsQueryParams``."""

    def test_defaults(self):
        """Default asset class is ``all`` and unit is ``value``."""
        q = FederalReservePrimaryDealerFailsQueryParams()
        assert q.asset_class == "all"
        assert q.unit == "value"

    def test_transform_query(self):
        """``transform_query`` builds the params model from a dict."""
        q = FederalReservePrimaryDealerFailsFetcher.transform_query(
            {"asset_class": "mbs", "unit": "percent"}
        )
        assert isinstance(q, FederalReservePrimaryDealerFailsQueryParams)
        assert q.asset_class == "mbs"
        assert q.unit == "percent"


class TestExtractData:
    """Tests for ``FederalReservePrimaryDealerFailsFetcher.aextract_data``."""

    @pytest.mark.asyncio
    async def test_single_url_when_no_early_start(self, monkeypatch):
        """A recent ``start_date`` issues exactly one request to the modern series."""
        from openbb_core.provider.utils import helpers

        mock = AsyncMock(return_value={"pd": {"timeseries": _modern_rows()}})
        monkeypatch.setattr(helpers, "amake_request", mock)
        q = FederalReservePrimaryDealerFailsQueryParams(start_date=dateType(2024, 1, 1))
        data = await FederalReservePrimaryDealerFailsFetcher.aextract_data(q, None)
        assert mock.await_count == 1
        assert len(data) == len(_modern_rows())

    @pytest.mark.asyncio
    async def test_aggregates_two_extra_urls_before_2001(self, monkeypatch):
        """A pre-2001 start triggers the modern plus both historical series fetches."""
        from openbb_core.provider.utils import helpers

        modern = {"pd": {"timeseries": _modern_rows()}}
        sbp2001 = {"pd": {"timeseries": _rows(EARLY_KEYIDS, [("2000-01-05", "5")])}}
        sbp2013 = {"pd": {"timeseries": _rows(EARLY_KEYIDS, [("2002-01-05", "7")])}}
        mock = AsyncMock(side_effect=[modern, sbp2001, sbp2013])
        monkeypatch.setattr(helpers, "amake_request", mock)
        q = FederalReservePrimaryDealerFailsQueryParams(start_date=dateType(2000, 1, 1))
        data = await FederalReservePrimaryDealerFailsFetcher.aextract_data(q, None)
        assert mock.await_count == 3
        urls = [c.args[0] for c in mock.await_args_list]
        assert "SBP2001" in urls[1]
        assert "SBP2013" in urls[2]
        assert len(data) == len(_modern_rows()) + len(
            sbp2001["pd"]["timeseries"]
        ) + len(sbp2013["pd"]["timeseries"])

    @pytest.mark.asyncio
    async def test_aggregates_one_extra_url_between_2001_and_2013(self, monkeypatch):
        """A start between 2001-07 and 2013-04 fetches only the SBP2013 series."""
        from openbb_core.provider.utils import helpers

        modern = {"pd": {"timeseries": _modern_rows()}}
        sbp2013 = {"pd": {"timeseries": _rows(EARLY_KEYIDS, [("2010-01-05", "9")])}}
        mock = AsyncMock(side_effect=[modern, sbp2013])
        monkeypatch.setattr(helpers, "amake_request", mock)
        q = FederalReservePrimaryDealerFailsQueryParams(start_date=dateType(2010, 1, 1))
        data = await FederalReservePrimaryDealerFailsFetcher.aextract_data(q, None)
        assert mock.await_count == 2
        assert "SBP2013" in mock.await_args_list[1].args[0]
        assert len(data) == len(_modern_rows()) + len(sbp2013["pd"]["timeseries"])

    @pytest.mark.asyncio
    async def test_request_failure_wraps_to_openbb_error(self, monkeypatch):
        """A request exception is wrapped in ``OpenBBError``."""
        from openbb_core.provider.utils import helpers

        mock = AsyncMock(side_effect=RuntimeError("boom"))
        monkeypatch.setattr(helpers, "amake_request", mock)
        q = FederalReservePrimaryDealerFailsQueryParams()
        with pytest.raises(OpenBBError, match="Failed to fetch data"):
            await FederalReservePrimaryDealerFailsFetcher.aextract_data(q, None)


class TestTransformData:
    """Tests for ``FederalReservePrimaryDealerFailsFetcher.transform_data``."""

    def test_empty_raises(self):
        """Empty input raises ``EmptyDataError``."""
        q = FederalReservePrimaryDealerFailsQueryParams()
        with pytest.raises(EmptyDataError, match="No data returned"):
            FederalReservePrimaryDealerFailsFetcher.transform_data(q, [])

    def test_all_value_includes_totals(self):
        """``all`` / ``value`` returns every series plus synthesised FTD/FTR totals."""
        q = FederalReservePrimaryDealerFailsQueryParams(asset_class="all", unit="value")
        out = FederalReservePrimaryDealerFailsFetcher.transform_data(q, _modern_rows())
        cols = set(out[0].model_dump())
        assert "FTD Total" in cols
        assert "FTR Total" in cols
        assert all(isinstance(r, FederalReservePrimaryDealerFailsData) for r in out)
        assert isinstance(out[0].model_dump()["FTD Total"], int)

    def test_percent_normalizes_within_total(self):
        """``unit=percent`` divides each value by its FTD/FTR total per date."""
        q = FederalReservePrimaryDealerFailsQueryParams(
            asset_class="treasuries", unit="percent"
        )
        out = FederalReservePrimaryDealerFailsFetcher.transform_data(q, _modern_rows())
        assert set(out[0].model_dump()) - {"date"} == {
            "FTD Treasury Securities (Ex-TIPS)",
            "FTR Treasury Securities (Ex-TIPS)",
        }
        assert out[0].model_dump()[
            "FTD Treasury Securities (Ex-TIPS)"
        ] == pytest.approx(1.0 / 6.0)

    def test_asset_class_agency(self):
        """``agency`` keeps only the Ex-MBS agency columns."""
        q = FederalReservePrimaryDealerFailsQueryParams(asset_class="agency")
        out = FederalReservePrimaryDealerFailsFetcher.transform_data(q, _modern_rows())
        assert set(out[0].model_dump()) - {"date"} == {
            "FTD Agency and GSE Securities (Ex-MBS)",
            "FTR Agency and GSE Securities (Ex-MBS)",
        }

    def test_asset_class_mbs(self):
        """``mbs`` keeps the MBS columns but excludes the Ex-MBS agency ones."""
        q = FederalReservePrimaryDealerFailsQueryParams(asset_class="mbs")
        out = FederalReservePrimaryDealerFailsFetcher.transform_data(q, _modern_rows())
        assert set(out[0].model_dump()) - {"date"} == {
            "FTD Agency and GSE MBS",
            "FTR Agency and GSE MBS",
            "FTD Other MBS",
            "FTR Other MBS",
        }

    def test_asset_class_tips(self):
        """``tips`` keeps the TIPS columns but excludes Ex-TIPS treasuries."""
        q = FederalReservePrimaryDealerFailsQueryParams(asset_class="tips")
        out = FederalReservePrimaryDealerFailsFetcher.transform_data(q, _modern_rows())
        assert set(out[0].model_dump()) - {"date"} == {"FTD TIPS", "FTR TIPS"}

    def test_asset_class_corporate(self):
        """``corporate`` keeps only the corporate securities columns."""
        q = FederalReservePrimaryDealerFailsQueryParams(asset_class="corporate")
        out = FederalReservePrimaryDealerFailsFetcher.transform_data(q, _modern_rows())
        assert set(out[0].model_dump()) - {"date"} == {
            "FTD Corporate Securities",
            "FTR Corporate Securities",
        }

    def test_missing_value_becomes_none(self):
        """A date present for only some keyids yields ``None`` for the gaps."""
        rows = _rows(ALL_KEYIDS, [("2024-01-03", "100")])
        rows.append({"asofdate": "2024-01-10", "keyid": "PDFTD-USTET", "value": "200"})
        q = FederalReservePrimaryDealerFailsQueryParams(
            asset_class="treasuries", unit="value"
        )
        out = FederalReservePrimaryDealerFailsFetcher.transform_data(q, rows)
        gap = next(r for r in out if r.date == dateType(2024, 1, 10))
        dumped = gap.model_dump()
        assert dumped["FTR Treasury Securities (Ex-TIPS)"] is None
        assert dumped["FTD Treasury Securities (Ex-TIPS)"] == 200

    def test_start_and_end_date_filter(self):
        """``start_date`` and ``end_date`` bound the returned rows inclusively."""
        rows = _rows(
            ALL_KEYIDS,
            [("2024-01-03", "100"), ("2024-01-10", "200"), ("2024-01-17", "300")],
        )
        q = FederalReservePrimaryDealerFailsQueryParams(
            asset_class="corporate",
            start_date=dateType(2024, 1, 10),
            end_date=dateType(2024, 1, 10),
        )
        out = FederalReservePrimaryDealerFailsFetcher.transform_data(q, rows)
        assert {r.date for r in out} == {dateType(2024, 1, 10)}
