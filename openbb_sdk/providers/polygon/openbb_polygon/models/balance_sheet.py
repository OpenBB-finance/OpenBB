from datetime import date as dateType
from typing import Dict, List, Optional

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.helpers import data_transformer, get_querystring
from openbb_provider.models.balance_sheet import (
    BalanceSheetData,
    BalanceSheetQueryParams,
)


from pydantic import Field

from openbb_polygon.utils.helpers import get_data
from openbb_polygon.utils.types import PolygonFundamentalQueryParams


class PolygonBalanceSheetQueryParams(PolygonFundamentalQueryParams):
    __doc__ = PolygonFundamentalQueryParams.__doc__


class PolygonBalanceSheetData(Data):
    cik: Optional[str]
    start_date: dateType = Field(alias="date")
    assets: Optional[int]
    current_assets: Optional[int]
    current_liabilities: Optional[int]
    equity: Optional[int] = Field(alias="total_equity")
    equity_attributable_to_noncontrolling_interest: Optional[int]
    equity_attributable_to_parent: Optional[int]
    liabilities: Optional[int]
    liabilities_and_equity: Optional[int] = Field(
        alias="total_liabilities_and_stockholders_equity"
    )
    noncurrent_assets: Optional[int]
    noncurrent_liabilities: Optional[int]


class PolygonBalanceSheetFetcher(
    Fetcher[
        BalanceSheetQueryParams,
        BalanceSheetData,
        PolygonBalanceSheetQueryParams,
        PolygonBalanceSheetData,
    ]
):
    @staticmethod
    def transform_query(
        query: BalanceSheetQueryParams, extra_params: Optional[Dict] = None
    ) -> PolygonBalanceSheetQueryParams:
        period = "annual" if query.period == "annually" else "quarterly"
        return PolygonBalanceSheetQueryParams(
            symbol=query.symbol, period=period, **extra_params if extra_params else {}  # type: ignore
        )

    @staticmethod
    def extract_data(
        query: PolygonBalanceSheetQueryParams, credentials: Optional[Dict[str, str]]
    ) -> List[PolygonBalanceSheetData]:
        if credentials:
            api_key = credentials.get("polygon_api_key")

        base_url = "https://api.polygon.io/vX/reference/financials"
        query_string = get_querystring(query.dict(), [])
        request_url = f"{base_url}?{query_string}&apiKey={api_key}"
        data = get_data(request_url)["results"]

        if len(data) == 0:
            raise RuntimeError("No balance sheet found")

        to_return = []
        for item in data:
            new = {"start_date": item["start_date"]}
            new["cik"] = item["cik"]
            bs = item["financials"]["balance_sheet"]
            # TODO: Unpack this dynamically to avoid hardcoding.
            new["assets"] = bs["assets"].get("value")
            new["current_assets"] = bs["current_assets"].get("value")
            new["current_liabilities"] = bs["current_liabilities"].get("value")
            new["equity"] = bs["equity"].get("value")
            new["equity_attributable_to_noncontrolling_interest"] = bs[
                "equity_attributable_to_noncontrolling_interest"
            ].get("value")
            new["equity_attributable_to_parent"] = bs[
                "equity_attributable_to_parent"
            ].get("value")
            new["equity"] = bs["equity"].get("value")
            new["liabilities"] = bs["liabilities"].get("value")
            new["liabilities_and_equity"] = bs["liabilities_and_equity"].get("value")
            new["noncurrent_assets"] = bs["noncurrent_assets"].get("value")
            new["noncurrent_liabilities"] = bs["noncurrent_liabilities"].get("value")

            to_return.append(PolygonBalanceSheetData(**new))
        return to_return

    @staticmethod
    def transform_data(
        data: List[PolygonBalanceSheetData],
    ) -> List[BalanceSheetData]:
        return data_transformer(data, BalanceSheetData)
