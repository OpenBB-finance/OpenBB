"""FMP Cryptos Historical Price Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Literal, Optional

from dateutil.relativedelta import relativedelta
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.crypto_historical import (
    CryptoHistoricalData,
    CryptoHistoricalQueryParams,
)
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class FMPCryptoHistoricalQueryParams(CryptoHistoricalQueryParams):
    """
    FMP Crypto Historical Price Query.

    Source:
    https://site.financialmodelingprep.com/developer/docs/cryptocurrency-historical-data-api/#Historical-Daily-Prices
    """

    __alias_dict__ = {"start_date": "from", "end_date": "to"}
    __json_schema_extra__ = {
        "symbol": {"multiple_items_allowed": True},
        "interval": {"choices": ["1m", "5m", "15m", "30m", "1h", "4h", "1d"]},
    }

    interval: Literal["1m", "5m", "15m", "30m", "1h", "4h", "1d"] = Field(
        default="1d", description=QUERY_DESCRIPTIONS.get("interval", "")
    )


class FMPCryptoHistoricalData(CryptoHistoricalData):
    """FMP Crypto Historical Price Data."""

    __alias_dict__ = {
        "change_percent": "changeOverTime",
    }

    adj_close: Optional[float] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("adj_close", "")
    )
    change: Optional[float] = Field(
        default=None,
        description="Change in the price from the previous close.",
    )
    change_percent: Optional[float] = Field(
        default=None,
        description="Change in the price from the previous close, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )


class FMPCryptoHistoricalFetcher(
    Fetcher[
        FMPCryptoHistoricalQueryParams,
        list[FMPCryptoHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FMPCryptoHistoricalQueryParams:
        """Transform the query params. Start and end dates are set to 1 year interval."""
        transformed_params = params

        now = datetime.now().date()
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=1)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return FMPCryptoHistoricalQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: FMPCryptoHistoricalQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the FMP endpoint."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        from openbb_core.provider.utils.errors import EmptyDataError
        from openbb_core.provider.utils.helpers import (
            amake_request,
            get_querystring,
        )
        from openbb_fmp.utils.helpers import get_interval, response_callback
        from warnings import warn

        api_key = credentials.get("fmp_api_key") if credentials else ""

        interval = get_interval(query.interval)

        base_url = "https://financialmodelingprep.com/api/v3"
        query_str = get_querystring(query.model_dump(), ["symbol"])

        def get_url_params(symbol: str) -> str:
            url_params = f"{symbol}?{query_str}&apikey={api_key}"
            url = f"{base_url}/historical-chart/{interval}/{url_params}"
            if interval == "1day":
                url = f"{base_url}/historical-price-full/{url_params}"
            return url

        symbols = query.symbol.split(",")

        results: list = []
        messages: list = []

        async def get_one(symbol):
            """Get data for one symbol."""

            url = get_url_params(symbol)
            data: list = []

            response = await amake_request(url, response_callback=response_callback)

            if isinstance(response, dict) and response.get("Error Message"):
                message = f"Error fetching data for {symbol}: {response.get('Error Message', '')}"
                warn(message)
                messages.append(message)

            if not response:
                message = f"No data found for {symbol}."
                warn(message)
                messages.append(message)

            if isinstance(response, list) and len(response) > 0:
                data = response
                if len(symbols) > 1:
                    for d in data:
                        d["symbol"] = symbol

            if isinstance(response, dict) and response.get("historical"):
                data = response["historical"]
                if len(symbols) > 1:
                    for d in data:
                        d["symbol"] = symbol

            if data:
                results.extend(data)

        tasks = [get_one(symbol) for symbol in symbols]

        await asyncio.gather(*tasks)

        if not results:
            raise EmptyDataError(
                f"{str(','.join(messages)).replace(',',' ') if messages else 'No data found'}"
            )

        return results

    @staticmethod
    def transform_data(
        query: FMPCryptoHistoricalQueryParams, data: list[dict], **kwargs: Any
    ) -> list[FMPCryptoHistoricalData]:
        """Return the transformed data."""

        # Get rid of duplicate fields.
        to_pop = ["label", "changePercent", "unadjustedVolume"]
        results: list[FMPCryptoHistoricalData] = []

        for d in sorted(
            data,
            key=lambda x: (
                (x["date"], x["symbol"])
                if len(query.symbol.split(",")) > 1
                else x["date"]
            ),
            reverse=False,
        ):
            _ = [d.pop(pop) for pop in to_pop if pop in d]
            if d.get("unadjusted_volume") and d["adjusted_volume"] == d.get("volume"):
                _ = d.pop("unadjusted_volume", None)
            results.append(FMPCryptoHistoricalData.model_validate(d))

        return results
