"""Finviz Price Target Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.price_target import (
    PriceTargetData,
    PriceTargetQueryParams,
)
from pydantic import Field


class FinvizPriceTargetQueryParams(PriceTargetQueryParams):
    """Finviz Price Target Query.

    Source: https://finviz.com/quote.ashx?
    """

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}


class FinvizPriceTargetData(PriceTargetData):
    """Finviz Price Target Data."""

    __alias_dict__ = {
        "published_date": "Date",
        "status": "Status",
        "analyst_company": "Outer",
        "rating_change": "Rating",
    }

    status: Optional[str] = Field(
        default=None,
        description="The action taken by the firm."
        + " This could be 'Upgrade', 'Downgrade', 'Reiterated', etc.",
    )
    rating_change: Optional[str] = Field(
        default=None,
        description="The rating given by the analyst."
        + " This could be 'Buy', 'Sell', 'Underweight', etc."
        + " If the rating is a revision, the change is indicated by '->'",
    )


class FinvizPriceTargetFetcher(
    Fetcher[FinvizPriceTargetQueryParams, List[FinvizPriceTargetData]]
):
    """Finviz Price Target Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FinvizPriceTargetQueryParams:
        """Transform the query params."""
        return FinvizPriceTargetQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FinvizPriceTargetQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Finviz endpoint."""
        # pylint: disable=import-outside-toplevel
        from finvizfinance import util  # noqa
        from finvizfinance.quote import finvizfinance
        from openbb_core.app.model.abstract.error import OpenBBError
        from openbb_core.provider.utils.errors import EmptyDataError
        from openbb_core.provider.utils.helpers import get_requests_session
        from pandas import DataFrame
        from warnings import warn

        results: List[Dict] = []
        util.session = get_requests_session()
        messages: List = []

        def get_one(symbol) -> List[Dict]:
            """Get the data for one symbol."""
            price_targets = DataFrame()
            result: List[Dict] = []
            try:
                data = finvizfinance(symbol)
                price_targets = data.ticker_outer_ratings()
                if price_targets is None or len(price_targets) == 0:
                    messages.append(f"Failed to get data for {symbol}")
                    return result
                price_targets["symbol"] = symbol
                prices = (
                    price_targets["Price"].astype(str).str.replace("$", "", regex=False)
                )
                price_targets["price_target"] = (
                    prices.str.split("→").str.get(0).str.strip()
                )
                price_targets["adj_price_target"] = (
                    prices.str.split("→").str.get(-1).str.strip()
                )
                price_targets.loc[
                    price_targets["adj_price_target"] == price_targets["price_target"],
                    "price_target",
                ] = None
                price_targets = price_targets.replace("", None).drop(columns="Price")
            except Exception as e:  # pylint: disable=W0718
                messages.append(f"Failed to get data for {symbol} -> {e}")
                return result
            result = price_targets.to_dict(orient="records")
            return result

        symbols = query.symbol.split(",") if query.symbol else []

        for symbol in symbols:
            result = get_one(symbol)
            if result:
                results.extend(result)

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
        query: FinvizPriceTargetQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[FinvizPriceTargetData]:
        """Transform and validate the raw data."""
        return [FinvizPriceTargetData.model_validate(d) for d in data]
