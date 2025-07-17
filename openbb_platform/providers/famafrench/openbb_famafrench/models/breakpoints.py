"""Fama-French Breakpoints Model."""

# pylint: disable=unused-argument

from datetime import date as dateType
from typing import Any, Optional

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field

from openbb_famafrench.utils.constants import BreakpointChoices


class FamaFrenchBreakpointQueryParams(QueryParams):
    """Fama-French Breakpoints Query."""

    breakpoint_type: BreakpointChoices = Field(
        default="me",
        description="""Type of breakpoint to fetch.

The breakpoints for month t use all NYSE stocks that have a CRSP share code of 10 or 11
and have good shares and price data. We exclude closed end funds and REITs.

Breakpoints are computed either monthly or annually, see the description of each breakpoint type below.

Data contains every fifth percentile, from 5% to 100%.

ME
--

Market Equity. Market equity (size) is price times shares outstanding.
Price and shares outstanding are from CRSP.

ME breakpoints are computed for each month.
It is price times shares outstanding (divided by 1,000,000) at month end.

BE/ME
-----

BE/ME breakpoints are computed at the end of each June.
The BE used in June of year t is the book equity for the last fiscal year end in t-1.
ME is price times shares outstanding at the end of December of t-1.

The breakpoints for year t use all NYSE stocks for which we have ME for December of t-1
and (positive) BE for the last fiscal year end in t-1.

Operating Profitability
-----------------------

Operating Profitability breakpoints are computed at the end of each June.
OP for June of year t is annual revenues minus

- cost of goods sold
- interest expense
- selling, general, and administrative expenses

divided by book equity for the last fiscal year end in t-1.

Please be aware that some of the value-weight averages of operating profitability for deciles 1 and 10 are extreme.
These are driven by extraordinary values of OP for individual firms.
We have spot checked the accounting data that produce the extraordinary values
and all the numbers we examined accurately reflect the data in the firm's accounting statements.

The breakpoints for year t use all NYSE stocks for which we have (positive) book equity data for t-1,
non-missing revenues data for t-1, and non-missing data for at least one of the following:

- cost of goods sold
- selling, general and administrative expenses
- interest expense for t-1.

Investment
----------

Investment breakpoints are computed at the end of each June.
Inv used in June of year t is the change in total assets from the fiscal year ending in year t-2
to the fiscal year ending in t-1, divided by t-2 total assets.

The breakpoints for year t use all NYSE stocks for which we have total assets data for t-2 and t-1.

E/P
---

E/P (in percent) breakpoints are computed at the end of each June.
The E used in June of year t is the earnings for the last fiscal year end in t-1.
P (actually ME) is price times shares outstanding at the end of December of t-1.

The breakpoints for year t use all NYSE stocks for which we have ME for December of t-1
and (positive) earnings for the last fiscal year end in t-1.

CF/P
----

CF/P (in percent) breakpoints is computed at the end of each June.
The CF used in June of year t is the cash flow for the last fiscal year end in t-1.
P (actually ME) is price times shares outstanding at the end of December of t-1.

The breakpoints for year t use all NYSE stocks for which we have ME for December of t-1
and (positive) cash flow for the last fiscal year end in t-1.

D/P
---

D/P (in percent) breakpoints are computed at the end of each June.
The dividend yield in June of year t is the total dividends paid from July of t-1
to June of t per dollar of equity in June of t.

The breakpoints for year t use NYSE stocks for which we have at least
seven months (to compute the dividend yield) from July of t-1 to June of t.
(Only six monthly returns are required in June 1926.)
We do not include stocks that pay no dividends from July of t-1 to June of t.

Prior 2-12
----------

Prior return breakpoints are computed for each month.
The prior return at the end of month t is the cumulative return from month t-11 to month t-1.

The breakpoints for month t use NYSE stocks.
To be included, a stock must have a price for the end of month t-12 and a good return for t-1.
In addition, any missing returns from t-11 to t-2 must be -99.0, CRSP's code for a missing price.
""",
    )

    start_date: Optional[dateType] = Field(
        default=None,
        description="Start date for the data.",
    )
    end_date: Optional[dateType] = Field(
        default=None,
        description="End date for the data.",
    )


class FamaFrenchBreakpointData(Data):
    """Fama-French Breakpoints Data."""

    date: dateType = Field(
        description="Date of the data.",
    )
    num_firms: Optional[int] = Field(
        default=None,
        description="Number of firms in the sample. Not returned for BE/ME breakpoints.",
    )
    num_firms_less_than_0: Optional[int] = Field(
        default=None,
        description="Number of firms with ratio less than or equal to 0."
        + " This is only applicable for ratio breakpoints.",
    )
    num_firms_greater_than_0: Optional[int] = Field(
        default=None,
        description="Number of firms with ratio greater than 0."
        + " This is only applicable for ratio breakpoints.",
    )
    percentile_5: float = Field(
        description="Fifth percentile of the sample.",
        title="5th Percentile",
    )
    percentile_10: float = Field(
        description="Tenth percentile of the sample.",
        title="10th Percentile",
    )
    percentile_15: float = Field(
        description="Fifteenth percentile of the sample.",
        title="15th Percentile",
    )
    percentile_20: float = Field(
        description="Twentieth percentile of the sample.",
        title="20th Percentile",
    )
    percentile_25: float = Field(
        description="Twenty-fifth percentile of the sample.",
        title="25th Percentile",
    )
    percentile_30: float = Field(
        description="Thirtieth percentile of the sample.",
        title="30th Percentile",
    )
    percentile_35: float = Field(
        description="Thirty-fifth percentile of the sample.",
        title="35th Percentile",
    )
    percentile_40: float = Field(
        description="Fortieth percentile of the sample.",
        title="40th Percentile",
    )
    percentile_45: float = Field(
        description="Forty-fifth percentile of the sample.",
        title="45th Percentile",
    )
    percentile_50: float = Field(
        description="Fiftieth percentile of the sample.",
        title="50th Percentile",
    )
    percentile_55: float = Field(
        description="Fifty-fifth percentile of the sample.",
        title="55th Percentile",
    )
    percentile_60: float = Field(
        description="Sixtieth percentile of the sample.",
        title="60th Percentile",
    )
    percentile_65: float = Field(
        description="Sixty-fifth percentile of the sample.",
        title="65th Percentile",
    )
    percentile_70: float = Field(
        description="Seventieth percentile of the sample.",
        title="70th Percentile",
    )
    percentile_75: float = Field(
        description="Seventy-fifth percentile of the sample.",
        title="75th Percentile",
    )
    percentile_80: float = Field(
        description="Eightieth percentile of the sample.",
        title="80th Percentile",
    )
    percentile_85: float = Field(
        description="Eighty-fifth percentile of the sample.",
        title="85th Percentile",
    )
    percentile_90: float = Field(
        description="Ninetieth percentile of the sample.",
        title="90th Percentile",
    )
    percentile_95: float = Field(
        description="Ninety-fifth percentile of the sample.",
        title="95th Percentile",
    )
    percentile_100: float = Field(
        description="Hundredth percentile of the sample.",
        title="100th Percentile",
    )


class FamaFrenchBreakpointFetcher(
    Fetcher[FamaFrenchBreakpointQueryParams, list[FamaFrenchBreakpointData]]
):
    """Fama-French Breakpoints Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FamaFrenchBreakpointQueryParams:
        """Transform the query parameters into a QueryParams object."""
        return FamaFrenchBreakpointQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FamaFrenchBreakpointQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> tuple:
        """Extract data from the Fama-French FTP."""
        # pylint: disable=import-outside-toplevel
        from openbb_famafrench.utils.helpers import get_breakpoint_data

        try:
            return get_breakpoint_data(
                breakpoint_type=query.breakpoint_type,
            )
        except Exception as e:
            raise OpenBBError(e) from e

    @staticmethod
    def transform_data(
        query: FamaFrenchBreakpointQueryParams,
        data: tuple,
        **kwargs: Any,
    ) -> AnnotatedResult[list[FamaFrenchBreakpointData]]:
        """Transform the extracted data."""
        dfs, meta = data

        if not dfs:
            raise OpenBBError(
                f"The data is unexpectedly empty. -> {query.breakpoint_type}"
            )

        df = dfs[0]
        metadata = meta[0]

        if query.start_date:
            df = df[df["date"] >= query.start_date.strftime("%Y-%m-%d")]

        if query.end_date:
            df = df[df["date"] <= query.end_date.strftime("%Y-%m-%d")]

        return AnnotatedResult(
            result=[
                FamaFrenchBreakpointData(**d) for d in df.to_dict(orient="records")
            ],
            metadata={"description": metadata},
        )
