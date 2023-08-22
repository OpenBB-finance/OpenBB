from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.balance_sheet import BalanceSheetData
from openbb_provider.utils.helpers import get_querystring
from pydantic import validator

from openbb_polygon.utils.helpers import get_data
from openbb_polygon.utils.types import PolygonFundamentalQueryParams


class PolygonBalanceSheetQueryParams(PolygonFundamentalQueryParams):
    """Polygon Fundamental QueryParams.

    Source: https://polygon.io/docs/stocks#!/get_vx_reference_financials
    """


class PolygonBalanceSheetData(BalanceSheetData):
    """Return Balance Sheet Data."""

    class Config:
        fields = {
            "date": "start_date",
            "equity": "total_equity",
            "total_liabilities_and_stockholders_equity": "liabilities_and_equity",
            "minority_interest": "equity_attributable_to_noncontrolling_interest",
        }

    @validator("symbol", pre=True, check_fields=False)
    def symbol_from_tickers(cls, v):  # pylint: disable=no-self-argument
        if isinstance(v, list):
            return ",".join(v)
        return v


class PolygonBalanceSheetFetcher(
    Fetcher[
        PolygonBalanceSheetQueryParams,
        List[PolygonBalanceSheetData],
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> PolygonBalanceSheetQueryParams:
        return PolygonBalanceSheetQueryParams(**params)

    @staticmethod
    def extract_data(
        query: PolygonBalanceSheetQueryParams,
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
    ) -> List[PolygonBalanceSheetData]:
        FIELDS = [
            "assets",
            "current_assets",
            "current_liabilities",
            "equity",
            "equity_attributable_to_noncontrolling_interest",
            "equity_attributable_to_parent",
            "liabilities",
            "liabilities_and_equity",
            "noncurrent_assets",
            "noncurrent_liabilities",
        ]

        to_return = []
        for item in data:
            new = {"start_date": item["start_date"], "cik": item["cik"]}
            if bs := item["financials"]["balance_sheet"]:
                for field in FIELDS:
                    new[field] = bs[field].get("value", 0)

            to_return.append(PolygonBalanceSheetData(**new))
        return to_return
