"""The Commodity router."""

# pylint: disable=unused-argument,unused-import
# flake8: noqa: F401

# pylint: disable=unused-argument

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

from openbb_commodity.price.price_router import router as price_router

router = Router(prefix="", description="Commodity market data.")
router.include_router(price_router)


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
