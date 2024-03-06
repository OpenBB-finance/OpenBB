"""Cboe Equity Info Model."""

# pylint: disable=invalid-name,too-many-locals, expression-not-assigned
from typing import Any, Dict, List, Optional

from openbb_cboe.utils.helpers import (
    TICKER_EXCEPTIONS,
    get_company_directory,
    get_index_directory,
)
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_quote import (
    EquityQuoteData,
    EquityQuoteQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import amake_requests
from pandas import DataFrame, concat
from pydantic import Field


class CboeEquityQuoteQueryParams(EquityQuoteQueryParams):
    """CBOE Equity Quote Query.

    Source: https://www.cboe.com/
    """

    __json_schema_extra__ = {"symbol": ["multiple_items_allowed"]}

    use_cache: bool = Field(
        default=True,
        description="When True, the company directories will be cached for"
        + " 24 hours and are used to validate symbols."
        + " The results of the function are not cached. Set as False to bypass.",
    )


class CboeEquityQuoteData(EquityQuoteData):
    """CBOE Equity Quote Data."""

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

    iv30: Optional[float] = Field(
        default=None, description="The 30-day implied volatility of the stock."
    )
    iv30_change: Optional[float] = Field(
        default=None, description="Change in 30-day implied volatility of the stock."
    )
    iv30_change_percent: Optional[float] = Field(
        default=None,
        description="Change in 30-day implied volatility of the"
        + " stock as a normalized percentage value.",
    )
    iv30_annual_high: Optional[float] = Field(
        default=None, description="The 1-year high of 30-day implied volatility."
    )
    hv30_annual_high: Optional[float] = Field(
        default=None, description="The 1-year high of 30-day realized volatility."
    )
    iv30_annual_low: Optional[float] = Field(
        default=None, description="The 1-year low of 30-day implied volatility."
    )
    hv30_annual_low: Optional[float] = Field(
        default=None, description="The 1-year low of 30-dayrealized volatility."
    )
    iv60_annual_high: Optional[float] = Field(
        default=None, description="The 1-year high of 60-day implied volatility."
    )
    hv60_annual_high: Optional[float] = Field(
        default=None, description="The 1-year high of 60-day realized volatility."
    )
    iv60_annual_low: Optional[float] = Field(
        default=None, description="The 1-year low of 60-day implied volatility."
    )
    hv60_annual_low: Optional[float] = Field(
        default=None, description="The 1-year low of 60-day realized volatility."
    )
    iv90_annual_high: Optional[float] = Field(
        default=None, description="The 1-year high of 90-day implied volatility."
    )
    hv90_annual_high: Optional[float] = Field(
        default=None, description="The 1-year high of 90-day realized volatility."
    )
    iv90_annual_low: Optional[float] = Field(
        default=None, description="The 1-year low of 90-day implied volatility."
    )
    hv90_annual_low: Optional[float] = Field(
        default=None, description="The 1-year low of 90-day realized volatility."
    )


class CboeEquityQuoteFetcher(
    Fetcher[
        CboeEquityQuoteQueryParams,
        List[CboeEquityQuoteData],
    ]
):
    """Transform the query, extract and transform the data from the CBOE endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> CboeEquityQuoteQueryParams:
        """Transform the query."""
        return CboeEquityQuoteQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CboeEquityQuoteQueryParams,  # pylint: disable=unused-argument
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> DataFrame:
        """Return the raw data from the Cboe endpoint."""

        symbols = query.symbol.split(",")
        # First get the index and company directories so we know how to handle the ticker symbols.
        # Using cache for faster response times.
        SYMBOLS = await get_company_directory(use_cache=query.use_cache, **kwargs)
        INDEXES = await get_index_directory(use_cache=query.use_cache, **kwargs)
        INDEXES = INDEXES.set_index("index_symbol")

        # Create a list of European indices.
        EU_INDEXES = INDEXES[INDEXES["source"] == "eu_proprietary_index"]

        # Check all symbols and create a list of URLs to request.
        urls = []
        for symbol in symbols:
            base_url = "https://cdn.cboe.com/api/global/delayed_quotes/quotes/"
            url = (
                f"{base_url}_{symbol.replace('^', '')}.json"
                if symbol.replace("^", "") in INDEXES.index
                or symbol.replace("^", "") in TICKER_EXCEPTIONS
                else f"{base_url}{symbol.replace('^', '')}.json"
            )
            # European Indices require a different endpoint.
            if symbol in EU_INDEXES.index:
                eu_name = EU_INDEXES.at[symbol, "name"]
                _symbol = EU_INDEXES[EU_INDEXES["name"].str.contains(eu_name)].index[0]
                url = (
                    "https://cdn.cboe.com/api/global/european_indices/"
                    + f"index_quotes/{_symbol.replace('^', '')}.json"
                )
            urls.append(url)
        # Now make the requests.
        responses = await amake_requests(urls)
        if not responses:
            raise EmptyDataError()
        quotes_data = [d["data"] for d in responses]
        # There is no context for this data so we'll remove it.
        [d.pop("seqno") for d in quotes_data if "seqno" in d]
        [d.pop("exchange_id") for d in quotes_data if "exchange_id" in d]

        quotes = DataFrame(quotes_data)
        quotes.symbol = quotes.symbol.str.replace("^", "")
        quotes.symbol = [s.split("-")[0] for s in quotes.symbol]
        # Drop an additional symbol column from EU Indices.
        if "index" in quotes.columns:
            quotes = quotes.drop(columns="index")
        quotes = DataFrame(quotes).set_index("symbol")

        # Now get the URLs for the IV data.
        base_url = "https://cdn.cboe.com/api/global/delayed_quotes/historical_data/"
        iv_urls = []
        for symbol in symbols:
            iv_url = (
                base_url + f"_{symbol.replace('^', '')}.json"
                if symbol.replace("^", "") in TICKER_EXCEPTIONS
                or symbol.replace("^", "") in INDEXES.index
                else base_url + f"{symbol.replace('^', '')}.json"
            )
            # There is no IV data for the EU Indices, so we'll skip those symbols.
            if symbol not in EU_INDEXES.index:
                iv_urls.append(iv_url)

            # While iterating through the symbols, grab the name belonging to the ticker.
            if symbol.replace("^", "") in SYMBOLS.index:
                quotes.loc[symbol.replace("^", ""), "name"] = SYMBOLS.loc[
                    symbol.replace("^", ""), "name"
                ]
            if symbol.replace("^", "") in INDEXES.index:
                quotes.loc[symbol.replace("^", ""), "name"] = INDEXES.loc[
                    symbol.replace("^", ""), "name"
                ]
            if symbol.replace("^", "") in EU_INDEXES.index:
                quotes.loc[symbol.replace("^", ""), "name"] = EU_INDEXES.loc[
                    symbol.replace("^", ""), "name"
                ]

        # Now get the IV data.
        iv = DataFrame()
        iv_responses = await amake_requests(iv_urls)
        if iv_responses:
            iv_data = [d["data"] for d in iv_responses]
            iv = DataFrame(iv_data)
            iv["symbol"] = iv["symbol"].astype(str).str.replace("^", "")
            iv = iv.set_index("symbol")
        if not iv_responses:
            iv = DataFrame()

        # Merge the IV data with the quotes data.
        results = concat([quotes, iv], axis=1)

        if len(results) == 0:
            raise EmptyDataError()
        return results

    @staticmethod
    def transform_data(
        query: CboeEquityQuoteQueryParams, data: DataFrame, **kwargs: Any
    ) -> List[CboeEquityQuoteData]:
        """Transform the data to the standard format."""
        data = data.replace(0, None).dropna(how="all", axis=1)
        # We need to convert the percent columns to normalized values.
        percent_cols = [
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
        for col in percent_cols:
            if col in data.columns:
                data[col] = data[col] / 100
        data = data.dropna(how="all", axis=1).fillna("N/A").replace("N/A", None)
        return [
            CboeEquityQuoteData.model_validate(d)
            for d in data.reset_index().to_dict("records")
        ]
