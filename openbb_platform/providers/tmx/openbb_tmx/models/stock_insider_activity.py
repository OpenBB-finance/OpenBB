"""TMX Company Insider Acitivity Model"""

from typing import Any, Dict, List, Optional

import pandas as pd
from openbb_provider.abstract.data import Data
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.helpers import to_snake_case
from openbb_tmx.utils.helpers import get_company_insider_activity
from pydantic import Field


class TmxStockInsiderActivityQueryParams(QueryParams):
    """TMX Company Insiders Query Params"""

    symbol: str = Field(description="The ticker symbol of the company")


class TmxStockInsiderActivityData(Data):
    """TMX Company Insiders Data"""

    period: str = Field(description="The period of the activity", alias="periodkey")
    bought: int = Field(description="The number of shares bought", alias="buyShares")
    sold: int = Field(description="The number of shares sold", alias="soldShares")
    net_activity: int = Field(description="The net activity", alias="netActivity")
    total_shares: int = Field(
        description="The total number of shares traded.", alias="totalShares"
    )


class TmxStockInsiderActivityFetcher(
    Fetcher[
        TmxStockInsiderActivityQueryParams,
        List[TmxStockInsiderActivityData],
    ]
):
    """TMX Company Insiders Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TmxStockInsiderActivityQueryParams:
        """Transform the query."""
        return TmxStockInsiderActivityQueryParams(**params)

    @staticmethod
    def extract_data(
        query: TmxStockInsiderActivityQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the TMX endpoint."""

        results = []

        query.symbol = (
            query.symbol.upper()
            .replace(".TO", "")
            .replace(".TSX", "")
            .replace("-", ".")
        )

        data = get_company_insider_activity(query.symbol)

        if data is not None and "activitySummary" in data:
            _data = pd.DataFrame(data["activitySummary"])
            _data["periodkey"] = [to_snake_case(c) for c in _data["periodkey"]]
            results = _data.to_dict(orient="records")
        return results

    @staticmethod
    def transform_data(data: List[Dict]) -> List[TmxStockInsiderActivityData]:
        """Transform the data."""
        return [TmxStockInsiderActivityData.model_validate(d) for d in data]
