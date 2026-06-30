"""ECB Router.

Self-registering ``openbb_core_extension`` router. The always-on utility
commands below expose the SDMX catalogue (list/search dataflows, topics,
dimension discovery and progressive dimension choices). Model-driven data
commands are appended further down, each guarded so it only registers in the
``obb.ecb.*`` namespace when its "owning" extension (economy / currency /
fixedincome) is not installed.
"""

from typing import Annotated, Any

from fastapi import Query
from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.example import APIEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query as OBBQuery
from openbb_core.app.router import Router
from openbb_core.app.service.system_service import SystemService

from openbb_ecb._installed import (
    CURRENCY_INSTALLED,
    ECONOMY_INSTALLED,
    FIXEDINCOME_INSTALLED,
)
from openbb_ecb.utils.metadata import EcbMetadata, EcbMetadataDependency

router = Router(prefix="", description="ECB provider router.")
api_prefix = SystemService().system_settings.api_settings.prefix


@router.command(
    methods=["GET"],
    widget_config={
        "name": "ECB Dataflows",
        "description": "The catalogue of ECB SDMX dataflows.",
        "type": "table",
        "category": "ECB",
        "subCategory": "Catalogue",
        "source": ["ECB"],
        "gridData": {"w": 30, "h": 15},
    },
    examples=[APIEx(description="List every ECB dataflow.", parameters={})],
)
async def list_dataflows(
    metadata: EcbMetadataDependency,
) -> list[dict[str, Any]]:
    """List all ECB SDMX dataflows in the catalogue."""
    return metadata.list_dataflows()


@router.command(
    methods=["GET"],
    widget_config={
        "name": "ECB Dataflow Search",
        "description": "Search the ECB dataflow catalogue — click a row to explore it.",
        "type": "table",
        "category": "ECB",
        "subCategory": "Catalogue",
        "source": ["ECB"],
        "gridData": {"w": 30, "h": 15},
        "params": [
            {
                "paramName": "query",
                "label": "Query",
                "value": None,
                "description": "Search by id, name, or description (+ AND, | OR)."
                " Empty lists every dataflow.",
                "type": "text",
            },
            {
                "paramName": "dataflow",
                "label": "Dataflow",
                "description": "Selected dataflow (set by clicking a result row).",
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/ecb/list_dataflows",
                "style": {"popupWidth": 600},
            },
        ],
        "data": {
            "table": {
                "columnsDefs": [
                    {
                        "field": "value",
                        "headerName": "Dataflow",
                        "renderFn": "cellOnClick",
                        "renderFnParams": {
                            "actionType": "groupBy",
                            "groupByParamName": "dataflow",
                        },
                    },
                ],
            },
        },
    },
    examples=[
        APIEx(description="List every ECB dataflow.", parameters={}),
        APIEx(
            description="Search dataflows by keyword.",
            parameters={"query": "interest rate"},
        ),
    ],
)
async def search_dataflows(
    metadata: EcbMetadataDependency,
    query: Annotated[
        str | None,
        Query(description="Search dataflows by id/name/description (+ AND, | OR)."),
    ] = None,
    dataflow: Annotated[
        str | None, Query(description="Selected dataflow (set by clicking a row).")
    ] = None,
) -> list[dict[str, Any]]:
    """Search the ECB dataflow catalogue; an empty query lists every dataflow."""
    return metadata.search_dataflows(query or "")


@router.command(
    methods=["GET"],
    widget_config={"exclude": True},
    examples=[APIEx(description="List ECB topics for dropdowns.", parameters={})],
)
async def list_topics(
    metadata: EcbMetadataDependency,
) -> list[dict[str, Any]]:
    """Return [{label, value, count}] for every ECB topic that has dataflows."""
    return metadata.list_topics()


@router.command(
    methods=["GET"],
    widget_config={
        "name": "ECB Topic Dataflows",
        "description": "The dataflows grouped under an ECB topic.",
        "type": "table",
        "category": "ECB",
        "subCategory": "Catalogue",
        "source": ["ECB"],
        "gridData": {"w": 20, "h": 12},
        "params": [
            {
                "paramName": "topic_id",
                "label": "Topic",
                "value": "07",
                "description": "The ECB topic.",
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/ecb/list_topics",
            }
        ],
    },
    examples=[
        APIEx(
            description="List the dataflows under a topic.",
            parameters={"topic_id": "07"},
        )
    ],
)
async def topic_dataflows(
    metadata: EcbMetadataDependency,
    topic_id: Annotated[str, Query(description="The topic (category) id.")],
) -> list[dict[str, Any]]:
    """Return the dataflows categorised under a topic, as table rows."""
    ids = set(metadata.get_topic_dataflows(topic_id))
    return [flow for flow in metadata.list_dataflows() if flow["value"] in ids]


@router.command(
    methods=["GET"],
    widget_config={
        "name": "ECB Dataflow Dimensions",
        "description": "The queryable dimensions and codelist values of a dataflow.",
        "type": "table",
        "category": "ECB",
        "subCategory": "Catalogue",
        "source": ["ECB"],
        "gridData": {"w": 30, "h": 20},
        "params": [
            {
                "paramName": "dataflow",
                "label": "Dataflow",
                "value": "EXR",
                "description": "The ECB dataflow to inspect.",
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/ecb/list_dataflows",
                "style": {"popupWidth": 600},
            }
        ],
    },
    examples=[
        APIEx(
            description="Discover the queryable dimensions of a dataflow.",
            parameters={"dataflow": "EXR"},
        )
    ],
)
async def get_dataflow_dimensions(
    metadata: EcbMetadataDependency,
    dataflow: Annotated[str, Query(description="The ECB dataflow id, e.g. 'EXR'.")],
) -> list[dict[str, Any]]:
    """Return the ordered dimensions of a dataflow with their codelist values.

    Use the dimension ids and codes to build a series key for the
    ``indicators`` command, e.g. ``EXR::D.USD.EUR.SP00.A``. Shares the
    ``dataflow`` parameter with ``available_indicators`` so a release picked in
    the calendar drives both.
    """
    return metadata.get_dataflow_dimensions(dataflow)


@router.command(
    methods=["GET"],
    widget_config={"exclude": True},
    examples=[
        APIEx(
            description="Get options for one dimension, narrowed by prior selections.",
            parameters={"dataflow_id": "EXR", "dimension_id": "CURRENCY"},
        )
    ],
)
async def dimension_choices(
    metadata: EcbMetadataDependency,
    dataflow_id: Annotated[str, Query(description="The ECB dataflow id.")],
    dimension_id: Annotated[
        str, Query(description="The dimension to list options for.")
    ],
    selections: Annotated[
        str | None,
        Query(
            description="Prior selections as 'DIM=VALUE,DIM=VALUE' to narrow the"
            " available options for this dimension.",
        ),
    ] = None,
) -> list[dict[str, str]]:
    """Return ``[{label, value}]`` for one dimension, optionally narrowed.

    With ``selections`` provided, the SDMX availability service is consulted to
    return only values that yield data given the prior choices; otherwise the
    full codelist is returned.
    """
    options = metadata.resolve_dimension_values(dataflow_id, dimension_id)
    if not selections:
        return options

    chosen: dict[str, str] = {}
    for part in selections.split(","):
        if "=" in part:
            dim, val = part.split("=", 1)
            chosen[dim.strip()] = val.strip()

    dims = metadata.get_dataflow_dimensions(dataflow_id)
    key_parts = [chosen.get(d["id"], "") for d in dims]
    key = ".".join(key_parts)
    available = metadata._fetch_available_constraint(dataflow_id, key)
    allowed = set(available.get(dimension_id, []))
    if not allowed:
        return options
    return [opt for opt in options if opt["value"] in allowed]


# A dataflow's "geography" dimension, in preference order (it has at most one) —
# what the ``reference_area`` parameter maps to for indicators and tables.
_GEOGRAPHY_DIMS = ("REF_AREA", "COUNT_AREA", "CURRENCY")


def _dataflow_dim_options(
    metadata: EcbMetadata, dataflow: str | None, candidates: tuple[str, ...]
) -> list[dict[str, str]]:
    """Return ``[{label, value}]`` for the first candidate dimension in a dataflow."""
    if not dataflow or dataflow not in metadata.dataflows:
        return []
    dim_id = next(
        (
            d["id"]
            for d in metadata.get_dataflow_dimensions(dataflow)
            if d["id"] in candidates
        ),
        None,
    )
    return metadata.resolve_dimension_values(dataflow, dim_id) if dim_id else []


@router.command(
    methods=["GET"],
    widget_config={"exclude": True},
    include_in_schema=False,
    examples=[APIEx(parameters={"dataflow": "ICP"})],
)
async def indicator_frequencies(
    metadata: EcbMetadataDependency,
    dataflow: Annotated[str | None, Query(description="The ECB dataflow id.")] = None,
) -> list[dict[str, str]]:
    """Return the frequency choices for a dataflow's ``available_indicators`` dropdown."""
    return _dataflow_dim_options(metadata, dataflow, ("FREQ",))


@router.command(
    methods=["GET"],
    widget_config={"exclude": True},
    include_in_schema=False,
    examples=[APIEx(parameters={"dataflow": "ICP"})],
)
async def indicator_areas(
    metadata: EcbMetadataDependency,
    dataflow: Annotated[str | None, Query(description="The ECB dataflow id.")] = None,
) -> list[dict[str, str]]:
    """Return the reference-area (or currency) choices for a dataflow's dropdown."""
    return _dataflow_dim_options(metadata, dataflow, _GEOGRAPHY_DIMS)


@router.command(
    methods=["GET"],
    widget_config={
        "name": "ECB Presentation Tables",
        "description": "The ECB presentation tables (Blue-Book-style hierarchies)"
        " — click a row to load it in the ECB Presentation Table widget.",
        "type": "table",
        "category": "ECB",
        "subCategory": "Presentation Tables",
        "source": ["ECB"],
        "gridData": {"w": 20, "h": 15},
        "params": [
            {
                "paramName": "table_id",
                "label": "Table",
                "description": "Selected table (set by clicking a row).",
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/ecb/list_table_choices",
                "style": {"popupWidth": 700},
            },
        ],
        "data": {
            "table": {
                "columnsDefs": [
                    {
                        "field": "value",
                        "headerName": "Table",
                        "renderFn": "cellOnClick",
                        "renderFnParams": {
                            "actionType": "groupBy",
                            "groupByParamName": "table_id",
                        },
                    },
                ],
            },
        },
    },
    examples=[APIEx(description="List ECB presentation tables.", parameters={})],
)
async def list_tables(
    metadata: EcbMetadataDependency,
    table_id: Annotated[
        str | None, Query(description="Selected table (set by clicking a row).")
    ] = None,
) -> list[dict[str, Any]]:
    """List the ECB presentation tables backed by a live dataflow."""
    return metadata.list_tables()


@router.command(
    methods=["GET"],
    widget_config={"exclude": True},
    include_in_schema=False,
    examples=[APIEx(description="Presentation-table choices.", parameters={})],
)
async def list_table_choices(
    metadata: EcbMetadataDependency,
    dataflow_id: Annotated[
        str | None, Query(description="Optional dataflow filter.")
    ] = None,
) -> list[dict[str, str]]:
    """Return ``[{label, value}]`` of presentation tables (optionally by dataflow)."""
    tables = (
        metadata.list_tables_for_dataflow(dataflow_id)
        if dataflow_id
        else metadata.list_tables()
    )
    return [{"label": t["label"], "value": t["value"]} for t in tables]


def _table_dim_options(
    metadata: EcbMetadata, table_id: str, candidates: tuple[str, ...]
) -> list[dict[str, str]]:
    """Return ``[{label, value}]`` for the first candidate dim in the table's
    valid context — only values that actually return data for this table.
    """
    valid = metadata.get_table_valid_context(table_id)
    dim_id = next((d for d in candidates if d in valid), None)
    if not dim_id:
        return []
    dataflow_id = metadata.get_table(table_id)["dataflow_id"]
    labels = next(
        (
            {opt["value"]: opt["label"] for opt in dim["values"]}
            for dim in metadata.get_dataflow_dimensions(dataflow_id)
            if dim["id"] == dim_id
        ),
        {},
    )
    return [{"label": labels.get(code, code), "value": code} for code in valid[dim_id]]


@router.command(
    methods=["GET"],
    widget_config={"exclude": True},
    include_in_schema=False,
    examples=[APIEx(parameters={"table_id": "HCL_JDF_BSI_MFI_BALANCE_SHEET@HCL_BSI"})],
)
async def presentation_table_frequencies(
    metadata: EcbMetadataDependency,
    table_id: Annotated[
        str | None, Query(description="The presentation table id.")
    ] = None,
) -> list[dict[str, str]]:
    """Return the valid frequency choices for a presentation table's dropdown."""
    if not table_id or table_id not in metadata.presentation_tables:
        return []
    return _table_dim_options(metadata, table_id, ("FREQ",))


@router.command(
    methods=["GET"],
    widget_config={"exclude": True},
    include_in_schema=False,
    examples=[APIEx(parameters={"table_id": "HCL_JDF_BSI_MFI_BALANCE_SHEET@HCL_BSI"})],
)
async def presentation_table_areas(
    metadata: EcbMetadataDependency,
    table_id: Annotated[
        str | None, Query(description="The presentation table id.")
    ] = None,
) -> list[dict[str, str]]:
    """Return the valid reference-area (or currency) choices for a table."""
    if not table_id or table_id not in metadata.presentation_tables:
        return []
    return _table_dim_options(metadata, table_id, _GEOGRAPHY_DIMS)


@router.command(
    methods=["GET"],
    widget_config={
        "name": "ECB Presentation Table",
        "description": "An ECB presentation table (Blue-Book-style hierarchy): an"
        " indented title per row with the recent periods pivoted into columns. Pick"
        " a frequency and reference area; other dimensions use standard values.",
        "type": "table",
        "category": "ECB",
        "subCategory": "Presentation Tables",
        "source": ["ECB"],
        "gridData": {"w": 40, "h": 20},
        "params": [
            {
                "paramName": "table_id",
                "label": "Table",
                "value": "HCL_JDF_BSI_MFI_BALANCE_SHEET@HCL_BSI",
                "description": "The ECB presentation table.",
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/ecb/list_table_choices",
                "style": {"popupWidth": 700},
            },
            {
                "paramName": "frequency",
                "label": "Frequency",
                "description": "Observation frequency.",
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/ecb/presentation_table_frequencies",
                "optionsParams": {"table_id": "$table_id"},
            },
            {
                "paramName": "reference_area",
                "label": "Reference area",
                "description": "Reference area (or currency) for the table.",
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/ecb/presentation_table_areas",
                "optionsParams": {"table_id": "$table_id"},
                "style": {"popupWidth": 500},
            },
            {
                "paramName": "limit",
                "label": "Periods",
                "value": 8,
                "description": "Number of recent periods to show as columns.",
                "type": "number",
            },
        ],
        "data": {
            "table": {
                "columnsDefs": [
                    {
                        "field": "title",
                        "headerName": "Title",
                        "pinned": "left",
                        "cellDataType": "text",
                        "width": 360,
                    },
                ],
            },
        },
    },
    examples=[
        APIEx(
            description="The euro area MFI balance sheet (monthly).",
            parameters={
                "table_id": "HCL_JDF_BSI_MFI_BALANCE_SHEET@HCL_BSI",
                "frequency": "M",
                "reference_area": "U2",
            },
        )
    ],
)
async def presentation_table(
    metadata: EcbMetadataDependency,
    table_id: Annotated[str, Query(description="The presentation table id.")],
    frequency: Annotated[
        str | None, Query(description="Observation frequency code (e.g. 'M').")
    ] = None,
    reference_area: Annotated[
        str | None, Query(description="Reference area / currency code (e.g. 'U2').")
    ] = None,
    limit: Annotated[
        int, Query(description="Number of recent periods to show as columns.", ge=1)
    ] = 8,
) -> list[dict[str, Any]]:
    """Resolve a presentation table to indented rows with recent periods pivoted.

    Starts from the table's cached working default slice — so it renders out of the
    box — and overrides only the frequency / reference area the user selects.
    """
    from openbb_ecb.utils.table_builder import build_presentation_table

    if table_id not in metadata.presentation_tables:
        return []
    context = dict(metadata.get_table_default_context(table_id))
    if frequency:
        context["FREQ"] = frequency
    if reference_area:
        valid = metadata.get_table_valid_context(table_id)
        geography = next((d for d in _GEOGRAPHY_DIMS if d in valid), None)
        if geography:
            context[geography] = reference_area
    return await build_presentation_table(metadata, table_id, context, limit=limit)


# ---------------------------------------------------------------------------
# Model-driven data commands.
#
# Each command registers in the ``obb.ecb.*`` namespace only when its owning
# extension is NOT installed (the alias model names below match the provider's
# ``fetcher_dict`` aliases). When the owner IS installed, the fetcher plugs into
# the owner's canonical command instead (e.g. ``obb.economy.balance_of_payments(
# provider='ecb')``), so we avoid double registration.
# ---------------------------------------------------------------------------


if not ECONOMY_INSTALLED:

    @router.command(
        model="AvailableEcbIndicators",
        examples=[
            APIEx(parameters={"provider": "ecb"}),
            APIEx(
                description="Search the catalogue.",
                parameters={"provider": "ecb", "query": "interest rate"},
            ),
        ],
    )
    async def available_indicators(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Search the ECB SDMX catalogue of dataflows."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="EcbIndicators",
        examples=[
            APIEx(
                description="Fetch any ECB series by 'FLOW::KEY' symbol.",
                parameters={"provider": "ecb", "symbol": "EXR::D.USD.EUR.SP00.A"},
            ),
        ],
    )
    async def indicators(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Fetch any ECB SDMX series by a 'FLOW::KEY' symbol."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="EcbBalanceOfPayments",
        examples=[APIEx(parameters={"provider": "ecb"})],
    )
    async def balance_of_payments(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Euro area balance of payments statistics."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="EcbReleaseCalendar",
        examples=[APIEx(parameters={"provider": "ecb"})],
    )
    async def calendar(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get the ECB statistical release calendar."""
        return await OBBject.from_query(OBBQuery(**locals()))


if not CURRENCY_INSTALLED:

    @router.command(
        model="EcbCurrencyHistorical",
        examples=[APIEx(parameters={"provider": "ecb", "symbol": "EURUSD"})],
    )
    async def exchange_rates(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Euro foreign-exchange reference rates (historical)."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="EcbCurrencyReferenceRates",
        examples=[APIEx(parameters={"provider": "ecb"})],
    )
    async def reference_rates(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get the latest euro foreign-exchange reference rates."""
        return await OBBject.from_query(OBBQuery(**locals()))


if not FIXEDINCOME_INSTALLED:

    @router.command(
        model="EcbYieldCurve",
        examples=[APIEx(parameters={"provider": "ecb"})],
    )
    async def yield_curve(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Euro area government bond yield curve."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="EcbKeyInterestRates",
        examples=[
            APIEx(parameters={"provider": "ecb", "interest_rate_type": "deposit"})
        ],
    )
    async def key_interest_rates(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get the key ECB interest rates (deposit, lending, refinancing)."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="EcbEuroShortTermRate",
        examples=[APIEx(parameters={"provider": "ecb"})],
    )
    async def euro_short_term_rate(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get the euro short-term rate (€STR) and its detail."""
        return await OBBject.from_query(OBBQuery(**locals()))


@router.command(
    model="EcbMfiInterestRates",
    examples=[
        APIEx(
            parameters={
                "provider": "ecb",
                "symbol": "household_loans_for_house_purchase",
            }
        )
    ],
)
async def mfi_interest_rates(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """MFI (bank) interest rates on euro-area loans and deposits."""
    return await OBBject.from_query(OBBQuery(**locals()))


@router.command(
    model="EcbReleases",
    widget_config={
        "name": "ECB Releases",
        "description": "ECB press releases, publications, and blog posts — each"
        " article's full content is rendered inline as a newsfeed.",
        "type": "newsfeed",
        "category": "ECB",
        "subCategory": "Releases",
        "source": ["ECB"],
        "gridData": {"w": 40, "h": 20},
        "refetchInterval": 600000,
    },
    examples=[APIEx(parameters={"provider": "ecb"})],
)
async def releases(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """ECB press releases, publications, and blog posts."""
    return await OBBject.from_query(OBBQuery(**locals()))


@router.command(
    model="EcbEligibleAssets",
    examples=[APIEx(parameters={"provider": "ecb", "currency": "EUR", "limit": 10})],
)
async def eligible_assets(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Eurosystem list of eligible marketable (collateral) assets."""
    return await OBBject.from_query(OBBQuery(**locals()))


# apps.json is authored with standalone ``obb.ecb.*`` widget ids. When an owning
# extension is installed, the ECB fetcher serves data through that extension's
# command instead, so the widget id must be remapped to the owner's namespace.
_OWNER_WIDGET_MAP: dict[str, str] = {}
if CURRENCY_INSTALLED:
    _OWNER_WIDGET_MAP.update(
        {
            "ecb_exchange_rates_ecb_obb": "currency_price_historical_ecb_obb",
            "ecb_reference_rates_ecb_obb": "currency_reference_rates_ecb_obb",
        }
    )
if ECONOMY_INSTALLED:
    _OWNER_WIDGET_MAP.update(
        {
            "ecb_available_indicators_ecb_obb": "economy_available_indicators_ecb_obb",
            "ecb_balance_of_payments_ecb_obb": "economy_balance_of_payments_ecb_obb",
            "ecb_calendar_ecb_obb": "economy_calendar_ecb_obb",
            "ecb_indicators_ecb_obb": "economy_indicators_ecb_obb",
        }
    )
if FIXEDINCOME_INSTALLED:
    _OWNER_WIDGET_MAP.update(
        {
            "ecb_key_interest_rates_ecb_obb": "fixedincome_rate_ecb_ecb_obb",
            "ecb_euro_short_term_rate_ecb_obb": "fixedincome_rate_estr_ecb_obb",
            "ecb_yield_curve_ecb_obb": "fixedincome_government_yield_curve_ecb_obb",
        }
    )


def _rewrite_widget_ids(apps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Remap standalone ``ecb_*`` widget ids to owner namespaces when installed."""
    if not _OWNER_WIDGET_MAP:
        return apps
    for app in apps:
        for tab in app.get("tabs", {}).values():
            for item in tab.get("layout", []):
                item["i"] = _OWNER_WIDGET_MAP.get(item.get("i"), item.get("i"))
    return apps


async def get_ecb_apps_json() -> list[dict[str, Any]]:
    """Serve the bundled OpenBB Workspace app definitions (``apps.json``)."""
    import json
    from pathlib import Path

    apps_file = Path(__file__).parent / "apps.json"
    try:
        with apps_file.open("r", encoding="utf-8") as file:
            return _rewrite_widget_ids(json.load(file))
    except Exception:  # noqa: BLE001
        return []


router._api_router.add_api_route(
    path="/apps.json",
    endpoint=get_ecb_apps_json,
    methods=["GET"],
    include_in_schema=False,
)
