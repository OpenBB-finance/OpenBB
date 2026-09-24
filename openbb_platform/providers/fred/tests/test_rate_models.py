"""Tests for the FRED reference rate models."""

from datetime import date, datetime

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import run_async

from openbb_fred import FIXEDINCOME_INSTALLED
from openbb_fred.models.ameribor import FredAmeriborFetcher
from openbb_fred.models.dwpcr_rates import (
    FREDDiscountWindowPrimaryCreditRateData,
    FREDDiscountWindowPrimaryCreditRateFetcher,
)
from openbb_fred.models.ecb_interest_rates import (
    FREDEuropeanCentralBankInterestRatesData,
    FREDEuropeanCentralBankInterestRatesFetcher,
)
from openbb_fred.models.euro_short_term_rate import FredEuroShortTermRateFetcher
from openbb_fred.models.fed_projections import FREDPROJECTIONFetcher
from openbb_fred.models.federal_funds_rate import FredFederalFundsRateFetcher
from openbb_fred.models.ffrmc import (
    FREDSelectedTreasuryConstantMaturityData,
    FREDSelectedTreasuryConstantMaturityFetcher,
)
from openbb_fred.models.iorb_rates import FREDIORBData, FREDIORBFetcher
from openbb_fred.models.overnight_bank_funding_rate import (
    FredOvernightBankFundingRateFetcher,
)
from openbb_fred.models.series import (
    FredSeriesData,
    FredSeriesFetcher,
    FredSeriesQueryParams,
)
from openbb_fred.models.sofr import FREDSOFRFetcher
from openbb_fred.models.sonia_rates import FREDSONIAData, FREDSONIAFetcher
from openbb_fred.models.tbffr import (
    FREDSelectedTreasuryBillData,
    FREDSelectedTreasuryBillFetcher,
)
from openbb_fred.models.tmc import (
    FREDTreasuryConstantMaturityData,
    FREDTreasuryConstantMaturityFetcher,
)
from openbb_fred.utils.api import observations_url

CREDENTIALS = {"fred_api_key": "test-key"}

OBSERVATIONS = [
    {
        "realtime_start": "2024-01-02",
        "realtime_end": "2024-01-02",
        "date": "2024-01-02",
        "value": "5.33",
    },
    {
        "realtime_start": "2024-01-03",
        "realtime_end": "2024-01-03",
        "date": "2024-01-03",
        "value": ".",
    },
]

VALUE_MODELS = (
    FREDDiscountWindowPrimaryCreditRateData,
    FREDEuropeanCentralBankInterestRatesData,
    FREDIORBData,
    FREDSONIAData,
    FREDSelectedTreasuryBillData,
    FREDSelectedTreasuryConstantMaturityData,
    FREDTreasuryConstantMaturityData,
)

WHOLE_RECORD_FETCHERS = (
    FREDDiscountWindowPrimaryCreditRateFetcher,
    FREDSelectedTreasuryBillFetcher,
    FREDSelectedTreasuryConstantMaturityFetcher,
    FREDTreasuryConstantMaturityFetcher,
)

OBSERVATION_FETCHERS = WHOLE_RECORD_FETCHERS + (
    FREDEuropeanCentralBankInterestRatesFetcher,
    FREDIORBFetcher,
    FREDSONIAFetcher,
)

SERIES_BACKED_FETCHERS = (
    FredAmeriborFetcher,
    FredEuroShortTermRateFetcher,
    FredFederalFundsRateFetcher,
    FredOvernightBankFundingRateFetcher,
    FREDSOFRFetcher,
)

SHORT_RUN_PROJECTION_IDS = [
    "FEDTARRH",
    "FEDTARCTH",
    "FEDTARMD",
    "FEDTARRM",
    "FEDTARCTM",
    "FEDTARRL",
    "FEDTARCTL",
]

LONG_RUN_PROJECTION_IDS = [
    "FEDTARRHLR",
    "FEDTARCTHLR",
    "FEDTARMDLR",
    "FEDTARRMLR",
    "FEDTARCTMLR",
    "FEDTARRLLR",
    "FEDTARCTLLR",
]

AMERIBOR_ROWS = [
    {
        "date": date(2024, 1, 2),
        "AMERIBOR": 5.0,
        "AMBOR30": 5.25,
        "AMBOR90": None,
    },
    {
        "date": date(2024, 1, 3),
        "AMERIBOR": 5.1,
        "AMBOR30": None,
        "AMBOR90": 5.5,
    },
]

AMERIBOR_METADATA = {
    "AMERIBOR": {"title": "Overnight AMERIBOR Benchmark Interest Rate"},
    "AMBOR90T": {"title": "90-Day Term AMERIBOR"},
}

ESTR_ROWS = [
    {
        "date": date(2024, 1, 2),
        "ECBESTRVOLWGTTRMDMNRT": 3.65,
        "ECBESTRNUMTRANS": 1234,
        "ECBESTRNUMACTBANKS": 45,
        "ECBESTRTOTVOL": 52000.0,
        "ECBESTRSHRVOL5LRGACTBNK": 48.0,
        "ECBESTRRT75THPCTVOL": 5.0,
        "ECBESTRRT25THPCTVOL": 2.5,
    },
    {
        "date": date(2024, 1, 3),
        "ECBESTRVOLWGTTRMDMNRT": None,
        "ECBESTRNUMTRANS": 1000,
    },
]

ESTR_METADATA = {
    "ECBESTRVOLWGTTRMDMNRT": {"title": "Euro Short-Term Rate"},
    "ECBESTRTOTVOL": {"title": "Euro Short-Term Rate: Total Volume"},
}

EFFR_ROWS = [
    {
        "date": date(2024, 1, 2),
        "DFF": 5.33,
        "DFEDTARU": 5.5,
        "DFEDTARL": 5.25,
        "EFFR1": 5.0,
        "EFFR25": 5.1,
        "EFFR75": 5.33,
        "EFFR99": 5.5,
        "EFFRVOL": 95.0,
    },
    {
        "date": date(2024, 1, 3),
        "DFF": 5.33,
        "DFEDTARU": 5.5,
        "DFEDTARL": 5.25,
        "EFFR1": 5.0,
        "EFFR25": 5.1,
        "EFFR75": 5.33,
        "EFFR99": None,
        "EFFRVOL": 95.0,
    },
]

EFFR_METADATA = {
    "DFF": {"title": "Federal Funds Effective Rate"},
    "EFFRVOL": {"title": "Federal Funds Volume"},
}

OBFR_ROWS = [
    {
        "date": date(2024, 1, 2),
        "OBFR": 5.25,
        "OBFR1": 5.0,
        "OBFR25": 5.1,
        "OBFR75": 5.33,
        "OBFR99": 5.5,
        "OBFRVOL": 95.0,
    },
    {"date": date(2024, 1, 3), "OBFR": None, "OBFRVOL": 90.0},
]

OBFR_METADATA = {
    "OBFR": {"title": "Overnight Bank Funding Rate"},
    "OBFRVOL": {"title": "Overnight Bank Funding Volume"},
}

SOFR_ROWS = [
    {
        "date": date(2024, 1, 2),
        "SOFR": 5.33,
        "SOFR1": 5.0,
        "SOFR25": 5.1,
        "SOFR75": 5.25,
        "SOFR99": 5.5,
        "SOFRVOL": 1800.0,
        "SOFR30DAYAVG": 4.33,
        "SOFR90DAYAVG": 4.0,
        "SOFR180DAYAVG": 2.5,
        "SOFRINDEX": 1.15,
    },
    {"date": date(2024, 1, 3), "SOFR": None, "SOFRINDEX": 1.16},
]

SOFR_METADATA = {
    "SOFR": {"title": "Secured Overnight Financing Rate"},
    "SOFRVOL": {"title": "Secured Overnight Financing Volume"},
}

DISTRIBUTIONS = {
    "estr": (FredEuroShortTermRateFetcher, ESTR_ROWS, ESTR_METADATA),
    "effr": (FredFederalFundsRateFetcher, EFFR_ROWS, EFFR_METADATA),
    "obfr": (FredOvernightBankFundingRateFetcher, OBFR_ROWS, OBFR_METADATA),
    "sofr": (FREDSOFRFetcher, SOFR_ROWS, SOFR_METADATA),
}

RATE_WIDGETS = {
    "ameribor": "fixedincome_rate_ameribor_fred_obb",
    "dpcredit": "fixedincome_rate_dpcredit_fred_obb",
    "ecb": "fixedincome_rate_ecb_fred_obb",
    "effr": "fixedincome_rate_effr_fred_obb",
    "effr_forecast": "fixedincome_rate_effr_forecast_fred_obb",
    "estr": "fixedincome_rate_estr_fred_obb",
    "iorb": "fixedincome_rate_iorb_fred_obb",
    "obfr": "fixedincome_rate_overnight_bank_funding_fred_obb",
    "sofr": "fixedincome_rate_sofr_fred_obb",
    "sonia": "fixedincome_rate_sonia_fred_obb",
    "tcm": "fixedincome_spreads_tcm_fred_obb",
    "tcm_effr": "fixedincome_spreads_tcm_effr_fred_obb",
    "treasury_effr": "fixedincome_spreads_treasury_effr_fred_obb",
}

PLOTTED_FIELDS = {
    "ameribor": ["rate"],
    "dpcredit": ["rate"],
    "ecb": ["rate"],
    "effr": [
        "rate",
        "target_range_upper",
        "target_range_lower",
        "percentile_1",
        "percentile_25",
        "percentile_75",
        "percentile_99",
    ],
    "effr_forecast": [
        "range_high",
        "central_tendency_high",
        "median",
        "range_midpoint",
        "central_tendency_midpoint",
        "range_low",
        "central_tendency_low",
    ],
    "estr": ["rate", "percentile_25", "percentile_75"],
    "iorb": ["rate"],
    "obfr": [
        "rate",
        "percentile_1",
        "percentile_25",
        "percentile_75",
        "percentile_99",
    ],
    "sofr": [
        "rate",
        "percentile_1",
        "percentile_25",
        "percentile_75",
        "percentile_99",
        "average_30d",
        "average_90d",
        "average_180d",
    ],
    "sonia": ["rate"],
    "tcm": ["rate"],
    "tcm_effr": ["rate"],
    "treasury_effr": ["rate"],
}

UNPLOTTED_FIELDS = {
    "ameribor": ["maturity", "title"],
    "effr": ["volume"],
    "estr": [
        "volume",
        "transactions",
        "number_of_banks",
        "large_bank_share_of_volume",
    ],
    "obfr": ["volume"],
    "sofr": ["volume", "index"],
}

PLOTTED_COLUMNS = [
    (widget, field) for widget, fields in PLOTTED_FIELDS.items() for field in fields
]

UNPLOTTED_COLUMNS = [
    (widget, field) for widget, fields in UNPLOTTED_FIELDS.items() for field in fields
]

fixedincome_owned = pytest.mark.skipif(
    FIXEDINCOME_INSTALLED,
    reason="openbb_fixedincome owns the rate and spread commands when it is importable,"
    " so this package does not publish their widgets",
)


class _Reader:
    """Stand in for the single-series FRED reader, and remember its calls."""

    def __init__(self, answer=None):
        self.answer = OBSERVATIONS if answer is None else answer
        self.calls: list = []

    async def __call__(self, *args, **kwargs):
        """Answer one read."""
        self.calls.append((args, kwargs))

        return self.answer

    @property
    def series_id(self):
        """The series the first read asked for."""
        return self.calls[0][0][0]

    @property
    def api_key(self):
        """The key the first read carried."""
        return self.calls[0][0][1]

    @property
    def url(self):
        """The signed URL the first read would have been sent to."""
        args, kwargs = self.calls[0]

        return observations_url(*args, **kwargs)


class _ManyReader:
    """Stand in for the many-series FRED reader, and remember its calls."""

    def __init__(self, answers: dict):
        self.answers = answers
        self.calls: list = []

    async def __call__(self, series_ids, api_key, **kwargs):
        """Answer one read."""
        self.calls.append((list(series_ids), api_key, kwargs))

        return [self.answers.get(series_id, []) for series_id in series_ids]


def _reads(monkeypatch, answer=None) -> _Reader:
    """Put a recording reader in front of ``get_observations``."""
    reader = _Reader(answer)
    monkeypatch.setattr("openbb_fred.utils.api.get_observations", reader)

    return reader


def _series(monkeypatch, rows, metadata=None) -> list:
    """Put a recording stand-in in front of ``FredSeriesFetcher``."""
    asked: list = []

    async def answer(params, credentials):
        asked.append((params, credentials))

        return AnnotatedResult(
            result=[FredSeriesData.model_validate(row) for row in rows],
            metadata=metadata or {},
        )

    monkeypatch.setattr(
        "openbb_fred.models.series.FredSeriesFetcher.fetch_data", answer
    )

    return asked


def _refuses(monkeypatch, error: Exception) -> None:
    """Make every read of the underlying series fail."""

    async def answer(params, credentials):
        raise error

    monkeypatch.setattr(
        "openbb_fred.models.series.FredSeriesFetcher.fetch_data", answer
    )


def _distribution(monkeypatch, name: str):
    """Read one distribution-style rate model from its recorded payload."""
    fetcher, rows, metadata = DISTRIBUTIONS[name]
    _series(monkeypatch, rows, metadata)

    return run_async(fetcher.fetch_data, {}, CREDENTIALS)


class TestMissingObservationValue:
    """FRED writes an observation it has no value for as a lone period."""

    @pytest.mark.parametrize("model", VALUE_MODELS)
    def test_a_period_reads_as_no_rate(self, model):
        assert model.model_validate({"date": "2024-01-02", "value": "."}).rate is None

    @pytest.mark.parametrize("model", VALUE_MODELS)
    def test_an_empty_value_reads_as_no_rate(self, model):
        assert model.model_validate({"date": "2024-01-02", "value": ""}).rate is None

    @pytest.mark.parametrize("model", VALUE_MODELS)
    def test_a_written_number_reads_as_a_rate(self, model):
        row = model.model_validate({"date": "2024-01-02", "value": "5.33"})

        assert row.rate == 5.33

    @pytest.mark.parametrize("model", VALUE_MODELS)
    def test_the_published_percent_is_passed_through_unscaled(self, model):
        """These series carry a percent, and it reaches the caller as written."""
        row = model.model_validate({"date": "2024-01-02", "value": "0.05"})

        assert row.rate == 0.05


class TestSeriesSelection:
    """Which FRED series each rate model reads."""

    async def test_the_discount_window_reads_business_days_by_default(
        self, monkeypatch
    ):
        reader = _reads(monkeypatch)

        await FREDDiscountWindowPrimaryCreditRateFetcher.fetch_data({}, CREDENTIALS)

        assert reader.series_id == "DPCREDIT"

    @pytest.mark.parametrize(
        ("parameter", "series_id"),
        [
            ("daily_excl_weekend", "DPCREDIT"),
            ("monthly", "MPCREDIT"),
            ("weekly", "WPCREDIT"),
            ("daily", "RIFSRPF02ND"),
            ("annual", "RIFSRPF02NA"),
        ],
    )
    async def test_the_discount_window_parameter_picks_the_series(
        self, monkeypatch, parameter, series_id
    ):
        reader = _reads(monkeypatch)

        await FREDDiscountWindowPrimaryCreditRateFetcher.fetch_data(
            {"parameter": parameter}, CREDENTIALS
        )

        assert reader.series_id == series_id

    async def test_the_ecb_reads_the_lending_rate_by_default(self, monkeypatch):
        reader = _reads(monkeypatch)

        await FREDEuropeanCentralBankInterestRatesFetcher.fetch_data({}, CREDENTIALS)

        assert reader.series_id == "ECBMLFR"

    @pytest.mark.parametrize(
        ("interest_rate_type", "series_id"),
        [
            ("deposit", "ECBDFR"),
            ("lending", "ECBMLFR"),
            ("refinancing", "ECBMRRFR"),
        ],
    )
    async def test_the_ecb_rate_type_picks_the_series(
        self, monkeypatch, interest_rate_type, series_id
    ):
        reader = _reads(monkeypatch)

        await FREDEuropeanCentralBankInterestRatesFetcher.fetch_data(
            {"interest_rate_type": interest_rate_type}, CREDENTIALS
        )

        assert reader.series_id == series_id

    async def test_interest_on_reserve_balances_is_a_single_series(self, monkeypatch):
        reader = _reads(monkeypatch)

        await FREDIORBFetcher.fetch_data({}, CREDENTIALS)

        assert reader.series_id == "IORB"

    async def test_sonia_reads_the_rate_itself_by_default(self, monkeypatch):
        reader = _reads(monkeypatch)

        await FREDSONIAFetcher.fetch_data({}, CREDENTIALS)

        assert reader.series_id == "IUDSOIA"

    @pytest.mark.parametrize(
        ("parameter", "series_id"),
        [
            ("rate", "IUDSOIA"),
            ("index", "IUDZOS2"),
            ("10th_percentile", "IUDZLS6"),
            ("25th_percentile", "IUDZLS7"),
            ("75th_percentile", "IUDZLS8"),
            ("90th_percentile", "IUDZLS9"),
            ("total_nominal_value", "IUDZLT2"),
        ],
    )
    async def test_the_sonia_parameter_picks_the_series(
        self, monkeypatch, parameter, series_id
    ):
        reader = _reads(monkeypatch)

        await FREDSONIAFetcher.fetch_data({"parameter": parameter}, CREDENTIALS)

        assert reader.series_id == series_id

    @pytest.mark.parametrize(
        ("maturity", "series_id"), [("3m", "TB3SMFFM"), ("6m", "TB6SMFFM")]
    )
    async def test_the_bill_spread_maturity_picks_the_series(
        self, monkeypatch, maturity, series_id
    ):
        reader = _reads(monkeypatch)

        await FREDSelectedTreasuryBillFetcher.fetch_data(
            {"maturity": maturity}, CREDENTIALS
        )

        assert reader.series_id == series_id

    async def test_the_bill_spread_falls_back_to_three_months(self, monkeypatch):
        """``maturity`` accepts None, and the model still names a series."""
        reader = _reads(monkeypatch)

        await FREDSelectedTreasuryBillFetcher.fetch_data(
            {"maturity": None}, CREDENTIALS
        )

        assert reader.series_id == "TB3SMFFM"

    @pytest.mark.parametrize(
        ("maturity", "series_id"), [("3m", "T10Y3M"), ("2y", "T10Y2Y")]
    )
    async def test_the_constant_maturity_spread_picks_the_series(
        self, monkeypatch, maturity, series_id
    ):
        reader = _reads(monkeypatch)

        await FREDTreasuryConstantMaturityFetcher.fetch_data(
            {"maturity": maturity}, CREDENTIALS
        )

        assert reader.series_id == series_id

    async def test_the_constant_maturity_spread_falls_back_to_three_months(
        self, monkeypatch
    ):
        reader = _reads(monkeypatch)

        await FREDTreasuryConstantMaturityFetcher.fetch_data(
            {"maturity": None}, CREDENTIALS
        )

        assert reader.series_id == "T10Y3M"

    @pytest.mark.parametrize(
        ("maturity", "series_id"),
        [
            ("10y", "T10YFF"),
            ("5y", "T5YFF"),
            ("1y", "T1YFF"),
            ("6m", "T6MFF"),
            ("3m", "T3MFF"),
        ],
    )
    async def test_the_funds_rate_spread_maturity_picks_the_series(
        self, monkeypatch, maturity, series_id
    ):
        reader = _reads(monkeypatch)

        await FREDSelectedTreasuryConstantMaturityFetcher.fetch_data(
            {"maturity": maturity}, CREDENTIALS
        )

        assert reader.series_id == series_id

    async def test_the_funds_rate_spread_falls_back_to_ten_years(self, monkeypatch):
        reader = _reads(monkeypatch)

        await FREDSelectedTreasuryConstantMaturityFetcher.fetch_data(
            {"maturity": None}, CREDENTIALS
        )

        assert reader.series_id == "T10YFF"


class TestRequestParameters:
    """What each read of a single series carries to the transport."""

    @pytest.mark.parametrize("fetcher", OBSERVATION_FETCHERS)
    async def test_the_key_reaches_the_transport(self, monkeypatch, fetcher):
        reader = _reads(monkeypatch)

        await fetcher.fetch_data({}, CREDENTIALS)

        assert reader.api_key == "test-key"
        assert "api_key=test-key" in reader.url

    @pytest.mark.parametrize("fetcher", OBSERVATION_FETCHERS)
    async def test_a_request_without_credentials_carries_no_key(
        self, monkeypatch, fetcher
    ):
        reader = _reads(monkeypatch)

        await fetcher.fetch_data({}, None)

        assert reader.api_key is None
        assert "api_key=&" in reader.url

    @pytest.mark.parametrize("fetcher", OBSERVATION_FETCHERS)
    async def test_the_dates_reach_fred_as_the_observation_window(
        self, monkeypatch, fetcher
    ):
        """FRED names the window ``observation_start`` and ``observation_end``."""
        reader = _reads(monkeypatch)

        await fetcher.fetch_data(
            {"start_date": date(2024, 1, 1), "end_date": date(2024, 1, 31)},
            CREDENTIALS,
        )

        assert "observation_start=2024-01-01" in reader.url
        assert "observation_end=2024-01-31" in reader.url

    @pytest.mark.parametrize("fetcher", OBSERVATION_FETCHERS)
    async def test_a_request_without_dates_asks_for_the_whole_history(
        self, monkeypatch, fetcher
    ):
        """An unasked-for window is left off the request rather than guessed at."""
        reader = _reads(monkeypatch)

        await fetcher.fetch_data({}, CREDENTIALS)

        assert "observation_start" not in reader.url
        assert "observation_end" not in reader.url

    @pytest.mark.parametrize("fetcher", OBSERVATION_FETCHERS)
    async def test_the_cache_switch_reaches_the_transport(self, monkeypatch, fetcher):
        """Reads are cached unless the request turns the cache off."""
        reader = _reads(monkeypatch)

        await fetcher.fetch_data({}, CREDENTIALS)
        await fetcher.fetch_data({"use_cache": False}, CREDENTIALS)

        assert [call[1]["use_cache"] for call in reader.calls] == [True, False]


class TestObservationRows:
    """The rows the single-series rate models hand back."""

    @pytest.mark.parametrize("fetcher", OBSERVATION_FETCHERS)
    async def test_every_observation_becomes_a_row(self, monkeypatch, fetcher):
        _reads(monkeypatch)

        rows = await fetcher.fetch_data({}, CREDENTIALS)

        assert [row.date for row in rows] == [date(2024, 1, 2), date(2024, 1, 3)]

    @pytest.mark.parametrize("fetcher", OBSERVATION_FETCHERS)
    async def test_a_missing_observation_keeps_its_date(self, monkeypatch, fetcher):
        """A period FRED has no value for is a row with no rate, not a gap."""
        _reads(monkeypatch)

        rows = await fetcher.fetch_data({}, CREDENTIALS)

        assert [row.rate for row in rows] == [5.33, None]

    @pytest.mark.parametrize("fetcher", (FREDIORBFetcher, FREDSONIAFetcher))
    async def test_only_the_date_and_the_rate_are_published(self, monkeypatch, fetcher):
        _reads(monkeypatch)

        rows = await fetcher.fetch_data({}, CREDENTIALS)

        assert set(rows[0].model_dump()) == {"date", "rate"}

    @pytest.mark.parametrize("fetcher", WHOLE_RECORD_FETCHERS)
    async def test_the_record_keeps_the_fields_fred_sent(self, monkeypatch, fetcher):
        """These models validate the whole observation, vintage stamps included."""
        _reads(monkeypatch)

        rows = await fetcher.fetch_data({}, CREDENTIALS)

        assert set(rows[0].model_dump()) == {
            "date",
            "rate",
            "realtime_start",
            "realtime_end",
        }


class TestAmeriborSeriesSelection:
    """Which AMERIBOR series a maturity resolves to."""

    async def test_every_maturity_is_read_by_default(self, monkeypatch):
        asked = _series(monkeypatch, [{"date": date(2024, 1, 2), "AMERIBOR": 5.0}])

        await FredAmeriborFetcher.fetch_data({}, CREDENTIALS)

        assert asked[0][0]["symbol"] == ("AMERIBOR,AMBOR30,AMBOR90,AMBOR30T,AMBOR90T")

    @pytest.mark.parametrize(
        ("maturity", "symbol"),
        [
            ("overnight", "AMERIBOR"),
            ("average_30d", "AMBOR30"),
            ("average_90d", "AMBOR90"),
            ("term_30d", "AMBOR30T"),
            ("term_90d", "AMBOR90T"),
        ],
    )
    async def test_one_maturity_reads_one_series(self, monkeypatch, maturity, symbol):
        asked = _series(monkeypatch, [{"date": date(2024, 1, 2), "AMERIBOR": 5.0}])

        await FredAmeriborFetcher.fetch_data({"maturity": maturity}, CREDENTIALS)

        assert asked[0][0]["symbol"] == symbol

    async def test_several_maturities_read_several_series(self, monkeypatch):
        asked = _series(monkeypatch, [{"date": date(2024, 1, 2), "AMERIBOR": 5.0}])

        await FredAmeriborFetcher.fetch_data(
            {"maturity": "overnight,term_30d"}, CREDENTIALS
        )

        assert asked[0][0]["symbol"] == "AMERIBOR,AMBOR30T"

    async def test_the_maturities_are_read_in_the_order_asked_for(self, monkeypatch):
        asked = _series(monkeypatch, [{"date": date(2024, 1, 2), "AMERIBOR": 5.0}])

        await FredAmeriborFetcher.fetch_data(
            {"maturity": "term_90d,overnight"}, CREDENTIALS
        )

        assert asked[0][0]["symbol"] == "AMBOR90T,AMERIBOR"

    async def test_all_alongside_a_maturity_still_reads_every_series(self, monkeypatch):
        """'all' names the whole set, so it absorbs whatever it is listed with."""
        asked = _series(monkeypatch, [{"date": date(2024, 1, 2), "AMERIBOR": 5.0}])

        await FredAmeriborFetcher.fetch_data({"maturity": "overnight,all"}, CREDENTIALS)

        assert asked[0][0]["symbol"] == ("AMERIBOR,AMBOR30,AMBOR90,AMBOR30T,AMBOR90T")

    async def test_the_query_names_only_fields_the_series_read_takes(self, monkeypatch):
        """``maturity`` is spent resolving the series ids, and is not forwarded."""
        asked = _series(monkeypatch, [{"date": date(2024, 1, 2), "AMERIBOR": 5.0}])

        await FredAmeriborFetcher.fetch_data({"maturity": "overnight"}, CREDENTIALS)

        assert set(asked[0][0]) <= set(FredSeriesQueryParams.model_fields)

    async def test_the_query_reaches_fred_under_its_own_parameter_names(
        self, monkeypatch
    ):
        """The resolved series ids, and every pass-through, as FRED reads them."""
        asked = _series(monkeypatch, [{"date": date(2024, 1, 2), "AMERIBOR": 5.0}])

        await FredAmeriborFetcher.fetch_data(
            {
                "maturity": "term_90d,overnight",
                "start_date": date(2024, 1, 1),
                "end_date": date(2024, 1, 31),
                "frequency": "m",
                "aggregation_method": "avg",
                "transform": "chg",
                "use_cache": False,
            },
            CREDENTIALS,
        )
        sent = FredSeriesFetcher.transform_query(asked[0][0]).model_dump(
            exclude_none=True
        )

        assert sent == {
            "series_id": "AMBOR90T,AMERIBOR",
            "observation_start": date(2024, 1, 1),
            "observation_end": date(2024, 1, 31),
            "frequency": "m",
            "aggregation_method": "avg",
            "units": "chg",
            "limit": 100000,
            "use_cache": False,
        }

    @pytest.mark.parametrize("credentials", [CREDENTIALS, None])
    async def test_the_credentials_are_handed_to_the_series_read(
        self, monkeypatch, credentials
    ):
        asked = _series(monkeypatch, [{"date": date(2024, 1, 2), "AMERIBOR": 5.0}])

        await FredAmeriborFetcher.fetch_data({}, credentials)

        assert asked[0][1] == credentials


class TestAmeriborRows:
    """The rows AMERIBOR hands back."""

    @pytest.fixture
    def rows(self, monkeypatch):
        _series(monkeypatch, AMERIBOR_ROWS, AMERIBOR_METADATA)

        return run_async(FredAmeriborFetcher.fetch_data, {}, CREDENTIALS)

    def test_the_published_percent_is_passed_through_unscaled(self, rows):
        assert [row.rate for row in rows.result] == [5.0, 5.25, 5.1, 5.5]

    def test_a_series_with_no_value_that_day_is_dropped(self, rows):
        assert len(rows.result) == 4

    def test_each_series_reads_as_its_maturity(self, rows):
        assert [row.maturity for row in rows.result] == [
            "overnight",
            "day_30",
            "overnight",
            "day_90",
        ]

    def test_the_series_of_a_day_run_from_the_shortest_maturity(self, rows):
        assert [(row.date, row.symbol) for row in rows.result] == [
            (date(2024, 1, 2), "AMERIBOR"),
            (date(2024, 1, 2), "AMBOR30"),
            (date(2024, 1, 3), "AMERIBOR"),
            (date(2024, 1, 3), "AMBOR90"),
        ]

    def test_a_row_carries_the_title_of_its_series(self, rows):
        assert rows.result[0].title == "Overnight AMERIBOR Benchmark Interest Rate"

    def test_a_series_without_a_title_is_named_by_its_id(self, rows):
        assert rows.result[1].title == "AMBOR30"

    def test_the_metadata_of_a_series_with_no_rows_is_still_published(self, rows):
        """AMBOR90T was read and described, but published no value in this window."""
        assert set(rows.metadata) == {"AMERIBOR", "AMBOR90T"}
        assert set(rows.metadata).isdisjoint(type(rows.result[0]).model_fields)

    async def test_the_term_series_share_the_average_maturities(self, monkeypatch):
        """The term and average series of a tenor read as the same maturity."""
        _series(
            monkeypatch,
            [{"date": date(2024, 1, 2), "AMBOR30T": 5.25, "AMBOR90T": 5.5}],
        )

        result = await FredAmeriborFetcher.fetch_data(
            {"maturity": "term_30d,term_90d"}, CREDENTIALS
        )

        assert [row.maturity for row in result.result] == ["day_30", "day_90"]


class TestSeriesBackedRequests:
    """What the rate models built on the FRED series read ask that read for."""

    @pytest.mark.parametrize(
        ("name", "series_ids"),
        [
            (
                "estr",
                [
                    "ECBESTRVOLWGTTRMDMNRT",
                    "ECBESTRNUMTRANS",
                    "ECBESTRNUMACTBANKS",
                    "ECBESTRTOTVOL",
                    "ECBESTRSHRVOL5LRGACTBNK",
                    "ECBESTRRT75THPCTVOL",
                    "ECBESTRRT25THPCTVOL",
                ],
            ),
            (
                "effr",
                [
                    "DFF",
                    "DFEDTARU",
                    "DFEDTARL",
                    "EFFR1",
                    "EFFR25",
                    "EFFR75",
                    "EFFR99",
                    "EFFRVOL",
                ],
            ),
            (
                "obfr",
                ["OBFR", "OBFR1", "OBFR25", "OBFR75", "OBFR99", "OBFRVOL"],
            ),
            (
                "sofr",
                [
                    "SOFR",
                    "SOFR1",
                    "SOFR25",
                    "SOFR75",
                    "SOFR99",
                    "SOFRVOL",
                    "SOFR30DAYAVG",
                    "SOFR90DAYAVG",
                    "SOFR180DAYAVG",
                    "SOFRINDEX",
                ],
            ),
        ],
    )
    async def test_every_component_series_is_read(self, monkeypatch, name, series_ids):
        fetcher, rows, metadata = DISTRIBUTIONS[name]
        asked = _series(monkeypatch, rows, metadata)

        await fetcher.fetch_data({}, CREDENTIALS)

        assert asked[0][0]["symbol"].split(",") == series_ids

    @pytest.mark.parametrize(
        ("name", "start_date"), [("estr", "2019-10-02"), ("sofr", "2018-04-02")]
    )
    async def test_the_read_starts_when_the_rate_was_first_published(
        self, monkeypatch, name, start_date
    ):
        fetcher, rows, metadata = DISTRIBUTIONS[name]
        asked = _series(monkeypatch, rows, metadata)

        await fetcher.fetch_data({}, CREDENTIALS)

        assert asked[0][0]["start_date"] == start_date

    @pytest.mark.parametrize("name", ["estr", "sofr"])
    async def test_an_asked_for_start_date_is_kept(self, monkeypatch, name):
        """The first-publication date is a fallback, not an override."""
        fetcher, rows, metadata = DISTRIBUTIONS[name]
        asked = _series(monkeypatch, rows, metadata)

        await fetcher.fetch_data({"start_date": date(2024, 1, 1)}, CREDENTIALS)

        assert asked[0][0]["start_date"] == date(2024, 1, 1)

    async def test_the_effective_rate_on_its_own_reads_one_series(self, monkeypatch):
        asked = _series(monkeypatch, [{"date": date(2024, 1, 2), "DFF": 5.33}])

        await FredFederalFundsRateFetcher.fetch_data({"effr_only": True}, CREDENTIALS)

        assert asked[0][0]["symbol"] == "DFF"


class TestDistributionRows:
    """The rows the rate models that publish a whole distribution hand back."""

    @pytest.mark.parametrize("name", list(DISTRIBUTIONS))
    def test_a_day_without_a_complete_reading_is_dropped(self, monkeypatch, name):
        rows = _distribution(monkeypatch, name)

        assert [row.date for row in rows.result] == [date(2024, 1, 2)]

    @pytest.mark.parametrize(
        ("name", "rate"),
        [("estr", 3.65), ("effr", 5.33), ("obfr", 5.25), ("sofr", 5.33)],
    )
    def test_the_published_rate_is_passed_through_unscaled(
        self, monkeypatch, name, rate
    ):
        rows = _distribution(monkeypatch, name)

        assert rows.result[0].rate == rate

    @pytest.mark.parametrize(
        ("name", "volume"),
        [("estr", 52000.0), ("effr", 95.0), ("obfr", 95.0), ("sofr", 1800.0)],
    )
    def test_the_published_volume_is_passed_through_unscaled(
        self, monkeypatch, name, volume
    ):
        """Volume is an amount rather than a percent, and it too is left as written."""
        rows = _distribution(monkeypatch, name)

        assert rows.result[0].volume == volume

    @pytest.mark.parametrize(
        ("name", "quantiles"),
        [
            ("effr", [5.0, 5.1, 5.33, 5.5]),
            ("obfr", [5.0, 5.1, 5.33, 5.5]),
            ("sofr", [5.0, 5.1, 5.25, 5.5]),
        ],
    )
    def test_the_published_quantiles_are_passed_through_unscaled(
        self, monkeypatch, name, quantiles
    ):
        rows = _distribution(monkeypatch, name)
        row = rows.result[0]

        assert [
            row.percentile_1,
            row.percentile_25,
            row.percentile_75,
            row.percentile_99,
        ] == quantiles

    @pytest.mark.parametrize("name", ["estr", "obfr", "sofr"])
    def test_the_metadata_stays_keyed_by_the_fred_series_id(self, monkeypatch, name):
        rows = _distribution(monkeypatch, name)

        assert set(rows.metadata) == set(DISTRIBUTIONS[name][2])
        assert set(rows.metadata).isdisjoint(type(rows.result[0]).model_fields)


class TestEuroShortTermRateRows:
    """The rows the euro short term rate hands back."""

    @pytest.fixture
    def rows(self, monkeypatch):
        return _distribution(monkeypatch, "estr")

    def test_the_published_percentiles_are_passed_through_unscaled(self, rows):
        assert (rows.result[0].percentile_25, rows.result[0].percentile_75) == (
            2.5,
            5.0,
        )

    def test_the_published_large_bank_share_is_passed_through_unscaled(self, rows):
        assert rows.result[0].large_bank_share_of_volume == 48.0

    def test_the_published_counts_are_passed_through_unscaled(self, rows):
        """A transaction count is not a percent, and it too is left as written."""
        assert (rows.result[0].transactions, rows.result[0].number_of_banks) == (
            1234,
            45,
        )


class TestFederalFundsRateQuery:
    """The dates a federal funds rate request is given when it names none."""

    def test_the_request_ends_today(self):
        query = FredFederalFundsRateFetcher.transform_query({})

        assert query.end_date == datetime.now().date()

    def test_an_asked_for_end_date_is_kept(self):
        query = FredFederalFundsRateFetcher.transform_query(
            {"end_date": date(2024, 1, 31)}
        )

        assert query.end_date == date(2024, 1, 31)

    def test_the_full_set_starts_where_the_quantiles_start(self):
        """The quantile and volume series only begin in 2016."""
        query = FredFederalFundsRateFetcher.transform_query({})

        assert query.start_date == date(2016, 1, 1)

    def test_naming_the_default_asks_for_the_same_span(self):
        """``effr_only=False`` is the default, so it reads the same history."""
        query = FredFederalFundsRateFetcher.transform_query({"effr_only": False})

        assert query.start_date == date(2016, 1, 1)

    def test_the_rate_on_its_own_reads_its_whole_history(self):
        query = FredFederalFundsRateFetcher.transform_query({"effr_only": True})

        assert query.start_date is None

    def test_an_asked_for_start_date_is_kept(self):
        query = FredFederalFundsRateFetcher.transform_query(
            {"start_date": date(1971, 8, 15), "effr_only": False}
        )

        assert query.start_date == date(1971, 8, 15)


class TestFederalFundsRateRows:
    """The rows the federal funds rate hands back."""

    @pytest.fixture
    def rows(self, monkeypatch):
        return _distribution(monkeypatch, "effr")

    def test_the_published_target_range_is_passed_through_unscaled(self, rows):
        assert (
            rows.result[0].target_range_lower,
            rows.result[0].target_range_upper,
        ) == (5.25, 5.5)

    def test_the_metadata_is_keyed_by_the_field_it_describes(self, rows):
        """Alone among these models, it renames the series to the field it fills."""
        assert rows.metadata == {
            "rate": {"title": "Federal Funds Effective Rate"},
            "volume": {"title": "Federal Funds Volume"},
        }


class TestSofrRows:
    """The rows SOFR hands back."""

    @pytest.fixture
    def rows(self, monkeypatch):
        return _distribution(monkeypatch, "sofr")

    def test_the_published_averages_are_passed_through_unscaled(self, rows):
        assert [
            rows.result[0].average_30d,
            rows.result[0].average_90d,
            rows.result[0].average_180d,
        ] == [4.33, 4.0, 2.5]

    def test_the_published_index_is_passed_through_unscaled(self, rows):
        """The index is a level rather than a percent, and it too is left as written."""
        assert rows.result[0].index == 1.15


class TestFedProjections:
    """The federal funds rate projections the FOMC publishes."""

    @staticmethod
    def _answers(ids):
        """Give every projection series two periods, one of them unpublished."""
        return {
            series_id: [
                {"date": "2024-12-01", "value": str(5.5 - index * 0.25)},
                {"date": "2025-12-01", "value": "."},
            ]
            for index, series_id in enumerate(ids)
        }

    async def test_the_projections_of_the_coming_years_are_read(self, monkeypatch):
        reader = _ManyReader(self._answers(SHORT_RUN_PROJECTION_IDS))
        monkeypatch.setattr("openbb_fred.utils.api.get_observations_many", reader)

        await FREDPROJECTIONFetcher.fetch_data({}, CREDENTIALS)

        assert reader.calls[0][0] == SHORT_RUN_PROJECTION_IDS

    async def test_the_long_run_projections_are_their_own_series(self, monkeypatch):
        reader = _ManyReader(self._answers(LONG_RUN_PROJECTION_IDS))
        monkeypatch.setattr("openbb_fred.utils.api.get_observations_many", reader)

        await FREDPROJECTIONFetcher.fetch_data({"long_run": True}, CREDENTIALS)

        assert reader.calls[0][0] == LONG_RUN_PROJECTION_IDS

    async def test_every_projection_becomes_a_column(self, monkeypatch):
        reader = _ManyReader(self._answers(SHORT_RUN_PROJECTION_IDS))
        monkeypatch.setattr("openbb_fred.utils.api.get_observations_many", reader)

        rows = await FREDPROJECTIONFetcher.fetch_data({}, CREDENTIALS)

        assert rows[0].model_dump() == {
            "date": date(2024, 12, 1),
            "range_high": 5.5,
            "central_tendency_high": 5.25,
            "median": 5.0,
            "range_midpoint": 4.75,
            "central_tendency_midpoint": 4.5,
            "range_low": 4.25,
            "central_tendency_low": 4.0,
        }

    async def test_a_period_reads_as_no_projection(self, monkeypatch):
        reader = _ManyReader(self._answers(SHORT_RUN_PROJECTION_IDS))
        monkeypatch.setattr("openbb_fred.utils.api.get_observations_many", reader)

        rows = await FREDPROJECTIONFetcher.fetch_data({}, CREDENTIALS)

        assert rows[1].median is None

    async def test_a_series_that_skips_a_period_reads_as_nothing_there(
        self, monkeypatch
    ):
        answers = self._answers(SHORT_RUN_PROJECTION_IDS)
        answers["FEDTARMD"] = [{"date": "2024-12-01", "value": "5.0"}]
        reader = _ManyReader(answers)
        monkeypatch.setattr("openbb_fred.utils.api.get_observations_many", reader)

        rows = await FREDPROJECTIONFetcher.fetch_data({}, CREDENTIALS)

        assert (rows[0].median, rows[1].median) == (5.0, None)

    async def test_the_periods_are_ordered(self, monkeypatch):
        reader = _ManyReader(self._answers(SHORT_RUN_PROJECTION_IDS))
        monkeypatch.setattr("openbb_fred.utils.api.get_observations_many", reader)

        rows = await FREDPROJECTIONFetcher.fetch_data({}, CREDENTIALS)

        assert [row.date for row in rows] == [date(2024, 12, 1), date(2025, 12, 1)]

    async def test_the_cache_switch_reaches_the_transport(self, monkeypatch):
        """Reads are cached unless the request turns the cache off."""
        reader = _ManyReader(self._answers(SHORT_RUN_PROJECTION_IDS))
        monkeypatch.setattr("openbb_fred.utils.api.get_observations_many", reader)

        await FREDPROJECTIONFetcher.fetch_data({}, CREDENTIALS)
        await FREDPROJECTIONFetcher.fetch_data({"use_cache": False}, CREDENTIALS)

        assert [call[2]["use_cache"] for call in reader.calls] == [True, False]

    async def test_a_request_without_credentials_carries_no_key(self, monkeypatch):
        reader = _ManyReader(self._answers(SHORT_RUN_PROJECTION_IDS))
        monkeypatch.setattr("openbb_fred.utils.api.get_observations_many", reader)

        await FREDPROJECTIONFetcher.fetch_data({}, None)

        assert reader.calls[0][1] is None


class TestUpstreamFailure:
    """A failure reading the underlying series reaches the caller."""

    @pytest.mark.parametrize("fetcher", SERIES_BACKED_FETCHERS)
    async def test_the_error_is_not_swallowed(self, monkeypatch, fetcher):
        _refuses(monkeypatch, OpenBBError("FRED is unreachable."))

        with pytest.raises(OpenBBError, match="FRED is unreachable."):
            await fetcher.fetch_data({}, CREDENTIALS)

    @pytest.mark.parametrize("fetcher", SERIES_BACKED_FETCHERS)
    async def test_the_kind_of_failure_is_kept(self, monkeypatch, fetcher):
        """A transport failure is not rewritten as a provider error."""
        _refuses(monkeypatch, TimeoutError("The read timed out."))

        with pytest.raises(TimeoutError, match="The read timed out."):
            await fetcher.fetch_data({}, CREDENTIALS)


class TestEmptyResponse:
    """A request that comes back with nothing is reported, not published empty."""

    @pytest.mark.parametrize(
        ("fetcher", "message"),
        [
            (FredAmeriborFetcher, "returned with no data"),
            (FredFederalFundsRateFetcher, "returned empty"),
        ],
    )
    async def test_an_empty_read_is_reported(self, monkeypatch, fetcher, message):
        _series(monkeypatch, [])

        with pytest.raises(EmptyDataError, match=message):
            await fetcher.fetch_data({}, CREDENTIALS)

    async def test_the_federal_funds_rate_reports_a_response_of_gaps(self, monkeypatch):
        """Every day missing a series leaves nothing to publish."""
        _series(monkeypatch, [{"date": date(2024, 1, 2), "DFF": None}])

        with pytest.raises(EmptyDataError, match="returned empty"):
            await FredFederalFundsRateFetcher.fetch_data({}, CREDENTIALS)

    @pytest.mark.parametrize(
        "fetcher",
        [
            FredEuroShortTermRateFetcher,
            FredOvernightBankFundingRateFetcher,
            FREDSOFRFetcher,
        ],
    )
    def test_an_empty_payload_is_reported(self, fetcher):
        query = fetcher.transform_query({})

        with pytest.raises(EmptyDataError, match="returned empty"):
            fetcher.transform_data(query, {})


@fixedincome_owned
class TestChartMetadata:
    """What each rate widget tells the Workspace to plot, read from its widget JSON."""

    @pytest.fixture(scope="class")
    def columns(self):
        """Read every rate widget's built column definitions, keyed by field."""
        from openbb_core.api.rest_api import app
        from openbb_platform_api.utils.widgets import build_json

        from openbb_fred.fred_router import widget_id

        registry = build_json(app.openapi(), [])

        return {
            widget: {
                column["field"]: column
                for column in registry[widget_id(declared)]["data"]["table"][
                    "columnsDefs"
                ]
            }
            for widget, declared in RATE_WIDGETS.items()
        }

    @pytest.mark.parametrize("widget", list(RATE_WIDGETS))
    def test_every_rate_is_charted_against_its_date(self, columns, widget):
        assert columns[widget]["date"]["chartDataType"] == "time"

    @pytest.mark.parametrize(("widget", "field"), PLOTTED_COLUMNS)
    def test_every_rate_family_column_is_plotted(self, columns, widget, field):
        """Rates, percentiles, target ranges and averages share the percent axis."""
        assert columns[widget][field]["chartDataType"] == "series"

    @pytest.mark.parametrize(("widget", "field"), PLOTTED_COLUMNS)
    def test_a_plotted_column_is_still_typed_for_the_table(
        self, columns, widget, field
    ):
        """Declaring the chart role must not cost a column its cell type."""
        assert columns[widget][field]["cellDataType"] == "number"

    @pytest.mark.parametrize(("widget", "field"), UNPLOTTED_COLUMNS)
    def test_a_column_that_is_not_a_rate_is_kept_off_the_chart(
        self, columns, widget, field
    ):
        assert columns[widget][field]["chartDataType"] == "excluded"

    @pytest.mark.parametrize(("widget", "field"), UNPLOTTED_COLUMNS)
    def test_a_column_kept_off_the_chart_still_reaches_the_table(
        self, columns, widget, field
    ):
        """'excluded' leaves the column in the table, where 'hide' would drop it."""
        assert columns[widget][field].get("hide") is not True

    @pytest.mark.parametrize("widget", ["effr", "estr", "obfr", "sofr"])
    def test_the_volume_is_not_plotted_against_the_rates(self, columns, widget):
        """Volume is an amount in the billions, and it flattens every rate series."""
        assert columns[widget]["volume"]["chartDataType"] == "excluded"

    @pytest.mark.parametrize("widget", ["effr", "obfr", "sofr"])
    def test_the_volume_keeps_its_currency_marks_in_the_table(self, columns, widget):
        volume = columns[widget]["volume"]

        assert (volume["prefix"], volume["suffix"]) == ("$", "B")

    def test_the_sofr_index_is_not_plotted_against_the_rates(self, columns):
        """The index is a level around 1.2 rather than a rate."""
        assert columns["sofr"]["index"]["chartDataType"] == "excluded"

    def test_the_ameribor_tenors_are_charted_as_separate_series(self, columns):
        """Its rows are long-format, so the symbol names the series to draw."""
        assert columns["ameribor"]["symbol"]["chartDataType"] == "category"

    @pytest.mark.parametrize("widget", list(RATE_WIDGETS))
    def test_every_column_declares_how_it_is_charted(self, columns, widget):
        """A column left undeclared is one the Workspace has to guess at."""
        for field, column in columns[widget].items():
            assert column.get("chartDataType") in {
                "time",
                "category",
                "series",
                "excluded",
            }, (widget, field)
