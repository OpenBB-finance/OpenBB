"""YFinance Equity Profile Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_info import (
    EquityInfoData,
    EquityInfoQueryParams,
)
from pydantic import Field, field_validator


class YFinanceEquityProfileQueryParams(EquityInfoQueryParams):
    """YFinance Equity Profile Query."""

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}


class YFinanceEquityProfileData(EquityInfoData):
    """YFinance Equity Profile Data."""

    __alias_dict__ = {
        "name": "longName",
        "issue_type": "quoteType",
        "stock_exchange": "exchange",
        "first_stock_price_date": "firstTradeDateEpochUtc",
        "exchange_timezone": "timeZoneFullName",
        "industry_category": "industry",
        "hq_country": "country",
        "hq_address1": "address1",
        "hq_address_city": "city",
        "hq_address_postal_code": "zip",
        "hq_state": "state",
        "business_phone_no": "phone",
        "company_url": "website",
        "long_description": "longBusinessSummary",
        "employees": "fullTimeEmployees",
        "market_cap": "marketCap",
        "shares_outstanding": "sharesOutstanding",
        "shares_float": "floatShares",
        "shares_implied_outstanding": "impliedSharesOutstanding",
        "shares_short": "sharesShort",
        "dividend_yield": "yield",
    }

    exchange_timezone: Optional[str] = Field(
        description="The timezone of the exchange.",
        default=None,
    )
    issue_type: Optional[str] = Field(
        description="The issuance type of the asset.",
        default=None,
    )
    currency: Optional[str] = Field(
        description="The currency in which the asset is traded.", default=None
    )
    market_cap: Optional[int] = Field(
        description="The market capitalization of the asset.",
        default=None,
    )
    shares_outstanding: Optional[int] = Field(
        description="The number of listed shares outstanding.",
        default=None,
    )
    shares_float: Optional[int] = Field(
        description="The number of shares in the public float.",
        default=None,
    )
    shares_implied_outstanding: Optional[int] = Field(
        description=(
            "Implied shares outstanding of common equity"
            "assuming the conversion of all convertible subsidiary equity into common."
        ),
        default=None,
    )
    shares_short: Optional[int] = Field(
        description="The reported number of shares short.",
        default=None,
    )
    dividend_yield: Optional[float] = Field(
        description="The dividend yield of the asset, as a normalized percent.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    beta: Optional[float] = Field(
        description="The beta of the asset relative to the broad market.",
        default=None,
    )

    @field_validator("first_stock_price_date", mode="before", check_fields=False)
    @classmethod
    def validate_first_trade_date(cls, v):
        """Validate first stock price date."""
        # pylint: disable=import-outside-toplevel
        from datetime import timezone  # noqa
        from openbb_core.provider.utils.helpers import safe_fromtimestamp  # noqa

        return safe_fromtimestamp(v, tz=timezone.utc).date() if v else None


class YFinanceEquityProfileFetcher(
    Fetcher[YFinanceEquityProfileQueryParams, List[YFinanceEquityProfileData]]
):
    """YFinance Equity Profile fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> YFinanceEquityProfileQueryParams:
        """Transform the query."""
        return YFinanceEquityProfileQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: YFinanceEquityProfileQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the raw data from YFinance."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        from curl_adapter import CurlCffiAdapter
        from openbb_core.app.model.abstract.error import OpenBBError
        from openbb_core.provider.utils.errors import EmptyDataError
        from openbb_core.provider.utils.helpers import get_requests_session
        from warnings import warn
        from yfinance import Ticker

        symbols = query.symbol.split(",")
        results = []
        fields = [
            "symbol",
            "longName",
            "exchange",
            "timeZoneFullName",
            "quoteType",
            "firstTradeDateEpochUtc",
            "currency",
            "sharesOutstanding",
            "floatShares",
            "impliedSharesOutstanding",
            "sharesShort",
            "sector",
            "industry",
            "address1",
            "city",
            "state",
            "zip",
            "country",
            "phone",
            "website",
            "fullTimeEmployees",
            "longBusinessSummary",
            "marketCap",
            "yield",
            "dividendYield",
            "beta",
        ]
        messages: list = []
        session = get_requests_session()
        session.mount("https://", CurlCffiAdapter())
        session.mount("http://", CurlCffiAdapter())

        async def get_one(symbol):
            """Get the data for one ticker symbol."""
            result: dict = {}
            ticker: dict = {}
            try:
                ticker = Ticker(
                    symbol,
                    session=session,
                ).get_info()
            except Exception as e:
                messages.append(
                    f"Error getting data for {symbol} -> {e.__class__.__name__}: {e}"
                )
            if ticker:
                for field in fields:
                    if field in ticker:
                        result[
                            field.replace("dividendYield", "dividend_yield").replace(
                                "issueType", "issue_type"
                            )
                        ] = ticker.get(field, None)
                if result:
                    results.append(result)

        tasks = [get_one(symbol) for symbol in symbols]

        await asyncio.gather(*tasks)

        if not results and messages:
            raise OpenBBError("\n".join(messages))

        if not results and not messages:
            raise EmptyDataError("No data was returned for any symbol")

        if results and messages:
            for message in messages:
                warn(message)

        return results

    @staticmethod
    def transform_data(
        query: YFinanceEquityProfileQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[YFinanceEquityProfileData]:
        """Transform the data."""
        return [YFinanceEquityProfileData.model_validate(d) for d in data]
