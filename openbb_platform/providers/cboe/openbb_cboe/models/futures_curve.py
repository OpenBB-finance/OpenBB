"""CBOE Futures Curve Model."""

# IMPORT STANDARD
from typing import Any, Dict, List, Optional

from openbb_cboe.utils.helpers import get_settlement_prices
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.futures_curve import (
    FuturesCurveData,
    FuturesCurveQueryParams,
)
from pydantic import Field


class CboeFuturesCurveQueryParams(FuturesCurveQueryParams):
    """CBOE Futures Curve Query.

    Source: https://www.cboe.com/
    """


class CboeFuturesCurveData(FuturesCurveData):
    """CBOE Futures Curve Data."""

    symbol: str = Field(description="The trading symbol for the tenor of future.")


class CboeFuturesCurveFetcher(
    Fetcher[
        CboeFuturesCurveQueryParams,
        List[CboeFuturesCurveData],
    ]
):
    """Transform the query, extract and transform the data from the CBOE endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> CboeFuturesCurveQueryParams:
        return CboeFuturesCurveQueryParams(**params)

    @staticmethod
    def extract_data(
        query: CboeFuturesCurveQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the CBOE endpoint."""

        query.symbol = query.symbol.upper()
        FUTURES = get_settlement_prices(settlement_date=query.date)
        if len(FUTURES) == 0:
            return []

        if query.symbol not in FUTURES["product"].unique().tolist():
            raise RuntimeError(
                "The symbol, "
                f"{query.symbol}"
                ", is not valid.  Chose from: "
                f"{FUTURES['product'].unique().tolist()}"
            )

        data = get_settlement_prices(settlement_date=query.date)
        data = data[data["product"] == query.symbol]

        return data[["expiration", "symbol", "price"]].to_dict("records")

    @staticmethod
    def transform_data(
        query: CboeFuturesCurveQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[CboeFuturesCurveData]:
        return [CboeFuturesCurveData.model_validate(d) for d in data]
