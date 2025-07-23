"""Fama-French Factors Fetcher Model."""

# pylint: disable=unused-argument

from datetime import date as dateType
from typing import Any, Literal, Optional, Union

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field

from openbb_famafrench.utils.constants import RegionalPortfolios, portfolio_choices


class FamaFrenchRegionalPortfolioReturnsQueryParams(QueryParams):
    """Regional Portfolio Returns Query parameters."""

    __json_schema_extra__ = {
        "portfolio": {
            "x-widget_config": {
                "options": [
                    {"value": d, "label": d}
                    for d in portfolio_choices
                    if d.get("value") in getattr(RegionalPortfolios, "__args__", [])
                ]
            }
        },
    }

    portfolio: RegionalPortfolios = Field(
        default="developed_ex_us_6_portfolios_me_op",
        description="The specific portfolio file to fetch.",
    )
    measure: Literal[
        "value",
        "equal",
        "number_of_firms",
        "firm_size",
    ] = Field(
        default="value",
        description="The measure to fetch for the portfolio.",
    )
    frequency: Literal["monthly", "annual"] = Field(
        default="monthly",
        description="The frequency of the data to fetch."
        + " Ignored when the portfolio ends with 'daily'.",
    )
    start_date: Optional[dateType] = Field(
        default=None,
        description="The start date for the data. Defaults to the earliest available date.",
    )
    end_date: Optional[dateType] = Field(
        default=None,
        description="The end date for the data. Defaults to the latest available date.",
    )


class FamaFrenchRegionalPortfolioReturnsData(Data):
    """Regional Portfolio Returns Data."""

    __alias_dict__ = {
        "date": "Date",
    }

    date: dateType = Field(
        description="The date of the data.",
    )
    portfolio: str = Field(
        description="The individual portfolio formation within the portfolio file.",
    )
    measure: Literal[
        "value",
        "equal",
        "number_of_firms",
        "firm_size",
    ] = Field(
        description="The measure of the portfolio.",
    )
    value: Union[int, float] = Field(
        description="The value represented by the 'measure'."
        + " Missing data are indicated by -99.99 or -999",
    )


class FamaFrenchRegionalPortfolioReturnsFetcher(
    Fetcher[
        FamaFrenchRegionalPortfolioReturnsQueryParams,
        list[FamaFrenchRegionalPortfolioReturnsData],
    ]
):
    """Regional Portfolio Returns Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FamaFrenchRegionalPortfolioReturnsQueryParams:
        """Transform the query parameters into a QueryParams object."""
        return FamaFrenchRegionalPortfolioReturnsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FamaFrenchRegionalPortfolioReturnsQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> tuple:
        """Extract data from the Fama-French FTP."""
        # pylint: disable=import-outside-toplevel
        from openbb_famafrench.utils.helpers import get_portfolio_data

        dataset = ""

        for item in portfolio_choices:
            if item.get("label") == query.portfolio:
                dataset = item["value"]
                break

        try:
            return get_portfolio_data(
                dataset=dataset,
                measure=query.measure,
                frequency=(None if "daily" in dataset.lower() else query.frequency),
            )
        except Exception as e:  # pylint: disable=broad-except
            raise OpenBBError(e) from e

    @staticmethod
    def transform_data(
        query: FamaFrenchRegionalPortfolioReturnsQueryParams,
        data: tuple,
        **kwargs: Any,
    ) -> AnnotatedResult[list[FamaFrenchRegionalPortfolioReturnsData]]:
        """Transform the extracted data."""
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
                    if query.measure == "number_of_firms"
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

        # Flatten the DataFrame to conform to the Data model
        # This avoids having undefined fields.
        flattened_data = (
            returns_data.reset_index()
            .melt(
                id_vars=["Date"],
                var_name="portfolio",
                value_name="value",
            )
            .copy()
        )
        flattened_data.loc[:, "measure"] = query.measure

        return AnnotatedResult(
            result=[
                FamaFrenchRegionalPortfolioReturnsData(**d)
                for d in flattened_data.to_dict(orient="records")
            ],
            metadata=meta[0] if isinstance(meta, list) else meta,
        )
