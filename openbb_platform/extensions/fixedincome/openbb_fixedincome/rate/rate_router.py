"""Fixed Income Rate Router."""

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router

router = Router(prefix="/rate")

# pylint: disable=unused-argument


@router.command(
    model="AMERIBOR",
    exclude_auto_examples=True,
    examples=[
        'obb.fixedincome.rate.ameribor(parameter="30_day_ma").to_df()',
    ],
)
async def ameribor(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:  # type: ignore
    """Ameribor.

    Ameribor (short for the American interbank offered rate) is a benchmark interest rate that reflects the true cost of
    short-term interbank borrowing. This rate is based on transactions in overnight unsecured loans conducted on the
    American Financial Exchange (AFX).
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="SONIA",
    exclude_auto_examples=True,
    examples=[
        'obb.fixedincome.rate.sonia(parameter="total_nominal_value")',
    ],
)
async def sonia(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:  # type: ignore
    """Sterling Overnight Index Average.

    SONIA (Sterling Overnight Index Average) is an important interest rate benchmark. SONIA is based on actual
    transactions and reflects the average of the interest rates that banks pay to borrow sterling overnight from other
    financial institutions and other institutional investors.
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="IORB",
    exclude_auto_examples=True,
    examples=[
        "obb.fixedincome.rate.iorb()",
    ],
)
async def iorb(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:  # type: ignore
    """Interest on Reserve Balances.

    Get Interest Rate on Reserve Balances data A bank rate is the interest rate a nation's central bank charges to its
    domestic banks to borrow money. The rates central banks charge are set to stabilize the economy. In the
    United States, the Federal Reserve System's Board of Governors set the bank rate, also known as the discount rate.
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FEDFUNDS",
    exclude_auto_examples=True,
    examples=[
        'obb.fixedincome.rate.effr(parameter="daily", provider="fred").to_df()',
    ],
)
async def effr(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:  # type: ignore
    """Fed Funds Rate.

    Get Effective Federal Funds Rate data. A bank rate is the interest rate a nation's central bank charges to its
    domestic banks to borrow money. The rates central banks charge are set to stabilize the economy. In the
    United States, the Federal Reserve System's Board of Governors set the bank rate, also known as the discount rate.
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="PROJECTIONS",
    exclude_auto_examples=True,
    examples=[
        "obb.fixedincome.rate.effr_forecast(long_run=True)",
    ],
)
async def effr_forecast(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:  # type: ignore
    """Fed Funds Rate Projections.

    The projections for the federal funds rate are the value of the midpoint of the
    projected appropriate target range for the federal funds rate or the projected
    appropriate target level for the federal funds rate at the end of the specified
    calendar year or over the longer run.
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="ESTR",
    exclude_auto_examples=True,
    examples=[
        'obb.fixedincome.rate.estr(parameter="number_of_active_banks")',
    ],
)
async def estr(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:  # type: ignore
    """Euro Short-Term Rate.

    The euro short-term rate (€STR) reflects the wholesale euro unsecured overnight borrowing costs of banks located in
    the euro area. The €STR is published on each TARGET2 business day based on transactions conducted and settled on
    the previous TARGET2 business day (the reporting date “T”) with a maturity date of T+1 which are deemed to have been
    executed at arm’s length and thus reflect market rates in an unbiased way.
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="EuropeanCentralBankInterestRates",
    exclude_auto_examples=True,
    examples=[
        'obb.fixedincome.rate.ecb(interest_rate_type="refinancing")',
    ],
)
async def ecb(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """European Central Bank Interest Rates.

    The Governing Council of the ECB sets the key interest rates for the euro area:

    - The interest rate on the main refinancing operations (MRO), which provide
    the bulk of liquidity to the banking system.
    - The rate on the deposit facility, which banks may use to make overnight deposits with the Eurosystem.
    - The rate on the marginal lending facility, which offers overnight credit to banks from the Eurosystem.
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="DiscountWindowPrimaryCreditRate",
    exclude_auto_examples=True,
    examples=[
        'obb.fixedincome.rate.dpcredit(start_date="2023-02-01", end_date="2023-05-01").to_df()',
    ],
)
async def dpcredit(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Discount Window Primary Credit Rate.

    A bank rate is the interest rate a nation's central bank charges to its domestic banks to borrow money.
    The rates central banks charge are set to stabilize the economy.
    In the United States, the Federal Reserve System's Board of Governors set the bank rate,
    also known as the discount rate.
    """
    return await OBBject.from_query(Query(**locals()))
