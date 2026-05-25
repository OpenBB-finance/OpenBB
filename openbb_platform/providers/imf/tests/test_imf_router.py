"""Tests for the IMF utilities router."""

# ruff: noqa: I001

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from openbb_imf.imf_router import (
    _APPS_WIDGET_ID_FALLBACK_MAP,
    _INDENT_UNIT,
    _dump_economic_indicator_rows,
    _indent_title,
    _rewrap_indent,
    _render_dataflows_markdown,
    _render_parameters_markdown,
    _rewrite_widget_ids,
    get_dataflow_dimensions,
    get_imf_apps_json,
    indicator_choices,
    list_bop_country_choices,
    list_cpi_country_choices,
    list_dataflow_choices,
    list_dataflows,
    list_table_choices,
    list_tables,
    presentation_table,
    presentation_table_choices,
    router,
)
from openbb_imf.portwatch_router import (
    container_metrics,
    country_activity,
    disruption_events,
    disruption_sankey,
    disruptions_map,
    list_container_port_choices,
    list_country_choices,
    list_disruption_event_choices,
    list_port_id_choices,
    list_tradenow_region_choices,
    monthly_trade,
)


class TestIndentHelpers:
    """Tests for ``_INDENT_UNIT`` and ``_indent_title``."""

    def test_indent_unit_starts_with_gt(self):
        """The unit string starts with ``>`` then eight non-breaking spaces."""
        assert _INDENT_UNIT[0] == ">"
        assert _INDENT_UNIT[1:] == " " * 8

    def test_indent_zero_level_returns_title_unchanged(self):
        """Level 0 (or below) leaves the title untouched."""
        assert _indent_title("Total", 0) == "Total"
        assert _indent_title("Total", -1) == "Total"

    def test_indent_positive_level_prefixes_unit(self):
        """Each positive level prepends one ``_INDENT_UNIT``."""
        assert _indent_title("Total", 1) == _INDENT_UNIT + "Total"
        assert _indent_title("Sub", 2) == _INDENT_UNIT * 2 + "Sub"

    def test_indent_non_string_passes_through(self):
        """Non-string titles short-circuit and return as-is."""
        assert _indent_title(None, 3) is None
        assert _indent_title(7, 3) == 7


class TestRewrapIndent:
    """Tests for ``_rewrap_indent``."""

    def test_no_leading_spaces_returns_unchanged(self):
        """A title without leading whitespace is returned as-is."""
        assert _rewrap_indent("▸ Header") == "▸ Header"
        assert _rewrap_indent("") == ""

    def test_three_spaces_becomes_one_indent_unit(self):
        """Three leading ASCII spaces map to ``_INDENT_UNIT`` (level 1)."""
        assert (
            _rewrap_indent("   Financial assets") == _INDENT_UNIT + "Financial assets"
        )

    def test_six_spaces_becomes_two_indent_units(self):
        """Six leading ASCII spaces map to two ``_INDENT_UNIT`` markers."""
        assert (
            _rewrap_indent("      Monetary gold and SDRs")
            == _INDENT_UNIT * 2 + "Monetary gold and SDRs"
        )

    def test_eight_spaces_floor_divides_to_two(self):
        """Non-multiple leading spaces floor-divide by 3 to a level integer."""
        assert (
            _rewrap_indent("        General government")
            == _INDENT_UNIT * 2 + "General government"
        )

    def test_eleven_spaces_floor_divides_to_three(self):
        """Eleven leading spaces collapse to three ``_INDENT_UNIT`` markers."""
        assert (
            _rewrap_indent("           General government")
            == _INDENT_UNIT * 3 + "General government"
        )

    def test_non_string_passes_through(self):
        """Non-string inputs short-circuit."""
        assert _rewrap_indent(None) is None
        assert _rewrap_indent(7) == 7

    def test_first_character_is_gt_when_indented(self):
        """Every indented title's first character is the literal ``>``."""
        for raw in ("   A", "      B", "        C", "           D"):
            out = _rewrap_indent(raw)
            assert out[0] == ">"


class TestDumpEconomicIndicatorRows:
    """Tests for ``_dump_economic_indicator_rows``."""

    def test_handles_results_attribute(self):
        """The helper unwraps ``.result`` and serialises each model."""
        item = SimpleNamespace(model_dump=lambda **kw: {"k": 1})
        results = SimpleNamespace(result=[item])
        assert _dump_economic_indicator_rows(results) == [{"k": 1}]

    def test_handles_plain_list(self):
        """A plain list is iterated directly."""
        item = SimpleNamespace(model_dump=lambda **kw: {"k": 2})
        assert _dump_economic_indicator_rows([item]) == [{"k": 2}]

    def test_handles_dict_rows(self):
        """Dict rows fall through the ``dict(r)`` branch."""

        class _Mapping:
            """A mapping-like object lacking ``model_dump``."""

            def keys(self):
                """Expose the single ``k`` key."""
                return ["k"]

            def __getitem__(self, key):
                """Return the value for ``k``."""
                return 3 if key == "k" else None

        assert _dump_economic_indicator_rows([_Mapping()]) == [{"k": 3}]

    def test_handles_empty(self):
        """Empty or falsy input returns an empty list."""
        assert _dump_economic_indicator_rows(None) == []
        assert _dump_economic_indicator_rows([]) == []
        assert _dump_economic_indicator_rows(SimpleNamespace(result=[])) == []


class TestRenderMarkdownHelpers:
    """Tests for ``_render_dataflows_markdown`` and ``_render_parameters_markdown``."""

    def test_render_parameters_emits_dim_headers(self):
        """Each dimension produces a level-3 markdown header and a code list."""
        params = {"COUNTRY": [{"value": "USA", "label": "United States"}]}
        md = _render_parameters_markdown(params)
        assert "### `COUNTRY`" in md
        assert "- `USA` : United States" in md
        assert "---" in md

    def test_render_dataflows_walks_dataflows(self):
        """The dataflow renderer pulls indicators, params, and presentations."""
        metadata = MagicMock()
        metadata.dataflows = {"TF": {"name": "Test", "description": "Desc"}}
        metadata.list_all_dataflow_tables.return_value = {
            "TF": [
                {
                    "name": "T1",
                    "description": "d1",
                    "id": "P1",
                    "friendly_name": "Friendly",
                }
            ]
        }
        metadata.get_indicators_in.return_value = [{"code": "X"}]
        metadata.get_dataflow_parameters.return_value = {"COUNTRY": []}

        md = _render_dataflows_markdown(metadata)
        assert "## `TF` - Test" in md
        assert "**Number of Series:** 1" in md
        assert "**Dimensions:** `COUNTRY`" in md
        assert "#### T1" in md
        assert "**Symbol:** `TF::P1`" in md
        assert "**Friendly Name:** `Friendly`" in md
        assert "d1" in md

    def test_render_dataflows_drops_duplicate_presentation_names(self):
        """Duplicate presentation names are emitted only once."""
        metadata = MagicMock()
        metadata.dataflows = {"TF": {"name": "X", "description": ""}}
        metadata.list_all_dataflow_tables.return_value = {
            "TF": [
                {"name": "Same", "id": "P1", "description": "Same"},
                {"name": "Same", "id": "P2", "description": "Same"},
            ]
        }
        metadata.get_indicators_in.return_value = []
        metadata.get_dataflow_parameters.return_value = {}

        md = _render_dataflows_markdown(metadata)
        assert md.count("#### Same") == 1

    def test_render_dataflows_tolerates_missing_indicator_dim(self):
        """A dataflow whose ``get_indicators_in`` raises ``KeyError`` is skipped."""
        metadata = MagicMock()
        metadata.dataflows = {
            "FFS": {"name": "Financial Soundness", "description": "desc"},
            "OK": {"name": "Other", "description": ""},
        }
        metadata.list_all_dataflow_tables.return_value = {}

        def _indicators(df_id):
            """Raise ``KeyError`` for ``FFS`` only."""
            if df_id == "FFS":
                raise KeyError(
                    "Could not find an indicator-like dimension for dataflow 'FFS'."
                )
            return [{"indicator": "X"}]

        metadata.get_indicators_in.side_effect = _indicators
        metadata.get_dataflow_parameters.return_value = {}

        md = _render_dataflows_markdown(metadata)
        assert "## `FFS` - Financial Soundness" in md
        assert "## `OK` - Other" in md
        assert "**Number of Series:** 1" in md


class TestChoiceEndpoints:
    """Tests for the small ``list_*_choices`` async endpoints."""

    @patch("openbb_imf.utils.port_watch_helpers.list_countries")
    @pytest.mark.asyncio
    async def test_list_country_choices_delegates(self, mock_list):
        """``list_country_choices`` defers to ``list_countries``."""
        mock_list.return_value = [{"label": "USA", "value": "USA"}]
        assert await list_country_choices() == [{"label": "USA", "value": "USA"}]
        mock_list.assert_called_once()

    @patch("openbb_imf.utils.port_watch_helpers.get_tradenow_region_choices")
    @pytest.mark.asyncio
    async def test_list_tradenow_region_choices(self, mock_get):
        """The endpoint surfaces the helper's choices unchanged."""
        mock_get.return_value = [{"label": "WLD", "value": "WLD"}]
        assert await list_tradenow_region_choices() == [
            {"label": "WLD", "value": "WLD"}
        ]

    @patch("openbb_imf.utils.port_watch_helpers.get_container_port_choices")
    @pytest.mark.asyncio
    async def test_list_container_port_choices_prepends_top10(self, mock_get):
        """The container-port endpoint prepends the ``TOP10`` sentinel."""
        mock_get.return_value = [{"label": "Port A", "value": "1"}]
        choices = await list_container_port_choices()
        assert choices[0] == {"label": "Top 10 by Metric", "value": "TOP10"}
        assert choices[1] == {"label": "Port A", "value": "1"}

    @patch("openbb_imf.utils.port_watch_helpers.get_sankey_event_choices")
    @pytest.mark.asyncio
    async def test_list_disruption_event_choices_prepends_latest(self, mock_get):
        """The disruption endpoint prepends the ``LATEST`` sentinel."""
        mock_get.return_value = [{"label": "Event A", "value": "1"}]
        choices = await list_disruption_event_choices()
        assert choices[0] == {"label": "Latest Disruption", "value": "LATEST"}
        assert choices[1] == {"label": "Event A", "value": "1"}


class TestPresentationTableIndent:
    """Tests for the ``presentation_table`` post-processing indent logic."""

    def test_indent_rows_via_level_string(self):
        """A string ``level`` is parsed back into an int before indenting."""
        rows = [
            {"title": "A", "level": "0"},
            {"title": "B", "level": "1"},
            {"title": "C", "level": "2"},
        ]
        for row in rows:
            level = row.get("level")
            try:
                lvl = int(level) if level is not None else 0
            except (TypeError, ValueError):
                lvl = 0
            row["title"] = _indent_title(row.get("title", ""), lvl)

        assert rows[0]["title"] == "A"
        assert rows[1]["title"] == _INDENT_UNIT + "B"
        assert rows[2]["title"] == _INDENT_UNIT * 2 + "C"

    def test_indent_rows_with_invalid_level_treats_as_zero(self):
        """A non-numeric level falls back to level 0 (no indent)."""
        row = {"title": "X", "level": "bogus"}
        try:
            lvl = int(row.get("level"))
        except (TypeError, ValueError):
            lvl = 0
        row["title"] = _indent_title(row.get("title", ""), lvl)
        assert row["title"] == "X"


class TestAppsJson:
    """Tests for ``get_imf_apps_json``."""

    @pytest.mark.asyncio
    async def test_returns_apps_json_when_present(self, tmp_path, monkeypatch):
        """A valid ``apps.json`` next to the router yields a parsed list."""
        from openbb_imf import imf_router as router_module

        apps_path = tmp_path / "apps.json"
        apps_path.write_text('[{"name": "Demo"}]', encoding="utf-8")

        monkeypatch.setattr(router_module, "__file__", str(tmp_path / "imf_router.py"))

        assert await get_imf_apps_json() == [{"name": "Demo"}]

    @pytest.mark.asyncio
    async def test_returns_empty_when_missing(self, tmp_path, monkeypatch):
        """A missing ``apps.json`` returns the empty fallback list."""
        from openbb_imf import imf_router as router_module

        monkeypatch.setattr(router_module, "__file__", str(tmp_path / "imf_router.py"))
        assert await get_imf_apps_json() == []


class TestRouterRegistration:
    """Tests confirming the new fetcher endpoints are registered on the router."""

    def test_country_activity_registered(self):
        """``country_activity`` is reachable through the router's api routes."""
        paths = {r.path for r in router.api_router.routes}
        assert any(p.endswith("/country_activity") for p in paths)

    def test_monthly_trade_registered(self):
        """``monthly_trade`` is registered."""
        paths = {r.path for r in router.api_router.routes}
        assert any(p.endswith("/monthly_trade") for p in paths)

    def test_container_metrics_registered(self):
        """``container_metrics`` is registered."""
        paths = {r.path for r in router.api_router.routes}
        assert any(p.endswith("/container_metrics") for p in paths)

    def test_disruption_events_registered(self):
        """``disruption_events`` is registered."""
        paths = {r.path for r in router.api_router.routes}
        assert any(p.endswith("/disruption_events") for p in paths)

    def test_disruptions_map_registered(self):
        """``disruptions_map`` is registered."""
        paths = {r.path for r in router.api_router.routes}
        assert any(p.endswith("/disruptions_map") for p in paths)

    def test_disruption_sankey_registered(self):
        """``disruption_sankey`` is registered."""
        paths = {r.path for r in router.api_router.routes}
        assert any(p.endswith("/disruption_sankey") for p in paths)

    def test_choice_endpoints_registered(self):
        """The 4 ``list_*_choices`` endpoints are registered."""
        paths = {r.path for r in router.api_router.routes}
        assert any(p.endswith("/list_country_choices") for p in paths)
        assert any(p.endswith("/list_tradenow_region_choices") for p in paths)
        assert any(p.endswith("/list_container_port_choices") for p in paths)
        assert any(p.endswith("/list_disruption_event_choices") for p in paths)


def _patched_query_and_obbject(sentinel):
    """Return contextmanagers patching ``OBBQuery`` and ``OBBject.from_query``."""
    return (
        patch("openbb_imf.portwatch_router.OBBQuery", new=MagicMock()),
        patch(
            "openbb_imf.portwatch_router.OBBject.from_query",
            new=AsyncMock(return_value=sentinel),
        ),
    )


class TestFetcherEndpointBodies:
    """Invocation tests for the 6 new fetcher-backed endpoint bodies."""

    @pytest.mark.asyncio
    async def test_country_activity_calls_from_query(self):
        """``country_activity`` delegates to ``OBBject.from_query``."""

        sentinel = SimpleNamespace(result=[])
        q_patch, o_patch = _patched_query_and_obbject(sentinel)
        with q_patch, o_patch as mock_from_query:
            out = await country_activity(
                cc=MagicMock(),
                provider_choices=MagicMock(),
                standard_params=MagicMock(),
                extra_params=MagicMock(),
            )
        assert out is sentinel
        mock_from_query.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_monthly_trade_calls_from_query(self):
        """``monthly_trade`` delegates to ``OBBject.from_query``."""

        sentinel = SimpleNamespace(result=[])
        q_patch, o_patch = _patched_query_and_obbject(sentinel)
        with q_patch, o_patch:
            out = await monthly_trade(
                cc=MagicMock(),
                provider_choices=MagicMock(),
                standard_params=MagicMock(),
                extra_params=MagicMock(),
            )
        assert out is sentinel

    @pytest.mark.asyncio
    async def test_container_metrics_calls_from_query(self):
        """``container_metrics`` delegates to ``OBBject.from_query``."""

        sentinel = SimpleNamespace(result=[])
        q_patch, o_patch = _patched_query_and_obbject(sentinel)
        with q_patch, o_patch:
            out = await container_metrics(
                cc=MagicMock(),
                provider_choices=MagicMock(),
                standard_params=MagicMock(),
                extra_params=MagicMock(),
            )
        assert out is sentinel

    @pytest.mark.asyncio
    async def test_disruption_events_calls_from_query(self):
        """``disruption_events`` delegates to ``OBBject.from_query``."""

        sentinel = SimpleNamespace(result=[])
        q_patch, o_patch = _patched_query_and_obbject(sentinel)
        with q_patch, o_patch:
            out = await disruption_events(
                cc=MagicMock(),
                provider_choices=MagicMock(),
                standard_params=MagicMock(),
                extra_params=MagicMock(),
            )
        assert out is sentinel

    @pytest.mark.asyncio
    async def test_disruptions_map_calls_from_query(self):
        """``disruptions_map`` delegates to ``OBBject.from_query``."""

        sentinel = SimpleNamespace(result=[])
        q_patch, o_patch = _patched_query_and_obbject(sentinel)
        with q_patch, o_patch:
            out = await disruptions_map(
                cc=MagicMock(),
                provider_choices=MagicMock(),
                standard_params=MagicMock(),
                extra_params=MagicMock(),
            )
        assert out is sentinel

    @pytest.mark.asyncio
    async def test_disruption_sankey_calls_from_query(self):
        """``disruption_sankey`` delegates to ``OBBject.from_query``."""

        sentinel = SimpleNamespace(result=[])
        q_patch, o_patch = _patched_query_and_obbject(sentinel)
        with q_patch, o_patch:
            out = await disruption_sankey(
                cc=MagicMock(),
                provider_choices=MagicMock(),
                standard_params=MagicMock(),
                extra_params=MagicMock(),
            )
        assert out is sentinel


class TestListDataflows:
    """Tests for ``list_dataflows``."""

    @pytest.mark.asyncio
    async def test_json_returns_dataflow_dict(self):
        """JSON output returns ``metadata.dataflows`` verbatim."""
        meta = MagicMock()
        meta.dataflows = {"X": {"name": "X"}}
        meta.list_all_dataflow_tables.return_value = {}
        out = await list_dataflows(meta, output_format="json")
        assert out.results == {"X": {"name": "X"}}

    @pytest.mark.asyncio
    async def test_markdown_returns_rendered_string(self):
        """Markdown output delegates to ``_render_dataflows_markdown``."""
        meta = MagicMock()
        meta.dataflows = {"X": {"name": "X"}}
        meta.list_all_dataflow_tables.return_value = {}
        meta.get_indicators_in.return_value = []
        meta.get_dataflow_parameters.return_value = {}
        out = await list_dataflows(meta, output_format="markdown")
        assert isinstance(out.results, str)
        assert "## `X`" in out.results


class TestGetDataflowDimensions:
    """Tests for ``get_dataflow_dimensions``."""

    @pytest.mark.asyncio
    async def test_json_format_returns_params(self):
        """JSON format returns the raw parameters dict."""
        meta = MagicMock()
        meta.get_dataflow_parameters.return_value = {"COUNTRY": []}
        out = await get_dataflow_dimensions(meta, dataflow_id="X", output_format="json")
        assert out.results == {"COUNTRY": []}

    @pytest.mark.asyncio
    async def test_markdown_format_renders(self):
        """Markdown format goes through ``_render_parameters_markdown``."""
        meta = MagicMock()
        meta.get_dataflow_parameters.return_value = {
            "COUNTRY": [{"value": "USA", "label": "United States"}]
        }
        out = await get_dataflow_dimensions(
            meta, dataflow_id="X", output_format="markdown"
        )
        assert "### `COUNTRY`" in out.results


class TestListPortIdChoices:
    """Tests for ``list_port_id_choices``."""

    @pytest.mark.asyncio
    async def test_delegates_to_helper(self):
        """The endpoint forwards the helper output unchanged."""
        with patch(
            "openbb_imf.utils.port_watch_helpers.get_port_id_choices",
            return_value=[{"label": "Port", "value": "P1"}],
        ):
            assert await list_port_id_choices() == [{"label": "Port", "value": "P1"}]


class TestListTables:
    """Tests for ``list_tables``."""

    @pytest.mark.asyncio
    async def test_builds_imf_table_metadata(self):
        """Each presentation becomes an ``ImfTableMetadata`` instance."""
        meta = MagicMock()
        meta.list_all_dataflow_tables.return_value = {
            "DF1": [
                {
                    "id": "T1",
                    "name": "Table 1",
                    "description": " desc ",
                    "agency_id": "IMF.STA",
                    "codelist_id": "CL",
                }
            ]
        }
        out = await list_tables(meta)
        assert len(out.results) == 1
        first = out.results[0]
        assert first.name == "Table 1"
        assert first.symbol == "DF1::T1"
        assert first.description == "desc"


class TestListTableChoices:
    """Tests for ``list_table_choices``."""

    @pytest.mark.asyncio
    async def test_flattens_presentations(self):
        """Each presentation becomes a ``{label, value}`` row."""
        meta = MagicMock()
        meta.list_all_dataflow_tables.return_value = {
            "DF1": [{"id": "T1", "name": "Table 1"}],
            "DF2": [{"id": "T2", "name": "Table 2"}],
        }
        out = await list_table_choices(meta)
        assert {row["value"] for row in out} == {"DF1::T1", "DF2::T2"}


class TestListDataflowChoices:
    """Tests for ``list_dataflow_choices``."""

    @pytest.mark.asyncio
    async def test_sorts_by_label(self):
        """Choices are sorted by the human-readable label."""
        meta = MagicMock()
        meta.dataflows = {
            "Z": {"name": "Zeta"},
            "A": {"name": "Alpha"},
        }
        out = await list_dataflow_choices(meta)
        assert [r["label"] for r in out] == ["Alpha", "Zeta"]


class TestPresentationTableChoices:
    """Tests for the progressive ``presentation_table_choices`` endpoint."""

    @pytest.mark.asyncio
    async def test_no_dataflow_group_returns_global_choices(self):
        """With no ``dataflow_group``, the global table_dataflow_choices is returned."""
        from openbb_imf.utils.constants import table_dataflow_choices

        meta = MagicMock()
        out = await presentation_table_choices(meta)
        assert out == table_dataflow_choices

    @pytest.mark.asyncio
    async def test_dataflow_group_only_returns_table_choices(self):
        """Group without table returns the table names for that group."""
        meta = MagicMock()
        out = await presentation_table_choices(meta, dataflow_group="cpi")
        assert any(r["value"] == "cpi" for r in out)

    @pytest.mark.asyncio
    async def test_table_with_country_dim_returns_country_choices(self):
        """Group+table returns sorted countries using the ``COUNTRY`` dimension."""
        meta = MagicMock()
        meta.get_dataflow_parameters.return_value = {
            "COUNTRY": [
                {"label": "Zambia", "value": "ZMB"},
                {"label": "Angola", "value": "AGO"},
            ]
        }
        out = await presentation_table_choices(meta, dataflow_group="cpi", table="cpi")
        assert [r["value"] for r in out] == ["AGO", "ZMB"]

    @pytest.mark.asyncio
    async def test_table_with_jurisdiction_dim(self):
        """When ``COUNTRY`` is absent, fall back to ``JURISDICTION``."""
        meta = MagicMock()
        meta.get_dataflow_parameters.return_value = {
            "JURISDICTION": [{"label": "USA", "value": "USA"}]
        }
        out = await presentation_table_choices(meta, dataflow_group="cpi", table="cpi")
        assert out == [{"label": "USA", "value": "USA"}]

    @pytest.mark.asyncio
    async def test_table_with_ref_area_dim(self):
        """When neither ``COUNTRY`` nor ``JURISDICTION`` is present, use ``REF_AREA``."""
        meta = MagicMock()
        meta.get_dataflow_parameters.return_value = {
            "REF_AREA": [{"label": "World", "value": "WLD"}]
        }
        out = await presentation_table_choices(meta, dataflow_group="cpi", table="cpi")
        assert out == [{"label": "World", "value": "WLD"}]

    @pytest.mark.asyncio
    async def test_frequency_branch_calls_params_builder(self):
        """Group+table+country reaches the ``ImfParamsBuilder`` frequency branch."""

        meta = MagicMock()
        meta.get_dataflow_parameters.return_value = {"COUNTRY": [], "FREQUENCY": []}
        meta.get_dataflow_table_structure.return_value = {
            "indicators": [
                {"indicator_code": "X", "dimension_id": "INDICATOR"},
                {"indicator_code": "X", "dimension_id": "INDICATOR"},
                {"indicator_code": "Y", "dimension_id": "INDICATOR"},
                {"indicator_code": None, "dimension_id": "BAD"},
            ]
        }

        fake_pb = MagicMock()
        fake_pb._get_dimensions_in_order.return_value = [
            "INDICATOR",
            "COUNTRY",
            "FREQUENCY",
            "OTHER",
        ]
        fake_pb.get_options_for_dimension.return_value = [
            {"label": "Annual", "value": "A"}
        ]

        with patch(
            "openbb_imf.utils.progressive_helper.ImfParamsBuilder",
            return_value=fake_pb,
        ):
            out = await presentation_table_choices(
                meta,
                dataflow_group="cpi",
                table="cpi",
                country="USA,GBR",
            )
        assert out == [{"label": "Annual", "value": "A"}]
        fake_pb.get_options_for_dimension.assert_called_once_with("FREQUENCY")
        fake_pb.set_dimension.assert_any_call(("INDICATOR", "X+Y"))
        fake_pb.set_dimension.assert_any_call(("COUNTRY", "USA+GBR"))

    @pytest.mark.asyncio
    async def test_indicator_long_joined_truncated_to_top20(self):
        """Joined indicator codes >800 chars are truncated to the first 20."""
        meta = MagicMock()
        meta.get_dataflow_parameters.return_value = {"COUNTRY": []}
        codes = [f"CODE{i:016d}" for i in range(60)]
        meta.get_dataflow_table_structure.return_value = {
            "indicators": [
                {"indicator_code": c, "dimension_id": "INDICATOR"} for c in codes
            ]
        }

        fake_pb = MagicMock()
        fake_pb._get_dimensions_in_order.return_value = ["INDICATOR", "COUNTRY"]
        fake_pb.get_options_for_dimension.return_value = []

        with patch(
            "openbb_imf.utils.progressive_helper.ImfParamsBuilder",
            return_value=fake_pb,
        ):
            await presentation_table_choices(
                meta,
                dataflow_group="cpi",
                table="cpi",
                country="USA",
            )
        ind_call = next(
            c
            for c in fake_pb.set_dimension.call_args_list
            if c.args[0][0] == "INDICATOR"
        )
        joined = ind_call.args[0][1]
        assert len(joined.split("+")) == 20

    @pytest.mark.asyncio
    async def test_indicator_codes_truncated_to_wildcard(self):
        """Even truncated to 20, oversize joined codes collapse to ``*``."""
        meta = MagicMock()
        meta.get_dataflow_parameters.return_value = {"COUNTRY": []}
        codes = [f"CODE_{i:0050d}" for i in range(40)]
        meta.get_dataflow_table_structure.return_value = {
            "indicators": [
                {"indicator_code": c, "dimension_id": "INDICATOR"} for c in codes
            ]
        }

        fake_pb = MagicMock()
        fake_pb._get_dimensions_in_order.return_value = ["INDICATOR", "COUNTRY"]
        fake_pb.get_options_for_dimension.return_value = []

        with patch(
            "openbb_imf.utils.progressive_helper.ImfParamsBuilder",
            return_value=fake_pb,
        ):
            await presentation_table_choices(
                meta,
                dataflow_group="cpi",
                table="cpi",
                country="USA",
            )
        ind_call = next(
            c
            for c in fake_pb.set_dimension.call_args_list
            if c.args[0][0] == "INDICATOR"
        )
        assert ind_call.args[0][1] == "*"

    @pytest.mark.asyncio
    async def test_freq_branch_with_freq_fallback(self):
        """When ``FREQUENCY`` is absent, fall back to ``FREQ`` as the freq dim."""

        meta = MagicMock()
        meta.get_dataflow_parameters.return_value = {"REF_AREA": [], "FREQ": []}
        meta.get_dataflow_table_structure.return_value = {"indicators": []}

        fake_pb = MagicMock()
        fake_pb._get_dimensions_in_order.return_value = ["REF_AREA", "FREQ"]
        fake_pb.get_options_for_dimension.return_value = []

        with patch(
            "openbb_imf.utils.progressive_helper.ImfParamsBuilder",
            return_value=fake_pb,
        ):
            out = await presentation_table_choices(
                meta,
                dataflow_group="cpi",
                table="cpi",
                country="USA",
            )
        fake_pb.get_options_for_dimension.assert_called_once_with("FREQ")
        assert out == []

    @pytest.mark.asyncio
    async def test_all_four_params_returns_transform_options(self):
        """All four params set takes the ``TYPE_OF_TRANSFORMATION`` branch."""
        meta = MagicMock()
        meta.get_dataflow_parameters.return_value = {
            "COUNTRY": [],
            "FREQUENCY": [],
            "TYPE_OF_TRANSFORMATION": [],
        }
        meta.get_dataflow_table_structure.return_value = {
            "indicators": [
                {"indicator_code": "X", "dimension_id": "INDICATOR"},
            ]
        }

        fake_pb = MagicMock()
        fake_pb._get_dimensions_in_order.return_value = [
            "INDICATOR",
            "COUNTRY",
            "FREQUENCY",
            "TYPE_OF_TRANSFORMATION",
        ]
        fake_pb.get_options_for_dimension.return_value = [
            {"label": "Percent Change", "value": "PCH"}
        ]

        with patch(
            "openbb_imf.utils.progressive_helper.ImfParamsBuilder",
            return_value=fake_pb,
        ):
            out = await presentation_table_choices(
                meta,
                dataflow_group="cpi",
                table="cpi",
                country="USA",
                frequency="A",
            )
        assert out == [{"label": "Percent Change", "value": "PCH"}]
        fake_pb.get_options_for_dimension.assert_called_once_with(
            "TYPE_OF_TRANSFORMATION"
        )
        fake_pb.set_dimension.assert_any_call(("INDICATOR", "X"))
        fake_pb.set_dimension.assert_any_call(("COUNTRY", "USA"))
        fake_pb.set_dimension.assert_any_call(("FREQUENCY", "A"))

    @pytest.mark.asyncio
    async def test_all_four_params_indicator_truncated_to_wildcard(self):
        """In the transform branch, oversize indicator joins collapse to ``*``."""
        meta = MagicMock()
        meta.get_dataflow_parameters.return_value = {
            "COUNTRY": [],
            "FREQUENCY": [],
            "TYPE_OF_TRANSFORMATION": [],
        }
        codes = [f"CODE_{i:0050d}" for i in range(40)]
        meta.get_dataflow_table_structure.return_value = {
            "indicators": [
                {"indicator_code": c, "dimension_id": "INDICATOR"} for c in codes
            ]
        }

        fake_pb = MagicMock()
        fake_pb._get_dimensions_in_order.return_value = [
            "INDICATOR",
            "COUNTRY",
            "FREQUENCY",
            "TYPE_OF_TRANSFORMATION",
        ]
        fake_pb.get_options_for_dimension.return_value = []

        with patch(
            "openbb_imf.utils.progressive_helper.ImfParamsBuilder",
            return_value=fake_pb,
        ):
            await presentation_table_choices(
                meta,
                dataflow_group="cpi",
                table="cpi",
                country="USA",
                frequency="A",
            )
        ind_call = next(
            c
            for c in fake_pb.set_dimension.call_args_list
            if c.args[0][0] == "INDICATOR"
        )
        assert ind_call.args[0][1] == "*"

    @pytest.mark.asyncio
    async def test_all_four_params_no_transform_dim_returns_empty(self):
        """When the dataflow has no ``TYPE_OF_TRANSFORMATION``, returns ``[]``."""
        meta = MagicMock()
        meta.get_dataflow_parameters.return_value = {
            "COUNTRY": [],
            "FREQUENCY": [],
        }
        meta.get_dataflow_table_structure.return_value = {"indicators": []}

        fake_pb = MagicMock()
        fake_pb._get_dimensions_in_order.return_value = ["COUNTRY", "FREQUENCY"]
        fake_pb.get_options_for_dimension.return_value = []

        with patch(
            "openbb_imf.utils.progressive_helper.ImfParamsBuilder",
            return_value=fake_pb,
        ):
            out = await presentation_table_choices(
                meta,
                dataflow_group="cpi",
                table="cpi",
                country="USA",
                frequency="A",
            )
        assert out == []
        fake_pb.get_options_for_dimension.assert_not_called()


class TestPresentationTable:
    """Tests for the ``presentation_table`` endpoint."""

    @pytest.mark.asyncio
    async def test_missing_dataflow_group_raises(self):
        """Missing dataflow_group is rejected as ``OpenBBError``."""
        from openbb_core.app.model.abstract.error import OpenBBError

        with pytest.raises(OpenBBError):
            await presentation_table(table="cpi", country="USA", frequency="A")

    @pytest.mark.asyncio
    async def test_missing_country_raises(self):
        """Missing country is rejected as ``OpenBBError``."""
        from openbb_core.app.model.abstract.error import OpenBBError

        with pytest.raises(OpenBBError):
            await presentation_table(dataflow_group="cpi", table="cpi", frequency="A")

    @pytest.mark.asyncio
    async def test_indents_titles_from_fetcher_rows(self):
        """Fetcher rows have their ``title`` indented according to ``level``."""
        rows = [
            SimpleNamespace(model_dump=lambda **_: {"title": "Top", "level": 0}),
            SimpleNamespace(model_dump=lambda **_: {"title": "Child", "level": "1"}),
            SimpleNamespace(model_dump=lambda **_: {"title": "Bad", "level": "junk"}),
        ]
        result_holder = SimpleNamespace(result=rows)

        with patch(
            "openbb_imf.models.economic_indicators.ImfEconomicIndicatorsFetcher.fetch_data",
            new=AsyncMock(return_value=result_holder),
        ):
            out = await presentation_table(
                dataflow_group="cpi",
                table="cpi",
                country="USA",
                frequency="A",
                limit=1,
            )
        assert out[0]["title"] == "Top"
        assert out[1]["title"] == _INDENT_UNIT + "Child"
        assert out[2]["title"] == "Bad"

    @pytest.mark.asyncio
    async def test_rewraps_pre_indented_titles_when_level_missing(self):
        """Rows with ``level=None`` have leading whitespace rewrapped to ``_INDENT_UNIT``."""
        rows = [
            SimpleNamespace(
                model_dump=lambda **_: {
                    "title": "▸ 3. GOVERNMENT BALANCE SHEET",
                    "level": None,
                }
            ),
            SimpleNamespace(
                model_dump=lambda **_: {"title": "   Financial assets", "level": None}
            ),
            SimpleNamespace(
                model_dump=lambda **_: {
                    "title": "        General government",
                    "level": None,
                }
            ),
            SimpleNamespace(
                model_dump=lambda **_: {
                    "title": "           Central government",
                    "level": None,
                }
            ),
        ]
        result_holder = SimpleNamespace(result=rows)

        with patch(
            "openbb_imf.models.economic_indicators.ImfEconomicIndicatorsFetcher.fetch_data",
            new=AsyncMock(return_value=result_holder),
        ):
            out = await presentation_table(
                dataflow_group="qgfs",
                table="qgfs_balance",
                country="BRA",
                frequency="Q",
                limit=1,
            )
        assert out[0]["title"] == "▸ 3. GOVERNMENT BALANCE SHEET"
        assert out[1]["title"] == _INDENT_UNIT + "Financial assets"
        assert out[2]["title"] == _INDENT_UNIT * 2 + "General government"
        assert out[3]["title"] == _INDENT_UNIT * 3 + "Central government"
        for row in out[1:]:
            assert row["title"][0] == ">"

    @pytest.mark.asyncio
    async def test_drops_country_for_single_country_request(self):
        """When the country parameter resolves to one country the column is dropped."""
        rows = [
            SimpleNamespace(
                model_dump=lambda **_: {
                    "country": "United States",
                    "title": "Header",
                    "level": 0,
                    "2025-06-30": 1.0,
                    "2025-12-31": 2.0,
                    "2025-09-30": 3.0,
                }
            )
        ]
        result_holder = SimpleNamespace(result=rows)
        with patch(
            "openbb_imf.models.economic_indicators.ImfEconomicIndicatorsFetcher.fetch_data",
            new=AsyncMock(return_value=result_holder),
        ):
            out = await presentation_table(
                dataflow_group="cpi",
                table="cpi",
                country="USA",
                frequency="A",
                limit=1,
            )
        assert list(out[0].keys()) == [
            "title",
            "2025-12-31",
            "2025-09-30",
            "2025-06-30",
        ]
        assert "country" not in out[0]

    @pytest.mark.asyncio
    async def test_keeps_country_for_multi_country_request(self):
        """When the country parameter lists multiple codes the column is kept."""
        rows = [
            SimpleNamespace(
                model_dump=lambda **_: {
                    "country": "United States",
                    "title": "Header",
                    "level": 0,
                    "2025-12-31": 1.0,
                    "extra_meta": "kept",
                }
            )
        ]
        result_holder = SimpleNamespace(result=rows)
        with patch(
            "openbb_imf.models.economic_indicators.ImfEconomicIndicatorsFetcher.fetch_data",
            new=AsyncMock(return_value=result_holder),
        ):
            out = await presentation_table(
                dataflow_group="cpi",
                table="cpi",
                country="USA+JPN",
                frequency="A",
                limit=1,
            )
        assert list(out[0].keys()) == ["country", "title", "2025-12-31", "extra_meta"]
        assert out[0]["country"] == "United States"
        assert out[0]["extra_meta"] == "kept"


class TestIndicatorChoices:
    """Tests for the ``indicator_choices`` progressive endpoint."""

    def _meta(self, dim_order=("COUNTRY", "INDICATOR", "FREQUENCY"), **overrides):
        """Build a fake metadata supporting indicator_choices' lookups."""
        meta = MagicMock()
        meta.dataflows = {
            "DF1": {"id": "DF1", "structureRef": {"id": "DSD1"}, "name": "DF1"}
        }
        meta.datastructures = {
            "DSD1": {
                "dimensions": [
                    {"id": dim, "position": str(i)} for i, dim in enumerate(dim_order)
                ]
                + [{"id": "TIME_PERIOD", "position": "99"}]
            }
        }
        meta.get_dataflow_parameters.return_value = overrides.get(
            "params",
            {
                "COUNTRY": [{"value": "USA", "label": "United States"}],
                "INDICATOR": [{"value": "GDP", "label": "Gross Domestic"}],
                "FREQUENCY": [{"value": "A", "label": "Annual"}],
            },
        )
        meta.get_available_constraints.return_value = overrides.get(
            "constraints",
            {
                "key_values": [
                    {
                        "id": "COUNTRY",
                        "values": ["USA"],
                    },
                    {
                        "id": "FREQUENCY",
                        "values": ["A"],
                    },
                    {
                        "id": "INDICATOR",
                        "values": ["GDP"],
                    },
                ]
            },
        )
        meta._resolve_codelist_id.return_value = "CL_X"
        meta._codelist_cache = overrides.get("codelist_cache", {"CL_X": {}})
        return meta

    @pytest.mark.asyncio
    async def test_returns_empty_when_symbol_missing(self):
        """No symbol → empty list."""
        assert await indicator_choices(self._meta(), symbol=None) == []

    @pytest.mark.asyncio
    async def test_returns_empty_when_all_symbols_blank(self):
        """All-whitespace symbol list → empty."""
        assert await indicator_choices(self._meta(), symbol=" , , ") == []

    @pytest.mark.asyncio
    async def test_returns_empty_when_dataflow_unknown(self):
        """Unknown dataflow ID → empty."""
        meta = self._meta()
        meta.dataflows = {}
        assert (
            await indicator_choices(meta, symbol="UNKNOWN::IND", country="true") == []
        )

    @pytest.mark.asyncio
    async def test_country_branch(self):
        """``country='true'`` returns sorted countries with an ``All`` row prefix."""
        meta = self._meta()
        out = await indicator_choices(meta, symbol="DF1::GDP", country="true")
        assert out[0] == {"label": "All Countries", "value": "*"}
        assert {row["value"] for row in out[1:]} == {"USA"}

    @pytest.mark.asyncio
    async def test_frequency_branch(self):
        """``frequency='true'`` returns frequency options."""
        meta = self._meta()
        out = await indicator_choices(
            meta, symbol="DF1::GDP", country="USA", frequency="true"
        )
        assert any(row["value"] == "A" for row in out)

    @pytest.mark.asyncio
    async def test_transform_branch_with_unit_fallback(self):
        """``transform='true'`` resolves the transform dim via ``detect_transform_dimension``."""

        meta = self._meta(
            dim_order=("COUNTRY", "INDICATOR", "FREQUENCY", "UNIT_MEASURE")
        )
        meta.get_dataflow_parameters.return_value = {
            "COUNTRY": [{"value": "USA", "label": "United States"}],
            "INDICATOR": [{"value": "GDP", "label": "Gross Domestic"}],
            "FREQUENCY": [{"value": "A", "label": "Annual"}],
            "UNIT_MEASURE": [{"value": "USD", "label": "USD"}],
        }
        meta.get_available_constraints.return_value = {
            "key_values": [{"id": "UNIT_MEASURE", "values": ["USD"]}]
        }

        with patch(
            "openbb_imf.utils.helpers.detect_transform_dimension",
            return_value=(None, "UNIT_MEASURE", None, None),
        ):
            out = await indicator_choices(
                meta,
                symbol="DF1::GDP",
                country="USA",
                frequency="A",
                transform="true",
            )
        assert out[0] == {"label": "All", "value": "all"}
        assert any(row["value"] == "USD" for row in out[1:])

    @pytest.mark.asyncio
    async def test_transform_branch_empty_when_no_transform_dim(self):
        """Without an effective transform dim, the transform branch returns ``[]``."""

        meta = self._meta()
        with patch(
            "openbb_imf.utils.helpers.detect_transform_dimension",
            return_value=(None, None, None, None),
        ):
            out = await indicator_choices(
                meta,
                symbol="DF1::GDP",
                country="USA",
                frequency="A",
                transform="true",
            )
        assert out == []

    @pytest.mark.asyncio
    async def test_default_fallthrough_returns_empty(self):
        """When none of the ``true`` toggles fire, the function returns ``[]``."""
        meta = self._meta()
        out = await indicator_choices(
            meta, symbol="DF1::GDP", country="USA", frequency="A"
        )
        assert out == []

    @pytest.mark.asyncio
    async def test_symbol_without_double_colon_added_to_dataflows(self):
        """A bare symbol (no ``::``) is treated as a dataflow id."""
        meta = self._meta()
        out = await indicator_choices(meta, symbol="DF1", country="true")
        assert out[0] == {"label": "All Countries", "value": "*"}

    @pytest.mark.asyncio
    async def test_multi_symbol_joined_into_plus_separated(self):
        """Multiple comma-separated symbols join into a single ``+``-separated key."""

        meta = self._meta()
        meta.get_available_constraints.return_value = {
            "key_values": [{"id": "FREQUENCY", "values": ["A"]}]
        }
        with patch(
            "openbb_imf.utils.helpers.detect_transform_dimension",
            return_value=(None, None, None, None),
        ):
            await indicator_choices(
                meta,
                symbol="DF1::GDP,DF1::CPI",
                country="USA",
                frequency="true",
            )
        called_with = meta.get_available_constraints.call_args.kwargs
        assert "GDP+CPI" in called_with["key"]

    @pytest.mark.asyncio
    async def test_dimension_values_extra_filters_applied(self):
        """``dimension_values`` are split into ``DIM:VAL`` pairs and consumed."""
        meta = self._meta(dim_order=("COUNTRY", "INDICATOR", "FREQUENCY", "SECTOR"))
        meta.get_dataflow_parameters.return_value = {
            "COUNTRY": [{"value": "USA", "label": "USA"}],
            "INDICATOR": [{"value": "GDP", "label": "GDP"}],
            "FREQUENCY": [{"value": "A", "label": "Annual"}],
            "SECTOR": [{"value": "FIN", "label": "Finance"}],
        }
        meta.get_available_constraints.return_value = {
            "key_values": [{"id": "FREQUENCY", "values": ["A"]}]
        }
        out = await indicator_choices(
            meta,
            symbol="DF1::GDP",
            frequency="true",
            dimension_values=[
                "COUNTRY:USA",
                "SECTOR:FIN",
                "BAD_NO_COLON",
                "",
                None,
            ],
        )
        assert any(row["value"] == "A" for row in out)

    @pytest.mark.asyncio
    async def test_indicator_dim_resolved_via_dim_order_fallback(self):
        """When the indicator code isn't in any known indicator-dim, search dim_order."""
        meta = self._meta(dim_order=("COUNTRY", "WIDGET_KIND", "FREQUENCY"))
        meta.get_dataflow_parameters.return_value = {
            "COUNTRY": [{"value": "USA", "label": "USA"}],
            "WIDGET_KIND": [{"value": "GDP", "label": "GDP"}],
            "FREQUENCY": [{"value": "A", "label": "Annual"}],
        }
        meta.get_available_constraints.return_value = {
            "key_values": [{"id": "WIDGET_KIND", "values": ["GDP"]}]
        }
        out = await indicator_choices(meta, symbol="DF1::GDP", country="true")
        assert any(row["value"] == "USA" for row in out[1:]) or out[0] == {
            "label": "All Countries",
            "value": "*",
        }

    @pytest.mark.asyncio
    async def test_indicator_dim_resolved_via_known_first_match_in_indicator_dims(
        self,
    ):
        """If the first known indicator dim contains the code, it wins."""
        meta = self._meta(dim_order=("COUNTRY", "INDICATOR", "INDEX_TYPE", "FREQUENCY"))
        meta.get_dataflow_parameters.return_value = {
            "COUNTRY": [{"value": "USA", "label": "USA"}],
            "INDICATOR": [{"value": "GDP", "label": "GDP"}],
            "INDEX_TYPE": [{"value": "GDP", "label": "Different GDP"}],
            "FREQUENCY": [{"value": "A", "label": "Annual"}],
        }
        meta.get_available_constraints.return_value = {
            "key_values": [{"id": "COUNTRY", "values": ["USA"]}]
        }
        out = await indicator_choices(meta, symbol="DF1::GDP", country="true")
        assert out[0]["value"] == "*"

    @pytest.mark.asyncio
    async def test_indicator_dim_default_when_no_match(self):
        """If no dim contains the indicator value, fall back to the first known one."""
        meta = self._meta(dim_order=("COUNTRY", "INDICATOR", "FREQUENCY"))
        meta.get_dataflow_parameters.return_value = {
            "COUNTRY": [{"value": "USA", "label": "USA"}],
            "INDICATOR": [{"value": "OTHER", "label": "Other"}],
            "FREQUENCY": [{"value": "A", "label": "Annual"}],
        }
        meta.get_available_constraints.return_value = {
            "key_values": [{"id": "COUNTRY", "values": ["USA"]}]
        }
        out = await indicator_choices(meta, symbol="DF1::NOMATCH", country="true")
        assert out[0]["value"] == "*"

    @pytest.mark.asyncio
    async def test_codelist_labels_used_when_param_labels_missing(self):
        """Codelist labels back-fill when the param-list label is unset."""
        meta = self._meta()
        meta.get_dataflow_parameters.return_value = {
            "COUNTRY": [],
            "INDICATOR": [],
            "FREQUENCY": [],
        }
        meta._codelist_cache = {"CL_X": {"USA": "United States of America"}}
        meta.get_available_constraints.return_value = {
            "key_values": [{"id": "COUNTRY", "values": ["USA"]}]
        }
        out = await indicator_choices(meta, symbol="DF1::GDP", country="true")
        labels = [row["label"] for row in out[1:]]
        assert "United States of America" in labels

    @pytest.mark.asyncio
    async def test_symbol_with_empty_dataflow_id_returns_empty(self):
        """A ``::IND`` style symbol with an empty dataflow id falls through to ``[]``."""
        meta = self._meta()
        out = await indicator_choices(meta, symbol="::GDP", country="true")
        assert out == []

    @pytest.mark.asyncio
    async def test_dimension_values_freq_extra_reassigns_frequency(self):
        """``FREQ`` in ``dimension_values`` overrides the ``frequency`` argument."""
        meta = self._meta()
        meta.get_dataflow_parameters.return_value = {
            "COUNTRY": [],
            "INDICATOR": [],
            "FREQUENCY": [],
        }
        meta.get_available_constraints.return_value = {
            "key_values": [{"id": "FREQUENCY", "values": ["A"]}]
        }
        out = await indicator_choices(
            meta,
            symbol="DF1::GDP",
            frequency="true",
            dimension_values=["FREQ:A"],
        )
        assert out == []

    @pytest.mark.asyncio
    async def test_dimension_values_transform_extra_reassigns_transform(self):
        """``UNIT_MEASURE`` in ``dimension_values`` overrides the ``transform`` arg."""
        meta = self._meta(
            dim_order=("COUNTRY", "INDICATOR", "FREQUENCY", "UNIT_MEASURE")
        )
        meta.get_dataflow_parameters.return_value = {
            "COUNTRY": [],
            "INDICATOR": [],
            "FREQUENCY": [],
            "UNIT_MEASURE": [],
        }
        meta.get_available_constraints.return_value = {
            "key_values": [{"id": "UNIT_MEASURE", "values": ["USD"]}]
        }
        with patch(
            "openbb_imf.utils.helpers.detect_transform_dimension",
            return_value=(None, "UNIT_MEASURE", None, None),
        ):
            out = await indicator_choices(
                meta,
                symbol="DF1::GDP",
                country="USA",
                frequency="A",
                transform="true",
                dimension_values=["UNIT_MEASURE:USD"],
            )
        assert out == []

    @pytest.mark.asyncio
    async def test_transform_dim_branch_in_build_key(self):
        """The ``transform_dim`` branch in ``build_key_with_indicator`` fires when the dim is in ``dim_order``."""
        meta = self._meta(
            dim_order=("COUNTRY", "INDICATOR", "FREQUENCY", "TYPE_OF_TRANSFORMATION")
        )
        meta.get_dataflow_parameters.return_value = {
            "COUNTRY": [{"value": "USA", "label": "USA"}],
            "INDICATOR": [{"value": "GDP", "label": "GDP"}],
            "FREQUENCY": [{"value": "A", "label": "Annual"}],
            "TYPE_OF_TRANSFORMATION": [{"value": "PCT", "label": "Pct"}],
        }
        meta.get_available_constraints.return_value = {
            "key_values": [{"id": "COUNTRY", "values": ["USA"]}]
        }
        with patch(
            "openbb_imf.utils.helpers.detect_transform_dimension",
            return_value=("TYPE_OF_TRANSFORMATION", None, None, None),
        ):
            out = await indicator_choices(
                meta,
                symbol="DF1::GDP",
                country="true",
                transform="PCT",
            )
        assert out[0]["value"] == "*"

    @pytest.mark.asyncio
    async def test_codelist_id_unresolved_falls_back_to_value_as_label(self):
        """When neither param-label nor codelist-label resolves, label = value."""
        meta = self._meta()
        meta.get_dataflow_parameters.return_value = {
            "COUNTRY": [],
            "INDICATOR": [],
            "FREQUENCY": [],
        }
        meta._codelist_cache = {}
        meta._resolve_codelist_id.return_value = None
        meta.get_available_constraints.return_value = {
            "key_values": [{"id": "COUNTRY", "values": ["USA"]}]
        }
        out = await indicator_choices(meta, symbol="DF1::GDP", country="true")
        labels = [row["label"] for row in out[1:]]
        assert "USA" in labels


class TestBopCpiCountryChoices:
    """Tests for ``list_bop_country_choices`` and ``list_cpi_country_choices``."""

    @pytest.mark.asyncio
    async def test_list_bop_country_choices_sorts_and_skips_empty(self):
        """Skips entries missing ``value``, sorts the rest by label, upper-cases codes."""
        meta = MagicMock()
        meta.get_dataflow_parameters.return_value = {
            "COUNTRY": [
                {"value": "usa", "label": "United States"},
                {"value": "", "label": "Skipped"},
                {"label": "No Value"},
                {"value": "alb", "label": "Albania"},
            ]
        }
        choices = await list_bop_country_choices(meta)
        meta.get_dataflow_parameters.assert_called_once_with("BOP")
        assert choices == [
            {"label": "Albania", "value": "ALB"},
            {"label": "United States", "value": "USA"},
        ]

    @pytest.mark.asyncio
    async def test_list_bop_country_choices_falls_back_to_code_label(self):
        """Entries without a label fall back to the code as the label."""
        meta = MagicMock()
        meta.get_dataflow_parameters.return_value = {"COUNTRY": [{"value": "USA"}]}
        assert await list_bop_country_choices(meta) == [
            {"label": "USA", "value": "USA"}
        ]

    @pytest.mark.asyncio
    async def test_list_cpi_country_choices_sorts_and_skips_empty(self):
        """``list_cpi_country_choices`` mirrors the BOP behaviour against the CPI dataflow."""
        meta = MagicMock()
        meta.get_dataflow_parameters.return_value = {
            "COUNTRY": [
                {"value": "fra", "label": "France"},
                {"value": "", "label": "Skipped"},
                {"label": "No Value"},
                {"value": "deu", "label": "Germany"},
            ]
        }
        choices = await list_cpi_country_choices(meta)
        meta.get_dataflow_parameters.assert_called_once_with("CPI")
        assert choices == [
            {"label": "France", "value": "FRA"},
            {"label": "Germany", "value": "DEU"},
        ]

    @pytest.mark.asyncio
    async def test_list_cpi_country_choices_falls_back_to_code_label(self):
        """CPI entries without a label fall back to the code."""
        meta = MagicMock()
        meta.get_dataflow_parameters.return_value = {"COUNTRY": [{"value": "JPN"}]}
        assert await list_cpi_country_choices(meta) == [
            {"label": "JPN", "value": "JPN"}
        ]


class TestRewriteWidgetIds:
    """Tests for ``_rewrite_widget_ids`` and the apps.json fallback path."""

    def test_rewrites_mapped_ids_and_preserves_unmapped(self):
        """Only IDs in the fallback map are rewritten; everything else passes through."""
        apps = [
            {
                "tabs": {
                    "a": {
                        "layout": [
                            {"i": "economy_cpi_imf_obb"},
                            {"i": "imf_presentation_table_custom_obb"},
                        ]
                    },
                    "b": {
                        "layout": [
                            {"i": "economy_balance_of_payments_imf_obb"},
                        ]
                    },
                }
            }
        ]
        out = _rewrite_widget_ids(apps)
        layout_a = [w["i"] for w in out[0]["tabs"]["a"]["layout"]]
        layout_b = [w["i"] for w in out[0]["tabs"]["b"]["layout"]]
        assert layout_a == [
            _APPS_WIDGET_ID_FALLBACK_MAP["economy_cpi_imf_obb"],
            "imf_presentation_table_custom_obb",
        ]
        assert layout_b == [
            _APPS_WIDGET_ID_FALLBACK_MAP["economy_balance_of_payments_imf_obb"]
        ]

    def test_tolerates_missing_tabs_and_layout(self):
        """Apps without ``tabs`` or with ``layout=None`` are skipped gracefully."""
        apps = [
            {},
            {"tabs": {}},
            {"tabs": {"x": {}}},
            {"tabs": {"x": {"layout": None}}},
            {"tabs": {"x": {"layout": [{"i": "economy_cpi_imf_obb"}]}}},
        ]
        out = _rewrite_widget_ids(apps)
        rewritten = out[-1]["tabs"]["x"]["layout"][0]["i"]
        assert rewritten == _APPS_WIDGET_ID_FALLBACK_MAP["economy_cpi_imf_obb"]

    @pytest.mark.asyncio
    async def test_get_imf_apps_json_rewrites_when_economy_absent(
        self, tmp_path, monkeypatch
    ):
        """When ``ECONOMY_INSTALLED`` is False the served apps.json has rewritten IDs."""
        from openbb_imf import imf_router as router_module

        apps_path = tmp_path / "apps.json"
        apps_path.write_text(
            '[{"tabs": {"cpi": {"layout": [{"i": "economy_cpi_imf_obb"}]}}}]',
            encoding="utf-8",
        )
        monkeypatch.setattr(router_module, "__file__", str(tmp_path / "imf_router.py"))
        monkeypatch.setattr(router_module, "ECONOMY_INSTALLED", False)

        apps = await get_imf_apps_json()
        assert (
            apps[0]["tabs"]["cpi"]["layout"][0]["i"]
            == (_APPS_WIDGET_ID_FALLBACK_MAP["economy_cpi_imf_obb"])
        )


def _load_standalone_router_module():
    """Re-execute ``imf_router`` with ``ECONOMY_INSTALLED`` forced to False.

    Loaded under a private module name so the global ``openbb_imf.imf_router``
    used elsewhere in the suite is untouched. ``Router.command`` is replaced
    during load with a passthrough decorator so the fallback endpoints bind
    without requiring the IMF-prefixed models to exist in the live provider
    registry or FastAPI's response-model machinery.
    """
    import importlib.util
    from pathlib import Path

    import openbb_imf
    from openbb_core.app.router import Router

    spec = importlib.util.spec_from_file_location(
        "openbb_imf_imf_router_standalone",
        Path(openbb_imf.__file__).parent / "imf_router.py",
    )
    module = importlib.util.module_from_spec(spec)
    original_economy = openbb_imf.ECONOMY_INSTALLED
    original_command = Router.command
    openbb_imf.ECONOMY_INSTALLED = False

    def _passthrough_command(self, func=None, **_kwargs):
        """Bind ``func`` to the caller without touching the underlying FastAPI router."""
        if func is None:
            return lambda f: _passthrough_command(self, f, **_kwargs)
        return func

    Router.command = _passthrough_command  # type: ignore[assignment]
    try:
        spec.loader.exec_module(module)
    finally:
        openbb_imf.ECONOMY_INSTALLED = original_economy
        Router.command = original_command  # type: ignore[assignment]
    return module


class TestStandaloneFallbackEndpoints:
    """Tests for the nine endpoints registered only when ``openbb-economy`` is absent."""

    _STANDALONE_NAMES = (
        "available_indicators",
        "indicators",
        "cpi",
        "balance_of_payments",
        "direction_of_trade",
        "port_info",
        "port_volume",
        "chokepoint_info",
        "chokepoint_volume",
    )

    def test_standalone_module_binds_all_fallback_endpoint_names(self):
        """All nine fallback endpoint names exist as module attributes after reload."""
        module = _load_standalone_router_module()
        for name in self._STANDALONE_NAMES:
            assert callable(getattr(module, name, None)), f"missing {name}"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("endpoint_name", _STANDALONE_NAMES)
    async def test_standalone_endpoint_body_delegates_to_from_query(
        self, endpoint_name
    ):
        """Each fallback endpoint body calls ``OBBject.from_query(OBBQuery(**locals()))``."""
        module = _load_standalone_router_module()
        fn = getattr(module, endpoint_name)

        sentinel = SimpleNamespace(result=[])
        with (
            patch.object(module, "OBBQuery", new=MagicMock()),
            patch.object(
                module.OBBject,
                "from_query",
                new=AsyncMock(return_value=sentinel),
            ) as mock_from_query,
        ):
            out = await fn(
                cc=MagicMock(),
                provider_choices=MagicMock(),
                standard_params=MagicMock(),
                extra_params=MagicMock(),
            )
        assert out is sentinel
        mock_from_query.assert_awaited_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
