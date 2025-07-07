"""Fama-French Factors Fetcher Model."""

# pylint: disable=unused-argument

from datetime import date as dateType
from typing import Any, Literal, Optional

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field

from openbb_famafrench.utils.constants import InternationalIndexPortfolios


class FamaFrenchInternationalIndexReturnsQueryParams(QueryParams):
    """International Index Returns Query parameters."""

    __json_schema_extra__ = {
        "country": {
            "x-widget_config": {
                "options": [
                    {
                        "value": d,
                        "label": d.replace("_", " ").title().replace("Ex ", "Ex-"),
                    }
                    for d in getattr(InternationalIndexPortfolios, "__args__", [])
                ]
            }
        },
    }

    index: InternationalIndexPortfolios = Field(
        default="all",
        description="International index to fetch the portfolio returns for. Defaults to 'all'.",
    )
    measure: Literal[
        "usd",
        "local",
        "ratios",
    ] = Field(
        default="usd",
        description="The measure to fetch for the portfolio."
        + " Only 'annual' frequency is supported for 'ratios'.",
    )
    frequency: Literal["monthly", "annual"] = Field(
        default="monthly",
        description="The frequency of the data to fetch."
        + " Ignored when `measure` is set to 'ratios'.",
    )
    dividends: Optional[bool] = Field(
        default=None, description="When False, portoflios exclude dividends."
    )
    all_data_items_required: Optional[bool] = Field(
        default=None,
        description="If True (default), includes firms with data for all four ratios."
        + " When False, includes only firms with Book-to-Market (B/M) data.",
    )
    start_date: Optional[dateType] = Field(
        default=None,
        description="The start date for the data. Defaults to the earliest available date.",
    )
    end_date: Optional[dateType] = Field(
        default=None,
        description="The end date for the data. Defaults to the latest available date.",
    )


class FamaFrenchInternationalIndexReturnsData(Data):
    """International Index Portfolio Returns Data."""

    __alias_dict__ = {
        "date": "Date",
        "mkt": "Mkt",
        "firms": "Firms",
        "bm": "B/M",
        "be_me_high": "BE/ME High",
        "be_me_low": "BE/ME Low",
        "ep": "E/P",
        "e_p_high": "E/P High",
        "e_p_low": "E/P Low",
        "ce_p": "CE/P",
        "ce_p_high": "CE/P High",
        "ce_p_low": "CE/P Low",
        "yld": "Yld",
        "yld_high": "Yld High",
        "yld_low": "Yld Low",
        "yld_zero": "Yld Zero",
    }

    date: dateType = Field(
        description="The date of the data.",
    )
    mkt: Optional[float] = Field(
        default=None,
        description="""
        The market return (Mkt) for the first set is the value weighted average
        of the returns for only firms with all four ratios.

        The market return for the second set includes all firms with book-to-market data,
        and Firms is the number of firms with B/M data.

        Not returned if `measure` is set to 'ratios'.
        """,
    )
    firms: Optional[int] = Field(
        default=None,
        description="The number of firms, relative to `all_data_items_required` parameter."
        + " Only returned when `measure` is set to 'ratios'.",
    )
    bm: Optional[float] = Field(
        default=None,
        description="Book to Market equity ratio."
        + " Not returned if `measure` is set to 'ratios'.",
        title="B/M",
    )
    be_me_high: Optional[float] = Field(
        default=None,
        description="Book Equity to Market Equity returns for the value portfolio."
        + " Not returned if `measure` is set to 'ratios'.",
        title="BE/ME High",
    )
    be_me_low: Optional[float] = Field(
        default=None,
        description="Book Equity to Market Equity returns for the growth portfolio."
        + " Not returned if `measure` is set to 'ratios'.",
        title="BE/ME Low",
    )
    ep: Optional[float] = Field(
        default=None,
        description="Earnings to Price ratio."
        + " Only returned when `measure` is set to 'ratios'.",
        title="E/P",
    )
    e_p_high: Optional[float] = Field(
        default=None,
        description="Earnings to Price returns for the value portfolio."
        + " Not returned if `measure` is set to 'ratios'.",
        title="E/P High",
    )
    e_p_low: Optional[float] = Field(
        default=None,
        description="Earnings to Price returns for the growth portfolio."
        + " Not returned if `measure` is set to 'ratios'.",
        title="E/P Low",
    )
    ce_p: Optional[float] = Field(
        default=None,
        description="Cash Earnings to Price ratio."
        + " Only returned when `measure` is set to 'ratios'.",
        title="CE/P",
    )
    ce_p_high: Optional[float] = Field(
        default=None,
        description="Cash Earnings to Price returns for the value portfolio."
        + " Not returned if `measure` is set to 'ratios'.",
        title="CE/P High",
    )
    ce_p_low: Optional[float] = Field(
        default=None,
        description="Cash Earnings to Price returns for the growth portfolio."
        + " Not returned if `measure` is set to 'ratios'.",
        title="CE/P Low",
    )
    yld: Optional[float] = Field(
        default=None,
        description="Dividend Yield ratio."
        + " Only returned when `measure` is set to 'ratios'.",
        title="Yld",
    )
    yld_high: Optional[float] = Field(
        default=None,
        description="Dividend Yield returns for the value portfolio."
        + " Not returned if `measure` is set to 'ratios'.",
        title="Yld High",
    )
    yld_low: Optional[float] = Field(
        default=None,
        description="Dividend Yield returns for the growth portfolio."
        + " Not returned if `measure` is set to 'ratios'.",
        title="Yld Low",
    )
    yld_zero: Optional[float] = Field(
        default=None,
        description="Dividend Yield returns for firms not paying dividends."
        + " Not returned if `measure` is set to 'ratios'.",
        title="Yld Zero",
    )


class FamaFrenchInternationalIndexReturnsFetcher(
    Fetcher[
        FamaFrenchInternationalIndexReturnsQueryParams,
        list[FamaFrenchInternationalIndexReturnsData],
    ]
):
    """International Index Returns Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FamaFrenchInternationalIndexReturnsQueryParams:
        """Transform the query parameters into a QueryParams object."""
        return FamaFrenchInternationalIndexReturnsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FamaFrenchInternationalIndexReturnsQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> tuple:
        """Extract data from the Fama-French FTP."""
        # pylint: disable=import-outside-toplevel
        from openbb_famafrench.utils.helpers import get_international_portfolio  # noqa
        from warnings import warn

        if query.measure == "ratios" and query.frequency != "annual":
            warn("Only 'annual' frequency is supported for 'ratios' measure.")
            query.frequency = "annual"

        try:
            return get_international_portfolio(
                index=query.index,
                measure=query.measure,
                frequency=query.frequency,
                dividends=True if query.dividends is None else query.dividends,
                all_data_items_required=(
                    True
                    if query.all_data_items_required is None
                    else query.all_data_items_required
                ),
            )
        except Exception as e:  # pylint: disable=broad-except
            raise OpenBBError(e) from e

    @staticmethod
    def transform_data(
        query: FamaFrenchInternationalIndexReturnsQueryParams,
        data: tuple,
        **kwargs: Any,
    ) -> AnnotatedResult[list[FamaFrenchInternationalIndexReturnsData]]:
        """Transform the extracted data."""
        # pylint: disable=import-outside-toplevel
        from pandas import MultiIndex

        dfs, meta = data

        if not dfs:
            raise OpenBBError(
                "The request was returned empty."
                + " This may be due to an invalid, or incorrectly mapped, portfolio choice."
            )
        returns_data = dfs[0] if isinstance(dfs, list) else dfs

        # Values of -99.99  or -999 indicate no data,
        # Drop columns that have no data.
        for col in returns_data.columns:
            if all(returns_data[col].values == "-99.99") or all(
                returns_data[col].values == "-999"
            ):
                returns_data = returns_data.drop(columns=[col])
            else:
                returns_data[col] = (
                    returns_data[col].astype(int)
                    if query.measure == "ratios" and col == "firms"
                    else returns_data[col].astype(float)
                )

        if query.start_date:
            returns_data = returns_data[
                returns_data.index >= query.start_date.strftime("%Y-%m-%d")
            ]

        if query.end_date:
            returns_data = returns_data[
                returns_data.index <= query.end_date.strftime("%Y-%m-%d")
            ]

        if isinstance(returns_data.columns, MultiIndex):
            returns_data.columns = [
                " ".join([str(level) for level in col if str(level) != ""])
                for col in returns_data.columns.values
            ]

        metadata = meta[0] if isinstance(meta, list) else meta
        description = metadata.pop("description", "")
        new_description = """
We form value and growth portfolios in each country using four ratios:

- book-to-market (B/M)
- earnings-price (E/P)
- cash earnings to price (CE/P)
- dividend yield (D/P)

The returns on the index portfolios are constructed by averaging the returns on the country portfolios.
Each country is added to the index portfolios when the return data for the country begin;
the country start dates can be inferred from the country return files.

We weight countries in the index portfolios in proportion to their EAFE + Canada weights.

The raw data are from Morgan Stanley Capital International for 1975 to 2006 and from
Bloomberg for 2007 to present.
        """
        metadata["description"] = "### " + description + "\n" + new_description

        return AnnotatedResult(
            result=[
                FamaFrenchInternationalIndexReturnsData(**d)
                for d in returns_data.reset_index().to_dict(orient="records")
            ],
            metadata=meta[0] if isinstance(meta, list) else meta,
        )
