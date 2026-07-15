"""JODI Gas Router."""

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
    prefix="/gas",
    description="JODI-Gas World Database."
    + " Monthly data from January 2009 to the most recent month.",
)


@router.command(
    model="JodiGasBalance",
    examples=[
        APIEx(
            description="Get the United States natural gas balance - one column per questionnaire flow.",
            parameters={"provider": "jodi"},
        ),
        APIEx(
            description="Get Norway's natural gas balance, in terajoules.",
            parameters={
                "provider": "jodi",
                "country": "norway",
                "unit": "tj",
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
    """Get a country's monthly natural gas balance - production, pipeline and LNG trade, deliveries, and stocks, one column per flow of the JODI questionnaire."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="JodiGasProduction",
    examples=[
        APIEx(
            description="Get monthly natural gas production - one column per reporting country.",
            parameters={"provider": "jodi"},
        ),
        APIEx(
            description="Compare natural gas production in the United States, Qatar, and Norway.",
            parameters={
                "provider": "jodi",
                "country": "united_states,qatar,norway",
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
    """Monthly natural gas production - one column per reporting country."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="JodiGasDemand",
    examples=[
        APIEx(
            description="Get monthly natural gas demand - one column per reporting country.",
            parameters={"provider": "jodi"},
        ),
        APIEx(
            description="Compare natural gas demand in Germany, France, and Italy.",
            parameters={
                "provider": "jodi",
                "country": "germany,france,italy",
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
    """Monthly natural gas demand, as gross inland deliveries - one column per reporting country."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="JodiGasImports",
    examples=[
        APIEx(
            description="Get monthly natural gas imports - one column per reporting country.",
            parameters={"provider": "jodi"},
        ),
        APIEx(
            description="Compare LNG imports of Japan, China, and South Korea.",
            parameters={
                "provider": "jodi",
                "country": "japan,china,south_korea",
                "flow": "lng",
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
    """Monthly natural gas imports - total, pipeline, or LNG - one column per reporting country."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="JodiGasExports",
    examples=[
        APIEx(
            description="Get monthly natural gas exports - one column per reporting country.",
            parameters={"provider": "jodi"},
        ),
        APIEx(
            description="Compare LNG exports from the United States, Qatar, and Australia.",
            parameters={
                "provider": "jodi",
                "country": "united_states,qatar,australia",
                "flow": "lng",
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
    """Monthly natural gas exports - total, pipeline, or LNG - one column per reporting country."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="JodiGasStocks",
    examples=[
        APIEx(
            description="Get monthly natural gas closing stock levels - one column per reporting country.",
            parameters={"provider": "jodi"},
        ),
        APIEx(
            description="Compare natural gas stocks in Germany, France, and the Netherlands.",
            parameters={
                "provider": "jodi",
                "country": "germany,france,netherlands",
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
    """Monthly natural gas closing stock levels - one column per reporting country."""
    return await OBBject.from_query(OpenBBQuery(**locals()))
