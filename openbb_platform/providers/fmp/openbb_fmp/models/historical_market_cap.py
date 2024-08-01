"""FMP Historical Market Cap Model."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from warnings import warn

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.historical_market_cap import (
    HistoricalMarketCapData,
    HistoricalMarketCapQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError


class FmpHistoricalMarketCapQueryParams(HistoricalMarketCapQueryParams):
    """FMP Historical Market Cap Query.

    Source: https://site.financialmodelingprep.com/developer/docs#historical-market-cap-company-information

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
        List[FmpHistoricalMarketCapData],
    ]
):
    """FMP Historical Market Cap Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FmpHistoricalMarketCapQueryParams:
        """Transform the query params."""
        # pylint: disable=import-outside-toplevel
        from dateutil.relativedelta import relativedelta

        transformed_params = params
        now = datetime.now().date()

        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=5)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return FmpHistoricalMarketCapQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: FmpHistoricalMarketCapQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        # pylint: disable=import-outside-toplevel
        from dateutil.relativedelta import relativedelta
        from openbb_core.provider.utils.helpers import amake_requests

        symbols = query.symbol.split(",")
        api_key = credentials.get("fmp_api_key") if credentials else ""

        urls: List = []
        results: List = []

        def generate_urls(symbol, start_date, end_date):
            """Generate URLs for each 5-year interval between start_date and end_date."""
            base_url = f"https://financialmodelingprep.com/api/v3/historical-market-capitalization/{symbol}?limit=5000"
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

        for symbol in symbols:
            generate_urls(symbol, query.start_date, query.end_date)

        async def response_callback(response, _):
            """Return the response data."""
            res = await response.json()
            if res:
                results.extend(res)

        await amake_requests(urls, response_callback, **kwargs)

        return results

    @staticmethod
    def transform_data(
        query: FmpHistoricalMarketCapQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[FmpHistoricalMarketCapData]:
        """Return the transformed data."""
        # pylint: disable=import-outside-toplevel
        from pandas import DataFrame

        if not data:
            raise EmptyDataError("The request was returned empty.")

        symbols = query.symbol.split(",")
        df = DataFrame(data)

        for symbol in symbols:
            if symbol not in df["symbol"].unique():
                warn(f"No data was found for: {symbol}")

        records = df.sort_values(by=["date", "marketCap"]).to_dict(orient="records")

        return [FmpHistoricalMarketCapData.model_validate(d) for d in records]
