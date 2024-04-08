"""TMX Equity Profile fetcher."""

# pylint: disable=unused-argument

import asyncio
import json
import warnings
from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, List, Optional, Union

from numpy import nan
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_quote import (
    EquityQuoteData,
    EquityQuoteQueryParams,
)
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from openbb_tmx.utils import gql
from openbb_tmx.utils.helpers import get_data_from_gql, get_random_agent
from pydantic import Field, field_validator

_warn = warnings.warn


class TmxEquityQuoteQueryParams(EquityQuoteQueryParams):
    """TMX Equity Profile query params."""

    __json_schema_extra__ = {"symbol": ["multiple_items_allowed"]}


class TmxEquityQuoteData(EquityQuoteData):
    """TMX Equity Profile Data."""

    __alias_dict__ = {
        "last_price": "price",
        "open": "openPrice",
        "high": "dayHigh",
        "low": "dayLow",
        "change": "priceChange",
        "change_percent": "percentChange",
        "prev_close": "prevClose",
        "stock_exchange": "exchangeCode",
        "industry_category": "industry",
        "industry_group": "qmdescription",
        "exchange": "exchangeCode",
        "security_type": "datatype",
    }
    name: Optional[str] = Field(default=None, description="The name of the asset.")
    security_type: Optional[str] = Field(
        description="The issuance type of the asset.", default=None
    )
    exchange: Optional[str] = Field(
        default=None,
        description="The listing exchange code.",
    )
    sector: Optional[str] = Field(default=None, description="The sector of the asset.")
    industry_category: Optional[str] = Field(
        default=None,
        description="The industry category of the asset.",
    )
    industry_group: Optional[str] = Field(
        default=None,
        description="The industry group of the asset.",
    )
    last_price: Optional[float] = Field(
        default=None, description="The last price of the asset."
    )
    open: Optional[float] = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("open", ""),
    )
    high: Optional[float] = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("high", ""),
    )
    low: Optional[float] = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("low", ""),
    )
    close: Optional[float] = Field(
        default=None,
    )
    vwap: Optional[float] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("vwap", "")
    )
    volume: Optional[int] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("vwap", "")
    )
    prev_close: Optional[float] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("prev_close", "")
    )
    change: Optional[float] = Field(
        default=None,
        description="The change in price.",
    )
    change_percent: Optional[float] = Field(
        default=None,
        description="The change in price as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    year_high: Optional[float] = Field(
        description="Fifty-two week high.", default=None, alias="weeks52high"
    )
    year_low: Optional[float] = Field(
        description="Fifty-two week low.", default=None, alias="weeks52low"
    )
    ma_21: Optional[float] = Field(
        description="Twenty-one day moving average.",
        default=None,
        alias="day21MovingAvg",
    )
    ma_50: Optional[float] = Field(
        description="Fifty day moving average.", default=None, alias="day50MovingAvg"
    )
    ma_200: Optional[float] = Field(
        description="Two-hundred day moving average.",
        default=None,
        alias="day200MovingAvg",
    )
    volume_avg_10d: Optional[int] = Field(
        description="Ten day average volume.", default=None, alias="averageVolume10D"
    )
    volume_avg_30d: Optional[int] = Field(
        description="Thirty day average volume.", default=None, alias="averageVolume30D"
    )
    volume_avg_50d: Optional[int] = Field(
        description="Fifty day average volume.", default=None, alias="averageVolume50D"
    )
    market_cap: Optional[int] = Field(
        description="Market capitalization.", default=None, alias="MarketCap"
    )
    market_cap_all_classes: Optional[int] = Field(
        description="Market capitalization of all share classes.",
        default=None,
        alias="MarketCapAllClasses",
    )
    div_amount: Optional[float] = Field(
        description="The most recent dividend amount.",
        default=None,
        alias="dividendAmount",
    )
    div_currency: Optional[str] = Field(
        description="The currency the dividend is paid in.",
        default=None,
        alias="dividendCurrency",
    )
    div_yield: Optional[float] = Field(
        description="The dividend yield as a normalized percentage.",
        default=None,
        alias="dividendYield",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    div_freq: Optional[str] = Field(
        description="The frequency of dividend payments.",
        default=None,
        alias="dividendFrequency",
    )
    div_ex_date: Optional[dateType] = Field(
        description="The ex-dividend date.", default=None, alias="exDividendDate"
    )
    div_pay_date: Optional[dateType] = Field(
        description="The next dividend ayment date.",
        default=None,
        alias="dividendPayDate",
    )
    div_growth_3y: Optional[Union[float, str]] = Field(
        description="The three year dividend growth as a normalized percentage.",
        default=None,
        alias="dividend3Years",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    div_growth_5y: Optional[Union[float, str]] = Field(
        description="The five year dividend growth as a normalized percentage.",
        default=None,
        alias="dividend5Years",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    pe: Optional[Union[float, str]] = Field(
        description="The price to earnings ratio.", default=None, alias="peRatio"
    )
    eps: Optional[Union[float, str]] = Field(
        description="The earnings per share.", default=None
    )
    debt_to_equity: Optional[Union[float, str]] = Field(
        description="The debt to equity ratio.", default=None, alias="totalDebtToEquity"
    )
    price_to_book: Optional[Union[float, str]] = Field(
        description="The price to book ratio.", default=None, alias="priceToBook"
    )
    price_to_cf: Optional[Union[float, str]] = Field(
        description="The price to cash flow ratio.",
        default=None,
        alias="priceToCashFlow",
    )
    return_on_equity: Optional[Union[float, str]] = Field(
        description="The return on equity, as a normalized percentage.",
        default=None,
        alias="returnOnEquity",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    return_on_assets: Optional[Union[float, str]] = Field(
        description="The return on assets, as a normalized percentage.",
        default=None,
        alias="returnOnAssets",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    beta: Optional[Union[float, str]] = Field(
        description="The beta relative to the TSX Composite.", default=None
    )
    alpha: Optional[Union[float, str]] = Field(
        description="The alpha relative to the TSX Composite.", default=None
    )
    shares_outstanding: Optional[int] = Field(
        description="The number of listed shares outstanding.",
        default=None,
        alias="shareOutStanding",
    )
    shares_escrow: Optional[int] = Field(
        description="The number of shares held in escrow.",
        default=None,
        alias="sharesESCROW",
    )
    shares_total: Optional[int] = Field(
        description="The total number of shares outstanding from all classes.",
        default=None,
        alias="totalSharesOutStanding",
    )

    @field_validator(
        "div_ex_date",
        "div_pay_date",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return the datetime object from the date string."""
        if v:
            try:
                return datetime.strptime(v, "%Y-%m-%d").date()
            except ValueError:
                return datetime.strptime(v, "%Y-%m-%d %H:%M:%S.%f").date()
        return None

    @field_validator(
        "return_on_equity",
        "return_on_assets",
        "div_yield",
        "div_growth_3y",
        "div_growth_5y",
        "change_percent",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def normalize_percent(cls, v):
        """Return percents as normalized percentage points."""
        return round(float(v) / 100, 6) if v else None


class TmxEquityQuoteFetcher(
    Fetcher[
        TmxEquityQuoteQueryParams,
        List[TmxEquityQuoteData],
    ]
):
    """Transform the query, extract and transform the data from the TMX endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TmxEquityQuoteQueryParams:
        """Transform the query."""
        return TmxEquityQuoteQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TmxEquityQuoteQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the TMX endpoint."""
        symbols = query.symbol.split(",")

        # The list where the results will be stored and appended to.
        results: List[Dict] = []
        user_agent = get_random_agent()

        url = "https://app-money.tmx.com/graphql"

        async def create_task(symbol: str, results) -> None:
            """Make a POST request to the TMX GraphQL endpoint for a single symbol."""
            symbol = (
                symbol.upper().replace("-", ".").replace(".TO", "").replace(".TSX", "")
            )

            payload = gql.stock_info_payload.copy()
            payload["variables"]["symbol"] = symbol

            data = {}
            r = await get_data_from_gql(
                method="POST",
                url=url,
                data=json.dumps(payload),
                headers={
                    "authority": "app-money.tmx.com",
                    "referer": f"https://money.tmx.com/en/quote/{symbol}",
                    "locale": "en",
                    "Content-Type": "application/json",
                    "User-Agent": user_agent,
                    "Accept": "*/*",
                },
                timeout=3,
            )
            if r["data"].get("getQuoteBySymbol"):
                data = r["data"]["getQuoteBySymbol"]
                results.append(data)
            else:
                _warn(f"Could not get data for {symbol}.")

        tasks = [create_task(symbol, results) for symbol in symbols]
        await asyncio.gather(*tasks)
        return results

    @staticmethod
    def transform_data(
        query: TmxEquityQuoteQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[TmxEquityQuoteData]:
        """Return the transformed data."""
        # Remove the items associated with `equity.profile()`.
        items_list = [
            "shortDescription",
            "longDescription",
            "website",
            "phoneNumber",
            "fullAddress",
            "email",
            "issueType",
            "exchangeName",
            "employees",
            "exShortName",
        ]
        data = [{k: v for k, v in d.items() if k not in items_list} for d in data]
        # Replace all NaN values with None.
        for d in data:
            for k, v in d.items():
                if v in (nan, 0, ""):
                    d[k] = None
        # Sort the data by the order of the symbols in the query.
        symbols = query.symbol.split(",")
        symbol_to_index = {symbol: index for index, symbol in enumerate(symbols)}
        data = sorted(data, key=lambda d: symbol_to_index[d["symbol"]])

        return [TmxEquityQuoteData.model_validate(d) for d in data]
