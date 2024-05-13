"""Cboe Options Chains Model."""

# pylint: disable=invalid-name, unused-argument

from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_cboe.utils.helpers import (
    TICKER_EXCEPTIONS,
    get_company_directory,
    get_index_directory,
)
from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.options_chains import (
    OptionsChainsData,
    OptionsChainsQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import amake_request
from pandas import DataFrame, DatetimeIndex, Series, to_datetime
from pydantic import Field


class CboeOptionsChainsQueryParams(OptionsChainsQueryParams):
    """CBOE Options Chains Query.

    Source: https://www.cboe.com/
    """

    use_cache: bool = Field(
        default=True,
        description="When True, the company directories will be cached for"
        + "24 hours and are used to validate symbols."
        + " The results of the function are not cached. Set as False to bypass.",
    )


class CboeOptionsChainsData(OptionsChainsData):
    """CBOE Options Chains Data."""

    last_trade_timestamp: Optional[datetime] = Field(
        description="Last trade timestamp of the option.", default=None
    )
    dte: int = Field(description="Days to expiration for the option.")


class CboeOptionsChainsFetcher(
    Fetcher[
        CboeOptionsChainsQueryParams,
        List[CboeOptionsChainsData],
    ]
):
    """Transform the query, extract and transform the data from the CBOE endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> CboeOptionsChainsQueryParams:
        """Transform the query."""
        return CboeOptionsChainsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CboeOptionsChainsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Return the raw data from the Cboe endpoint."""
        symbol = query.symbol.replace("^", "").split(",")[0].upper()
        INDEXES = await get_index_directory(use_cache=query.use_cache)
        SYMBOLS = await get_company_directory(use_cache=query.use_cache)
        INDEXES = INDEXES.set_index("index_symbol")

        if symbol not in SYMBOLS.index:
            raise RuntimeError(f"{symbol} was not found in the Cboe options directory.")

        quotes_url = (
            f"https://cdn.cboe.com/api/global/delayed_quotes/options/_{symbol}.json"
            if symbol in TICKER_EXCEPTIONS or symbol in INDEXES.index
            else f"https://cdn.cboe.com/api/global/delayed_quotes/options/{symbol}.json"
        )
        results = await amake_request(quotes_url)
        return results  # type: ignore

    @staticmethod
    def transform_data(
        query: CboeOptionsChainsQueryParams,
        data: Dict,
        **kwargs: Any,
    ) -> AnnotatedResult[List[CboeOptionsChainsData]]:
        """Transform the data to the standard format."""
        if not data:
            raise EmptyDataError()
        results_metadata = {}
        options = data.get("data", {}).pop("options", [])
        change_percent = data["data"].get("percent_change", None)
        iv30_percent = data["data"].get("iv30_change_percent", None)
        if change_percent:
            change_percent = change_percent / 100
        if iv30_percent:
            iv30_percent = iv30_percent / 100
        last_timestamp = data["data"].get("last_trade_time", None)
        if last_timestamp:
            last_timestamp = to_datetime(
                last_timestamp, format="%Y-%m-%dT%H:%M:%S"
            ).strftime("%Y-%m-%d %H:%M:%S")
        results_metadata.update(
            {
                "symbol": data["data"].get("symbol"),
                "security_type": data["data"].get("security_type", None),
                "bid": data["data"].get("bid", None),
                "bid_size": data["data"].get("bid_size", None),
                "ask": data["data"].get("ask", None),
                "ask_size": data["data"].get("ask_size", None),
                "open": data["data"].get("open", None),
                "high": data["data"].get("high", None),
                "low": data["data"].get("low", None),
                "close": data["data"].get("close", None),
                "volume": data["data"].get("volume", None),
                "current_price": data["data"].get("current_price", None),
                "prev_close": data["data"].get("prev_day_close", None),
                "change": data["data"].get("price_change", None),
                "change_percent": change_percent,
                "iv30": data["data"].get("iv30", None),
                "iv30_change": data["data"].get("iv30_change", None),
                "iv30_change_percent": iv30_percent,
                "last_tick": data["data"].get("tick", None),
                "last_trade_timestamp": last_timestamp,
            }
        )

        options_df = DataFrame.from_records(options)

        options_df = options_df.rename(
            columns={
                "option": "contract_symbol",
                "iv": "implied_volatility",
                "theo": "theoretical_price",
                "percent_change": "change_percent",
                "prev_day_close": "prev_close",
                "last_trade_time": "last_trade_timestamp",
            }
        )

        # Parses the option symbols into columns for expiration, strike, and option_type

        option_df_index = options_df["contract_symbol"].str.extractall(
            r"^(?P<Ticker>\D*)(?P<expiration>\d*)(?P<option_type>\D*)(?P<strike>\d*)"
        )
        option_df_index = option_df_index.reset_index().drop(
            columns=["match", "level_0"]
        )
        option_df_index.option_type = option_df_index.option_type.str.replace(
            "C", "call"
        ).str.replace("P", "put")
        option_df_index.strike = [ele.lstrip("0") for ele in option_df_index.strike]
        option_df_index.strike = Series(option_df_index.strike).astype(float)
        option_df_index.strike = option_df_index.strike * (1 / 1000)
        option_df_index.strike = option_df_index.strike.to_list()
        option_df_index.expiration = [
            ele.lstrip("1") for ele in option_df_index.expiration
        ]
        option_df_index.expiration = DatetimeIndex(
            option_df_index.expiration, yearfirst=True
        ).astype(str)
        option_df_index = option_df_index.drop(columns=["Ticker"])

        # Joins the parsed symbol into the dataframe.

        quotes = option_df_index.join(options_df)

        now = datetime.now()
        temp = DatetimeIndex(quotes.expiration)
        temp_ = (temp - now).days + 1
        quotes["dte"] = temp_

        quotes["last_trade_timestamp"] = (
            to_datetime(quotes["last_trade_timestamp"], format="%Y-%m-%dT%H:%M:%S")
            .fillna(value="-")
            .replace("-", None)
        )
        quotes = quotes.set_index(
            keys=["expiration", "strike", "option_type"]
        ).sort_index()
        quotes["open_interest"] = quotes["open_interest"].astype("int64")
        quotes["volume"] = quotes["volume"].astype("int64")
        quotes["bid_size"] = quotes["bid_size"].astype("int64")
        quotes["ask_size"] = quotes["ask_size"].astype("int64")
        quotes["prev_close"] = round(quotes["prev_close"], 2)
        quotes["change_percent"] = round(quotes["change_percent"] / 100, 4)

        return AnnotatedResult(
            result=[
                CboeOptionsChainsData.model_validate(d)
                for d in quotes.reset_index().to_dict("records")
            ],
            metadata=results_metadata,
        )
