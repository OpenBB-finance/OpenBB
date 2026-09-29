"""Tests for the FRED-native search, series and regional data models."""

from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_fred.models.regional import FredRegionalDataFetcher, FredRegionalQueryParams
from openbb_fred.models.search import FredSearchFetcher
from openbb_fred.models.series import FredSeriesFetcher

CREDENTIALS = {"fred_api_key": "test-key"}

GDP = {
    "id": "GDPC1",
    "realtime_start": "2024-10-01",
    "realtime_end": "2024-10-01",
    "title": "Real Gross Domestic Product",
    "observation_start": "1947-01-01",
    "observation_end": "2024-07-01",
    "frequency": "Quarterly",
    "frequency_short": "Q",
    "units": "Billions of Chained 2017 Dollars",
    "units_short": "Bil. of Chn. 2017 $",
    "seasonal_adjustment": "Seasonally Adjusted Annual Rate",
    "seasonal_adjustment_short": "SAAR",
    "last_updated": "2024-09-26 07:56:01-05",
    "popularity": 91,
    "group_popularity": 91,
    "notes": "BEA Account Code: A191RX",
}
UNEMPLOYMENT = {
    "id": "UNRATE",
    "realtime_start": "2024-10-01",
    "realtime_end": "2024-10-01",
    "title": "Unemployment Rate",
    "observation_start": "1948-01-01",
    "observation_end": "2024-08-01",
    "frequency": "Monthly",
    "frequency_short": "M",
    "units": "Percent",
    "units_short": "%",
    "seasonal_adjustment": "Seasonally Adjusted",
    "seasonal_adjustment_short": "SA",
    "last_updated": "2024-09-06 07:44:02-05",
    "popularity": 85,
    "group_popularity": 85,
    "notes": "The unemployment rate represents the number of unemployed.",
}
SERIESS = {"count": 2, "seriess": [GDP, UNEMPLOYMENT]}
RELEASES = {
    "releases": [
        {
            "id": 82,
            "realtime_start": "2024-10-01",
            "realtime_end": "2024-10-01",
            "name": "Gross Domestic Product",
            "press_release": True,
            "link": "https://www.bea.gov/data/gdp/gross-domestic-product",
        },
        {
            "id": 10,
            "realtime_start": "2024-10-01",
            "realtime_end": "2024-10-01",
            "name": "Consumer Price Index",
            "press_release": True,
            "link": "https://www.bls.gov/cpi/",
        },
    ]
}
SERIES_GROUP = {
    "series_group": {
        "title": "Per Capita Personal Income",
        "region_type": "state",
        "series_group": 882,
        "season": "NSA",
        "units": "Dollars",
        "frequency": "Annual",
        "min_date": "1929-01-01",
        "max_date": "2023-01-01",
    }
}
REGIONAL = {
    "meta": {
        "title": "Per Capita Personal Income by State",
        "region": "state",
        "seasonality": "Not Seasonally Adjusted",
        "units": "Dollars",
        "frequency": "Annual",
        "data": {
            "2022-01-01": [
                {
                    "region": "Alabama",
                    "code": 1,
                    "value": "50637",
                    "series_id": "ALPCPI",
                },
                {
                    "region": "Alaska",
                    "code": 2,
                    "value": "66130",
                    "series_id": "AKPCPI",
                },
            ],
            "2023-01-01": [
                {
                    "region": "Alabama",
                    "code": 1,
                    "value": "52034",
                    "series_id": "ALPCPI",
                },
                {
                    "region": "Alaska",
                    "code": 2,
                    "value": "69414",
                    "series_id": "AKPCPI",
                },
            ],
        },
    }
}


def _transport(answer, seen=None):
    """Return a ``fred_get`` stand-in answering from ``answer``."""
    from copy import deepcopy

    async def fake(url, **kwargs):
        if seen is not None:
            seen.append(url)
        return deepcopy(answer(url) if callable(answer) else answer)

    return fake


def _serve(monkeypatch, answer, seen=None):
    """Point the FRED transport at ``answer`` for the duration of a test."""
    monkeypatch.setattr(
        "openbb_fred.utils.rate_limiter.fred_get", _transport(answer, seen)
    )


def _raiser(error):
    """Return a ``fred_get`` stand-in that fails with ``error``."""

    async def fake(url, **kwargs):
        raise error

    return fake


class TestSearchQueryTransform:
    """How a search request is read before it is sent."""

    def test_a_release_id_alone_asks_for_that_release(self):
        query = FredSearchFetcher.transform_query({"release_id": 82})

        assert query.search_type == "release"

    def test_an_empty_request_lists_the_releases(self):
        query = FredSearchFetcher.transform_query({})

        assert query.search_type == "release" and query.release_id is None

    def test_a_query_is_read_as_a_full_text_search(self):
        query = FredSearchFetcher.transform_query({"query": "gdp"})

        assert query.search_type == "full_text"

    def test_a_full_text_search_without_a_query_is_reported(self):
        with pytest.raises(OpenBBError, match="A query is required"):
            FredSearchFetcher.transform_query(
                {"release_id": 82, "search_type": "full_text"}
            )

    def test_a_series_id_search_without_a_query_is_reported(self):
        with pytest.raises(OpenBBError, match="A query is required"):
            FredSearchFetcher.transform_query(
                {"release_id": 82, "search_type": "series_id"}
            )

    def test_a_series_id_lookup_needs_no_query(self):
        query = FredSearchFetcher.transform_query({"series_id": "ALPCPI"})

        assert query.series_id == "ALPCPI"

    def test_a_text_search_with_nothing_to_search_for_lists_the_releases(self):
        query = FredSearchFetcher.transform_query({"search_type": "full_text"})

        assert query.search_type == "release"

    def test_excluding_tags_without_naming_tags_is_reported(self):
        with pytest.raises(OpenBBError, match="requires 'tag_names' to be set"):
            FredSearchFetcher.transform_query(
                {"query": "gdp", "exclude_tag_names": "oecd"}
            )

    def test_excluded_tags_are_accepted_alongside_tags(self):
        query = FredSearchFetcher.transform_query(
            {"query": "gdp", "tag_names": "usa", "exclude_tag_names": "oecd"}
        )

        assert query.exclude_tag_names == "oecd"


class TestSeriesGroupLookup:
    """Resolving a series id to the group that carries its regional data."""

    async def test_every_named_series_is_looked_up(self, monkeypatch):
        seen: list = []
        _serve(monkeypatch, SERIES_GROUP, seen)
        results = await FredSearchFetcher.fetch_data(
            {"series_id": "ALPCPI,AKPCPI"}, CREDENTIALS
        )

        assert sorted(r.series_id for r in results) == ["AKPCPI", "ALPCPI"]
        assert len(seen) == 2

    async def test_the_lookup_reads_the_geographic_endpoint(self, monkeypatch):
        seen: list = []
        _serve(monkeypatch, SERIES_GROUP, seen)
        await FredSearchFetcher.fetch_data({"series_id": "ALPCPI"}, CREDENTIALS)

        assert seen[0].startswith("https://api.stlouisfed.org/geofred/series/group?")
        assert "series_id=ALPCPI" in seen[0]

    async def test_the_group_id_is_returned_as_text(self, monkeypatch):
        _serve(monkeypatch, SERIES_GROUP)
        results = await FredSearchFetcher.fetch_data(
            {"series_id": "ALPCPI"}, CREDENTIALS
        )

        assert results[0].series_group == "882"

    async def test_the_group_carries_the_fields_a_regional_query_needs(
        self, monkeypatch
    ):
        _serve(monkeypatch, SERIES_GROUP)
        results = await FredSearchFetcher.fetch_data(
            {"series_id": "ALPCPI"}, CREDENTIALS
        )
        found = results[0]

        assert found.region_type == "state"
        assert found.units == "Dollars"
        assert found.frequency == "Annual"
        assert found.seasonal_adjustment == "NSA"
        assert found.observation_start == date(1929, 1, 1)

    async def test_a_series_without_geographic_data_is_dropped(self, monkeypatch):
        def answer(url):
            return SERIES_GROUP if "ALPCPI" in url else {"series_group": None}

        _serve(monkeypatch, answer)
        results = await FredSearchFetcher.fetch_data(
            {"series_id": "ALPCPI,SP500"}, CREDENTIALS
        )

        assert [r.series_id for r in results] == ["ALPCPI"]

    async def test_a_series_id_overrides_the_other_parameters(self, monkeypatch):
        seen: list = []
        _serve(monkeypatch, SERIES_GROUP, seen)
        results = await FredSearchFetcher.fetch_data(
            {"query": "gdp", "series_id": "ALPCPI", "limit": 1}, CREDENTIALS
        )

        assert seen[0].startswith("https://api.stlouisfed.org/geofred/series/group?")
        assert [r.series_id for r in results] == ["ALPCPI"]

    async def test_no_geographic_data_at_all_is_reported(self, monkeypatch):
        _serve(monkeypatch, {"series_group": None})

        with pytest.raises(EmptyDataError, match="No results found for the provided"):
            await FredSearchFetcher.fetch_data({"series_id": "SP500"}, CREDENTIALS)


class TestReleaseListing:
    """Listing every release FRED publishes."""

    async def test_every_release_is_listed(self, monkeypatch):
        _serve(monkeypatch, RELEASES)
        results = await FredSearchFetcher.fetch_data({}, CREDENTIALS)

        assert [r.name for r in results] == [
            "Gross Domestic Product",
            "Consumer Price Index",
        ]

    async def test_a_release_carries_the_link_to_its_publisher(self, monkeypatch):
        _serve(monkeypatch, RELEASES)
        results = await FredSearchFetcher.fetch_data({}, CREDENTIALS)

        assert results[1].url == "https://www.bls.gov/cpi/"
        assert results[1].press_release is True

    async def test_the_listing_reads_the_releases_endpoint(self, monkeypatch):
        seen: list = []
        _serve(monkeypatch, RELEASES, seen)
        await FredSearchFetcher.fetch_data({}, CREDENTIALS)

        assert seen == [
            "https://api.stlouisfed.org/fred/releases?api_key=test-key&file_type=json"
        ]

    async def test_the_release_id_is_returned_as_text(self, monkeypatch):
        _serve(monkeypatch, RELEASES)
        results = await FredSearchFetcher.fetch_data({}, CREDENTIALS)

        assert [r.release_id for r in results] == ["82", "10"]

    async def test_a_listing_is_narrowed_by_the_query(self, monkeypatch):
        _serve(monkeypatch, RELEASES)
        results = await FredSearchFetcher.fetch_data(
            {"query": "Consumer", "search_type": "release"}, CREDENTIALS
        )

        assert [r.release_id for r in results] == ["10"]

    async def test_an_unexpected_listing_response_is_reported(self, monkeypatch):
        _serve(monkeypatch, {})

        with pytest.raises(OpenBBError, match="Unexpected result while retrieving"):
            await FredSearchFetcher.fetch_data({}, CREDENTIALS)


class TestReleaseSeries:
    """Reading the series that belong to one release."""

    async def test_the_series_of_a_release_are_read(self, monkeypatch):
        seen: list = []
        _serve(monkeypatch, SERIESS, seen)
        results = await FredSearchFetcher.fetch_data({"release_id": 82}, CREDENTIALS)

        assert "/fred/release/series?" in seen[0]
        assert "release_id=82" in seen[0]
        assert [r.series_id for r in results] == ["UNRATE", "GDPC1"]

    async def test_the_search_text_is_not_sent_for_a_release(self, monkeypatch):
        seen: list = []
        _serve(monkeypatch, SERIESS, seen)
        await FredSearchFetcher.fetch_data(
            {"release_id": 82, "query": "rate"}, CREDENTIALS
        )

        assert "search_text" not in seen[0]

    async def test_search_rank_ordering_is_not_sent_for_a_release(self, monkeypatch):
        seen: list = []
        _serve(monkeypatch, SERIESS, seen)
        await FredSearchFetcher.fetch_data(
            {"release_id": 82, "order_by": "search_rank"}, CREDENTIALS
        )

        assert "order_by" not in seen[0]

    async def test_another_ordering_is_sent_for_a_release(self, monkeypatch):
        seen: list = []
        _serve(monkeypatch, SERIESS, seen)
        await FredSearchFetcher.fetch_data(
            {"release_id": 82, "order_by": "popularity"}, CREDENTIALS
        )

        assert "order_by=popularity" in seen[0]

    async def test_the_limit_is_applied_here_and_not_sent(self, monkeypatch):
        seen: list = []
        _serve(monkeypatch, SERIESS, seen)
        results = await FredSearchFetcher.fetch_data(
            {"release_id": 82, "limit": 1}, CREDENTIALS
        )

        assert "limit" not in seen[0]
        assert len(results) == 1


class TestFullTextSearch:
    """Searching the whole of FRED for matching series."""

    async def test_the_search_endpoint_carries_the_query(self, monkeypatch):
        seen: list = []
        _serve(monkeypatch, SERIESS, seen)
        await FredSearchFetcher.fetch_data({"query": "rate"}, CREDENTIALS)

        assert "/fred/series/search?" in seen[0]
        assert "search_text=rate" in seen[0]

    async def test_a_term_matches_any_field_of_a_row(self, monkeypatch):
        _serve(monkeypatch, SERIESS)
        results = await FredSearchFetcher.fetch_data({"query": "rate"}, CREDENTIALS)

        assert sorted(r.series_id for r in results) == ["GDPC1", "UNRATE"]

    async def test_a_row_the_term_misses_is_dropped(self, monkeypatch):
        _serve(monkeypatch, SERIESS)
        results = await FredSearchFetcher.fetch_data({"query": "gdp"}, CREDENTIALS)

        assert [r.series_id for r in results] == ["GDPC1"]

    async def test_every_term_of_a_query_must_match(self, monkeypatch):
        _serve(monkeypatch, SERIESS)
        results = await FredSearchFetcher.fetch_data(
            {"query": "gdp;quarterly"}, CREDENTIALS
        )

        assert [r.series_id for r in results] == ["GDPC1"]

    async def test_a_query_no_row_satisfies_is_reported(self, monkeypatch):
        _serve(monkeypatch, SERIESS)

        with pytest.raises(EmptyDataError, match="No results found for the provided"):
            await FredSearchFetcher.fetch_data({"query": "gdp;monthly"}, CREDENTIALS)

    async def test_a_tag_narrows_the_results_further(self, monkeypatch):
        _serve(monkeypatch, SERIESS)
        results = await FredSearchFetcher.fetch_data(
            {"query": "rate", "tag_names": "quarterly"}, CREDENTIALS
        )

        assert [r.series_id for r in results] == ["GDPC1"]

    async def test_a_series_id_search_is_not_narrowed(self, monkeypatch):
        _serve(monkeypatch, SERIESS)
        results = await FredSearchFetcher.fetch_data(
            {"query": "gdp", "search_type": "series_id", "tag_names": "monthly"},
            CREDENTIALS,
        )

        assert sorted(r.series_id for r in results) == ["GDPC1", "UNRATE"]

    async def test_an_empty_result_set_is_reported(self, monkeypatch):
        _serve(monkeypatch, {"count": 0, "seriess": []})

        with pytest.raises(EmptyDataError, match="The request was returned empty"):
            await FredSearchFetcher.fetch_data({"query": "rate"}, CREDENTIALS)

    async def test_a_fred_error_code_is_reported(self, monkeypatch):
        _serve(
            monkeypatch,
            {"error_code": 400, "error_message": "Bad Request. Variable is not valid."},
        )

        with pytest.raises(OpenBBError, match="Status Code: 400"):
            await FredSearchFetcher.fetch_data({"query": "rate"}, CREDENTIALS)

    async def test_the_error_message_is_passed_through(self, monkeypatch):
        _serve(
            monkeypatch, {"error_code": 400, "error_message": "Variable is invalid."}
        )

        with pytest.raises(OpenBBError, match="Variable is invalid."):
            await FredSearchFetcher.fetch_data({"query": "rate"}, CREDENTIALS)

    async def test_a_response_that_is_not_a_search_result_is_reported(
        self, monkeypatch
    ):
        _serve(monkeypatch, [])

        with pytest.raises(OpenBBError, match="Unexpected response format"):
            await FredSearchFetcher.fetch_data({"query": "rate"}, CREDENTIALS)

    async def test_a_missing_value_reads_as_no_value(self, monkeypatch):
        _serve(monkeypatch, {"count": 1, "seriess": [{**GDP, "notes": None}]})
        results = await FredSearchFetcher.fetch_data({"query": "gdp"}, CREDENTIALS)

        assert results[0].notes is None


class TestSearchOrdering:
    """Ordering and truncating what a search returned."""

    async def test_the_default_order_is_the_newest_observation_first(self, monkeypatch):
        _serve(monkeypatch, SERIESS)
        results = await FredSearchFetcher.fetch_data({"query": "rate"}, CREDENTIALS)

        assert [r.series_id for r in results] == ["UNRATE", "GDPC1"]

    async def test_the_results_are_ordered_by_the_chosen_attribute(self, monkeypatch):
        _serve(monkeypatch, SERIESS)
        results = await FredSearchFetcher.fetch_data(
            {"query": "rate", "order_by": "popularity"}, CREDENTIALS
        )

        assert [r.popularity for r in results] == [91, 85]

    async def test_the_order_can_be_reversed(self, monkeypatch):
        _serve(monkeypatch, SERIESS)
        results = await FredSearchFetcher.fetch_data(
            {"query": "rate", "order_by": "popularity", "sort_order": "asc"},
            CREDENTIALS,
        )

        assert [r.popularity for r in results] == [85, 91]

    async def test_an_attribute_the_rows_lack_leaves_the_order_alone(self, monkeypatch):
        _serve(monkeypatch, RELEASES)
        results = await FredSearchFetcher.fetch_data(
            {"search_type": "release", "order_by": "popularity"}, CREDENTIALS
        )

        assert [r.release_id for r in results] == ["82", "10"]

    async def test_the_limit_truncates_the_results(self, monkeypatch):
        _serve(monkeypatch, SERIESS)
        results = await FredSearchFetcher.fetch_data(
            {"query": "rate", "limit": 1}, CREDENTIALS
        )

        assert [r.series_id for r in results] == ["UNRATE"]

    async def test_a_limit_above_the_result_count_keeps_everything(self, monkeypatch):
        _serve(monkeypatch, SERIESS)
        results = await FredSearchFetcher.fetch_data(
            {"query": "rate", "limit": 10}, CREDENTIALS
        )

        assert len(results) == 2


class TestSeriesQuery:
    """How a series request is read before it is sent."""

    def test_the_symbol_is_upper_cased(self):
        assert FredSeriesFetcher.transform_query({"symbol": "sp500"}).symbol == "SP500"

    def test_the_cache_is_used_by_default(self):
        assert FredSeriesFetcher.transform_query({"symbol": "SP500"}).use_cache is True


def _series_transport(observations, metadata=None, seen=None):
    """Return a ``fred_get`` stand-in serving observations and series metadata."""
    from copy import deepcopy

    meta = metadata or {}

    async def fake(url, **kwargs):
        if seen is not None:
            seen.append(url)

        series_id = url.split("series_id=")[1].split("&")[0]

        if "series/observations?" in url:
            return deepcopy({"observations": observations.get(series_id, [])})

        return deepcopy({"seriess": [meta.get(series_id, {})]})

    return fake


def _observation(day: str, value: str) -> dict:
    """Return one FRED observation as the API writes it."""
    return {
        "realtime_start": "2024-10-01",
        "realtime_end": "2024-10-01",
        "date": day,
        "value": value,
    }


SP500_META = {
    "title": "S&P 500",
    "units": "Index",
    "frequency": "Daily, Close",
    "seasonal_adjustment": "Not Seasonally Adjusted",
    "notes": "The observations are not seasonally adjusted.",
}
DGS10_META = {
    "title": "Market Yield on U.S. Treasury Securities at 10-Year Constant Maturity",
    "units": "Percent",
    "frequency": "Daily",
    "seasonal_adjustment": "Not Seasonally Adjusted",
    "notes": "Treasury Yield Curve Methodology.",
}


class TestSeriesExtract:
    """Reading the observations and metadata of one or more series."""

    async def test_one_symbol_reads_its_observations_and_its_metadata(
        self, monkeypatch
    ):
        seen: list = []
        monkeypatch.setattr(
            "openbb_fred.utils.rate_limiter.fred_get",
            _series_transport(
                {"SP500": [_observation("2024-01-02", "4742.83")]},
                {"SP500": SP500_META},
                seen,
            ),
        )
        await FredSeriesFetcher.fetch_data({"symbol": "SP500"}, CREDENTIALS)

        assert "/fred/series/observations?" in seen[0]
        assert seen[1].startswith("https://api.stlouisfed.org/fred/series?")

    async def test_every_symbol_of_a_comma_separated_request_is_read(self, monkeypatch):
        monkeypatch.setattr(
            "openbb_fred.utils.rate_limiter.fred_get",
            _series_transport(
                {
                    "SP500": [_observation("2024-01-02", "4742.83")],
                    "DGS10": [_observation("2024-01-02", "3.95")],
                },
                {"SP500": SP500_META, "DGS10": DGS10_META},
            ),
        )
        response = await FredSeriesFetcher.fetch_data(
            {"symbol": "SP500,DGS10"}, CREDENTIALS
        )

        assert response.result[0].SP500 == 4742.83
        assert response.result[0].DGS10 == 3.95

    async def test_the_metadata_describes_each_series(self, monkeypatch):
        monkeypatch.setattr(
            "openbb_fred.utils.rate_limiter.fred_get",
            _series_transport(
                {"SP500": [_observation("2024-01-02", "4742.83")]},
                {"SP500": SP500_META},
            ),
        )
        response = await FredSeriesFetcher.fetch_data({"symbol": "SP500"}, CREDENTIALS)

        assert response.metadata["SP500"]["title"] == "S&P 500"
        assert response.metadata["SP500"]["units"] == "Index"
        assert "data" not in response.metadata["SP500"]

    async def test_the_observations_are_returned_in_date_order(self, monkeypatch):
        monkeypatch.setattr(
            "openbb_fred.utils.rate_limiter.fred_get",
            _series_transport(
                {
                    "SP500": [
                        _observation("2024-01-03", "4704.81"),
                        _observation("2024-01-02", "4742.83"),
                    ]
                },
                {"SP500": SP500_META},
            ),
        )
        response = await FredSeriesFetcher.fetch_data({"symbol": "SP500"}, CREDENTIALS)

        assert [r.date for r in response.result] == [date(2024, 1, 2), date(2024, 1, 3)]

    async def test_an_unpublished_observation_is_dropped(self, monkeypatch):
        monkeypatch.setattr(
            "openbb_fred.utils.rate_limiter.fred_get",
            _series_transport(
                {
                    "SP500": [
                        _observation("2024-01-01", "."),
                        _observation("2024-01-02", "4742.83"),
                    ]
                },
                {"SP500": SP500_META},
            ),
        )
        response = await FredSeriesFetcher.fetch_data({"symbol": "SP500"}, CREDENTIALS)

        assert [r.date for r in response.result] == [date(2024, 1, 2)]

    async def test_a_date_one_series_lacks_reads_as_no_value(self, monkeypatch):
        monkeypatch.setattr(
            "openbb_fred.utils.rate_limiter.fred_get",
            _series_transport(
                {
                    "SP500": [
                        _observation("2024-01-02", "4742.83"),
                        _observation("2024-01-03", "4704.81"),
                    ],
                    "DGS10": [_observation("2024-01-02", "3.95")],
                },
                {"SP500": SP500_META, "DGS10": DGS10_META},
            ),
        )
        response = await FredSeriesFetcher.fetch_data(
            {"symbol": "SP500,DGS10"}, CREDENTIALS
        )

        assert response.result[1].DGS10 is None

    async def test_a_series_with_no_observations_is_dropped(self, monkeypatch):
        monkeypatch.setattr(
            "openbb_fred.utils.rate_limiter.fred_get",
            _series_transport(
                {"SP500": [_observation("2024-01-02", "4742.83")], "DGS10": []},
                {"SP500": SP500_META, "DGS10": DGS10_META},
            ),
        )
        response = await FredSeriesFetcher.fetch_data(
            {"symbol": "SP500,DGS10"}, CREDENTIALS
        )

        assert "DGS10" not in response.metadata
        assert not hasattr(response.result[0], "DGS10")

    async def test_a_request_answered_by_nothing_returns_no_rows(self, monkeypatch):
        monkeypatch.setattr(
            "openbb_fred.utils.rate_limiter.fred_get",
            _series_transport({"SP500": []}, {"SP500": SP500_META}),
        )
        response = await FredSeriesFetcher.fetch_data({"symbol": "SP500"}, CREDENTIALS)

        assert response.result == []

    async def test_a_response_that_is_not_an_object_reads_as_nothing(self, monkeypatch):
        _serve(monkeypatch, [])
        response = await FredSeriesFetcher.fetch_data({"symbol": "SP500"}, CREDENTIALS)

        assert response.result == []

    async def test_the_cache_switch_reaches_the_transport(self, monkeypatch):
        seen: list = []

        async def fake(url, **kwargs):
            seen.append(kwargs.get("use_cache"))
            return {"observations": [], "seriess": [{}]}

        monkeypatch.setattr("openbb_fred.utils.rate_limiter.fred_get", fake)
        await FredSeriesFetcher.fetch_data(
            {"symbol": "SP500", "use_cache": False}, CREDENTIALS
        )

        assert seen == [False, False]


class TestSeriesFailures:
    """What a failed series read reports."""

    async def test_a_reported_error_is_passed_through_unchanged(self, monkeypatch):
        original = OpenBBError("FRED API key is invalid.")
        monkeypatch.setattr(
            "openbb_fred.utils.rate_limiter.fred_get", _raiser(original)
        )

        with pytest.raises(OpenBBError) as raised:
            await FredSeriesFetcher.fetch_data({"symbol": "SP500"}, CREDENTIALS)

        assert raised.value is original

    async def test_an_unexpected_failure_is_reported_as_an_error(self, monkeypatch):
        failure = ValueError("the connection dropped")
        monkeypatch.setattr("openbb_fred.utils.rate_limiter.fred_get", _raiser(failure))

        with pytest.raises(OpenBBError, match="the connection dropped") as raised:
            await FredSeriesFetcher.fetch_data({"symbol": "SP500"}, CREDENTIALS)

        assert raised.value.__cause__ is failure

    async def test_a_failure_with_no_message_names_its_type(self, monkeypatch):
        monkeypatch.setattr(
            "openbb_fred.utils.rate_limiter.fred_get", _raiser(TimeoutError())
        )

        with pytest.raises(
            OpenBBError, match=r"FRED request failed \(TimeoutError\)\."
        ):
            await FredSeriesFetcher.fetch_data({"symbol": "SP500"}, CREDENTIALS)


class TestRegionalQueryValidation:
    """What a regional request must carry, and the start date it is given."""

    def test_a_series_group_without_a_frequency_is_reported(self):
        with pytest.raises(OpenBBError, match="frequency is a required field"):
            FredRegionalQueryParams(
                symbol="882", is_series_group=True, region_type="state", units="Dollars"
            )

    def test_a_series_group_without_a_region_type_is_reported(self):
        with pytest.raises(OpenBBError, match="region_type is a required field"):
            FredRegionalQueryParams(
                symbol="882", is_series_group=True, frequency="a", units="Dollars"
            )

    def test_a_series_group_without_units_is_reported(self):
        with pytest.raises(OpenBBError, match="units is a required field"):
            FredRegionalQueryParams(
                symbol="882", is_series_group=True, frequency="a", region_type="state"
            )

    def test_a_series_group_reads_the_whole_record_by_default(self):
        query = FredRegionalQueryParams(
            symbol="882",
            is_series_group=True,
            frequency="a",
            region_type="state",
            units="Dollars",
        )

        assert query.start_date == date(1900, 1, 1)

    def test_a_given_start_date_is_kept_for_a_series_group(self):
        query = FredRegionalQueryParams(
            symbol="882",
            is_series_group=True,
            frequency="a",
            region_type="state",
            units="Dollars",
            start_date=date(2000, 1, 1),
        )

        assert query.start_date == date(2000, 1, 1)

    def test_a_series_is_given_no_start_date(self):
        query = FredRegionalQueryParams(symbol="ALPCPI", is_series_group=False)

        assert query.start_date is None

    def test_a_given_start_date_is_kept_for_a_series(self):
        query = FredRegionalQueryParams(
            symbol="ALPCPI", is_series_group=False, start_date=date(2000, 1, 1)
        )

        assert query.start_date == date(2000, 1, 1)


class TestRegionalExtract:
    """Which geographic endpoint a regional request reads."""

    async def test_a_series_group_reads_the_regional_endpoint(self, monkeypatch):
        seen: list = []
        _serve(monkeypatch, REGIONAL, seen)
        await FredRegionalDataFetcher.fetch_data(
            {
                "symbol": "882",
                "is_series_group": True,
                "frequency": "a",
                "region_type": "state",
                "units": "Dollars",
            },
            CREDENTIALS,
        )

        assert seen[0].startswith("https://api.stlouisfed.org/geofred/regional/data?")
        assert "series_group=882" in seen[0]
        assert "region_type=state" in seen[0]

    async def test_the_season_is_sent_in_upper_case(self, monkeypatch):
        seen: list = []
        _serve(monkeypatch, REGIONAL, seen)
        await FredRegionalDataFetcher.fetch_data(
            {
                "symbol": "882",
                "is_series_group": True,
                "frequency": "a",
                "region_type": "state",
                "units": "Dollars",
                "season": "sa",
            },
            CREDENTIALS,
        )

        assert "season=SA" in seen[0]

    async def test_a_series_reads_the_series_endpoint(self, monkeypatch):
        seen: list = []
        _serve(monkeypatch, REGIONAL, seen)
        await FredRegionalDataFetcher.fetch_data(
            {"symbol": "ALPCPI", "is_series_group": False}, CREDENTIALS
        )

        assert seen[0].startswith("https://api.stlouisfed.org/geofred/series/data?")
        assert "series_id=ALPCPI" in seen[0]

    async def test_the_group_only_parameters_are_not_sent_for_a_series(
        self, monkeypatch
    ):
        seen: list = []
        _serve(monkeypatch, REGIONAL, seen)
        await FredRegionalDataFetcher.fetch_data(
            {
                "symbol": "ALPCPI",
                "is_series_group": False,
                "region_type": "state",
                "units": "Dollars",
                "season": "sa",
            },
            CREDENTIALS,
        )

        assert "region_type" not in seen[0]
        assert "season" not in seen[0]
        assert "units" not in seen[0]

    async def test_the_limit_and_end_date_are_not_sent(self, monkeypatch):
        seen: list = []
        _serve(monkeypatch, REGIONAL, seen)
        await FredRegionalDataFetcher.fetch_data(
            {
                "symbol": "ALPCPI",
                "is_series_group": False,
                "end_date": date(2023, 1, 1),
                "limit": 10,
            },
            CREDENTIALS,
        )

        assert "limit" not in seen[0]
        assert "end_date" not in seen[0]


class TestRegionalTransform:
    """Flattening the regional response into one row per region and date."""

    async def test_every_region_is_returned_for_every_date(self, monkeypatch):
        _serve(monkeypatch, REGIONAL)
        response = await FredRegionalDataFetcher.fetch_data(
            {"symbol": "ALPCPI", "is_series_group": False}, CREDENTIALS
        )

        assert [(r.date, r.region) for r in response.result] == [
            (date(2022, 1, 1), "Alabama"),
            (date(2022, 1, 1), "Alaska"),
            (date(2023, 1, 1), "Alabama"),
            (date(2023, 1, 1), "Alaska"),
        ]

    async def test_each_row_carries_its_region_code_and_series(self, monkeypatch):
        _serve(monkeypatch, REGIONAL)
        response = await FredRegionalDataFetcher.fetch_data(
            {"symbol": "ALPCPI", "is_series_group": False}, CREDENTIALS
        )
        first = response.result[0]

        assert first.code == 1
        assert first.series_id == "ALPCPI"
        assert first.value == 50637

    async def test_each_row_carries_the_units_of_the_response(self, monkeypatch):
        _serve(monkeypatch, REGIONAL)
        response = await FredRegionalDataFetcher.fetch_data(
            {"symbol": "ALPCPI", "is_series_group": False}, CREDENTIALS
        )

        assert response.result[0].units == "Dollars"

    async def test_the_metadata_describes_the_response_without_the_data(
        self, monkeypatch
    ):
        _serve(monkeypatch, REGIONAL)
        response = await FredRegionalDataFetcher.fetch_data(
            {"symbol": "ALPCPI", "is_series_group": False}, CREDENTIALS
        )

        assert response.metadata["title"] == "Per Capita Personal Income by State"
        assert response.metadata["frequency"] == "Annual"
        assert "data" not in response.metadata

    async def test_observations_after_the_end_date_are_dropped(self, monkeypatch):
        _serve(monkeypatch, REGIONAL)
        response = await FredRegionalDataFetcher.fetch_data(
            {
                "symbol": "ALPCPI",
                "is_series_group": False,
                "end_date": date(2022, 6, 30),
            },
            CREDENTIALS,
        )

        assert {r.date for r in response.result} == {date(2022, 1, 1)}

    async def test_a_response_describing_no_periods_returns_no_rows(self, monkeypatch):
        _serve(monkeypatch, {"meta": {"units": "Dollars", "data": {}}})
        response = await FredRegionalDataFetcher.fetch_data(
            {"symbol": "ALPCPI", "is_series_group": False}, CREDENTIALS
        )

        assert response.result == []
        assert response.metadata == {"units": "Dollars"}

    async def test_a_response_carrying_nothing_is_reported(self, monkeypatch):
        _serve(monkeypatch, {})

        with pytest.raises(EmptyDataError):
            await FredRegionalDataFetcher.fetch_data(
                {"symbol": "ALPCPI", "is_series_group": False}, CREDENTIALS
            )

    async def test_a_response_with_an_empty_description_is_reported(self, monkeypatch):
        _serve(monkeypatch, {"meta": None})

        with pytest.raises(EmptyDataError):
            await FredRegionalDataFetcher.fetch_data(
                {"symbol": "ALPCPI", "is_series_group": False}, CREDENTIALS
            )
