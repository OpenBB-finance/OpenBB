# pylint: disable=import-outside-toplevel,unused-argument
"""Fama-French Router."""

from typing import Annotated

from fastapi import Query as FastAPIQuery
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

router = Router(prefix="", description="Fama-French research factors and portfolios.")


@router.command(
    model="FamaFrenchFactors",
    methods=["GET"],
    examples=[
        APIEx(
            description="Fama-French 3-factors data for America, default is monthly.",
            parameters={
                "provider": "famafrench",
            },
        ),
        APIEx(
            description="Fama-French 5-factors data for Europe.",
            parameters={
                "provider": "famafrench",
                "region": "europe",
                "factor": "5_factors",
            },
        ),
    ],
)
async def factors(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Fama-French factors.

    Metadata for the selected dataset are returned in the
    `extra['results_metadata']` field of the response.

    Source
    ------

    https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html

    All returns are in U.S. dollars, include dividends and capital gains,
    and are not continuously compounded.

    Market is the return on a region's value-weight market portfolio
    minus the U.S. one month T-bill rate.

    The Fama/French 5 factors (2x3) are constructed using the 6,
    value-weight, portfolios formed on size and book-to-market, the 6,
    value-weight, portfolios formed on size and operating profitability,
    and the 6, value-weight, portfolios formed on size and investment.

    To construct the SMB, HML, RMW, and CMA factors, we sort stocks in a
    region into two market cap and three respective book-to-market equity (B/M),
    operating profitability (OP), and investment (INV) groups at the end of each June.

    Big stocks are those in the top 90% of June market cap for the region,
    and small stocks are those in the bottom 10%.
    The B/M, OP, and INV breakpoints for a region are the 30th and 70th percentiles
    of respective ratios for the big stocks of the region.

    Rm–Rf for July of year t to June of t+1 include all stocks
    for which we have market equity data for June of t.
    SMB, HML, RMW, and CMA for July of year t to June of t+1 include all stocks
    for which we have market equity data for December of t-1
    and June of t, (positive) book equity data for t-1 (for SMB, HML, and RMW),
    non-missing revenues and at least one of the following: cost of goods sold,
    selling, general and administrative expenses, or interest expense for
    t-1 (for SMB and RMW), and total assets data for t-2 and t-1 (for SMB and CMA).

    The momentum and short term reversal portfolios are reconstituted monthly
    and the other research portfolios are reconstituted annually.
    We reconstruct the full history of returns each month when we update the portfolios.
    """
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    methods=["GET"],
    include_in_schema=False,
    openapi_extra={"widget_config": {"exclude": True}},
    examples=[
        APIEx(
            description="Get region choices.",
            parameters={
                "provider": "famafrench",
            },
        ),
        APIEx(
            description="Get factor choices by region.",
            parameters={
                "provider": "famafrench",
                "region": "europe",
            },
        ),
        APIEx(
            description="Get interval choices for factors by region.",
            parameters={
                "provider": "famafrench",
                "region": "europe",
                "factor": "5_Factors",
            },
        ),
        APIEx(
            description="Get regional choices by portfolio.",
            parameters={
                "provider": "famafrench",
                "portfolio": "6 Portfolios ME BE-ME",
            },
        ),
    ],
)
async def factor_choices(
    region: Annotated[
        str | None,
        FastAPIQuery(description="Region to get factor choices for."),
    ] = None,
    factor: Annotated[
        str | None,
        FastAPIQuery(
            description="Factor to get interval choices for.",
        ),
    ] = None,
    is_portfolio: Annotated[
        bool | None,
        FastAPIQuery(
            description="When True, returns portfolio choices by region.",
        ),
    ] = None,
    portfolio: Annotated[
        str | None,
        FastAPIQuery(
            description="When supplied, returns regional choices for the portfolio.",
        ),
    ] = None,
) -> list:
    """
    Endpoint (optionsEndpoint) for providing dynamic menu choices to OpenBB Workspace widgets.

    Intended to be referenced in 'widgets.json', and returns a list of {'value': str, 'label': str}.
    """
    # pylint: disable=import-outside-toplevel
    from openbb_famafrench.utils.helpers import get_factor_choices

    return await get_factor_choices(
        region=region,
        factor=factor,
        is_portfolio=is_portfolio is True,
        portfolio=portfolio,
    )


@router.command(
    model="FamaFrenchUSPortfolioReturns",
    methods=["GET"],
    examples=[
        APIEx(
            description="Get model US portfolio returns "
            + "used for constructing the Fama-French Factor models.",
            parameters={
                "provider": "famafrench",
            },
        ),
        APIEx(
            description="If the portfolio name does not have a frequency - i.e."
            + " '_daily' - use the frequency parameter to specify the interval.",
            parameters={
                "provider": "famafrench",
                "portfolio": "5_industry_portfolios_wout_div",
                "frequency": "annual",
                "measure": "equal",
            },
        ),
    ],
)
async def us_portfolio_returns(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """US Portfolio returns.

    Metadata for the selected dataset are returned in the
    `extra['results_metadata']` field of the response.

    Source
    ------

    https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html

    All returns are in U.S. dollars, include dividends (unless the portfolio is 'wout_div')
    and capital gains, and are not continuously compounded.


    The momentum and short term reversal portfolios are reconstituted monthly
    and the other research portfolios are reconstituted annually.
    We reconstruct the full history of returns each month when we update the portfolios.


    Size and Book-to-Market Portfolios
    ----------------------------------

    - Small Value
    - Small Neutral
    - Small Growth
    - Big Value
    - Big Neutral
    - Big Growth

    BE < 0; bottom 30%, middle 40%, top 30%; quintiles; deciles.
    Firms with negative book equity are in only the BE < 0 portfolio.

    Size and Operating Profitability Portfolios
    -------------------------------------------

    - Small Robust
    - Small Neutral
    - Small Weak
    - Big Robust
    - Big Neutral
    - Big Weak

    Operating Profitability bottom 30%, middle 40%, top 30%; quintiles; deciles.

    Size and Investment Portfolios
    ------------------------------

    - Small Conservative
    - Small Neutral
    - Small Aggressive
    - Big Conservative
    - Big Neutral
    - Big Aggressive

    ME < 0 (not used); bottom 30%, middle 40%, top 30%; quintiles; deciles.
    Investment bottom 30%, middle 40%, top 30%; quintiles; deciles.

    Definitions
    -----------

    ME : Market Equity

    Market equity (size) is price times shares outstanding.
    Price and shares outstanding are from CRSP.

    BE : Book Equity

    Book equity is constructed from Compustat data or collected from the
    Moody’s Industrial, Financial, and Utilities manuals.
    BE is the book value of stockholders’ equity, plus balance sheet deferred taxes
    and investment tax credit (if available), minus the book value of preferred stock.
    Depending on availability, we use the redemption, liquidation, or par value (in that order)
    to estimate the book value of preferred stock. Stockholders’ equity is the value reported
    by Moody’s or Compustat, if it is available. If not, we measure stockholders’ equity as
    the book value of common equity plus the par value of preferred stock,
    or the book value of assets minus total liabilities (in that order).

    See Davis, Fama, and French, 2000,
    “Characteristics, Covariances, and Average Returns: 1929-1997”
    Journal of Finance, for more details.

    BE/ME : Book-to-Market

    The book-to-market ratio used to form portfolios in June of year t is book equity
    for the fiscal year ending in calendar year t-1,
    divided by market equity at the end of December of t-1.

    OP : Operating Profitability

    The operating profitability ratio used to form portfolios in June of year t is annual revenues
    minus cost of goods sold, interest expense, and selling, general, and administrative expense
    divided by the sum of book equity and minority interest for the last fiscal year ending in t-1.

    INV : Investment

    The investment ratio used to form portfolios in June of year t is the change in total assets
    from the fiscal year ending in year t-2 to the fiscal year ending in t-1,
    divided by t-2 total assets.

    E/P : Earnings/Price

    Earnings is total earnings before extraordinary items, from Compustat.
    The earnings/price ratio used to form portfolios in June of year t is earnings
    for the fiscal year ending in calendar year t-1,
    divided by market equity at the end of December of t-1.

    CF/P : Cashflow/Price

    Cashflow is total earnings before extraordinary items, plus equity’s share of depreciation,
    plus deferred taxes (if available), from Compustat. Equity’s share is defined as market equity
    divided by assets minus book equity plus market equity.
    The cashflow/price ratio used to form portfolios in June of year t is the cashflow for the
    fiscal year ending in calendar year t-1, divided by market equity at the end of December of t-1.

    D/P : Dividend Yield

    The dividend yield used to form portfolios in June of year t is the total dividends paid
    from July of t-1 to June of t per dollar of equity in June of t.
    The dividend yield is computed using the with and without dividend returns from CRSP,
    as described in Fama and French, 1988, “Dividend yields and expected stock returns,”
    Journal of Financial Economics 25.
    """
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="FamaFrenchRegionalPortfolioReturns",
    methods=["GET"],
    examples=[
        APIEx(
            description="Get model Regional portfolio returns "
            + "used for constructing the Fama-French Factor models.",
            parameters={
                "provider": "famafrench",
            },
        ),
        APIEx(
            description="Get portfolios formed by equal-weight, with annual returns.",
            parameters={
                "provider": "famafrench",
                "frequency": "annual",
                "measure": "equal",
            },
        ),
    ],
)
async def regional_portfolio_returns(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Regional portfolio returns.

    Metadata for the selected dataset are returned in the
    `extra['results_metadata']` field of the response.

    See the `us_portfolio_returns` endpoint for more details.
    """
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="FamaFrenchCountryPortfolioReturns",
    methods=["GET"],
    examples=[
        APIEx(
            description="Get model Country portfolio returns "
            + "used for constructing the Fama-French Factor models.",
            parameters={
                "provider": "famafrench",
            },
        ),
        APIEx(
            description="Parameters are different than the regional and US portfolio returns.",
            parameters={
                "provider": "famafrench",
                "frequency": "annual",
                "measure": "local",
                "country": "japan",
                "dividends": False,
                "all_data_items_required": False,
            },
        ),
    ],
)
async def country_portfolio_returns(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Country portfolio returns.

    Metadata for the selected dataset are returned in the
    `extra['results_metadata']` field of the response.

    Source
    ------

    https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html

    We form value and growth portfolios in each country using four valuation ratios:

    - book-to-market (B/M)
    - earnings-price (E/P)
    - cash earnings to price (CE/P)
    - dividend yield (D/P)

    We form the portfolios at the end of December each year by sorting on one of the four ratios and
    then compute value-weighted returns for the following 12 months.

    The value portfolios (High) contain firms in the top 30% of a ratio
    and the growth portfolios (Low) contain firms in the bottom 30%.

    There are two sets of portfolios.

    In one, firms are included only if we have data on all four ratios.

    In the other, a firm is included in a sort variable's portfolios
    if we have data for that variable.

    The market return (Mkt) for the first set is the value weighted average of the returns
    for only firms with all four ratios.

    The market return for the second set includes all firms with book-to-market data,
    and Firms is the number of firms with B/M data.
    """
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="FamaFrenchInternationalIndexReturns",
    methods=["GET"],
    examples=[
        APIEx(
            description="Get benchmark index returns "
            + "used for constructing the international Fama-French Factor models.",
            parameters={
                "provider": "famafrench",
            },
        ),
        APIEx(
            description="Parameters are similar to the country portfolio returns.",
            parameters={
                "provider": "famafrench",
                "frequency": "annual",
                "measure": "ratios",
                "index": "europe_ex_uk",
                "dividends": False,
                "all_data_items_required": False,
            },
        ),
    ],
)
async def international_index_returns(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """International index returns.

    Metadata for the selected dataset are returned in the
    `extra['results_metadata']` field of the response.

    See the `country_portfolio_returns` endpoint for more details.

    Source
    ------

    https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html

    The returns on the index portfolios are constructed by
    averaging the returns on the country portfolios.

    We weight countries in the index portfolios in proportion to their EAFE + Canada weights.

    Each country is added to the index portfolios when the return data for the country begin;
    the country start dates can be inferred from the country return files.
    """
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="FamaFrenchBreakpoints",
    methods=["GET"],
    examples=[
        APIEx(
            description="Get US breakpoints "
            + "used for constructing the research portfolios.",
            parameters={
                "provider": "famafrench",
            },
        ),
        APIEx(
            description="See the parameters description for details on the breakpoints.",
            parameters={
                "provider": "famafrench",
                "breakpoint": "op",
                "start_date": "1998-01-01",
            },
        ),
    ],
)
async def breakpoints(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Fama-French breakpoints.

    Metadata for the selected dataset are returned in the
    `extra['results_metadata']` field of the response.

    Source
    ------

    https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html#Breakpoints
    """
    return await OBBject.from_query(OpenBBQuery(**locals()))
