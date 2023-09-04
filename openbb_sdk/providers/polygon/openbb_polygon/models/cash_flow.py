from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.cash_flow import CashFlowStatementData
from openbb_provider.utils.helpers import get_querystring
from pydantic import validator

from openbb_polygon.utils.helpers import get_data
from openbb_polygon.utils.types import PolygonFundamentalQueryParams


class PolygonCashFlowStatementQueryParams(PolygonFundamentalQueryParams):
    """Polygon Fundamental QueryParams.

    Source: https://polygon.io/docs/stocks#!/get_vx_reference_financials
    """


class PolygonCashFlowStatementData(CashFlowStatementData):
    """Return Balance Sheet Data."""

    class Config:
        fields = {"date": "start_date"}

    @validator("symbol", pre=True, check_fields=False)
    def symbol_from_tickers(cls, v):  # pylint: disable=no-self-argument
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
            raise RuntimeError("No balance sheet found")

        return data

    @staticmethod
    def transform_data(
        data: dict,
    ) -> List[PolygonCashFlowStatementData]:
        transformed_data = []

        for item in data:
            sub_data = {
                key: value["value"]
                for key, value in item["financials"]["cash_flow_statement"].items()
            }
            sub_data["start_date"] = item["start_date"]
            sub_data["cik"] = item["cik"]
            sub_data["symbol"] = item["tickers"]
            transformed_data.append(PolygonCashFlowStatementData(**sub_data))

        return transformed_data
