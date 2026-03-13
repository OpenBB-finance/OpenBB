"""FMP Historical Market Cap Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.historical_market_cap import (
    HistoricalMarketCapData,
    HistoricalMarketCapQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError


class FmpHistoricalMarketCapQueryParams(HistoricalMarketCapQueryParams):
    """FMP Historical Market Cap Query.

    Source: https://site.financialmodelingprep.com/developer/docs#historical-market-cap

    """

    __json_schema_extra__ = {
        "symbol": {"multiple_items_allowed": True},
    }


class FmpHistoricalMarketCapData(HistoricalMarketCapData):
    """FMP Historical Market Cap Data."""

    __alias_dict__ = {
        "market_cap": "marketCap",
    }


class FmpHistoricalMarketCapFetcher(
    Fetcher[
        FmpHistoricalMarketCapQueryParams,
        list[FmpHistoricalMarketCapData],
    ]
):
    """FMP Historical Market Cap Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FmpHistoricalMarketCapQueryParams:
        """Transform the query params."""
        return FmpHistoricalMarketCapQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FmpHistoricalMarketCapQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list:
        """Return the raw data from the FMP endpoint."""
        # pylint: disable=import-outside-toplevel
        import warnings  # noqa
        from dateutil.relativedelta import relativedelta
        from openbb_fmp.utils.helpers import get_data_urls

        symbols = query.symbol.split(",")
        api_key = credentials.get("fmp_api_key") if credentials else ""
        results: list = []

        def generate_urls(symbol, start_date, end_date):
            """Generate URLs for each 5-year interval between start_date and end_date."""
            urls: list = []
            base_url = f"https://financialmodelingprep.com/stable/historical-market-capitalization?symbol={symbol}&limit=5000"
            base_url = base_url + "&from={}&to={}"

            while start_date <= end_date:
                next_date = start_date + relativedelta(months=60)
                url = base_url.format(
                    start_date.strftime("%Y-%m-%d"),
                    min(next_date, end_date).strftime("%Y-%m-%d"),
                )
                url = url + f"&apikey={api_key}"
                urls.append(url)
                start_date = next_date

            return urls

        for symbol in symbols:
            end_date = (
                query.end_date
                if query.end_date is not None
                else datetime.today().date()
            )

            urls = (
                generate_urls(symbol, query.start_date, end_date)
                if query.start_date and end_date
                else [
                    f"https://financialmodelingprep.com/stable/historical-market-capitalization?symbol={symbol}&limit=5000&apikey={api_key}"
                ]
            )
            data = await get_data_urls(urls, **kwargs)

            if not data:
                warnings.warn(f"No data was found for: {symbol}")
                continue

            results.extend(data)

        return results

    @staticmethod
    def transform_data(
        query: FmpHistoricalMarketCapQueryParams,
        data: list,
        **kwargs: Any,
    ) -> list[FmpHistoricalMarketCapData]:
        """Return the transformed data."""
        if not data:
            raise EmptyDataError("No data was returned for the given symbols.")
        symbols = query.symbol.split(",")
        return [
            FmpHistoricalMarketCapData.model_validate(d)
            for d in sorted(
                data,
                key=lambda x: (
                    x.get("date", len(symbols)),
                    -(x.get("marketCap", 0) or 0),
                ),
            )
        ]
