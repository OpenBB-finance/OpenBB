"""Unit tests targeting 100% coverage for openbb_oecd.models."""

from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_oecd.models.available_indicators import (
    OecdAvailableIndicatorsFetcher,
    OecdAvailableIndicatorsQueryParams,
    _build_also_in,
)
from openbb_oecd.models.balance_of_payments import (
    OECDBalanceOfPaymentsFetcher,
    OECDBalanceOfPaymentsQueryParams,
    _format_end_period,
    _format_start_period,
)
from openbb_oecd.models.composite_leading_indicator import (
    OECDCompositeLeadingIndicatorFetcher,
    OECDCompositeLeadingIndicatorQueryParams,
)
from openbb_oecd.models.consumer_price_index import (
    OECDCPIFetcher,
    OECDCPIQueryParams,
)
from openbb_oecd.models.country_interest_rates import (
    OecdCountryInterestRatesFetcher,
    OecdCountryInterestRatesQueryParams,
)
from openbb_oecd.models.gdp_forecast import (
    OECDGdpForecastFetcher,
    OECDGdpForecastQueryParams,
)
from openbb_oecd.models.gdp_nominal import (
    OECDGdpNominalFetcher,
    OECDGdpNominalQueryParams,
)
from openbb_oecd.models.gdp_real import (
    OECDGdpRealFetcher,
    OECDGdpRealQueryParams,
)
from openbb_oecd.models.house_price_index import (
    OECDHousePriceIndexFetcher,
    OECDHousePriceIndexQueryParams,
)
from openbb_oecd.models.share_price_index import (
    OECDSharePriceIndexFetcher,
    OECDSharePriceIndexQueryParams,
)
from openbb_oecd.models.unemployment import (
    OECDUnemploymentFetcher,
    OECDUnemploymentQueryParams,
)

QB_PATH = "openbb_oecd.utils.query_builder.OecdQueryBuilder"
META_PATH = "openbb_oecd.utils.metadata.OecdMetadata"


def _mock_qb(records=None, raise_exc=None):
    """Build a MagicMock OecdQueryBuilder with configurable fetch_data behaviour."""
    qb = MagicMock()
    qb.metadata.resolve_country_codes.return_value = ["USA"]
    if raise_exc is not None:
        qb.fetch_data.side_effect = raise_exc
    else:
        qb.fetch_data.return_value = {"data": records if records is not None else []}
    return qb


class TestAvailableIndicators:
    """Cover available_indicators.py missing branches."""

    def test_build_also_in_empty_indicator(self):
        """Empty indicator returns empty list (line 25)."""
        assert _build_also_in("", "DF", {}, {}, MagicMock()) == []

    def test_build_also_in_unknown_indicator(self):
        """Indicator missing from code_to_dataflows returns empty list (line 25)."""
        assert _build_also_in("CODE", "DF", {}, {}, MagicMock()) == []

    def test_build_also_in_resolves_via_metadata(self):
        """Missing name in cache triggers _resolve_dataflow_id fallback (lines 39-45)."""
        meta = MagicMock()
        meta._resolve_dataflow_id.return_value = "DF_FULL"
        code_to_dfs = {"IND": ["DF_OTHER"]}
        df_name_cache = {"DF_FULL": "Other Flow"}
        out = _build_also_in("IND", "DF_THIS", code_to_dfs, df_name_cache, meta)
        assert out == ["DF_OTHER (Other Flow)"]

    def test_build_also_in_resolve_raises(self):
        """metadata._resolve_dataflow_id raising is swallowed (lines 44-45)."""
        meta = MagicMock()
        meta._resolve_dataflow_id.side_effect = RuntimeError("nope")
        code_to_dfs = {"IND": ["DF_OTHER"]}
        out = _build_also_in("IND", "DF_THIS", code_to_dfs, {}, meta)
        assert out == ["DF_OTHER"]

    def test_build_also_in_truncates_after_ten(self):
        """More than 10 entries adds 'and N more' suffix."""
        codes = [f"DF{i}" for i in range(12)]
        df_name_cache = {c: f"Name{c}" for c in codes}
        out = _build_also_in("IND", "DF_X", {"IND": codes}, df_name_cache, MagicMock())
        assert out[-1] == "... and 2 more"

    def test_enrich_results_missing_full_id_fallback(self):
        """full_id resolved from datastructures when short id missing (line 208)."""
        meta = MagicMock()
        meta._short_id_map = {}
        meta.datastructures = {"DF_FULL": {"dimensions": []}}
        meta._dataflow_constraints = {"DF_FULL": {}}
        meta.codelists = {}
        results = [{"dataflow_id": "DF_FULL", "indicator": "IND"}]
        out = OecdAvailableIndicatorsFetcher._enrich_results(results, meta, {}, {})
        assert out[0]["series_id"] == "DF_FULL::IND"

    def test_enrich_results_skips_unresolved_dataflow(self):
        """Datastructure missing → loop skips this df (line 210)."""
        meta = MagicMock()
        meta._short_id_map = {}
        meta.datastructures = {}
        meta._dataflow_constraints = {}
        meta.codelists = {}
        results = [{"dataflow_id": "DF_X", "indicator": "IND"}]
        out = OecdAvailableIndicatorsFetcher._enrich_results(results, meta, {}, {})
        assert out[0]["frequencies"] == []
        assert out[0]["transformations"] == []

    def test_extract_data_dataflows_string_splits(self):
        """Comma-separated dataflows string is parsed into a list (line 262)."""
        meta = MagicMock()
        meta.search_indicators.return_value = []
        meta.list_dataflows.return_value = []
        with patch("openbb_oecd.utils.metadata.OecdMetadata", return_value=meta):
            q = OecdAvailableIndicatorsQueryParams(dataflows="DF_KEI, DF_QNA")
            OecdAvailableIndicatorsFetcher.extract_data(q, None)
        args, kwargs = meta.search_indicators.call_args
        assert kwargs["dataflows"] == ["DF_KEI", "DF_QNA"]

    def test_extract_data_topic_intersects_with_dataflows(self):
        """Topic + dataflow intersection path (lines 267-274)."""
        meta = MagicMock()
        meta.list_dataflows.return_value = [
            {"value": "AGENCY:DSD_KEI@DF_KEI"},
            {"value": "AGENCY:DSD_QNA@DF_QNA"},
        ]
        meta.search_indicators.return_value = []
        with patch("openbb_oecd.utils.metadata.OecdMetadata", return_value=meta):
            q = OecdAvailableIndicatorsQueryParams(topic="ECO", dataflows=["DF_KEI"])
            OecdAvailableIndicatorsFetcher.extract_data(q, None)
        _, kwargs = meta.search_indicators.call_args
        assert kwargs["dataflows"] == ["AGENCY:DSD_KEI@DF_KEI"]

    def test_extract_data_topic_no_intersection_keeps_explicit(self):
        """Empty intersection falls back to explicit dataflows (line 274)."""
        meta = MagicMock()
        meta.list_dataflows.return_value = [{"value": "AGENCY,DF_OTHER,1.0"}]
        meta.search_indicators.return_value = []
        with patch("openbb_oecd.utils.metadata.OecdMetadata", return_value=meta):
            q = OecdAvailableIndicatorsQueryParams(topic="ECO", dataflows=["DF_KEI"])
            OecdAvailableIndicatorsFetcher.extract_data(q, None)
        _, kwargs = meta.search_indicators.call_args
        assert kwargs["dataflows"] == ["DF_KEI"]

    def test_extract_data_topic_without_dataflows(self):
        """Topic alone expands to its dataflows (line 276)."""
        meta = MagicMock()
        meta.list_dataflows.return_value = [{"value": "AGENCY:DSD_KEI@DF_KEI"}]
        meta.search_indicators.return_value = []
        with patch("openbb_oecd.utils.metadata.OecdMetadata", return_value=meta):
            q = OecdAvailableIndicatorsQueryParams(topic="ECO")
            OecdAvailableIndicatorsFetcher.extract_data(q, None)
        _, kwargs = meta.search_indicators.call_args
        assert kwargs["dataflows"] == ["AGENCY:DSD_KEI@DF_KEI"]

    def test_extract_data_keywords_string_splits(self):
        """Comma-separated keywords string is parsed (line 281)."""
        meta = MagicMock()
        meta.search_indicators.return_value = []
        with patch("openbb_oecd.utils.metadata.OecdMetadata", return_value=meta):
            q = OecdAvailableIndicatorsQueryParams(keywords="gdp, growth")
            OecdAvailableIndicatorsFetcher.extract_data(q, None)
        _, kwargs = meta.search_indicators.call_args
        assert kwargs["keywords"] == ["gdp", "growth"]

    def test_extract_data_empty_results_returns_early(self):
        """Empty search_indicators short-circuits enrichment (line 290)."""
        meta = MagicMock()
        meta.search_indicators.return_value = []
        with patch("openbb_oecd.utils.metadata.OecdMetadata", return_value=meta):
            q = OecdAvailableIndicatorsQueryParams()
            out = OecdAvailableIndicatorsFetcher.extract_data(q, None)
        assert out == []

    def test_transform_query_passthrough(self):
        """transform_query returns query params (line 152)."""
        q = OecdAvailableIndicatorsFetcher.transform_query({"query": "gdp"})
        assert q.query == "gdp"

    def test_build_enrichment_indexes(self):
        """Reverse indexes built from cached dataflows (lines 162-185)."""
        meta = MagicMock()
        meta._dataflow_indicators_cache = {
            "FULL_A": [
                {"indicator": "GDP", "dataflow_id": "DF_A"},
                {"indicator": "CPI", "dataflow_id": "DF_A"},
                {"indicator": ""},
            ],
        }
        meta.dataflows = {
            "FULL_A": {"short_id": "DF_A", "name": "Flow A"},
            "FULL_B": {"short_id": "", "name": "Flow B"},
        }
        c2d, names = OecdAvailableIndicatorsFetcher._build_enrichment_indexes(meta)
        assert c2d["GDP"] == ["DF_A"]
        assert c2d["CPI"] == ["DF_A"]
        assert names["DF_A"] == "Flow A"
        assert names["FULL_B"] == "Flow B"

    def test_enrich_results_with_constraints(self):
        """Frequency/transformation labels built from constraints (lines 225-227)."""
        meta = MagicMock()
        meta._short_id_map = {"DF_X": "FULL_X"}
        meta.datastructures = {
            "FULL_X": {
                "dimensions": [
                    {"id": "FREQ", "codelist_id": "CL_FREQ"},
                    {"id": "TRANSFORMATION", "codelist_id": "CL_TR"},
                ]
            }
        }
        meta._dataflow_constraints = {
            "FULL_X": {"FREQ": ["A"], "TRANSFORMATION": ["G1"]}
        }
        meta.codelists = {"CL_FREQ": {"A": "Annual"}, "CL_TR": {"G1": "Growth"}}
        results = [{"dataflow_id": "DF_X", "indicator": "GDP"}]
        out = OecdAvailableIndicatorsFetcher._enrich_results(results, meta, {}, {})
        assert out[0]["frequencies"] == ["A (Annual)"]
        assert out[0]["transformations"] == ["G1 (Growth)"]

    def test_extract_data_with_results_enriches(self):
        """Non-empty results trigger enrichment path (lines 293-297)."""
        meta = MagicMock()
        meta._dataflow_indicators_cache = {"FULL": [{"indicator": "GDP"}]}
        meta.dataflows = {"FULL": {"short_id": "DF", "name": "Flow"}}
        meta.search_indicators.return_value = [
            {"dataflow_id": "DF", "indicator": "GDP"}
        ]
        meta._short_id_map = {"DF": "FULL"}
        meta.datastructures = {"FULL": {"dimensions": []}}
        meta._dataflow_constraints = {"FULL": {}}
        meta.codelists = {}
        with patch("openbb_oecd.utils.metadata.OecdMetadata", return_value=meta):
            q = OecdAvailableIndicatorsQueryParams()
            out = OecdAvailableIndicatorsFetcher.extract_data(q, None)
        assert out and out[0]["series_id"] == "DF::GDP"

    def test_transform_data(self):
        """transform_data validates each row (line 308)."""
        data = [
            {
                "series_id": "DF::IND",
                "indicator": "IND",
                "dataflow_id": "DF",
            }
        ]
        out = OecdAvailableIndicatorsFetcher.transform_data(
            OecdAvailableIndicatorsQueryParams(), data
        )
        assert len(out) == 1
        assert out[0].symbol == "DF::IND"


class TestBalanceOfPayments:
    """Cover balance_of_payments.py missing branches."""

    def test_format_start_period_quarterly(self):
        """Quarterly start formats year-Qn (line 63-64)."""
        assert _format_start_period(date(2024, 5, 1), "Q") == "2024-Q2"

    def test_format_start_period_monthly(self):
        """Monthly start formats year-MM (line 65)."""
        assert _format_start_period(date(2024, 3, 15), "M") == "2024-03"

    def test_format_end_period_quarterly(self):
        """Quarterly end formats year-Qn (line 72-73)."""
        assert _format_end_period(date(2024, 8, 1), "Q") == "2024-Q3"

    def test_format_end_period_monthly(self):
        """Monthly end formats year-MM (line 74)."""
        assert _format_end_period(date(2024, 11, 1), "M") == "2024-11"

    def test_validator_normalizes_country(self):
        """Spaces and case normalized in the validator."""
        q = OECDBalanceOfPaymentsQueryParams(country="United States")
        assert q.country == "united_states"

    def test_extract_data_non_200_raises(self):
        """HTTP non-200 raises OpenBBError (line 179)."""
        resp = MagicMock(status_code=500, reason="Server", text="")
        with (
            patch("openbb_core.provider.utils.helpers.make_request", return_value=resp),
            patch("openbb_oecd.utils.metadata.OecdMetadata") as MetaCls,
        ):
            MetaCls.return_value.resolve_country_codes.return_value = ["USA"]
            with pytest.raises(OpenBBError, match="BOP request failed"):
                OECDBalanceOfPaymentsFetcher.extract_data(
                    OECDBalanceOfPaymentsQueryParams(
                        country="united_states",
                        start_date=date(2020, 1, 1),
                        end_date=date(2021, 1, 1),
                    ),
                    None,
                )

    def test_extract_data_empty_text_raises(self):
        """Empty body raises OpenBBError wrapping EmptyDataError (line 186)."""
        resp = MagicMock(status_code=200, reason="OK", text="   ")
        with (
            patch("openbb_core.provider.utils.helpers.make_request", return_value=resp),
            patch("openbb_oecd.utils.metadata.OecdMetadata") as MetaCls,
        ):
            MetaCls.return_value.resolve_country_codes.return_value = ["USA"]
            with pytest.raises(OpenBBError):
                OECDBalanceOfPaymentsFetcher.extract_data(
                    OECDBalanceOfPaymentsQueryParams(), None
                )

    def test_extract_data_csv_parse_error(self):
        """read_csv failure raises OpenBBError (lines 192-193)."""
        resp = MagicMock(status_code=200, reason="OK", text="rows here")
        with (
            patch("openbb_core.provider.utils.helpers.make_request", return_value=resp),
            patch("openbb_oecd.utils.metadata.OecdMetadata") as MetaCls,
            patch("pandas.read_csv", side_effect=ValueError("bad csv")),
        ):
            MetaCls.return_value.resolve_country_codes.return_value = ["USA"]
            with pytest.raises(OpenBBError, match="Failed to parse"):
                OECDBalanceOfPaymentsFetcher.extract_data(
                    OECDBalanceOfPaymentsQueryParams(), None
                )

    def test_extract_data_empty_dataframe(self):
        """Empty parsed DataFrame raises OpenBBError (line 198)."""
        from pandas import DataFrame

        resp = MagicMock(status_code=200, reason="OK", text="A,B\n")
        with (
            patch("openbb_core.provider.utils.helpers.make_request", return_value=resp),
            patch("openbb_oecd.utils.metadata.OecdMetadata") as MetaCls,
            patch("pandas.read_csv", return_value=DataFrame()),
        ):
            MetaCls.return_value.resolve_country_codes.return_value = ["USA"]
            with pytest.raises(OpenBBError, match="No BOP data rows"):
                OECDBalanceOfPaymentsFetcher.extract_data(
                    OECDBalanceOfPaymentsQueryParams(), None
                )

    def test_extract_data_empty_string_column(self):
        """All-null string column triggers sample.empty branch (line 225)."""
        from pandas import DataFrame

        df = DataFrame(
            {
                "MEASURE": ["CA"],
                "ACCOUNTING_ENTRY": ["B"],
                "UNIT_MEASURE": ["USD_EXC"],
                "TIME_PERIOD": ["2020"],
                "OBS_VALUE": [1.0],
                "EMPTY_COL": [None],
                "REF_AREA": ["USA"],
            }
        )
        df["EMPTY_COL"] = df["EMPTY_COL"].astype("string")
        resp = MagicMock(status_code=200, reason="OK", text="ignored")
        with (
            patch("openbb_core.provider.utils.helpers.make_request", return_value=resp),
            patch("openbb_oecd.utils.metadata.OecdMetadata") as MetaCls,
            patch("pandas.read_csv", return_value=df),
        ):
            MetaCls.return_value.resolve_country_codes.return_value = ["USA"]
            out = OECDBalanceOfPaymentsFetcher.extract_data(
                OECDBalanceOfPaymentsQueryParams(), None
            )
        assert out and out[0]["OBS_VALUE"] == 1.0

    def test_extract_data_no_colon_in_string_column(self):
        """String column without ': ' assigns label = code (line 234)."""
        from pandas import DataFrame

        df = DataFrame(
            {
                "MEASURE": ["CA"],
                "ACCOUNTING_ENTRY": ["B"],
                "UNIT_MEASURE": ["USD_EXC"],
                "TIME_PERIOD": ["2020"],
                "OBS_VALUE": [1.0],
                "REF_AREA": ["USA"],
                "TAG": ["plain_text"],
            }
        )
        resp = MagicMock(status_code=200, reason="OK", text="ignored")
        with (
            patch("openbb_core.provider.utils.helpers.make_request", return_value=resp),
            patch("openbb_oecd.utils.metadata.OecdMetadata") as MetaCls,
            patch("pandas.read_csv", return_value=df),
        ):
            MetaCls.return_value.resolve_country_codes.return_value = ["USA"]
            out = OECDBalanceOfPaymentsFetcher.extract_data(
                OECDBalanceOfPaymentsQueryParams(), None
            )
        assert out and out[0].get("OBS_VALUE") == 1.0

    def test_transform_data_skips_missing_value(self):
        """Row with empty OBS_VALUE skipped (line 257)."""
        rows = [{"OBS_VALUE": None, "TIME_PERIOD": "2020"}]
        q = OECDBalanceOfPaymentsQueryParams()
        out = OECDBalanceOfPaymentsFetcher.transform_data(q, rows)
        assert out == []

    def test_transform_data_skips_invalid_date(self):
        """Row with unparsable TIME_PERIOD skipped (line 262)."""
        rows = [{"OBS_VALUE": 1.0, "TIME_PERIOD": "not-a-date"}]
        q = OECDBalanceOfPaymentsQueryParams()
        out = OECDBalanceOfPaymentsFetcher.transform_data(q, rows)
        assert out == []

    def test_transform_data_skips_before_start(self):
        """Row before start_date skipped (line 265)."""
        rows = [
            {
                "OBS_VALUE": 1.0,
                "TIME_PERIOD": "2010",
                "MEASURE": "CA",
                "ACCOUNTING_ENTRY": "B",
                "UNIT_MEASURE": "USD_EXC",
                "REF_AREA": "USA",
            }
        ]
        q = OECDBalanceOfPaymentsQueryParams(start_date=date(2020, 1, 1))
        out = OECDBalanceOfPaymentsFetcher.transform_data(q, rows)
        assert out == []

    def test_transform_data_skips_after_end(self):
        """Row after end_date skipped (line 268)."""
        rows = [
            {
                "OBS_VALUE": 1.0,
                "TIME_PERIOD": "2030",
                "MEASURE": "CA",
                "ACCOUNTING_ENTRY": "B",
                "UNIT_MEASURE": "USD_EXC",
                "REF_AREA": "USA",
            }
        ]
        q = OECDBalanceOfPaymentsQueryParams(end_date=date(2020, 1, 1))
        out = OECDBalanceOfPaymentsFetcher.transform_data(q, rows)
        assert out == []

    def test_transform_data_unmapped_column_skipped(self):
        """Row with unmapped MEASURE/ENTRY/UNIT combo skipped (line 276)."""
        rows = [
            {
                "OBS_VALUE": 1.0,
                "TIME_PERIOD": "2020",
                "MEASURE": "ZZZ",
                "ACCOUNTING_ENTRY": "B",
                "UNIT_MEASURE": "USD_EXC",
                "REF_AREA": "USA",
            }
        ]
        q = OECDBalanceOfPaymentsQueryParams()
        out = OECDBalanceOfPaymentsFetcher.transform_data(q, rows)
        assert out == []

    def test_transform_data_happy_path(self):
        """Valid row maps into BOP data object."""
        rows = [
            {
                "OBS_VALUE": 12.5,
                "TIME_PERIOD": "2020",
                "MEASURE": "CA",
                "ACCOUNTING_ENTRY": "B",
                "UNIT_MEASURE": "USD_EXC",
                "REF_AREA": "USA",
                "REF_AREA_label": "United States",
            }
        ]
        q = OECDBalanceOfPaymentsQueryParams()
        out = OECDBalanceOfPaymentsFetcher.transform_data(q, rows)
        assert len(out) == 1
        assert out[0].balance_total == 12.5

    def test_format_start_period_annual(self):
        """Annual start formats year only (line 62)."""
        assert _format_start_period(date(2024, 6, 1), "A") == "2024"

    def test_format_end_period_annual(self):
        """Annual end formats year only (line 71)."""
        assert _format_end_period(date(2024, 6, 1), "A") == "2024"

    def test_transform_query_returns_params(self):
        """transform_query returns query (line 130)."""
        q = OECDBalanceOfPaymentsFetcher.transform_query({"country": "united_states"})
        assert q.country == "united_states"

    def test_extract_data_with_dates_and_colon_columns(self):
        """Covers dim_filter with dates, colon-split labels, and percent path (lines 161-167, 205, 228-234, 286)."""
        from pandas import DataFrame

        df = DataFrame(
            {
                "MEASURE: Measure": ["CA: Current account", "S: Services"],
                "ACCOUNTING_ENTRY: Entry": ["B: Balance", "B: Balance"],
                "UNIT_MEASURE: Unit": ["PT_B1GQ: Percent", "USD_EXC: USD"],
                "TIME_PERIOD": ["2020", "2020"],
                "OBS_VALUE": [2.5, 100.0],
                "REF_AREA: Area": ["USA: United States", "USA: United States"],
            }
        )
        resp = MagicMock(status_code=200, reason="OK", text="ignored")
        with (
            patch("openbb_core.provider.utils.helpers.make_request", return_value=resp),
            patch("openbb_oecd.utils.metadata.OecdMetadata") as MetaCls,
            patch("pandas.read_csv", return_value=df),
        ):
            MetaCls.return_value.resolve_country_codes.return_value = ["USA"]
            q = OECDBalanceOfPaymentsQueryParams(
                country="united_states",
                frequency="annual",
                start_date=date(2020, 1, 1),
                end_date=date(2020, 12, 31),
            )
            rows = OECDBalanceOfPaymentsFetcher.extract_data(q, None)
            out = OECDBalanceOfPaymentsFetcher.transform_data(q, rows)
        assert out
        balance_pct = [r for r in out if r.balance_percent_of_gdp is not None]
        assert balance_pct and balance_pct[0].balance_percent_of_gdp == 0.025


class TestCompositeLeadingIndicator:
    """Cover composite_leading_indicator.py missing branches."""

    def test_validator_none_returns_g20(self):
        """None country normalizes to g20 (line 50)."""
        q = OECDCompositeLeadingIndicatorQueryParams(country=None)
        assert q.country == "g20"

    def test_validator_list_input(self):
        """List input bypasses split branch (lines 54-55)."""
        q = OECDCompositeLeadingIndicatorQueryParams(country=["g20"])
        assert q.country == "g20"

    def test_validator_all_returns_all(self):
        """Token 'all' short-circuits (line 57)."""
        q = OECDCompositeLeadingIndicatorQueryParams(country="all,g20")
        assert q.country == "all"

    def test_validator_unknown_country_warns_and_skips(self):
        """Unknown country warned and dropped (line 60)."""
        with pytest.warns(UserWarning, match="not supported"):
            q = OECDCompositeLeadingIndicatorQueryParams(country="g20,atlantis")
        assert q.country == "g20"

    def test_validator_no_valid_raises(self):
        """All-invalid input raises (line 64)."""
        with (
            pytest.warns(UserWarning, match="not supported"),
            pytest.raises(OpenBBError, match="No valid countries"),
        ):
            OECDCompositeLeadingIndicatorQueryParams(country="atlantis")

    def test_transform_query_fills_defaults(self):
        """None dates and country filled in (lines 88, 95, 98)."""
        q = OECDCompositeLeadingIndicatorFetcher.transform_query(
            {"start_date": None, "end_date": None, "country": None}
        )
        assert q.start_date == date(1947, 1, 1)
        assert q.end_date.year == date.today().year
        assert q.country == "g20"

    def test_transform_query_all_uses_recent_start(self):
        """country='all' yields 2020 start (line 88)."""
        q = OECDCompositeLeadingIndicatorFetcher.transform_query(
            {"start_date": None, "country": "all"}
        )
        assert q.start_date == date(2020, 1, 1)

    def test_extract_data_growth_clears_adjustment(self):
        """growth_rate=True wipes adjustment (line 116)."""
        qb = _mock_qb(records=[{"TIME_PERIOD": "2020", "OBS_VALUE": 1.0}])
        with patch(
            "openbb_oecd.utils.query_builder.OecdQueryBuilder",
            return_value=qb,
        ):
            q = OECDCompositeLeadingIndicatorQueryParams(
                country="g20", growth_rate=True
            )
            OECDCompositeLeadingIndicatorFetcher.extract_data(q, None)
        kwargs = qb.fetch_data.call_args.kwargs
        assert kwargs["ADJUSTMENT"] == ""
        assert kwargs["TRANSFORMATION"] == "GY"

    def test_extract_data_wraps_exception(self):
        """fetch_data exceptions wrap as OpenBBError (lines 134-135)."""
        qb = _mock_qb(raise_exc=RuntimeError("boom"))
        with patch(
            "openbb_oecd.utils.query_builder.OecdQueryBuilder",
            return_value=qb,
        ):
            with pytest.raises(OpenBBError, match="boom"):
                OECDCompositeLeadingIndicatorFetcher.extract_data(
                    OECDCompositeLeadingIndicatorQueryParams(country="g20"), None
                )

    def test_extract_data_empty_raises(self):
        """Empty records raise OpenBBError (line 140)."""
        qb = _mock_qb(records=[])
        with patch(
            "openbb_oecd.utils.query_builder.OecdQueryBuilder",
            return_value=qb,
        ):
            with pytest.raises(OpenBBError, match="No data"):
                OECDCompositeLeadingIndicatorFetcher.extract_data(
                    OECDCompositeLeadingIndicatorQueryParams(country="g20"), None
                )

    def test_transform_data_skips_bad_date(self):
        """Bad TIME_PERIOD skipped (line 160)."""
        q = OECDCompositeLeadingIndicatorQueryParams(country="g20")
        out = OECDCompositeLeadingIndicatorFetcher.transform_data(
            q, [{"TIME_PERIOD": "bad", "OBS_VALUE": 1.0}]
        )
        assert out == []

    def test_transform_data_skips_missing_value(self):
        """Missing OBS_VALUE skipped (line 165)."""
        q = OECDCompositeLeadingIndicatorQueryParams(country="g20")
        out = OECDCompositeLeadingIndicatorFetcher.transform_data(
            q, [{"TIME_PERIOD": "2020", "OBS_VALUE": None}]
        )
        assert out == []

    def test_transform_data_growth_scales(self):
        """growth_rate=True divides value by 100 (line 170)."""
        q = OECDCompositeLeadingIndicatorQueryParams(country="g20", growth_rate=True)
        out = OECDCompositeLeadingIndicatorFetcher.transform_data(
            q, [{"TIME_PERIOD": "2020", "OBS_VALUE": 50.0, "REF_AREA": "USA"}]
        )
        assert out[0].value == 0.5


class TestConsumerPriceIndex:
    """Cover consumer_price_index.py missing branches."""

    def test_validate_expenditure_string(self):
        """Expenditure parsed and lowercased (line 150)."""
        q = OECDCPIQueryParams(country="united_states", expenditure="Total, Energy")
        assert q.expenditure == "total,energy"

    def test_validate_expenditure_unknown_raises(self):
        """Unknown expenditure raises (lines 152-155)."""
        with pytest.raises(ValueError, match="not a valid choice"):
            OECDCPIQueryParams(country="united_states", expenditure="nonsense")

    def test_validate_expenditure_all(self):
        """'all' keyword accepted (line 156)."""
        q = OECDCPIQueryParams(country="united_states", expenditure="all")
        assert q.expenditure == "all"

    def test_transform_query_defaults(self):
        """transform_query fills nulls (lines 184, 186, 188)."""
        q = OECDCPIFetcher.transform_query(
            {"start_date": None, "end_date": None, "country": None}
        )
        assert q.start_date == date(1950, 1, 1)
        assert q.end_date.year == date.today().year
        assert q.country == "united_states"

    def test_extract_data_harmonized_quarter_becomes_monthly(self):
        """harmonized+quarter forced to monthly (line 209)."""
        qb = _mock_qb(records=[{"TIME_PERIOD": "2020", "OBS_VALUE": 1.0}])
        with patch(
            "openbb_oecd.utils.query_builder.OecdQueryBuilder",
            return_value=qb,
        ):
            q = OECDCPIQueryParams(
                country="united_states", harmonized=True, frequency="quarter"
            )
            OECDCPIFetcher.extract_data(q, None)
        assert qb.fetch_data.call_args.kwargs["FREQ"] == "M"

    def test_extract_data_expenditure_all_clears_code(self):
        """'all' expenditure clears the code list (line 215)."""
        qb = _mock_qb(records=[{"TIME_PERIOD": "2020", "OBS_VALUE": 1.0}])
        with patch(
            "openbb_oecd.utils.query_builder.OecdQueryBuilder",
            return_value=qb,
        ):
            q = OECDCPIQueryParams(country="united_states", expenditure="all")
            OECDCPIFetcher.extract_data(q, None)
        assert qb.fetch_data.call_args.kwargs["EXPENDITURE"] == ""

    def test_extract_data_wraps_exception(self):
        """Exceptions wrap as OpenBBError (lines 233-234)."""
        qb = _mock_qb(raise_exc=RuntimeError("bad"))
        with patch(
            "openbb_oecd.utils.query_builder.OecdQueryBuilder",
            return_value=qb,
        ):
            with pytest.raises(OpenBBError, match="No data"):
                OECDCPIFetcher.extract_data(
                    OECDCPIQueryParams(country="united_states"), None
                )

    def test_extract_data_empty_raises(self):
        """Empty records raise (line 239)."""
        qb = _mock_qb(records=[])
        with patch(
            "openbb_oecd.utils.query_builder.OecdQueryBuilder",
            return_value=qb,
        ):
            with pytest.raises(OpenBBError):
                OECDCPIFetcher.extract_data(
                    OECDCPIQueryParams(country="united_states"), None
                )

    def test_transform_data_filters(self):
        """Bad date/range/value rows skipped (lines 260, 263, 266, 271)."""
        q = OECDCPIQueryParams(
            country="united_states",
            start_date=date(2020, 1, 1),
            end_date=date(2020, 12, 31),
            transform="index",
        )
        rows = [
            {"TIME_PERIOD": "bad", "OBS_VALUE": 1.0},
            {"TIME_PERIOD": "2010", "OBS_VALUE": 1.0},
            {"TIME_PERIOD": "2030", "OBS_VALUE": 1.0},
            {"TIME_PERIOD": "2020", "OBS_VALUE": None},
            {
                "TIME_PERIOD": "2020",
                "OBS_VALUE": 100.0,
                "REF_AREA": "USA",
                "EXPENDITURE": "_T",
                "FREQ": "A",
                "TRANSFORMATION_label": "Not applicable",
            },
        ]
        out = OECDCPIFetcher.transform_data(q, rows)
        assert len(out) == 1
        assert out[0].value == 100.0

    def test_transform_data_yoy_scales_and_appends_transform(self):
        """YoY value scales by 100 and transform label appended (lines 276, 291)."""
        q = OECDCPIQueryParams(country="united_states", transform="yoy")
        rows = [
            {
                "TIME_PERIOD": "2020",
                "OBS_VALUE": 50.0,
                "REF_AREA": "USA",
                "EXPENDITURE": "_T",
                "TRANSFORMATION_label": "Year-on-year growth",
            }
        ]
        out = OECDCPIFetcher.transform_data(q, rows)
        assert out[0].value == 0.5
        assert "Year-on-year growth" in out[0].title


class TestCountryInterestRates:
    """Cover country_interest_rates.py missing branches."""

    def test_transform_query_all_uses_2020(self):
        """country=all uses 2020 start (line 72)."""
        q = OecdCountryInterestRatesFetcher.transform_query(
            {"start_date": None, "country": "all"}
        )
        assert q.start_date == date(2020, 1, 1)

    def test_transform_query_default_end_and_country(self):
        """None end and country defaulted (lines 78, 80)."""
        q = OecdCountryInterestRatesFetcher.transform_query(
            {"start_date": None, "end_date": None, "country": None}
        )
        assert q.end_date.year == date.today().year
        assert q.country == "united_states"

    def test_extract_data_wraps_exception(self):
        """Exception wrapped (lines 115-116)."""
        qb = _mock_qb(raise_exc=RuntimeError("oops"))
        with patch(
            "openbb_oecd.utils.query_builder.OecdQueryBuilder",
            return_value=qb,
        ):
            with pytest.raises(OpenBBError, match="oops"):
                OecdCountryInterestRatesFetcher.extract_data(
                    OecdCountryInterestRatesQueryParams(country="united_states"), None
                )

    def test_extract_data_empty_raises(self):
        """Empty records raise EmptyDataError (line 121)."""
        qb = _mock_qb(records=[])
        with patch(
            "openbb_oecd.utils.query_builder.OecdQueryBuilder",
            return_value=qb,
        ):
            with pytest.raises(EmptyDataError):
                OecdCountryInterestRatesFetcher.extract_data(
                    OecdCountryInterestRatesQueryParams(country="united_states"), None
                )

    def test_extract_data_returns_records(self):
        """Non-empty rows returned (line 123)."""
        rows = [{"TIME_PERIOD": "2020", "OBS_VALUE": 1.0}]
        qb = _mock_qb(records=rows)
        with patch(
            "openbb_oecd.utils.query_builder.OecdQueryBuilder",
            return_value=qb,
        ):
            out = OecdCountryInterestRatesFetcher.extract_data(
                OecdCountryInterestRatesQueryParams(country="united_states"), None
            )
        assert out == rows

    def test_transform_data_filters(self):
        """Bad date/missing value rows skipped (lines 140, 145)."""
        q = OecdCountryInterestRatesQueryParams(country="united_states")
        rows = [
            {"TIME_PERIOD": "bad", "OBS_VALUE": 1.0},
            {"TIME_PERIOD": "2020", "OBS_VALUE": None},
            {"TIME_PERIOD": "2020", "OBS_VALUE": 5.0, "REF_AREA": "USA"},
        ]
        out = OecdCountryInterestRatesFetcher.transform_data(q, rows)
        assert len(out) == 1
        assert out[0].value == 0.05


class TestGdpForecast:
    """Cover gdp_forecast.py missing branches."""

    def test_transform_query_defaults(self):
        """Missing country/dates filled in (lines 76, 79, 84)."""
        q = OECDGdpForecastFetcher.transform_query(
            {"country": None, "start_date": None, "end_date": None}
        )
        assert q.country == "all"
        assert q.start_date.year == date.today().year
        assert q.end_date.year == date.today().year + 2

    def test_extract_data_capita_quarter_warns(self):
        """capita+quarter combo forces annual + warns (lines 104-107)."""
        qb = _mock_qb(records=[{"TIME_PERIOD": "2025", "OBS_VALUE": 1.0}])
        with patch("openbb_oecd.utils.query_builder.OecdQueryBuilder", return_value=qb):
            q = OECDGdpForecastQueryParams(
                country="all", units="capita", frequency="quarter"
            )
            with pytest.warns(UserWarning, match="not available"):
                OECDGdpForecastFetcher.extract_data(q, None)
        assert qb.fetch_data.call_args.kwargs["FREQ"] == "A"

    def test_extract_data_wraps_exception(self):
        """Exception wrapped (lines 122-123)."""
        qb = _mock_qb(raise_exc=RuntimeError("nope"))
        with patch("openbb_oecd.utils.query_builder.OecdQueryBuilder", return_value=qb):
            with pytest.raises(OpenBBError, match="nope"):
                OECDGdpForecastFetcher.extract_data(
                    OECDGdpForecastQueryParams(country="all"), None
                )

    def test_extract_data_empty_raises(self):
        """Empty records → EmptyDataError (line 127)."""
        qb = _mock_qb(records=[])
        with patch("openbb_oecd.utils.query_builder.OecdQueryBuilder", return_value=qb):
            with pytest.raises(EmptyDataError):
                OECDGdpForecastFetcher.extract_data(
                    OECDGdpForecastQueryParams(country="all"), None
                )

    def test_transform_data_filters_and_scales(self):
        """Bad date / missing value / growth scaling / non-positive skip (lines 144, 147, 150, 154)."""
        q = OECDGdpForecastQueryParams(country="all", units="growth")
        rows = [
            {"TIME_PERIOD": "bad", "OBS_VALUE": 1.0},
            {"TIME_PERIOD": "2025", "OBS_VALUE": None},
            {"TIME_PERIOD": "2025", "OBS_VALUE": -1.0, "REF_AREA": "USA"},
            {"TIME_PERIOD": "2025", "OBS_VALUE": 5.0, "REF_AREA": "USA"},
        ]
        out = OECDGdpForecastFetcher.transform_data(q, rows)
        assert len(out) == 1
        assert out[0].value == 0.05

    def test_transform_data_int_cast_path(self):
        """units='current_prices' triggers int cast branch."""
        q = OECDGdpForecastQueryParams(country="all", units="current_prices")
        rows = [{"TIME_PERIOD": "2025", "OBS_VALUE": 1.5, "REF_AREA": "USA"}]
        out = OECDGdpForecastFetcher.transform_data(q, rows)
        assert out[0].value == 1


class TestGdpNominal:
    """Cover gdp_nominal.py missing branches."""

    def test_transform_query_all_recent_start(self):
        """country=all yields 2020 start (line 84)."""
        q = OECDGdpNominalFetcher.transform_query(
            {"start_date": None, "country": "all"}
        )
        assert q.start_date == date(2020, 1, 1)

    def test_transform_query_default_country(self):
        """None country default (lines 90, 92)."""
        q = OECDGdpNominalFetcher.transform_query(
            {"start_date": None, "end_date": None, "country": None}
        )
        assert q.country == "united_states"
        assert q.end_date.year == date.today().year

    def test_extract_data_index_volume_uses_dr(self):
        """units='index' + price_base 'current_prices' flips to DR (line 113)."""
        qb = _mock_qb(records=[{"TIME_PERIOD": "2020", "OBS_VALUE": 1.0}])
        with patch("openbb_oecd.utils.query_builder.OecdQueryBuilder", return_value=qb):
            q = OECDGdpNominalQueryParams(
                country="united_states", units="index", price_base="current_prices"
            )
            OECDGdpNominalFetcher.extract_data(q, None)
        assert qb.fetch_data.call_args.kwargs["PRICE_BASE"] == "DR"

    def test_extract_data_wraps_exception(self):
        """Exception wrapped (lines 132-133)."""
        qb = _mock_qb(raise_exc=RuntimeError("ugh"))
        with patch("openbb_oecd.utils.query_builder.OecdQueryBuilder", return_value=qb):
            with pytest.raises(OpenBBError, match="ugh"):
                OECDGdpNominalFetcher.extract_data(
                    OECDGdpNominalQueryParams(country="united_states"), None
                )

    def test_extract_data_empty_raises(self):
        """Empty records → EmptyDataError (line 137)."""
        qb = _mock_qb(records=[])
        with patch("openbb_oecd.utils.query_builder.OecdQueryBuilder", return_value=qb):
            with pytest.raises(EmptyDataError):
                OECDGdpNominalFetcher.extract_data(
                    OECDGdpNominalQueryParams(country="united_states"), None
                )

    def test_transform_data_filters(self):
        """Date/range/value filters (lines 155, 157, 159, 162)."""
        q = OECDGdpNominalQueryParams(
            country="united_states",
            start_date=date(2020, 1, 1),
            end_date=date(2020, 12, 31),
            units="level",
        )
        rows = [
            {"TIME_PERIOD": "bad", "OBS_VALUE": 1.0},
            {"TIME_PERIOD": "2010", "OBS_VALUE": 1.0},
            {"TIME_PERIOD": "2030", "OBS_VALUE": 1.0},
            {"TIME_PERIOD": "2020", "OBS_VALUE": None},
            {"TIME_PERIOD": "2020", "OBS_VALUE": 1.0, "REF_AREA": "USA"},
        ]
        out = OECDGdpNominalFetcher.transform_data(q, rows)
        assert len(out) == 1


class TestGdpReal:
    """Cover gdp_real.py missing branches."""

    def test_transform_query_all_start(self):
        """country=all → 2020 start (line 64)."""
        q = OECDGdpRealFetcher.transform_query({"start_date": None, "country": "all"})
        assert q.start_date == date(2020, 1, 1)

    def test_transform_query_default_country(self):
        """None country default (lines 70, 72)."""
        q = OECDGdpRealFetcher.transform_query(
            {"start_date": None, "end_date": None, "country": None}
        )
        assert q.country == "united_states"

    def test_extract_data_wraps_exception(self):
        """Exception wrapped (lines 107-108)."""
        qb = _mock_qb(raise_exc=RuntimeError("oops"))
        with patch("openbb_oecd.utils.query_builder.OecdQueryBuilder", return_value=qb):
            with pytest.raises(OpenBBError, match="oops"):
                OECDGdpRealFetcher.extract_data(
                    OECDGdpRealQueryParams(country="united_states"), None
                )

    def test_extract_data_empty_raises(self):
        """Empty rows → EmptyDataError (line 112)."""
        qb = _mock_qb(records=[])
        with patch("openbb_oecd.utils.query_builder.OecdQueryBuilder", return_value=qb):
            with pytest.raises(EmptyDataError):
                OECDGdpRealFetcher.extract_data(
                    OECDGdpRealQueryParams(country="united_states"), None
                )

    def test_extract_data_returns_records(self):
        """Non-empty records returned (line 114)."""
        rows = [{"TIME_PERIOD": "2020", "OBS_VALUE": 1.0, "REF_AREA": "USA"}]
        qb = _mock_qb(records=rows)
        with patch("openbb_oecd.utils.query_builder.OecdQueryBuilder", return_value=qb):
            out = OECDGdpRealFetcher.extract_data(
                OECDGdpRealQueryParams(country="united_states"), None
            )
        assert out == rows

    def test_transform_data_filters(self):
        """Date/value filters (lines 129, 131, 133, 136)."""
        q = OECDGdpRealQueryParams(
            country="united_states",
            start_date=date(2020, 1, 1),
            end_date=date(2020, 12, 31),
        )
        rows = [
            {"TIME_PERIOD": "bad", "OBS_VALUE": 1.0},
            {"TIME_PERIOD": "2010", "OBS_VALUE": 1.0},
            {"TIME_PERIOD": "2030", "OBS_VALUE": 1.0},
            {"TIME_PERIOD": "2020", "OBS_VALUE": None},
            {"TIME_PERIOD": "2020", "OBS_VALUE": 2.5, "REF_AREA": "USA"},
        ]
        out = OECDGdpRealFetcher.transform_data(q, rows)
        assert len(out) == 1
        assert out[0].value == 2_500_000


class TestHousePriceIndex:
    """Cover house_price_index.py missing branches."""

    def test_transform_query_all_start(self):
        """country=all → 2000 start (line 64)."""
        q = OECDHousePriceIndexFetcher.transform_query(
            {"start_date": None, "country": "all"}
        )
        assert q.start_date == date(2000, 1, 1)

    def test_transform_query_default_country(self):
        """None country default (lines 70, 72)."""
        q = OECDHousePriceIndexFetcher.transform_query(
            {"start_date": None, "end_date": None, "country": None}
        )
        assert q.country == "united_states"

    def test_extract_data_monthly_fallback_to_quarterly(self):
        """Monthly failure falls back to quarterly (lines 106-127)."""
        qb = MagicMock()
        qb.metadata.resolve_country_codes.return_value = ["USA"]
        qb.fetch_data.side_effect = [
            RuntimeError("no monthly"),
            {"data": [{"TIME_PERIOD": "2020", "OBS_VALUE": 1.0, "REF_AREA": "USA"}]},
        ]
        with patch("openbb_oecd.utils.query_builder.OecdQueryBuilder", return_value=qb):
            with pytest.warns(UserWarning, match="quarterly"):
                out = OECDHousePriceIndexFetcher.extract_data(
                    OECDHousePriceIndexQueryParams(
                        country="united_states", frequency="monthly"
                    ),
                    None,
                )
        assert out and qb.fetch_data.call_count == 2

    def test_extract_data_monthly_fallback_fails(self):
        """Quarterly fallback failure raises OpenBBError (lines 128-129)."""
        qb = MagicMock()
        qb.metadata.resolve_country_codes.return_value = ["USA"]
        qb.fetch_data.side_effect = [RuntimeError("m"), RuntimeError("q")]
        with patch("openbb_oecd.utils.query_builder.OecdQueryBuilder", return_value=qb):
            with pytest.warns(UserWarning):
                with pytest.raises(OpenBBError, match="q"):
                    OECDHousePriceIndexFetcher.extract_data(
                        OECDHousePriceIndexQueryParams(
                            country="united_states", frequency="monthly"
                        ),
                        None,
                    )

    def test_extract_data_non_monthly_exception(self):
        """Non-monthly failure raises directly (line 131)."""
        qb = _mock_qb(raise_exc=RuntimeError("boom"))
        with patch("openbb_oecd.utils.query_builder.OecdQueryBuilder", return_value=qb):
            with pytest.raises(OpenBBError, match="boom"):
                OECDHousePriceIndexFetcher.extract_data(
                    OECDHousePriceIndexQueryParams(
                        country="united_states", frequency="quarter"
                    ),
                    None,
                )

    def test_extract_data_empty_raises(self):
        """Empty records → EmptyDataError (line 135)."""
        qb = _mock_qb(records=[])
        with patch("openbb_oecd.utils.query_builder.OecdQueryBuilder", return_value=qb):
            with pytest.raises(EmptyDataError):
                OECDHousePriceIndexFetcher.extract_data(
                    OECDHousePriceIndexQueryParams(country="united_states"), None
                )

    def test_transform_data_filters_and_scales(self):
        """Date / value filters + percent scaling (lines 151, 156, 159)."""
        q = OECDHousePriceIndexQueryParams(country="united_states", transform="yoy")
        rows = [
            {"TIME_PERIOD": "bad", "OBS_VALUE": 1.0},
            {"TIME_PERIOD": "2020", "OBS_VALUE": None},
            {"TIME_PERIOD": "2020", "OBS_VALUE": 50.0, "REF_AREA": "USA"},
        ]
        out = OECDHousePriceIndexFetcher.transform_data(q, rows)
        assert out[0].value == 0.5


class TestSharePriceIndex:
    """Cover share_price_index.py missing branches."""

    def test_transform_query_all_uses_2000(self):
        """country=all → 2000 start (line 54)."""
        q = OECDSharePriceIndexFetcher.transform_query(
            {"start_date": None, "country": "all"}
        )
        assert q.start_date == date(2000, 1, 1)

    def test_transform_query_default_country(self):
        """None country defaulted (lines 61, 64)."""
        q = OECDSharePriceIndexFetcher.transform_query(
            {"start_date": None, "end_date": None, "country": None}
        )
        assert q.country == "united_states"
        assert q.end_date.year == date.today().year

    def test_extract_data_wraps_exception(self):
        """Exception wrapped (lines 95-96)."""
        qb = _mock_qb(raise_exc=RuntimeError("ugh"))
        with patch("openbb_oecd.utils.query_builder.OecdQueryBuilder", return_value=qb):
            with pytest.raises(OpenBBError, match="ugh"):
                OECDSharePriceIndexFetcher.extract_data(
                    OECDSharePriceIndexQueryParams(country="united_states"), None
                )

    def test_extract_data_empty_raises(self):
        """Empty records → OpenBBError (line 101)."""
        qb = _mock_qb(records=[])
        with patch("openbb_oecd.utils.query_builder.OecdQueryBuilder", return_value=qb):
            with pytest.raises(OpenBBError, match="no data rows"):
                OECDSharePriceIndexFetcher.extract_data(
                    OECDSharePriceIndexQueryParams(country="united_states"), None
                )

    def test_extract_data_returns_records(self):
        """Non-empty rows returned (line 105)."""
        rows = [{"TIME_PERIOD": "2020", "OBS_VALUE": 1.0}]
        qb = _mock_qb(records=rows)
        with patch("openbb_oecd.utils.query_builder.OecdQueryBuilder", return_value=qb):
            out = OECDSharePriceIndexFetcher.extract_data(
                OECDSharePriceIndexQueryParams(country="united_states"), None
            )
        assert out == rows

    def test_transform_data_filters(self):
        """Bad date / missing value (lines 119, 124)."""
        q = OECDSharePriceIndexQueryParams(country="united_states")
        rows = [
            {"TIME_PERIOD": "bad", "OBS_VALUE": 1.0},
            {"TIME_PERIOD": "2020", "OBS_VALUE": None},
            {"TIME_PERIOD": "2020", "OBS_VALUE": 100.0, "REF_AREA": "USA"},
        ]
        out = OECDSharePriceIndexFetcher.transform_data(q, rows)
        assert len(out) == 1
        assert out[0].value == 100.0


class TestUnemployment:
    """Cover unemployment.py missing branches."""

    def test_validator_normalizes(self):
        """Validator strips and lowercases (line 64)."""
        q = OECDUnemploymentQueryParams(country="United States")
        assert q.country == "united_states"

    def test_transform_query_all_uses_2010(self):
        """country=all → 2010 start (line 81)."""
        q = OECDUnemploymentFetcher.transform_query(
            {"start_date": None, "end_date": None, "country": "all"}
        )
        assert q.start_date == date(2010, 1, 1)

    def test_transform_query_end_default(self):
        """None end_date filled in (line 87)."""
        q = OECDUnemploymentFetcher.transform_query(
            {"start_date": date(2020, 1, 1), "end_date": None}
        )
        assert q.end_date.year == date.today().year

    def test_extract_data_wraps_exception(self):
        """Exception wrapped (lines 123-124)."""
        qb = _mock_qb(raise_exc=RuntimeError("nope"))
        with patch("openbb_oecd.utils.query_builder.OecdQueryBuilder", return_value=qb):
            with pytest.raises(OpenBBError, match="nope"):
                OECDUnemploymentFetcher.extract_data(
                    OECDUnemploymentQueryParams(country="united_states"), None
                )

    def test_extract_data_empty_raises(self):
        """Empty records → EmptyDataError (line 128)."""
        qb = _mock_qb(records=[])
        with patch("openbb_oecd.utils.query_builder.OecdQueryBuilder", return_value=qb):
            with pytest.raises(EmptyDataError):
                OECDUnemploymentFetcher.extract_data(
                    OECDUnemploymentQueryParams(country="united_states"), None
                )

    def test_extract_data_returns_records(self):
        """Non-empty rows returned (line 130)."""
        rows = [{"TIME_PERIOD": "2020", "OBS_VALUE": 1.0}]
        qb = _mock_qb(records=rows)
        with patch("openbb_oecd.utils.query_builder.OecdQueryBuilder", return_value=qb):
            out = OECDUnemploymentFetcher.extract_data(
                OECDUnemploymentQueryParams(country="united_states"), None
            )
        assert out == rows

    def test_transform_data_filters(self):
        """Date and value filters (lines 143, 145, 147, 150)."""
        q = OECDUnemploymentQueryParams(
            country="united_states",
            start_date=date(2020, 1, 1),
            end_date=date(2020, 12, 31),
        )
        rows = [
            {"TIME_PERIOD": "bad", "OBS_VALUE": 1.0},
            {"TIME_PERIOD": "2010", "OBS_VALUE": 1.0},
            {"TIME_PERIOD": "2030", "OBS_VALUE": 1.0},
            {"TIME_PERIOD": "2020", "OBS_VALUE": None},
            {"TIME_PERIOD": "2020", "OBS_VALUE": 5.0, "REF_AREA": "USA"},
        ]
        out = OECDUnemploymentFetcher.transform_data(q, rows)
        assert len(out) == 1
        assert out[0].value == 0.05
