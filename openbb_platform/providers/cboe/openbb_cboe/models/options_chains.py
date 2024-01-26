"""Cboe Options Chains Model."""

# pylint: disable=invalid-name, unused-argument

from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_cboe.utils.helpers import (
    TICKER_EXCEPTIONS,
    get_company_directory,
    get_index_directory,
)
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
    ) -> List[Dict]:
        """Return the raw data from the Cboe endpoint"""

        symbol = query.symbol.replace("^", "").split(",")[0]
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

        return await amake_request(quotes_url)

    @staticmethod
    def transform_data(
        query: CboeOptionsChainsQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[CboeOptionsChainsData]:
        """Transform the data to the standard format"""

        if not data:
            raise EmptyDataError()

        options_df = DataFrame.from_records(data["data"]["options"])

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

        return [
            CboeOptionsChainsData.model_validate(d)
            for d in quotes.reset_index().to_dict("records")
        ]
