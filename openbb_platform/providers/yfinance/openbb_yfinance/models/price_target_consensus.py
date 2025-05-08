"""YFinance Price Target Consensus Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Optional

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.price_target_consensus import (
    PriceTargetConsensusData,
    PriceTargetConsensusQueryParams,
)
from pydantic import Field, field_validator


class YFinancePriceTargetConsensusQueryParams(PriceTargetConsensusQueryParams):
    """YFinance Price Target Consensus Query."""

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def check_symbol(cls, value):
        """Check the symbol."""
        if not value:
            raise OpenBBError("Error: Symbol is a required field for yFinance.")
        return value


class YFinancePriceTargetConsensusData(PriceTargetConsensusData):
    """YFinance Price Target Consensus Data."""

    __alias_dict__ = {
        "target_high": "targetHighPrice",
        "target_low": "targetLowPrice",
        "target_consensus": "targetMeanPrice",
        "target_median": "targetMedianPrice",
        "recommendation": "recommendationKey",
        "recommendation_mean": "recommendationMean",
        "number_of_analysts": "numberOfAnalystOpinions",
        "current_price": "currentPrice",
    }

    recommendation: Optional[str] = Field(
        default=None,
        description="Recommendation - buy, sell, etc.",
    )
    recommendation_mean: Optional[float] = Field(
        default=None,
        description="Mean recommendation score where 1 is strong buy and 5 is strong sell.",
    )
    number_of_analysts: Optional[int] = Field(
        default=None, description="Number of analysts providing opinions."
    )
    current_price: Optional[float] = Field(
        default=None,
        description="Current price of the stock.",
    )
    currency: Optional[str] = Field(
        default=None,
        description="Currency the stock is priced in.",
    )


class YFinancePriceTargetConsensusFetcher(
    Fetcher[
        YFinancePriceTargetConsensusQueryParams, List[YFinancePriceTargetConsensusData]
    ]
):
    """YFinance Price Target Consensus Fetcher."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any],
    ) -> YFinancePriceTargetConsensusQueryParams:
        """Transform the query."""
        return YFinancePriceTargetConsensusQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: YFinancePriceTargetConsensusQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the raw data from YFinance."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        from curl_adapter import CurlCffiAdapter
        from openbb_core.provider.utils.errors import EmptyDataError
        from openbb_core.provider.utils.helpers import get_requests_session
        from warnings import warn
        from yfinance import Ticker

        symbols = query.symbol.split(",")  # type: ignore
        results = []
        fields = [
            "symbol",
            "currentPrice",
            "currency",
            "targetHighPrice",
            "targetLowPrice",
            "targetMeanPrice",
            "targetMedianPrice",
            "recommendationMean",
            "recommendationKey",
            "numberOfAnalystOpinions",
        ]
        session = get_requests_session()
        session.mount("https://", CurlCffiAdapter())
        session.mount("http://", CurlCffiAdapter())
        messages: list = []

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
                    f"Error getting data for {symbol}: {e.__class__.__name__}: {e}"
                )
            if ticker:
                for field in fields:
                    if field in ticker:
                        result[field] = ticker.get(field, None)
                if result and result.get("numberOfAnalystOpinions") is not None:
                    results.append(result)

        tasks = [get_one(symbol) for symbol in symbols]

        await asyncio.gather(*tasks)

        if not results and not messages:
            raise EmptyDataError("No data was returned for the given symbol(s)")

        if not results and messages:
            raise OpenBBError("\n".join(messages))

        if results and messages:
            for message in messages:
                warn(message)

        return results

    @staticmethod
    def transform_data(
        query: YFinancePriceTargetConsensusQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[YFinancePriceTargetConsensusData]:
        """Transform the data."""
        return [YFinancePriceTargetConsensusData.model_validate(d) for d in data]
