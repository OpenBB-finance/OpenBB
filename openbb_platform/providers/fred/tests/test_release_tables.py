"""Test the release table utilities."""

import datetime

import pytest


class TestReleasePresentation:
    """A release table, in its published order with the periods across."""

    SERIES = {
        "TOTAL": {
            "series_id": "TOTAL",
            "title": "Retail Trade: Total",
            "units": "Millions of Dollars",
            "frequency": "Monthly",
            "observations": [
                {"date": "2026-04-01", "value": "100"},
                {"date": "2026-05-01", "value": "."},
                {"date": "2026-06-01", "value": "120"},
            ],
        },
        "PART": {
            "series_id": "PART",
            "title": "Retail Trade: Grocery",
            "units": "Millions of Dollars",
            "frequency": "Monthly",
            "observations": [{"date": "2026-06-01", "value": "40"}],
        },
        "OTHER": {
            "series_id": "OTHER",
            "title": "A Series Not In The Table",
            "units": "Percent",
            "frequency": "Annual",
            "observations": [{"date": "2026-01-01", "value": "9"}],
        },
    }
    LINES = [
        {"series_id": "TOTAL", "name": "Total", "level": 1, "table": "Sales"},
        {"series_id": "PART", "name": "Grocery", "level": 2, "table": "Sales"},
    ]

    @pytest.fixture
    def release(self, monkeypatch):
        """Serve one release and one table without touching the network."""

        async def observed(release_id, api_key, use_cache=True):
            return {"release_id": 9, "name": "Retail Sales"}, self.SERIES

        async def structure(release_id, element_id, api_key, use_cache=True):
            return self.LINES if element_id else []

        monkeypatch.setattr(
            "openbb_fred.utils.v2.release_observations", observed, raising=False
        )
        monkeypatch.setattr(
            "openbb_fred.utils.release_tables.table_lines", structure, raising=False
        )

    async def test_the_table_keeps_its_published_order(self, release):
        """Alphabetical would put Grocery first. The table says otherwise."""
        from openbb_fred.utils.release_tables import build_release_table

        rows = await build_release_table("9", "201241", "all", 6, "key")

        assert [r["symbol"] for r in rows] == ["TOTAL", "PART"]

    async def test_a_child_line_is_indented(self, release):
        from openbb_fred.utils.release_tables import INDENT, build_release_table

        rows = await build_release_table("9", "201241", "all", 6, "key")

        assert rows[0]["series"] == "Total"
        assert rows[1]["series"] == f"{INDENT}Grocery"

    async def test_the_table_names_its_own_lines(self, release):
        """The table label reads better than the full series title."""
        from openbb_fred.utils.release_tables import build_release_table

        rows = await build_release_table("9", "201241", "all", 6, "key")

        assert rows[0]["series"] == "Total"
        assert "Retail Trade: Total" not in rows[0]["series"]

    async def test_only_the_table_membership_is_returned(self, release):
        from openbb_fred.utils.release_tables import build_release_table

        rows = await build_release_table("9", "201241", "all", 6, "key")

        assert "OTHER" not in [r["symbol"] for r in rows]

    async def test_the_columns_read_in_key_order(self, release):
        """The grid has no column definitions, so key order is column order."""
        from openbb_fred.utils.release_tables import build_release_table

        rows = await build_release_table("9", "201241", "all", 6, "key")

        assert list(rows[0])[:4] == ["series", "symbol", "units", "trend"]
        assert list(rows[0])[4:] == ["2026-06-01", "2026-04-01"]

    async def test_every_row_shares_one_period_axis(self, release):
        """A series ending early must not add a column of its own."""
        from openbb_fred.utils.release_tables import build_release_table

        rows = await build_release_table("9", "201241", "all", 6, "key")
        columns = {k for row in rows for k in row if k.startswith("20")}

        assert columns == {"2026-06-01", "2026-04-01"}
        assert rows[1]["2026-04-01"] is None

    async def test_a_period_without_a_value_is_left_empty(self, release):
        """FRED writes a period for a date it has not published."""
        from openbb_fred.utils.release_tables import build_release_table

        rows = await build_release_table("9", "201241", "all", 6, "key")

        assert "2026-05-01" not in rows[0]

    async def test_the_window_is_the_most_recent_periods(self, release):
        from openbb_fred.utils.release_tables import build_release_table

        rows = await build_release_table("9", "201241", "all", 1, "key")

        assert list(rows[0])[4:] == ["2026-06-01"]

    async def test_without_a_table_the_names_arrange_the_release(self, release):
        """One interval, and the shared part of the names becomes the heading."""
        from openbb_fred.utils.release_tables import INDENT, build_release_table

        rows = await build_release_table("9", None, "", 6, "key")

        assert [(r["series"], r["symbol"]) for r in rows] == [
            ("Retail Trade", None),
            (f"{INDENT}Grocery", "PART"),
            (f"{INDENT}Total", "TOTAL"),
        ]

    async def test_an_absent_frequency_falls_back_to_the_published_one(self, release):
        """A stale choice must not empty the table."""
        from openbb_fred.utils.release_tables import build_release_table

        rows = await build_release_table("9", "201241", "daily", 6, "key")

        assert [r["symbol"] for r in rows] == ["TOTAL", "PART"]

    async def test_a_heading_is_rendered_as_a_row(self, monkeypatch, release):
        """The heading tells the lines below it apart, so it is a line too."""
        from openbb_fred.utils.release_tables import build_release_table

        async def structure(release_id, element_id, api_key, use_cache=True):
            return [
                {"series_id": None, "name": "Sales", "level": 1, "table": "Sales"},
                {"series_id": "TOTAL", "name": "Total", "level": 2, "table": "Sales"},
                {"series_id": "PART", "name": "Grocery", "level": 3, "table": "Sales"},
            ]

        monkeypatch.setattr(
            "openbb_fred.utils.release_tables.table_lines", structure, raising=False
        )

        rows = await build_release_table("9", "201241", "all", 6, "key")

        assert rows[0]["series"] == "Sales"
        assert rows[0]["symbol"] is None
        assert rows[0]["trend"] is None
        assert list(rows[0]) == list(rows[1])

    async def test_a_heading_over_retired_lines_is_dropped(self, monkeypatch, release):
        from openbb_fred.utils.release_tables import build_release_table

        async def structure(release_id, element_id, api_key, use_cache=True):
            return [
                {"series_id": None, "name": "Gone", "level": 1, "table": "Sales"},
                {"series_id": "DEAD", "name": "Retired", "level": 2, "table": "Sales"},
            ]

        async def observed(release_id, api_key, use_cache=True):
            return {}, {
                "DEAD": {
                    "series_id": "DEAD",
                    "title": "Retired Line (DISCONTINUED)",
                    "units": "Percent",
                    "frequency": "Monthly",
                    "observations": [{"date": "2026-06-01", "value": "1"}],
                }
            }

        monkeypatch.setattr(
            "openbb_fred.utils.release_tables.table_lines", structure, raising=False
        )
        monkeypatch.setattr(
            "openbb_fred.utils.v2.release_observations", observed, raising=False
        )

        assert await build_release_table("9", "201241", "all", 6, "key") == []

    async def test_a_frequency_narrows_the_whole_release(self, release):
        from openbb_fred.utils.release_tables import build_release_table

        rows = await build_release_table("9", None, "annual", 6, "key")

        assert [r["symbol"] for r in rows] == ["OTHER"]


class TestRetirement:
    """What FRED still publishes, and what it has stopped publishing."""

    def test_a_marked_title_is_retired(self):
        from openbb_fred.utils.release_tables import current

        assert not current({"title": "Old Series (DISCONTINUED)"})

    def test_a_series_that_stopped_publishing_is_retired(self):
        from openbb_fred.utils.release_tables import current

        assert not current(
            {
                "title": "Live Series",
                "frequency": "Monthly",
                "observation_end": "2017-02-01",
            }
        )

    def test_a_recent_update_does_not_revive_it(self):
        """FRED revises the notes on a series it stopped publishing."""
        from openbb_fred.utils.release_tables import current

        assert not current(
            {
                "title": "Live Series",
                "frequency": "Monthly",
                "observation_end": "2017-02-01",
                "last_updated": "2025-01-15 09:40:07",
            }
        )

    def test_a_series_still_publishing_is_current(self):
        from openbb_fred.utils.release_tables import current

        assert current(
            {
                "title": "Live Series",
                "frequency": "Monthly",
                "observation_end": datetime.date.today().isoformat(),
            }
        )

    def test_an_annual_series_is_given_longer(self):
        """A year between periods is not a series that stopped."""
        from openbb_fred.utils.release_tables import current

        today = datetime.date.today()
        two_years_back = today.replace(year=today.year - 2).isoformat()

        assert current(
            {"title": "Live", "frequency": "Annual", "observation_end": two_years_back}
        )
        assert not current(
            {"title": "Live", "frequency": "Daily", "observation_end": two_years_back}
        )

    def test_the_observations_say_when_a_series_last_published(self):
        """The observations endpoint carries the span as the observations."""
        from openbb_fred.utils.release_tables import last_observed

        assert (
            last_observed(
                {
                    "observations": [
                        {"date": "2026-01-01", "value": "1"},
                        {"date": "2026-02-01", "value": "."},
                    ]
                }
            )
            == "2026-01-01"
        )

    def test_a_series_with_no_observations_is_kept(self):
        """Absence of a span is not evidence the series stopped."""
        from openbb_fred.utils.release_tables import current, last_observed

        assert last_observed({"observations": []}) is None
        assert current({"title": "Live Series"})

    async def test_a_search_that_never_answers_returns_what_it_has(self, monkeypatch):
        from openbb_fred.utils import release_tables

        calls = []

        async def refuse(params, credentials):
            calls.append(params)
            raise OSError("no answer")

        async def instant(_):
            return None

        monkeypatch.setattr(
            "openbb_fred.models.search.FredSearchFetcher.fetch_data",
            refuse,
            raising=False,
        )
        monkeypatch.setattr("asyncio.sleep", instant)

        assert await release_tables.release_series("9", {}) == []
        assert len(calls) == release_tables.TRIES

    async def test_a_release_is_read_a_page_at_a_time(self, monkeypatch):
        """A release can publish more series than one search returns."""
        from openbb_fred.models.search import FredSearchData
        from openbb_fred.utils import release_tables

        offsets: list[int] = []

        async def paged(params, credentials):
            offsets.append(params["offset"])
            held = release_tables.PAGE if not params["offset"] else 1

            return [
                FredSearchData.model_validate(
                    {"id": f"S{params['offset']}_{n}", "title": "A Series"}
                )
                for n in range(held)
            ]

        monkeypatch.setattr(
            "openbb_fred.models.search.FredSearchFetcher.fetch_data",
            paged,
            raising=False,
        )

        found = await release_tables.release_series("9", {})

        assert offsets == [0, release_tables.PAGE]
        assert len(found) == release_tables.PAGE + 1

    async def test_units_come_from_the_search(self, monkeypatch):
        from openbb_fred.utils import release_tables

        async def listed(release_id, credentials):
            return [
                {"series_id": "A", "units": "Percent"},
                {"series_id": "B", "units": None},
            ]

        monkeypatch.setattr(release_tables, "release_series", listed)

        assert await release_tables.get_units(9, {}) == {"A": "Percent"}


class TestSearchCeilings:
    """The ceilings that stop the series search reading without bound."""

    async def test_a_release_that_never_runs_out_stops_at_the_ceiling(
        self, monkeypatch
    ):
        """Every page comes back full, so only the ceiling ends the paging."""
        from openbb_fred.models.search import FredSearchData
        from openbb_fred.utils import release_tables

        full = [
            FredSearchData.model_validate({"id": f"S{n}", "title": "A Series"})
            for n in range(release_tables.PAGE)
        ]
        offsets: list[int] = []

        async def never_empty(params, credentials):
            offsets.append(params["offset"])

            return full

        monkeypatch.setattr(
            "openbb_fred.models.search.FredSearchFetcher.fetch_data",
            never_empty,
            raising=False,
        )

        found = await release_tables.release_series("9", {})

        assert offsets == list(range(0, release_tables.MAX_SERIES, release_tables.PAGE))
        assert len(found) == release_tables.MAX_SERIES

    async def test_a_ceiling_of_no_attempts_asks_for_nothing(self, monkeypatch):
        """The ceiling is read afresh on every page, so zero reads nothing."""
        from openbb_fred.utils import release_tables

        calls: list = []

        async def answer(params, credentials):
            calls.append(params)

            return []

        monkeypatch.setattr(
            "openbb_fred.models.search.FredSearchFetcher.fetch_data",
            answer,
            raising=False,
        )
        monkeypatch.setattr(release_tables, "TRIES", 0)

        assert await release_tables.release_series("9", {}) == []
        assert calls == []


class TestSharedPrefix:
    """The lead every table name in one release repeats."""

    def test_a_single_name_repeats_nothing(self):
        from openbb_fred.utils.release_tables import shared_prefix

        assert shared_prefix(["Only One"]) == ""

    def test_a_name_that_leads_another_is_cut_at_its_separator(self):
        """'Table 1: Sales' leads 'Table 1: Sales Total' the whole way."""
        from openbb_fred.utils.release_tables import shared_prefix

        assert shared_prefix(["Table 1: Sales", "Table 1: Sales Total"]) == "Table 1: "

    def test_a_name_that_leads_another_without_a_separator_shares_nothing(self):
        """The lead has to end at a separator to be worth trimming."""
        from openbb_fred.utils.release_tables import shared_prefix

        assert shared_prefix(["Sales", "Sales Total"]) == ""


class TestUnreadableMap:
    """The packaged map is read once, and its absence is not fatal."""

    def test_a_missing_asset_reads_as_empty(self, monkeypatch, tmp_path):
        from openbb_fred.utils import release_tables

        release_tables.release_map.cache_clear()
        monkeypatch.setattr(
            release_tables, "RELEASE_MAP", tmp_path / "absent.json", raising=False
        )

        try:
            assert release_tables.release_map() == {}
        finally:
            release_tables.release_map.cache_clear()


class TestCommonLead:
    """The repeated lead on a whole-release listing."""

    def test_a_single_name_keeps_itself(self):
        from openbb_fred.utils.release_tables import common_lead

        assert common_lead(["Only One"]) == ""

    def test_the_lead_is_cut_at_a_word(self):
        from openbb_fred.utils.release_tables import common_lead

        assert common_lead(["Home Value in Alabama", "Home Value in Alaska"]) == (
            "Home Value in "
        )

    def test_names_sharing_nothing_keep_themselves(self):
        from openbb_fred.utils.release_tables import common_lead

        assert common_lead(["Alpha", "Beta"]) == ""

    def test_a_shorter_name_ends_the_lead(self):
        from openbb_fred.utils.release_tables import common_lead

        assert common_lead(["One Two", "One Two Three"]) == "One "


class TestTableStructure:
    """The lines a table publishes, headings and nesting included."""

    NESTED = {
        "51840": {
            "name": "Table 6",
            "elements": {
                "51841": {
                    "element_id": 51841,
                    "series_id": None,
                    "type": "table",
                    "name": "Quarterly",
                    "level": "1",
                    "children": [],
                }
            },
        },
        "51841": {
            "name": "Quarterly",
            "elements": {
                "0": None,
                "51842": {
                    "element_id": 51842,
                    "series_id": None,
                    "type": "header",
                    "name": "Bargaining Status",
                    "level": "1",
                    "children": [{"element_id": 51843}],
                },
                "51843": {
                    "element_id": 51843,
                    "series_id": "UNION",
                    "type": "series",
                    "name": "Union",
                    "level": "2",
                    "children": [],
                },
            },
        },
    }

    @pytest.fixture
    def served(self, monkeypatch):
        """Answer the table endpoint from the nested fixture."""
        seen: list[str] = []

        async def answer(url, use_cache=True, **kwargs):
            element_id = url.split("element_id=")[1].split("&")[0]
            seen.append(element_id)

            return self.NESTED.get(element_id)

        monkeypatch.setattr(
            "openbb_fred.utils.rate_limiter.fred_get", answer, raising=False
        )

        return seen

    async def test_no_element_reads_nothing(self, served):
        from openbb_fred.utils.release_tables import table_lines

        assert await table_lines("11", None, "key") == []
        assert served == []

    async def test_a_wrapper_is_followed_to_its_table(self, served):
        from openbb_fred.utils.release_tables import table_lines

        lines = await table_lines("11", "51840", "key")

        assert served == ["51840", "51841"]
        assert [line["name"] for line in lines] == [
            "Quarterly",
            "Bargaining Status",
            "Union",
        ]

    async def test_a_nested_line_carries_its_own_depth(self, served):
        from openbb_fred.utils.release_tables import table_lines

        lines = await table_lines("11", "51840", "key")

        assert [line["level"] for line in lines] == [1, 2, 3]

    async def test_a_heading_carries_no_series(self, served):
        from openbb_fred.utils.release_tables import table_lines

        lines = await table_lines("11", "51840", "key")

        assert lines[1]["series_id"] is None
        assert lines[2]["series_id"] == "UNION"

    async def test_a_node_is_read_once(self, monkeypatch):
        """A table that points back at itself would never stop."""
        from openbb_fred.utils.release_tables import table_lines

        seen: list[str] = []

        async def looping(url, use_cache=True, **kwargs):
            element_id = url.split("element_id=")[1].split("&")[0]
            seen.append(element_id)

            return {
                "name": "Loop",
                "elements": {
                    "1": {
                        "element_id": 1,
                        "series_id": None,
                        "type": "table",
                        "name": "Loop",
                        "level": "1",
                        "children": [],
                    }
                },
            }

        monkeypatch.setattr(
            "openbb_fred.utils.rate_limiter.fred_get", looping, raising=False
        )

        await table_lines("11", "1", "key")

        assert seen == ["1"]

    async def test_an_unreadable_node_reads_as_nothing(self, monkeypatch):
        from openbb_fred.utils.release_tables import table_lines

        async def refuse(url, use_cache=True, **kwargs):
            raise OSError("no answer")

        monkeypatch.setattr(
            "openbb_fred.utils.rate_limiter.fred_get", refuse, raising=False
        )

        assert await table_lines("11", "51840", "key") == []


class TestDistinctLines:
    """Every line in a table is named apart from every other."""

    @staticmethod
    def _rows(names):
        from openbb_fred.utils.release_tables import INDENT

        return [
            {"series": INDENT * depth + name, "symbol": symbol}
            for name, depth, symbol in names
        ]

    def test_a_heading_with_nothing_under_it_is_dropped(self):
        from openbb_fred.utils.release_tables import drop_empty_headings

        rows = self._rows(
            [("Kept", 0, None), ("Line", 1, "A"), ("Empty", 0, None)],
        )

        assert [r["series"].strip(" ") for r in drop_empty_headings(rows)] == [
            "Kept",
            "Line",
        ]

    def test_a_heading_followed_by_a_heading_is_dropped(self):
        from openbb_fred.utils.release_tables import drop_empty_headings

        rows = self._rows([("Outer", 0, None), ("Inner", 1, None)])

        assert drop_empty_headings(rows) == []

    def test_a_heading_ends_where_the_indent_returns(self):
        """A line at the same depth belongs to the next heading, not this one."""
        from openbb_fred.utils.release_tables import drop_empty_headings

        rows = self._rows([("Heading", 0, None), ("Line", 0, "A")])

        assert [r["series"] for r in drop_empty_headings(rows)] == ["Line"]

    def test_a_unique_name_is_left_alone(self):
        from openbb_fred.utils.release_tables import distinguish

        rows = self._rows([("Union", 1, "A"), ("Nonunion", 1, "B")])
        named = [r["series"].strip(" ") for r in distinguish(rows)]

        assert named == ["Union", "Nonunion"]

    def test_a_name_repeated_under_another_heading_is_left_alone(self):
        """The heading above the line already says which one it is."""
        from openbb_fred.utils.release_tables import distinguish

        rows = self._rows(
            [
                ("Union", 0, "A"),
                ("Goods", 1, "B"),
                ("Nonunion", 0, "C"),
                ("Goods", 1, "D"),
            ]
        )
        named = [r["series"].strip(" ") for r in distinguish(rows)]

        assert named == ["Union", "Goods", "Nonunion", "Goods"]

    def test_a_deeper_repeat_is_left_alone(self):
        from openbb_fred.utils.release_tables import distinguish

        rows = self._rows(
            [
                ("Union", 0, "A"),
                ("Goods", 1, "B"),
                ("Manufacturing", 2, "C"),
                ("Nonunion", 0, "D"),
                ("Goods", 1, "E"),
                ("Manufacturing", 2, "F"),
            ]
        )
        named = [r["series"].strip(" ") for r in distinguish(rows)]

        assert named[2] == "Manufacturing"
        assert named[5] == "Manufacturing"

    def test_a_name_the_hierarchy_repeats_takes_its_unit(self):
        """A release publishes the same measure at several units."""
        from openbb_fred.utils.release_tables import distinguish

        rows = self._rows([("Total", 0, "A"), ("Total", 0, "B")])
        named = [
            r["series"].strip(" ")
            for r in distinguish(
                rows,
                {
                    "A": ["Percent Change", "Seasonally Adjusted"],
                    "B": ["Percent Change from Year Ago", "Seasonally Adjusted"],
                },
            )
        ]

        assert named == [
            "Total (Percent Change)",
            "Total (Percent Change from Year Ago)",
        ]

    def test_a_name_one_unit_repeats_takes_its_adjustment(self):
        """The same measure is published seasonally adjusted and not."""
        from openbb_fred.utils.release_tables import distinguish

        rows = self._rows([("Total", 0, "A"), ("Total", 0, "B")])
        named = [
            r["series"].strip(" ")
            for r in distinguish(
                rows,
                {
                    "A": ["Index", "Seasonally Adjusted"],
                    "B": ["Index", "Not Seasonally Adjusted"],
                },
            )
        ]

        assert named == [
            "Total (Seasonally Adjusted)",
            "Total (Not Seasonally Adjusted)",
        ]

    def test_a_name_nothing_published_tells_apart_takes_its_symbol(self):
        from openbb_fred.utils.release_tables import distinguish

        rows = self._rows([("Total", 0, "A"), ("Total", 0, "B")])
        named = [
            r["series"].strip(" ")
            for r in distinguish(rows, {"A": ["Percent"], "B": ["Percent"]})
        ]

        assert named == ["Total (A)", "Total (B)"]

    def test_the_same_name_under_one_heading_is_told_apart(self):
        from openbb_fred.utils.release_tables import distinguish

        rows = self._rows(
            [("Union", 0, None), ("Goods", 1, "A"), ("Goods", 1, "B")],
        )
        named = [
            r["series"].strip(" ")
            for r in distinguish(rows, {"A": ["Index"], "B": ["Percent"]})
        ]

        assert named == ["Union", "Goods (Index)", "Goods (Percent)"]


class TestResolvedElement:
    """The table a release is read by when the picker holds another's."""

    def test_the_table_asked_for_is_kept(self):
        from openbb_fred.utils.release_tables import resolve_element

        assert resolve_element("9", "201241") == "201241"

    def test_a_table_from_another_release_is_replaced(self):
        """The picker keeps its selection when the release changes."""
        from openbb_fred.utils.release_tables import list_elements, resolve_element

        assert resolve_element("311", "201241") == list_elements("311")[0]["value"]

    def test_no_table_reads_the_first_one(self):
        from openbb_fred.utils.release_tables import list_elements, resolve_element

        assert resolve_element("311", None) == list_elements("311")[0]["value"]

    def test_a_release_without_tables_is_read_whole(self):
        from openbb_fred.utils.release_tables import resolve_element

        assert resolve_element("503", "201241") == ""

    def test_an_unknown_release_reads_nothing(self):
        from openbb_fred.utils.release_tables import resolve_element

        assert resolve_element("nope", "201241") is None


class TestPeriodAxis:
    """One column per period, whatever calendar a series is dated on."""

    def test_an_annual_period_is_its_year(self):
        from openbb_fred.utils.release_tables import period_of

        assert period_of("2025-09-30", "Annual") == "2025"
        assert period_of("2025-01-01", "Annual") == "2025"

    def test_a_quarterly_period_is_its_quarter(self):
        from openbb_fred.utils.release_tables import period_of

        assert period_of("2025-04-01", "Quarterly") == "2025Q2"
        assert period_of("2025-12-31", "Quarterly") == "2025Q4"

    def test_a_monthly_period_is_its_month(self):
        from openbb_fred.utils.release_tables import period_of

        assert period_of("2025-06-15", "Monthly") == "2025-06"

    def test_a_daily_period_is_its_date(self):
        from openbb_fred.utils.release_tables import period_of

        assert period_of("2025-06-15", "Daily") == "2025-06-15"
        assert period_of("2025-06-15", None) == "2025-06-15"

    def test_two_calendars_read_onto_one_column(self):
        """A fiscal year and a calendar year are the same annual period."""
        from openbb_fred.utils.release_tables import align

        axis, aligned = align(
            {
                "FISCAL": {"2025-09-30": 1.0, "2024-09-30": 2.0},
                "CALENDAR": {"2025-01-01": 3.0, "2024-01-01": 4.0},
            },
            "Annual",
        )

        assert axis == ["2025-09-30", "2024-09-30"]
        assert aligned == {
            "FISCAL": {"2025-09-30": 1.0, "2024-09-30": 2.0},
            "CALENDAR": {"2025-09-30": 3.0, "2024-09-30": 4.0},
        }

    def test_the_axis_runs_newest_first(self):
        from openbb_fred.utils.release_tables import align

        axis, _ = align({"A": {"2024-01-01": 1.0, "2026-01-01": 2.0}}, "Annual")

        assert axis == ["2026-01-01", "2024-01-01"]

    def test_the_column_takes_the_date_most_of_the_release_carries(self):
        """A calendar year names the column a fiscal year is read onto."""
        from openbb_fred.utils.release_tables import align

        axis, _ = align(
            {
                "FISCAL": {"2025-09-30": 1.0},
                "ONE": {"2025-01-01": 2.0},
                "TWO": {"2025-01-01": 3.0},
            },
            "Annual",
        )

        assert axis == ["2025-01-01"]

    def test_the_last_observation_in_a_period_is_carried(self):
        from openbb_fred.utils.release_tables import align

        _, aligned = align({"A": {"2025-01-01": 1.0, "2025-07-01": 2.0}}, "Annual")

        assert aligned == {"A": {"2025-07-01": 2.0}}


class TestRegroupedLines:
    """What a published table's lines repeat is read from their heading."""

    @staticmethod
    def _lines(named):
        return [
            {"series_id": series_id, "name": name, "level": level, "table": "T"}
            for name, level, series_id in named
        ]

    def test_a_published_name_keeps_no_trailing_punctuation(self):
        """A release separates the parts of a name with a semicolon."""
        from openbb_fred.utils.release_tables import hierarchy

        lines = hierarchy(
            [
                ("A", "Current Capacity Utilization; Diffusion Index"),
                ("B", "Current Capacity Utilization; Percentage Reporting"),
            ]
        )

        assert [line["name"] for line in lines] == [
            "Current Capacity Utilization",
            "Diffusion Index",
            "Percentage Reporting",
        ]

    def test_a_joining_word_never_becomes_a_heading(self):
        """'less Food and Energy' is one name, not a branch of the tree."""
        from openbb_fred.utils.release_tables import hierarchy

        lines = hierarchy(
            [
                ("A", "Sticky Price Index"),
                ("B", "Sticky Price Index less Food and Energy"),
                ("C", "Sticky Price Index less Shelter"),
            ]
        )

        assert [(line["name"], line["level"], line["series_id"]) for line in lines] == [
            ("Sticky Price Index", 1, "A"),
            ("less Food and Energy", 2, "B"),
            ("less Shelter", 2, "C"),
        ]

    def test_a_shared_lead_is_read_from_the_heading(self):
        from openbb_fred.utils.release_tables import regroup

        lines = regroup(
            self._lines(
                [
                    ("Diesel", 1, None),
                    ("Automotive diesel fuel per gallon in Pacific", 2, "A"),
                    ("Automotive diesel fuel per gallon in Mountain", 2, "B"),
                ]
            )
        )

        assert [(line["name"], line["level"]) for line in lines] == [
            ("Diesel", 1),
            ("Pacific", 2),
            ("Mountain", 2),
        ]

    def test_measures_across_the_same_places_become_headings(self):
        from openbb_fred.utils.release_tables import regroup

        lines = regroup(
            self._lines(
                [
                    ("Alcoholic Beverages", 1, None),
                    ("Malt beverages, per 16 oz. in Midwest urban", 2, "A"),
                    ("Malt beverages, per 16 oz. in West urban", 2, "B"),
                    ("Wine, per 1 liter in Midwest urban", 2, "C"),
                    ("Wine, per 1 liter in West urban", 2, "D"),
                ]
            )
        )

        assert [(line["name"], line["level"], line["series_id"]) for line in lines] == [
            ("Alcoholic Beverages", 1, None),
            ("Malt beverages, per 16 oz.", 2, None),
            ("Midwest urban", 3, "A"),
            ("West urban", 3, "B"),
            ("Wine, per 1 liter", 2, None),
            ("Midwest urban", 3, "C"),
            ("West urban", 3, "D"),
        ]

    def test_one_measure_is_left_on_its_line(self):
        """A measure read in one place needs no heading of its own."""
        from openbb_fred.utils.release_tables import regroup

        lines = regroup(
            self._lines(
                [
                    ("Fuels", 1, None),
                    ("Coal, per ton in Midwest urban", 2, "A"),
                    ("Wood, per cord in Midwest urban", 2, "B"),
                ]
            )
        )

        assert [(line["name"], line["level"]) for line in lines] == [
            ("Fuels", 1),
            ("Coal, per ton in Midwest urban", 2),
            ("Wood, per cord in Midwest urban", 2),
        ]

    def test_a_measure_read_in_one_place_keeps_its_line(self):
        """It reads beside the measures that do have a heading of their own."""
        from openbb_fred.utils.release_tables import regroup

        lines = regroup(
            self._lines(
                [
                    ("Fuels", 1, None),
                    ("Coal, per ton in Midwest urban", 2, "A"),
                    ("Coal, per ton in West urban", 2, "B"),
                    ("Wood, per cord in Midwest urban", 2, "C"),
                ]
            )
        )

        assert [(line["name"], line["level"], line["series_id"]) for line in lines] == [
            ("Fuels", 1, None),
            ("Coal, per ton", 2, None),
            ("Midwest urban", 3, "A"),
            ("West urban", 3, "B"),
            ("Wood, per cord in Midwest urban", 2, "C"),
        ]

    def test_lines_that_name_no_place_are_left_alone(self):
        from openbb_fred.utils.release_tables import regroup

        lines = regroup(self._lines([("Union", 1, "A"), ("Nonunion", 1, "B")]))

        assert [(line["name"], line["level"]) for line in lines] == [
            ("Union", 1),
            ("Nonunion", 1),
        ]

    def test_a_line_with_children_is_not_regrouped(self):
        """A published tree already says how its lines are read."""
        from openbb_fred.utils.release_tables import regroup

        lines = regroup(
            self._lines(
                [
                    ("Total in Midwest urban", 1, "A"),
                    ("Part", 2, "B"),
                    ("Other in Midwest urban", 1, "C"),
                ]
            )
        )

        assert [(line["name"], line["level"]) for line in lines] == [
            ("Total in Midwest urban", 1),
            ("Part", 2),
            ("Other in Midwest urban", 1),
        ]


class TestConcept:
    """What a group of series is a measure of, read from their titles."""

    def test_one_title_says_nothing_shared(self):
        from openbb_fred.utils.release_tables import concept

        assert concept(["Employment Level"]) == ""

    def test_a_title_that_is_the_lead_is_taken_whole(self):
        from openbb_fred.utils.release_tables import concept

        assert (
            concept(["Employment Level", "Employment Level - 16-19 Yrs."])
            == "Employment Level"
        )

    def test_the_lead_is_cut_at_a_separator(self):
        from openbb_fred.utils.release_tables import concept

        assert (
            concept(["Employment Level - 16-19 Yrs.", "Employment Level - 20-24 Yrs."])
            == "Employment Level"
        )

    def test_the_lead_falls_back_to_a_word(self):
        from openbb_fred.utils.release_tables import concept

        assert concept(["Employed Persons Alpha", "Employed Persons Beta"]) == (
            "Employed Persons"
        )

    def test_titles_sharing_nothing_have_no_measure(self):
        from openbb_fred.utils.release_tables import concept

        assert concept(["Alpha", "Beta"]) == ""

    def test_a_run_is_headed_by_what_it_measures(self):
        """The line names are breakdowns and never say what is measured."""
        from openbb_fred.utils.release_tables import regroup

        lines = regroup(
            [
                {"series_id": "A", "name": "16 to 19 years", "level": 1, "table": "T"},
                {"series_id": "B", "name": "20 to 24 years", "level": 1, "table": "T"},
                {"series_id": "C", "name": "16 to 19 years", "level": 1, "table": "T"},
                {"series_id": "D", "name": "20 to 24 years", "level": 1, "table": "T"},
            ],
            {
                "A": "Employment Level - 16-19 Yrs.",
                "B": "Employment Level - 20-24 Yrs.",
                "C": "Multiple Jobholders - 16-19 Yrs.",
                "D": "Multiple Jobholders - 20-24 Yrs.",
            },
        )

        assert [(line["name"], line["level"], line["series_id"]) for line in lines] == [
            ("Employment Level", 1, None),
            ("16 to 19 years", 2, "A"),
            ("20 to 24 years", 2, "B"),
            ("Multiple Jobholders", 1, None),
            ("16 to 19 years", 2, "C"),
            ("20 to 24 years", 2, "D"),
        ]

    def test_one_measure_across_the_table_is_left_to_the_title(self):
        from openbb_fred.utils.release_tables import regroup

        lines = regroup(
            [
                {"series_id": "A", "name": "16 to 19 years", "level": 1, "table": "T"},
                {"series_id": "B", "name": "20 to 24 years", "level": 1, "table": "T"},
            ],
            {
                "A": "Employment Level - 16-19 Yrs.",
                "B": "Employment Level - 20-24 Yrs.",
            },
        )

        assert [line["name"] for line in lines] == ["16 to 19 years", "20 to 24 years"]

    def test_a_measure_read_once_keeps_its_place(self):
        """A run of one is not worth a heading of its own."""
        from openbb_fred.utils.release_tables import regroup

        lines = regroup(
            [
                {"series_id": "A", "name": "16 to 19 years", "level": 1, "table": "T"},
                {"series_id": "B", "name": "20 to 24 years", "level": 1, "table": "T"},
                {"series_id": "C", "name": "All workers", "level": 1, "table": "T"},
            ],
            {
                "A": "Employment Level - 16-19 Yrs.",
                "B": "Employment Level - 20-24 Yrs.",
                "C": "Multiple Jobholders",
            },
        )

        assert [(line["name"], line["level"]) for line in lines] == [
            ("Employment Level", 1),
            ("16 to 19 years", 2),
            ("20 to 24 years", 2),
            ("All workers", 1),
        ]

    def test_a_lead_of_one_word_is_kept(self):
        """Trimming it would leave the line reading as a fragment."""
        from openbb_fred.utils.release_tables import regroup

        lines = regroup(
            [
                {"series_id": "A", "name": "Retail Trade", "level": 1, "table": "T"},
                {
                    "series_id": "B",
                    "name": "Retail Trade, ex Auto",
                    "level": 1,
                    "table": "T",
                },
            ]
        )

        assert [line["name"] for line in lines] == [
            "Retail Trade",
            "Retail Trade, ex Auto",
        ]


class TestNamedHierarchy:
    """The tree a release describes in the names of its series."""

    def test_a_shared_part_becomes_a_heading(self):
        """A part only one branch takes is read on the heading, not below it."""
        from openbb_fred.utils.release_tables import hierarchy

        lines = hierarchy(
            [
                ("A", "Balances: 30 Days: Accounts"),
                ("B", "Balances: 30 Days: Amounts"),
            ]
        )

        assert [(line["name"], line["level"], line["series_id"]) for line in lines] == [
            ("Balances 30 Days", 1, None),
            ("Accounts", 2, "A"),
            ("Amounts", 2, "B"),
        ]

    def test_a_branch_becomes_a_heading_of_its_own(self):
        from openbb_fred.utils.release_tables import hierarchy

        lines = hierarchy(
            [
                ("A", "Balances: 30 Days: Accounts"),
                ("B", "Balances: 30 Days: Amounts"),
                ("C", "Balances: 60 Days: Accounts"),
                ("D", "Balances: 60 Days: Amounts"),
            ]
        )

        assert [(line["name"], line["level"], line["series_id"]) for line in lines] == [
            ("Balances", 1, None),
            ("30 Days", 2, None),
            ("Accounts", 3, "A"),
            ("Amounts", 3, "B"),
            ("60 Days", 2, None),
            ("Accounts", 3, "C"),
            ("Amounts", 3, "D"),
        ]

    def test_a_name_with_no_punctuation_still_arranges(self):
        """A release that separates the parts by nothing but a space."""
        from openbb_fred.utils.release_tables import hierarchy

        lines = hierarchy(
            [
                ("A", "PADD I Regular Conventional Gas Price"),
                ("B", "PADD I Regular Reformulated Gas Price"),
                ("C", "PADD II Regular Conventional Gas Price"),
            ]
        )

        assert [(line["name"], line["level"], line["series_id"]) for line in lines] == [
            ("PADD", 1, None),
            ("I Regular", 2, None),
            ("Conventional Gas Price", 3, "A"),
            ("Reformulated Gas Price", 3, "B"),
            ("II Regular Conventional Gas Price", 2, "C"),
        ]

    def test_a_part_belonging_to_one_series_stays_on_its_line(self):
        from openbb_fred.utils.release_tables import hierarchy

        lines = hierarchy([("A", "Balances: Total"), ("B", "Originations: New")])

        assert [(line["name"], line["level"]) for line in lines] == [
            ("Balances Total", 1),
            ("Originations New", 1),
        ]

    def test_a_heading_that_is_itself_a_series_carries_it(self):
        """A parent line publishes its own total as well as its children."""
        from openbb_fred.utils.release_tables import hierarchy

        lines = hierarchy([("A", "Balances"), ("B", "Balances: Revolving")])

        assert [(line["name"], line["level"], line["series_id"]) for line in lines] == [
            ("Balances", 1, "A"),
            ("Revolving", 2, "B"),
        ]

    def test_two_series_naming_the_same_line_are_siblings(self):
        """Naming the same thing does not make one the parent of the other."""
        from openbb_fred.utils.release_tables import hierarchy

        lines = hierarchy(
            [("A", "Balances"), ("B", "Balances"), ("C", "Balances: Revolving")]
        )

        assert [(line["name"], line["level"], line["series_id"]) for line in lines] == [
            ("Balances", 1, "A"),
            ("Balances", 1, "B"),
            ("Revolving", 2, "C"),
        ]

    def test_a_name_two_series_share_closes_its_branch(self):
        """Nothing is left under them, so the next heading follows directly."""
        from openbb_fred.utils.release_tables import hierarchy

        lines = hierarchy([("A", "Balances"), ("B", "Balances"), ("C", "Originations")])

        assert [(line["name"], line["level"], line["series_id"]) for line in lines] == [
            ("Balances", 1, "A"),
            ("Balances", 1, "B"),
            ("Originations", 1, "C"),
        ]

    def test_a_series_without_a_name_is_dropped(self):
        from openbb_fred.utils.release_tables import hierarchy

        assert hierarchy([("A", "")]) == []


class TestFrequencies:
    """The publication frequencies one release actually carries."""

    SERIES = {
        "A": {"frequency": "Monthly", "title": "Monthly Series"},
        "B": {"frequency": "Annual", "title": "Annual Series"},
        "C": {"frequency": "Daily", "title": "Daily Series"},
        "D": {"frequency": "Weekly", "title": "Weekly Series (DISCONTINUED)"},
    }

    @pytest.fixture
    def release(self, monkeypatch):
        """Serve one release whose tables each carry their own frequencies."""

        async def observed(release_id, api_key, use_cache=True):
            return {}, self.SERIES

        async def structure(release_id, element_id, api_key, use_cache=True):
            if not element_id:
                return []

            return [
                {"series_id": s, "name": s, "level": 1, "table": "T"}
                for s in ("A", "D")
            ]

        monkeypatch.setattr(
            "openbb_fred.utils.v2.release_observations", observed, raising=False
        )
        monkeypatch.setattr(
            "openbb_fred.utils.release_tables.table_lines", structure, raising=False
        )

    async def test_a_table_offers_only_its_own_frequencies(self, release):
        """The release carries four, the table carries one."""
        from openbb_fred.utils.release_tables import list_frequencies

        offered = await list_frequencies("9", "201241", {"fred_api_key": "key"})

        assert offered == [{"label": "Monthly", "value": "monthly"}]

    async def test_the_release_whole_offers_every_frequency(self, release):
        """Each is offered on its own, the one most published leading."""
        from openbb_fred.utils.release_tables import list_frequencies

        offered = await list_frequencies("9", None, {"fred_api_key": "key"})

        assert offered == [
            {"label": "Daily", "value": "daily"},
            {"label": "Monthly", "value": "monthly"},
            {"label": "Annual", "value": "annual"},
        ]

    async def test_the_most_published_interval_leads(self, release):
        """The leading choice is the one the table is mostly written in."""
        from openbb_fred.utils.release_tables import frequencies

        present = frequencies(
            self.SERIES | {"E": {"frequency": "Annual", "title": "Another Annual"}},
            ["A", "B", "C", "D", "E"],
        )

        assert present == ["annual", "daily", "monthly"]

    async def test_a_retired_series_offers_no_frequency(self, release):
        """The weekly series is retired, so weekly is not on offer."""
        from openbb_fred.utils.release_tables import list_frequencies

        offered = await list_frequencies("9", None, {"fred_api_key": "key"})

        assert "weekly" not in {f["value"] for f in offered}

    async def test_a_table_of_retired_series_offers_nothing(self, release):
        from openbb_fred.utils.release_tables import frequencies

        assert frequencies(self.SERIES, ["D"]) == []

    async def test_an_unreadable_release_offers_nothing(self, monkeypatch):
        from openbb_fred.utils.release_tables import list_frequencies

        async def refuse(release_id, api_key, use_cache=True):
            raise OSError("no answer")

        monkeypatch.setattr(
            "openbb_fred.utils.v2.release_observations", refuse, raising=False
        )

        assert await list_frequencies("9", None, None) == []


class TestReleaseMap:
    """The packaged map of releases and their tables."""

    def test_the_map_is_packaged(self):
        from openbb_fred.utils.release_tables import release_map

        assert len(release_map()) > 200

    def test_every_mapped_release_is_offered(self):
        """A release publishing no table still publishes series."""
        from openbb_fred.utils.release_tables import list_releases, release_map

        offered = {r["value"] for r in list_releases()}

        assert offered == set(release_map())

    def test_a_retired_release_is_not_mapped(self):
        """Coinbase Index stopped publishing, so it is not offered at all."""
        from openbb_fred.utils.release_tables import list_releases, release_map

        assert "440" not in release_map()
        assert "440" not in {r["value"] for r in list_releases()}

    def test_a_release_without_tables_is_offered_whole(self):
        """Zillow publishes its series without arranging them into a table."""
        from openbb_fred.utils.release_tables import list_elements, release_map

        assert release_map()["503"]["elements"] == []
        assert list_elements("503") == [{"label": "All Series", "value": ""}]

    def test_only_tables_are_offered(self):
        """A section is a folder, and holds no lines of its own."""
        from openbb_fred.utils.release_tables import list_elements, release_map

        sections = {
            element["element_id"]
            for element in release_map()["52"]["elements"]
            if element["type"] == "section"
        }

        assert sections
        assert sections.isdisjoint({e["value"] for e in list_elements("52")})

    def test_elements_are_indented_by_depth(self):
        from openbb_fred.utils.release_tables import list_elements

        labels = [e["label"] for e in list_elements("52")]

        assert any(label.startswith("— — ") for label in labels)

    def test_an_unknown_release_is_empty(self):
        from openbb_fred.utils.release_tables import list_elements

        assert list_elements("nope") == []
