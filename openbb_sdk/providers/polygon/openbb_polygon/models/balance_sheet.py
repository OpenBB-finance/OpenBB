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
            "total_current_assets": "current_assets",
            "marketable_securities": "fixed_assets",
            "property_plant_equipment_net": "public_utilities_property_plant_and_equipment_net",
            "other_non_current_assets": "other_noncurrent_assets_of_regulated_entity",
            "total_non_current_assets": "noncurrent_assets",
            "total_assets": "assets",
            "total_current_liabilities": "current_liabilities",
            "other_non_current_liabilities": "other _noncurrent_liabilities_of_regulated_entity",
            "total_non_current_liabilities": "noncurrent_liabilities",
            "total_liabilities": "liabilities",
            "preferred_stock": "temporary_equity",
            "total_shareholder_equity": "temporary_equity_attributable_to_parent",
            "total_equity": "equity",
            "total_liabilities_and_shareholders_equity": "liabilities_and_equity",
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
        transformed_data = []

        for item in data:
            sub_data = {
                key: value["value"]
                for key, value in item["financials"]["balance_sheet"].items()
            }
            sub_data["start_date"] = item["start_date"]
            sub_data["cik"] = item["cik"]
            sub_data["symbol"] = item["tickers"]
            transformed_data.append(PolygonBalanceSheetData(**sub_data))

        return transformed_data
