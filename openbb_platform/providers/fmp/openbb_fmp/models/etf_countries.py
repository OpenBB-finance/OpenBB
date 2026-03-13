"""FMP ETF Countries Model."""

# pylint: disable=unused-argument

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.etf_countries import (
    EtfCountriesData,
    EtfCountriesQueryParams,
)


class FMPEtfCountriesQueryParams(EtfCountriesQueryParams):
    """FMP ETF Countries Query."""

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}


class FMPEtfCountriesData(EtfCountriesData):
    """FMP ETF Countries Data."""


class FMPEtfCountriesFetcher(
    Fetcher[
        FMPEtfCountriesQueryParams,
        list[FMPEtfCountriesData],
    ]
):
    """FMP ETF Countries Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FMPEtfCountriesQueryParams:
        """Transform the query."""
        return FMPEtfCountriesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPEtfCountriesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list:
        """Return the raw data from the FMP endpoint."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        import warnings
        from openbb_core.provider.utils.errors import EmptyDataError
        from openbb_fmp.utils.helpers import get_data

        api_key = credentials.get("fmp_api_key") if credentials else ""
        symbols = query.symbol.split(",")
        results: list = []

        async def get_one(symbol):
            """Get data for one symbol."""
            url = f"https://financialmodelingprep.com/stable/etf/country-weightings?symbol={symbol}&apikey={api_key}"
            result = await get_data(url, **kwargs)

            if not result:
                warnings.warn(f"Symbol Error: No data found for {symbol}")
                return

            new_data: list = []
            if result:
                for row in result:
                    row_weight = row.get("weightPercentage", "0%").replace("%", "")
                    if not row_weight or row_weight == "0":
                        continue
                    new_row = {
                        "symbol": symbol,
                        "country": row["country"],
                        "weight": float(row_weight) * 0.01,
                    }
                    new_data.append(new_row)

                if new_data:
                    results.extend(new_data)
            return

        await asyncio.gather(*[get_one(symbol) for symbol in symbols])

        if not results:
            raise EmptyDataError("No data found for the given symbols.")

        return results

    @staticmethod
    def transform_data(
        query: FMPEtfCountriesQueryParams, data: list, **kwargs: Any
    ) -> list[FMPEtfCountriesData]:
        """Return the transformed data."""
        symbols = query.symbol.split(",")

        return [
            FMPEtfCountriesData.model_validate(d)
            for d in sorted(
                data,
                key=lambda x: (
                    symbols.index(x.get("symbol", len(symbols))),
                    -(x.get("weightPercentage", 0) or 0),
                ),
            )
        ]
