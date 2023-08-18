from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.cash_flows import CashFlowStatementData
from openbb_provider.utils.helpers import get_querystring
from pydantic import validator

from openbb_polygon.utils.helpers import get_data
from openbb_polygon.utils.types import PolygonFundamentalQueryParams

# noqa: E501


class PolygonCashFlowStatementQueryParams(PolygonFundamentalQueryParams):
    __doc__ = PolygonFundamentalQueryParams.__doc__


class PolygonCashFlowStatementData(CashFlowStatementData):
    """Cash Flow Statement Data."""

    class Config:
        fields = {"date": "start_date"}

    @validator("symbol", pre=True, check_fields=False)
    def symbol_from_tickers(cls, v):
        if isinstance(v, list):
            return ",".join(v)
        return v


class PolygonCashFlowStatementFetcher(
    Fetcher[
        PolygonCashFlowStatementQueryParams,
        List[PolygonCashFlowStatementData],
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> PolygonCashFlowStatementQueryParams:
        return PolygonCashFlowStatementQueryParams(**params)

    @staticmethod
    def extract_data(
        query: PolygonCashFlowStatementQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> dict:
        api_key = credentials.get("polygon_api_key") if credentials else ""

        base_url = "https://api.polygon.io/vX/reference/financials"
        query_string = get_querystring(query.dict(by_alias=True), [])
        request_url = f"{base_url}?{query_string}&apiKey={api_key}"
        data = get_data(request_url, **kwargs)["results"]

        if len(data) == 0:
            raise RuntimeError("No Cash Flow Statement found")

        return data

    @staticmethod
    def transform_data(
        data: dict,
    ) -> List[PolygonCashFlowStatementData]:
        FIELDS = [
            "net_cash_flow_from_financing_activities",
            "net_cash_flow_from_investing_activities",
            "net_cash_flow_from_operating_activities",
            "net_cash_flow_continuing",
            "net_cash_flow_from_financing_activities_continuing",
            "net_cash_flow_from_investing_activities_continuing",
            "net_cash_flow_from_operating_activities_continuing",
            "net_cash_flow",
        ]

        to_return = []
        for item in data:
            new = {"start_date": item["start_date"], "cik": item["cik"]}
            if cf := item["financials"]["cash_flow_statement"]:
                for field in FIELDS:
                    new[field] = cf[field].get("value", 0)

            to_return.append(PolygonCashFlowStatementData(**new))
        return to_return
