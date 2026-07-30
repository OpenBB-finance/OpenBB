"""Tests for the Kansas City Fed regional models."""

import io
from datetime import date

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_federal_reserve.models.regional.kansas_city_div_lmci import (
    FederalReserveKansasCityDivisionalLmciData,
    FederalReserveKansasCityDivisionalLmciFetcher,
)
from openbb_federal_reserve.models.regional.kansas_city_fsi import (
    FederalReserveKansasCityFinancialStressData,
    FederalReserveKansasCityFinancialStressFetcher,
)
from openbb_federal_reserve.models.regional.kansas_city_natural_rate import (
    FederalReserveKansasCityNaturalRateData,
    FederalReserveKansasCityNaturalRateFetcher,
)
from openbb_federal_reserve.models.regional.kansas_city_prs import (
    FederalReserveKansasCityPolicyRateUncertaintyData,
    FederalReserveKansasCityPolicyRateUncertaintyFetcher,
)
from openbb_federal_reserve.models.regional.kansas_city_roro import (
    FederalReserveKansasCityRiskIndexData,
    FederalReserveKansasCityRiskIndexFetcher,
)

_FSI = b'"DATE","KCFSI"\n2026-04-01,-0.5\n2026-05-01,-0.88\n'
_RORO_DAILY = (
    b"t,z_spreads,z_equities,z_liquidity,z_goldcurrency,z_roro\n"
    b"22jun2026,.1,.2,.3,.4,.5\n"
    b"23jun2026,.0029,1.084,.00069,1.0755,.8118\n"
)
_RORO_WEEKLY = (
    b"t,z_spreads,z_equities,z_liquidity,z_goldcurrency,z_roro\n"
    b"14may2003,,,,,\n"
    b"10jun2026,-.1,-.2,-.3,-.4,-.5\n"
    b"17jun2026,-.337,-1.466,-.420,-1.046,-1.134\n"
)
_PRS = b"Year,Month,Day,KCPRU,KCPRS\n2026,6,22,1.1,0.0\n2026,6,23,1.178,-0.018\n"
_NATURAL_RATE = (
    b",KC Fed Model-Based Natural Rate,,,KC Fed Model-Based Natural Unemployment,,\n"
    b"Date,Point Estimate,Lower (68%),Upper (68%),Point Estimate,Lower (68%),Upper (68%)\n"
    b'"2026-03-01"," 1.10","-1.80","2.40","4.60","3.60","5.40"\n'
    b'"2026-04-01"," 1.134","-1.783","2.481","4.563","3.622","5.432"\n'
)


def _div_lmci_workbook() -> bytes:
    """Build a Divisional LMCI workbook with both sheets."""
    from datetime import datetime

    from openpyxl import Workbook

    header = [
        "Date",
        "United States",
        "New England",
        "Middle Atlantic",
        "East North Central",
        "West North Central",
        "South Atlantic",
        "East South Central",
        "West South Central",
        "Mountain",
        "Pacific",
    ]
    workbook = Workbook()
    activity = workbook.active
    activity.title = "Level of Activity"
    activity.append(header)
    activity.append([datetime(2026, 2, 1), *[round(0.1 * i, 2) for i in range(10)]])
    activity.append([datetime(2026, 3, 1), *[round(0.2 * i, 2) for i in range(10)]])
    momentum = workbook.create_sheet("Momentum")
    momentum.append(header)
    momentum.append([datetime(2026, 2, 1), *[round(-0.1 * i, 2) for i in range(10)]])
    momentum.append([datetime(2026, 3, 1), *[round(-0.2 * i, 2) for i in range(10)]])
    buffer = io.BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


class TestFinancialStress:
    """Tests for the KCFSI fetcher."""

    def test_parses_and_filters(self, monkeypatch):
        """The KCFSI CSV parses and dates filter."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.kansas_city.fetch_kansas_city",
            lambda *a, **k: _FSI,
        )
        query = FederalReserveKansasCityFinancialStressFetcher.transform_query(
            {"start_date": "2026-05-01", "end_date": "2026-05-31"}
        )
        rows = FederalReserveKansasCityFinancialStressFetcher.extract_data(query, None)
        result = FederalReserveKansasCityFinancialStressFetcher.transform_data(
            query, rows
        )
        assert all(
            isinstance(r, FederalReserveKansasCityFinancialStressData) for r in result
        )
        assert len(result) == 1
        assert result[0].date == date(2026, 5, 1)
        assert result[0].kcfsi == -0.88

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.kansas_city.fetch_kansas_city",
            lambda *a, **k: b"",
        )
        query = FederalReserveKansasCityFinancialStressFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveKansasCityFinancialStressFetcher.extract_data(query, None)


class TestRiskIndex:
    """Tests for the RORO fetcher."""

    def test_daily_parses_lowercase_dates(self, monkeypatch):
        """The daily CSV parses lowercase ``%d%b%Y`` dates and filters."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.kansas_city.fetch_kansas_city",
            lambda *a, **k: _RORO_DAILY,
        )
        query = FederalReserveKansasCityRiskIndexFetcher.transform_query(
            {
                "frequency": "daily",
                "start_date": "2026-06-23",
                "end_date": "2026-06-23",
            }
        )
        rows = FederalReserveKansasCityRiskIndexFetcher.extract_data(query, None)
        result = FederalReserveKansasCityRiskIndexFetcher.transform_data(query, rows)
        assert all(isinstance(r, FederalReserveKansasCityRiskIndexData) for r in result)
        assert len(result) == 1
        assert result[0].date == date(2026, 6, 23)
        assert result[0].roro == 0.8118
        assert result[0].gold_currency == 1.0755

    def test_weekly_drops_empty_first_row(self, monkeypatch):
        """The all-NaN first weekly row drops and dates filter."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.kansas_city.fetch_kansas_city",
            lambda *a, **k: _RORO_WEEKLY,
        )
        query = FederalReserveKansasCityRiskIndexFetcher.transform_query(
            {"frequency": "weekly"}
        )
        rows = FederalReserveKansasCityRiskIndexFetcher.extract_data(query, None)
        result = FederalReserveKansasCityRiskIndexFetcher.transform_data(query, rows)
        assert [r.date for r in result] == [date(2026, 6, 10), date(2026, 6, 17)]
        assert result[-1].roro == -1.134

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.kansas_city.fetch_kansas_city",
            lambda *a, **k: b"",
        )
        query = FederalReserveKansasCityRiskIndexFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveKansasCityRiskIndexFetcher.extract_data(query, None)


class TestPolicyRateUncertainty:
    """Tests for the KCPRU/KCPRS fetcher."""

    def test_builds_date_from_int_columns(self, monkeypatch):
        """The date builds from Year/Month/Day columns and dates filter."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.kansas_city.fetch_kansas_city",
            lambda *a, **k: _PRS,
        )
        query = FederalReserveKansasCityPolicyRateUncertaintyFetcher.transform_query(
            {"start_date": "2026-06-23", "end_date": "2026-06-30"}
        )
        rows = FederalReserveKansasCityPolicyRateUncertaintyFetcher.extract_data(
            query, None
        )
        result = FederalReserveKansasCityPolicyRateUncertaintyFetcher.transform_data(
            query, rows
        )
        assert all(
            isinstance(r, FederalReserveKansasCityPolicyRateUncertaintyData)
            for r in result
        )
        assert len(result) == 1
        assert result[0].date == date(2026, 6, 23)
        assert result[0].kcpru == 1.178
        assert result[0].kcprs == -0.018

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.kansas_city.fetch_kansas_city",
            lambda *a, **k: b"",
        )
        query = FederalReserveKansasCityPolicyRateUncertaintyFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveKansasCityPolicyRateUncertaintyFetcher.extract_data(
                query, None
            )


class TestNaturalRate:
    """Tests for the Model-Based r*/u* fetcher."""

    def test_skips_two_header_rows_and_filters(self, monkeypatch):
        """The two-header-row CSV parses past its offset and dates filter."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.kansas_city.fetch_kansas_city",
            lambda *a, **k: _NATURAL_RATE,
        )
        query = FederalReserveKansasCityNaturalRateFetcher.transform_query(
            {"start_date": "2026-04-01", "end_date": "2026-04-30"}
        )
        rows = FederalReserveKansasCityNaturalRateFetcher.extract_data(query, None)
        result = FederalReserveKansasCityNaturalRateFetcher.transform_data(query, rows)
        assert all(
            isinstance(r, FederalReserveKansasCityNaturalRateData) for r in result
        )
        assert len(result) == 1
        assert result[0].date == date(2026, 4, 1)
        assert result[0].rstar == 1.134
        assert result[0].ustar == 4.563
        assert result[0].ustar_upper == 5.432

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.kansas_city.fetch_kansas_city",
            lambda *a, **k: b"",
        )
        query = FederalReserveKansasCityNaturalRateFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveKansasCityNaturalRateFetcher.extract_data(query, None)


class TestDivisionalLmci:
    """Tests for the Divisional LMCI fetcher."""

    def test_pivots_to_wide_and_filters(self, monkeypatch):
        """The selected sheet pivots to one wide row per month and dates filter."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.kansas_city.fetch_kansas_city",
            lambda *a, **k: _div_lmci_workbook(),
        )
        query = FederalReserveKansasCityDivisionalLmciFetcher.transform_query(
            {
                "indicator": "level_of_activity",
                "start_date": "2026-03-01",
                "end_date": "2026-03-31",
            }
        )
        rows = FederalReserveKansasCityDivisionalLmciFetcher.extract_data(query, None)
        result = FederalReserveKansasCityDivisionalLmciFetcher.transform_data(
            query, rows
        )
        assert all(
            isinstance(r, FederalReserveKansasCityDivisionalLmciData) for r in result
        )
        assert len(result) == 1
        row = result[0].model_dump()
        assert row["date"] == date(2026, 3, 1)
        assert row["United States"] == 0.0
        assert row["Pacific"] == 1.8

    def test_momentum_sheet(self, monkeypatch):
        """The momentum indicator selects the Momentum sheet."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.kansas_city.fetch_kansas_city",
            lambda *a, **k: _div_lmci_workbook(),
        )
        query = FederalReserveKansasCityDivisionalLmciFetcher.transform_query(
            {"indicator": "momentum", "start_date": "2026-03-01"}
        )
        rows = FederalReserveKansasCityDivisionalLmciFetcher.extract_data(query, None)
        result = FederalReserveKansasCityDivisionalLmciFetcher.transform_data(
            query, rows
        )
        assert result[0].model_dump()["Pacific"] == -1.8

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.kansas_city.fetch_kansas_city",
            lambda *a, **k: b"",
        )
        query = FederalReserveKansasCityDivisionalLmciFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveKansasCityDivisionalLmciFetcher.extract_data(query, None)
