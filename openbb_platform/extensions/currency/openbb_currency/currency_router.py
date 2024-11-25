"""The Currency router."""

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

from openbb_currency.price.price_router import router as price_router

router = Router(prefix="", description="Foreign exchange (FX) market data.")
router.include_router(price_router)


# pylint: disable=unused-argument
@router.command(
    model="CurrencyPairs",
    examples=[
        APIEx(parameters={"provider": "fmp"}),
        APIEx(
            description="Search for 'EUR' currency pair using 'intrinio' as provider.",
            parameters={"provider": "intrinio", "query": "EUR"},
        ),
        APIEx(
            description="Search for terms  using 'polygon' as provider.",
            parameters={"provider": "polygon", "query": "EUR"},
        ),
    ],
)
async def search(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Currency Search.

    Search available currency pairs.
    Currency pairs are the national currencies from two countries coupled for trading on
    the foreign exchange (FX) marketplace.
    Both currencies will have exchange rates on which the trade will have its position basis.
    All trading within the forex market, whether selling, buying, or trading, will take place through currency pairs.
    (ref: Investopedia)
    Major currency pairs include pairs such as EUR/USD, USD/JPY, GBP/USD, etc.
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="CurrencyReferenceRates",
    examples=[APIEx(parameters={"provider": "ecb"})],
)
async def reference_rates(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get current, official, currency reference rates.

    Foreign exchange reference rates are the exchange rates set by a major financial institution or regulatory body,
    serving as a benchmark for the value of currencies around the world.
    These rates are used as a standard to facilitate international trade and financial transactions,
    ensuring consistency and reliability in currency conversion.
    They are typically updated on a daily basis and reflect the market conditions at a specific time.
    Central banks and financial institutions often use these rates to guide their own exchange rates,
    impacting global trade, loans, and investments.
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="CurrencySnapshots",
    examples=[
        APIEx(parameters={"provider": "fmp"}),
        APIEx(
            description="Get exchange rates from USD and XAU to EUR, JPY, and GBP using 'fmp' as provider.",
            parameters={
                "provider": "fmp",
                "base": "USD,XAU",
                "counter_currencies": "EUR,JPY,GBP",
                "quote_type": "indirect",
            },
        ),
    ],
)
async def snapshots(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Snapshots of currency exchange rates from an indirect or direct perspective of a base currency."""
    return await OBBject.from_query(Query(**locals()))
