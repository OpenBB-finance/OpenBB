"""Tests for the FRED release table and economic calendar models."""

import json
from datetime import date, datetime, timedelta
from urllib.parse import parse_qs, urlparse

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_fred.models.economic_calendar import (
    FredEconomicCalendarFetcher,
    FredEconomicCalendarQueryParams,
)
from openbb_fred.models.release_table import FredReleaseTableFetcher, _quarter_start
from openbb_fred.models.search import FredSearchData

CREDENTIALS = {"fred_api_key": "test-key"}

SECTIONS = {
    "name": "Gross Domestic Product",
    "element_id": 12344,
    "release_id": "53",
    "elements": {
        "12345": {
            "element_id": 12345,
            "release_id": 53,
            "parent_id": None,
            "type": "table",
            "name": "Table 1. Gross Domestic Product",
            "level": "0",
            "children": [{"element_id": 12346}],
        },
        "12346": {
            "element_id": 12346,
            "release_id": 53,
            "parent_id": 12345,
            "type": "section",
            "name": "Personal consumption expenditures",
            "level": "1",
            "children": [],
        },
    },
}


def _tables(*rows: dict) -> dict:
    """Return the release tables payload carrying these elements."""
    return {
        "name": "SOFR Averages",
        "element_id": 1217633,
        "release_id": "483",
        "elements": {str(row["element_id"]): dict(row) for row in rows},
    }


def _series(element_id: int, value: str, **fields) -> dict:
    """Return one series element of a release table."""
    return {
        "element_id": element_id,
        "release_id": 483,
        "parent_id": 1217633,
        "type": "series",
        "level": "1",
        "series_id": f"SERIES{element_id}",
        "name": f"Series {element_id}",
        "observation_date": "2024-07-12",
        "observation_value": value,
        "children": [],
        **fields,
    }


def _periods(asked: list) -> list:
    """Return the observation date each release table request asked for."""
    return [
        parse_qs(urlparse(url).query).get("observation_date", [None])[0]
        for url in asked
    ]


@pytest.fixture(name="serve_tables")
def serve_tables_fixture(monkeypatch):
    """Answer the release tables endpoint from recorded payloads."""

    def serve(payloads: dict, frequency: str = "D", units: dict | None = None) -> list:
        asked: list = []

        async def release_info(params, credentials=None, **kwargs):
            return [
                FredSearchData.model_validate({"id": "A", "frequency_short": frequency})
            ]

        async def series_units(release_id, credentials):
            return units or {}

        async def get(url, **kwargs):
            asked.append(url)
            period = parse_qs(urlparse(url).query).get("observation_date", ["*"])[0]

            return payloads.get(period, payloads.get("*", {}))

        monkeypatch.setattr(
            "openbb_fred.models.search.FredSearchFetcher.fetch_data", release_info
        )
        monkeypatch.setattr("openbb_fred.models.release_table.get_units", series_units)
        monkeypatch.setattr("openbb_fred.utils.rate_limiter.fred_get", get)

        return asked

    return serve


class TestQuarterStart:
    """The first day of the quarter a date falls in."""

    def test_a_january_date_starts_its_quarter_in_january(self):
        assert _quarter_start("2024-01-31") == "2024-01-01"

    def test_a_may_date_starts_its_quarter_in_april(self):
        assert _quarter_start("2024-05-17") == "2024-04-01"

    def test_an_august_date_starts_its_quarter_in_july(self):
        assert _quarter_start("2024-08-02") == "2024-07-01"

    def test_a_december_date_starts_its_quarter_in_october(self):
        assert _quarter_start("2024-12-31") == "2024-10-01"

    def test_the_first_day_of_a_quarter_is_left_alone(self):
        assert _quarter_start("2024-07-01") == "2024-07-01"


class TestRequestedPeriods:
    """Which period a requested date is read as, given the release frequency."""

    async def test_a_daily_release_reads_the_day_asked_for(self, serve_tables):
        asked = serve_tables({"*": _tables(_series(1, "5.0"))})
        await FredReleaseTableFetcher.fetch_data(
            {"release_id": "483", "date": "2024-07-12"}, CREDENTIALS
        )

        assert _periods(asked) == ["2024-07-12"]

    async def test_a_monthly_release_reads_the_first_of_the_month(self, serve_tables):
        asked = serve_tables({"*": _tables(_series(1, "5.0"))}, frequency="M")
        await FredReleaseTableFetcher.fetch_data(
            {"release_id": "483", "date": "2024-07-12"}, CREDENTIALS
        )

        assert _periods(asked) == ["2024-07-01"]

    async def test_a_quarterly_release_reads_the_first_of_the_quarter(
        self, serve_tables
    ):
        asked = serve_tables({"*": _tables(_series(1, "5.0"))}, frequency="Q")
        await FredReleaseTableFetcher.fetch_data(
            {"release_id": "53", "date": "2024-05-17"}, CREDENTIALS
        )

        assert _periods(asked) == ["2024-04-01"]

    async def test_two_days_in_one_month_are_read_as_one_period(self, serve_tables):
        asked = serve_tables({"*": _tables(_series(1, "5.0"))}, frequency="M")
        await FredReleaseTableFetcher.fetch_data(
            {"release_id": "483", "date": "2024-07-05,2024-07-27"}, CREDENTIALS
        )

        assert _periods(asked) == ["2024-07-01"]

    async def test_two_days_in_one_quarter_are_read_as_one_period(self, serve_tables):
        asked = serve_tables({"*": _tables(_series(1, "5.0"))}, frequency="Q")
        await FredReleaseTableFetcher.fetch_data(
            {"release_id": "53", "date": "2024-05-17,2024-06-30"}, CREDENTIALS
        )

        assert _periods(asked) == ["2024-04-01"]

    async def test_each_requested_period_is_read(self, serve_tables):
        asked = serve_tables({"*": _tables(_series(1, "5.0"))}, frequency="M")
        await FredReleaseTableFetcher.fetch_data(
            {"release_id": "483", "date": "2024-06-05,2024-07-27"}, CREDENTIALS
        )

        assert sorted(_periods(asked)) == ["2024-06-01", "2024-07-01"]

    async def test_no_date_reads_the_latest_observation(self, serve_tables):
        asked = serve_tables({"*": _tables(_series(1, "5.0"))})
        await FredReleaseTableFetcher.fetch_data({"release_id": "483"}, CREDENTIALS)

        assert _periods(asked) == [None]


class TestMissingRelease:
    """A release id the search does not know."""

    async def test_a_release_without_information_is_reported(self, monkeypatch):
        async def release_info(params, credentials=None, **kwargs):
            return []

        monkeypatch.setattr(
            "openbb_fred.models.search.FredSearchFetcher.fetch_data", release_info
        )

        with pytest.raises(OpenBBError, match="No release information found for, 999."):
            await FredReleaseTableFetcher.fetch_data({"release_id": "999"}, CREDENTIALS)


class TestTableElements:
    """A release that answers with its table of contents rather than values."""

    async def test_every_element_is_returned(self, serve_tables):
        serve_tables({"*": SECTIONS})
        rows = await FredReleaseTableFetcher.fetch_data(
            {"release_id": "53"}, CREDENTIALS
        )

        assert [r.element_id for r in rows] == ["12345", "12346"]

    async def test_an_element_carries_its_kind_and_name(self, serve_tables):
        serve_tables({"*": SECTIONS})
        rows = await FredReleaseTableFetcher.fetch_data(
            {"release_id": "53"}, CREDENTIALS
        )

        assert (rows[0].element_type, rows[0].name) == (
            "table",
            "Table 1. Gross Domestic Product",
        )

    async def test_the_identifiers_are_returned_as_text(self, serve_tables):
        serve_tables({"*": SECTIONS})
        rows = await FredReleaseTableFetcher.fetch_data(
            {"release_id": "53"}, CREDENTIALS
        )

        assert (rows[1].element_id, rows[1].parent_id) == ("12346", "12345")

    async def test_a_top_level_element_has_no_parent(self, serve_tables):
        serve_tables({"*": SECTIONS})
        rows = await FredReleaseTableFetcher.fetch_data(
            {"release_id": "53"}, CREDENTIALS
        )

        assert rows[0].parent_id is None

    async def test_an_element_has_no_observation(self, serve_tables):
        serve_tables({"*": SECTIONS})
        rows = await FredReleaseTableFetcher.fetch_data(
            {"release_id": "53"}, CREDENTIALS
        )

        assert (rows[0].date, rows[0].value, rows[0].symbol) == (None, None, None)

    async def test_the_child_list_and_release_id_are_dropped(self, serve_tables):
        serve_tables({"*": SECTIONS})
        query = FredReleaseTableFetcher.transform_query({"release_id": "53"})
        extracted = await FredReleaseTableFetcher.aextract_data(query, CREDENTIALS)

        assert "children" not in extracted[0]
        assert "release_id" not in extracted[0]

    async def test_an_element_is_not_repeated_across_periods(self, serve_tables):
        asked = serve_tables({"*": SECTIONS}, frequency="M")
        rows = await FredReleaseTableFetcher.fetch_data(
            {"release_id": "53", "date": "2024-06-05,2024-07-27"}, CREDENTIALS
        )

        assert len(asked) == 2
        assert [r.element_id for r in rows] == ["12345", "12346"]


class TestReleaseObservationRows:
    """A release table that answers with observation values."""

    async def test_an_observation_becomes_a_row(self, serve_tables):
        serve_tables({"*": _tables(_series(1217635, "5.33808"))})
        rows = await FredReleaseTableFetcher.fetch_data(
            {"release_id": "483"}, CREDENTIALS
        )

        assert (rows[0].symbol, rows[0].value, rows[0].date) == (
            "SERIES1217635",
            5.33808,
            date(2024, 7, 12),
        )

    async def test_a_value_written_with_separators_is_read_as_a_number(
        self, serve_tables
    ):
        serve_tables({"*": _tables(_series(1, "1,234,567.89"))})
        rows = await FredReleaseTableFetcher.fetch_data(
            {"release_id": "483"}, CREDENTIALS
        )

        assert rows[0].value == 1234567.89

    async def test_a_missing_observation_is_dropped(self, serve_tables):
        serve_tables({"*": _tables(_series(1, "."), _series(2, "5.0"))})
        rows = await FredReleaseTableFetcher.fetch_data(
            {"release_id": "483"}, CREDENTIALS
        )

        assert [r.element_id for r in rows] == ["2"]

    async def test_a_header_row_is_dropped(self, serve_tables):
        serve_tables(
            {"*": _tables(_series(1, "5.0", type="header"), _series(2, "5.0"))}
        )
        rows = await FredReleaseTableFetcher.fetch_data(
            {"release_id": "483"}, CREDENTIALS
        )

        assert [r.element_id for r in rows] == ["2"]

    async def test_the_units_of_the_series_are_attached(self, serve_tables):
        serve_tables({"*": _tables(_series(1, "5.0"))}, units={"SERIES1": "Percent"})
        rows = await FredReleaseTableFetcher.fetch_data(
            {"release_id": "483"}, CREDENTIALS
        )

        assert rows[0].units == "Percent"

    async def test_a_series_without_published_units_carries_none(self, serve_tables):
        serve_tables({"*": _tables(_series(1, "5.0"))}, units={"OTHER": "Percent"})
        rows = await FredReleaseTableFetcher.fetch_data(
            {"release_id": "483"}, CREDENTIALS
        )

        assert rows[0].units is None

    async def test_the_children_of_a_row_are_listed(self, serve_tables):
        serve_tables(
            {
                "*": _tables(
                    _series(100, "5.0"),
                    _series(101, "1.0", parent_id=100),
                    _series(102, "2.0", parent_id=100),
                )
            }
        )
        rows = await FredReleaseTableFetcher.fetch_data(
            {"release_id": "483"}, CREDENTIALS
        )
        listed = {r.element_id: r.children for r in rows}

        assert listed["100"] == "101,102"

    async def test_a_row_without_children_lists_none(self, serve_tables):
        serve_tables(
            {
                "*": _tables(
                    _series(100, "5.0"),
                    _series(101, "1.0", parent_id=100),
                )
            }
        )
        rows = await FredReleaseTableFetcher.fetch_data(
            {"release_id": "483"}, CREDENTIALS
        )
        listed = {r.element_id: r.children for r in rows}

        assert listed["101"] is None


class TestLineNumbers:
    """The line a row occupies in the published table."""

    async def test_a_line_number_is_read_as_a_number(self, serve_tables):
        serve_tables({"*": _tables(_series(1, "5.0", line="7"))})
        rows = await FredReleaseTableFetcher.fetch_data(
            {"release_id": "483"}, CREDENTIALS
        )

        assert rows[0].line == 7

    async def test_a_line_that_is_not_a_number_is_dropped(self, serve_tables):
        serve_tables({"*": _tables(_series(1, "5.0", line="n/a"))})
        rows = await FredReleaseTableFetcher.fetch_data(
            {"release_id": "483"}, CREDENTIALS
        )

        assert rows[0].line is None

    async def test_a_release_that_publishes_no_lines_carries_none(self, serve_tables):
        serve_tables({"*": _tables(_series(1, "5.0", line=None))})
        rows = await FredReleaseTableFetcher.fetch_data(
            {"release_id": "483"}, CREDENTIALS
        )

        assert rows[0].line is None


class TestReleaseObservationDates:
    """How the period a release table row belongs to is written."""

    @pytest.mark.parametrize(
        ("published", "expected"),
        [
            ("Q1 2024", date(2024, 3, 31)),
            ("Q2 2024", date(2024, 6, 30)),
            ("Q3 2024", date(2024, 9, 30)),
            ("Q4 2024", date(2024, 12, 31)),
        ],
    )
    async def test_a_quarter_becomes_its_last_day(
        self, serve_tables, published, expected
    ):
        serve_tables({"*": _tables(_series(1, "5.0", observation_date=published))})
        rows = await FredReleaseTableFetcher.fetch_data(
            {"release_id": "53"}, CREDENTIALS
        )

        assert rows[0].date == expected

    async def test_a_month_and_year_becomes_the_first_of_the_month(self, serve_tables):
        serve_tables({"*": _tables(_series(1, "5.0", observation_date="Jul 2024"))})
        rows = await FredReleaseTableFetcher.fetch_data(
            {"release_id": "483"}, CREDENTIALS
        )

        assert rows[0].date == date(2024, 7, 1)

    async def test_an_unreadable_period_is_passed_through_unchanged(self, serve_tables):
        serve_tables({"*": _tables(_series(1, "5.0", observation_date="not-a-date"))})
        query = FredReleaseTableFetcher.transform_query({"release_id": "483"})
        extracted = await FredReleaseTableFetcher.aextract_data(query, CREDENTIALS)

        assert extracted[0]["observation_date"] == "not-a-date"


class TestEmptyRelease:
    """A release that publishes no table."""

    async def test_a_response_without_elements_is_reported(self, serve_tables):
        serve_tables({"*": {"name": "Nothing"}})

        with pytest.raises(EmptyDataError, match="No tables were found"):
            await FredReleaseTableFetcher.fetch_data({"release_id": "483"}, CREDENTIALS)

    async def test_a_release_of_only_missing_values_is_reported(self, serve_tables):
        serve_tables({"*": _tables(_series(1, "."), _series(2, "."))})

        with pytest.raises(EmptyDataError, match="No tables were found"):
            await FredReleaseTableFetcher.fetch_data({"release_id": "483"}, CREDENTIALS)

    async def test_the_message_points_at_the_search_command(self, serve_tables):
        serve_tables({"*": {}})

        with pytest.raises(EmptyDataError, match="fred_search"):
            await FredReleaseTableFetcher.fetch_data({"release_id": "483"}, CREDENTIALS)


class TestRowOrder:
    """The order the rows of a release table are returned in."""

    async def test_rows_are_ordered_by_period(self, serve_tables):
        serve_tables(
            {
                "2024-06-01": _tables(_series(2, "2.0", observation_date="2024-06-30")),
                "2024-07-01": _tables(_series(1, "1.0", observation_date="2024-07-31")),
            },
            frequency="M",
        )
        rows = await FredReleaseTableFetcher.fetch_data(
            {"release_id": "483", "date": "2024-06-15,2024-07-15"}, CREDENTIALS
        )

        assert [r.date for r in rows] == [date(2024, 6, 30), date(2024, 7, 31)]

    async def test_rows_of_one_period_are_ordered_by_line(self, serve_tables):
        serve_tables(
            {
                "*": _tables(
                    _series(1, "1.0", line="9"),
                    _series(2, "2.0", line="3"),
                )
            }
        )
        rows = await FredReleaseTableFetcher.fetch_data(
            {"release_id": "483"}, CREDENTIALS
        )

        assert [r.line for r in rows] == [3, 9]

    async def test_a_row_without_a_line_is_ordered_last(self, serve_tables):
        serve_tables(
            {
                "*": _tables(
                    _series(1, "1.0", line="n/a"),
                    _series(2, "2.0", line="3"),
                )
            }
        )
        rows = await FredReleaseTableFetcher.fetch_data(
            {"release_id": "483"}, CREDENTIALS
        )

        assert [r.line for r in rows] == [3, None]


class _Page:
    """A response carrying one rendered page of the releases calendar."""

    def __init__(self, payload: dict) -> None:
        self._payload = payload

    async def text(self) -> str:
        """Return the response body."""
        return json.dumps(self._payload)


def _day(label: str) -> str:
    """Return the row that opens one day of the calendar."""
    return f'<tr><td colspan="2"><span>{label}</span></td></tr>'


def _event(when: str, name: str, rid: int) -> str:
    """Return the row one scheduled release occupies."""
    return f'<tr><td>{when}</td><td><a href="/release?rid={rid}">{name}</a></td></tr>'


def _pager(*rows: str) -> str:
    """Return the table one calendar page renders."""
    return (
        "<table><thead><tr><th>Date</th><th>Release</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
    )


def _page(scheduled: int, *rows: str) -> dict:
    """Return the payload one calendar request answers with."""
    return {"ptic": scheduled, "pager": _pager(*rows)}


def _days(asked: list) -> list:
    """Return the day each calendar request asked for."""
    return [parse_qs(urlparse(url).query)["vs"][0] for url in asked]


class _UnnamedDay:
    """A day of the requested range that carries no label."""

    @staticmethod
    def strftime(pattern: str) -> str:
        """Return the label of the day."""
        return ""


ONE_DAY = _page(
    2,
    _day("Tuesday July 01, 2025"),
    _event("1:00 am", "Euro Short Term Rate", 502),
    _event("7:00 am", "SOFR Averages and Index Data", 483),
)


@pytest.fixture(name="serve_calendar")
def serve_calendar_fixture(monkeypatch):
    """Answer the releases calendar from recorded pages."""

    def serve(by_date: dict) -> list:
        asked: list = []

        async def get(url, *, response_callback=None, **kwargs):
            asked.append(url)
            query = parse_qs(urlparse(url).query, keep_blank_values=True)
            pages = by_date.get(query["vs"][0], by_date.get("*", []))

            return await response_callback(
                _Page(pages[int(query.get("pageID", ["1"])[0]) - 1]), None
            )

        monkeypatch.setattr("openbb_fred.utils.rate_limiter.fred_get", get)

        return asked

    return serve


class TestCalendarDay:
    """Reading one day of the release calendar."""

    async def test_each_scheduled_release_becomes_an_event(self, serve_calendar):
        serve_calendar({"*": [ONE_DAY]})
        rows = await FredEconomicCalendarFetcher.fetch_data(
            {"start_date": date(2025, 7, 1), "end_date": date(2025, 7, 1)}
        )

        assert [r.event for r in rows] == [
            "Euro Short Term Rate",
            "SOFR Averages and Index Data",
        ]

    async def test_the_day_header_is_not_an_event(self, serve_calendar):
        serve_calendar({"*": [ONE_DAY]})
        rows = await FredEconomicCalendarFetcher.fetch_data(
            {"start_date": date(2025, 7, 1), "end_date": date(2025, 7, 1)}
        )

        assert len(rows) == 2

    async def test_the_release_id_is_read_from_the_link(self, serve_calendar):
        serve_calendar({"*": [ONE_DAY]})
        rows = await FredEconomicCalendarFetcher.fetch_data(
            {"start_date": date(2025, 7, 1), "end_date": date(2025, 7, 1)}
        )

        assert [r.release_id for r in rows] == [502, 483]

    async def test_an_event_takes_its_day_from_the_header_above_it(
        self, serve_calendar
    ):
        serve_calendar({"*": [ONE_DAY]})
        rows = await FredEconomicCalendarFetcher.fetch_data(
            {"start_date": date(2025, 7, 1), "end_date": date(2025, 7, 1)}
        )

        assert rows[0].date.strftime("%Y-%m-%d %H:%M") == "2025-07-01 01:00"

    @pytest.mark.parametrize(
        ("day", "label", "abbreviation", "offset"),
        [
            (date(2025, 1, 7), "Tuesday January 07, 2025", "CST", -6),
            (date(2025, 7, 1), "Tuesday July 01, 2025", "CDT", -5),
        ],
    )
    async def test_the_times_are_read_in_the_central_zone(
        self, serve_calendar, day, label, abbreviation, offset
    ):
        serve_calendar(
            {
                "*": [
                    _page(
                        1,
                        _day(label),
                        _event("1:00 am", "Euro Short Term Rate", 502),
                    )
                ]
            }
        )
        rows = await FredEconomicCalendarFetcher.fetch_data(
            {"start_date": day, "end_date": day}
        )

        assert str(rows[0].date.tzinfo) == "US/Central"
        assert rows[0].date.tzname() == abbreviation
        assert rows[0].date.utcoffset() == timedelta(hours=offset)

    async def test_an_updated_marker_is_stripped_from_the_day(self, serve_calendar):
        serve_calendar(
            {
                "*": [
                    _page(
                        1,
                        _day("Tuesday July 01, 2025 Updated"),
                        _event("1:00 am", "Euro Short Term Rate", 502),
                    )
                ]
            }
        )
        rows = await FredEconomicCalendarFetcher.fetch_data(
            {"start_date": date(2025, 7, 1), "end_date": date(2025, 7, 1)}
        )

        assert rows[0].date.strftime("%Y-%m-%d") == "2025-07-01"

    async def test_a_revised_marker_is_stripped_from_the_day(self, serve_calendar):
        serve_calendar(
            {
                "*": [
                    _page(
                        1,
                        _day("Tuesday July 01, 2025 Revised"),
                        _event("1:00 am", "Euro Short Term Rate", 502),
                    )
                ]
            }
        )
        rows = await FredEconomicCalendarFetcher.fetch_data(
            {"start_date": date(2025, 7, 1), "end_date": date(2025, 7, 1)}
        )

        assert rows[0].date.strftime("%Y-%m-%d") == "2025-07-01"

    async def test_a_blank_time_repeats_the_time_above_it(self, serve_calendar):
        serve_calendar(
            {
                "*": [
                    _page(
                        2,
                        _day("Tuesday July 01, 2025"),
                        _event("7:00 am", "SOFR Averages and Index Data", 483),
                        _event("", "Secured Overnight Financing Rate Data", 445),
                    )
                ]
            }
        )
        rows = await FredEconomicCalendarFetcher.fetch_data(
            {"start_date": date(2025, 7, 1), "end_date": date(2025, 7, 1)}
        )

        assert rows[1].date.strftime("%H:%M") == "07:00"

    async def test_a_time_written_as_not_available_repeats_the_time_above_it(
        self, serve_calendar
    ):
        serve_calendar(
            {
                "*": [
                    _page(
                        2,
                        _day("Tuesday July 01, 2025"),
                        _event("7:00 am", "SOFR Averages and Index Data", 483),
                        _event("N/A", "ICE BofA Indices", 209),
                    )
                ]
            }
        )
        rows = await FredEconomicCalendarFetcher.fetch_data(
            {"start_date": date(2025, 7, 1), "end_date": date(2025, 7, 1)}
        )

        assert rows[1].date.strftime("%H:%M") == "07:00"


class TestCalendarPageWithoutADay:
    """A page of the calendar read without the day it belongs to."""

    async def test_a_row_without_a_day_keeps_its_published_time(
        self, serve_calendar, monkeypatch
    ):
        monkeypatch.setattr(
            "pandas.date_range", lambda *args, **kwargs: [_UnnamedDay()]
        )
        serve_calendar(
            {"*": [_page(1, _event("7:00 am", "SOFR Averages and Index Data", 483))]}
        )
        rows = await FredEconomicCalendarFetcher.fetch_data(
            {"start_date": date(2025, 7, 1), "end_date": date(2025, 7, 1)}
        )

        assert rows[0].date.strftime("%H:%M") == "07:00"
        assert str(rows[0].date.tzinfo) == "US/Central"


class TestCalendarRange:
    """Reading a range of days."""

    async def test_every_day_of_the_range_is_read(self, serve_calendar):
        asked = serve_calendar({"*": [ONE_DAY]})
        await FredEconomicCalendarFetcher.fetch_data(
            {"start_date": date(2025, 7, 1), "end_date": date(2025, 7, 3)}
        )

        assert _days(asked) == ["2025-07-01", "2025-07-02", "2025-07-03"]

    async def test_a_start_date_alone_reads_the_following_week(self, serve_calendar):
        asked = serve_calendar({"*": [ONE_DAY]})
        await FredEconomicCalendarFetcher.fetch_data({"start_date": date(2025, 7, 1)})

        assert _days(asked)[-1] == "2025-07-08"

    async def test_no_dates_read_from_yesterday_to_tomorrow(self, serve_calendar):
        asked = serve_calendar({"*": [ONE_DAY]})
        opened = datetime.today().date()
        await FredEconomicCalendarFetcher.fetch_data({})
        closed = datetime.today().date()
        spans = [
            [(day + timedelta(days=offset)).isoformat() for offset in (-1, 0, 1)]
            for day in {opened, closed}
        ]

        assert [day[:10] for day in _days(asked)] in spans

    async def test_the_events_of_the_range_are_ordered_by_time(self, serve_calendar):
        serve_calendar(
            {
                "2025-07-01": [
                    _page(
                        1,
                        _day("Tuesday July 01, 2025"),
                        _event("7:00 am", "SOFR Averages and Index Data", 483),
                    )
                ],
                "2025-07-02": [
                    _page(
                        1,
                        _day("Wednesday July 02, 2025"),
                        _event("1:00 am", "Euro Short Term Rate", 502),
                    )
                ],
            }
        )
        rows = await FredEconomicCalendarFetcher.fetch_data(
            {"start_date": date(2025, 7, 1), "end_date": date(2025, 7, 2)}
        )

        assert [r.date.strftime("%Y-%m-%d %H:%M") for r in rows] == [
            "2025-07-01 07:00",
            "2025-07-02 01:00",
        ]


class TestCalendarPaging:
    """Reading a day that spans more than one page."""

    @staticmethod
    def _spread(scheduled: int) -> dict:
        """Return a day of that many releases, one to a page."""
        return {
            "*": [
                _page(
                    scheduled,
                    _day("Tuesday July 01, 2025"),
                    _event("1:00 am", "Euro Short Term Rate", 502),
                ),
                _page(scheduled, _event("7:00 am", "SOFR Averages", 483)),
                _page(scheduled, _event("8:00 am", "Federal Funds Data", 378)),
            ]
        }

    async def test_a_second_page_is_read_when_the_first_falls_short(
        self, serve_calendar
    ):
        serve_calendar(self._spread(60))
        rows = await FredEconomicCalendarFetcher.fetch_data(
            {"start_date": date(2025, 7, 1), "end_date": date(2025, 7, 1)}
        )

        assert [r.release_id for r in rows] == [502, 483]

    async def test_a_continuation_page_takes_its_day_from_the_request(
        self, serve_calendar
    ):
        serve_calendar(self._spread(60))
        rows = await FredEconomicCalendarFetcher.fetch_data(
            {"start_date": date(2025, 7, 1), "end_date": date(2025, 7, 1)}
        )

        assert rows[1].date.strftime("%Y-%m-%d %H:%M") == "2025-07-01 07:00"

    async def test_only_as_many_pages_as_the_count_calls_for_are_read(
        self, serve_calendar
    ):
        asked = serve_calendar(self._spread(60))
        await FredEconomicCalendarFetcher.fetch_data(
            {"start_date": date(2025, 7, 1), "end_date": date(2025, 7, 1)}
        )

        assert [
            parse_qs(urlparse(url).query).get("pageID", ["1"])[0] for url in asked
        ] == ["1", "2"]

    async def test_a_further_page_is_read_for_every_fifty_releases(
        self, serve_calendar
    ):
        asked = serve_calendar(self._spread(101))
        rows = await FredEconomicCalendarFetcher.fetch_data(
            {"start_date": date(2025, 7, 1), "end_date": date(2025, 7, 1)}
        )

        assert len(asked) == 3
        assert [r.release_id for r in rows] == [502, 483, 378]

    async def test_a_complete_first_page_is_not_followed(self, serve_calendar):
        asked = serve_calendar({"*": [ONE_DAY]})
        await FredEconomicCalendarFetcher.fetch_data(
            {"start_date": date(2025, 7, 1), "end_date": date(2025, 7, 1)}
        )

        assert len(asked) == 1


class TestCalendarReleaseFilter:
    """Reading the calendar of a single release."""

    async def test_a_release_id_reads_the_whole_range_in_one_request(
        self, serve_calendar
    ):
        asked = serve_calendar({"*": [ONE_DAY]})
        await FredEconomicCalendarFetcher.fetch_data(
            {
                "start_date": date(2025, 7, 1),
                "end_date": date(2025, 7, 31),
                "release_id": 483,
            }
        )
        query = parse_qs(urlparse(asked[0]).query)

        assert len(asked) == 1
        assert (query["vs"][0], query["ve"][0], query["rid"][0]) == (
            "2025-07-01",
            "2025-07-31",
            "483",
        )


class TestCalendarWithoutEvents:
    """A calendar request that finds nothing scheduled."""

    async def test_a_range_with_nothing_scheduled_is_reported(self, serve_calendar):
        serve_calendar({"*": [_page(0)]})

        with pytest.raises(OpenBBError, match="returned no data"):
            await FredEconomicCalendarFetcher.fetch_data(
                {"start_date": date(2025, 7, 1), "end_date": date(2025, 7, 2)}
            )

    async def test_a_day_with_nothing_scheduled_is_left_out(self, serve_calendar):
        serve_calendar(
            {
                "2025-07-01": [_page(0)],
                "2025-07-02": [
                    _page(
                        1,
                        _day("Wednesday July 02, 2025"),
                        _event("1:00 am", "Euro Short Term Rate", 502),
                    )
                ],
            }
        )
        rows = await FredEconomicCalendarFetcher.fetch_data(
            {"start_date": date(2025, 7, 1), "end_date": date(2025, 7, 2)}
        )

        assert [r.date.strftime("%Y-%m-%d") for r in rows] == ["2025-07-02"]

    async def test_a_release_with_nothing_scheduled_is_reported(self, serve_calendar):
        serve_calendar({"*": [_page(0)]})

        with pytest.raises(OpenBBError, match="returned no data"):
            await FredEconomicCalendarFetcher.fetch_data(
                {
                    "start_date": date(2025, 7, 1),
                    "end_date": date(2025, 7, 2),
                    "release_id": 483,
                }
            )


class TestCalendarRequestFailure:
    """A calendar request the source refuses."""

    async def test_a_failed_request_is_reported_with_its_message(self, monkeypatch):
        async def get(url, **kwargs):
            raise RuntimeError("the source is unavailable")

        monkeypatch.setattr("openbb_fred.utils.rate_limiter.fred_get", get)

        with pytest.raises(OpenBBError, match="the source is unavailable"):
            await FredEconomicCalendarFetcher.fetch_data(
                {"start_date": date(2025, 7, 1), "end_date": date(2025, 7, 1)}
            )

    async def test_a_failure_without_a_message_names_its_type(self, monkeypatch):
        async def get(url, **kwargs):
            raise RuntimeError

        monkeypatch.setattr("openbb_fred.utils.rate_limiter.fred_get", get)

        with pytest.raises(
            OpenBBError, match=r"FRED request failed \(RuntimeError\)\."
        ):
            await FredEconomicCalendarFetcher.fetch_data(
                {"start_date": date(2025, 7, 1), "end_date": date(2025, 7, 1)}
            )

    async def test_an_unreadable_page_is_reported(self, monkeypatch):
        async def get(url, *, response_callback=None, **kwargs):
            return await response_callback(
                _Page({"ptic": 3, "pager": "<p>no table here</p>"}), None
            )

        monkeypatch.setattr("openbb_fred.utils.rate_limiter.fred_get", get)

        with pytest.raises(OpenBBError, match="No tables found"):
            await FredEconomicCalendarFetcher.fetch_data(
                {"start_date": date(2025, 7, 1), "end_date": date(2025, 7, 1)}
            )


class TestCalendarValidation:
    """Turning the read rows into economic calendar events."""

    def test_a_row_becomes_an_event(self):
        query = FredEconomicCalendarQueryParams()
        rows = FredEconomicCalendarFetcher.transform_data(
            query,
            [
                {
                    "date": "2025-07-01 07:00:00-05:00",
                    "event": "SOFR Averages and Index Data",
                    "release_id": "483",
                }
            ],
        )

        assert (rows[0].event, rows[0].release_id) == (
            "SOFR Averages and Index Data",
            483,
        )

    def test_a_release_id_is_optional(self):
        query = FredEconomicCalendarQueryParams()
        rows = FredEconomicCalendarFetcher.transform_data(
            query, [{"date": "2025-07-01 07:00:00-05:00", "event": "Something"}]
        )

        assert rows[0].release_id is None

    def test_a_release_filter_is_carried_by_the_query(self):
        query = FredEconomicCalendarFetcher.transform_query({"release_id": 483})

        assert query.release_id == 483
