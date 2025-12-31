"""The Commodity router."""

# pylint: disable=unused-argument,unused-import
# flake8: noqa: F401

# pylint: disable=unused-argument

from datetime import datetime

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.example import APIEx
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
    model="CommodityPsdReport",
    no_validate=True,
    widget_config={
        "name": "USDA FAS Commodity Production Supply & Demand Report",
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
    """Agriculture commodity production, supply, and demand PDF reports (World Agricultural Outlook).

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
            parameters={
                "provider": "government_us",
            }
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
