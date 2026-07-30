"""Tests for the Chicago Fed regional models."""

from datetime import date
from io import BytesIO
from unittest.mock import MagicMock

import pytest
from openbb_core.provider.utils.errors import EmptyDataError
from pandas import DataFrame

from openbb_federal_reserve.models.regional.chicago_ag_credit import (
    FederalReserveChicagoAgCreditData,
    FederalReserveChicagoAgCreditFetcher,
)
from openbb_federal_reserve.models.regional.chicago_bbki import (
    FederalReserveChicagoBraveButtersKelleyData,
    FederalReserveChicagoBraveButtersKelleyFetcher,
)
from openbb_federal_reserve.models.regional.chicago_carts import (
    FederalReserveChicagoRetailTradeData,
    FederalReserveChicagoRetailTradeFetcher,
)
from openbb_federal_reserve.models.regional.chicago_cflmi import (
    FederalReserveChicagoLaborMarketData,
    FederalReserveChicagoLaborMarketFetcher,
)
from openbb_federal_reserve.models.regional.chicago_cfnai import (
    FederalReserveChicagoNationalActivityData,
    FederalReserveChicagoNationalActivityFetcher,
)
from openbb_federal_reserve.models.regional.chicago_cfsec import (
    FederalReserveChicagoEconomicConditionsData,
    FederalReserveChicagoEconomicConditionsFetcher,
)
from openbb_federal_reserve.models.regional.chicago_farm_loans import (
    FederalReserveChicagoFarmLoanRatesData,
    FederalReserveChicagoFarmLoanRatesFetcher,
)
from openbb_federal_reserve.models.regional.chicago_farmland import (
    FederalReserveChicagoFarmlandValuesData,
    FederalReserveChicagoFarmlandValuesFetcher,
)
from openbb_federal_reserve.models.regional.chicago_mei import (
    FederalReserveChicagoMidwestEconomyData,
    FederalReserveChicagoMidwestEconomyFetcher,
)
from openbb_federal_reserve.models.regional.chicago_nfci import (
    FederalReserveChicagoFinancialConditionsData,
    FederalReserveChicagoFinancialConditionsFetcher,
)

_CFNAI = (
    "Date,P_I,EU_H,C_H,SO_I,CFNAI,CFNAI_MA3,DIFFUSION\n"
    "2024/01,0.10,0.00,0.00,0.00,0.10,0.05,0.10\n"
    "2024/02,0.20,-0.10,0.00,0.00,0.10,0.10,0.20\n"
    "2024/03,0.05,0.05,0.00,0.00,0.10,,\n"
)
_NFCI = (
    "Friday_of_Week,NFCI,ANFCI,Risk,Credit,Leverage,Nonfinancial_Leverage\n"
    "01/03/2025,-0.50,-0.40,-0.60,0.00,0.10,-0.40\n"
    "01/10/2025,-0.55,-0.45,-0.62,-0.01,0.12,-0.41\n"
)
_CARTS_FIG1 = (
    "date,Mils. $,Mils. 2017$\n"
    "2026-05-21,616575.99,501029.22\n"
    "2026-05-28,617609.59,501588.53\n"
)
_CARTS_FIG2 = (
    "metric,pos,value,date\n"
    '"Sales SA, m/m",17.17,-0.2%,May-2026\n'
    '"Prices SA, m/m",85.71,+0.8%,May-2026\n'
)
_CARTS_FIG3 = (
    "date,Mils. $,CARTS Nowcast,Mils. 2017$,Inflation-adjusted Nowcast\n"
    "Apr-2026,0.70,NA,0.05,NA\n"
    "May-2026,NA,-0.24,NA,-1.07\n"
)
_CARTS_FIG4 = (
    '"CARTS Real Sales Nowcast Contributions, SA m/m % chg.",value,month\n'
    "Census,0.13,May\n"
    "Transactions,-0.22,May\n"
)
_CARTS_FIG5 = (
    "date,Census,VISA SMI (minus 100),CARTS Nowcast\n"
    "Apr-2026,6.34,0.10,NA\n"
    "May-2026,NA,1.00,6.09\n"
)
_CARTS_FIG6 = (
    "date,BEA,CPI,CARTS Nowcast\nApr-2026,NA,4.62,3.70\nMay-2026,NA,5.45,4.65\n"
)
_CARTS_FIGURES = {
    "fig1": _CARTS_FIG1,
    "fig2": _CARTS_FIG2,
    "fig3": _CARTS_FIG3,
    "fig4": _CARTS_FIG4,
    "fig5": _CARTS_FIG5,
    "fig6": _CARTS_FIG6,
}
_FARMLAND = (
    "YYYYQ,Year-over-year,blank,Illinois,Indiana,Iowa,Wisconsin\n"
    "2025/10,6,,3,9,7,9\n"
    "2026/01,3,,-2,8,2,7\n"
)
_AG_CREDIT = (
    "YYYYQ,Loan Demand Index,Fund Availability Index,Loan Repayment Index,"
    "Average Loan-to-deposit Ratio (percent)\n"
    "2025/10,135,83,69,79.6\n"
    "2026/01,141,90,63,79.8\n"
)
_FARM_LOANS = (
    "YYYYQ,Operating Loans,Feeder Cattle Loans,Farm Real Estate Loans\n"
    "Note: As of 1st day of period.,,,\n"
    "2026/01,7.11,7.25,6.63\n"
    "2026/04,7.08,7.12,6.74\n"
)
_BBKI = (
    "Date,CoincidentIndex,LeadingIndex,Cycle,CycleLeading,CycleLagging,"
    "Trend,Irregular,MGDP\n"
    "04/30/2022,-0.07,-1.43,-0.22,-2.85,2.62,2.29,1.10,1.20\n"
    "05/31/2022,-0.18,-1.47,-0.59,-2.92,2.32,2.29,,\n"
)
_MEI = (
    "Year/Month,MEI,ILIndex,INIndex,IAIndex,MIIndex,WIIndex,Regional,"
    "Manufacturing,Construction,Services,Consumer\n"
    "2021/04,0.63,0.25,-0.00,0.11,0.12,0.15,0.00,0.39,-0.02,0.17,0.09\n"
    "2021/05,0.69,0.30,-0.02,0.11,0.10,0.16,0.03,0.44,0.04,0.10,0.11\n"
)


def _response(text: str) -> MagicMock:
    """Build a make_request response with the given text body."""
    response = MagicMock()
    response.text = text
    response.status_code = 200
    response.raise_for_status = MagicMock()
    return response


def _csv_bytes_response(text: str) -> MagicMock:
    """Build a 200 make_request response carrying CSV text encoded as bytes."""
    response = MagicMock()
    response.content = text.encode("utf-8")
    response.status_code = 200
    response.raise_for_status = MagicMock()
    return response


def _xlsx_response(frame: DataFrame, sheet_name: str) -> MagicMock:
    """Build a 200 make_request response carrying a one-sheet XLSX workbook."""
    buffer = BytesIO()
    frame.to_excel(buffer, sheet_name=sheet_name, index=False)
    response = MagicMock()
    response.content = buffer.getvalue()
    response.status_code = 200
    response.raise_for_status = MagicMock()
    return response


def _patch_text(monkeypatch, text: str) -> None:
    """Patch make_request to return CSV text bytes for the Chicago helper."""
    monkeypatch.setattr(
        "openbb_core.provider.utils.helpers.make_request",
        lambda *a, **k: _csv_bytes_response(text),
    )


def _patch_xlsx(monkeypatch, frame: DataFrame, sheet_name: str) -> None:
    """Patch make_request to return an XLSX workbook for the Chicago helper."""
    monkeypatch.setattr(
        "openbb_core.provider.utils.helpers.make_request",
        lambda *a, **k: _xlsx_response(frame, sheet_name),
    )


def _patch_carts(monkeypatch) -> None:
    """Patch make_request to serve the CARTS figure matching the requested URL."""

    def _request(url, *a, **k):
        for figure, text in _CARTS_FIGURES.items():
            if figure in url:
                return _csv_bytes_response(text)
        return _csv_bytes_response("")

    monkeypatch.setattr("openbb_core.provider.utils.helpers.make_request", _request)


class TestNationalActivity:
    """Tests for the CFNAI fetcher."""

    def test_parses_and_filters(self, monkeypatch):
        """The CSV parses, columns map, dates filter, and NaN maps to None."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _response(_CFNAI),
        )
        query = FederalReserveChicagoNationalActivityFetcher.transform_query(
            {"start_date": "2024-02-01"}
        )
        rows = FederalReserveChicagoNationalActivityFetcher.extract_data(query, None)
        result = FederalReserveChicagoNationalActivityFetcher.transform_data(
            query, rows
        )
        assert all(
            isinstance(r, FederalReserveChicagoNationalActivityData) for r in result
        )
        assert result[0].date == date(2024, 2, 1)
        assert result[0].cfnai == 0.10
        assert result[0].production_income == 0.20
        assert result[-1].cfnai_ma3 is None

    def test_end_date_filter(self, monkeypatch):
        """The end_date filter trims later observations."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _response(_CFNAI),
        )
        query = FederalReserveChicagoNationalActivityFetcher.transform_query(
            {"end_date": "2024-01-31"}
        )
        rows = FederalReserveChicagoNationalActivityFetcher.extract_data(query, None)
        result = FederalReserveChicagoNationalActivityFetcher.transform_data(
            query, rows
        )
        assert [r.date for r in result] == [date(2024, 1, 1)]

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _response(""),
        )
        query = FederalReserveChicagoNationalActivityFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveChicagoNationalActivityFetcher.extract_data(query, None)


class TestFinancialConditions:
    """Tests for the NFCI fetcher."""

    def test_parses_subindices(self, monkeypatch):
        """The NFCI CSV parses with its subindices and adjusted series."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _response(_NFCI),
        )
        query = FederalReserveChicagoFinancialConditionsFetcher.transform_query(
            {"start_date": "2025-01-01", "end_date": "2025-12-31"}
        )
        rows = FederalReserveChicagoFinancialConditionsFetcher.extract_data(query, None)
        result = FederalReserveChicagoFinancialConditionsFetcher.transform_data(
            query, rows
        )
        assert all(
            isinstance(r, FederalReserveChicagoFinancialConditionsData) for r in result
        )
        assert result[0].date == date(2025, 1, 3)
        assert result[0].nfci == -0.50
        assert result[0].adjusted_nfci == -0.40
        assert result[0].nonfinancial_leverage == -0.40

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _response(""),
        )
        query = FederalReserveChicagoFinancialConditionsFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveChicagoFinancialConditionsFetcher.extract_data(query, None)


class TestEconomicConditions:
    """Tests for the CFSEC survey fetcher."""

    _FRAME = DataFrame(
        {
            "Date": ["2026-05", "2026-06"],
            "Activity": [11.43, 17.52],
            "ActivityMfg": [43.42, 65.31],
            "ActivityNmfg": [-6.72, -9.09],
            "Outlook": [-2.26, 18.39],
            "Hiring": [-8.54, -8.70],
            "HiringExp": [-14.40, -11.04],
            "CapXExp": [-11.35, 1.67],
            "LaborCosts": [-35.59, -20.65],
            "NonlaborCosts": [-2.87, -17.65],
        }
    )

    def test_parses_and_filters(self, monkeypatch):
        """The survey workbook parses, columns map, and dates filter."""
        _patch_xlsx(monkeypatch, self._FRAME, "Data")
        query = FederalReserveChicagoEconomicConditionsFetcher.transform_query(
            {"start_date": "2026-06-01", "end_date": "2026-12-31"}
        )
        rows = FederalReserveChicagoEconomicConditionsFetcher.extract_data(query, None)
        result = FederalReserveChicagoEconomicConditionsFetcher.transform_data(
            query, rows
        )
        assert all(
            isinstance(r, FederalReserveChicagoEconomicConditionsData) for r in result
        )
        assert [r.date for r in result] == [date(2026, 6, 1)]
        assert result[0].activity == 17.52
        assert result[0].activity_manufacturing == 65.31

    def test_reference_date_basis(self, monkeypatch):
        """The reference-date view reads its own sheet and full dates."""
        reference = self._FRAME.assign(Date=["2026-05-31", "2026-06-15"])
        _patch_xlsx(monkeypatch, reference, "Data by Reference Date")
        query = FederalReserveChicagoEconomicConditionsFetcher.transform_query(
            {"date_basis": "reference"}
        )
        rows = FederalReserveChicagoEconomicConditionsFetcher.extract_data(query, None)
        result = FederalReserveChicagoEconomicConditionsFetcher.transform_data(
            query, rows
        )
        assert [r.date for r in result] == [date(2026, 5, 31), date(2026, 6, 15)]
        assert result[-1].activity == 17.52

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _csv_bytes_response(""),
        )
        query = FederalReserveChicagoEconomicConditionsFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveChicagoEconomicConditionsFetcher.extract_data(query, None)


class TestRetailTrade:
    """Tests for the CARTS fetcher."""

    def test_weekly_pivots_and_filters(self, monkeypatch):
        """The weekly figure pivots to one column per series and the date filters."""
        _patch_carts(monkeypatch)
        query = FederalReserveChicagoRetailTradeFetcher.transform_query(
            {"figure": "weekly", "start_date": "2026-05-28", "end_date": "2026-12-31"}
        )
        rows = FederalReserveChicagoRetailTradeFetcher.extract_data(query, None)
        result = FederalReserveChicagoRetailTradeFetcher.transform_data(query, rows)
        assert all(isinstance(r, FederalReserveChicagoRetailTradeData) for r in result)
        assert [r.date for r in result] == [date(2026, 5, 28)]
        row = result[0].model_dump()
        assert row["Retail and Food Services Sales (Mils. $)"] == 617609.59
        assert row["Retail and Food Services Sales (Mils. 2017$)"] == 501588.53

    def test_monthly_nowcast_and_nan(self, monkeypatch):
        """The monthly figure exposes the nowcast columns and maps NA to None."""
        _patch_carts(monkeypatch)
        query = FederalReserveChicagoRetailTradeFetcher.transform_query(
            {"figure": "monthly"}
        )
        rows = FederalReserveChicagoRetailTradeFetcher.extract_data(query, None)
        result = FederalReserveChicagoRetailTradeFetcher.transform_data(query, rows)
        by_date = {r.date: r.model_dump() for r in result}
        assert by_date[date(2026, 5, 1)]["Sales Nowcast, m/m % chg."] == -0.24
        assert by_date[date(2026, 5, 1)]["Sales, m/m % chg."] is None
        columns = set(result[0].model_dump()) - {"date"}
        assert columns == {
            "Sales, m/m % chg.",
            "Sales Nowcast, m/m % chg.",
            "Inflation-adjusted Sales, m/m % chg.",
            "Inflation-adjusted Sales Nowcast, m/m % chg.",
        }

    def test_current_month_strips_percent(self, monkeypatch):
        """The current-month snapshot parses its dated percent strings."""
        _patch_carts(monkeypatch)
        query = FederalReserveChicagoRetailTradeFetcher.transform_query(
            {"figure": "current_month"}
        )
        rows = FederalReserveChicagoRetailTradeFetcher.extract_data(query, None)
        result = FederalReserveChicagoRetailTradeFetcher.transform_data(query, rows)
        assert [r.date for r in result] == [date(2026, 5, 1)]
        row = result[0].model_dump()
        assert row["Sales SA, m/m"] == -0.2
        assert row["Prices SA, m/m"] == 0.8

    def test_nowcast_contributions_derives_year(self, monkeypatch):
        """The contributions figure recovers its year from the snapshot figure."""
        _patch_carts(monkeypatch)
        query = FederalReserveChicagoRetailTradeFetcher.transform_query(
            {"figure": "nowcast_contributions"}
        )
        rows = FederalReserveChicagoRetailTradeFetcher.extract_data(query, None)
        result = FederalReserveChicagoRetailTradeFetcher.transform_data(query, rows)
        assert [r.date for r in result] == [date(2026, 5, 1)]
        row = result[0].model_dump()
        assert row["Census"] == 0.13
        assert row["Transactions"] == -0.22

    def test_benchmark_figures(self, monkeypatch):
        """The benchmark figures expose their comparison series as columns."""
        _patch_carts(monkeypatch)
        query = FederalReserveChicagoRetailTradeFetcher.transform_query(
            {"figure": "vs_bea_cpi"}
        )
        rows = FederalReserveChicagoRetailTradeFetcher.extract_data(query, None)
        result = FederalReserveChicagoRetailTradeFetcher.transform_data(query, rows)
        by_date = {r.date: r.model_dump() for r in result}
        assert by_date[date(2026, 5, 1)]["CPI, m/m % chg."] == 5.45
        assert by_date[date(2026, 5, 1)]["CARTS Nowcast, m/m % chg."] == 4.65
        assert by_date[date(2026, 5, 1)]["BEA PCE Goods, m/m % chg."] is None

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        _patch_text(monkeypatch, "")
        query = FederalReserveChicagoRetailTradeFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveChicagoRetailTradeFetcher.extract_data(query, None)


class TestLaborMarket:
    """Tests for the CFLMI fetcher."""

    _FRAME = DataFrame(
        {
            "date": ["2026-04-18", "2026-05-16"],
            "layoffs_other_seps": [2.068, 2.059],
            "hiring_rate_uw": [45.72, 45.51],
            "fcr": [4.327, 4.328],
            "s": [2.243, None],
            "f": [48.04, None],
        }
    )

    def test_pivots_rates_with_labels_and_nan(self, monkeypatch):
        """The rates sheet pivots to labelled columns and NaN maps to None."""
        _patch_xlsx(monkeypatch, self._FRAME, "1. Rates")
        query = FederalReserveChicagoLaborMarketFetcher.transform_query(
            {"table": "rates", "start_date": "2026-01-01", "end_date": "2026-12-31"}
        )
        rows = FederalReserveChicagoLaborMarketFetcher.extract_data(query, None)
        result = FederalReserveChicagoLaborMarketFetcher.transform_data(query, rows)
        assert all(isinstance(r, FederalReserveChicagoLaborMarketData) for r in result)
        by_date = {r.date: r.model_dump() for r in result}
        row = by_date[date(2026, 5, 16)]
        assert row["Hiring Rate (Unemployment-Weighted)"] == 45.51
        assert row["Separation Rate"] is None
        assert row["Job-Finding Rate"] is None
        assert result[0].release is None

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _csv_bytes_response(""),
        )
        query = FederalReserveChicagoLaborMarketFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveChicagoLaborMarketFetcher.extract_data(query, None)


class TestFarmlandValues:
    """Tests for the Farmland Values fetcher."""

    def test_parses_drops_blank_and_filters(self, monkeypatch):
        """The CSV parses, drops the blank column, and the quarter-month maps."""
        _patch_text(monkeypatch, _FARMLAND)
        query = FederalReserveChicagoFarmlandValuesFetcher.transform_query(
            {"start_date": "2026-01-01", "end_date": "2026-12-31"}
        )
        rows = FederalReserveChicagoFarmlandValuesFetcher.extract_data(query, None)
        result = FederalReserveChicagoFarmlandValuesFetcher.transform_data(query, rows)
        assert all(
            isinstance(r, FederalReserveChicagoFarmlandValuesData) for r in result
        )
        assert [r.date for r in result] == [date(2026, 1, 1)]
        assert result[0].year_over_year == 3.0
        assert result[0].illinois == -2.0
        assert not hasattr(result[0], "blank")

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        _patch_text(monkeypatch, "")
        query = FederalReserveChicagoFarmlandValuesFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveChicagoFarmlandValuesFetcher.extract_data(query, None)


class TestAgCredit:
    """Tests for the Agricultural Credit Conditions fetcher."""

    def test_parses_and_filters(self, monkeypatch):
        """The CSV parses, columns map, and the quarter-month maps."""
        _patch_text(monkeypatch, _AG_CREDIT)
        query = FederalReserveChicagoAgCreditFetcher.transform_query(
            {"start_date": "2026-01-01", "end_date": "2026-12-31"}
        )
        rows = FederalReserveChicagoAgCreditFetcher.extract_data(query, None)
        result = FederalReserveChicagoAgCreditFetcher.transform_data(query, rows)
        assert all(isinstance(r, FederalReserveChicagoAgCreditData) for r in result)
        assert [r.date for r in result] == [date(2026, 1, 1)]
        assert result[0].loan_demand_index == 141.0
        assert result[0].loan_to_deposit_ratio == 79.8

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        _patch_text(monkeypatch, "")
        query = FederalReserveChicagoAgCreditFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveChicagoAgCreditFetcher.extract_data(query, None)


class TestFarmLoanRates:
    """Tests for the New Farm Loan Interest Rates fetcher."""

    def test_skips_note_row_and_filters(self, monkeypatch):
        """The leading note row is dropped and observations parse."""
        _patch_text(monkeypatch, _FARM_LOANS)
        query = FederalReserveChicagoFarmLoanRatesFetcher.transform_query(
            {"start_date": "2026-04-01", "end_date": "2026-12-31"}
        )
        rows = FederalReserveChicagoFarmLoanRatesFetcher.extract_data(query, None)
        result = FederalReserveChicagoFarmLoanRatesFetcher.transform_data(query, rows)
        assert all(
            isinstance(r, FederalReserveChicagoFarmLoanRatesData) for r in result
        )
        assert [r.date for r in result] == [date(2026, 4, 1)]
        assert result[0].operating_loans == 7.08
        assert result[0].farm_real_estate_loans == 6.74

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        _patch_text(monkeypatch, "")
        query = FederalReserveChicagoFarmLoanRatesFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveChicagoFarmLoanRatesFetcher.extract_data(query, None)


class TestBraveButtersKelley:
    """Tests for the frozen BBKI fetcher."""

    def test_parses_maps_and_nan_to_none(self, monkeypatch):
        """The CSV parses, columns map, and trailing NaN maps to None."""
        _patch_text(monkeypatch, _BBKI)
        query = FederalReserveChicagoBraveButtersKelleyFetcher.transform_query(
            {"start_date": "2022-05-01", "end_date": "2022-12-31"}
        )
        rows = FederalReserveChicagoBraveButtersKelleyFetcher.extract_data(query, None)
        result = FederalReserveChicagoBraveButtersKelleyFetcher.transform_data(
            query, rows
        )
        assert all(
            isinstance(r, FederalReserveChicagoBraveButtersKelleyData) for r in result
        )
        assert [r.date for r in result] == [date(2022, 5, 31)]
        assert result[0].coincident_index == -0.18
        assert result[0].irregular is None
        assert result[0].monthly_gdp is None

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        _patch_text(monkeypatch, "")
        query = FederalReserveChicagoBraveButtersKelleyFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveChicagoBraveButtersKelleyFetcher.extract_data(query, None)


class TestMidwestEconomy:
    """Tests for the frozen MEI fetcher."""

    def test_parses_and_filters(self, monkeypatch):
        """The CSV parses, columns map, and dates filter."""
        _patch_text(monkeypatch, _MEI)
        query = FederalReserveChicagoMidwestEconomyFetcher.transform_query(
            {"start_date": "2021-05-01", "end_date": "2021-12-31"}
        )
        rows = FederalReserveChicagoMidwestEconomyFetcher.extract_data(query, None)
        result = FederalReserveChicagoMidwestEconomyFetcher.transform_data(query, rows)
        assert all(
            isinstance(r, FederalReserveChicagoMidwestEconomyData) for r in result
        )
        assert [r.date for r in result] == [date(2021, 5, 1)]
        assert result[0].mei == 0.69
        assert result[0].michigan == 0.10
        assert result[0].consumer == 0.11

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        _patch_text(monkeypatch, "")
        query = FederalReserveChicagoMidwestEconomyFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveChicagoMidwestEconomyFetcher.extract_data(query, None)
