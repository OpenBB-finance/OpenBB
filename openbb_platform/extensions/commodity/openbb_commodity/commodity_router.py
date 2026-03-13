"""The Commodity router."""

# pylint: disable=unused-argument,unused-import
# flake8: noqa: F401

# pylint: disable=unused-argument

from datetime import datetime

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.example import APIEx, PythonEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router
from openbb_core.app.service.system_service import SystemService

from openbb_commodity.price.price_router import router as price_router

router = Router(prefix="", description="Commodity market data.")
router.include_router(price_router)
api_prefix = SystemService().system_settings.api_settings.prefix


@router.command(
    model="PetroleumStatusReport",
    examples=[
        APIEx(
            description="Get the EIA's Weekly Petroleum Status Report.",
            parameters={"provider": "eia"},
        ),
        APIEx(
            description="Select the category of data, and filter for a specific table within the report.",
            parameters={
                "category": "weekly_estimates",
                "table": "imports",
                "provider": "eia",
            },
        ),
    ],
)
async def petroleum_status_report(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """EIA Weekly Petroleum Status Report."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="ShortTermEnergyOutlook",
    examples=[
        APIEx(
            description="Get the EIA's Short Term Energy Outlook.",
            parameters={"provider": "eia"},
        ),
        APIEx(
            description="Select the specific table of data from the STEO. Table 03d is World Crude Oil Production.",
            parameters={
                "table": "03d",
                "provider": "eia",
            },
        ),
    ],
)
async def short_term_energy_outlook(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Monthly short term (18 month) projections using EIA's STEO model.

    Source: www.eia.gov/steo/
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="CommodityPsdData",
    examples=[
        APIEx(
            description="Get the World Crop Production Summary table.",
            parameters={
                "provider": "government_us",
            },
        ),
        APIEx(
            description="Get the current Corn World Trade table from the PDS report.",
            parameters={
                "provider": "government_us",
                "report_id": "corn_world_trade",
            },
        ),
        APIEx(
            description="Get all attributes for Coffee globally, for a single year.",
            parameters={
                "provider": "government_us",
                "commodity": "coffee",
                "start_year": 2025,
                "end_year": 2025,
            },
        ),
        APIEx(
            description="Compare Brazil coffee exports versus the world from 2010 to present.",
            parameters={
                "provider": "government_us",
                "commodity": "coffee",
                "country": "brazil",
                "attribute": "exports",
                "aggregate_regions": True,
                "start_year": 2010,
            },
        ),
        APIEx(
            description="Get historical production of corn in the US from 2020.",
            parameters={
                "provider": "government_us",
                "commodity": "corn",
                "country": "united_states",
                "attribute": "production",
                "start_year": 2020,
            },
        ),
        APIEx(
            description="Get regional aggregates for wheat beginning and ending stocks from 2020.",
            parameters={
                "provider": "government_us",
                "commodity": "wheat",
                "country": "world",
                "attribute": "beginning_stocks,ending_stocks",
                "aggregate_regions": True,
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
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="CommodityPsdReport",
    no_validate=True,
    widget_config={
        "name": "USDA FAS Commodity Production Supply & Distribution Reports",
        "description": "Monthly publications released by the USDA Foreign Agriculture Service.",
        "type": "pdf",
        "refetchInterval": False,
        "gridData": {
            "w": 20,
            "h": 30,
        },
        "category": "Commodity",
        "subCategory": "Agriculture",
        "source": ["USDA", "FAS"],
    },
    examples=[
        APIEx(
            parameters={
                "provider": "government_us",
                "commodity": "sugar",
                "year": 2022,
                "month": 5,
            }
        ),
        APIEx(
            description="Get the PSD report for coffee for March 2023.",
            parameters={
                "provider": "government_us",
                "commodity": "coffee",
                "year": 2023,
                "month": 3,
            },
        ),
    ],
)
async def psd_report(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Agriculture commodity production, supply, and distribution PDF reports (World Agricultural Outlook).

    This command returns only the results portion of the OBBject response.
    It contains a dictionary where the PDF content is base64 encoded under the 'content' key.
    """
    response = await OBBject.from_query(Query(**locals()))
    return response.model_dump().get("results", {})


@router.command(
    model="WeatherBulletin",
    no_validate=True,
    widget_config={"exclude": True},
    examples=[
        APIEx(
            description="Get weather bulletins for the current year.",
            parameters={
                "provider": "government_us",
            },
        ),
        APIEx(
            description="Get weather bulletins for May 2023, week 2.",
            parameters={
                "provider": "government_us",
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
                "    urls.append(obb.commodity.weather_bulletins(year=year, month=5, week=2)[0]['value'])",
                "pdfs = obb.commodity.weather_bulletins_download(urls=urls)",
                "# PDFs are now in a list where each item has 'content' and 'data_format' keys",
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

    Use this endpoint to programmatically access the list of available weather bulletins.
    Suitable for dropdown selections in a UI.
    """
    response = await OBBject.from_query(Query(**locals()))
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
                "optionsEndpoint": f"{api_prefix}/commodity/weather_bulletins",
                "optionsParams": {
                    "year": "$year",
                    "month": "$month",
                    "week": "$week",
                    "provider": "government_us",
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
                "options": [{"value": week, "label": str(week)} for week in range(1, 6)]
                + [{"value": None, "label": "All Weeks"}],
            },
            {
                "paramName": "provider",
                "show": False,
                "value": "government_us",
                "type": "text",
                "options": [{"value": "government_us", "label": "government_us"}],
            },
        ],
    },
    examples=[
        APIEx(
            parameters={
                "provider": "government_us",
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
    response = await OBBject.from_query(Query(**locals()))
    return response.model_dump().get("results", {})
