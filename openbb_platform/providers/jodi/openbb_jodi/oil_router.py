"""JODI Oil Router."""

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.example import APIEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query as OpenBBQuery
from openbb_core.app.router import Router

router = Router(
    prefix="/oil",
    description="JODI-Oil World Database."
    + " Monthly data from January 2002 to the most recent month.",
)


@router.command(
    model="JodiOilBalance",
    examples=[
        APIEx(
            description="Get the United States crude oil balance - one column per questionnaire flow.",
            parameters={"provider": "jodi"},
        ),
        APIEx(
            description="Get India's gasoline balance, in thousand metric tons.",
            parameters={
                "provider": "jodi",
                "country": "india",
                "product": "gasoline",
                "unit": "ktons",
                "start_date": "2020-01-01",
            },
        ),
    ],
)
async def balance(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get a country's monthly petroleum balance for one product - production, trade, stocks, and refinery activity, one column per flow of the JODI questionnaire."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="JodiOilProduction",
    examples=[
        APIEx(
            description="Get monthly crude oil production - one column per reporting country.",
            parameters={"provider": "jodi"},
        ),
        APIEx(
            description="Compare crude oil production in Saudi Arabia, Iraq, and the United States.",
            parameters={
                "provider": "jodi",
                "country": "saudi_arabia,iraq,united_states",
                "start_date": "2020-01-01",
            },
        ),
    ],
)
async def production(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Monthly production of a primary petroleum product - one column per reporting country."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="JodiOilDemand",
    examples=[
        APIEx(
            description="Get monthly total petroleum products demand - one column per reporting country.",
            parameters={"provider": "jodi"},
        ),
        APIEx(
            description="Compare gasoline demand in the United States, China, and India.",
            parameters={
                "provider": "jodi",
                "country": "united_states,china,india",
                "product": "gasoline",
                "start_date": "2020-01-01",
            },
        ),
    ],
)
async def demand(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Monthly demand for a refined petroleum product - one column per reporting country."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="JodiOilDemandByProduct",
    examples=[
        APIEx(
            description="Get monthly United States demand - one column per refined product.",
            parameters={"provider": "jodi"},
        ),
        APIEx(
            description="Get Japan's demand barrel, in thousand barrels per day.",
            parameters={
                "provider": "jodi",
                "country": "japan",
                "unit": "kbd",
                "start_date": "2020-01-01",
            },
        ),
    ],
)
async def demand_by_product(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get a country's monthly petroleum demand - one column per refined product, in published order."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="JodiOilImports",
    examples=[
        APIEx(
            description="Get monthly crude oil imports - one column per reporting country.",
            parameters={"provider": "jodi"},
        ),
        APIEx(
            description="Compare crude oil imports of China, India, and South Korea.",
            parameters={
                "provider": "jodi",
                "country": "china,india,south_korea",
                "start_date": "2020-01-01",
            },
        ),
    ],
)
async def imports(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Monthly imports of a petroleum product - one column per reporting country."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="JodiOilExports",
    examples=[
        APIEx(
            description="Get monthly crude oil exports - one column per reporting country.",
            parameters={"provider": "jodi"},
        ),
        APIEx(
            description="Compare fuel oil exports from Russia and Saudi Arabia.",
            parameters={
                "provider": "jodi",
                "country": "russia,saudi_arabia",
                "product": "fuel_oil",
                "start_date": "2020-01-01",
            },
        ),
    ],
)
async def exports(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Monthly exports of a petroleum product - one column per reporting country."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="JodiOilStocks",
    examples=[
        APIEx(
            description="Get monthly crude oil closing stock levels - one column per reporting country.",
            parameters={"provider": "jodi"},
        ),
        APIEx(
            description="Compare gasoline stocks in the United States and Japan, in thousand barrels.",
            parameters={
                "provider": "jodi",
                "country": "united_states,japan",
                "product": "gasoline",
                "unit": "kbbl",
                "start_date": "2020-01-01",
            },
        ),
    ],
)
async def stocks(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Monthly closing stock levels of a petroleum product - one column per reporting country."""
    return await OBBject.from_query(OpenBBQuery(**locals()))
