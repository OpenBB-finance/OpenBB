"""Price router for Currency."""

# pylint: disable=unused-argument
from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router

router = Router(prefix="/price")


# pylint: disable=unused-argument
@router.command(
    model="CurrencyHistorical",
    examples=[
        "# Filter historical data with specific start and end date.",
        "obb.currency.price.historical(symbol='EURUSD', start_date='2023-01-01', end_date='20213-12-31')",
        "# Get data with different granularity.",
        "obb.currency.price.historical(symbol='EURUSD', interval='15m', provider='polygon')",
    ],
)
async def historical(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """
    Currency Historical Price. Currency historical data.

    Currency historical prices refer to the past exchange rates of one currency against
    another over a specific period.
    This data provides insight into the fluctuations and trends in the foreign exchange market,
    helping analysts, traders, and economists understand currency performance,
    evaluate economic health, and make predictions about future movements.
    """
    return await OBBject.from_query(Query(**locals()))
