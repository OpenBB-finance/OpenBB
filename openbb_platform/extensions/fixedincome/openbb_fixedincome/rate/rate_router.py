"""Fixed Income Rate Router."""

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

router = Router(prefix="/rate")

# pylint: disable=unused-argument


@router.command(
    model="Ameribor",
    examples=[
        APIEx(parameters={"provider": "fred"}),
        APIEx(
            description="The change from one year ago is applied with the transform parameter.",
            parameters={"maturity": "all", "transform": "pc1", "provider": "fred"},
        ),
    ],
)
async def ameribor(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:  # type: ignore
    """AMERIBOR.

    AMERIBOR (short for the American interbank offered rate) is a benchmark interest rate that reflects the true cost of
    short-term interbank borrowing. This rate is based on transactions in overnight unsecured loans conducted on the
    American Financial Exchange (AFX).
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="SONIA",
    examples=[
        APIEx(parameters={"provider": "fred"}),
        APIEx(parameters={"parameter": "total_nominal_value", "provider": "fred"}),
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
    model="SOFR",
    examples=[
        APIEx(parameters={"provider": "fred"}),
    ],
)
async def sofr(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:  # type: ignore
    """Secured Overnight Financing Rate.

    The Secured Overnight Financing Rate (SOFR) is a broad measure of the cost of
    borrowing cash overnight collateralizing by Treasury securities.
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="IORB",
    examples=[APIEx(parameters={"provider": "fred"})],
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
    model="FederalFundsRate",
    examples=[
        APIEx(parameters={"provider": "fred"}),
        APIEx(parameters={"effr_only": True, "provider": "fred"}),
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
    domestic banks to borrow money. The rates central banks charge are set to stabilize the economy.
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="PROJECTIONS",
    examples=[
        APIEx(parameters={"provider": "fred"}),
        APIEx(parameters={"long_run": True, "provider": "fred"}),
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
    model="EuroShortTermRate",
    examples=[
        APIEx(parameters={"provider": "fred"}),
        APIEx(parameters={"transform": "ch1", "provider": "fred"}),
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
    executed at arm's length and thus reflect market rates in an unbiased way.
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="EuropeanCentralBankInterestRates",
    examples=[
        APIEx(parameters={"provider": "fred"}),
        APIEx(parameters={"interest_rate_type": "refinancing", "provider": "fred"}),
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
    examples=[
        APIEx(parameters={"provider": "fred"}),
        APIEx(
            parameters={
                "start_date": "2023-02-01",
                "end_date": "2023-05-01",
                "provider": "fred",
            }
        ),
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


@router.command(
    model="OvernightBankFundingRate",
    examples=[APIEx(parameters={"provider": "fred"})],
)
async def overnight_bank_funding(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:  # type: ignore
    """Overnight Bank Funding.

    For the United States, the overnight bank funding rate (OBFR) is calculated as a volume-weighted median of
    overnight federal funds transactions and Eurodollar transactions reported in the
    FR 2420 Report of Selected Money Market Rates.
    """
    return await OBBject.from_query(Query(**locals()))
