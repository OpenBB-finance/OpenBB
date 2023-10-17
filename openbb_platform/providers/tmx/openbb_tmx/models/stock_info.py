"""TMX Stock Info fetcher"""
import concurrent.futures
import json
from datetime import date as dateType
from typing import Any, Dict, List, Optional, Union

import requests
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.stock_info import (
    StockInfoData,
    StockInfoQueryParams,
)
from openbb_tmx.utils.gql import GQL
from openbb_tmx.utils.helpers import get_random_agent
from pydantic import Field


class TmxStockInfoQueryParams(StockInfoQueryParams):
    """TMX Stock Info query params."""


class TmxStockInfoData(StockInfoData):
    """TMX Stock Info Data."""

    __alias_dict__ = {
        "open": "openPrice",
        "high": "dayHigh",
        "low": "dayLow",
        "change": "priceChange",
        "change_percent": "percentChange",
        "prev_close": "prevClose",
    }
    vwap: Optional[float] = Field(
        description="Current volume weighted average price.", default=None
    )
    volume: Optional[int] = Field(description="Current volume.", default=None)
    ma_21: Optional[float] = Field(
        description="Twenty-one day moving average.",
        default=None,
        alias="day21MovingAvg",
    )
    ma_50: Optional[float] = Field(
        description="Fifty day moving average.", default=None, alias="day50MovingAvg"
    )
    ma_200: Optional[float] = Field(
        description="Two hundred day moving average.",
        default=None,
        alias="day200MovingAvg",
    )
    one_year_high: Optional[float] = Field(
        description="Fifty-two week high.", default=None, alias="weeks52high"
    )
    one_year_low: Optional[float] = Field(
        description="Fifty-two week low.", default=None, alias="weeks52low"
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
        description="The dividend yield.", default=None, alias="dividendYield"
    )
    div_freq: Optional[str] = Field(
        description="The frequency of dividend payments.",
        default=None,
        alias="dividendFrequency",
    )
    div_ex_date: Optional[Union[dateType, str]] = Field(
        description="The ex-dividend date.", default=None, alias="exDividendDate"
    )
    div_pay_date: Optional[Union[dateType, str]] = Field(
        description="The next dividend ayment date.",
        default=None,
        alias="dividendPayDate",
    )
    div_growth_3y: Optional[Union[float, str]] = Field(
        description="The three year dividend growth.",
        default=None,
        alias="dividend3Years",
    )
    div_growth_5y: Optional[Union[float, str]] = Field(
        description="The five year dividend growth.",
        default=None,
        alias="dividend5Years",
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
    roe: Optional[Union[float, str]] = Field(
        description="The return on equity.", default=None, alias="returnOnEquity"
    )
    roa: Optional[Union[float, str]] = Field(
        description="The return on assets.", default=None, alias="returnOnAssets"
    )
    beta: Optional[Union[float, str]] = Field(
        description="The beta relative to the TSX Composite.", default=None
    )
    alpha: Optional[Union[float, str]] = Field(
        description="The alpha relative to the TSX Composite.", default=None
    )
    sector: Optional[str] = Field(
        description="The sector of the company.", default=None
    )
    industry: Optional[str] = Field(
        description="The industry of the company.", default=None
    )
    industry_group: Optional[str] = Field(
        description="The industry group of the company.",
        default=None,
        alias="qmdescription",
    )
    issue_type: Optional[str] = Field(
        description="The issuance type of the asset.", default=None, alias="issueType"
    )
    exchange_name: Optional[str] = Field(
        description="The exchange name of the listing.",
        default=None,
        alias="exchangeName",
    )
    exchange_short_name: Optional[str] = Field(
        description="The exchange short name.", alias="exShortName"
    )
    exchange_code: Optional[str] = Field(
        description="The exchange code.", default=None, alias="exchangeCode"
    )
    data_type: Optional[str] = Field(
        description="The type of asset class data.", default=None, alias="datatype"
    )
    website: Optional[str] = Field(
        description="The website of the company.", default=None
    )
    email: Optional[str] = Field(description="The email of the company.", default=None)
    phone: Optional[str] = Field(
        description="The phone number of the company.",
        default=None,
        alias="phoneNumber",
    )
    address: Optional[str] = Field(
        description="The full address of the company.",
        default=None,
        alias="fullAddress",
    )
    employees: Optional[Union[int, str]] = Field(
        description="The number of employees.", default=None
    )
    description_short: Optional[str] = Field(
        description="The short description of the asset.",
        default=None,
        alias="shortDescription",
    )
    description_long: Optional[str] = Field(
        description="The long description of the asset.",
        default=None,
        alias="longDescription",
    )


class TmxStockInfoFetcher(
    Fetcher[
        TmxStockInfoQueryParams,
        List[TmxStockInfoData],
    ]
):
    """Transform the query, extract and transform the data from the TMX endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TmxStockInfoQueryParams:
        """Transform the query."""
        return TmxStockInfoQueryParams(**params)

    @staticmethod
    def get_stock_info_data(symbol: str) -> Dict:
        """Requests data for a single ticker symbol, to send to extract_data."""

        symbol = symbol.upper().replace("-", ".").replace(".TO", "").replace(".TSX", "")

        payload = GQL.stock_info_payload.copy()
        payload["variables"]["symbol"] = symbol

        data = []
        url = "https://app-money.tmx.com/graphql"
        r = requests.post(
            url,
            data=json.dumps(payload),
            headers={
                "authority": "app-money.tmx.com",
                "referer": f"https://money.tmx.com/en/quote/{symbol}",
                "locale": "en",
                "Content-Type": "application/json",
                "User-Agent": get_random_agent(),
                "Accept": "*/*",
            },
            timeout=3,
        )
        try:
            if r.status_code == 403:
                raise RuntimeError(f"HTTP error - > {r.text}")
            else:
                data = r.json()["data"]["getQuoteBySymbol"]
        except Exception as e:
            raise (e)

        return data

    @staticmethod
    def extract_data(
        query: TmxStockInfoQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the TMX endpoint."""

        # Check if the symbol is in list-form.
        symbols = (
            query.symbol
            if isinstance(query.symbol, list) and "," not in query.symbol
            else [query.symbol]
        )

        # If the symbol is a string list, convert to an iterable.
        if "," in query.symbol and not isinstance(query.symbol, list):
            symbols = query.symbol.split(",") if "," in query.symbol else query.symbol

        # If the symbol is a string and a single ticker, convert it to an iterable.
        if "," not in query.symbol and isinstance(query.symbol, str):
            symbols = [query.symbol]

        # The list where the results will be stored and appended to.
        results = []

        # Get the data for each symbol and append results to the list.
        def get_one(symbol: str) -> None:
            data = TmxStockInfoFetcher.get_stock_info_data(symbol)
            if data is not None:
                results.append(data)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(get_one, symbols)

        return sorted(results, key=lambda x: x["percentChange"], reverse=True)

    @staticmethod
    def transform_data(data: List[Dict], **kwargs: Any) -> List[TmxStockInfoData]:
        """Return the transformed data."""
        return [TmxStockInfoData.model_validate(d) for d in data]
