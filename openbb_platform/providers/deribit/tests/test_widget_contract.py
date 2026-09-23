"""Tests for the contract the Workspace widgets rely on."""

import importlib
from functools import cache
from typing import Literal, get_args, get_origin

import pytest
from pydantic import ValidationError

from openbb_deribit import deribit_provider
from openbb_deribit.deribit_router import router
from openbb_deribit.models.order_book import DeribitOrderBookQueryParams
from openbb_deribit.models.settlements import DeribitSettlementsQueryParams
from openbb_deribit.models.trades import DeribitTradesQueryParams
from openbb_deribit.utils.constants import (
    MAX_SETTLEMENT_COUNT,
    MAX_TRADE_COUNT,
    ORDER_BOOK_DEPTHS,
)

MODEL_DATA = {
    "DeribitAnnouncements": ("announcements", "DeribitAnnouncementsData"),
    "DeribitAprHistory": ("apr_history", "DeribitAprHistoryData"),
    "DeribitBlockRfqTrades": ("block_rfq_trades", "DeribitBlockRfqTradesData"),
    "DeribitBookSummary": ("book_summary", "DeribitBookSummaryData"),
    "DeribitCombos": ("combos", "DeribitCombosData"),
    "DeribitCurrencies": ("currencies", "DeribitCurrenciesData"),
    "DeribitDeliveryPrices": ("delivery_prices", "DeribitDeliveryPricesData"),
    "DeribitExpirations": ("expirations", "DeribitExpirationsData"),
    "DeribitFundingChart": ("funding_chart", "DeribitFundingChartData"),
    "DeribitFundingRateHistory": (
        "funding_rate_history",
        "DeribitFundingRateHistoryData",
    ),
    "DeribitFuturesCurve": ("futures_curve", "DeribitFuturesCurveData"),
    "DeribitFuturesHistorical": (
        "futures_historical",
        "DeribitFuturesHistoricalData",
    ),
    "DeribitFuturesInfo": ("futures_info", "DeribitFuturesInfoData"),
    "DeribitFuturesInstruments": (
        "futures_instruments",
        "DeribitFuturesInstrumentData",
    ),
    "DeribitHistoricalVolatility": (
        "historical_volatility",
        "DeribitHistoricalVolatilityData",
    ),
    "DeribitIndexHistorical": ("index_historical", "DeribitIndexHistoricalData"),
    "DeribitIndexPrice": ("index_price", "DeribitIndexPriceData"),
    "DeribitInstruments": ("instruments", "DeribitInstrumentsData"),
    "DeribitMarkPriceHistory": (
        "mark_price_history",
        "DeribitMarkPriceHistoryData",
    ),
    "DeribitOptionsChains": ("options_chains", "DeribitOptionsChainsData"),
    "DeribitOrderBook": ("order_book", "DeribitOrderBookData"),
    "DeribitSettlements": ("settlements", "DeribitSettlementsData"),
    "DeribitTicker": ("ticker", "DeribitTickerData"),
    "DeribitTradeVolumes": ("trade_volumes", "DeribitTradeVolumesData"),
    "DeribitTrades": ("trades", "DeribitTradesData"),
    "DeribitVolatilityIndex": ("volatility_index", "DeribitVolatilityIndexData"),
}


def _widgets():
    """Yield every model-backed route with its widget config."""
    for sub in router.routers.values():
        for route in sub.api_router.routes:
            extra = getattr(route, "openapi_extra", None) or {}
            config = extra.get("widget_config") or {}

            if extra.get("model") and not config.get("exclude"):
                yield route.path, extra["model"], config


def _data_model(model: str):
    """Return the data model a widget returns."""
    module_name, class_name = MODEL_DATA[model]

    return getattr(
        importlib.import_module(f"openbb_deribit.models.{module_name}"), class_name
    )


def _literal_fields(params):
    """Yield each field of a query model whose type is a Literal, with its values."""
    for name, field in params.model_fields.items():
        annotation = field.annotation
        options = [annotation, *get_args(annotation)]

        for option in options:
            if get_origin(option) is Literal:
                yield name, get_args(option)
                break


class TestQueryStringChoices:
    """Choice parameters must survive arriving as text.

    A widget sends every parameter in the query string, so a choice typed as
    ``Literal[20]`` is handed the string ``"20"`` and rejected by FastAPI before
    the model is ever reached. Every choice must therefore be spelled as text.
    """

    @pytest.mark.parametrize(
        "name", sorted(deribit_provider.fetcher_dict), ids=lambda n: n
    )
    def test_every_choice_is_text(self, name):
        """No query choice is typed as a number."""
        params = deribit_provider.fetcher_dict[name].query_params_type

        for field, values in _literal_fields(params):
            numeric = [v for v in values if not isinstance(v, str)]

            assert not numeric, (
                f"{params.__name__}.{field} offers non-text choices {numeric};"
                " a query string cannot carry them"
            )

    @pytest.mark.parametrize("depth", ORDER_BOOK_DEPTHS)
    def test_depth_accepts_its_own_choices(self, depth):
        """Every advertised depth is accepted exactly as advertised."""
        query = DeribitOrderBookQueryParams(symbol="BTC-PERPETUAL", depth=depth)

        assert query.depth == depth

    def test_depth_accepts_a_number_from_python(self):
        """A Python caller passing a number is still understood."""
        query = DeribitOrderBookQueryParams(symbol="BTC-PERPETUAL", depth=20)

        assert query.depth == "20"

    def test_depth_rejects_an_unlisted_value(self):
        """A depth the exchange does not offer is refused."""
        with pytest.raises(ValidationError):
            DeribitOrderBookQueryParams(symbol="BTC-PERPETUAL", depth="7")


class TestExchangeLimits:
    """Limits are bounded to what the exchange accepts, not left to fail at it."""

    def test_trades_ceiling(self):
        """One over the trade ceiling is refused here, not by Deribit."""
        assert DeribitTradesQueryParams(limit=MAX_TRADE_COUNT).limit == MAX_TRADE_COUNT

        with pytest.raises(ValidationError):
            DeribitTradesQueryParams(limit=MAX_TRADE_COUNT + 1)

    def test_settlements_ceiling(self):
        """One over the settlement ceiling is refused here."""
        assert (
            DeribitSettlementsQueryParams(limit=MAX_SETTLEMENT_COUNT).limit
            == MAX_SETTLEMENT_COUNT
        )

        with pytest.raises(ValidationError):
            DeribitSettlementsQueryParams(limit=MAX_SETTLEMENT_COUNT + 1)

    def test_limits_have_a_floor(self):
        """Asking for nothing is refused."""
        with pytest.raises(ValidationError):
            DeribitTradesQueryParams(limit=0)

    def test_trade_kinds_exclude_what_the_exchange_refuses(self):
        """The by-currency path refuses spot and the wildcard, so neither is offered."""
        kinds = dict(_literal_fields(DeribitTradesQueryParams))["kind"]

        assert "spot" not in kinds
        assert "any" not in kinds
        assert DeribitTradesQueryParams().kind in kinds


def _widget_config(model, field) -> dict:
    """Return the widget config a model declares for one field."""
    declared = model.model_fields[field].json_schema_extra or {}

    return declared.get("x-widget_config", {})


class TestModelColumns:
    """Every field a model returns carries its own column definition.

    The platform generates a column for every field of the response schema but
    never sets ``chartDataType``. A field that does not declare one is charted
    by default, which is how identifiers ended up plotted against prices.
    """

    @pytest.mark.parametrize("model", sorted(MODEL_DATA), ids=lambda m: m)
    def test_every_field_declares_a_chart_disposition(self, model):
        """No field is left for the grid to guess at."""
        data = _data_model(model)
        undeclared = [
            field
            for field in data.model_fields
            if "chartDataType" not in _widget_config(data, field)
        ]

        assert not undeclared, f"{model} leaves {undeclared} undeclared"

    @pytest.mark.parametrize("model", sorted(MODEL_DATA), ids=lambda m: m)
    def test_dispositions_are_valid(self, model):
        """A disposition is one the grid understands."""
        data = _data_model(model)

        for field in data.model_fields:
            disposition = _widget_config(data, field).get("chartDataType")

            assert disposition in {"series", "category", "excluded"}, (
                f"{model}.{field} declares {disposition!r}"
            )

    @pytest.mark.parametrize("model", sorted(MODEL_DATA), ids=lambda m: m)
    def test_at_most_one_series_and_one_axis(self, model):
        """A model nominates a single series against a single axis."""
        data = _data_model(model)
        counts = {"series": [], "category": []}

        for field in data.model_fields:
            disposition = _widget_config(data, field).get("chartDataType")

            if disposition in counts:
                counts[disposition].append(field)

        assert len(counts["series"]) <= 1, f"{model} plots {counts['series']}"
        assert len(counts["category"]) <= 1, f"{model} axes {counts['category']}"

        if counts["series"]:
            assert counts["category"], f"{model} plots a series with no axis"


class TestChartedWidgets:
    """A widget that enables a chart has a model that names what to plot."""

    def test_an_enabled_chart_has_a_series(self):
        """No widget turns on a chart its model cannot fill."""
        for path, model, config in _widgets():
            table = (config.get("data") or {}).get("table") or {}

            if not (table.get("chartView") or {}).get("enabled"):
                continue

            data = _data_model(model)
            series = [
                field
                for field in data.model_fields
                if _widget_config(data, field).get("chartDataType") == "series"
            ]

            assert series, f"{path} charts but {model} names no series"

    def test_a_router_defines_columns_only_where_the_model_cannot(self):
        """Columns live on the model wherever the platform can read them off it.

        A model publishing one object of columns rather than a row per record
        gives the grid nothing to infer from, so that widget writes them out.
        Any other router doing so would be duplicating what the schema already
        says, and the two copies would drift.
        """
        for route, model, config in _widgets():
            table = (config.get("data") or {}).get("table") or {}

            if "columnsDefs" not in table:
                continue

            assert _is_columnar(model), (
                f"{route} writes its columns out, but {model} publishes a row"
                " per record, so the grid already reads them off its schema"
            )

    def test_a_columnar_model_has_its_columns_written_out(self):
        """A model the grid cannot read columns off names them in the router."""
        for route, model, config in _widgets():
            if not _is_columnar(model):
                continue

            table = (config.get("data") or {}).get("table") or {}

            assert table.get("columnsDefs"), (
                f"{model} publishes columns rather than rows, so {route} must"
                " name them; the grid can infer nothing from its schema"
            )


SYMBOL_PARAMS = {"symbol", "index_name", "combo_id"}


@cache
def _served_widgets() -> dict:
    """Return the widget catalogue this install publishes.

    Reading the catalogue rather than the routes covers the analysis endpoints,
    which carry no model and are published under a different suffix, and honours
    every widget the routers exclude.
    """
    from openbb_core.api.rest_api import app
    from openbb_platform_api.utils.widgets import build_json

    return build_json(app.openapi(), [])


def _is_columnar(model: str) -> bool:
    """Return whether a model publishes columns rather than a row per record."""
    from typing import get_origin

    fields = _data_model(model).model_fields.values()

    return all(get_origin(field.annotation) is list for field in fields)


def _served_widget_ids() -> set:
    """Return the identifier of every widget this install publishes."""
    return set(_served_widgets())


def _choice_routes() -> set:
    """Return the path of every choice feed this install serves."""
    return {
        route.path
        for sub in router.routers.values()
        for route in sub.api_router.routes
        if route.path.endswith("_choices")
    }


class TestSymbolChoices:
    """Nobody can guess a Deribit instrument name, so every one is offered."""

    @pytest.mark.parametrize(
        "name", sorted(deribit_provider.fetcher_dict), ids=lambda n: n
    )
    def test_symbol_parameters_offer_choices(self, name):
        """A symbol-like parameter names an endpoint to read its choices from."""
        query = deribit_provider.fetcher_dict[name].query_params_type
        extra = getattr(query, "__json_schema_extra__", {})

        for param in SYMBOL_PARAMS & set(query.model_fields):
            config = (extra.get(param) or {}).get("x-widget_config", {})

            assert config.get("type") == "endpoint", (
                f"{query.__name__}.{param} offers no dropdown"
            )
            assert config.get("optionsEndpoint"), (
                f"{query.__name__}.{param} names no options endpoint"
            )

    @pytest.mark.parametrize(
        "name", sorted(deribit_provider.fetcher_dict), ids=lambda n: n
    )
    def test_options_endpoints_are_served(self, name):
        """Every dropdown points at a route this extension actually serves."""
        query = deribit_provider.fetcher_dict[name].query_params_type
        extra = getattr(query, "__json_schema_extra__", {})
        served = _choice_routes()

        for param in SYMBOL_PARAMS & set(query.model_fields):
            endpoint = (
                (extra.get(param) or {})
                .get("x-widget_config", {})
                .get("optionsEndpoint", "")
            )
            path = endpoint.replace("/api/v1/deribit", "")

            assert path in served, (
                f"{query.__name__}.{param} points at {path}, which is not served"
            )


class TestParameterGroups:
    """A group binds one parameter across the widgets that share it."""

    @pytest.fixture(scope="class")
    def apps(self):
        """Return the dashboard as it is served."""
        import asyncio

        from openbb_deribit.deribit_router import deribit_apps

        return asyncio.run(deribit_apps())

    def test_groups_bind_served_widgets(self, apps):
        """Every widget a group names is one this install serves."""
        served = _served_widget_ids()

        for app in apps:
            for group in app["groups"]:
                unknown = [w for w in group["widgetIds"] if w not in served]

                assert not unknown, f"group {group['name']} names {unknown}"

    def test_groups_bind_a_parameter_each_widget_has(self, apps):
        """A group never binds a parameter one of its widgets lacks."""
        widgets = _served_widgets()

        for app in apps:
            for group in app["groups"]:
                for widget_id in group["widgetIds"]:
                    offered = {
                        param.get("paramName")
                        for param in widgets[widget_id].get("params", [])
                    }

                    assert group["paramName"] in offered, (
                        f"group {group['name']} binds {group['paramName']},"
                        f" which {widget_id} has no parameter for"
                    )

    def test_widgets_only_name_defined_groups(self, apps):
        """A widget never joins a group the app does not define."""
        for app in apps:
            defined = {group["name"] for group in app["groups"]}

            for tab in app["tabs"].values():
                for widget in tab["layout"]:
                    unknown = [g for g in widget.get("groups", []) if g not in defined]

                    assert not unknown, f"{widget['i']} names {unknown}"

    def test_group_membership_is_declared_on_both_sides(self, apps):
        """A widget in a group's list says so, and the reverse."""
        for app in apps:
            for group in app["groups"]:
                members = set(group["widgetIds"])
                claimed = {
                    widget["i"]
                    for tab in app["tabs"].values()
                    for widget in tab["layout"]
                    if group["name"] in widget.get("groups", [])
                }

                assert claimed == members, (
                    f"group {group['name']}: listed {sorted(members)}"
                    f" but claimed by {sorted(claimed)}"
                )


class TestGroupEndpoints:
    """An endpoint-backed group binds one options endpoint, not several.

    The Workspace reads a group's choices from a single endpoint. Binding
    widgets whose dropdowns are fed by different endpoints leaves the group
    unable to resolve a value, and the widgets are called with no parameter
    at all.
    """

    @pytest.fixture(scope="class")
    def bound(self):
        """Return each group with the options endpoints its widgets declare."""
        import asyncio

        from openbb_deribit.deribit_router import deribit_apps

        widgets = _served_widgets()
        groups = []

        for entry in asyncio.run(deribit_apps()):
            for group in entry["groups"]:
                endpoints = {
                    param.get("optionsEndpoint")
                    for widget_id in group["widgetIds"]
                    for param in widgets[widget_id].get("params", [])
                    if param.get("paramName") == group["paramName"]
                }
                groups.append((group, endpoints))

        return groups

    def test_each_endpoint_group_binds_one_endpoint(self, bound):
        """No group mixes widgets whose choices come from different feeds."""
        for group, endpoints in bound:
            if group["type"] != "endpointParam":
                continue

            assert len(endpoints) == 1, (
                f"group {group['name']} binds {len(endpoints)} endpoints:"
                f" {sorted(map(str, endpoints))}"
            )

    def test_endpoint_groups_actually_have_an_endpoint(self, bound):
        """A group declared endpoint-backed has widgets that offer choices."""
        for group, endpoints in bound:
            if group["type"] != "endpointParam":
                continue

            assert endpoints != {None}, (
                f"group {group['name']} is endpointParam but offers no choices"
            )

    def test_plain_groups_are_not_endpoint_backed(self, bound):
        """A group bound as a plain parameter has no dropdown to reconcile."""
        for group, endpoints in bound:
            if group["type"] == "endpointParam":
                continue

            assert endpoints <= {None}, (
                f"group {group['name']} is a plain param but its widgets offer"
                f" {sorted(map(str, endpoints - {None}))}"
            )

    def test_a_group_starts_somewhere_or_its_widgets_do_not_need_it(self, bound):
        """A group names a starting value unless its widgets can do without one.

        A widget bound to a group with nothing selected must still have
        something to show. Most do that by starting on a named value; one whose
        parameter is optional does it by deciding for itself what to show, and
        an empty string is neither -- it is a value that means nothing.
        """
        widgets = _served_widgets()

        for group, _endpoints in bound:
            if group.get("defaultValue"):
                continue

            assert "defaultValue" not in group, (
                f"group {group['name']} starts on {group['defaultValue']!r},"
                " which is a placeholder rather than a value"
            )

            for widget_id in group["widgetIds"]:
                param = next(
                    item
                    for item in widgets[widget_id]["params"]
                    if item["paramName"] == group["paramName"]
                )

                assert param.get("optional"), (
                    f"group {group['name']} names no starting value and"
                    f" {widget_id} requires {group['paramName']}"
                )


RATE_FIELDS = {
    "apr",
    "ask_iv",
    "bid_iv",
    "change_percent",
    "current_funding",
    "current_interest",
    "funding_8h",
    "implied_volatility",
    "interest_1h",
    "interest_8h",
    "interest_rate",
    "iv",
    "volatility",
}

NOT_A_RATE = {"interest_value"}


class TestRateFormatting:
    """A rate is shown as a percentage, at the scale the exchange publishes it.

    The exchange sends funding as a decimal fraction — 0.00011627 is 0.0116%.
    A field left unmarked renders that fraction raw, which reads as a stray
    decimal rather than a rate.
    """

    @pytest.mark.parametrize("model", sorted(MODEL_DATA), ids=lambda m: m)
    def test_rates_are_marked_as_percentages(self, model):
        """Every rate-like field declares itself a percentage."""
        data = _data_model(model)

        for field in set(data.model_fields) & RATE_FIELDS:
            extra = data.model_fields[field].json_schema_extra or {}

            assert extra.get("x-unit_measurement") == "percent", (
                f"{model}.{field} is a rate but is not marked a percentage,"
                " so it renders as a bare decimal"
            )

    @pytest.mark.parametrize("model", sorted(MODEL_DATA), ids=lambda m: m)
    def test_rates_are_stored_in_percent_units(self, model):
        """A rate is stored as the number that precedes the percent sign.

        A chart plots the stored value and never applies the grid's formatter,
        so asking the grid to scale a fraction leaves the axis reading 0.44
        where the table reads 44 %.
        """
        data = _data_model(model)

        for field in set(data.model_fields) & RATE_FIELDS:
            extra = data.model_fields[field].json_schema_extra or {}

            assert "x-frontend_multiply" not in extra, (
                f"{model}.{field} asks the grid to scale it, which a chart axis"
                " does not do"
            )

    @pytest.mark.parametrize("model", sorted(MODEL_DATA), ids=lambda m: m)
    def test_values_that_are_not_rates_stay_plain(self, model):
        """A number that is not a rate is never dressed up as one."""
        data = _data_model(model)

        for field in set(data.model_fields) & NOT_A_RATE:
            extra = data.model_fields[field].json_schema_extra or {}

            assert extra.get("x-unit_measurement") != "percent", (
                f"{model}.{field} is not a rate"
            )

    def test_the_same_quantity_is_scaled_the_same_way(self):
        """A field carried by several models is marked identically in each."""
        seen: dict = {}

        for model in MODEL_DATA:
            data = _data_model(model)

            for field in set(data.model_fields) & RATE_FIELDS:
                extra = data.model_fields[field].json_schema_extra or {}
                mark = (
                    extra.get("x-unit_measurement"),
                    extra.get("x-frontend_multiply"),
                )
                seen.setdefault(field, {}).setdefault(mark, []).append(model)

        for field, marks in seen.items():
            assert len(marks) == 1, (
                f"{field} is marked {len(marks)} different ways: "
                + "; ".join(f"{mark} in {models}" for mark, models in marks.items())
            )


class TestColumnDefinitions:
    """A grid column names a field the endpoint actually returns.

    A column pointing at a field nothing emits renders as an empty strip the
    reader cannot explain, and a field with no column is shown with whatever
    defaults the grid guesses.
    """

    ANALYSIS = {
        "deribit_options_optimizer_custom_obb": ("optimizer", {}),
        "deribit_options_straddle_custom_obb": ("straddle", {}),
        "deribit_options_strangle_custom_obb": ("strangle", {"moneyness": 4.0}),
        "deribit_options_spreads_custom_obb": ("spreads", {"moneyness": 4.0}),
    }

    @staticmethod
    def _declared(widget_id: str) -> set:
        """Return the fields one widget declares a column for."""
        widget = _served_widgets()[widget_id]
        table = (widget.get("data") or {}).get("table") or {}

        return {column["field"] for column in table.get("columnsDefs") or []}

    @pytest.mark.parametrize("widget_id", sorted(ANALYSIS), ids=lambda w: w)
    def test_every_analysis_column_is_returned(self, widget_id, loaded_chain):
        """No analysis widget declares a column its endpoint never fills."""
        import asyncio

        from openbb_deribit.routers import options

        loaded_chain()
        command, params = self.ANALYSIS[widget_id]
        output = asyncio.run(getattr(options, command)(symbol="BTC", **params))
        emitted: set = set()

        for row in output.results:
            emitted |= set(row)

        declared = self._declared(widget_id)

        assert declared, f"{widget_id} declares no columns"
        assert not declared - emitted, f"{widget_id} declares dead {declared - emitted}"
        assert not emitted - declared, (
            f"{widget_id} returns undeclared {emitted - declared}"
        )

    def test_the_chain_declares_the_fields_it_publishes(self):
        """The chain widget names a column for every field it fills.

        Its model publishes one object of columns rather than a row per
        contract, so the grid cannot infer them from the response schema and
        they are written out instead.
        """
        from openbb_deribit.models.options_chains import DeribitOptionsChainsData

        declared = self._declared("deribit_options_chains_deribit_obb")
        published = {
            name
            for name, field in DeribitOptionsChainsData.model_fields.items()
            if not ((field.json_schema_extra or {}).get("x-widget_config") or {}).get(
                "hide"
            )
        }

        assert declared == published, (
            f"declared but not published: {sorted(declared - published)};"
            f" published but not declared: {sorted(published - declared)}"
        )

    def test_every_table_widget_has_columns(self):
        """No table this extension serves is left for the grid to guess at."""
        bare = [
            widget_id
            for widget_id, widget in _served_widgets().items()
            if widget_id.startswith("deribit_")
            and widget.get("type") == "table"
            and not ((widget.get("data") or {}).get("table") or {}).get("columnsDefs")
        ]

        assert not bare, f"{bare} serve a table with no columns"


class TestMultiSelectCurrencies:
    """A multi-select sends its choices joined, so the model must accept them.

    A parameter typed as a bare ``Literal`` renders as a multi-select but
    rejects the comma-joined value the moment a second choice is picked, which
    the reader sees as the widget breaking on its own dropdown.
    """

    MULTI = (
        "DeribitHistoricalVolatility",
        "DeribitVolatilityIndex",
    )

    @pytest.mark.parametrize("name", MULTI, ids=lambda n: n)
    def test_several_currencies_are_accepted(self, name):
        """Picking a second currency is understood, not refused."""
        query = deribit_provider.fetcher_dict[name].query_params_type

        assert query(currency="BTC,ETH").currency == "BTC,ETH"

    @pytest.mark.parametrize("name", MULTI, ids=lambda n: n)
    def test_a_currency_is_read_however_it_is_typed(self, name):
        """Case and spacing are the reader's, not the exchange's."""
        query = deribit_provider.fetcher_dict[name].query_params_type

        assert query(currency=" btc , eth ").currency == "BTC,ETH"

    @pytest.mark.parametrize("name", MULTI, ids=lambda n: n)
    def test_an_unlisted_currency_names_what_is_listed(self, name):
        """A currency the exchange does not publish is refused readably."""
        query = deribit_provider.fetcher_dict[name].query_params_type

        with pytest.raises(ValidationError, match=r"no .* for \['DOGE'\]"):
            query(currency="BTC,DOGE")

    def test_every_multi_select_accepts_the_joined_form(self):
        """No parameter offers a multi-select its model cannot parse."""
        broken: list = []

        for name, fetcher in deribit_provider.fetcher_dict.items():
            query = fetcher.query_params_type
            extra = getattr(query, "__json_schema_extra__", {}) or {}

            for param, config in extra.items():
                if not config.get("multiple_items_allowed"):
                    continue

                choices = dict(_literal_fields(query)).get(param)

                if choices and len(choices) > 1:
                    broken.append(f"{name}.{param}")

        assert not broken, (
            f"{broken} render a multi-select but are typed as a fixed choice,"
            " so a second selection is rejected before the model is reached"
        )


PEGGED = {"USDC", "USDT"}

VOLATILITY_MODELS = ("DeribitHistoricalVolatility", "DeribitVolatilityIndex")


class TestVolatilityIsOnlyOfferedWhereItExists:
    """A currency is only offered where the number it produces means something.

    A dollar-pegged token has no volatility against the dollar to read, and the
    exchange computes no volatility index for one at all. Offering either is
    offering a reading of the peg.
    """

    @pytest.mark.parametrize("name", VOLATILITY_MODELS, ids=lambda n: n)
    def test_no_pegged_currency_is_offered(self, name):
        """Neither volatility view offers a dollar-pegged token."""
        query = deribit_provider.fetcher_dict[name].query_params_type
        offered = {
            option["value"]
            for option in query.__json_schema_extra__["currency"]["x-widget_config"][
                "options"
            ]
        }

        assert not offered & PEGGED, f"{name} offers {sorted(offered & PEGGED)}"

    @pytest.mark.parametrize("name", VOLATILITY_MODELS, ids=lambda n: n)
    def test_a_pegged_currency_is_refused(self, name):
        """Asking for one anyway says what the exchange does publish."""
        query = deribit_provider.fetcher_dict[name].query_params_type

        with pytest.raises(ValidationError, match="USDC"):
            query(currency="USDC")

    def test_the_volatility_index_is_only_what_deribit_computes(self):
        """DVOL exists for the two coins the exchange computes it for."""
        from openbb_deribit.utils.constants import VOLATILITY_INDEX_CURRENCIES

        assert VOLATILITY_INDEX_CURRENCIES == ("BTC", "ETH")

    def test_settlement_views_still_take_the_currency_that_settles(self):
        """A stablecoin is a currency contracts settle in, and that is unchanged."""
        from openbb_deribit.utils.constants import CURRENCIES

        query = deribit_provider.fetcher_dict["DeribitSettlements"].query_params_type
        choices = set(dict(_literal_fields(query))["currency"])

        assert choices >= PEGGED
        assert choices <= set(CURRENCIES)

    def test_the_dashboard_does_not_bind_the_two_meanings_together(self):
        """Settlement currency and the asset measured are separate groups.

        They share a parameter name but not a set of values, so one control
        driving both would send a settlement currency to a volatility widget.
        """
        import asyncio

        from openbb_deribit.deribit_router import deribit_apps

        apps = asyncio.run(deribit_apps())
        bound: dict = {}

        for group in apps[0]["groups"]:
            for widget_id in group["widgetIds"]:
                bound[widget_id] = group["name"]

        volatility = {
            bound[widget_id] for widget_id in bound if "volatility" in widget_id
        }
        settlement = {bound["deribit_reference_expirations_deribit_obb"]}

        assert volatility and not volatility & settlement


OPTION_LISTINGS = ("DeribitBookSummary", "DeribitInstruments", "DeribitTrades")


class TestOptionsAreListedByUnderlying:
    """Options belong to the asset they are written on, not the rail they settle on.

    Only BTC and ETH are both. USDC settles options written on seven different
    underlyings, so a listing scoped to it is a mixture rather than a chain,
    and USDT settles none at all.
    """

    @pytest.mark.parametrize("name", OPTION_LISTINGS, ids=lambda n: n)
    def test_a_settlement_rail_cannot_list_options(self, name):
        """Asking for options by a currency that only settles them is refused."""
        query = deribit_provider.fetcher_dict[name].query_params_type

        with pytest.raises(ValidationError, match="it is not an underlying"):
            query(currency="USDC", kind="option")

    @pytest.mark.parametrize("name", OPTION_LISTINGS, ids=lambda n: n)
    def test_the_same_rail_still_lists_what_it_does_carry(self, name):
        """Futures settled in USDC are a real listing and stay reachable."""
        query = deribit_provider.fetcher_dict[name].query_params_type

        assert query(currency="USDC", kind="future").currency == "USDC"

    @pytest.mark.parametrize("name", OPTION_LISTINGS, ids=lambda n: n)
    def test_an_underlying_lists_its_own_options(self, name):
        """BTC is both the rail and the underlying, so it lists options."""
        query = deribit_provider.fetcher_dict[name].query_params_type

        assert query(currency="BTC", kind="option").currency == "BTC"

    @pytest.mark.parametrize("name", OPTION_LISTINGS, ids=lambda n: n)
    def test_naming_the_instrument_bypasses_the_rail(self, name):
        """A named contract is not a listing, so the currency does not apply."""
        query = deribit_provider.fetcher_dict[name].query_params_type

        assert query(symbol="SOL_USDC-23SEP26-124-C", currency="USDC", kind="option")

    def test_no_listing_offers_a_currency_that_lists_nothing(self):
        """USDT and EURR carry no contracts, so no listing offers them."""
        from openbb_deribit.utils.constants import LISTING_CURRENCIES

        allowed = set(LISTING_CURRENCIES) | {"any"}

        for name in (*OPTION_LISTINGS, "DeribitCombos", "DeribitBlockRfqTrades"):
            query = deribit_provider.fetcher_dict[name].query_params_type
            choices = set(dict(_literal_fields(query))["currency"])

            assert choices <= allowed, f"{name} offers {sorted(choices - allowed)}"
