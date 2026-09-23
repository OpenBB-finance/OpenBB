"""Tests for the FRED request builders and typed endpoint access."""

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_fred.utils.api import (
    GEO_ROOT_URL,
    ROOT_URL,
    build_url,
    get_observations,
    get_observations_many,
    headers,
    observation_dates,
    observations_url,
    release_tables_url,
    unwrap_series,
)


def _params(url: str) -> dict:
    """Return the query parameters of a URL."""
    from urllib.parse import parse_qs, urlsplit

    parsed = parse_qs(urlsplit(url).query, keep_blank_values=True)

    return {k: v[0] for k, v in parsed.items()}


class TestBuildUrl:
    """The single constructor every FRED request URL is built by."""

    def test_the_key_and_format_are_always_sent(self):
        url = build_url("series", "abc")

        assert url.startswith(f"{ROOT_URL}/series?")
        assert _params(url) == {"api_key": "abc", "file_type": "json"}

    def test_a_missing_key_is_sent_empty(self):
        assert _params(build_url("series", None))["api_key"] == ""

    def test_a_leading_slash_does_not_double(self):
        assert build_url("/series", "abc").startswith(f"{ROOT_URL}/series?")

    def test_an_absent_parameter_is_left_out(self):
        assert "element_id" not in _params(build_url("series", "abc", element_id=None))

    def test_a_value_is_escaped(self):
        url = build_url("series/search", "abc", search_text="real gdp")

        assert "real%20gdp" in url or "real+gdp" in url
        assert _params(url)["search_text"] == "real gdp"

    def test_another_root_is_addressable(self):
        url = build_url("series/data", "abc", root=GEO_ROOT_URL)

        assert url.startswith(f"{GEO_ROOT_URL}/series/data?")


class TestObservationsUrl:
    """The observations request for one series."""

    def test_the_series_is_named(self):
        assert _params(observations_url("IORB", "abc"))["series_id"] == "IORB"

    def test_the_dates_become_the_observation_window(self):
        from datetime import date

        sent = _params(
            observations_url("GDP", "abc", date(2024, 1, 1), date(2024, 6, 1))
        )

        assert sent["observation_start"] == "2024-01-01"
        assert sent["observation_end"] == "2024-06-01"

    def test_a_date_already_written_is_kept(self):
        sent = _params(observations_url("GDP", "abc", "2024-01-01"))

        assert sent["observation_start"] == "2024-01-01"

    def test_no_window_sends_no_window(self):
        sent = _params(observations_url("GDP", "abc"))

        assert "observation_start" not in sent
        assert "observation_end" not in sent

    def test_the_cache_switch_never_reaches_the_api(self):
        sent = _params(observations_url("GDP", "abc", use_cache=False))

        assert "use_cache" not in sent

    def test_the_preferences_never_reach_the_api(self):
        sent = _params(observations_url("GDP", "abc", preferences={"a": 1}))

        assert "preferences" not in sent


class TestReleaseTablesUrl:
    """The release tables request the four release models share."""

    def test_the_release_and_element_are_named(self):
        sent = _params(release_tables_url("50", "12345", "abc"))

        assert sent["release_id"] == "50"
        assert sent["element_id"] == "12345"
        assert sent["include_observation_values"] == "true"

    def test_a_release_without_an_element_is_read_whole(self):
        assert "element_id" not in _params(release_tables_url("50", None, "abc"))

    def test_a_period_is_carried(self):
        sent = _params(release_tables_url("50", "1", "abc", "2024-01-01"))

        assert sent["observation_date"] == "2024-01-01"

    def test_no_period_asks_for_the_latest(self):
        assert "observation_date" not in _params(release_tables_url("50", "1", "abc"))


class TestObservationDates:
    """The periods a release table is asked for."""

    def test_nothing_asked_for_reads_the_latest(self):
        assert observation_dates(None) == [None]

    def test_a_date_becomes_its_period_start(self):
        assert observation_dates("2024-03-17") == ["2024-03-01"]

    def test_a_repeated_month_is_read_once(self):
        assert observation_dates("2024-03-17,2024-03-02") == ["2024-03-01"]

    def test_the_periods_run_oldest_first(self):
        assert observation_dates("2024-05-02,2024-01-09") == [
            "2024-01-01",
            "2024-05-01",
        ]

    def test_a_repeated_pair_does_not_corrupt_the_year(self):
        """'2011-11-11' must not become '2001-01-01'."""
        assert observation_dates("2011-11-11") == ["2011-11-01"]

    def test_a_date_object_is_read(self):
        from datetime import date

        assert observation_dates(date(2011, 11, 11)) == ["2011-11-01"]


class TestHeaders:
    """The headers a FRED request carries."""

    def test_a_request_declares_its_own_agent(self):
        sent = headers()

        assert sent["Accept"] == "application/json"
        assert sent["Accept-Encoding"] == "gzip, deflate"
        assert sent["User-Agent"]

    def test_no_key_sends_no_authorization(self):
        assert "Authorization" not in headers()

    def test_a_key_travels_as_a_bearer_token(self):
        assert headers("abc")["Authorization"] == "Bearer abc"

    def test_an_empty_key_still_declares_the_scheme(self):
        assert headers("")["Authorization"] == "Bearer "


class TestGetObservations:
    """Reading one series through the transport."""

    async def test_the_observations_are_returned(self, monkeypatch):
        async def answer(url, use_cache=True, **kwargs):
            return {"observations": [{"date": "2024-01-01", "value": "1.0"}]}

        monkeypatch.setattr("openbb_fred.utils.rate_limiter.fred_get", answer)

        assert await get_observations("GDP", "abc") == [
            {"date": "2024-01-01", "value": "1.0"}
        ]

    async def test_an_empty_response_is_reported(self, monkeypatch):
        async def answer(url, use_cache=True, **kwargs):
            return {}

        monkeypatch.setattr("openbb_fred.utils.rate_limiter.fred_get", answer)

        with pytest.raises(OpenBBError, match="No data exists for series id: GDP"):
            await get_observations("GDP", "abc")

    async def test_an_error_message_is_reported(self, monkeypatch):
        async def answer(url, use_cache=True, **kwargs):
            return {"error_message": "Bad Request."}

        monkeypatch.setattr("openbb_fred.utils.rate_limiter.fred_get", answer)

        with pytest.raises(OpenBBError, match="Bad Request."):
            await get_observations("GDP", "abc")

    async def test_the_cache_switch_reaches_the_transport(self, monkeypatch):
        seen: list = []

        async def answer(url, use_cache=True, **kwargs):
            seen.append(use_cache)
            return {"observations": []}

        monkeypatch.setattr("openbb_fred.utils.rate_limiter.fred_get", answer)
        await get_observations("GDP", "abc", use_cache=False)

        assert seen == [False]


class TestGetObservationsMany:
    """Reading many series under one rate limit."""

    async def test_the_results_line_up_with_the_series(self, monkeypatch):
        async def answer(urls, use_cache=True, **kwargs):
            return [
                {"observations": [{"series": url.split("series_id=")[1][:4]}]}
                for url in urls
            ]

        monkeypatch.setattr("openbb_fred.utils.rate_limiter.fred_get_many", answer)
        read = await get_observations_many(["AAAA", "BBBB", "CCCC"], "abc")

        assert [rows[0]["series"] for rows in read] == ["AAAA", "BBBB", "CCCC"]

    async def test_a_series_without_data_is_reported(self, monkeypatch):
        async def answer(urls, use_cache=True, **kwargs):
            return [{"observations": [{"date": "2024-01-01"}]}, {}]

        monkeypatch.setattr("openbb_fred.utils.rate_limiter.fred_get_many", answer)

        with pytest.raises(OpenBBError, match="No data exists for series id: BBBB"):
            await get_observations_many(["AAAA", "BBBB"], "abc")

    async def test_nothing_asked_for_reads_nothing(self, monkeypatch):
        asked: list = []

        async def answer(urls, use_cache=True, **kwargs):
            asked.append(list(urls))
            return []

        monkeypatch.setattr("openbb_fred.utils.rate_limiter.fred_get_many", answer)

        assert await get_observations_many([], "abc") == []
        assert asked == [[]]


class TestPublishedValue:
    """Reading one observation as a number."""

    def test_a_number_is_read(self):
        from openbb_fred.utils.api import published_value

        assert published_value("4.35") == 4.35

    @pytest.mark.parametrize("missing", [".", "", None])
    def test_a_date_with_nothing_published_reads_as_nothing(self, missing):
        from openbb_fred.utils.api import published_value

        assert published_value(missing) is None

    def test_a_value_that_is_not_a_number_reads_as_nothing(self):
        from openbb_fred.utils.api import published_value

        assert published_value([]) is None
        assert published_value("n/a") is None


class TestUnwrapSeries:
    """Splitting a series fetch into its rows and metadata."""

    def test_an_annotated_result_gives_up_both_halves(self):
        from openbb_core.provider.abstract.annotated_result import AnnotatedResult

        rows, metadata = unwrap_series(
            AnnotatedResult(result=[1, 2], metadata={"GDP": {"title": "GDP"}})
        )

        assert rows == [1, 2]
        assert metadata == {"GDP": {"title": "GDP"}}

    def test_rows_on_their_own_carry_no_metadata(self):
        assert unwrap_series([1, 2]) == ([1, 2], {})

    def test_nothing_reads_as_empty(self):
        assert unwrap_series(None) == ([], {})

    def test_an_annotated_result_without_metadata_reads_as_empty(self):
        from openbb_core.provider.abstract.annotated_result import AnnotatedResult

        assert unwrap_series(AnnotatedResult(result=[1], metadata=None)) == ([1], {})
