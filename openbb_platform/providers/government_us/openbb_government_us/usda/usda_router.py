"""USDA Router."""

from datetime import datetime
from pathlib import Path

from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse
from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.example import APIEx, PythonEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query as OpenBBQuery
from openbb_core.app.router import Router
from openbb_core.app.service.system_service import SystemService

from openbb_government_us.usda import COMMODITY_INSTALLED
from openbb_government_us.usda.utils.ers_catalog import load_catalog, viz_paths

router = Router(
    prefix="",
    description="Data connector to the U.S. Department of Agriculture.",
)
api_prefix = SystemService().system_settings.api_settings.prefix

DEFAULT_ERS_VIZ = "Marketbaskets/Marketbaskets"


async def get_usda_apps_json() -> list[dict]:
    """Serve the USDA app definition for OpenBB Workspace."""
    import json

    apps_file = Path(__file__).parent / "assets" / "apps.json"
    try:
        with apps_file.open("r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:  # noqa: BLE001
        return []


router._api_router.add_api_route(
    path="/apps.json",
    endpoint=get_usda_apps_json,
    methods=["GET"],
    include_in_schema=False,
)


async def ers_viz_catalog() -> list[dict]:
    """List the USDA ERS Tableau Public visualizations.

    Returns
    -------
    list[dict]
        One record per visualization, with its embed path and public URL.
    """
    return [
        {
            "viz": f"{entry['workbook']}/{entry['default_view']}",
            "title": entry["title"],
            "description": entry["description"],
            "last_updated": entry["last_updated"],
            "url": f"https://public.tableau.com/views/{entry['workbook']}"
            f"/{entry['default_view']}",
        }
        for entry in load_catalog()
    ]


router._api_router.add_api_route(
    path="/ers_viz_catalog",
    endpoint=ers_viz_catalog,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


async def ers_chart(
    viz: str = DEFAULT_ERS_VIZ,
    theme: str | None = "dark",
) -> HTMLResponse:
    """Render an embedded USDA ERS Tableau Public visualization (OpenBB Workspace iframe widget)."""
    import json

    entry = viz_paths().get(viz)
    if entry is None:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown ERS visualization '{viz}'."
            " Valid values are 'workbook/view' paths from the catalog.",
        )
    template = (Path(__file__).parent / "assets" / "ers_chart.html").read_text(
        encoding="utf-8"
    )
    payload = {
        "viz": viz,
        "title": entry["title"],
        "description": entry["description"],
        "last_updated": entry["last_updated"],
        "theme": "light" if (theme or "").lower() == "light" else "dark",
    }
    blob = (
        json.dumps(payload)
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
    )
    return HTMLResponse(
        content=template.replace("__ERS_CHART_DATA__", blob),
        headers={"Cache-Control": "no-cache"},
    )


router._api_router.add_api_route(
    path="/ers_chart",
    endpoint=ers_chart,
    methods=["GET"],
    response_class=HTMLResponse,
    openapi_extra={
        "widget_config": {
            "name": "USDA ERS Interactive Charts",
            "description": "Interactive data visualizations published by the"
            " USDA Economic Research Service on Tableau Public.",
            "category": "Economy",
            "subCategory": "Agriculture",
            "source": ["USDA", "ERS"],
            "type": "iframe",
            "widgetId": "usda_ers_chart_usda_obb",
            "gridData": {
                "w": 40,
                "h": 30,
            },
            "params": [
                {
                    "label": "Visualization",
                    "show": True,
                    "paramName": "viz",
                    "value": DEFAULT_ERS_VIZ,
                    "type": "text",
                    "options": [
                        {
                            "label": entry["title"],
                            "value": f"{entry['workbook']}/{entry['default_view']}",
                        }
                        for entry in load_catalog()
                    ],
                    "style": {"popupWidth": 600},
                },
                {"paramName": "theme", "show": False},
            ],
            "refetchInterval": False,
        }
    },
)


@router.command(
    model="FarmToConsumerPriceSpreads",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get the milk and dairy market basket alongside whole milk, from 2015.",
            parameters={
                "item": "milk_and_dairy_basket,whole_milk",
                "start_year": 2015,
                "provider": "usda",
            },
        ),
        APIEx(
            description="Get every fresh vegetable series.",
            parameters={"category": "fresh_vegetables", "provider": "usda"},
        ),
    ],
)
async def price_spreads(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS price spreads from farm to consumer - retail price versus farm value for food items and market baskets."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


async def price_spread_items(category: str | None = None) -> list:
    """List price-spread items, narrowed to a category when provided.

    Parameters
    ----------
    category : str | None
        Data product category. When None, every item is returned.
    """
    from openbb_government_us.usda.utils.ers_price_spreads import PRICE_SPREADS_FILES

    return [
        {"label": slug.replace("_", " ").capitalize(), "value": slug}
        for slug, meta in PRICE_SPREADS_FILES.items()
        if not category or meta["category"] == category
    ]


router._api_router.add_api_route(
    path="/price_spread_items",
    endpoint=price_spread_items,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


async def milk_cost_items(
    report: str = "by_state", category: str | None = None
) -> list:
    """List milk cost items, narrowed to a cost category when provided.

    Parameters
    ----------
    report : str
        Report key, by_state or by_size_of_operation.
    category : str | None
        Cost category key. When None, every item is returned.
    """
    from openbb_government_us.usda.utils import ers_milk_cost_of_production as milk

    rows = await milk.afetch_report(
        report if report in milk.MILK_COST_FILES else "by_state"
    )
    label_to_key = {label: key for key, label in milk.ITEM_CHOICES.items()}
    category_label = milk.CATEGORY_CHOICES.get(category or "", category)
    entries: list = []
    seen: set = set()
    for row in rows:
        if category and row["category"] != category_label:
            continue
        key = label_to_key.get(row["item"])
        if key and key not in seen:
            seen.add(key)
            entries.append({"label": row["item"], "value": key})
    return entries


router._api_router.add_api_route(
    path="/milk_cost_items",
    endpoint=milk_cost_items,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


async def bell_report_commodities(is_workspace: bool = False) -> list:
    """List the commodities available for the Bell Report."""
    from openbb_government_us.usda.utils.fas_bell_report import get_commodities

    commodities = await get_commodities()
    if is_workspace:
        return [
            {
                "label": f"{row['commodity_name']} ({row['commodity_code']})",
                "value": str(row["commodity_code"]),
            }
            for row in commodities
        ]
    return commodities


router._api_router.add_api_route(
    path="/bell_report_commodities",
    endpoint=bell_report_commodities,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


async def bell_report_weeks(is_workspace: bool = False, limit: int = 260) -> list:
    """List the published period ending dates for the Bell Report."""
    from openbb_government_us.usda.utils.fas_bell_report import get_published_weeks

    weeks = (await get_published_weeks())[:limit]
    if is_workspace:
        return [
            {
                "label": row["week_ending"].strftime("%Y-%m-%d"),
                "value": row["week_ending"].strftime("%Y-%m-%d"),
            }
            for row in weeks
        ]
    return [
        {
            "week_ending": row["week_ending"],
            "released_at": row["released_at"],
        }
        for row in weeks
    ]


router._api_router.add_api_route(
    path="/bell_report_weeks",
    endpoint=bell_report_weeks,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


async def bell_report_urls(
    commodity_code: str = "101",
    week_ending: str | None = None,
) -> list:
    """List the downloadable Bell Reports for a commodity and period.

    One entry per marketing year report. Only published periods are
    offered, so an embargoed report is never addressable.
    """
    from openbb_core.app.model.abstract.error import OpenBBError

    from openbb_government_us.usda.utils.fas_bell_report import (
        REPORT_NAMES,
        build_report_url,
        get_commodities,
        get_published_weeks,
    )

    codes = [int(c.strip()) for c in str(commodity_code).split(",") if c.strip()]
    commodities = await get_commodities()
    by_code = {row["commodity_code"]: row for row in commodities}
    unknown = [c for c in codes if c not in by_code]

    if unknown:
        raise OpenBBError(
            f"Unknown commodity code(s) -> {unknown}. Valid codes are: "
            + ", ".join(str(c) for c in sorted(by_code))
        )

    weeks = await get_published_weeks()
    if week_ending:
        matches = [
            w for w in weeks if w["week_ending"].strftime("%Y-%m-%d") == week_ending
        ]
        if not matches:
            raise OpenBBError(
                f"No published Bell Report for the week ending {week_ending}."
                f" The most recent published week is {weeks[0]['week_ending']}."
            )
        week = matches[0]
    else:
        week = weeks[0]

    names = ", ".join(by_code[c]["commodity_name"] for c in codes)
    stamp = week["week_ending"].strftime("%Y-%m-%d")
    entries: list = []

    for report in REPORT_NAMES:
        url = build_report_url(
            report,
            week["week_ending"],
            week["released_at"].date(),
            [by_code[c]["id"] for c in codes],
        )
        entries.append(
            {
                "label": f"Bell Report {report.upper()} - {names} - {stamp}",
                "value": url,
            }
        )

    return entries


router._api_router.add_api_route(
    path="/bell_report_urls",
    endpoint=bell_report_urls,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


@router.command(
    methods=["POST"],
    model="FasBellReport",
    no_validate=True,
    widget_config={
        "name": "USDA FAS Bell Report",
        "description": "Weekly export sales commitments by commodity and"
        " marketing year, published by the Foreign Agricultural Service.",
        "type": "multi_file_viewer",
        "refetchInterval": False,
        "gridData": {"w": 40, "h": 30},
        "category": "Commodity",
        "subCategory": "Agriculture",
        "source": ["USDA", "FAS"],
        "params": [
            {
                "paramName": "urls",
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/usda/bell_report_urls",
                "optionsParams": {
                    "commodity_code": "$commodity_code",
                    "week_ending": "$week_ending",
                },
                "show": False,
                "multiSelect": True,
                "roles": ["fileSelector"],
            },
            {
                "paramName": "commodity_code",
                "label": "Commodity",
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/usda/bell_report_commodities",
                "optionsParams": {"is_workspace": True},
                "value": "101",
                "multiSelect": True,
                "style": {"popupWidth": 500},
            },
            {
                "paramName": "week_ending",
                "label": "Period Ending Date",
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/usda/bell_report_weeks",
                "optionsParams": {"is_workspace": True},
                "description": "Only published weeks are listed.",
            },
        ],
    },
    examples=[
        APIEx(
            parameters={
                "provider": "usda",
                "urls": [
                    "https://apps.fas.usda.gov/esrqs/ReportsHome.aspx?RN=BR&wed=07%2F03%2F2025&YGO=07%2F04%2F2024&RD=07%2F10%2F2025&MY=N&CID=1%2C&AppUserId=0"
                ],
            },
        ),
        PythonEx(
            description="List the reports published for wheat and corn, then download them.",
            code=[
                "urls = [d['value'] for d in obb.usda.bell_report_urls(commodity_code='101,401')]",
                "pdfs = obb.usda.bell_report(urls=urls)",
            ],
        ),
    ],
)
async def bell_report(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Download one, or more, USDA FAS Bell Reports.

    This command returns only the results portion of the OBBject response.
    It contains a list of dictionaries where the base64 encoded content of the
    document is under the 'content' key.
    """
    response = await OBBject.from_query(OpenBBQuery(**locals()))
    return response.model_dump().get("results", {})


@router.command(
    model="ErsPublications",
    widget_config={"exclude": True},
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get the Livestock, Dairy, and Poultry Outlook releases.",
            parameters={"series": "LDPM", "provider": "usda"},
        ),
        APIEx(
            description="Get every research report released since 2025.",
            parameters={
                "series": "research-reports",
                "start_date": "2025-01-01",
                "provider": "usda",
            },
        ),
    ],
)
async def publications(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the USDA ERS publications catalog - outlook, research, and discontinued report series."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


async def ers_publication_urls(
    series: str = "outlook-reports",
    limit: int = 25,
) -> list:
    """List the most recent ERS publications as downloadable choices."""
    from openbb_government_us.usda.utils.ers_publications import fetch_publications

    rows = await fetch_publications(series)
    rows.sort(key=lambda row: row["release_date"] or "", reverse=True)
    return [
        {
            "label": f"{row['release_date']} - {row['title']}",
            "value": row["url"],
        }
        for row in rows[:limit]
    ]


router._api_router.add_api_route(
    path="/ers_publication_urls",
    endpoint=ers_publication_urls,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


async def ers_publication_series() -> list:
    """List the ERS publication series groups and codes."""
    from openbb_government_us.usda.utils.ers_publications import (
        SERIES_CODES,
        SERIES_GROUPS,
    )

    return [
        {"label": group.replace("-", " ").title(), "value": group}
        for group in SERIES_GROUPS
    ] + [
        {"label": f"{code}: {name}", "value": code}
        for code, name in SERIES_CODES.items()
    ]


router._api_router.add_api_route(
    path="/ers_publication_series",
    endpoint=ers_publication_series,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


@router.command(
    methods=["POST"],
    model="ErsPublicationDownload",
    no_validate=True,
    widget_config={
        "name": "USDA ERS Publications Viewer",
        "description": "Full Report PDFs published by the USDA Economic Research"
        " Service, including the Outlook report series.",
        "type": "multi_file_viewer",
        "refetchInterval": False,
        "gridData": {"w": 20, "h": 30},
        "category": "Economy",
        "subCategory": "Agriculture",
        "source": ["USDA", "ERS"],
        "params": [
            {
                "paramName": "urls",
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/usda/ers_publication_urls",
                "optionsParams": {"series": "$series"},
                "show": False,
                "multiSelect": True,
                "roles": ["fileSelector"],
            },
            {
                "paramName": "series",
                "label": "Series",
                "value": "outlook-reports",
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/usda/ers_publication_series",
                "style": {"popupWidth": 500},
            },
        ],
    },
    examples=[
        APIEx(
            parameters={
                "provider": "usda",
                "urls": ["https://www.ers.usda.gov/publications/115092"],
            }
        ),
        PythonEx(
            description="Download the latest Livestock, Dairy, and Poultry Outlook.",
            code=[
                "rows = obb.usda.publications(series='LDPM').to_df()",
                "pdfs = obb.usda.publication_documents(urls=[rows.iloc[0]['url']])",
            ],
        ),
    ],
)
async def publication_documents(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Download one, or more, USDA ERS publication Full Report PDFs.

    This command returns only the results portion of the OBBject response.
    It contains a list of dictionaries where the base64 encoded content of the
    document is under the 'content' key.
    """
    response = await OBBject.from_query(OpenBBQuery(**locals()))
    return response.model_dump().get("results", {})


async def psd_report_commodities() -> list:
    """List the commodities that publish a PSD circular."""
    from openbb_government_us.usda.utils.psd_circulars import COMMODITIES

    return [
        {"label": commodity.replace("_", " ").title(), "value": commodity}
        for commodity in COMMODITIES
    ]


router._api_router.add_api_route(
    path="/psd_report_commodities",
    endpoint=psd_report_commodities,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


async def psd_report_urls(commodity: str | None = None) -> list:
    """List PSD circulars for the file selector.

    Parameters
    ----------
    commodity : str | None
        Commodity(ies) to list, as a comma-separated list. When a commodity is
        given, every historical circular for it is returned, newest first. When
        None, only the latest circular for every commodity is returned.
    """
    from openbb_government_us.usda.utils.psd_circulars import (
        historical_circulars,
        latest_circulars,
    )

    codes = (
        [c.strip() for c in str(commodity).split(",") if c.strip()]
        if commodity
        else [None]
    )
    entries: list = []

    for code in codes:
        rows = (
            await historical_circulars(code) if code else await latest_circulars(None)
        )
        for row in rows:
            stamp = f"{row['year']}-{row['month']:02d}"
            label = f"{row['commodity'].replace('_', ' ').title()} - {stamp}"
            entries.append({"label": label, "value": row["url"]})

    return entries


router._api_router.add_api_route(
    path="/psd_report_urls",
    endpoint=psd_report_urls,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


def _psd_attribute_label(key: str) -> str:
    """Format a PSD attribute key for display."""
    return (
        key.replace("_", " ")
        .title()
        .replace("Us", "US")
        .replace("Ty", "TY")
        .replace("Fsi", "FSI")
    )


async def psd_data_attributes(commodity: str | None = None) -> list:
    """List the PSD attributes available for a commodity.

    Parameters
    ----------
    commodity : str | None
        Commodity name. When None (report mode), every attribute is listed.
    """
    from openbb_government_us.usda.utils.psd_codes import ATTRIBUTES, COMMODITIES
    from openbb_government_us.usda.utils.psd_data_downloader import (
        _get_commodity_attributes,
    )

    code = COMMODITIES.get(commodity or "")
    keys = _get_commodity_attributes(code) if code else sorted(ATTRIBUTES)
    return [{"label": "All Attributes", "value": None}] + [
        {"label": _psd_attribute_label(key), "value": key} for key in keys
    ]


router._api_router.add_api_route(
    path="/psd_data_attributes",
    endpoint=psd_data_attributes,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


async def psd_data_countries(commodity: str | None = None) -> list:
    """List the PSD countries available for a commodity.

    Parameters
    ----------
    commodity : str | None
        Commodity name. When None (report mode), every country and region is
        listed.
    """
    from openbb_government_us.usda.utils.psd_codes import (
        COMMODITIES,
        COUNTRIES,
        REGIONS,
    )
    from openbb_government_us.usda.utils.psd_data_downloader import (
        _get_commodity_countries,
    )

    code = COMMODITIES.get(commodity or "")
    options: list = [{"label": "All Countries", "value": None}]
    if code:
        for name, ccode in _get_commodity_countries(code).items():
            options.append({"label": name, "value": ccode})
    else:
        choices = {
            **{name: c for name, c in COUNTRIES.items() if name != "world"},
            **REGIONS,
        }
        for name, ccode in choices.items():
            options.append({"label": name.replace("_", " ").title(), "value": ccode})
    return options


router._api_router.add_api_route(
    path="/psd_data_countries",
    endpoint=psd_data_countries,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


@router.command(
    model="FasReportCalendar",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get the upcoming Weekly Export Sales releases.",
            parameters={"report_type": "export_sales", "provider": "usda"},
        ),
        APIEx(
            description="Get upcoming releases covering cotton.",
            parameters={"commodity": "cotton", "provider": "usda"},
        ),
    ],
)
async def report_calendar(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the USDA Foreign Agricultural Service calendar of upcoming report releases."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="DairyData",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get the dairy situation at a glance since 2020.",
            parameters={
                "table": "situation_at_a_glance",
                "start_year": 2020,
                "provider": "usda",
            },
        ),
    ],
)
async def dairy_data(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS dairy data - supply, use, prices, and trade for milk and dairy products."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="MilkCostOfProduction",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get milk production costs by size of operation.",
            parameters={"report": "by_size_of_operation", "provider": "usda"},
        ),
        APIEx(
            description="Get Wisconsin operating costs since 2022.",
            parameters={
                "state": "wisconsin",
                "category": "operating costs",
                "start_year": 2022,
                "provider": "usda",
            },
        ),
    ],
)
async def milk_cost_of_production(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS milk cost of production estimates, by state or by size of operation."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="MajorLandUses",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get cropland used for crops.",
            parameters={"table": "cropland_used_for_crops", "provider": "usda"},
        ),
    ],
)
async def major_land_uses(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS major land uses - acreage by land use class for the United States and its regions."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="UsAgriculturalTrade",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get the top export markets for corn, by volume.",
            parameters={
                "table": "top_export_markets",
                "commodity": "Corn",
                "provider": "usda",
            },
        ),
        APIEx(
            description="Get the monthly agricultural trade totals since 2020.",
            parameters={
                "table": "monthly",
                "start_year": 2020,
                "provider": "usda",
            },
        ),
    ],
)
async def agricultural_trade(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the ERS U.S. agricultural trade data update - each table pivoted to a wide layout with the year and period in the rows and the trade direction, commodity, or trade partner spread into columns."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


async def agricultural_trade_measures(table: str | None = None) -> list:
    """List the measures available in an agricultural-trade table.

    Parameters
    ----------
    table : str | None
        Table slug to scope the measures to. When None or unknown, the
        year-to-date exports table's measures are returned.
    """
    from openbb_government_us.usda.utils.ers_fatus_trade import (
        MEASURE_LABELS,
        TABLE_MEASURES,
    )

    measures = TABLE_MEASURES.get(table or "", TABLE_MEASURES["exports_ytd"])
    return [
        {"label": MEASURE_LABELS[measure], "value": measure} for measure in measures
    ]


router._api_router.add_api_route(
    path="/agricultural_trade_measures",
    endpoint=agricultural_trade_measures,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


async def agricultural_trade_commodities(table: str | None = None) -> list:
    """List the commodities available in an agricultural-trade table.

    Parameters
    ----------
    table : str | None
        Table slug to scope the commodities to. When None, every commodity is
        returned.
    """
    from openbb_government_us.usda.utils.ers_fatus_trade import distinct_field

    return [
        {"label": name, "value": name}
        for name in await distinct_field("commodity", table)
    ]


router._api_router.add_api_route(
    path="/agricultural_trade_commodities",
    endpoint=agricultural_trade_commodities,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


async def agricultural_trade_periods(table: str = "exports_ytd") -> list:
    """List the reporting bases an agricultural-trade table publishes.

    Parameters
    ----------
    table : str
        Table slug to scope the bases to. When unknown, the year-to-date
        exports table is used.
    """
    from openbb_government_us.usda.utils.ers_fatus_trade import (
        TRADE_TABLES,
        table_period_bases,
    )

    if table not in TRADE_TABLES:
        table = "exports_ytd"
    return [
        {"label": basis, "value": basis} for basis in await table_period_bases(table)
    ]


router._api_router.add_api_route(
    path="/agricultural_trade_periods",
    endpoint=agricultural_trade_periods,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


@router.command(
    model="MeatPriceSpreads",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get the pork values and spreads table, annual rows only.",
            parameters={
                "table": "pork",
                "frequency": "annual",
                "provider": "usda",
            },
        ),
        APIEx(
            description="Get the historical monthly beef, pork, and broiler series since 2000.",
            parameters={
                "table": "historical_monthly",
                "start_year": 2000,
                "provider": "usda",
            },
        ),
    ],
)
async def meat_price_spreads(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS meat price spreads - retail values, farm values, price spreads, and farmers' shares for beef, pork, poultry, and eggs."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="WheatData",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get world and U.S. wheat supply and disappearance since 2010.",
            parameters={
                "table": "world_supply_and_disappearance",
                "start_year": 2010,
                "provider": "usda",
            },
        ),
        APIEx(
            description="Get the historical by-class quarterly balance sheet.",
            parameters={"table": "by_class_quarterly", "provider": "usda"},
        ),
    ],
)
async def wheat_data(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS wheat data - the Wheat Yearbook supply, use, price, and trade tables, each pivoted to a wide layout by year."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="CommodityCostsAndReturns",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get the U.S. total corn budget since 2020.",
            parameters={
                "commodity": "corn",
                "region": "U.S. total",
                "start_year": 2020,
                "provider": "usda",
            },
        ),
        APIEx(
            description="Get farrow-to-finish hog operating costs.",
            parameters={
                "commodity": "hogs_farrow_finish",
                "category": "operating_costs",
                "provider": "usda",
            },
        ),
    ],
)
async def commodity_costs_and_returns(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS commodity costs and returns - annual per-unit cost-and-return budgets by commodity and ERS Farm Resource Region."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


async def commodity_cost_regions(commodity: str = "corn") -> list:
    """List the ERS Farm Resource Regions for a commodity's cost budget.

    Parameters
    ----------
    commodity : str
        Commodity key. Unknown commodities fall back to corn's regions.
    """
    from openbb_government_us.usda.utils.ers_commodity_costs_and_returns import (
        COMMODITY_REGIONS,
    )

    regions = COMMODITY_REGIONS.get(commodity) or COMMODITY_REGIONS["corn"]
    return [{"label": region, "value": region} for region in regions]


router._api_router.add_api_route(
    path="/commodity_cost_regions",
    endpoint=commodity_cost_regions,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


async def rice_frequencies(table: str = "us_supply_disappearance_price") -> list:
    """List the observation frequencies a Rice Yearbook table publishes.

    Parameters
    ----------
    table : str
        Table key from RICE_TABLES. When absent, the default table is used.
    """
    from openbb_government_us.usda.utils.ers_rice_yearbook import (
        RICE_TABLES,
        table_frequencies,
    )

    if table not in RICE_TABLES:
        table = "us_supply_disappearance_price"
    return [{"label": freq, "value": freq} for freq in await table_frequencies(table)]


router._api_router.add_api_route(
    path="/rice_frequencies",
    endpoint=rice_frequencies,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


@router.command(
    model="RiceYearbook",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get world rice trade on a milled basis since 2020.",
            parameters={
                "table": "world_trade_milled_basis",
                "start_year": 2020,
                "provider": "usda",
            },
        ),
        APIEx(
            description="Get the top 10 U.S. rice export markets.",
            parameters={"table": "us_top_export_markets", "provider": "usda"},
        ),
    ],
)
async def rice_yearbook(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS rice data - the Rice Yearbook acreage, supply, use, stocks, price, and trade tables, each pivoted to a wide layout by year."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


async def sugar_frequencies(table: str = "table_24a") -> list:
    """List the period bases a Sugar and Sweeteners Yearbook table publishes.

    Parameters
    ----------
    table : str
        Table key from SUGAR_SWEETENERS_FILES. When absent, the default table
        is used.
    """
    from openbb_government_us.usda.utils.ers_sugar_sweeteners_yearbook import (
        SUGAR_SWEETENERS_FILES,
        table_frequencies,
    )

    if table not in SUGAR_SWEETENERS_FILES:
        table = "table_24a"
    return [{"label": freq, "value": freq} for freq in await table_frequencies(table)]


router._api_router.add_api_route(
    path="/sugar_frequencies",
    endpoint=sugar_frequencies,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


@router.command(
    model="SugarSweetenersYearbook",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get U.S. sugar supply and use since 2020.",
            parameters={
                "table": "table_24a",
                "start_year": 2020,
                "provider": "usda",
            },
        ),
        APIEx(
            description="Get the world white refined sugar futures price table.",
            parameters={"table": "table_2", "provider": "usda"},
        ),
        APIEx(
            description="Get U.S. honey imports by country of source since 2020.",
            parameters={
                "table": "table_48a",
                "start_year": 2020,
                "provider": "usda",
            },
        ),
    ],
)
async def sugar_sweeteners_yearbook(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS Sugar and Sweeteners Yearbook tables - U.S., Mexican, and world sugar and sweetener prices, supply and use, production, consumption, and trade, each pivoted to a wide layout by attribute."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


async def oil_crops_frequencies(
    table: str = "soybeans_supply_disappearance_price",
) -> list:
    """List the observation frequencies an Oil Crops Yearbook table publishes.

    Parameters
    ----------
    table : str
        Table key from OIL_CROPS_TABLES. When absent, the default table is used.
    """
    from openbb_government_us.usda.utils.ers_oil_crops_yearbook import (
        FREQUENCIES_BY_TABLE,
        FREQUENCY_LABELS,
        OIL_CROPS_TABLES,
    )

    if table not in OIL_CROPS_TABLES:
        table = "soybeans_supply_disappearance_price"
    return [
        {"label": FREQUENCY_LABELS[freq], "value": freq}
        for freq in FREQUENCIES_BY_TABLE[table]
    ]


router._api_router.add_api_route(
    path="/oil_crops_frequencies",
    endpoint=oil_crops_frequencies,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


@router.command(
    model="OilCropsYearbook",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get U.S. soybean exports by destination since 2015.",
            parameters={
                "table": "soybean_exports_by_destination",
                "start_year": 2015,
                "provider": "usda",
            },
        ),
        APIEx(
            description="Get world oilseed supply and distribution, by oilseed.",
            parameters={
                "table": "world_oilseed_supply_and_distribution",
                "provider": "usda",
            },
        ),
    ],
)
async def oil_crops_yearbook(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS Oil Crops Yearbook data - the U.S. and world oilseed, oilmeal, and vegetable-oil supply, use, price, and trade tables, each pivoted to a wide layout by year."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="FeedGrainsDatabase",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get corn and sorghum farm prices since 1990.",
            parameters={
                "table": "corn_and_sorghum_farm_prices",
                "start_year": 1990,
                "provider": "usda",
            },
        ),
        APIEx(
            description="Get U.S. corn and sorghum exports by selected destinations.",
            parameters={
                "table": "corn_and_sorghum_exports_by_destination",
                "provider": "usda",
            },
        ),
    ],
)
async def feed_grains_database(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS feed grains data - the Feed Grains Yearbook acreage, supply, use, price, and trade tables, each pivoted to a wide layout by year."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


async def fruit_yearbook_tables(category: str | None = None) -> list:
    """List the Fruit and Tree Nuts Yearbook tables, narrowed to a category.

    Parameters
    ----------
    category : str | None
        Letter category A through H. When None, every table is returned.
    """
    from openbb_government_us.usda.utils.ers_fruit_and_tree_nuts_data import (
        TABLE_TITLES,
        category_tables,
    )

    return [
        {"label": f"{code} - {TABLE_TITLES[code]}", "value": code}
        for code in category_tables(category)
    ]


router._api_router.add_api_route(
    path="/fruit_yearbook_tables",
    endpoint=fruit_yearbook_tables,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


@router.command(
    model="FruitAndTreeNutsData",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get U.S. apple production, utilization, and grower price since 2010.",
            parameters={"table": "B-3", "start_year": 2010, "provider": "usda"},
        ),
        APIEx(
            description="Get the tree-nut area-bearing table, one column per nut.",
            parameters={"category": "F", "table": "F-1", "provider": "usda"},
        ),
    ],
)
async def fruit_and_tree_nuts_data(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS fruit and tree nuts data - the Fruit and Tree Nuts Yearbook area, production, price, supply, per-capita availability, and import-share tables, each pivoted to a wide layout by year."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="VegetablesAndPulses",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get the U.S. fresh asparagus balance sheet since 2015.",
            parameters={
                "table": "Table13_Asparagus",
                "start_year": 2015,
                "provider": "usda",
            },
        ),
        APIEx(
            description="Get selected world vegetable production since 2020.",
            parameters={
                "table": "Table09_WorldVegProduction",
                "start_year": 2020,
                "provider": "usda",
            },
        ),
    ],
)
async def vegetables_and_pulses(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS vegetables and pulses yearbook data - U.S. and world vegetable and pulse-crop supply, availability, per capita use, price, trade, and cash receipts, each table pivoted to a wide layout with the data elements as columns and years as rows."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


async def cotton_frequencies(table: str = "cotton_supply_and_use") -> list:
    """List the reporting frequencies a cotton, wool, or textile table publishes.

    Parameters
    ----------
    table : str
        Table key from CWT_TABLES. When absent, the default table is used.
    """
    from openbb_government_us.usda.utils.ers_cotton_wool_and_textile_data import (
        CWT_TABLES,
        table_frequencies,
    )

    if table not in CWT_TABLES:
        table = "cotton_supply_and_use"
    return [{"label": freq, "value": freq} for freq in await table_frequencies(table)]


router._api_router.add_api_route(
    path="/cotton_frequencies",
    endpoint=cotton_frequencies,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


@router.command(
    model="CottonWoolAndTextileData",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get world cotton supply and use since 2010.",
            parameters={
                "table": "world_cotton_supply_and_use",
                "start_year": 2010,
                "provider": "usda",
            },
        ),
        APIEx(
            description="Get U.S. cotton textile and apparel imports by country of origin.",
            parameters={
                "table": "rfe_cotton_textile_imports_by_origin",
                "provider": "usda",
            },
        ),
    ],
)
async def cotton_wool_and_textile_data(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS cotton, wool, and textile data - the Cotton and Wool Yearbook supply, use, price, and trade tables plus the raw-fiber equivalents of U.S. textile trade, each pivoted to a wide layout by year."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="FertilizerUseAndPrice",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get average U.S. farm prices of selected fertilizers since 2010.",
            parameters={
                "table": "farm_prices",
                "start_year": 2010,
                "provider": "usda",
            },
        ),
        APIEx(
            description="Get the percent of corn acreage receiving nitrogen, by State.",
            parameters={"table": "corn_nitrogen_share", "provider": "usda"},
        ),
    ],
)
async def fertilizer_use_and_price(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS fertilizer use and price - U.S. nutrient and material consumption, farm prices, price indexes, and crop-by-State application rates and shares, each pivoted to a wide layout by year."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="FoodPriceOutlook",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get the annual consumer food price index changes since 2000.",
            parameters={
                "table": "cpi_annual",
                "start_year": 2000,
                "provider": "usda",
            },
        ),
        APIEx(
            description="Get the consumer forecast prediction intervals for beef and eggs.",
            parameters={
                "table": "cpi_forecast",
                "item": "beef,eggs",
                "provider": "usda",
            },
        ),
        APIEx(
            description="Get the historical consumer forecast vintages for all food.",
            parameters={
                "table": "cpi_forecast_history",
                "item": "all food",
                "provider": "usda",
            },
        ),
    ],
)
async def food_price_outlook(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS Food Price Outlook - consumer and producer food price index forecasts, prediction intervals, and the annual percent-change record, each pivoted to a wide layout."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


async def food_price_outlook_items(table: str = "cpi_forecast") -> list:
    """List the price-index items available in a Food Price Outlook table.

    Parameters
    ----------
    table : str
        Table key. Unknown tables fall back to the CPI forecast table.
    """
    from openbb_government_us.usda.utils import ers_food_price_outlook as fpo

    key = table if table in fpo.FOOD_PRICE_OUTLOOK_FILES else "cpi_forecast"
    seen: dict[str, None] = {}
    for record in await fpo.afetch_table(key):
        item = record.get("item")
        if item:
            seen.setdefault(item, None)
    return [{"label": item, "value": item} for item in seen]


router._api_router.add_api_route(
    path="/food_price_outlook_items",
    endpoint=food_price_outlook_items,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


@router.command(
    model="FruitAndVegetablePrices",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get 2023 average retail and cup-equivalent prices for vegetables.",
            parameters={"table": "vegetable", "provider": "usda"},
        ),
    ],
)
async def fruit_and_vegetable_prices(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS fruit and vegetable prices - 2023 average retail price, preparation yield factor, cup-equivalent size, and average price per edible cup-equivalent, one row per commodity and marketed form."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="LivestockAndMeatDomesticData",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get red meat and poultry production since 2020.",
            parameters={
                "table": "production",
                "start_year": 2020,
                "provider": "usda",
            },
        ),
        APIEx(
            description="Get monthly livestock prices since 2024.",
            parameters={
                "table": "livestock_prices",
                "start_year": 2024,
                "provider": "usda",
            },
        ),
    ],
)
async def livestock_and_meat_domestic_data(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS livestock and meat domestic data - slaughter, production, weights, cold storage, supply and disappearance, and livestock and wholesale prices, each pivoted to a wide layout by attribute."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="SeasonAveragePriceForecasts",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get only the latest weekly forecast vintage for soybeans.",
            parameters={
                "commodity": "Soybeans",
                "latest": True,
                "provider": "usda",
            },
        ),
        APIEx(
            description="Get wheat season-average price forecasts since 2015.",
            parameters={
                "commodity": "Wheat",
                "start_year": 2015,
                "provider": "usda",
            },
        ),
    ],
)
async def season_average_price_forecasts(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS season-average price forecasts - weekly ERS model and monthly WASDE marketing-year average price forecasts, with farm-bill PLC and ARC benchmarks, for corn, soybeans, wheat, and cotton."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


async def farm_income_states(table: str = "income_statement") -> list:
    """List the states published for a farm income and wealth table.

    Parameters
    ----------
    table : str
        Table key. Unknown tables fall back to the income statement's states.
    """
    from openbb_government_us.usda.utils.ers_farm_income_and_wealth_statistics import (
        TABLE_PREFIXES,
        state_options,
    )

    return state_options(table if table in TABLE_PREFIXES else "income_statement")


router._api_router.add_api_route(
    path="/farm_income_states",
    endpoint=farm_income_states,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


@router.command(
    model="FarmHouseholdIncomeAndCharacteristics",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get mean and median U.S. farm operator household income"
            " since 2000.",
            parameters={
                "table": "mean_median_income",
                "start_year": 2000,
                "provider": "usda",
            },
        ),
        APIEx(
            description="Get 2024 household characteristics by age of the principal"
            " operator.",
            parameters={
                "table": "by_age_2024",
                "provider": "usda",
            },
        ),
    ],
)
async def farm_household_income_and_characteristics(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS Farm Household Income and Characteristics - income, finances, and characteristics of U.S. farm operator households, each pivoted to a wide layout by year or category."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="FarmIncomeAndWealthStatistics",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get the Iowa farm income statement since 2015.",
            parameters={
                "table": "income_statement",
                "state": "IA",
                "start_year": 2015,
                "provider": "usda",
            },
        ),
        APIEx(
            description="Get the U.S. farm sector balance sheet.",
            parameters={"table": "balance_sheet", "provider": "usda"},
        ),
        APIEx(
            description="Get U.S. farm financial ratios since 2000.",
            parameters={
                "table": "financial_ratios",
                "start_year": 2000,
                "provider": "usda",
            },
        ),
    ],
)
async def farm_income_and_wealth_statistics(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS farm income and wealth statistics - U.S. and State-level farm sector income statements, production expenses, cash receipts, government payments, farm-related income, home consumption, inventory change, balance sheets, financial ratios, and farm business income, each pivoted to a wide layout by year."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="FoodDollarSeries",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get the real (2017-dollar) food dollar in millions of dollars.",
            parameters={
                "series": "real",
                "units": "level",
                "table": 1,
                "provider": "usda",
            },
        ),
        APIEx(
            description="Get the beef, pork, and other meats commodity-group breakdown.",
            parameters={"table": 9, "provider": "usda"},
        ),
    ],
)
async def food_dollar_series(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS food dollar series - the marketing-bill breakdown of the U.S. food dollar into industry groups and primary factors, in nominal and real terms, each table pivoted to a wide layout by year."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


async def food_dollar_components(series: str = "nominal") -> list:
    """List the primary-factor components available for a food-dollar series.

    Parameters
    ----------
    series : str
        Series key, nominal or real. Unknown series fall back to nominal.
    """
    from openbb_government_us.usda.utils.ers_food_dollar_series import (
        COMPONENT_LABELS,
        SERIES_COMPONENTS,
    )

    components = SERIES_COMPONENTS.get(series) or SERIES_COMPONENTS["nominal"]
    return [{"label": COMPONENT_LABELS[key], "value": key} for key in components]


router._api_router.add_api_route(
    path="/food_dollar_components",
    endpoint=food_dollar_components,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


async def food_dollar_tables(series: str = "nominal") -> list:
    """List the food-dollar tables available for a series.

    Parameters
    ----------
    series : str
        Series key, nominal or real. Unknown series fall back to nominal.
    """
    from openbb_government_us.usda.utils.ers_food_dollar_series import (
        FOOD_DOLLAR_FILES,
        TABLE_NAMES,
    )

    tables = (FOOD_DOLLAR_FILES.get(series) or FOOD_DOLLAR_FILES["nominal"])["tables"]
    return [{"label": f"{num} - {TABLE_NAMES[num]}", "value": num} for num in tables]


router._api_router.add_api_route(
    path="/food_dollar_tables",
    endpoint=food_dollar_tables,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


@router.command(
    model="FoodExpenditureSeries",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get constant-dollar food and alcohol expenditures since 2015.",
            parameters={
                "measure": "constant",
                "start_year": 2015,
                "provider": "usda",
            },
        ),
        APIEx(
            description="Get monthly food sales.",
            parameters={"table": "monthly", "provider": "usda"},
        ),
        APIEx(
            description="Get food expenditures by final purchaser since 2010.",
            parameters={
                "table": "by_final_purchaser",
                "start_year": 2010,
                "provider": "usda",
            },
        ),
        APIEx(
            description="Get California per-capita food sales without taxes and tips.",
            parameters={
                "table": "state_per_capita",
                "state": "california",
                "taxes": "without",
                "provider": "usda",
            },
        ),
    ],
)
async def food_expenditure_series(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS Food Expenditure Series - U.S. food and alcohol expenditures by outlet, final purchaser, month, and state, in nominal and constant dollars, each pivoted to a wide layout by year."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="UsFoodImports",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get U.S. food import volume by food group since 2015.",
            parameters={
                "table": "by_food_group",
                "measure": "volume",
                "start_year": 2015,
                "provider": "usda",
            },
        ),
        APIEx(
            description="Get fresh fruit imports by source country.",
            parameters={
                "table": "by_source",
                "food_group": "Fruits",
                "commodity": "Fresh or chilled fruit",
                "provider": "usda",
            },
        ),
    ],
)
async def us_food_imports(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS U.S. food imports - annual value, volume, unit prices, and price inflation by food group and by source country."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


async def food_import_commodities(food_group: str = "Fruits") -> list:
    """List the product lines available for a food group's source-country table.

    Parameters
    ----------
    food_group : str
        Detail food-group category code, e.g. 'Fruits'.
    """
    from openbb_government_us.usda.utils.ers_us_food_imports import (
        FOOD_GROUPS,
        afetch_records,
        product_lines,
    )

    group = food_group if food_group in FOOD_GROUPS else "Fruits"
    records = await afetch_records()
    return [{"label": name, "value": name} for name in product_lines(records, group)]


router._api_router.add_api_route(
    path="/food_import_commodities",
    endpoint=food_import_commodities,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


@router.command(
    model="UsBioenergyStatistics",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get fuel ethanol supply and disappearance by calendar"
            " year since 2015.",
            parameters={
                "table": "ethanol_supply_calendar_year",
                "start_year": 2015,
                "provider": "usda",
            },
        ),
        APIEx(
            description="Get fuel ethanol production capacity by State.",
            parameters={
                "table": "ethanol_capacity_by_state",
                "provider": "usda",
            },
        ),
    ],
)
async def us_bioenergy_statistics(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS U.S. Bioenergy Statistics - ethanol, biodiesel, and renewable diesel supply, use, capacity, consumption, and prices, each pivoted to a wide layout by period."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="AgriculturalExchangeRates",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get real bilateral exchange rates for North American"
            " partner countries.",
            parameters={
                "provider": "usda",
                "table": "real_bilateral_annual",
                "region": "North America",
            },
        ),
        APIEx(
            description="Get the monthly U.S.-import-weighted real trade-weighted"
            " index since 2020.",
            parameters={
                "provider": "usda",
                "table": "real_index_monthly",
                "weights": "U.S. suppliers (U.S. import weights)",
                "start_year": 2020,
            },
        ),
    ],
)
async def agricultural_exchange_rates(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS agricultural exchange rates - real and nominal commodity trade-weighted exchange rate indexes and bilateral local-currency-per-USD rates, each pivoted to a wide layout with time in the rows and the commodity (index tables) or partner country (bilateral tables) in the columns."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


async def agricultural_productivity_states(table: str = "national_indices") -> list:
    """List the states published for an agricultural productivity table.

    Parameters
    ----------
    table : str
        Table key. Unknown tables fall back to the national table's states.
    """
    from openbb_government_us.usda.utils.ers_agricultural_productivity import (
        AGRICULTURAL_PRODUCTIVITY_FILES,
        state_options,
    )

    return state_options(
        table if table in AGRICULTURAL_PRODUCTIVITY_FILES else "national_indices"
    )


router._api_router.add_api_route(
    path="/agricultural_productivity_states",
    endpoint=agricultural_productivity_states,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


@router.command(
    model="AgriculturalProductivity",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get the U.S. farm output, input, and TFP indices since 2000.",
            parameters={
                "table": "national_indices",
                "start_year": 2000,
                "provider": "usda",
            },
        ),
        APIEx(
            description="Get California's relative TFP, output, and input levels.",
            parameters={
                "table": "state_relative_levels",
                "state": "CA",
                "provider": "usda",
            },
        ),
    ],
)
async def agricultural_productivity(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS agricultural productivity - the farm output, input, and total factor productivity indices for the United States and the relative productivity levels of the 48 contiguous States, each pivoted to a wide layout with the series as columns and years as rows."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


async def ag_productivity_countries(grouping: str = "country_grouping") -> list:
    """List the countries, territories, and aggregates in a grouping.

    Parameters
    ----------
    grouping : str
        Grouping key. Unknown groupings fall back to the country grouping.
    """
    from openbb_government_us.usda.utils.ers_international_agricultural_productivity import (  # noqa: E501
        GROUPINGS,
        entity_options,
    )

    return entity_options(grouping if grouping in GROUPINGS else "country_grouping")


router._api_router.add_api_route(
    path="/ag_productivity_countries",
    endpoint=ag_productivity_countries,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


@router.command(
    model="InternationalAgriculturalProductivity",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get U.S. agricultural productivity indices since 2000.",
            parameters={
                "grouping": "north_america",
                "country": 179,
                "start_year": 2000,
                "provider": "usda",
            },
        ),
        APIEx(
            description="Get India's physical output and input quantities.",
            parameters={
                "grouping": "asia_pacific",
                "country": 103,
                "measure": "physical_quantities",
                "provider": "usda",
            },
        ),
    ],
)
async def international_agricultural_productivity(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS international agricultural productivity - agricultural total factor productivity indices, output and input quantity indices, and the underlying physical output and input quantities for countries, territories, regions, income groups, and the world, pivoted to a wide layout by year."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="InternationalMacroeconomicDataSet",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get real GDP year-to-year growth rates by country and"
            " region since 2000.",
            parameters={
                "variable": "real_gdp",
                "measure": "growth",
                "start_year": 2000,
                "provider": "usda",
            },
        ),
        APIEx(
            description="Get historical and projected population by country and"
            " region.",
            parameters={
                "variable": "population",
                "measure": "level",
                "provider": "usda",
            },
        ),
        APIEx(
            description="Get consumer price indices, 2017 = 100, since 2010.",
            parameters={
                "variable": "cpi",
                "measure": "level",
                "start_year": 2010,
                "provider": "usda",
            },
        ),
    ],
)
async def international_macroeconomic_data_set(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS International Macroeconomic Data Set - historical and projected real GDP, GDP per capita, GDP deflator, real GDP shares, real exchange rates, consumer price indices, and population for baseline countries and regions from 1970 through the 2035 projection horizon, pivoted to a wide layout with the countries and regions as columns and the years as rows."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


async def livestock_trade_products(
    table: str = "beef_veal", direction: str = "imports"
) -> list:
    """List the product blocks published for a species and trade direction.

    Parameters
    ----------
    table : str
        Species key. Unknown species fall back to beef and veal.
    direction : str
        'imports' or 'exports'. Unknown directions fall back to imports.
    """
    from openbb_government_us.usda.utils.ers_livestock_and_meat_international_trade_data import (  # noqa: E501
        DIRECTIONS,
        SPECIES,
        afetch_products,
    )

    species = table if table in SPECIES else "beef_veal"
    trade = direction if direction in DIRECTIONS else "imports"
    return await afetch_products(species, trade)


router._api_router.add_api_route(
    path="/livestock_trade_products",
    endpoint=livestock_trade_products,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


@router.command(
    model="LivestockAndMeatInternationalTradeData",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get U.S. beef and veal exports by partner since 2015.",
            parameters={
                "table": "beef_veal",
                "direction": "exports",
                "start_year": 2015,
                "provider": "usda",
            },
        ),
        APIEx(
            description="Get monthly U.S. pork imports by partner.",
            parameters={
                "table": "pork",
                "direction": "imports",
                "frequency": "monthly",
                "provider": "usda",
            },
        ),
        APIEx(
            description="Get U.S. shell-egg exports by partner.",
            parameters={
                "table": "poultry_eggs",
                "direction": "exports",
                "product": "Shell-egg",
                "provider": "usda",
            },
        ),
    ],
)
async def livestock_and_meat_international_trade_data(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS livestock and meat international trade data - U.S. import and export trade in live cattle, hogs, sheep, and goats and in beef and veal, pork, lamb and mutton, poultry meat, and eggs, by trading partner, each pivoted to a wide layout with years as columns and the two cumulative year-to-date columns trailing."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


async def state_ag_trade_states(table: str = "exports_by_commodity") -> list:
    """List the states published for a state agricultural trade table.

    Parameters
    ----------
    table : str
        Table key. Unknown tables fall back to the calendar-year states.
    """
    from openbb_government_us.usda.utils.ers_state_agricultural_trade import (
        TABLE_LABELS,
        state_options,
    )

    return state_options(table if table in TABLE_LABELS else "exports_by_commodity")


router._api_router.add_api_route(
    path="/state_ag_trade_states",
    endpoint=state_ag_trade_states,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


@router.command(
    model="StateAgriculturalTrade",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get California's agricultural exports by commodity.",
            parameters={
                "table": "exports_by_commodity",
                "state": "California",
                "provider": "usda",
            },
        ),
        APIEx(
            description="Get total agricultural exports spread across the states.",
            parameters={
                "table": "exports_by_state",
                "commodity": "Total agricultural exports",
                "provider": "usda",
            },
        ),
        APIEx(
            description="Get Texas's top export commodities by fiscal year.",
            parameters={
                "table": "top_exports",
                "state": "Texas",
                "provider": "usda",
            },
        ),
        APIEx(
            description="Get California's top import commodities by fiscal year.",
            parameters={
                "table": "top_imports",
                "state": "California",
                "provider": "usda",
            },
        ),
    ],
)
async def state_agricultural_trade(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS state agricultural trade - state-level U.S. agricultural exports by commodity and by state on a calendar-year basis, and the top export and import commodities by state on a fiscal-year basis, each pivoted to a wide layout with the years in the rows."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="NormalizedPrices",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get the national prices-received and prices-paid"
            " indices (2011=100).",
            parameters={"table": "table2_national_indices", "provider": "usda"},
        ),
        APIEx(
            description="Get State-level normalized prices for the current"
            " report year.",
            parameters={"table": "table3_state_prices", "provider": "usda"},
        ),
    ],
)
async def normalized_prices(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS normalized prices - national and State-level normalized prices for crops, livestock, milk, poultry, eggs, and wool, plus national prices-received and prices-paid indices, each pivoted to a wide layout with report years, index years, or States in the columns."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="AgriculturalTradeMultipliers",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get the trade multipliers for soybeans and corn.",
            parameters={"commodity": "soybeans,corn", "provider": "usda"},
        ),
    ],
)
async def agricultural_trade_multipliers(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS agricultural trade multipliers - producer- and port-level output and employment multipliers per commodity, with export value, in a wide layout."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="AgriculturalAndFoodRdExpenditures",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get nominal (current-dollar) R&D expenditures since 2000.",
            parameters={
                "measure": "nominal",
                "start_year": 2000,
                "provider": "usda",
            },
        ),
    ],
)
async def agricultural_and_food_rd_expenditures(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS agricultural and food research and development (R&D) expenditures - public and private U.S. R&D spending in current and constant dollars with the R&D price index, pivoted to a wide layout with the R&D series as columns and years as rows."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


async def ge_crop_states(crop: str = "corn") -> list:
    """List the states published for a crop's genetically engineered adoption data.

    Parameters
    ----------
    crop : str
        Crop key. Unknown crops fall back to corn.
    """
    from openbb_government_us.usda.utils.ers_adoption_of_genetically_engineered_crops_in_the_united_states import (  # noqa: E501
        CROPS,
        state_options,
    )

    return state_options(crop if crop in CROPS else "corn")


router._api_router.add_api_route(
    path="/ge_crop_states",
    endpoint=ge_crop_states,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


@router.command(
    model="AdoptionOfGeneticallyEngineeredCropsInTheUnitedStates",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get U.S. corn GE adoption by trait since 2010.",
            parameters={
                "crop": "corn",
                "state": "United States",
                "start_year": 2010,
                "provider": "usda",
            },
        ),
        APIEx(
            description="Get Texas upland cotton GE adoption.",
            parameters={"crop": "cotton", "state": "Texas", "provider": "usda"},
        ),
        APIEx(
            description="Get U.S. herbicide-tolerant soybean adoption.",
            parameters={
                "crop": "soybeans",
                "state": "United States",
                "provider": "usda",
            },
        ),
    ],
)
async def adoption_of_genetically_engineered_crops(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS adoption of genetically engineered crops - the annual share of planted acres in genetically engineered corn, upland cotton, and soybean varieties, by trait and by State, pivoted to a wide layout with the GE traits as columns and years as rows."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="FoodSecurityInTheUnitedStates",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get food security prevalence by race and ethnicity"
            " since 2015.",
            parameters={
                "table": "by_characteristic",
                "category": "Race/ethnicity of households",
                "start_year": 2015,
                "provider": "usda",
            },
        ),
        APIEx(
            description="Get the by-State 3-year-average food insecurity prevalence.",
            parameters={"table": "by_state", "provider": "usda"},
        ),
    ],
)
async def food_security_in_the_united_states(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS food security in the United States - household and child food security, food insecurity, and very low food security prevalence by year, characteristic, and State, each pivoted to a wide layout."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


async def food_security_categories(table: str = "by_characteristic") -> list:
    """List the category options for a food-security table.

    Parameters
    ----------
    table : str
        Table key from FOOD_SECURITY_TABLES, e.g. 'by_characteristic'.
    """
    from openbb_government_us.usda.utils.ers_food_security_in_the_united_states import (
        FOOD_SECURITY_TABLES,
        afetch_categories,
    )

    if table not in FOOD_SECURITY_TABLES:
        table = "by_characteristic"
    return [{"label": name, "value": name} for name in await afetch_categories(table)]


router._api_router.add_api_route(
    path="/food_security_categories",
    endpoint=food_security_categories,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


async def food_availability_groups(data_system: str = "food_availability") -> list:
    """List the food-group files published for a data system."""
    from openbb_government_us.usda.utils.ers_food_availability_per_capita_data_system import (
        DATA_SYSTEMS,
        group_options,
    )

    return group_options(
        data_system if data_system in DATA_SYSTEMS else "food_availability"
    )


router._api_router.add_api_route(
    path="/food_availability_groups",
    endpoint=food_availability_groups,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


async def food_availability_commodities(
    data_system: str = "food_availability", food_group: str = "eggs"
) -> list:
    """List the commodity blocks published for a data system's file.

    Parameters
    ----------
    data_system : str
        Data system key. Unknown systems fall back to food availability.
    food_group : str
        Food-group file slug. Unknown slugs fall back to the system's first file.
    """
    from openbb_government_us.usda.utils.ers_food_availability_per_capita_data_system import (
        CATALOG,
        DATA_SYSTEMS,
        afetch_blocks,
    )

    system = data_system if data_system in DATA_SYSTEMS else "food_availability"
    groups = CATALOG[system]
    group = food_group if food_group in groups else next(iter(groups))
    return [
        {"label": block, "value": block} for block in await afetch_blocks(system, group)
    ]


router._api_router.add_api_route(
    path="/food_availability_commodities",
    endpoint=food_availability_commodities,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


@router.command(
    model="FoodAvailabilityPerCapitaDataSystem",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get the loss-adjusted rice availability budget since 1990.",
            parameters={
                "data_system": "loss_adjusted",
                "food_group": "grains",
                "commodity": "Rice: Per capita availability adjusted for loss",
                "start_year": 1990,
                "provider": "usda",
            },
        ),
        APIEx(
            description="Get the nutrient availability of the U.S. food supply since 2000.",
            parameters={
                "data_system": "nutrient",
                "food_group": "totals",
                "start_year": 2000,
                "provider": "usda",
            },
        ),
    ],
)
async def food_availability_per_capita(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS Food Availability (Per Capita) Data System - per capita food supply, loss-adjusted availability, and nutrient availability of the U.S. food supply, each file pivoted to a wide layout with the measures as columns and years as rows."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


async def fmap_food_items(group: str = "Dairy") -> list:
    """List the food items in a Tier-1 food group.

    Parameters
    ----------
    group : str
        Tier-1 food group. Unknown groups fall back to the default group.
    """
    from openbb_government_us.usda.utils.ers_food_at_home_monthly_area_prices import (
        DEFAULT_GROUP,
        GROUPS,
        item_options,
    )

    return item_options(group if group in GROUPS else DEFAULT_GROUP)


router._api_router.add_api_route(
    path="/fmap_food_items",
    endpoint=fmap_food_items,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


async def fmap_measures(table: str = "monthly_area_prices") -> list:
    """List the measures a Food-at-Home Monthly Area Prices table publishes.

    Parameters
    ----------
    table : str
        Table key. Unknown tables fall back to the default table.
    """
    from openbb_government_us.usda.utils.ers_food_at_home_monthly_area_prices import (
        DEFAULT_TABLE,
        FMAP_TABLES,
        measure_options,
    )

    return measure_options(table if table in FMAP_TABLES else DEFAULT_TABLE)


router._api_router.add_api_route(
    path="/fmap_measures",
    endpoint=fmap_measures,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


@router.command(
    model="FoodAtHomeMonthlyAreaPrices",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get the GEKS price index for whole milk across the 15 areas.",
            parameters={
                "item": "40000",
                "measure": "price_index_geks",
                "provider": "usda",
            },
        ),
        APIEx(
            description="Get the supplemental Fisher Ideal price index for fresh whole fruit since 2017.",
            parameters={
                "table": "supplemental_price_indexes",
                "group": "Fruit",
                "item": "30000",
                "measure": "price_index_fisher_ideal",
                "start_year": 2017,
                "provider": "usda",
            },
        ),
    ],
)
async def food_at_home_monthly_area_prices(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS Food-at-Home Monthly Area Prices - monthly unit values, purchases, store counts, and price indexes for a food item and measure, spread across the national, Census-region, and metropolitan areas."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


async def rural_urban_continuum_states(vintage: str = "2023") -> list:
    """List the states published for a rural-urban continuum code vintage.

    Parameters
    ----------
    vintage : str
        A vintage key. Unknown vintages fall back to the latest, 2023.
    """
    from openbb_government_us.usda.utils.ers_rural_urban_continuum_codes import (
        VINTAGES,
        afetch_states,
    )

    return await afetch_states(vintage if vintage in VINTAGES else "2023")


router._api_router.add_api_route(
    path="/rural_urban_continuum_states",
    endpoint=rural_urban_continuum_states,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


@router.command(
    model="RuralUrbanContinuumCodes",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get the 2023 Rural-Urban Continuum Codes for Wyoming.",
            parameters={"vintage": "2023", "state": "WY", "provider": "usda"},
        ),
        APIEx(
            description="Get the code-only 1974 Rural-Urban Continuum Codes"
            " for Alabama.",
            parameters={"vintage": "1974", "state": "AL", "provider": "usda"},
        ),
    ],
)
async def rural_urban_continuum_codes(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS Rural-Urban Continuum Codes - a county-level lookup classifying U.S. counties by metro/nonmetro status and degree of urbanization, published in vintages from 1974 to 2023."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


async def urban_influence_code_states(vintage: str = "2024") -> list:
    """List the states published for an Urban Influence Codes vintage.

    Parameters
    ----------
    vintage : str
        Vintage key. Unknown vintages fall back to the 2024 revision's states.
    """
    from openbb_government_us.usda.utils.ers_urban_influence_codes import (
        VINTAGES,
        state_options,
    )

    return state_options(vintage if vintage in VINTAGES else "2024")


router._api_router.add_api_route(
    path="/urban_influence_code_states",
    endpoint=urban_influence_code_states,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


@router.command(
    model="UrbanInfluenceCodes",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get the 2024 Urban Influence Codes for Alabama counties.",
            parameters={"vintage": "2024", "state": "AL", "provider": "usda"},
        ),
        APIEx(
            description="Get the 2003 codes with population density for Wyoming.",
            parameters={"vintage": "2003", "state": "WY", "provider": "usda"},
        ),
        APIEx(
            description="Get the 1993 vintage codes for the whole United States.",
            parameters={"vintage": "1993", "provider": "usda"},
        ),
    ],
)
async def urban_influence_codes(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS Urban Influence Codes - a county-level classification of every U.S. county by metropolitan status, size, and adjacency to metro and micro areas, published in the 1993, 2003, 2013, and 2024 vintages as a FIPS lookup table."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="CountyTypologyCodes",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get the 2025-edition county typology codes for Texas.",
            parameters={"vintage": "2025", "state": "TX", "provider": "usda"},
        ),
        APIEx(
            description="Get the 2004-edition county economic and policy types.",
            parameters={"vintage": "2004", "provider": "usda"},
        ),
    ],
)
async def county_typology_codes(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS County Typology Codes - county-level economic-dependence and policy typology classifications, published in successive vintages, as a one-row-per-county lookup table scoped by edition and state."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


async def ruca_states(table: str = "tract_2020") -> list:
    """List the states published for a rural-urban commuting area table.

    Parameters
    ----------
    table : str
        Table key. Unknown tables fall back to the 2020 census-tract states.
    """
    from openbb_government_us.usda.utils.ers_rural_urban_commuting_area_codes import (
        TABLE_LABELS,
        state_options,
    )

    return state_options(table if table in TABLE_LABELS else "tract_2020")


router._api_router.add_api_route(
    path="/ruca_states",
    endpoint=ruca_states,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


@router.command(
    model="RuralUrbanCommutingAreaCodes",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get the 2020 census-tract RUCA codes for Delaware.",
            parameters={"table": "tract_2020", "state": "DE", "provider": "usda"},
        ),
        APIEx(
            description="Get the 2010 ZIP-code RUCA codes for Vermont.",
            parameters={"table": "zip_2010", "state": "VT", "provider": "usda"},
        ),
        APIEx(
            description="Get the 1990 census-tract RUCA codes for Wyoming.",
            parameters={"table": "tract_1990", "state": "WY", "provider": "usda"},
        ),
    ],
)
async def rural_urban_commuting_area_codes(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS rural-urban commuting area (RUCA) codes - primary and secondary RUCA classification codes and descriptions for U.S. census tracts and ZIP codes across the 1990, 2000, 2010, and 2020 vintages, as a per-area lookup table scoped by state."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


async def far_zip_states(year: str = "2020") -> list:
    """List the states a frontier and remote area codes ZIP vintage publishes.

    Parameters
    ----------
    year : str
        Vintage key. Unknown vintages fall back to the latest vintage.
    """
    from openbb_government_us.usda.utils.ers_frontier_and_remote_area_codes import (
        FAR_ZIP_FILES,
        state_options,
    )

    return state_options(year if year in FAR_ZIP_FILES else "2020")


router._api_router.add_api_route(
    path="/far_zip_states",
    endpoint=far_zip_states,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


@router.command(
    model="FrontierAndRemoteAreaCodes",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get the 2020 frontier and remote area codes for"
            " California ZIP Codes.",
            parameters={"year": "2020", "state": "CA", "provider": "usda"},
        ),
        APIEx(
            description="Get the 2000 vintage for Massachusetts ZIP Codes.",
            parameters={"year": "2000", "state": "MA", "provider": "usda"},
        ),
    ],
)
async def frontier_and_remote_area_codes(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS frontier and remote (FAR) area codes - a ZIP-code geographic classification lookup at four FAR levels with grid population, land area, and population density, in a single-vintage lookup table scoped by State."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="CommutingZonesAndLaborMarketAreas",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get the 2020 commuting zones for Texas counties.",
            parameters={"vintage": "2020", "state": "Texas", "provider": "usda"},
        ),
        APIEx(
            description="Get the 2000 commuting-zone crosswalk for all counties.",
            parameters={"vintage": "2000", "provider": "usda"},
        ),
        APIEx(
            description="Get the 1980/1990 commuting zones and labor market areas.",
            parameters={"vintage": "1980_1990", "provider": "usda"},
        ),
    ],
)
async def commuting_zones_and_labor_market_areas(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS commuting zones and labor market areas - county-level commuting-zone and labor-market-area classifications for the 2020, preliminary 2020, 2000, and 1980/1990 vintages, as a FIPS lookup table selectable by vintage and filterable by state."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="NaturalAmenitiesScale",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get the natural amenities scale for Rhode Island counties.",
            parameters={"state": "RI", "provider": "usda"},
        ),
        APIEx(
            description="Get the natural amenities scale for California counties.",
            parameters={"state": "CA", "provider": "usda"},
        ),
    ],
)
async def natural_amenities_scale(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS natural amenities scale - a county-level measure of the physical characteristics that make a location a desirable place to live, combining six standardized climate, topography, and water-area components into a composite amenity scale and a 1-to-7 rank, as a one-row-per-county FIPS lookup scoped by state."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


async def poverty_area_measures_states(edition: str = "2025") -> list:
    """List the states published for a poverty area measures edition.

    Parameters
    ----------
    edition : str
        An edition key. Unknown editions fall back to the latest, 2025.
    """
    from openbb_government_us.usda.utils.ers_poverty_area_measures import (
        EDITIONS,
        afetch_states,
    )

    return await afetch_states(edition if edition in EDITIONS else "2025")


router._api_router.add_api_route(
    path="/poverty_area_measures_states",
    endpoint=poverty_area_measures_states,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


@router.command(
    model="PovertyAreaMeasures",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get the 2025-edition county poverty-area measures for"
            " Mississippi.",
            parameters={"edition": "2025", "state": "MS", "provider": "usda"},
        ),
        APIEx(
            description="Get the 2025-edition census-tract poverty-area measures"
            " for Mississippi.",
            parameters={
                "edition": "2025",
                "level": "tract",
                "state": "MS",
                "provider": "usda",
            },
        ),
    ],
)
async def poverty_area_measures(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS Poverty Area Measures - county- and census-tract-level poverty-area classification flags (high-poverty, extreme-poverty, persistent-poverty, and enduring-poverty), published in successive editions as a FIPS/tract lookup table scoped by edition, geography level, and state."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


async def area_road_ruggedness_states(vintage: str = "2020") -> list:
    """List the states an area and road ruggedness scales vintage publishes.

    Parameters
    ----------
    vintage : str
        Vintage key. Unknown vintages fall back to the latest vintage.
    """
    from openbb_government_us.usda.utils.ers_area_and_road_ruggedness_scales import (
        VINTAGE_CATALOG,
        state_options,
    )

    return state_options(vintage if vintage in VINTAGE_CATALOG else "2020")


router._api_router.add_api_route(
    path="/area_road_ruggedness_states",
    endpoint=area_road_ruggedness_states,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


@router.command(
    model="AreaAndRoadRuggednessScales",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get the 2020 area and road ruggedness scales for"
            " Colorado census tracts.",
            parameters={"vintage": "2020", "state": "CO", "provider": "usda"},
        ),
        APIEx(
            description="Get the 2010 vintage for West Virginia census tracts.",
            parameters={"vintage": "2010", "state": "WV", "provider": "usda"},
        ),
    ],
)
async def area_and_road_ruggedness_scales(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS area and road ruggedness scales - census-tract Area Ruggedness Scale (ARS) and Road Ruggedness Scale (RRS) classifications with terrain ruggedness statistics, rurality, and population, as a single-vintage geographic lookup table scoped by State."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="CostEstimatesOfFoodborneIllnesses",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get the mean cost of each health outcome, by pathogen.",
            parameters={
                "table": "health_outcome_cost",
                "provider": "usda",
            },
        ),
    ],
)
async def cost_estimates_of_foodborne_illnesses(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS Cost Estimates of Foodborne Illnesses - annual cases and the economic burden of major foodborne pathogens, by pathogen and by health outcome, in 2023 U.S. dollars."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="SnapPolicyDataSets",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get California SNAP policy variables since 2010.",
            parameters={"state": "CA", "start_year": 2010, "provider": "usda"},
        ),
        APIEx(
            description="Get Texas SNAP policy variables for 2019.",
            parameters={
                "state": "TX",
                "start_year": 2019,
                "end_year": 2019,
                "provider": "usda",
            },
        ),
    ],
)
async def snap_policy_data_sets(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS SNAP policy data sets - a selected State's monthly SNAP policy options from January 1996 to December 2020, with the forty-five broad-based categorical eligibility, recertification period, EBT issuance, interview-waiver, fingerprinting, noncitizen eligibility, online application, outreach spending, and vehicle-asset variables laid out as columns."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


async def intl_baseline_attributes(commodity: str = "Wheat") -> list:
    """List the measures published for an international baseline commodity.

    Parameters
    ----------
    commodity : str
        Commodity name. Unknown commodities fall back to wheat's measures.
    """
    from openbb_government_us.usda.utils.ers_international_baseline_data import (
        COMMODITIES,
        DEFAULT_COMMODITY,
        afetch_records,
        attributes_for_commodity,
    )

    name = commodity if commodity in COMMODITIES else DEFAULT_COMMODITY
    records = await afetch_records()
    return [
        {"label": attribute, "value": attribute}
        for attribute in attributes_for_commodity(records, name)
    ]


router._api_router.add_api_route(
    path="/intl_baseline_attributes",
    endpoint=intl_baseline_attributes,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


async def intl_baseline_countries(commodity: str = "Wheat") -> list:
    """List the countries and regions published for a baseline commodity.

    Parameters
    ----------
    commodity : str
        Commodity name. Unknown commodities fall back to wheat's areas.
    """
    from openbb_government_us.usda.utils.ers_international_baseline_data import (
        COMMODITIES,
        DEFAULT_COMMODITY,
        afetch_records,
        countries_for_commodity,
    )

    name = commodity if commodity in COMMODITIES else DEFAULT_COMMODITY
    records = await afetch_records()
    return [
        {"label": country, "value": country}
        for country in countries_for_commodity(records, name)
    ]


router._api_router.add_api_route(
    path="/intl_baseline_countries",
    endpoint=intl_baseline_countries,
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)


@router.command(
    model="InternationalBaselineData",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get projected corn exports by country and region since 2020.",
            parameters={
                "commodity": "Corn",
                "attribute": "Exports",
                "start_year": 2020,
                "provider": "usda",
            },
        ),
        APIEx(
            description="Get China's long-term wheat production projection.",
            parameters={
                "commodity": "Wheat",
                "attribute": "Production",
                "country": "China",
                "provider": "usda",
            },
        ),
    ],
)
async def international_baseline_data(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS International Baseline Data - long-term projections of area, yield, production, supply, use, and trade for grains, oilseeds, cotton, and livestock, pivoted to a wide layout with the countries and regions as columns and the crop or calendar years as rows."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="EatingAndHealthModuleAtus",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get the 2023 fast-food purchase frequency table.",
            parameters={
                "table": "fast_food_purchases",
                "year": "2023",
                "provider": "usda",
            },
        ),
        APIEx(
            description="Get 2022 food-related activity time by BMI group.",
            parameters={
                "table": "activities_by_bmi_group",
                "year": "2022",
                "provider": "usda",
            },
        ),
    ],
)
async def eating_and_health_module_atus(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS Eating and Health Module (ATUS) tables - time spent eating, drinking, in associated and secondary eating, preparing food, grocery shopping, and buying fast food, by demographic, food-security, and body-mass-index subgroups, each kept in its published wide layout for a selected survey release year."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="FoodConsumptionNutrientIntakesAndDietQuality",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get daily nutrient intake by food source for males.",
            parameters={
                "table": "2_nutrient_intake",
                "demographics": "Sex - Males",
                "provider": "usda",
            },
        ),
        APIEx(
            description="Get the standard error of the mean for the food-group"
            + " intake shares since 2003.",
            parameters={
                "table": "6_food_group_intake_share",
                "statistic": "se_of_mean",
                "start_year": 2003,
                "provider": "usda",
            },
        ),
        APIEx(
            description="Get the 2020-2025 recommended versus 2017-2018 actual"
            + " nutrient and food-group densities.",
            parameters={
                "table": "8_recommended_vs_actual_density",
                "provider": "usda",
            },
        ),
    ],
)
async def food_consumption_nutrient_intakes_and_diet_quality(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS food consumption, nutrient intakes, and diet quality - U.S. daily nutrient and food-group intake, share, and density by food source, population-subgroup sample sizes, and 2020-2025 recommended densities, from 1977 to 2018, each pivoted to a wide layout by survey cycle (Tables 1-7) or recommended-vs-actual density (Table 8)."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="ResourceRequirementsOfFoodDemand",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get the resources embodied in beef demand since 2015.",
            parameters={
                "table": "Xf1103",
                "start_year": 2015,
                "provider": "usda",
            },
        ),
        APIEx(
            description="Get the household home-kitchen and transportation resource use.",
            parameters={"table": "Xf3000", "provider": "usda"},
        ),
    ],
)
async def resource_requirements_of_food_demand(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS resource requirements of food demand - the employment, freshwater withdrawals, and energy use, total and by source, embodied across the U.S. food supply chain to meet final consumer demand for each food, beverage, and food-related category, pivoted to a wide layout with the resource-and-source measures as columns and year and supply-chain stage as rows."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="PurchaseToPlate",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get national average prices for grain products.",
            parameters={"food_group": "grains", "provider": "usda"},
        ),
    ],
)
async def purchase_to_plate(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS Purchase to Plate national average prices - estimated price per 100 edible grams for NHANES foods, pivoted to a price column per biennial survey cycle."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="GlobalFoodAssessment",
    examples=[
        APIEx(parameters={"provider": "usda"}),
        APIEx(
            description="Get the implied additional grain supply required across"
            " Sub-Saharan Africa's subregions.",
            parameters={
                "element": "Implied additional supply required",
                "region": "Sub-Saharan Africa",
                "provider": "usda",
            },
        ),
        APIEx(
            description="Get grain production for the Middle East and North Africa.",
            parameters={
                "element": "Grain production",
                "region": "Middle East and North Africa",
                "provider": "usda",
            },
        ),
    ],
)
async def global_food_assessment(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get ERS Global Food Assessment - grain food demand, other demand, total demand, production, and the implied additional supply required to close the food gap, pivoted to a wide layout with the subregions as columns and the base year and ten-year projection horizon as rows."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


if not COMMODITY_INSTALLED:

    @router.command(
        model="CommodityPsdData",
        examples=[
            APIEx(
                description="Get the World Crop Production Summary table.",
                parameters={"provider": "usda"},
            ),
            APIEx(
                description="Get all attributes for Coffee globally, for a single year.",
                parameters={
                    "provider": "usda",
                    "commodity": "coffee",
                    "start_year": 2025,
                    "end_year": 2025,
                },
            ),
            APIEx(
                description="Get historical production of corn in the US from 2020.",
                parameters={
                    "provider": "usda",
                    "commodity": "corn",
                    "country": "united_states",
                    "attribute": "production",
                    "start_year": 2020,
                },
            ),
        ],
    )
    async def psd_data(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get data tables and historical time series from the USDA FAS Production, Supply, and Distribution (PSD) Reports."""
        return await OBBject.from_query(OpenBBQuery(**locals()))

    @router.command(
        methods=["POST"],
        model="CommodityPsdReport",
        no_validate=True,
        widget_config={
            "name": "USDA FAS Commodity Production Supply & Distribution Reports",
            "description": "World Markets and Trade circulars released by the USDA"
            " Foreign Agricultural Service. Selecting a commodity offers every"
            " historical circular for it; with none selected, the latest circular"
            " for every commodity is offered.",
            "type": "multi_file_viewer",
            "refetchInterval": False,
            "gridData": {
                "w": 20,
                "h": 30,
            },
            "category": "Commodity",
            "subCategory": "Agriculture",
            "source": ["USDA", "FAS"],
            "params": [
                {
                    "paramName": "urls",
                    "type": "endpoint",
                    "optionsEndpoint": f"{api_prefix}/usda/psd_report_urls",
                    "optionsParams": {"commodity": "$commodity"},
                    "show": False,
                    "multiSelect": True,
                    "roles": ["fileSelector"],
                },
                {
                    "paramName": "commodity",
                    "label": "Commodity",
                    "description": "Leave empty for the latest circular from every"
                    " commodity.",
                    "value": None,
                    "type": "endpoint",
                    "optionsEndpoint": f"{api_prefix}/usda/psd_report_commodities",
                    "multiSelect": False,
                },
            ],
        },
        examples=[
            APIEx(
                parameters={
                    "provider": "usda",
                    "urls": [
                        "https://apps.fas.usda.gov/PSDOnline/Circulars/2026/01/Citrus.pdf"
                    ],
                }
            ),
            PythonEx(
                description="List the latest circular for every commodity, then download them.",
                code=[
                    "urls = [d['value'] for d in obb.usda.psd_report_urls()]",
                    "pdfs = obb.usda.psd_report(urls=urls)",
                ],
            ),
        ],
    )
    async def psd_report(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Download one, or more, USDA FAS commodity PSD circulars.

        This command returns only the results portion of the OBBject response.
        It contains a list of dictionaries where the base64 encoded content of the
        document is under the 'content' key.
        """
        response = await OBBject.from_query(OpenBBQuery(**locals()))
        return response.model_dump().get("results", {})

    @router.command(
        model="WeatherBulletin",
        no_validate=True,
        widget_config={"exclude": True},
        examples=[
            APIEx(
                description="Get weather bulletins for the current year.",
                parameters={"provider": "usda"},
            ),
            APIEx(
                description="Get weather bulletins for May 2023, week 2.",
                parameters={
                    "provider": "usda",
                    "year": 2023,
                    "month": 5,
                    "week": 2,
                },
            ),
            PythonEx(
                description="Get URLs for comparing versus 1 year ago and download the base64-encoded PDF content to memory.",
                code=[
                    "from datetime import datetime",
                    "urls = []",
                    "for year in [datetime.now().year, datetime.now().year - 1]:",
                    "    urls.append(obb.usda.weather_bulletins(year=year, month=5, week=2)[0]['value'])",
                    "pdfs = obb.usda.weather_bulletins_download(urls=urls)",
                ],
            ),
        ],
    )
    async def weather_bulletins(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get current and historical weather bulletins with their PDF links.

        This command returns only the results portion of the OBBject response.
        It contains a list of dictionaries where each dictionary has 'label' and 'value' keys.
        """
        response = await OBBject.from_query(OpenBBQuery(**locals()))
        return response.model_dump().get("results", {})

    @router.command(
        methods=["POST"],
        model="WeatherBulletinDownload",
        no_validate=True,
        widget_config={
            "name": "USDA Weather & Crop Bulletin",
            "description": "Weekly Weather and Crop Bulletin from the USDA.",
            "type": "multi_file_viewer",
            "refetchInterval": False,
            "gridData": {
                "w": 20,
                "h": 30,
            },
            "category": "Commodity",
            "subCategory": "Agriculture",
            "source": ["USDA", "WAOB"],
            "params": [
                {
                    "paramName": "urls",
                    "type": "endpoint",
                    "optionsEndpoint": f"{api_prefix}/usda/weather_bulletins",
                    "optionsParams": {
                        "year": "$year",
                        "month": "$month",
                        "week": "$week",
                        "provider": "usda",
                    },
                    "show": False,
                    "multiSelect": True,
                    "roles": ["fileSelector"],
                },
                {
                    "paramName": "year",
                    "type": "number",
                    "label": "Year",
                    "value": datetime.now().year,
                    "options": [
                        {"value": year, "label": str(year)}
                        for year in sorted(
                            list(range(1974, datetime.now().year + 1)),
                            reverse=True,
                        )
                    ],
                },
                {
                    "paramName": "month",
                    "type": "number",
                    "label": "Month",
                    "value": None,
                    "options": [
                        {"value": i, "label": month}
                        for i, month in enumerate(
                            [
                                "January",
                                "February",
                                "March",
                                "April",
                                "May",
                                "June",
                                "July",
                                "August",
                                "September",
                                "October",
                                "November",
                                "December",
                            ],
                            start=1,
                        )
                    ]
                    + [{"value": None, "label": "All Months"}],
                },
                {
                    "paramName": "week",
                    "type": "number",
                    "label": "Week",
                    "value": None,
                    "options": [
                        {"value": week, "label": str(week)} for week in range(1, 6)
                    ]
                    + [{"value": None, "label": "All Weeks"}],
                },
                {
                    "paramName": "provider",
                    "show": False,
                    "value": "usda",
                    "type": "text",
                    "options": [{"value": "usda", "label": "usda"}],
                },
            ],
        },
        examples=[
            APIEx(
                parameters={
                    "provider": "usda",
                    "urls": [
                        "https://esmis.nal.usda.gov/sites/default/release-files/cj82k728n/9w033w568/x059f4232/wwcb0125.pdf"
                    ],
                }
            ),
        ],
    )
    async def weather_bulletins_download(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Download one, or more, weather bulletin documents.

        This command returns only the results portion of the OBBject response.
        It contains a list of dictionaries where the base64 encoded content of the document is under the 'content' key.
        """
        response = await OBBject.from_query(OpenBBQuery(**locals()))
        return response.model_dump().get("results", {})
