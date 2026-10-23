"""Cboe Equity Quote Model."""

from typing import TYPE_CHECKING, Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_quote import (
    EquityQuoteData,
    EquityQuoteQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

from openbb_cboe.utils.constants import EQUITY_CHOICES_ENDPOINT

if TYPE_CHECKING:
    from pandas import DataFrame

PERCENT_COLUMNS = [
    "price_change_percent",
    "iv30",
    "iv30_change",
    "iv30_change_percent",
    "iv30_annual_high",
    "iv30_annual_low",
    "iv60_annual_high",
    "iv60_annual_low",
    "iv90_annual_high",
    "iv90_annual_low",
    "hv30_annual_high",
    "hv30_annual_low",
    "hv60_annual_high",
    "hv60_annual_low",
    "hv90_annual_high",
    "hv90_annual_low",
]


class CboeEquityQuoteQueryParams(EquityQuoteQueryParams):
    """Cboe Equity Quote Query.

    Source: https://www.cboe.com/
    """

    __json_schema_extra__ = {
        "symbol": {
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": EQUITY_CHOICES_ENDPOINT,
                "style": {"popupWidth": 600},
            },
        }
    }

    use_cache: bool = Field(
        default=True,
        description="When True, the company directories will be cached for"
        + " 24 hours and are used to validate symbols."
        + " The results of the function are not cached. Set as False to bypass.",
    )


class CboeEquityQuoteData(EquityQuoteData):
    """Cboe Equity Quote Data."""

    __alias_dict__ = {
        "last_timestamp": "last_trade_time",
        "prev_close": "prev_day_close",
        "asset_type": "security_type",
        "last_price": "current_price",
        "year_high": "annual_high",
        "year_low": "annual_low",
        "last_tick": "tick",
        "change": "price_change",
        "change_percent": "price_change_percent",
    }

    iv30: float | None = Field(
        default=None,
        serialization_alias="iv30",
        json_schema_extra={"x-widget_config": {"headerName": "IV30"}},
        description="The 30-day implied volatility of the stock.",
    )
    iv30_change: float | None = Field(
        default=None,
        serialization_alias="iv30_change",
        json_schema_extra={"x-widget_config": {"headerName": "IV30 Change"}},
        description="Change in 30-day implied volatility of the stock.",
    )
    iv30_change_percent: float | None = Field(
        default=None,
        serialization_alias="iv30_change_percent",
        json_schema_extra={"x-widget_config": {"headerName": "IV30 Change %"}},
        description="Change in 30-day implied volatility of the"
        + " stock as a normalized percentage value.",
    )
    iv30_annual_high: float | None = Field(
        default=None,
        serialization_alias="iv30_annual_high",
        json_schema_extra={"x-widget_config": {"headerName": "IV30 Annual High"}},
        description="The 1-year high of 30-day implied volatility.",
    )
    hv30_annual_high: float | None = Field(
        default=None,
        serialization_alias="hv30_annual_high",
        json_schema_extra={"x-widget_config": {"headerName": "HV30 Annual High"}},
        description="The 1-year high of 30-day realized volatility.",
    )
    iv30_annual_low: float | None = Field(
        default=None,
        serialization_alias="iv30_annual_low",
        json_schema_extra={"x-widget_config": {"headerName": "IV30 Annual Low"}},
        description="The 1-year low of 30-day implied volatility.",
    )
    hv30_annual_low: float | None = Field(
        default=None,
        serialization_alias="hv30_annual_low",
        json_schema_extra={"x-widget_config": {"headerName": "HV30 Annual Low"}},
        description="The 1-year low of 30-day realized volatility.",
    )
    iv60_annual_high: float | None = Field(
        default=None,
        serialization_alias="iv60_annual_high",
        json_schema_extra={"x-widget_config": {"headerName": "IV60 Annual High"}},
        description="The 1-year high of 60-day implied volatility.",
    )
    hv60_annual_high: float | None = Field(
        default=None,
        serialization_alias="hv60_annual_high",
        json_schema_extra={"x-widget_config": {"headerName": "HV60 Annual High"}},
        description="The 1-year high of 60-day realized volatility.",
    )
    iv60_annual_low: float | None = Field(
        default=None,
        serialization_alias="iv60_annual_low",
        json_schema_extra={"x-widget_config": {"headerName": "IV60 Annual Low"}},
        description="The 1-year low of 60-day implied volatility.",
    )
    hv60_annual_low: float | None = Field(
        default=None,
        serialization_alias="hv60_annual_low",
        json_schema_extra={"x-widget_config": {"headerName": "HV60 Annual Low"}},
        description="The 1-year low of 60-day realized volatility.",
    )
    iv90_annual_high: float | None = Field(
        default=None,
        serialization_alias="iv90_annual_high",
        json_schema_extra={"x-widget_config": {"headerName": "IV90 Annual High"}},
        description="The 1-year high of 90-day implied volatility.",
    )
    hv90_annual_high: float | None = Field(
        default=None,
        serialization_alias="hv90_annual_high",
        json_schema_extra={"x-widget_config": {"headerName": "HV90 Annual High"}},
        description="The 1-year high of 90-day realized volatility.",
    )
    iv90_annual_low: float | None = Field(
        default=None,
        serialization_alias="iv90_annual_low",
        json_schema_extra={"x-widget_config": {"headerName": "IV90 Annual Low"}},
        description="The 1-year low of 90-day implied volatility.",
    )
    hv90_annual_low: float | None = Field(
        default=None,
        serialization_alias="hv90_annual_low",
        json_schema_extra={"x-widget_config": {"headerName": "HV90 Annual Low"}},
        description="The 1-year low of 90-day realized volatility.",
    )


class CboeEquityQuoteFetcher(
    Fetcher[
        CboeEquityQuoteQueryParams,
        list[CboeEquityQuoteData],
    ]
):
    """Transform the query, extract and transform the data from the Cboe endpoints."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> CboeEquityQuoteQueryParams:
        """Transform the query."""
        return CboeEquityQuoteQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CboeEquityQuoteQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> "DataFrame":
        """Return the raw data from the Cboe endpoint."""
        from openbb_core.provider.utils.helpers import amake_requests
        from pandas import DataFrame, concat

        from openbb_cboe.utils.helpers import (
            TICKER_EXCEPTIONS,
            get_company_directory,
            get_index_directory,
        )

        symbols = query.symbol.split(",")
        company_directory = await get_company_directory(
            use_cache=query.use_cache, **kwargs
        )
        indexes = await get_index_directory(use_cache=query.use_cache, **kwargs)
        indexes = indexes.set_index("index_symbol")
        eu_indexes = indexes[indexes["source"] == "eu_proprietary_index"]
        urls: list = []

        for symbol in symbols:
            base_url = "https://cdn.cboe.com/api/global/delayed_quotes/quotes/"
            url = (
                f"{base_url}_{symbol.replace('^', '')}.json"
                if symbol.replace("^", "") in indexes.index
                or symbol.replace("^", "") in TICKER_EXCEPTIONS
                else f"{base_url}{symbol.replace('^', '')}.json"
            )

            if symbol in eu_indexes.index:
                eu_name = eu_indexes.at[symbol, "name"]
                _symbol = eu_indexes[eu_indexes["name"].str.contains(eu_name)].index[0]
                url = (
                    "https://cdn.cboe.com/api/global/european_indices/"
                    + f"index_quotes/{_symbol.replace('^', '')}.json"
                )

            urls.append(url)

        responses = await amake_requests(urls)

        if not responses:
            raise EmptyDataError()

        quotes_data = [d["data"] for d in responses]

        for d in quotes_data:
            d.pop("seqno", None)
            d.pop("exchange_id", None)

        quotes = DataFrame(quotes_data)
        quotes.symbol = quotes.symbol.str.replace("^", "")
        quotes.symbol = [s.split("-")[0] for s in quotes.symbol]

        if "index" in quotes.columns:
            quotes = quotes.drop(columns="index")

        quotes = DataFrame(quotes).set_index("symbol")
        base_url = "https://cdn.cboe.com/api/global/delayed_quotes/historical_data/"
        iv_urls: list = []

        for symbol in symbols:
            iv_url = (
                base_url + f"_{symbol.replace('^', '')}.json"
                if symbol.replace("^", "") in TICKER_EXCEPTIONS
                or symbol.replace("^", "") in indexes.index
                else base_url + f"{symbol.replace('^', '')}.json"
            )

            if symbol not in eu_indexes.index:
                iv_urls.append(iv_url)

            for directory in (company_directory, indexes, eu_indexes):
                if symbol.replace("^", "") in directory.index:
                    quotes.loc[symbol.replace("^", ""), "name"] = directory.loc[
                        symbol.replace("^", ""), "name"
                    ]

        iv = DataFrame()
        iv_responses = await amake_requests(iv_urls)

        if iv_responses:
            iv = DataFrame([d["data"] for d in iv_responses])
            iv["symbol"] = iv["symbol"].astype(str).str.replace("^", "")
            iv = iv.set_index("symbol")

        results = concat([quotes, iv], axis=1)

        if len(results) == 0:  # pragma: no cover
            raise EmptyDataError()

        return results

    @staticmethod
    def transform_data(
        query: CboeEquityQuoteQueryParams, data: "DataFrame", **kwargs: Any
    ) -> list[CboeEquityQuoteData]:
        """Transform the data to the standard format."""
        data = data.replace(0, None).dropna(how="all", axis=1)

        for col in PERCENT_COLUMNS:
            if col in data.columns:
                data[col] = data[col] / 100

        data = data.dropna(how="all", axis=1).fillna("N/A").replace("N/A", None)

        return [
            CboeEquityQuoteData.model_validate(d)
            for d in data.reset_index().to_dict("records")
        ]
