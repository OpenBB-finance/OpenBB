"""Test FRED API endpoints."""

import base64
from datetime import date
from math import inf, isfinite
from statistics import median

import pytest
import requests
from openbb_core.env import Env
from openbb_core.provider.utils.helpers import get_querystring

from openbb_fred.models.ameribor import MATURITY_TO_FRED_ID, FredAmeriborData
from openbb_fred.models.balance_of_payments import FredBalanceOfPaymentsData
from openbb_fred.models.bond_indices import BAML_CATEGORIES, FredBondIndicesData
from openbb_fred.models.commercial_paper import CP_SERIES_IDS, FREDCommercialPaperData
from openbb_fred.models.commodity_spot_prices import (
    SERIES_MAP,
    FredCommoditySpotPricesData,
)
from openbb_fred.models.consumer_price_index import FREDConsumerPriceIndexData
from openbb_fred.models.dwpcr_rates import FREDDiscountWindowPrimaryCreditRateData
from openbb_fred.models.ecb_interest_rates import (
    FREDEuropeanCentralBankInterestRatesData,
)
from openbb_fred.models.economic_calendar import FredEconomicCalendarData
from openbb_fred.models.euro_short_term_rate import FredEuroShortTermRateData
from openbb_fred.models.fed_projections import FREDPROJECTIONData
from openbb_fred.models.federal_funds_rate import FredFederalFundsRateData
from openbb_fred.models.ffrmc import FREDSelectedTreasuryConstantMaturityData
from openbb_fred.models.high_quality_market import (
    FredHighQualityMarketCorporateBondData,
)
from openbb_fred.models.iorb_rates import FREDIORBData
from openbb_fred.models.manufacturing_outlook_ny import FredManufacturingOutlookNYData
from openbb_fred.models.manufacturing_outlook_texas import (
    FredManufacturingOutlookTexasData,
)
from openbb_fred.models.mortgage_indices import (
    MORTGAGE_CHOICES_TO_ID,
    FredMortgageIndicesData,
)
from openbb_fred.models.non_farm_payrolls import FredNonFarmPayrollsData
from openbb_fred.models.overnight_bank_funding_rate import (
    FredOvernightBankFundingRateData,
)
from openbb_fred.models.personal_consumption_expenditures import (
    FredPersonalConsumptionExpendituresData,
)
from openbb_fred.models.regional import FredRegionalData
from openbb_fred.models.release_table import FredReleaseTableData
from openbb_fred.models.retail_prices import FredRetailPricesData
from openbb_fred.models.search import FredSearchData
from openbb_fred.models.senior_loan_officer_survey import (
    SLOOS_CATEGORIES,
    FredSeniorLoanOfficerSurveyData,
)
from openbb_fred.models.series import FredSeriesData
from openbb_fred.models.sofr import FREDSOFRData
from openbb_fred.models.sonia_rates import FREDSONIAData
from openbb_fred.models.spot import FREDSpotRateData
from openbb_fred.models.survey_of_economic_conditions_chicago import (
    FredSurveyOfEconomicConditionsChicagoData,
)
from openbb_fred.models.tbffr import FREDSelectedTreasuryBillData
from openbb_fred.models.tips_yields import FredTipsYieldsData
from openbb_fred.models.tmc import FREDTreasuryConstantMaturityData
from openbb_fred.models.university_of_michigan import FredUofMichiganData
from openbb_fred.models.yield_curve import FREDYieldCurveData
from openbb_fred.utils.api import observation_dates
from openbb_fred.utils.fred_helpers import YIELD_CURVES

PERCENT_BAND = (-100.0, 100.0)
POSITIVE_BAND = (0.0, 1.0e6)
INDEX_BAND = (0.0, 1.0e5)
COUNT_BAND = (0.0, 1.0e12)
WIDE_BAND = (-1.0e15, 1.0e15)
TRANSFORMS = ("chg", "ch1", "pch", "pc1", "pca", "cch", "cca", "log")


def results_of(result, data_class, minimum=1):
    """Return the rows one endpoint served, asserting the model shape they carry.

    Parameters
    ----------
    result : requests.Response
        The endpoint response.
    data_class : type
        The provider Data model the rows are expected to carry.
    minimum : int
        The fewest rows the parameters can legitimately return.

    Returns
    -------
    list
        The rows the response envelope carries.
    """
    assert isinstance(result, requests.Response)
    assert result.status_code == 200

    payload = result.json()

    assert isinstance(payload, dict)

    rows = payload["results"]

    assert isinstance(rows, list)
    assert len(rows) >= minimum
    assert all(isinstance(row, dict) for row in rows)
    assert set(data_class.model_fields) <= set(rows[0])

    return rows


def dates_of(rows, field="date"):
    """Return one date per row, asserting every one of them parses as a date."""
    dates = [date.fromisoformat(str(row[field])[:10]) for row in rows]
    assert dates

    return dates


def values_of(rows, *fields):
    """Return every value the rows carry under the named fields."""
    return [row.get(field) for field in fields for row in rows]


def assert_oldest_first(dates):
    """Assert the observations are ordered oldest first."""
    assert list(dates) == sorted(dates)


def assert_newest_first(dates):
    """Assert the observations are ordered newest first."""
    assert list(dates) == sorted(dates, reverse=True)


def assert_inside_window(dates, params):
    """Assert every observation falls inside the window the query asked for."""
    start = params.get("start_date")
    end = params.get("end_date")

    if start:
        assert min(dates) >= date.fromisoformat(start)

    if end:
        assert max(dates) <= date.fromisoformat(end)


def assert_finite(values, low, high):
    """Assert the served numbers are finite and inside a plausible band.

    Parameters
    ----------
    values : list
        The values read off the rows, nulls included.
    low : float
        The lowest value the field can plausibly carry.
    high : float
        The highest value the field can plausibly carry.

    Returns
    -------
    list
        The values that were actually served.
    """
    seen = [value for value in values if value is not None]
    assert all(isinstance(value, (int, float)) for value in seen)
    assert all(isfinite(value) for value in seen)
    assert all(low <= value <= high for value in seen)

    return seen


def assert_months(dates, requested):
    """Assert every observation falls in one of the months the query asked for."""
    months = {tuple(entry[:7].split("-")) for entry in observation_dates(requested)}
    assert {(f"{value.year:04d}", f"{value.month:02d}") for value in dates} <= months


def median_gap(dates):
    """Return the median number of days between consecutive observations."""
    ordered = sorted(set(dates))
    assert len(ordered) > 1

    return median(
        (later - earlier).days for earlier, later in zip(ordered, ordered[1:])
    )


def band_for(params, tight):
    """Return the band a field sits in, widened when the query transforms it."""
    return WIDE_BAND if params.get("transform") in TRANSFORMS else tight


@pytest.fixture(scope="session")
def headers():
    """Get the headers for the API request."""
    userpass = f"{Env().API_USERNAME}:{Env().API_PASSWORD}"
    userpass_bytes = userpass.encode("ascii")
    base64_bytes = base64.b64encode(userpass_bytes)

    return {"Authorization": f"Basic {base64_bytes.decode('ascii')}"}


class TestCommodityPrice:
    """Test the commodity price commands the FRED router serves."""

    @pytest.mark.parametrize(
        "params",
        [
            {"provider": "fred"},
            {
                "commodity": "all",
                "start_date": None,
                "end_date": None,
                "frequency": None,
                "transform": None,
                "aggregation_method": None,
                "provider": "fred",
            },
            {
                "commodity": "wti",
                "start_date": "2023-01-01",
                "end_date": "2024-01-01",
                "frequency": "m",
                "aggregation_method": "avg",
                "transform": "pc1",
                "use_cache": False,
                "provider": "fred",
            },
        ],
    )
    @pytest.mark.integration
    def test_commodity_spot_prices_are_served(self, params, headers):
        """Test the commodity price spot endpoint."""
        params = {p: v for p, v in params.items() if v is not None}

        query_str = get_querystring(params, [])
        url = f"http://localhost:8000/api/v1/fred/commodity/price/spot?{query_str}"
        result = requests.get(url, headers=headers, timeout=30)
        commodity = params.get("commodity", "all")
        rows = results_of(result, FredCommoditySpotPricesData)
        dates = dates_of(rows)

        assert_oldest_first(dates)
        assert_inside_window(dates, params)
        assert {row["symbol"] for row in rows} <= set(SERIES_MAP[commodity].split(","))
        assert all(row["commodity"] for row in rows)
        assert assert_finite(values_of(rows, "price"), *band_for(params, POSITIVE_BAND))

        if params.get("frequency") == "m":
            assert len(rows) <= 13
        else:
            assert len(rows) > 100


class TestEconomy:
    """Test the economy commands the FRED router serves."""

    @pytest.mark.parametrize(
        "params",
        [
            {"provider": "fred"},
            {
                "country": "united_states",
                "start_date": None,
                "end_date": None,
                "provider": "fred",
            },
            {
                "country": "japan",
                "start_date": "2020-01-01",
                "end_date": "2023-12-31",
                "use_cache": False,
                "provider": "fred",
            },
        ],
    )
    @pytest.mark.integration
    def test_balance_of_payments_is_served(self, params, headers):
        """Test the economy balance_of_payments endpoint."""
        params = {p: v for p, v in params.items() if v is not None}

        query_str = get_querystring(params, [])
        url = (
            f"http://localhost:8000/api/v1/fred/economy/balance_of_payments?{query_str}"
        )
        result = requests.get(url, headers=headers, timeout=30)
        rows = results_of(result, FredBalanceOfPaymentsData)
        periods = dates_of(rows, "period")

        assert_newest_first(periods)
        assert_inside_window(periods, params)
        assert median_gap(periods) >= 80
        assert assert_finite(
            values_of(rows, "balance_total", "credits_total", "debits_total"),
            *WIDE_BAND,
        )
        assert_finite(values_of(rows, "balance_percent_of_gdp"), -200.0, 200.0)

        if params.get("start_date"):
            assert len(rows) <= 24

    @pytest.mark.parametrize(
        "params",
        [
            {"provider": "fred"},
            {
                "start_date": "2025-07-01",
                "end_date": "2025-07-02",
                "release_id": None,
                "provider": "fred",
            },
            {
                "start_date": "2024-01-02",
                "end_date": "2024-01-09",
                "release_id": 10,
                "use_cache": False,
                "provider": "fred",
            },
        ],
    )
    @pytest.mark.integration
    def test_calendar_is_served(self, params, headers):
        """Test the economy calendar endpoint."""
        params = {p: v for p, v in params.items() if v is not None}

        query_str = get_querystring(params, [])
        url = f"http://localhost:8000/api/v1/fred/economy/calendar?{query_str}"
        result = requests.get(url, headers=headers, timeout=60)
        rows = results_of(result, FredEconomicCalendarData)
        dates = dates_of(rows)

        assert_inside_window(dates, params)
        assert all(row["event"] for row in rows)
        assert all(isinstance(row["release_id"], int) for row in rows)

        if params.get("release_id"):
            assert {row["release_id"] for row in rows} == {params["release_id"]}

    @pytest.mark.parametrize(
        "params",
        [
            {"country": "united_states", "provider": "fred"},
            {
                "country": "spain",
                "transform": "yoy",
                "frequency": "annual",
                "harmonized": False,
                "start_date": "2020-01-01",
                "end_date": "2023-06-06",
                "provider": "fred",
            },
            {
                "country": "portugal,spain",
                "transform": "period",
                "frequency": "monthly",
                "harmonized": True,
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "use_cache": False,
                "provider": "fred",
            },
        ],
    )
    @pytest.mark.integration
    def test_cpi_is_served(self, params, headers):
        """Test the economy cpi endpoint."""
        params = {p: v for p, v in params.items() if v is not None}

        query_str = get_querystring(params, [])
        url = f"http://localhost:8000/api/v1/fred/economy/cpi?{query_str}"
        result = requests.get(url, headers=headers, timeout=30)
        rows = results_of(result, FREDConsumerPriceIndexData)
        dates = dates_of(rows)

        assert_oldest_first(dates)
        assert_inside_window(dates, params)
        assert {row["country"] for row in rows} <= set(params["country"].split(","))
        assert assert_finite(values_of(rows, "value"), *PERCENT_BAND)

        if params.get("frequency") == "annual":
            assert len(rows) <= 8

    @pytest.mark.parametrize(
        "params",
        [
            {"symbol": "NYUR", "provider": "fred"},
            {
                "symbol": "CAICLAIMS",
                "is_series_group": False,
                "start_date": "1990-01-01",
                "end_date": "2010-01-01",
                "provider": "fred",
            },
            {
                "symbol": "156241",
                "is_series_group": True,
                "start_date": "2000-01-01",
                "end_date": None,
                "frequency": "w",
                "units": "Number",
                "region_type": "state",
                "season": "nsa",
                "aggregation_method": "eop",
                "transform": "ch1",
                "use_cache": False,
                "provider": "fred",
            },
        ],
    )
    @pytest.mark.integration
    def test_fred_regional_is_served(self, params, headers):
        """Test the economy fred_regional endpoint."""
        params = {p: v for p, v in params.items() if v is not None}

        query_str = get_querystring(params, [])
        url = f"http://localhost:8000/api/v1/fred/economy/fred_regional?{query_str}"
        result = requests.get(url, headers=headers, timeout=60)
        rows = results_of(result, FredRegionalData)
        dates = dates_of(rows)

        assert all(isinstance(row["region"], str) and row["region"] for row in rows)
        assert all(row["series_id"] for row in rows)
        assert all(row["code"] not in (None, "") for row in rows)
        assert assert_finite(values_of(rows, "value"), *WIDE_BAND)

        if params.get("end_date"):
            assert max(dates) <= date.fromisoformat(params["end_date"])

    @pytest.mark.parametrize(
        "params",
        [
            {"release_id": "50", "provider": "fred"},
            {"release_id": "14", "element_id": "7930", "provider": "fred"},
            {
                "release_id": "53",
                "element_id": "12883",
                "date": "2023-01-01",
                "use_cache": False,
                "provider": "fred",
            },
        ],
    )
    @pytest.mark.integration
    def test_fred_release_table_is_served(self, params, headers):
        """Test the economy fred_release_table endpoint."""
        params = {p: v for p, v in params.items() if v is not None}

        query_str = get_querystring(params, [])
        url = (
            f"http://localhost:8000/api/v1/fred/economy/fred_release_table?{query_str}"
        )
        result = requests.get(url, headers=headers, timeout=60)
        rows = results_of(result, FredReleaseTableData)
        keys = [
            (str(row["date"] or ""), inf if row["line"] is None else row["line"])
            for row in rows
        ]

        assert keys == sorted(keys)
        assert all(row["element_id"] for row in rows)
        assert all(row["name"] for row in rows)
        assert_finite(values_of(rows, "value"), *WIDE_BAND)

        observed = [row for row in rows if row["symbol"]]

        if observed:
            assert dates_of(observed)
            assert all(row["value"] is not None for row in observed)

    @pytest.mark.parametrize(
        "params",
        [
            {"provider": "fred"},
            {"query": "gdp", "provider": "fred"},
            {
                "query": "GDP*",
                "search_type": "series_id",
                "release_id": None,
                "offset": 0,
                "limit": 10,
                "order_by": "observation_end",
                "sort_order": "desc",
                "filter_variable": None,
                "filter_value": None,
                "tag_names": None,
                "exclude_tag_names": None,
                "series_id": None,
                "provider": "fred",
            },
            {
                "query": None,
                "search_type": "release",
                "release_id": 10,
                "limit": 10,
                "use_cache": False,
                "provider": "fred",
            },
            {"series_id": "NYICLAIMS", "provider": "fred"},
        ],
    )
    @pytest.mark.integration
    def test_fred_search_is_served(self, params, headers):
        """Test the economy fred_search endpoint."""
        params = {p: v for p, v in params.items() if v is not None}

        query_str = get_querystring(params, [])
        url = f"http://localhost:8000/api/v1/fred/economy/fred_search?{query_str}"
        result = requests.get(url, headers=headers, timeout=30)
        rows = results_of(result, FredSearchData)
        ends = [row["observation_end"] for row in rows]

        if params.get("limit"):
            assert len(rows) <= params["limit"]

        if all(end is not None for end in ends):
            assert ends == sorted(ends, reverse=True)

        if params.get("series_id"):
            assert {row["series_id"] for row in rows} == {params["series_id"]}
            assert all(row["series_group"] for row in rows)
        elif params.get("release_id"):
            assert all(row["series_id"] for row in rows)
        elif params.get("query"):
            assert all(row["series_id"] for row in rows)

            if params.get("search_type") != "series_id":
                term = params["query"].lower()
                assert all(
                    term in " ".join(str(v) for v in row.values()).lower()
                    for row in rows
                )
        else:
            assert all(row["release_id"] for row in rows)

    @pytest.mark.parametrize(
        "params",
        [
            {"symbol": "GDP", "provider": "fred"},
            {
                "symbol": "SP500",
                "start_date": None,
                "end_date": None,
                "limit": 10000,
                "frequency": "q",
                "aggregation_method": "eop",
                "transform": "chg",
                "provider": "fred",
            },
            {
                "symbol": "GDP,UNRATE",
                "start_date": "2020-01-01",
                "end_date": "2024-01-01",
                "use_cache": False,
                "provider": "fred",
            },
        ],
    )
    @pytest.mark.integration
    def test_fred_series_is_served(self, params, headers):
        """Test the economy fred_series endpoint."""
        params = {p: v for p, v in params.items() if v is not None}

        query_str = get_querystring(params, [])
        url = f"http://localhost:8000/api/v1/fred/economy/fred_series?{query_str}"
        result = requests.get(url, headers=headers, timeout=30)
        rows = results_of(result, FredSeriesData)
        dates = dates_of(rows)
        symbols = params["symbol"].split(",")
        carried = {key.lower().replace("_", "") for key in rows[0]}

        assert_oldest_first(dates)
        assert_inside_window(dates, params)
        assert {symbol.lower().replace("_", "") for symbol in symbols} <= carried
        assert assert_finite(
            [value for row in rows for key, value in row.items() if key != "date"],
            *WIDE_BAND,
        )

        if params.get("limit"):
            assert len(rows) <= params["limit"]

    @pytest.mark.parametrize(
        "params",
        [
            {"provider": "fred"},
            {
                "date": "2024-05-01,2024-04-01,2023-05-01",
                "category": "pce_price_index",
                "provider": "fred",
            },
            {
                "date": "2024-06-01",
                "category": "real_pce_percent_change",
                "use_cache": False,
                "provider": "fred",
            },
        ],
    )
    @pytest.mark.integration
    def test_pce_is_served(self, params, headers):
        """Test the economy pce endpoint."""
        params = {p: v for p, v in params.items() if v is not None}

        query_str = get_querystring(params, [])
        url = f"http://localhost:8000/api/v1/fred/economy/pce?{query_str}"
        result = requests.get(url, headers=headers, timeout=30)
        rows = results_of(result, FredPersonalConsumptionExpendituresData)
        dates = dates_of(rows)
        keys = [(row["date"], row["line"]) for row in rows]

        assert keys == sorted(keys)
        assert all(row["symbol"] and row["name"] and row["units"] for row in rows)
        assert all(row["element_id"] and row["parent_id"] for row in rows)
        assert all(isinstance(row["level"], int) for row in rows)
        assert assert_finite(values_of(rows, "value"), *WIDE_BAND)

        if params.get("date"):
            assert_months(dates, params["date"])
            assert len(set(dates)) <= len(observation_dates(params["date"]))

    @pytest.mark.parametrize(
        "params",
        [
            {},
            {"release_id": "9", "element_id": "201241"},
            {
                "release_id": "9",
                "element_id": "201241",
                "frequency": "monthly",
                "limit": 4,
                "use_cache": False,
            },
        ],
    )
    @pytest.mark.integration
    def test_release_table_is_served(self, params, headers):
        """Test the economy release_table endpoint."""
        params = {p: v for p, v in params.items() if v is not None}

        query_str = get_querystring(params, [])
        url = f"http://localhost:8000/api/v1/fred/economy/release_table?{query_str}"
        result = requests.get(url, headers=headers, timeout=60)

        assert isinstance(result, requests.Response)
        assert result.status_code == 200

        served = result.json()
        fixed = {"series", "symbol", "units", "trend"}

        assert isinstance(served, list)
        assert len(served) > 0
        assert all(isinstance(row, dict) for row in served)
        assert all(fixed <= set(row) for row in served)
        assert all(row["series"] for row in served)

        periods = [key for key in served[0] if key not in fixed]

        assert periods
        assert len(periods) <= params.get("limit", 8)
        assert all(date.fromisoformat(period) for period in periods)
        assert all(set(row) - fixed == set(periods) for row in served)

        observed = [row for row in served if row["symbol"]]

        assert observed
        assert all(isinstance(row["trend"], list) and row["trend"] for row in observed)
        assert assert_finite(
            [value for row in observed for value in row["trend"]], *WIDE_BAND
        )

    @pytest.mark.parametrize(
        "params",
        [
            {"provider": "fred"},
            {
                "country": "united_states",
                "item": "meats",
                "region": "all_city",
                "frequency": "annual",
                "start_date": "2022-01-01",
                "end_date": "2024-04-01",
                "transform": "pc1",
                "provider": "fred",
            },
            {
                "item": "eggs",
                "region": "northeast",
                "frequency": "monthly",
                "use_cache": False,
                "provider": "fred",
            },
        ],
    )
    @pytest.mark.integration
    def test_retail_prices_are_served(self, params, headers):
        """Test the economy retail_prices endpoint."""
        params = {p: v for p, v in params.items() if v is not None}

        query_str = get_querystring(params, [])
        url = f"http://localhost:8000/api/v1/fred/economy/retail_prices?{query_str}"
        result = requests.get(url, headers=headers, timeout=30)
        rows = results_of(result, FredRetailPricesData)
        dates = dates_of(rows)
        keys = [(row["date"], row["description"]) for row in rows]

        assert keys == sorted(keys)
        assert_inside_window(dates, params)
        assert {row["country"] for row in rows} == {"united_states"}
        assert all(row["symbol"] and row["description"] for row in rows)
        assert assert_finite(values_of(rows, "value"), *band_for(params, POSITIVE_BAND))


class TestEconomySurvey:
    """Test the economy survey commands the FRED router serves."""

    @pytest.mark.parametrize(
        "params",
        [
            {"provider": "fred"},
            {
                "start_date": "2024-01-01",
                "end_date": "2024-04-01",
                "transform": None,
                "aggregation_method": None,
                "frequency": None,
                "provider": "fred",
            },
            {
                "start_date": "2020-01-01",
                "end_date": "2024-01-01",
                "frequency": "quarter",
                "aggregation_method": "avg",
                "transform": "pch",
                "use_cache": False,
                "provider": "fred",
            },
        ],
    )
    @pytest.mark.integration
    def test_economic_conditions_chicago_is_served(self, params, headers):
        """Test the economy survey economic_conditions_chicago endpoint."""
        params = {p: v for p, v in params.items() if v is not None}

        query_str = get_querystring(params, [])
        url = f"http://localhost:8000/api/v1/fred/economy/survey/economic_conditions_chicago?{query_str}"
        result = requests.get(url, headers=headers, timeout=30)
        rows = results_of(result, FredSurveyOfEconomicConditionsChicagoData)
        dates = dates_of(rows)

        assert_oldest_first(dates)
        assert_inside_window(dates, params)
        assert assert_finite(
            values_of(rows, "activity_index", "one_year_outlook", "current_hiring"),
            *band_for(params, PERCENT_BAND),
        )

        if params.get("frequency") == "quarter":
            assert len(rows) <= 20

    @pytest.mark.parametrize(
        "params",
        [
            {"provider": "fred"},
            {
                "topic": "new_orders",
                "start_date": "2024-01-01",
                "end_date": "2024-04-01",
                "transform": None,
                "aggregation_method": None,
                "frequency": None,
                "provider": "fred",
            },
            {
                "topic": "business_outlook,employment",
                "seasonally_adjusted": True,
                "start_date": "2020-01-01",
                "end_date": "2024-01-01",
                "frequency": "quarter",
                "aggregation_method": "avg",
                "transform": "pch",
                "use_cache": False,
                "provider": "fred",
            },
        ],
    )
    @pytest.mark.integration
    def test_manufacturing_outlook_ny_is_served(self, params, headers):
        """Test the economy survey manufacturing_outlook_ny endpoint."""
        params = {p: v for p, v in params.items() if v is not None}

        query_str = get_querystring(params, [])
        url = f"http://localhost:8000/api/v1/fred/economy/survey/manufacturing_outlook_ny?{query_str}"
        result = requests.get(url, headers=headers, timeout=30)
        rows = results_of(result, FredManufacturingOutlookNYData)
        dates = dates_of(rows)
        topics = params.get("topic", "new_orders").split(",")
        expected = {
            f"{side}_{topic}" for topic in topics for side in ("current", "future")
        }

        assert_oldest_first(dates)
        assert_inside_window(dates, params)
        assert {row["topic"] for row in rows} <= expected
        assert assert_finite(
            values_of(rows, "diffusion_index"), *band_for(params, PERCENT_BAND)
        )
        assert_finite(
            values_of(
                rows,
                "percent_reporting_increase",
                "percent_reporting_decrease",
                "percent_reporting_no_change",
            ),
            *band_for(params, (0.0, 100.0)),
        )

    @pytest.mark.parametrize(
        "params",
        [
            {"provider": "fred"},
            {
                "topic": "new_orders",
                "start_date": "2024-01-01",
                "end_date": "2024-04-01",
                "transform": None,
                "aggregation_method": None,
                "frequency": None,
                "provider": "fred",
            },
            {
                "topic": "business_activity,production",
                "start_date": "2020-01-01",
                "end_date": "2024-01-01",
                "frequency": "annual",
                "aggregation_method": "eop",
                "transform": "ch1",
                "use_cache": False,
                "provider": "fred",
            },
        ],
    )
    @pytest.mark.integration
    def test_manufacturing_outlook_texas_is_served(self, params, headers):
        """Test the economy survey manufacturing_outlook_texas endpoint."""
        params = {p: v for p, v in params.items() if v is not None}

        query_str = get_querystring(params, [])
        url = f"http://localhost:8000/api/v1/fred/economy/survey/manufacturing_outlook_texas?{query_str}"
        result = requests.get(url, headers=headers, timeout=30)
        rows = results_of(result, FredManufacturingOutlookTexasData)
        dates = dates_of(rows)
        topics = params.get("topic", "new_orders_growth").split(",")
        expected = {
            f"{side}_{topic}" for topic in topics for side in ("current", "future")
        }

        assert_oldest_first(dates)
        assert_inside_window(dates, params)
        assert {row["topic"] for row in rows} <= expected
        assert assert_finite(
            values_of(rows, "diffusion_index"), *band_for(params, PERCENT_BAND)
        )

        if params.get("frequency") == "annual":
            assert len(rows) <= 5 * len(expected)

    @pytest.mark.parametrize(
        "params",
        [
            {"provider": "fred"},
            {
                "date": "2024-06-01,2023-06-01",
                "category": "avg_earnings_hourly",
                "provider": "fred",
            },
            {
                "date": "2024-06-01",
                "category": "employees_sa",
                "use_cache": False,
                "provider": "fred",
            },
        ],
    )
    @pytest.mark.integration
    def test_nonfarm_payrolls_are_served(self, params, headers):
        """Test the economy survey nonfarm_payrolls endpoint."""
        params = {p: v for p, v in params.items() if v is not None}

        query_str = get_querystring(params, [])
        url = f"http://localhost:8000/api/v1/fred/economy/survey/nonfarm_payrolls?{query_str}"
        result = requests.get(url, headers=headers, timeout=30)
        rows = results_of(result, FredNonFarmPayrollsData)
        dates = dates_of(rows)
        category = params.get("category", "employees_nsa")

        assert_oldest_first(dates)
        assert all(row["symbol"] and row["name"] for row in rows)
        assert all(row["element_id"] and row["parent_id"] for row in rows)
        assert all(isinstance(row["level"], int) for row in rows)

        if category.startswith("employees") and not category.endswith("percent"):
            assert assert_finite(values_of(rows, "value"), *COUNT_BAND)
        else:
            assert assert_finite(values_of(rows, "value"), *WIDE_BAND)

        if params.get("date"):
            assert_months(dates, params["date"])
            assert len(set(dates)) <= len(observation_dates(params["date"]))

    @pytest.mark.parametrize(
        "params",
        [
            {"provider": "fred"},
            {
                "category": "auto",
                "start_date": "2022-01-01",
                "end_date": "2024-04-01",
                "provider": "fred",
            },
            {
                "category": "credit_card",
                "transform": "pch",
                "start_date": "2020-01-01",
                "end_date": "2024-01-01",
                "use_cache": False,
                "provider": "fred",
            },
        ],
    )
    @pytest.mark.integration
    def test_sloos_is_served(self, params, headers):
        """Test the economy survey sloos endpoint."""
        params = {p: v for p, v in params.items() if v is not None}

        query_str = get_querystring(params, [])
        url = f"http://localhost:8000/api/v1/fred/economy/survey/sloos?{query_str}"
        result = requests.get(url, headers=headers, timeout=30)
        rows = results_of(result, FredSeniorLoanOfficerSurveyData)
        dates = dates_of(rows)
        wanted = SLOOS_CATEGORIES[params.get("category", "spreads")].split(",")

        assert_oldest_first(dates)
        assert_inside_window(dates, params)
        assert {row["symbol"] for row in rows} <= set(wanted)
        assert all(row["title"] for row in rows)
        assert assert_finite(values_of(rows, "value"), *band_for(params, PERCENT_BAND))

    @pytest.mark.parametrize(
        "params",
        [
            {"provider": "fred"},
            {
                "frequency": None,
                "start_date": "2022-01-01",
                "end_date": "2024-04-01",
                "transform": None,
                "aggregation_method": None,
                "provider": "fred",
            },
            {
                "frequency": "quarter",
                "aggregation_method": "avg",
                "transform": "pch",
                "start_date": "2020-01-01",
                "end_date": "2024-01-01",
                "use_cache": False,
                "provider": "fred",
            },
        ],
    )
    @pytest.mark.integration
    def test_university_of_michigan_is_served(self, params, headers):
        """Test the economy survey university_of_michigan endpoint."""
        params = {p: v for p, v in params.items() if v is not None}

        query_str = get_querystring(params, [])
        url = f"http://localhost:8000/api/v1/fred/economy/survey/university_of_michigan?{query_str}"
        result = requests.get(url, headers=headers, timeout=30)
        rows = results_of(result, FredUofMichiganData)
        dates = dates_of(rows)

        assert_oldest_first(dates)
        assert_inside_window(dates, params)
        assert assert_finite(
            values_of(rows, "consumer_sentiment"), *band_for(params, (0.0, 200.0))
        )
        assert assert_finite(
            values_of(rows, "inflation_expectation"),
            *band_for(params, PERCENT_BAND),
        )

        if params.get("frequency") == "quarter":
            assert len(rows) <= 20


class TestFixedIncome:
    """Test the top-level fixed income commands the FRED router serves."""

    @pytest.mark.parametrize(
        "params",
        [
            {"provider": "fred"},
            {
                "category": "high_yield",
                "index": "us,europe,emerging",
                "index_type": "total_return",
                "start_date": "2023-05-31",
                "end_date": "2024-06-01",
                "transform": None,
                "frequency": None,
                "aggregation_method": "avg",
                "provider": "fred",
            },
            {
                "category": "us",
                "index": "corporate",
                "index_type": "oas",
                "start_date": "2023-01-01",
                "end_date": "2024-01-01",
                "frequency": "m",
                "aggregation_method": "eop",
                "use_cache": False,
                "provider": "fred",
            },
        ],
    )
    @pytest.mark.integration
    def test_bond_indices_are_served(self, params, headers):
        """Test the fixedincome bond_indices endpoint."""
        params = {p: v for p, v in params.items() if v is not None}

        query_str = get_querystring(params, [])
        url = f"http://localhost:8000/api/v1/fred/fixedincome/bond_indices?{query_str}"
        result = requests.get(url, headers=headers, timeout=30)
        rows = results_of(result, FredBondIndicesData)
        dates = dates_of(rows)
        index = params.get("index", "yield_curve")

        assert_oldest_first(dates)
        assert_inside_window(dates, params)
        assert all(row["title"] for row in rows)

        if index == "yield_curve":
            maturities = set(BAML_CATEGORIES[params.get("category", "us")][index])
            assert {row["maturity"] for row in rows} <= maturities
        else:
            assert {row["maturity"] for row in rows} == {None}

        if params.get("index_type") == "total_return":
            assert assert_finite(values_of(rows, "value"), *INDEX_BAND)
        else:
            assert assert_finite(values_of(rows, "value"), *PERCENT_BAND)

    @pytest.mark.parametrize(
        "params",
        [
            {"provider": "fred"},
            {
                "index": "usda_30y,fha_30y",
                "start_date": "2023-05-31",
                "end_date": "2024-06-01",
                "transform": None,
                "frequency": None,
                "aggregation_method": "avg",
                "provider": "fred",
            },
            {
                "index": "conforming_30y",
                "start_date": "2023-01-01",
                "end_date": "2024-01-01",
                "frequency": "m",
                "aggregation_method": "eop",
                "transform": "pch",
                "use_cache": False,
                "provider": "fred",
            },
        ],
    )
    @pytest.mark.integration
    def test_mortgage_indices_are_served(self, params, headers):
        """Test the fixedincome mortgage_indices endpoint."""
        params = {p: v for p, v in params.items() if v is not None}

        query_str = get_querystring(params, [])
        url = f"http://localhost:8000/api/v1/fred/fixedincome/mortgage_indices?{query_str}"
        result = requests.get(url, headers=headers, timeout=30)
        rows = results_of(result, FredMortgageIndicesData)
        dates = dates_of(rows)
        wanted = {
            symbol
            for index in params.get("index", "primary").split(",")
            for symbol in MORTGAGE_CHOICES_TO_ID[index].split(",")
        }

        assert_oldest_first(dates)
        assert_inside_window(dates, params)
        assert {row["symbol"] for row in rows} <= wanted
        assert all(row["name"] for row in rows)
        assert assert_finite(values_of(rows, "rate"), *band_for(params, PERCENT_BAND))


class TestFixedIncomeCorporate:
    """Test the corporate bond commands the FRED router serves."""

    @pytest.mark.parametrize(
        "params",
        [
            {"provider": "fred"},
            {
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "maturity": "overnight",
                "category": "financial",
                "transform": None,
                "aggregation_method": None,
                "frequency": None,
                "provider": "fred",
            },
            {
                "start_date": "2023-01-01",
                "end_date": "2024-01-01",
                "maturity": "30d",
                "category": "asset_backed",
                "frequency": "m",
                "aggregation_method": "avg",
                "transform": "pch",
                "use_cache": False,
                "provider": "fred",
            },
        ],
    )
    @pytest.mark.integration
    def test_commercial_paper_is_served(self, params, headers):
        """Test the fixedincome corporate commercial_paper endpoint."""
        params = {p: v for p, v in params.items() if v is not None}

        query_str = get_querystring(params, [])
        url = f"http://localhost:8000/api/v1/fred/fixedincome/corporate/commercial_paper?{query_str}"
        result = requests.get(url, headers=headers, timeout=30)
        rows = results_of(result, FREDCommercialPaperData)
        dates = dates_of(rows)
        maturity = params.get("maturity", "all")
        category = params.get("category", "all")
        published = {
            (entry["maturity"], entry["asset"]) for entry in CP_SERIES_IDS.values()
        }

        assert_oldest_first(dates)
        assert_inside_window(dates, params)
        assert {(row["maturity"], row["asset_type"]) for row in rows} <= published
        assert all(row["title"] for row in rows)
        assert assert_finite(values_of(rows, "rate"), *band_for(params, PERCENT_BAND))

        if category != "all":
            assert {row["asset_type"] for row in rows} == set(category.split(","))

        if maturity != "all":
            assert {row["maturity"] for row in rows} == {
                entry if entry == "overnight" else f"day_{entry.rstrip('d')}"
                for entry in maturity.split(",")
            }

    @pytest.mark.parametrize(
        "params",
        [
            {"provider": "fred"},
            {"date": "2023-01-01", "yield_curve": "spot", "provider": "fred"},
            {
                "date": "2023-01-01,2024-01-01",
                "yield_curve": "par",
                "use_cache": False,
                "provider": "fred",
            },
        ],
    )
    @pytest.mark.integration
    def test_hqm_is_served(self, params, headers):
        """Test the fixedincome corporate hqm endpoint."""
        params = {p: v for p, v in params.items() if v is not None}

        query_str = get_querystring(params, [])
        url = f"http://localhost:8000/api/v1/fred/fixedincome/corporate/hqm?{query_str}"
        result = requests.get(url, headers=headers, timeout=30)
        rows = results_of(result, FredHighQualityMarketCorporateBondData)
        dates = dates_of(rows)

        assert_oldest_first(dates)
        assert all(row["maturity"].startswith("year_") for row in rows)
        assert all(float(row["maturity"][len("year_") :]) > 0 for row in rows)
        assert assert_finite(values_of(rows, "rate"), *PERCENT_BAND)
        assert 1 <= len(set(dates)) <= len(observation_dates(params.get("date")))

        if params.get("date"):
            assert_months(dates, params["date"])

    @pytest.mark.parametrize(
        "params",
        [
            {"provider": "fred"},
            {
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "maturity": "10",
                "category": "spot_rate",
                "provider": "fred",
            },
            {
                "start_date": None,
                "end_date": None,
                "maturity": "1,5.5,10",
                "category": "spot_rate,par_yield",
                "use_cache": False,
                "provider": "fred",
            },
        ],
    )
    @pytest.mark.integration
    def test_spot_rates_are_served(self, params, headers):
        """Test the fixedincome corporate spot_rates endpoint."""
        params = {p: v for p, v in params.items() if v is not None}

        query_str = get_querystring(params, [])
        url = f"http://localhost:8000/api/v1/fred/fixedincome/corporate/spot_rates?{query_str}"
        result = requests.get(url, headers=headers, timeout=30)
        rows = results_of(result, FREDSpotRateData)
        dates = dates_of(rows)
        labels = {"spot_rate": "Spot Rate", "par_yield": "Par Yield"}

        assert_inside_window(dates, params)
        assert assert_finite(values_of(rows, "rate"), *PERCENT_BAND)
        assert all("High Quality Market (HQM)" in row["title"] for row in rows)

        if params.get("maturity"):
            heads = tuple(
                f"{entry}-Year" for entry in str(params["maturity"]).split(",")
            )
            assert all(row["title"].startswith(heads) for row in rows)

        if params.get("category"):
            wanted = {labels[entry] for entry in str(params["category"]).split(",")}
            assert {row["title"].rsplit("Bond ", 1)[-1] for row in rows} == wanted


class TestFixedIncomeGovernment:
    """Test the government bond commands the FRED router serves."""

    @pytest.mark.parametrize(
        "params",
        [
            {"provider": "fred"},
            {
                "maturity": None,
                "start_date": None,
                "end_date": None,
                "transform": None,
                "aggregation_method": None,
                "frequency": None,
                "provider": "fred",
            },
            {
                "maturity": "10",
                "start_date": "2023-01-01",
                "end_date": "2024-01-01",
                "frequency": "m",
                "aggregation_method": "eop",
                "transform": "pc1",
                "use_cache": False,
                "provider": "fred",
            },
        ],
    )
    @pytest.mark.integration
    def test_tips_yields_are_served(self, params, headers):
        """Test the fixedincome government tips_yields endpoint."""
        params = {p: v for p, v in params.items() if v is not None}

        query_str = get_querystring(params, [])
        url = f"http://localhost:8000/api/v1/fred/fixedincome/government/tips_yields?{query_str}"
        result = requests.get(url, headers=headers, timeout=60)
        rows = results_of(result, FredTipsYieldsData)
        dates = dates_of(rows)

        assert_oldest_first(dates)
        assert_inside_window(dates, params)
        assert all(row["symbol"].startswith("DTP") for row in rows)
        assert dates_of(rows, "due")
        assert all(row["name"] for row in rows)
        assert assert_finite(values_of(rows, "value"), *band_for(params, PERCENT_BAND))

        if params.get("maturity"):
            assert all(
                row["symbol"].rsplit("DTP", 1)[-1].startswith(params["maturity"])
                for row in rows
            )

    @pytest.mark.parametrize(
        "params",
        [
            {"provider": "fred"},
            {
                "yield_curve_type": "nominal",
                "date": "2023-05-01,2024-05-01",
                "provider": "fred",
            },
            {
                "yield_curve_type": "real",
                "date": None,
                "use_cache": False,
                "provider": "fred",
            },
        ],
    )
    @pytest.mark.integration
    def test_yield_curve_is_served(self, params, headers):
        """Test the fixedincome government yield_curve endpoint."""
        params = {p: v for p, v in params.items() if v is not None}

        query_str = get_querystring(params, [])
        url = f"http://localhost:8000/api/v1/fred/fixedincome/government/yield_curve?{query_str}"
        result = requests.get(url, headers=headers, timeout=30)
        rows = results_of(result, FREDYieldCurveData)
        dates = dates_of(rows)
        curve = params.get("yield_curve_type", "nominal")
        maturities = set(YIELD_CURVES[curve].values())
        wanted = len(str(params["date"]).split(",")) if params.get("date") else 1
        served = [
            value
            for value in values_of(rows, "rate")
            if value is not None and isfinite(value)
        ]

        assert_oldest_first(dates)
        assert {row["maturity"] for row in rows} <= maturities
        assert len(set(dates)) == wanted
        assert len(rows) == wanted * len({row["maturity"] for row in rows})
        assert served
        assert all(PERCENT_BAND[0] <= value <= PERCENT_BAND[1] for value in served)


class TestFixedIncomeRate:
    """Test the reference rate commands the FRED router serves."""

    @pytest.mark.parametrize(
        "params",
        [
            {"provider": "fred"},
            {
                "maturity": "overnight",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "transform": None,
                "aggregation_method": None,
                "frequency": None,
                "provider": "fred",
            },
            {
                "maturity": "average_30d,term_90d",
                "start_date": "2023-01-01",
                "end_date": "2024-01-01",
                "frequency": "m",
                "aggregation_method": "avg",
                "transform": "pch",
                "use_cache": False,
                "provider": "fred",
            },
        ],
    )
    @pytest.mark.integration
    def test_ameribor_is_served(self, params, headers):
        """Test the fixedincome rate ameribor endpoint."""
        params = {p: v for p, v in params.items() if v is not None}

        query_str = get_querystring(params, [])
        url = f"http://localhost:8000/api/v1/fred/fixedincome/rate/ameribor?{query_str}"
        result = requests.get(url, headers=headers, timeout=30)
        rows = results_of(result, FredAmeriborData)
        dates = dates_of(rows)
        wanted = {
            symbol
            for entry in params.get("maturity", "all").split(",")
            for symbol in MATURITY_TO_FRED_ID[entry].split(",")
        }

        assert_oldest_first(dates)
        assert_inside_window(dates, params)
        assert {row["symbol"] for row in rows} <= wanted
        assert {row["maturity"] for row in rows} <= {"overnight", "day_30", "day_90"}
        assert all(row["title"] for row in rows)
        assert assert_finite(values_of(rows, "rate"), *band_for(params, PERCENT_BAND))

    @pytest.mark.parametrize(
        "params",
        [
            {"provider": "fred"},
            {
                "parameter": "daily_excl_weekend",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "provider": "fred",
            },
            {
                "parameter": "weekly",
                "start_date": "2020-01-01",
                "end_date": "2024-01-01",
                "use_cache": False,
                "provider": "fred",
            },
        ],
    )
    @pytest.mark.integration
    def test_dpcredit_is_served(self, params, headers):
        """Test the fixedincome rate dpcredit endpoint."""
        params = {p: v for p, v in params.items() if v is not None}

        query_str = get_querystring(params, [])
        url = f"http://localhost:8000/api/v1/fred/fixedincome/rate/dpcredit?{query_str}"
        result = requests.get(url, headers=headers, timeout=30)
        rows = results_of(result, FREDDiscountWindowPrimaryCreditRateData)
        dates = dates_of(rows)
        cadence = {"daily_excl_weekend": (1, 4), "weekly": (6, 8)}

        assert_oldest_first(dates)
        assert_inside_window(dates, params)
        assert len(set(dates)) == len(dates)
        assert assert_finite(values_of(rows, "rate"), 0.0, 25.0)

        low, high = cadence[params.get("parameter", "daily_excl_weekend")]
        assert low <= median_gap(dates) <= high

    @pytest.mark.parametrize(
        "params",
        [
            {"provider": "fred"},
            {
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "interest_rate_type": "lending",
                "provider": "fred",
            },
            {
                "start_date": "2020-01-01",
                "end_date": "2024-01-01",
                "interest_rate_type": "deposit",
                "use_cache": False,
                "provider": "fred",
            },
        ],
    )
    @pytest.mark.integration
    def test_ecb_is_served(self, params, headers):
        """Test the fixedincome rate ecb endpoint."""
        params = {p: v for p, v in params.items() if v is not None}

        query_str = get_querystring(params, [])
        url = f"http://localhost:8000/api/v1/fred/fixedincome/rate/ecb?{query_str}"
        result = requests.get(url, headers=headers, timeout=30)
        rows = results_of(result, FREDEuropeanCentralBankInterestRatesData)
        dates = dates_of(rows)

        assert_oldest_first(dates)
        assert_inside_window(dates, params)
        assert len(set(dates)) == len(dates)
        assert assert_finite(values_of(rows, "rate"), -5.0, 25.0)

    @pytest.mark.parametrize(
        "params",
        [
            {"provider": "fred"},
            {
                "frequency": "w",
                "transform": None,
                "aggregation_method": "avg",
                "effr_only": False,
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "provider": "fred",
            },
            {
                "effr_only": True,
                "start_date": "2023-01-01",
                "end_date": "2024-01-01",
                "use_cache": False,
                "provider": "fred",
            },
        ],
    )
    @pytest.mark.integration
    def test_effr_is_served(self, params, headers):
        """Test the fixedincome rate effr endpoint."""
        params = {p: v for p, v in params.items() if v is not None}

        query_str = get_querystring(params, [])
        url = f"http://localhost:8000/api/v1/fred/fixedincome/rate/effr?{query_str}"
        result = requests.get(url, headers=headers, timeout=30)
        rows = results_of(result, FredFederalFundsRateData)
        dates = dates_of(rows)

        assert_oldest_first(dates)
        assert_inside_window(dates, params)
        assert assert_finite(values_of(rows, "rate"), *PERCENT_BAND)

        if params.get("effr_only"):
            assert {row["target_range_upper"] for row in rows} == {None}
            assert {row["volume"] for row in rows} == {None}
        else:
            assert assert_finite(
                values_of(rows, "target_range_upper", "target_range_lower"),
                *PERCENT_BAND,
            )
            assert assert_finite(
                values_of(rows, "volume"), *band_for(params, COUNT_BAND)
            )

    @pytest.mark.parametrize(
        "params",
        [
            {"provider": "fred"},
            {"long_run": False, "provider": "fred"},
            {"long_run": True, "use_cache": False, "provider": "fred"},
        ],
    )
    @pytest.mark.integration
    def test_effr_forecast_is_served(self, params, headers):
        """Test the fixedincome rate effr_forecast endpoint."""
        params = {p: v for p, v in params.items() if v is not None}

        query_str = get_querystring(params, [])
        url = (
            f"http://localhost:8000/api/v1/fred/fixedincome/rate/effr_forecast?"
            f"{query_str}"
        )
        result = requests.get(url, headers=headers, timeout=30)
        rows = results_of(result, FREDPROJECTIONData)
        dates = dates_of(rows)

        assert_oldest_first(dates)
        assert assert_finite(
            values_of(rows, "median", "range_high", "range_low"), -5.0, 25.0
        )
        assert all(
            row["range_low"] <= row["median"] <= row["range_high"]
            for row in rows
            if None not in (row["range_low"], row["median"], row["range_high"])
        )

    @pytest.mark.parametrize(
        "params",
        [
            {"provider": "fred"},
            {
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "transform": None,
                "aggregation_method": None,
                "frequency": None,
                "provider": "fred",
            },
            {
                "start_date": "2023-01-01",
                "end_date": "2024-01-01",
                "frequency": "m",
                "aggregation_method": "avg",
                "transform": "pch",
                "use_cache": False,
                "provider": "fred",
            },
        ],
    )
    @pytest.mark.integration
    def test_estr_is_served(self, params, headers):
        """Test the fixedincome rate estr endpoint."""
        params = {p: v for p, v in params.items() if v is not None}

        query_str = get_querystring(params, [])
        url = f"http://localhost:8000/api/v1/fred/fixedincome/rate/estr?{query_str}"
        result = requests.get(url, headers=headers, timeout=30)
        rows = results_of(result, FredEuroShortTermRateData)
        dates = dates_of(rows)

        assert_oldest_first(dates)
        assert_inside_window(dates, params)
        assert assert_finite(values_of(rows, "rate"), *band_for(params, PERCENT_BAND))
        assert_finite(
            values_of(rows, "number_of_banks"), *band_for(params, (0.0, 1000.0))
        )
        assert_finite(values_of(rows, "transactions"), *band_for(params, COUNT_BAND))

    @pytest.mark.parametrize(
        "params",
        [
            {"provider": "fred"},
            {"start_date": "2023-01-01", "end_date": "2023-06-06", "provider": "fred"},
            {
                "start_date": "2021-01-01",
                "end_date": "2024-01-01",
                "use_cache": False,
                "provider": "fred",
            },
        ],
    )
    @pytest.mark.integration
    def test_iorb_is_served(self, params, headers):
        """Test the fixedincome rate iorb endpoint."""
        params = {p: v for p, v in params.items() if v is not None}

        query_str = get_querystring(params, [])
        url = f"http://localhost:8000/api/v1/fred/fixedincome/rate/iorb?{query_str}"
        result = requests.get(url, headers=headers, timeout=30)
        rows = results_of(result, FREDIORBData)
        dates = dates_of(rows)

        assert_oldest_first(dates)
        assert_inside_window(dates, params)
        assert len(set(dates)) == len(dates)
        assert assert_finite(values_of(rows, "rate"), 0.0, 25.0)

    @pytest.mark.parametrize(
        "params",
        [
            {"provider": "fred"},
            {
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "transform": None,
                "aggregation_method": None,
                "frequency": None,
                "provider": "fred",
            },
            {
                "start_date": "2023-01-01",
                "end_date": "2024-01-01",
                "frequency": "m",
                "aggregation_method": "eop",
                "transform": "chg",
                "use_cache": False,
                "provider": "fred",
            },
        ],
    )
    @pytest.mark.integration
    def test_overnight_bank_funding_is_served(self, params, headers):
        """Test the fixedincome rate overnight_bank_funding endpoint."""
        params = {p: v for p, v in params.items() if v is not None}

        query_str = get_querystring(params, [])
        url = f"http://localhost:8000/api/v1/fred/fixedincome/rate/overnight_bank_funding?{query_str}"
        result = requests.get(url, headers=headers, timeout=30)
        rows = results_of(result, FredOvernightBankFundingRateData)
        dates = dates_of(rows)

        assert_oldest_first(dates)
        assert_inside_window(dates, params)
        assert assert_finite(values_of(rows, "rate"), *band_for(params, PERCENT_BAND))
        assert_finite(
            values_of(rows, "percentile_1", "percentile_99"),
            *band_for(params, PERCENT_BAND),
        )
        assert_finite(values_of(rows, "volume"), *band_for(params, COUNT_BAND))

    @pytest.mark.parametrize(
        "params",
        [
            {"provider": "fred"},
            {
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "frequency": None,
                "transform": None,
                "aggregation_method": None,
                "provider": "fred",
            },
            {
                "start_date": "2023-01-01",
                "end_date": "2024-01-01",
                "frequency": "m",
                "aggregation_method": "avg",
                "transform": "pch",
                "use_cache": False,
                "provider": "fred",
            },
        ],
    )
    @pytest.mark.integration
    def test_sofr_is_served(self, params, headers):
        """Test the fixedincome rate sofr endpoint."""
        params = {p: v for p, v in params.items() if v is not None}

        query_str = get_querystring(params, [])
        url = f"http://localhost:8000/api/v1/fred/fixedincome/rate/sofr?{query_str}"
        result = requests.get(url, headers=headers, timeout=30)
        rows = results_of(result, FREDSOFRData)
        dates = dates_of(rows)

        assert_oldest_first(dates)
        assert_inside_window(dates, params)
        assert assert_finite(values_of(rows, "rate"), *band_for(params, PERCENT_BAND))
        assert_finite(
            values_of(rows, "average_30d", "average_180d"),
            *band_for(params, PERCENT_BAND),
        )
        assert_finite(values_of(rows, "volume"), *band_for(params, COUNT_BAND))

    @pytest.mark.parametrize(
        "params",
        [
            {"provider": "fred"},
            {
                "parameter": "rate",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "provider": "fred",
            },
            {
                "parameter": "index",
                "start_date": "2020-01-01",
                "end_date": "2024-01-01",
                "use_cache": False,
                "provider": "fred",
            },
        ],
    )
    @pytest.mark.integration
    def test_sonia_is_served(self, params, headers):
        """Test the fixedincome rate sonia endpoint."""
        params = {p: v for p, v in params.items() if v is not None}

        query_str = get_querystring(params, [])
        url = f"http://localhost:8000/api/v1/fred/fixedincome/rate/sonia?{query_str}"
        result = requests.get(url, headers=headers, timeout=30)
        rows = results_of(result, FREDSONIAData)
        dates = dates_of(rows)
        rates = values_of(rows, "rate")

        assert_oldest_first(dates)
        assert_inside_window(dates, params)
        assert len(set(dates)) == len(dates)

        if params.get("parameter") == "index":
            assert assert_finite(rates, 0.0, 1.0e6)
        else:
            assert assert_finite(rates, -5.0, 25.0)


class TestFixedIncomeSpreads:
    """Test the rate spread commands the FRED router serves."""

    @pytest.mark.parametrize(
        "params",
        [
            {"provider": "fred"},
            {
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "maturity": "3m",
                "provider": "fred",
            },
            {
                "start_date": "2020-01-01",
                "end_date": "2024-01-01",
                "maturity": "2y",
                "use_cache": False,
                "provider": "fred",
            },
        ],
    )
    @pytest.mark.integration
    def test_tcm_is_served(self, params, headers):
        """Test the fixedincome spreads tcm endpoint."""
        params = {p: v for p, v in params.items() if v is not None}

        query_str = get_querystring(params, [])
        url = f"http://localhost:8000/api/v1/fred/fixedincome/spreads/tcm?{query_str}"
        result = requests.get(url, headers=headers, timeout=30)
        rows = results_of(result, FREDTreasuryConstantMaturityData)
        dates = dates_of(rows)

        assert_oldest_first(dates)
        assert_inside_window(dates, params)
        assert len(set(dates)) == len(dates)
        assert assert_finite(values_of(rows, "rate"), -25.0, 25.0)

    @pytest.mark.parametrize(
        "params",
        [
            {"provider": "fred"},
            {
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "maturity": "10y",
                "provider": "fred",
            },
            {
                "start_date": "2020-01-01",
                "end_date": "2024-01-01",
                "maturity": "6m",
                "use_cache": False,
                "provider": "fred",
            },
        ],
    )
    @pytest.mark.integration
    def test_tcm_effr_is_served(self, params, headers):
        """Test the fixedincome spreads tcm_effr endpoint."""
        params = {p: v for p, v in params.items() if v is not None}

        query_str = get_querystring(params, [])
        url = f"http://localhost:8000/api/v1/fred/fixedincome/spreads/tcm_effr?{query_str}"
        result = requests.get(url, headers=headers, timeout=30)
        rows = results_of(result, FREDSelectedTreasuryConstantMaturityData)
        dates = dates_of(rows)

        assert_oldest_first(dates)
        assert_inside_window(dates, params)
        assert len(set(dates)) == len(dates)
        assert assert_finite(values_of(rows, "rate"), -25.0, 25.0)

    @pytest.mark.parametrize(
        "params",
        [
            {"provider": "fred"},
            {
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "maturity": "3m",
                "provider": "fred",
            },
            {
                "start_date": "2020-01-01",
                "end_date": "2024-01-01",
                "maturity": "6m",
                "use_cache": False,
                "provider": "fred",
            },
        ],
    )
    @pytest.mark.integration
    def test_treasury_effr_is_served(self, params, headers):
        """Test the fixedincome spreads treasury_effr endpoint."""
        params = {p: v for p, v in params.items() if v is not None}

        query_str = get_querystring(params, [])
        url = f"http://localhost:8000/api/v1/fred/fixedincome/spreads/treasury_effr?{query_str}"
        result = requests.get(url, headers=headers, timeout=30)
        rows = results_of(result, FREDSelectedTreasuryBillData)
        dates = dates_of(rows)

        assert_oldest_first(dates)
        assert_inside_window(dates, params)
        assert len(set(dates)) == len(dates)
        assert assert_finite(values_of(rows, "rate"), -25.0, 25.0)
