# pylint: disable=W0613:unused-argument

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router
from pydantic import BaseModel

router = Router(prefix="")


@router.command(model="TreasuryRates")
def treasury(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Treasury Rates. Treasury rates data."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="USYieldCurve")
def ycrv(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:  # type: ignore
    """US Yield Curve. Get United States yield curve."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="SOFR")
def sofr(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:  # type: ignore
    """
    Secured Overnight Financing Rate.
    The Secured Overnight Financing Rate (SOFR) is a broad measure of the cost of
    borrowing cash overnight collateralized by Treasury securities.
    """
    return OBBject(results=Query(**locals()).execute())


@router.command(model="ESTR")
def estr(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:  # type: ignore
    """
    Euro Short-Term Rate.
    The euro short-term rate (€STR) reflects the wholesale euro unsecured overnight borrowing costs of banks located in
    the euro area. The €STR is published on each TARGET2 business day based on transactions conducted and settled on
    the previous TARGET2 business day (the reporting date “T”) with a maturity date of T+1 which are deemed to have been
    executed at arm’s length and thus reflect market rates in an unbiased way."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="SONIA")
def sonia(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:  # type: ignore
    """
    Sterling Overnight Index Average.
    SONIA (Sterling Overnight Index Average) is an important interest rate benchmark. SONIA is based on actual
    transactions and reflects the average of the interest rates that banks pay to borrow sterling overnight from other
    financial institutions and other institutional investors."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="AMERIBOR")
def ameribor(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:  # type: ignore
    """
    Ameribor.
    Ameribor (short for the American interbank offered rate) is a benchmark interest rate that reflects the true cost of
    short-term interbank borrowing. This rate is based on transactions in overnight unsecured loans conducted on the
    American Financial Exchange (AFX)."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="FEDFUNDS")
def fed(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:  # type: ignore
    """
    Fed Funds Rate.
    Get Effective Federal Funds Rate data. A bank rate is the interest rate a nation's central bank charges to its
    domestic banks to borrow money. The rates central banks charge are set to stabilize the economy. In the
    United States, the Federal Reserve System's Board of Governors set the bank rate, also known as the discount rate.
    """
    return OBBject(results=Query(**locals()).execute())


@router.command(model="PROJECTIONS")
def projections(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:  # type: ignore
    """
    Fed Funds Rate Projections.
    The projections for the federal funds rate are the value of the midpoint of the
    projected appropriate target range for the federal funds rate or the projected
    appropriate target level for the federal funds rate at the end of the specified
    calendar year or over the longer run.
    """
    return OBBject(results=Query(**locals()).execute())


@router.command(model="IORB")
def iorb(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:  # type: ignore
    """
    Interest on Reserve Balances.
    Get Interest Rate on Reserve Balances data A bank rate is the interest rate a nation's central bank charges to its
    domestic banks to borrow money. The rates central banks charge are set to stabilize the economy. In the
    United States, the Federal Reserve System's Board of Governors set the bank rate, also known as the discount rate.
    """
    return OBBject(results=Query(**locals()).execute())


@router.command(model="DiscountWindowPrimaryCreditRate")
def dwpcr(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """
    Discount Window Primary Credit Rate.
    A bank rate is the interest rate a nation's central bank charges to its domestic banks to borrow money.
    The rates central banks charge are set to stabilize the economy.
    In the United States, the Federal Reserve System's Board of Governors set the bank rate,
    also known as the discount rate.
    """
    return OBBject(results=Query(**locals()).execute())


@router.command(model="EuropeanCentralBankInterestRates")
def ecb_interest_rates(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """
    European Central Bank Interest Rates.
    The Governing Council of the ECB sets the key interest rates for the euro area:

    - The interest rate on the main refinancing operations (MRO), which provide
    the bulk of liquidity to the banking system.
    - The rate on the deposit facility, which banks may use to make overnight deposits with the Eurosystem.
    - The rate on the marginal lending facility, which offers overnight credit to banks from the Eurosystem.
    """
    return OBBject(results=Query(**locals()).execute())


@router.command(model="ICEBofA")
def ice_bofa(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """
    ICE BofA US Corporate Bond Indices.
    The ICE BofA US Corporate Index tracks the performance of US dollar denominated investment grade corporate debt
    publicly issued in the US domestic market. Qualifying securities must have an investment grade rating (based on an
    average of Moody’s, S&P and Fitch), at least 18 months to final maturity at the time of issuance, at least one year
    remaining term to final maturity as of the rebalancing date, a fixed coupon schedule and a minimum amount
    outstanding of $250 million. The ICE BofA US Corporate Index is a component of the US Corporate Master Index.
    """
    return OBBject(results=Query(**locals()).execute())


@router.command(model="MoodyCorporateBondIndex")
def moody(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """
    Moody Corporate Bond Index.
    Moody's Aaa and Baa are investment bonds that acts as an index of
    the performance of all bonds given an Aaa or Baa rating by Moody's Investors Service respectively.
    These corporate bonds often are used in macroeconomics as an alternative to the federal ten-year
    Treasury Bill as an indicator of the interest rate.
    """
    return OBBject(results=Query(**locals()).execute())
