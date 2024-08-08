"""Multpl S&P 500 Multiples Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Optional
from warnings import warn

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.sp500_multiples import (
    SP500MultiplesData,
    SP500MultiplesQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import field_validator

BASE_URL = "https://www.multpl.com/"

URL_DICT = {
    "shiller_pe_month": "shiller-pe/table/by-month",
    "shiller_pe_year": "shiller-pe/table/by-year",
    "pe_year": "s-p-500-pe-ratio/table/by-year",
    "pe_month": "s-p-500-pe-ratio/table/by-month",
    "dividend_year": "s-p-500-dividend/table/by-year",
    "dividend_month": "s-p-500-dividend/table/by-month",
    "dividend_growth_quarter": "s-p-500-dividend-growth/table/by-quarter",
    "dividend_growth_year": "s-p-500-dividend-growth/table/by-year",
    "dividend_yield_year": "s-p-500-dividend-yield/table/by-year",
    "dividend_yield_month": "s-p-500-dividend-yield/table/by-month",
    "earnings_year": "s-p-500-earnings/table/by-year",
    "earnings_month": "s-p-500-earnings/table/by-month",
    "earnings_growth_year": "s-p-500-earnings-growth/table/by-year",
    "earnings_growth_quarter": "s-p-500-earnings-growth/table/by-quarter",
    "real_earnings_growth_year": "s-p-500-real-earnings-growth/table/by-year",
    "real_earnings_growth_quarter": "s-p-500-real-earnings-growth/table/by-quarter",
    "earnings_yield_year": "s-p-500-earnings-yield/table/by-year",
    "earnings_yield_month": "s-p-500-earnings-yield/table/by-month",
    "real_price_year": "s-p-500-historical-prices/table/by-year",
    "real_price_month": "s-p-500-historical-prices/table/by-month",
    "inflation_adjusted_price_year": "inflation-adjusted-s-p-500/table/by-year",
    "inflation_adjusted_price_month": "inflation-adjusted-s-p-500/table/by-month",
    "sales_year": "s-p-500-sales/table/by-year",
    "sales_quarter": "s-p-500-sales/table/by-quarter",
    "sales_growth_year": "s-p-500-sales-growth/table/by-year",
    "sales_growth_quarter": "s-p-500-sales-growth/table/by-quarter",
    "real_sales_year": "s-p-500-real-sales/table/by-year",
    "real_sales_quarter": "s-p-500-real-sales/table/by-quarter",
    "real_sales_growth_year": "s-p-500-real-sales-growth/table/by-year",
    "real_sales_growth_quarter": "s-p-500-real-sales-growth/table/by-quarter",
    "price_to_sales_year": "s-p-500-price-to-sales/table/by-year",
    "price_to_sales_quarter": "s-p-500-price-to-sales/table/by-quarter",
    "price_to_book_value_year": "s-p-500-price-to-book/table/by-year",
    "price_to_book_value_quarter": "s-p-500-price-to-book/table/by-quarter",
    "book_value_year": "s-p-500-book-value/table/by-year",
    "book_value_quarter": "s-p-500-book-value/table/by-quarter",
}


class MultplSP500MultiplesQueryParams(SP500MultiplesQueryParams):
    """Multpl S&P 500 Multiples Query Params."""

    __json_schema_extra__ = {
        "series_name": {
            "multiple_items_allowed": True,
            "choices": sorted(list(URL_DICT)),
        }
    }

    @field_validator("series_name", mode="before", check_fields=False)
    @classmethod
    def validate_series_name(cls, v):
        """Validate series_name."""
        series = v.split(",")
        new_values: List = []
        for s in series:
            if s not in URL_DICT:
                raise OpenBBError(
                    f"{s} is not a valid `series_name`. Choices are: \n{sorted(list(URL_DICT))}\n"
                )
            new_values.append(s)
        if not new_values:
            raise OpenBBError(
                f"No valid series names provided. Choices are: \n{sorted(list(URL_DICT))}\n"
            )
        return ",".join(new_values)


class MultplSP500MultiplesData(SP500MultiplesData):
    """Multpl S&P 500 Multiples Data."""

    __alias_dict__ = {
        "date": "Date",
        "value": "Value",
    }


class MultplSP500MultiplesFetcher(
    Fetcher[
        MultplSP500MultiplesQueryParams,
        List[MultplSP500MultiplesData],
    ]
):
    """Multpl S&P 500 Multiples Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> MultplSP500MultiplesQueryParams:
        """Transform the query params."""
        return MultplSP500MultiplesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: MultplSP500MultiplesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract data."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        from io import StringIO
        from openbb_core.provider.utils.helpers import amake_request
        from numpy import nan
        from pandas import read_html, to_datetime

        series = query.series_name.split(",")
        urls = {s: f"{BASE_URL}{URL_DICT[s]}" for s in series}
        results: List = []

        async def response_callback(response, _):
            """Response callback."""
            return await response.text()

        async def get_one(url, series):
            """Get data for one series."""
            res = await amake_request(url, response_callback=response_callback)
            if res:
                df = read_html(StringIO(res))[0]  # type: ignore
                if not df.empty:
                    df["Date"] = to_datetime(df["Date"]).dt.date
                    df = df.sort_values("Date").reset_index(drop=True)
                    if query.start_date:
                        df = df[df["Date"] >= query.start_date]
                    if query.end_date:
                        df = df[df["Date"] <= query.end_date]
                    df["Value"] = df["Value"].apply(
                        lambda x: (
                            x.strip().replace("† ", "").replace("%", "")
                            if isinstance(x, str)
                            else x
                        )
                    )
                    df["name"] = series
                    if "growth" in series or "yield" in series:
                        df["Value"] = df["Value"].astype(float) / 100

                    results.extend(df.replace({nan: None}).to_dict(orient="records"))
            else:
                warn(f"Failed to get data for {series}.")

        await asyncio.gather(*[get_one(url, series) for series, url in urls.items()])

        if not results:
            raise EmptyDataError("The request was returned empty.")

        return results

    @staticmethod
    def transform_data(
        query: MultplSP500MultiplesQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[MultplSP500MultiplesData]:
        """Transform and validate the data."""
        return [
            MultplSP500MultiplesData.model_validate(d)
            for d in sorted(
                data,
                key=lambda x: (x["Date"], x["name"]),
            )
        ]
