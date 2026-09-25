"""Tests for the FRED fixed income and bond index models."""

import json
from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_fred.models.bond_indices import FredBondIndicesFetcher
from openbb_fred.models.commercial_paper import ALL_IDS, FREDCommercialPaperFetcher
from openbb_fred.models.high_quality_market import (
    FredHighQualityMarketCorporateBondFetcher,
)
from openbb_fred.models.mortgage_indices import FredMortgageIndicesFetcher
from openbb_fred.models.search import FredSearchData
from openbb_fred.models.series import FredSeriesData
from openbb_fred.models.spot import FREDSpotRateFetcher
from openbb_fred.models.tips_yields import FredTipsYieldsFetcher
from openbb_fred.models.yield_curve import FREDYieldCurveData, FREDYieldCurveFetcher
from openbb_fred.utils.fred_helpers import get_spot_maturities, get_spot_series_id

CREDENTIALS = {"fred_api_key": "MOCK_API_KEY"}

YIELD_CURVE_SERIES = [
    "BAMLC1A0C13YEY",
    "BAMLC2A0C35YEY",
    "BAMLC3A0C57YEY",
    "BAMLC4A0C710YEY",
    "BAMLC7A0C1015YEY",
    "BAMLC8A0C15PYEY",
]
YIELD_CURVE_BANDS = [
    "year1_year3",
    "year3_year5",
    "year5_year7",
    "year7_year10",
    "year10_year15",
    "year15_plus",
]

TIPS_CATALOG = [
    {
        "series_id": "DTP10J32",
        "title": "10-Year 1.5% Treasury Inflation-Indexed Note, Due 01/15/2032",
        "observation_start": date(2022, 1, 20),
        "observation_end": date(2024, 7, 17),
    },
    {
        "series_id": "DTP5J29",
        "title": "5-Year 0.125% Treasury Inflation-Indexed Note, Due 04/15/2029",
        "observation_start": date(2019, 4, 18),
        "observation_end": date(2024, 7, 17),
    },
    {
        "series_id": "DTP10J24",
        "title": "10-Year 0.5% Treasury Inflation-Indexed Note"
        " (DISCONTINUED), Due 01/15/2024",
        "observation_start": date(2014, 1, 23),
        "observation_end": date(2024, 1, 12),
    },
]


def _annotated(rows: list[dict], metadata: dict | None = None) -> AnnotatedResult:
    """Return the shape ``FredSeriesFetcher`` answers with."""
    return AnnotatedResult(
        result=[FredSeriesData.model_validate(r) for r in rows],
        metadata=metadata or {},
    )


def _patch_series(monkeypatch, answer) -> None:
    """Answer every series read with ``answer``."""
    monkeypatch.setattr(
        "openbb_fred.models.series.FredSeriesFetcher.fetch_data",
        staticmethod(answer),
    )


def _serve_series(monkeypatch, rows: list[dict], metadata: dict | None = None) -> list:
    """Serve one fixed series payload, and collect the parameters asked for."""
    asked: list = []

    async def answer(params, credentials=None, **kwargs):
        asked.append(params)
        return _annotated(rows, metadata)

    _patch_series(monkeypatch, answer)

    return asked


def _fail_series(monkeypatch, error: Exception) -> None:
    """Fail every series read with ``error``."""

    async def answer(params, credentials=None, **kwargs):
        raise error

    _patch_series(monkeypatch, answer)


def _yield_curve_row() -> dict:
    """Return one observation date carrying every yield curve band."""
    row: dict = {"date": date(2024, 6, 3)}

    for offset, symbol in enumerate(reversed(YIELD_CURVE_SERIES)):
        row[symbol] = 5.0 + offset

    return row


def _yield_curve_metadata() -> dict:
    """Return the titles FRED publishes for the yield curve bands."""
    return {
        symbol: {"title": f"ICE BofA US Corporate {band} Effective Yield"}
        for symbol, band in zip(YIELD_CURVE_SERIES, YIELD_CURVE_BANDS)
    }


def _serve_tips_catalog(monkeypatch, catalog: list[dict] | None = None) -> None:
    """Answer the TIPS release search with a fixed catalog."""
    entries = TIPS_CATALOG if catalog is None else catalog

    async def answer(params=None, credentials=None, **kwargs):
        return [FredSearchData.model_validate(d) for d in entries]

    monkeypatch.setattr(
        "openbb_fred.models.search.FredSearchFetcher.fetch_data",
        staticmethod(answer),
    )


def _fail_tips_catalog(monkeypatch, error: Exception) -> None:
    """Fail the TIPS release search with ``error``."""

    async def answer(params=None, credentials=None, **kwargs):
        raise error

    monkeypatch.setattr(
        "openbb_fred.models.search.FredSearchFetcher.fetch_data",
        staticmethod(answer),
    )


class TestBondIndexSelection:
    """Resolving a category, an index and an index type to FRED series IDs."""

    def test_the_yield_curve_overrides_the_category(self):
        query = FredBondIndicesFetcher.transform_query(
            {"category": "emerging_markets", "index": "yield_curve"}
        )

        assert query.category == "us"
        assert query.index == "yield_curve"

    def test_the_yield_curve_maps_to_every_maturity_band(self):
        query = FredBondIndicesFetcher.transform_query({"index": "yield_curve"})

        assert query._symbols.split(",") == YIELD_CURVE_SERIES

    def test_the_index_type_picks_the_yield_curve_series(self):
        query = FredBondIndicesFetcher.transform_query(
            {"index": "yield_curve", "index_type": "oas"}
        )

        assert query._symbols.split(",") == [
            "BAMLC1A0C13Y",
            "BAMLC2A0C35Y",
            "BAMLC3A0C57Y",
            "BAMLC4A0C710Y",
            "BAMLC7A0C1015Y",
            "BAMLC8A0C15PY",
        ]

    def test_a_second_index_beside_the_yield_curve_is_refused(self):
        with pytest.warns(UserWarning, match="Multiple indices not allowed"):
            query = FredBondIndicesFetcher.transform_query(
                {"index": "yield_curve,corporate"}
            )

        assert query.index == "yield_curve"

    def test_a_list_holding_the_yield_curve_and_another_index_is_refused(self):
        with pytest.warns(UserWarning, match="Multiple indices not allowed"):
            query = FredBondIndicesFetcher.transform_query(
                {"index": ["yield_curve", "corporate"]}
            )

        assert query.index == "yield_curve"

    def test_an_index_the_us_category_does_not_publish_is_reported(self):
        with pytest.raises(
            OpenBBError, match="Invalid index, crossover, for category: 'us'"
        ):
            FredBondIndicesFetcher.transform_query(
                {"category": "us", "index": "crossover"}
            )

    def test_the_us_message_names_what_is_published(self):
        with pytest.raises(OpenBBError, match="corporate, seasoned_corporate"):
            FredBondIndicesFetcher.transform_query(
                {"category": "us", "index": "crossover"}
            )

    def test_seasoned_corporate_is_published_only_as_a_yield(self):
        with pytest.raises(
            OpenBBError, match="Invalid index_type for index: 'seasoned_corporate'"
        ):
            FredBondIndicesFetcher.transform_query(
                {"category": "us", "index": "seasoned_corporate", "index_type": "oas"}
            )

    def test_seasoned_corporate_maps_to_the_moody_series(self):
        query = FredBondIndicesFetcher.transform_query(
            {"category": "us", "index": "seasoned_corporate", "index_type": "yield"}
        )

        assert query._symbols == "DAAA,AAA10Y,AAAFF,DBAA,BAA10Y,BAAFF"

    def test_an_index_the_high_yield_category_does_not_publish_is_reported(self):
        with pytest.raises(
            OpenBBError, match="Invalid index, corporate, for category: 'high_yield'"
        ):
            FredBondIndicesFetcher.transform_query(
                {"category": "high_yield", "index": "corporate"}
            )

    def test_the_high_yield_message_names_the_three_regions(self):
        with pytest.raises(OpenBBError, match="Must be one of us, europe, emerging"):
            FredBondIndicesFetcher.transform_query(
                {"category": "high_yield", "index": "corporate"}
            )

    def test_a_high_yield_region_maps_to_its_series(self):
        query = FredBondIndicesFetcher.transform_query(
            {"category": "high_yield", "index": "europe", "index_type": "oas"}
        )

        assert query.index == "europe"
        assert query._symbols == "BAMLHE00EHYIOAS"

    def test_an_index_the_emerging_markets_category_does_not_publish_is_reported(self):
        with pytest.raises(
            OpenBBError, match="Invalid index, aa, for category: 'emerging_markets'"
        ):
            FredBondIndicesFetcher.transform_query(
                {"category": "emerging_markets", "index": "aa"}
            )

    def test_the_emerging_markets_message_names_what_is_published(self):
        with pytest.raises(OpenBBError, match="corporate, liquid_corporate"):
            FredBondIndicesFetcher.transform_query(
                {"category": "emerging_markets", "index": "aa"}
            )

    def test_an_emerging_markets_index_maps_to_its_series(self):
        query = FredBondIndicesFetcher.transform_query(
            {
                "category": "emerging_markets",
                "index": "crossover",
                "index_type": "total_return",
            }
        )

        assert query.index == "crossover"
        assert query._symbols == "BAMLEM5BCOCRPITRIV"

    def test_a_published_index_beside_an_unpublished_one_survives(self):
        with pytest.warns(UserWarning, match="Invalid index, crossover"):
            query = FredBondIndicesFetcher.transform_query(
                {"category": "us", "index": "corporate,crossover"}
            )

        assert query.index == "corporate"
        assert query._symbols == "BAMLC0A0CMEY"

    def test_nothing_published_for_the_request_is_reported(self):
        with pytest.raises(OpenBBError, match="No valid combinations of parameters"):
            FredBondIndicesFetcher.transform_query(
                {"category": "us", "index": "crossover"}
            )

    def test_an_unknown_category_matches_no_index(self):
        with pytest.raises(OpenBBError, match="No valid combinations of parameters"):
            FredBondIndicesFetcher.transform_query(
                {"category": "not_a_category", "index": "corporate"}
            )

    def test_an_index_type_that_publishes_no_series_is_reported(self):
        """The index type is read before it is validated, so it is checked here."""
        with pytest.raises(OpenBBError, match="Error mapping the provided choices"):
            FredBondIndicesFetcher.transform_query(
                {"category": "us", "index": "corporate", "index_type": "duration"}
            )


class TestBondIndexColumns:
    """Naming the column each requested index is carried in."""

    def test_a_yield_curve_is_named_by_maturity_band(self):
        from openbb_fred.models.bond_indices import index_columns

        query = FredBondIndicesFetcher.transform_query({"index": "yield_curve"})

        assert list(index_columns(query).values()) == YIELD_CURVE_BANDS

    def test_an_index_is_named_for_itself(self):
        from openbb_fred.models.bond_indices import index_columns

        query = FredBondIndicesFetcher.transform_query(
            {"category": "us", "index": "corporate,aaa"}
        )

        assert sorted(index_columns(query).values()) == ["aaa", "corporate"]

    def test_an_index_that_publishes_no_such_type_is_left_out(self):
        """'seasoned_corporate' publishes a yield and nothing else."""
        from openbb_fred.models.bond_indices import index_columns

        query = FredBondIndicesFetcher.transform_query(
            {"category": "us", "index": "corporate"}
        )
        query.index = "corporate,seasoned_corporate"
        query.index_type = "oas"

        assert list(index_columns(query).values()) == ["corporate"]


class TestBondIndexData:
    """Shaping the observations a bond index request returns."""

    async def test_the_published_yield_is_passed_through_unscaled(self, monkeypatch):
        """FRED publishes this yield in percent, and that is what is returned."""
        _serve_series(
            monkeypatch,
            [{"date": date(2024, 6, 3), "BAMLC0A0CMEY": 5.5}],
            {"BAMLC0A0CMEY": {"title": "ICE BofA US Corporate Index Effective Yield"}},
        )
        result = await FredBondIndicesFetcher.fetch_data(
            {"category": "us", "index": "corporate"}, CREDENTIALS
        )

        assert result.result[0].model_dump()["corporate"] == 5.5

    async def test_a_total_return_index_is_passed_through_unscaled(self, monkeypatch):
        """Every index type is passed through alike, so this one is no exception."""
        _serve_series(
            monkeypatch,
            [{"date": date(2024, 6, 3), "BAMLCC0A0CMTRIV": 4321.25}],
            {"BAMLCC0A0CMTRIV": {"title": "ICE BofA US Corporate Index Total Return"}},
        )
        result = await FredBondIndicesFetcher.fetch_data(
            {"category": "us", "index": "corporate", "index_type": "total_return"},
            CREDENTIALS,
        )

        assert result.result[0].model_dump()["corporate"] == 4321.25

    async def test_each_index_is_carried_in_its_own_column(self, monkeypatch):
        """Wide output is what lets the chart draw one line per index."""
        _serve_series(
            monkeypatch,
            [{"date": date(2024, 6, 3), "BAMLC0A0CMEY": 5.5, "BAMLC0A1CAAAEY": 4.9}],
            {},
        )
        result = await FredBondIndicesFetcher.fetch_data(
            {"category": "us", "index": "corporate,aaa"}, CREDENTIALS
        )
        row = result.result[0].model_dump(exclude_none=True)

        assert row["corporate"] == 5.5
        assert row["aaa"] == 4.9

    async def test_a_null_observation_is_reported_as_no_value(self, monkeypatch):
        _serve_series(
            monkeypatch,
            [
                {"date": date(2024, 6, 3), "BAMLC0A0CMEY": None},
                {"date": date(2024, 6, 4), "BAMLC0A0CMEY": 5.6},
            ],
            {"BAMLC0A0CMEY": {"title": "ICE BofA US Corporate Index Effective Yield"}},
        )
        result = await FredBondIndicesFetcher.fetch_data(
            {"category": "us", "index": "corporate"}, CREDENTIALS
        )
        rows = [d.model_dump() for d in result.result]

        assert rows[0]["corporate"] is None
        assert rows[1]["corporate"] == 5.6

    async def test_each_yield_curve_band_is_its_own_column(self, monkeypatch):
        _serve_series(monkeypatch, [_yield_curve_row()], _yield_curve_metadata())
        result = await FredBondIndicesFetcher.fetch_data(
            {"index": "yield_curve"}, CREDENTIALS
        )
        row = result.result[0].model_dump(exclude_none=True)

        assert [c for c in row if c != "date"] == YIELD_CURVE_BANDS

    async def test_the_yield_curve_runs_from_the_short_end_out(self, monkeypatch):
        """Sorting the band names as text would put 'year10_year15' first."""
        _serve_series(monkeypatch, [_yield_curve_row()], _yield_curve_metadata())
        result = await FredBondIndicesFetcher.fetch_data(
            {"index": "yield_curve"}, CREDENTIALS
        )
        columns = [
            c for c in result.result[0].model_dump(exclude_none=True) if c != "date"
        ]

        assert columns == YIELD_CURVE_BANDS

    async def test_an_index_that_is_not_the_yield_curve_is_named_for_itself(
        self, monkeypatch
    ):
        _serve_series(
            monkeypatch,
            [{"date": date(2024, 6, 3), "BAMLC0A0CMEY": 5.5}],
            {"BAMLC0A0CMEY": {"title": "ICE BofA US Corporate Index Effective Yield"}},
        )
        result = await FredBondIndicesFetcher.fetch_data(
            {"category": "us", "index": "corporate"}, CREDENTIALS
        )

        assert [
            c for c in result.result[0].model_dump(exclude_none=True) if c != "date"
        ] == ["corporate"]

    async def test_no_observations_is_reported_as_empty(self, monkeypatch):
        _serve_series(monkeypatch, [])

        with pytest.raises(EmptyDataError, match="No data found for the given query"):
            await FredBondIndicesFetcher.fetch_data(
                {"category": "us", "index": "corporate"}, CREDENTIALS
            )

    def test_a_payload_with_nothing_in_it_is_reported_as_empty(self):
        query = FredBondIndicesFetcher.transform_query(
            {"category": "us", "index": "corporate"}
        )

        with pytest.raises(EmptyDataError, match="The request was returned empty"):
            FredBondIndicesFetcher.transform_data(query, {})


class TestCommercialPaperSelection:
    """Turning a maturity and a category into the series IDs to read."""

    async def test_the_default_request_reads_every_published_series(self, monkeypatch):
        asked = _serve_series(monkeypatch, [])
        query = FREDCommercialPaperFetcher.transform_query({})
        await FREDCommercialPaperFetcher.aextract_data(query, CREDENTIALS)

        assert asked[0]["symbol"].split(",") == ALL_IDS

    async def test_a_category_of_all_expands_to_every_asset_type(self, monkeypatch):
        asked = _serve_series(monkeypatch, [])
        query = FREDCommercialPaperFetcher.transform_query(
            {"maturity": "30d", "category": "all"}
        )
        await FREDCommercialPaperFetcher.aextract_data(query, CREDENTIALS)

        assert asked[0]["symbol"].split(",") == [
            "RIFSPPAAAD30NB",
            "RIFSPPFAAD30NB",
            "RIFSPPNAAD30NB",
            "RIFSPPNA2P2D30NB",
        ]

    async def test_a_maturity_of_all_expands_to_every_tenor(self, monkeypatch):
        asked = _serve_series(monkeypatch, [])
        query = FREDCommercialPaperFetcher.transform_query(
            {"maturity": "all", "category": "financial"}
        )
        await FREDCommercialPaperFetcher.aextract_data(query, CREDENTIALS)

        assert asked[0]["symbol"].split(",") == [
            "RIFSPPFAAD01NB",
            "RIFSPPFAAD07NB",
            "RIFSPPFAAD15NB",
            "RIFSPPFAAD30NB",
            "RIFSPPFAAD60NB",
            "RIFSPPFAAD90NB",
        ]

    async def test_named_maturities_are_crossed_with_named_categories(
        self, monkeypatch
    ):
        asked = _serve_series(monkeypatch, [])
        query = FREDCommercialPaperFetcher.transform_query(
            {"maturity": "7d,30d", "category": "a2p2"}
        )
        await FREDCommercialPaperFetcher.aextract_data(query, CREDENTIALS)

        assert asked[0]["symbol"].split(",") == [
            "RIFSPPNA2P2D07NB",
            "RIFSPPNA2P2D30NB",
        ]

    async def test_the_history_starts_in_2019_when_no_start_date_is_given(
        self, monkeypatch
    ):
        asked = _serve_series(monkeypatch, [])
        query = FREDCommercialPaperFetcher.transform_query({})
        await FREDCommercialPaperFetcher.aextract_data(query, CREDENTIALS)

        assert asked[0]["start_date"] == "2019-01-01"

    async def test_a_given_start_date_is_kept(self, monkeypatch):
        asked = _serve_series(monkeypatch, [])
        query = FREDCommercialPaperFetcher.transform_query(
            {"start_date": date(2023, 1, 1)}
        )
        await FREDCommercialPaperFetcher.aextract_data(query, CREDENTIALS)

        assert asked[0]["start_date"] == date(2023, 1, 1)

    async def test_a_failed_read_is_reported(self, monkeypatch):
        _fail_series(monkeypatch, OpenBBError("FRED is unavailable."))

        with pytest.raises(OpenBBError, match="FRED is unavailable"):
            await FREDCommercialPaperFetcher.fetch_data(
                {"maturity": "30d", "category": "financial"}, CREDENTIALS
            )


class TestCommercialPaperData:
    """Shaping the observations a commercial paper request returns."""

    async def test_the_published_rate_is_passed_through_unscaled(self, monkeypatch):
        """FRED publishes this rate in percent, and that is what is returned."""
        _serve_series(monkeypatch, [{"date": date(2024, 6, 3), "RIFSPPFAAD30NB": 5.32}])
        result = await FREDCommercialPaperFetcher.fetch_data(
            {"maturity": "30d", "category": "financial"}, CREDENTIALS
        )

        assert result.result[0].model_dump()["financial_day_30"] == 5.32

    async def test_each_column_is_named_for_its_category_and_maturity(
        self, monkeypatch
    ):
        _serve_series(monkeypatch, [{"date": date(2024, 6, 3), "RIFSPPFAAD30NB": 5.32}])
        result = await FREDCommercialPaperFetcher.fetch_data(
            {"maturity": "30d", "category": "financial"}, CREDENTIALS
        )
        columns = [
            c for c in result.result[0].model_dump(exclude_none=True) if c != "date"
        ]

        assert columns == ["financial_day_30"]

    async def test_the_asset_types_run_in_published_order(self, monkeypatch):
        """Sorting the asset types as text would put 'a2p2' first."""
        _serve_series(
            monkeypatch,
            [
                {
                    "date": date(2024, 6, 3),
                    "RIFSPPNA2P2D01NB": 5.9,
                    "RIFSPPNAAD01NB": 5.3,
                }
            ],
        )
        result = await FREDCommercialPaperFetcher.fetch_data(
            {"maturity": "overnight", "category": "nonfinancial,a2p2"}, CREDENTIALS
        )
        columns = [
            c for c in result.result[0].model_dump(exclude_none=True) if c != "date"
        ]

        assert columns == ["nonfinancial_overnight", "a2p2_overnight"]

    async def test_the_maturities_run_from_overnight_outwards(self, monkeypatch):
        """Sorting the maturities as text would put 'day_15' first."""
        _serve_series(
            monkeypatch,
            [
                {
                    "date": date(2024, 6, 3),
                    "RIFSPPFAAD15NB": 5.4,
                    "RIFSPPFAAD90NB": 5.5,
                    "RIFSPPFAAD01NB": 5.3,
                }
            ],
        )
        result = await FREDCommercialPaperFetcher.fetch_data(
            {"maturity": "overnight,15d,90d", "category": "financial"}, CREDENTIALS
        )
        columns = [
            c for c in result.result[0].model_dump(exclude_none=True) if c != "date"
        ]

        assert columns == [
            "financial_overnight",
            "financial_day_15",
            "financial_day_90",
        ]

    async def test_no_observations_is_reported_as_empty(self, monkeypatch):
        _serve_series(monkeypatch, [])

        with pytest.raises(EmptyDataError, match="The request was returned empty"):
            await FREDCommercialPaperFetcher.fetch_data(
                {"maturity": "30d", "category": "financial"}, CREDENTIALS
            )


class TestMortgageIndexSelection:
    """Validating the mortgage index names and resolving them to series IDs."""

    def test_an_index_that_is_not_published_is_dropped_with_a_warning(self):
        with pytest.warns(UserWarning, match="Invalid index 'bogus' will be ignored"):
            query = FredMortgageIndicesFetcher.transform_query(
                {"index": "jumbo_30y,bogus"}
            )

        assert query.index == "jumbo_30y"

    def test_nothing_published_for_the_request_is_reported(self):
        with (
            pytest.warns(UserWarning, match="Invalid index 'bogus' will be ignored"),
            pytest.raises(OpenBBError, match="No valid indices found"),
        ):
            FredMortgageIndicesFetcher.transform_query({"index": "bogus"})

    def test_the_message_names_what_is_published(self):
        with (
            pytest.warns(UserWarning, match="Invalid index 'bogus' will be ignored"),
            pytest.raises(OpenBBError, match="conforming_30y"),
        ):
            FredMortgageIndicesFetcher.transform_query({"index": "bogus"})

    async def test_a_group_expands_to_every_index_in_it(self, monkeypatch):
        asked = _serve_series(monkeypatch, [])
        query = FredMortgageIndicesFetcher.transform_query({"index": "ltv_gt_80"})
        await FredMortgageIndicesFetcher.aextract_data(query, CREDENTIALS)

        assert asked[0]["symbol"].split(",") == [
            "OBMMIC30YFLVGT80FGE740",
            "OBMMIC30YFLVGT80FB720A739",
            "OBMMIC30YFLVGT80FB700A719",
            "OBMMIC30YFLVGT80FB680A699",
            "OBMMIC30YFLVGT80FLT680",
        ]

    async def test_a_failed_read_is_reported(self, monkeypatch):
        _fail_series(monkeypatch, OpenBBError("FRED is unavailable."))

        with pytest.raises(OpenBBError, match="FRED is unavailable"):
            await FredMortgageIndicesFetcher.fetch_data(
                {"index": "jumbo_30y"}, CREDENTIALS
            )


class TestMortgageIndexData:
    """Shaping the observations a mortgage index request returns."""

    async def test_the_published_rate_is_passed_through_unscaled(self, monkeypatch):
        """FRED publishes this rate in percent, and that is what is returned."""
        _serve_series(monkeypatch, [{"date": date(2024, 6, 3), "OBMMIJUMBO30YF": 7.05}])
        result = await FredMortgageIndicesFetcher.fetch_data(
            {"index": "jumbo_30y"}, CREDENTIALS
        )

        assert result.result[0].model_dump()["jumbo_30y"] == 7.05

    async def test_each_index_is_named_from_its_series_id(self, monkeypatch):
        _serve_series(monkeypatch, [{"date": date(2024, 6, 3), "OBMMIJUMBO30YF": 7.05}])
        result = await FredMortgageIndicesFetcher.fetch_data(
            {"index": "jumbo_30y"}, CREDENTIALS
        )
        columns = [
            c for c in result.result[0].model_dump(exclude_none=True) if c != "date"
        ]

        assert columns == ["jumbo_30y"]

    async def test_the_indices_run_in_published_order(self, monkeypatch):
        """Sorting the names as text would put the 15-year index first."""
        _serve_series(
            monkeypatch,
            [
                {
                    "date": date(2024, 6, 3),
                    "OBMMIC15YF": 6.3,
                    "OBMMIJUMBO30YF": 7.05,
                }
            ],
        )
        result = await FredMortgageIndicesFetcher.fetch_data(
            {"index": "conforming_15y,jumbo_30y"}, CREDENTIALS
        )
        columns = [
            c for c in result.result[0].model_dump(exclude_none=True) if c != "date"
        ]

        assert columns == ["jumbo_30y", "conforming_15y"]

    async def test_each_index_is_carried_in_its_own_column(self, monkeypatch):
        """Wide output is what lets the chart draw one line per index."""
        _serve_series(
            monkeypatch,
            [{"date": date(2024, 6, 3), "OBMMIC15YF": 6.3, "OBMMIJUMBO30YF": 7.05}],
        )
        result = await FredMortgageIndicesFetcher.fetch_data(
            {"index": "conforming_15y,jumbo_30y"}, CREDENTIALS
        )
        row = result.result[0].model_dump(exclude_none=True)

        assert row["jumbo_30y"] == 7.05
        assert row["conforming_15y"] == 6.3

    async def test_no_observations_is_reported_as_empty(self, monkeypatch):
        _serve_series(monkeypatch, [])

        with pytest.raises(EmptyDataError, match="The request was returned empty"):
            await FredMortgageIndicesFetcher.fetch_data(
                {"index": "jumbo_30y"}, CREDENTIALS
            )


class TestHighQualityMarketBonds:
    """Reading the HQM corporate bond yield curve out of a release table."""

    @staticmethod
    def _serve(monkeypatch, elements: dict) -> list:
        """Answer every release table read with ``elements``, collecting the URLs."""
        urls: list = []

        async def answer(url, **kwargs):
            urls.append(url)
            return {"elements": elements}

        monkeypatch.setattr("openbb_fred.utils.rate_limiter.fred_get", answer)

        return urls

    async def test_a_maturity_without_an_observation_is_dropped(self, monkeypatch):
        self._serve(
            monkeypatch,
            {
                "1": {
                    "name": "1-YEAR",
                    "observation_value": "4.5",
                    "observation_date": "2024-06-01",
                },
                "2": {
                    "name": "2-YEAR",
                    "observation_value": "",
                    "observation_date": "2024-06-01",
                },
                "3": {
                    "name": "10-YEAR",
                    "observation_value": "4.1",
                    "observation_date": "2024-06-01",
                },
            },
        )
        result = await FredHighQualityMarketCorporateBondFetcher.fetch_data(
            {}, CREDENTIALS
        )

        assert [d.maturity for d in result] == ["year_1", "year_10"]

    async def test_the_published_rate_is_passed_through_unscaled(self, monkeypatch):
        """The release table publishes percent, and that is what is returned."""
        self._serve(
            monkeypatch,
            {
                "1": {
                    "name": "1-YEAR",
                    "observation_value": "4.5",
                    "observation_date": "2024-06-01",
                }
            },
        )
        result = await FredHighQualityMarketCorporateBondFetcher.fetch_data(
            {}, CREDENTIALS
        )

        assert result[0].rate == 4.5

    async def test_the_maturities_run_by_length_and_not_by_name(self, monkeypatch):
        self._serve(
            monkeypatch,
            {
                "1": {
                    "name": "10-YEAR",
                    "observation_value": "4.1",
                    "observation_date": "2024-06-01",
                },
                "2": {
                    "name": "2-YEAR",
                    "observation_value": "4.8",
                    "observation_date": "2024-06-01",
                },
            },
        )
        result = await FredHighQualityMarketCorporateBondFetcher.fetch_data(
            {}, CREDENTIALS
        )

        assert [d.maturity for d in result] == ["year_2", "year_10"]

    async def test_the_spot_curve_reads_its_own_release_element(self, monkeypatch):
        urls = self._serve(
            monkeypatch,
            {
                "1": {
                    "name": "1-YEAR",
                    "observation_value": "4.5",
                    "observation_date": "2024-06-01",
                }
            },
        )
        await FredHighQualityMarketCorporateBondFetcher.fetch_data({}, CREDENTIALS)

        assert "element_id=219299" in urls[0]

    async def test_the_par_curve_reads_a_different_release_element(self, monkeypatch):
        urls = self._serve(
            monkeypatch,
            {
                "1": {
                    "name": "1-YEAR",
                    "observation_value": "4.5",
                    "observation_date": "2024-06-01",
                }
            },
        )
        await FredHighQualityMarketCorporateBondFetcher.fetch_data(
            {"yield_curve": "par"}, CREDENTIALS
        )

        assert "element_id=219294" in urls[0]

    async def test_a_period_with_no_release_table_contributes_nothing(
        self, monkeypatch
    ):
        async def answer(url, **kwargs):
            if "observation_date=2024-05-01" in url:
                return None
            return {
                "elements": {
                    "1": {
                        "name": "1-YEAR",
                        "observation_value": "4.5",
                        "observation_date": "2024-06-17",
                    }
                }
            }

        monkeypatch.setattr("openbb_fred.utils.rate_limiter.fred_get", answer)
        result = await FredHighQualityMarketCorporateBondFetcher.fetch_data(
            {"date": "2024-06-17,2024-05-30"}, CREDENTIALS
        )

        assert [d.date for d in result] == [date(2024, 6, 17)]

    async def test_one_request_is_made_for_each_requested_period(self, monkeypatch):
        urls = self._serve(
            monkeypatch,
            {
                "1": {
                    "name": "1-YEAR",
                    "observation_value": "4.5",
                    "observation_date": "2024-06-01",
                }
            },
        )
        await FredHighQualityMarketCorporateBondFetcher.fetch_data(
            {"date": "2024-06-17,2024-05-30"}, CREDENTIALS
        )

        assert sorted(url.split("observation_date=")[1][:10] for url in urls) == [
            "2024-05-01",
            "2024-06-01",
        ]


class TestPublishedMaturities:
    """What the packaged reference table says is published."""

    def test_the_par_yields_are_the_four_benchmarks(self):
        assert get_spot_maturities(["par_yield"]) == [2.0, 5.0, 10.0, 30.0]

    def test_the_spot_rates_run_from_one_year_to_a_century(self):
        published = get_spot_maturities(["spot_rate"])

        assert published[0] == 1.0
        assert published[-1] == 100.0

    def test_a_half_year_step_is_published(self):
        assert 1.5 in get_spot_maturities(["spot_rate"])

    def test_the_categories_combine(self):
        combined = get_spot_maturities(["spot_rate", "par_yield"])

        assert set(get_spot_maturities(["par_yield"])) <= set(combined)

    def test_an_unknown_category_publishes_nothing(self):
        assert get_spot_maturities(["not_a_category"]) == []

    def test_a_maturity_resolves_to_its_series(self):
        found = get_spot_series_id([10.0], ["par_yield"])

        assert [s["FRED Series ID"] for s in found] == ["HQMCB10YRP"]


class TestMaturityValidation:
    """A maturity that is not published is reported, not silently dropped."""

    async def test_a_maturity_above_the_range_is_reported(self):
        with pytest.raises(OpenBBError, match="Maturity not published"):
            await FREDSpotRateFetcher.fetch_data(
                {"maturity": 150.0, "category": "spot_rate"}, CREDENTIALS
            )

    async def test_a_maturity_below_the_range_is_reported(self):
        with pytest.raises(OpenBBError, match="Maturity not published"):
            await FREDSpotRateFetcher.fetch_data(
                {"maturity": 0.25, "category": "spot_rate"}, CREDENTIALS
            )

    async def test_a_maturity_between_the_steps_is_reported(self):
        with pytest.raises(OpenBBError, match="Maturity not published"):
            await FREDSpotRateFetcher.fetch_data(
                {"maturity": 10.25, "category": "spot_rate"}, CREDENTIALS
            )

    async def test_a_maturity_the_other_category_lacks_is_reported(self):
        with pytest.raises(OpenBBError, match="Maturity not published"):
            await FREDSpotRateFetcher.fetch_data(
                {"maturity": 3.0, "category": "par_yield"}, CREDENTIALS
            )

    async def test_the_message_names_what_is_published(self):
        with pytest.raises(OpenBBError, match="2.0, 5.0, 10.0, 30.0"):
            await FREDSpotRateFetcher.fetch_data(
                {"maturity": 3.0, "category": "par_yield"}, CREDENTIALS
            )

    async def test_an_unknown_category_is_reported(self):
        with pytest.raises(OpenBBError, match="No spot rates are published"):
            await FREDSpotRateFetcher.fetch_data(
                {"maturity": 10.0, "category": "not_a_category"}, CREDENTIALS
            )

    async def test_one_bad_maturity_among_good_ones_is_reported(self):
        with pytest.raises(OpenBBError, match="150.0"):
            await FREDSpotRateFetcher.fetch_data(
                {"maturity": "10,150", "category": "spot_rate"}, CREDENTIALS
            )

    async def test_a_maturity_that_is_not_a_number_is_reported(self):
        with pytest.raises(OpenBBError, match="maturity must be a float"):
            await FREDSpotRateFetcher.fetch_data(
                {"maturity": "ten", "category": "spot_rate"}, CREDENTIALS
            )


class TestExtract:
    """Reading the series a request resolves to."""

    async def test_every_resolved_series_is_read(self, monkeypatch):
        asked: list = []

        async def answer(series_ids, api_key, **kwargs):
            asked.extend(series_ids)
            return [[{"date": "2024-01-01", "value": "1.0"}] for _ in series_ids]

        monkeypatch.setattr("openbb_fred.utils.api.get_observations_many", answer)
        await FREDSpotRateFetcher.fetch_data(
            {"maturity": "2,10", "category": "par_yield"}, CREDENTIALS
        )

        assert asked == ["HQMCB2YRP", "HQMCB10YRP"]

    async def test_each_tenor_is_one_point_on_the_curve(self, monkeypatch):
        """A spot curve is read across maturities, not along a date axis."""

        async def answer(series_ids, api_key, **kwargs):
            return [[{"date": "2024-01-01", "value": "1.0"}] for _ in series_ids]

        monkeypatch.setattr("openbb_fred.utils.api.get_observations_many", answer)
        rows = await FREDSpotRateFetcher.fetch_data(
            {"maturity": "2,10", "category": "par_yield"}, CREDENTIALS
        )

        assert [d.maturity for d in rows] == ["year_2", "year_10"]

    async def test_the_cache_switch_reaches_the_transport(self, monkeypatch):
        seen: list = []

        async def answer(series_ids, api_key, **kwargs):
            seen.append(kwargs.get("use_cache"))
            return [[{"date": "2024-01-01", "value": "1.0"}] for _ in series_ids]

        monkeypatch.setattr("openbb_fred.utils.api.get_observations_many", answer)
        await FREDSpotRateFetcher.fetch_data(
            {"maturity": 10.0, "category": "par_yield", "use_cache": False},
            CREDENTIALS,
        )

        assert seen == [False]


class TestSpotRateData:
    """Shaping the observations a spot rate request returns."""

    async def test_a_gap_in_the_series_is_reported_as_no_rate(self, monkeypatch):
        async def answer(series_ids, api_key, **kwargs):
            return [
                [
                    {"date": "2024-01-01", "value": "4.5"},
                    {"date": "2024-01-02", "value": "."},
                    {"date": "2024-01-03", "value": "4.7"},
                ]
                for _ in series_ids
            ]

        monkeypatch.setattr("openbb_fred.utils.api.get_observations_many", answer)
        rows = await FREDSpotRateFetcher.fetch_data(
            {"maturity": 10.0, "category": "par_yield"}, CREDENTIALS
        )

        assert [d.rate for d in rows] == [4.5, None, 4.7]

    async def test_no_observations_is_reported_as_empty(self, monkeypatch):
        async def answer(series_ids, api_key, **kwargs):
            return [[] for _ in series_ids]

        monkeypatch.setattr("openbb_fred.utils.api.get_observations_many", answer)

        with pytest.raises(EmptyDataError, match="The request was returned empty"):
            await FREDSpotRateFetcher.fetch_data(
                {"maturity": 10.0, "category": "par_yield"}, CREDENTIALS
            )


class TestTipsYields:
    """Reading the TIPS release, then the observations of each security."""

    async def test_a_failed_catalog_read_is_reported(self, monkeypatch):
        _fail_tips_catalog(monkeypatch, OpenBBError("Release 72 is unavailable."))

        with pytest.raises(OpenBBError, match="Release 72 is unavailable"):
            await FredTipsYieldsFetcher.fetch_data({}, CREDENTIALS)

    async def test_a_silent_catalog_failure_names_the_exception_type(self, monkeypatch):
        _fail_tips_catalog(monkeypatch, RuntimeError())

        with pytest.raises(
            OpenBBError, match=r"FRED request failed \(RuntimeError\)\."
        ):
            await FredTipsYieldsFetcher.fetch_data({}, CREDENTIALS)

    async def test_a_failed_observation_read_is_reported(self, monkeypatch):
        _serve_tips_catalog(monkeypatch)
        _fail_series(monkeypatch, OpenBBError("Observations are unavailable."))

        with pytest.raises(OpenBBError, match="Observations are unavailable"):
            await FredTipsYieldsFetcher.fetch_data({}, CREDENTIALS)

    async def test_a_silent_observation_failure_names_the_exception_type(
        self, monkeypatch
    ):
        _serve_tips_catalog(monkeypatch)
        _fail_series(monkeypatch, TimeoutError())

        with pytest.raises(
            OpenBBError, match=r"FRED request failed \(TimeoutError\)\."
        ):
            await FredTipsYieldsFetcher.fetch_data({}, CREDENTIALS)

    async def test_a_discontinued_security_is_not_read(self, monkeypatch):
        _serve_tips_catalog(monkeypatch)
        asked = _serve_series(
            monkeypatch,
            [{"date": date(2024, 7, 17), "DTP5J29": 2.5, "DTP10J32": 2.1}],
        )
        await FredTipsYieldsFetcher.fetch_data({}, CREDENTIALS)

        assert asked[0]["symbol"].split(",") == ["DTP5J29", "DTP10J32"]

    async def test_a_maturity_narrows_the_securities_read(self, monkeypatch):
        _serve_tips_catalog(monkeypatch)
        asked = _serve_series(
            monkeypatch, [{"date": date(2024, 7, 17), "DTP10J32": 2.1}]
        )
        await FredTipsYieldsFetcher.fetch_data({"maturity": "10"}, CREDENTIALS)

        assert asked[0]["symbol"] == "DTP10J32"

    async def test_the_published_yield_is_passed_through_unscaled(self, monkeypatch):
        """FRED publishes these yields in percent, and that is what is returned."""
        _serve_tips_catalog(monkeypatch)
        _serve_series(
            monkeypatch,
            [{"date": date(2024, 7, 17), "DTP5J29": 2.5, "DTP10J32": 2.1}],
        )
        result = await FredTipsYieldsFetcher.fetch_data({}, CREDENTIALS)

        assert [d.value for d in result.result] == [2.5, 2.1]

    async def test_the_securities_run_by_due_date(self, monkeypatch):
        _serve_tips_catalog(monkeypatch)
        _serve_series(
            monkeypatch,
            [{"date": date(2024, 7, 17), "DTP10J32": 2.1, "DTP5J29": 2.5}],
        )
        result = await FredTipsYieldsFetcher.fetch_data({}, CREDENTIALS)

        assert [d.due for d in result.result] == [date(2029, 4, 15), date(2032, 1, 15)]

    async def test_each_row_is_named_for_its_security(self, monkeypatch):
        _serve_tips_catalog(monkeypatch)
        _serve_series(monkeypatch, [{"date": date(2024, 7, 17), "DTP5J29": 2.5}])
        result = await FredTipsYieldsFetcher.fetch_data({}, CREDENTIALS)

        assert result.result[0].name == "5-Year 0.125% TIPS Note, Due 04/15/2029"

    async def test_the_metadata_title_is_rewritten_to_tips(self, monkeypatch):
        _serve_tips_catalog(monkeypatch)
        _serve_series(
            monkeypatch,
            [{"date": date(2024, 7, 17), "DTP5J29": 2.5}],
            {"DTP5J29": {"title": "5-Year 0.125% Treasury Inflation-Indexed Note"}},
        )
        result = await FredTipsYieldsFetcher.fetch_data({}, CREDENTIALS)

        assert result.metadata["DTP5J29"]["title"] == (
            "5-Year 0.125% TIPS Note, Due 04/15/2029"
        )

    async def test_no_observations_is_reported_as_empty(self, monkeypatch):
        _serve_tips_catalog(monkeypatch)
        _serve_series(monkeypatch, [{"date": date(2024, 7, 17), "DTP5J29": None}])

        with pytest.raises(EmptyDataError, match="was returned empty"):
            await FredTipsYieldsFetcher.fetch_data({}, CREDENTIALS)


class TestFredYieldCurve:
    """Reading a treasury yield curve out of the constant maturity series."""

    async def test_an_empty_series_read_is_reported(self, monkeypatch):
        async def answer(params, credentials=None, **kwargs):
            return []

        _patch_series(monkeypatch, answer)

        with pytest.raises(EmptyDataError, match="The request was returned empty"):
            await FREDYieldCurveFetcher.fetch_data({}, CREDENTIALS)

    async def test_an_annotated_result_holding_no_rows_is_reported(self, monkeypatch):
        _serve_series(monkeypatch, [])

        with pytest.raises(EmptyDataError, match="The request was returned empty"):
            await FREDYieldCurveFetcher.fetch_data({}, CREDENTIALS)

    async def test_every_maturity_of_the_curve_is_read(self, monkeypatch):
        asked = _serve_series(
            monkeypatch, [{"date": date(2024, 6, 3), "DFII5": 2.1, "DFII10": 2.2}]
        )
        await FREDYieldCurveFetcher.fetch_data(
            {"yield_curve_type": "real"}, CREDENTIALS
        )

        assert asked[0]["symbol"] == "DFII5,DFII7,DFII10,DFII20,DFII30"

    async def test_the_published_rate_is_passed_through_unscaled(self, monkeypatch):
        """FRED publishes this rate in percent, and that is what is returned."""
        _serve_series(
            monkeypatch, [{"date": date(2024, 6, 3), "DFII5": 2.1, "DFII10": 2.2}]
        )
        result = await FREDYieldCurveFetcher.fetch_data(
            {"yield_curve_type": "real"}, CREDENTIALS
        )
        rates = {d.maturity: d.rate for d in result}

        assert rates["year_5"] == 2.1


class TestYieldCurveSchema:
    """What the yield curve model declares, beside the rates it carries."""

    def test_the_rate_is_a_declared_field(self):
        """It reached the client as an undeclared extra, invisible to the builder."""
        assert "rate" in FREDYieldCurveData.model_fields

    async def test_the_computed_maturity_still_reads_in_years(self, monkeypatch):
        _serve_series(
            monkeypatch, [{"date": date(2024, 6, 3), "DFII5": 2.1, "DFII10": 2.2}]
        )
        result = await FREDYieldCurveFetcher.fetch_data(
            {"yield_curve_type": "real"}, CREDENTIALS
        )
        years = {d.maturity: d.maturity_years for d in result}

        assert years["year_5"] == 5.0

    def test_a_maturity_carrying_no_unit_has_no_length_in_years(self):
        assert FREDYieldCurveData(maturity="30y").maturity_years is None


FIXED_INCOME_WIDGETS = [
    "fixedincome_government_yield_curve_fred_obb",
    "fixedincome_government_tips_yields_fred_obb",
    "fixedincome_corporate_hqm_fred_obb",
    "fixedincome_corporate_spot_rates_fred_obb",
    "fixedincome_bond_indices_fred_obb",
    "fixedincome_mortgage_indices_fred_obb",
    "fixedincome_corporate_commercial_paper_fred_obb",
]

PERCENT_COLUMNS = [
    ("fixedincome_corporate_spot_rates_fred_obb", "rate"),
    ("fixedincome_government_yield_curve_fred_obb", "rate"),
    ("fixedincome_government_tips_yields_fred_obb", "value"),
    ("fixedincome_corporate_hqm_fred_obb", "rate"),
]

WIDE_WIDGETS = [
    "fixedincome_bond_indices_fred_obb",
    "fixedincome_mortgage_indices_fred_obb",
    "fixedincome_corporate_commercial_paper_fred_obb",
]


@pytest.fixture(scope="module")
def widget():
    """Return the widget definition served for one declared command."""
    from openbb_core.api.rest_api import app
    from openbb_platform_api.utils.widgets import build_json

    from openbb_fred.fred_router import widget_id

    registry = build_json(app.openapi(), [])

    def served(declared: str) -> dict:
        published = widget_id(declared)

        if published not in registry:
            pytest.skip("the namespace owner serves this widget in this installation")

        return registry[published]

    return served


@pytest.fixture(scope="module")
def columns(widget):
    """Return the emitted column definitions of one widget, keyed by field."""

    def served(declared: str) -> dict:
        return {
            column["field"]: column
            for column in widget(declared)["data"]["table"]["columnsDefs"]
        }

    return served


class TestFixedIncomeChartMetadata:
    """The chart role every fixed income column is served to the Workspace with."""

    def test_the_yield_curve_plots_the_rate(self, columns):
        """The rate was absent from the schema, so nothing could be plotted."""
        assert (
            columns("fixedincome_government_yield_curve_fred_obb")["rate"][
                "chartDataType"
            ]
            == "series"
        )

    def test_the_yield_curve_runs_by_maturity(self, columns):
        """A curve is rate by maturity, so the maturity is the axis."""
        assert (
            columns("fixedincome_government_yield_curve_fred_obb")["maturity"][
                "chartDataType"
            ]
            == "category"
        )

    def test_the_yield_curve_does_not_run_by_date(self, columns):
        """Every point of one curve shares a date, so the date is no axis."""
        assert (
            columns("fixedincome_government_yield_curve_fred_obb")["date"][
                "chartDataType"
            ]
            == "excluded"
        )

    def test_the_computed_maturity_in_years_is_not_plotted(self, columns):
        """A computed field carries widget config the same as a declared one."""
        assert (
            columns("fixedincome_government_yield_curve_fred_obb")["maturity_years"][
                "chartDataType"
            ]
            == "excluded"
        )

    def test_the_yield_curve_keeps_every_column_in_the_table(self, columns):
        served = columns("fixedincome_government_yield_curve_fred_obb")

        assert set(served) == {"date", "maturity", "rate", "maturity_years"}

    def test_each_tips_security_is_charted_as_its_own_line(self, columns):
        served = columns("fixedincome_government_tips_yields_fred_obb")

        assert served["symbol"]["chartDataType"] == "category"
        assert served["value"]["chartDataType"] == "series"

    def test_the_tips_labels_stay_out_of_the_chart(self, columns):
        """The due date would otherwise compete with the observation date."""
        served = columns("fixedincome_government_tips_yields_fred_obb")

        assert served["due"]["chartDataType"] == "excluded"
        assert served["name"]["chartDataType"] == "excluded"

    @pytest.mark.parametrize(
        "declared",
        [
            "fixedincome_bond_indices_fred_obb",
            "fixedincome_mortgage_indices_fred_obb",
            "fixedincome_corporate_commercial_paper_fred_obb",
        ],
    )
    def test_a_wide_widget_declares_every_series_it_can_publish(
        self, columns, declared
    ):
        """A declared column is what carries the header, the role and the unit."""
        served = columns(declared)
        roles = {c: served[c]["chartDataType"] for c in served}

        assert roles.pop("date") == "time"
        assert roles
        assert set(roles.values()) == {"series"}

    @pytest.mark.parametrize(
        "declared",
        [
            "fixedincome_government_yield_curve_fred_obb",
            "fixedincome_corporate_hqm_fred_obb",
            "fixedincome_corporate_spot_rates_fred_obb",
        ],
    )
    def test_a_curve_is_charted_by_maturity_not_by_date(self, columns, declared):
        """Every row shares one date, so a date axis draws one stack of dots."""
        served = columns(declared)

        assert served["date"]["chartDataType"] == "excluded"
        assert served["maturity"]["chartDataType"] == "category"
        assert served["rate"]["chartDataType"] == "series"


class TestFixedIncomePercentFormatting:
    """How the Workspace is told to format every fixed income rate column."""

    @pytest.mark.parametrize(("declared", "field"), PERCENT_COLUMNS)
    def test_a_published_rate_is_formatted_as_a_percent(self, columns, declared, field):
        """FRED publishes 5.33 for 5.33%, so the browser must not scale it again."""
        assert columns(declared)[field]["formatterFn"] == "percent"

    @pytest.mark.parametrize("declared", FIXED_INCOME_WIDGETS)
    def test_no_column_is_scaled_a_second_time_in_the_browser(self, widget, declared):
        """normalizedPercent multiplies by 100, rendering the raw 5.33 as 533%."""
        assert "normalizedPercent" not in json.dumps(widget(declared))

    @pytest.mark.parametrize("declared", WIDE_WIDGETS)
    def test_a_wide_widget_formats_every_rate_as_a_percent(self, columns, declared):
        """FRED publishes 5.33 for 5.33%, so the browser must not scale it again."""
        if declared == "fixedincome_bond_indices_fred_obb":
            pytest.skip("one column serves a yield and a total return alike")

        served = columns(declared)
        formats = {served[c]["formatterFn"] for c in served if c != "date"}

        assert formats == {"percent"}
