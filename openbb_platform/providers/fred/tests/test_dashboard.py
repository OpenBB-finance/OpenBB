"""Test the packaged FRED dashboard, its layout, its groups and its widget schemas."""

import datetime

import pytest

from openbb_fred import ECONOMY_INSTALLED

economy_owned = pytest.mark.skipif(
    ECONOMY_INSTALLED,
    reason="openbb_economy owns the economy and survey commands when it is importable,"
    " so the widgets the template places are not published by this package",
)


class TestInterestRates:
    """The rates tab, from the curve down to what it costs to borrow."""

    CURVE = "fixedincome_government_yield_curve_fred_obb"
    SLOPE = "fixedincome_spreads_tcm_fred_obb"
    TIPS = "fixedincome_government_tips_yields_fred_obb"
    IORB = "fixedincome_rate_iorb_fred_obb"
    DPCREDIT = "fixedincome_rate_dpcredit_fred_obb"
    ECB = "fixedincome_rate_ecb_fred_obb"
    MORTGAGES = "fixedincome_mortgage_indices_fred_obb"
    HQM = "fixedincome_corporate_hqm_fred_obb"
    PAPER = "fixedincome_corporate_commercial_paper_fred_obb"
    SPOT = "fixedincome_corporate_spot_rates_fred_obb"
    BONDS = "fixedincome_bond_indices_fred_obb"

    ORDER = (
        CURVE,
        SLOPE,
        TIPS,
        "fixedincome_rate_effr_fred_obb",
        "fixedincome_rate_sofr_fred_obb",
        IORB,
        DPCREDIT,
        ECB,
        MORTGAGES,
        PAPER,
        HQM,
        SPOT,
        BONDS,
    )

    @pytest.fixture(scope="class")
    def served(self):
        """Read the template as the API serves it."""
        from openbb_core.provider.utils.helpers import run_async

        from openbb_fred.fred_router import fred_apps

        return run_async(fred_apps)[0]

    @pytest.fixture(scope="class")
    def registry(self):
        """Build the widget registry the template refers to."""
        from openbb_core.api.rest_api import app
        from openbb_platform_api.utils.widgets import build_json

        return build_json(app.openapi(), [])

    @pytest.fixture(scope="class")
    def cells(self, served):
        """Index the tab by the id each widget is declared under."""
        from openbb_fred.fred_router import widget_id

        laid_out = {c["i"]: c for c in served["tabs"]["InterestRates"]["layout"]}

        return {declared: laid_out[widget_id(declared)] for declared in self.ORDER}

    @staticmethod
    def _charted(registry, cell):
        """Return the columns a charted widget plots, keyed by chart role."""
        table = (registry[cell["i"]].get("data") or {}).get("table") or {}
        roles: dict = {}

        for column in table.get("columnsDefs") or []:
            roles.setdefault(column.get("chartDataType"), []).append(column["field"])

        return roles

    def test_the_tab_reads_from_the_curve_to_the_cost_of_borrowing(self, served):
        """Term structure, then money market, then policy, then credit."""
        from openbb_fred.fred_router import widget_id

        placed = [c["i"] for c in served["tabs"]["InterestRates"]["layout"]]

        assert placed == [widget_id(declared) for declared in self.ORDER]

    def test_the_curve_is_answered_by_its_own_slope(self, cells):
        """The snapshot alone cannot say whether the curve is inverting."""
        curve, slope = cells[self.CURVE], cells[self.SLOPE]

        assert curve["y"] == slope["y"] == 0
        assert curve["x"] + curve["w"] == slope["x"]
        assert slope["state"]["params"]["maturity"] == "3m"

    def test_every_time_series_opens_as_a_line(self, cells):
        """A rate is read as a line over time, not as a page of numbers."""
        for declared, cell in cells.items():
            if declared == self.TIPS:
                continue

            assert cell["state"]["chartView"] == {
                "enabled": True,
                "chartType": "line",
            }, declared

    def test_a_security_level_yield_stays_a_table(self, cells):
        """One line per outstanding issue is a blob, not a chart."""
        assert cells[self.TIPS]["state"]["chartView"]["enabled"] is False

    def test_a_point_in_time_curve_is_charted_by_maturity(self, cells, registry):
        """Every HQM row shares one date, so a date axis draws one stack of dots."""
        cell = cells[self.HQM]

        if cell["i"] not in registry:
            pytest.skip("the namespace owner serves these widgets in this installation")

        roles = self._charted(registry, cell)

        assert roles.get("time", []) == []
        assert roles["category"] == ["maturity"]
        assert roles["series"] == ["rate"]

    def test_the_yield_curve_is_charted_by_maturity(self, cells, registry):
        """Its rows share a date, so maturity carries the axis and date is dropped."""
        cell = cells[self.CURVE]

        if cell["i"] not in registry:
            pytest.skip("the namespace owner serves these widgets in this installation")

        roles = self._charted(registry, cell)

        assert roles["category"] == ["maturity"]
        assert roles["series"] == ["rate"]
        assert "date" in roles["excluded"]
        assert "time" not in roles

    def test_the_yield_curve_is_left_on_its_latest_date(self, cells):
        """Two dates would stack two curves onto one set of maturity ticks."""
        assert "date" not in cells[self.CURVE]["state"]["params"]

    def test_no_volume_or_index_level_shares_an_axis_with_a_rate(self, cells, registry):
        """A notional in billions flattens every percent it is plotted beside."""
        for declared in (
            "fixedincome_rate_effr_fred_obb",
            "fixedincome_rate_sofr_fred_obb",
        ):
            cell = cells[declared]

            if cell["i"] not in registry:
                pytest.skip(
                    "the namespace owner serves these widgets in this installation"
                )

            roles = self._charted(registry, cell)

            assert "volume" in roles["excluded"], declared
            assert "volume" not in roles["series"], declared
            assert not {"volume", "index"} & set(roles["series"]), declared

    def test_the_tips_default_narrows_to_a_single_tenor(self, cells):
        """All tenors at once draws every outstanding security as one blob."""
        assert cells[self.TIPS]["state"]["params"]["maturity"] == "10"

    def test_a_mortgage_index_asks_for_the_whole_primary_group(self):
        """Wide output carries each index in its own column, so all seven chart."""
        from openbb_fred.models.mortgage_indices import MORTGAGE_CHOICES_TO_ID

        assert len(MORTGAGE_CHOICES_TO_ID["primary"].split(",")) == 7

    def test_a_bond_index_asks_for_the_whole_curve(self, cells):
        """Wide output carries each maturity band in its own column."""
        from openbb_fred.models.bond_indices import BAML_CATEGORIES

        params = cells[self.BONDS]["state"]["params"]
        buckets = BAML_CATEGORIES[params["category"]][params["index"]]

        assert params["index"] == "yield_curve"
        assert len(buckets) == 6

    def test_a_commercial_paper_default_spans_the_short_curve(self, cells):
        """Wide output carries each maturity in its own column."""
        params = cells[self.PAPER]["state"]["params"]

        assert params["maturity"].split(",") == ["overnight", "30d", "90d"]

    def test_a_spot_rate_default_spans_four_tenors(self, cells):
        """Wide output carries each tenor in its own column."""
        params = cells[self.SPOT]["state"]["params"]

        assert params["maturity"].split(",") == ["2", "5", "10", "30"]

    def test_the_administered_rates_share_one_row(self, cells):
        """One series each, so three of them fit the width two charts would take."""
        row = [cells[self.IORB], cells[self.DPCREDIT], cells[self.ECB]]

        assert len({cell["y"] for cell in row}) == 1
        assert sum(cell["w"] for cell in row) == 40
        assert max(cell["w"] for cell in row) < min(
            cells[declared]["w"]
            for declared in self.ORDER
            if declared not in {self.IORB, self.DPCREDIT, self.ECB}
        )

    def test_the_crowded_charts_run_the_full_width(self, cells):
        """A tenor of TIPS and the whole credit curve each need the legend room."""
        assert cells[self.TIPS]["w"] == 40
        assert cells["fixedincome_bond_indices_fred_obb"]["w"] == 40

    def test_no_two_widgets_overlap(self, served):
        """A cell drawn over another hides it completely."""
        held: set = set()

        for cell in served["tabs"]["InterestRates"]["layout"]:
            covered = {
                (x, y)
                for x in range(cell["x"], cell["x"] + cell["w"])
                for y in range(cell["y"], cell["y"] + cell["h"])
            }

            assert covered.isdisjoint(held), cell["i"]

            held |= covered

    def test_one_control_redates_every_history_on_the_tab(self, served, registry):
        """Without the group each chart has to be re-dated on its own."""
        from openbb_fred.fred_router import widget_id

        group = next(g for g in served["groups"] if g["name"] == "History")
        dated = {
            widget_id(declared)
            for declared in self.ORDER
            if declared not in {self.CURVE, self.HQM}
        }

        assert group["paramName"] == "start_date"
        assert set(group["widgetIds"]) == dated

        for declared in (self.CURVE, self.HQM):
            assert widget_id(declared) not in group["widgetIds"]

        if not dated <= set(registry):
            pytest.skip("the namespace owner serves these widgets in this installation")

        for identifier in group["widgetIds"]:
            assert any(
                param["paramName"] == "start_date"
                for param in registry[identifier]["params"]
            ), identifier

    def test_every_preset_is_a_value_the_widget_offers(self, served, registry):
        """A saved parameter the widget does not offer returns nothing."""
        placed = [
            cell
            for cell in served["tabs"]["InterestRates"]["layout"]
            if cell["i"] in registry
        ]

        if not placed:
            pytest.skip("the namespace owner serves these widgets in this installation")

        checked = 0

        for cell in placed:
            offered = {
                param["paramName"]: {
                    option["value"] for option in param.get("options") or []
                }
                for param in registry[cell["i"]]["params"]
            }

            for name, value in (cell["state"].get("params") or {}).items():
                assert name in offered, (cell["i"], name)

                if offered[name]:
                    checked += 1

                    assert set(str(value).split(",")) <= offered[name], (
                        cell["i"],
                        name,
                    )

        assert checked


class TestSeriesDrilldown:
    """Clicking a symbol in the release table charts that series."""

    SEARCH = "economy_fred_search_fred_obb"
    TABLE = "fred_economy_release_table_custom_obb"
    SERIES = "economy_fred_series_fred_obb"

    @pytest.fixture(scope="class")
    def served(self):
        """Read the template as the API serves it."""
        from openbb_core.provider.utils.helpers import run_async

        from openbb_fred.fred_router import fred_apps

        return run_async(fred_apps)[0]

    @pytest.fixture(scope="class")
    def registry(self):
        """Build the widget registry the template refers to."""
        from openbb_core.api.rest_api import app
        from openbb_platform_api.utils.widgets import build_json

        return build_json(app.openapi(), [])

    @pytest.fixture(scope="class")
    def placed(self):
        """Name the drilldown widgets as this installation publishes them."""
        from openbb_fred.fred_router import widget_id

        return [widget_id(self.SEARCH), widget_id(self.TABLE), widget_id(self.SERIES)]

    def test_the_series_chart_sits_below_the_table(self, served, placed):
        laid_out = [c["i"] for c in served["tabs"]["ReleaseTables"]["layout"]]

        assert laid_out == placed

    def test_the_chart_opens_as_a_line(self, served, placed):
        cell = [
            c for c in served["tabs"]["ReleaseTables"]["layout"] if c["i"] == placed[-1]
        ][0]

        assert cell["state"]["chartView"] == {"enabled": True, "chartType": "line"}

    def test_a_symbol_click_drives_the_chart(self, served, registry, placed):
        group = next(g for g in served["groups"] if g["name"] == "Series")

        assert group["paramName"] == "symbol"
        assert group["widgetIds"] == placed

        table = registry[placed[1]]["data"]["table"]
        column = next(c for c in table["columnsDefs"] if c["field"] == "symbol")

        assert column["renderFn"] == "cellOnClick"
        assert column["renderFnParams"] == {
            "actionType": "groupBy",
            "groupBy": {"paramName": "symbol"},
        }

    @economy_owned
    def test_every_group_resolves_on_the_tab_it_belongs_to(self, served, registry):
        """Every member of a group shares one tab and the parameter."""
        for group in served["groups"]:
            members = set(group["widgetIds"])
            tab = next(
                (
                    t
                    for t in served["tabs"].values()
                    if members <= {c["i"] for c in t["layout"]}
                ),
                None,
            )

            assert tab is not None, group["name"]

            for widget in group["widgetIds"]:
                assert any(
                    p["paramName"] == group["paramName"]
                    for p in registry[widget]["params"]
                ), (group["name"], widget)

    @economy_owned
    def test_every_click_column_writes_to_a_grouped_parameter(
        self, served, registry, placed
    ):
        """A click has nowhere to write without a group on the parameter."""
        clicked: dict = {}
        laid_out = {
            cell["i"] for tab in served["tabs"].values() for cell in tab["layout"]
        }

        for identifier in sorted(laid_out):
            table = (registry[identifier].get("data") or {}).get("table") or {}

            for column in table.get("columnsDefs") or []:
                if column.get("renderFn") != "cellOnClick":
                    continue

                params = column["renderFnParams"]

                assert params["actionType"] == "groupBy"

                name = params["groupBy"]["paramName"]
                clicked[identifier, column["field"]] = name

                assert any(
                    g["paramName"] == name and identifier in g["widgetIds"]
                    for g in served["groups"]
                ), (identifier, column["field"])

        assert clicked[placed[0], "series_id"] == "symbol"
        assert clicked[placed[1], "symbol"] == "symbol"

    def test_the_search_is_not_bound_to_the_presented_release(self, served, placed):
        """Binding the release would turn the search into a release listing."""
        bound = {
            g["paramName"] for g in served["groups"] if placed[0] in g["widgetIds"]
        }

        assert bound == {"symbol"}
        assert "release_id" not in {g["paramName"] for g in served["groups"]}

        search = next(
            c for c in served["tabs"]["ReleaseTables"]["layout"] if c["i"] == placed[0]
        )

        assert search["state"]["params"]["search_type"] == "full_text"
        assert "release_id" not in search["state"]["params"]


class TestSparkline:
    """The trend column drawn beside the periods."""

    LINES = [{"series_id": "A", "name": "Total", "level": 1, "table": "T"}]
    SERIES = {
        "A": {
            "series_id": "A",
            "title": "A",
            "units": "Index",
            "frequency": "Monthly",
            "observations": [
                {"date": f"{datetime.date.today().year}-{m:02d}-01", "value": str(m)}
                for m in range(1, 13)
            ],
        }
    }

    @pytest.fixture
    def release(self, monkeypatch):
        """Serve one table without touching the network."""

        async def observed(release_id, api_key, use_cache=True):
            return {"release_id": 1, "name": "One"}, self.SERIES

        async def structure(release_id, element_id, api_key, use_cache=True):
            return self.LINES

        monkeypatch.setattr(
            "openbb_fred.utils.v2.release_observations", observed, raising=False
        )
        monkeypatch.setattr(
            "openbb_fred.utils.release_tables.table_lines", structure, raising=False
        )

    async def test_the_trend_is_a_list_of_values(self, release):
        from openbb_fred.utils.release_tables import build_release_table

        row = (await build_release_table("1", "1", "all", 3, "key"))[0]

        assert row["trend"] == [float(m) for m in range(1, 13)]

    async def test_the_trend_runs_oldest_to_newest(self, release):
        """A sparkline reads left to right, unlike the period columns."""
        from openbb_fred.utils.release_tables import build_release_table

        row = (await build_release_table("1", "1", "all", 3, "key"))[0]

        assert row["trend"][0] < row["trend"][-1]
        assert list(row)[4] > list(row)[5]

    async def test_the_trend_sits_before_the_first_period(self, release):
        from openbb_fred.utils.release_tables import build_release_table

        row = (await build_release_table("1", "1", "all", 3, "key"))[0]

        assert list(row)[:4] == ["series", "symbol", "units", "trend"]

    async def test_the_trend_outruns_the_visible_window(self, release):
        """Showing the same points twice would make the column pointless."""
        from openbb_fred.utils.release_tables import build_release_table

        row = (await build_release_table("1", "1", "all", 3, "key"))[0]
        periods = [k for k in row if k.startswith("20")]

        assert len(row["trend"]) > len(periods)

    def test_the_column_is_declared_with_a_sparkline(self):
        from openbb_core.api.rest_api import app
        from openbb_platform_api.utils.widgets import build_json

        table = build_json(app.openapi(), [])["fred_economy_release_table_custom_obb"][
            "data"
        ]["table"]
        trend = next(c for c in table["columnsDefs"] if c["field"] == "trend")

        assert trend["sparkline"]["type"] == "line"
        assert table["showAll"] is True

    def test_the_sparkline_declares_every_option_the_workspace_reads(self):
        """The Workspace rejects the whole widget when an option is absent."""
        from openbb_core.api.rest_api import app
        from openbb_platform_api.utils.widgets import build_json

        table = build_json(app.openapi(), [])["fred_economy_release_table_custom_obb"][
            "data"
        ]["table"]
        trend = next(c for c in table["columnsDefs"] if c["field"] == "trend")
        options = trend["sparkline"]["options"]

        assert isinstance(options["customFormatter"], str)
        assert options["strokeWidth"] == 2
        assert set(options["pointsOfInterest"]) == {"maximum", "minimum"}

        for point in options["pointsOfInterest"].values():
            assert set(point) == {"fill", "stroke", "size"}

    def test_the_period_columns_stay_inferred(self):
        """Declaring them is impossible - the axis changes with the release."""
        from openbb_core.api.rest_api import app
        from openbb_platform_api.utils.widgets import build_json

        table = build_json(app.openapi(), [])["fred_economy_release_table_custom_obb"][
            "data"
        ]["table"]

        assert [c["field"] for c in table["columnsDefs"]] == [
            "series",
            "symbol",
            "units",
            "trend",
        ]


class TestTableLabels:
    """The table picker reads without the repeated lead."""

    def test_the_repeated_lead_is_dropped(self):
        """Every table in release 9 is named after the release itself."""
        from openbb_fred.utils.release_tables import (
            list_elements,
            release_map,
            shared_prefix,
        )

        release = release_map()["9"]
        names = [
            element["name"]
            for element in release["elements"]
            if element.get("type", "table") == "table"
        ]
        lead = shared_prefix(names)
        labels = [element["label"].lstrip("— ") for element in list_elements("9")]

        assert lead.startswith(release["name"])
        assert labels == [name.removeprefix(lead) for name in names]
        assert not any(label.startswith(lead) for label in labels)

    def test_a_lead_is_cut_at_a_separator(self):
        from openbb_fred.utils.release_tables import shared_prefix

        assert shared_prefix(["Sales: Total, A", "Sales: Total, B"]) == "Sales: Total, "

    def test_a_partial_word_is_not_cut(self):
        """Trimming mid-word would leave the labels unreadable."""
        from openbb_fred.utils.release_tables import shared_prefix

        assert shared_prefix(["Retail Sales", "Retail Stores"]) == ""

    def test_a_single_table_keeps_its_name(self):
        from openbb_fred.utils.release_tables import shared_prefix

        assert shared_prefix(["Only One Table"]) == ""

    def test_names_that_differ_from_the_start_are_untouched(self):
        from openbb_fred.utils.release_tables import (
            list_elements,
            release_map,
            shared_prefix,
        )

        released = release_map()

        assert released

        for release_id in released:
            labels = [
                element["label"].lstrip("— ") for element in list_elements(release_id)
            ]

            assert shared_prefix(labels) == "", release_id

    def test_the_pickers_open_wide(self):
        """A table name runs long, so the popup takes the maximum width."""
        from openbb_core.api.rest_api import app
        from openbb_platform_api.utils.widgets import build_json

        widget = build_json(app.openapi(), [])["fred_economy_release_table_custom_obb"]
        params = {p["paramName"]: p for p in widget["params"]}

        assert params["release_id"]["style"] == {"popupWidth": 1000}
        assert params["element_id"]["style"] == {"popupWidth": 1000}


class TestReleaseTableWidget:
    """The schema the release table widget declares."""

    def test_the_grid_infers_the_period_columns(self):
        """Declared columns cannot describe a period axis that varies."""
        from openbb_core.api.rest_api import app
        from openbb_platform_api.utils.widgets import build_json

        table = build_json(app.openapi(), [])["fred_economy_release_table_custom_obb"][
            "data"
        ]["table"]
        declared = {c["field"] for c in table["columnsDefs"]}

        assert table["showAll"] is True
        assert not any(field.startswith("20") for field in declared)

    def test_the_table_picker_depends_on_the_release(self):
        from openbb_core.api.rest_api import app
        from openbb_platform_api.utils.widgets import build_json

        widget = build_json(app.openapi(), [])["fred_economy_release_table_custom_obb"]
        params = {p["paramName"]: p for p in widget["params"]}

        assert params["element_id"]["optionsParams"] == {"release_id": "$release_id"}
        assert params["element_id"]["optionsEndpoint"].endswith(
            "/economy/element_choices"
        )
