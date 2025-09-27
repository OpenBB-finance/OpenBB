"""e-Stat Statistical Data Model.

ATTRIBUTION: This service uses API functions from e-Stat,
however its contents are not guaranteed by government.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.bls_series import (
    SeriesData,
    SeriesQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

from openbb_estat.utils.helpers import (
    format_estat_date,
    handle_estat_error,
    validate_stats_params,
)


class EstatStatisticalDataQueryParams(SeriesQueryParams):
    """e-Stat Statistical Data Query Parameters."""

    stats_data_id: Optional[str] = Field(
        default=None,
        description="Statistical dataset ID (e.g., '0003433219'). Use symbol field or this.",
        alias="symbol",
    )
    stats_code: Optional[str] = Field(
        default=None,
        description="Statistical survey code (e.g., '00200521' for population census).",
    )
    category_code: Optional[str] = Field(
        default=None,
        description="Category code to filter data.",
    )
    area_code: Optional[str] = Field(
        default=None,
        description="Area code (prefecture, municipality, etc.).",
    )
    search_kind: Optional[str] = Field(
        default="1",
        description="Search type: '1' for statistics, '2' for regional mesh statistics.",
    )
    collect_area: Optional[str] = Field(
        default=None,
        description="Collection area for aggregated data (API v3.0).",
    )
    explanation_get_flg: Optional[str] = Field(
        default="Y",
        description="Include explanations: 'Y' or 'N'.",
    )


class EstatStatisticalData(SeriesData):
    """e-Stat Statistical Data."""

    stats_code: Optional[str] = Field(
        default=None,
        description="Statistical table code.",
    )
    category_name: Optional[str] = Field(
        default=None,
        description="Category name in Japanese and English.",
    )
    area_name: Optional[str] = Field(
        default=None,
        description="Area name (prefecture, municipality, etc.).",
    )
    unit: Optional[str] = Field(
        default=None,
        description="Unit of measurement.",
    )


class EstatStatisticalDataFetcher(Fetcher[EstatStatisticalDataQueryParams, List[EstatStatisticalData]]):
    """e-Stat Statistical Data Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> EstatStatisticalDataQueryParams:
        """Transform query parameters."""
        return EstatStatisticalDataQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: EstatStatisticalDataQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract data from e-Stat API."""
        # pylint: disable=import-outside-toplevel

        import aiohttp

        api_key = credentials.get("api_key") if credentials else ""

        base_url = "https://api.e-stat.go.jp/rest/3.0/app/json"

        # Build API parameters
        stats_data_id = query.stats_data_id or query.symbol
        if not stats_data_id:
            raise ValueError("Statistical dataset ID (stats_data_id or symbol) is required")

        params = {
            "appId": api_key,
            "lang": "E",  # English
            "statsDataId": stats_data_id,
            "metaGetFlg": "Y",  # Include metadata
            "cntGetFlg": "N",   # Don't include record count only
            "explanationGetFlg": query.explanation_get_flg or "Y",
            "annotationGetFlg": "Y",   # Include annotations
            "sectionHeaderFlg": "1",   # Include section headers
            "searchKind": query.search_kind or "1",
        }

        # Add optional parameters
        if query.area_code:
            params["cdArea"] = query.area_code
        if query.category_code:
            params["cdCat01"] = query.category_code
        if query.collect_area:
            params["collectArea"] = query.collect_area
        if query.start_date:
            params["startTime"] = query.start_date.strftime("%Y%m")
        if query.end_date:
            params["endTime"] = query.end_date.strftime("%Y%m")
        if query.stats_code:
            params["statsCode"] = query.stats_code

        # Validate and clean parameters
        params = validate_stats_params(params)

        async with aiohttp.ClientSession() as session:
            url = f"{base_url}/getStatsData"
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    raise Exception(f"API request failed with status {response.status}")

                data = await response.json()

                if "GET_STATS_DATA" not in data:
                    raise EmptyDataError("No data returned from e-Stat API")

                get_stats_data = data["GET_STATS_DATA"]

                # Check for API errors
                if "RESULT" in get_stats_data:
                    result = get_stats_data["RESULT"]
                    status = result.get("STATUS", -1)
                    if status != 0:
                        error_msg = result.get("ERROR_MSG", "Unknown error")
                        formatted_error = handle_estat_error(status, error_msg)
                        raise EmptyDataError(formatted_error)

                # Extract statistical data
                if "STATISTICAL_DATA" not in get_stats_data:
                    raise EmptyDataError("No statistical data found in response")

                stats_data = get_stats_data["STATISTICAL_DATA"]

                if "DATA_INF" not in stats_data or "VALUE" not in stats_data["DATA_INF"]:
                    raise EmptyDataError("No data values found in response")

                values = stats_data["DATA_INF"]["VALUE"]
                return values if isinstance(values, list) else [values]

    @staticmethod
    def transform_data(
        query: EstatStatisticalDataQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[EstatStatisticalData]:
        """Transform the data."""
        results = []

        for item in data:
            try:
                # Parse e-Stat data structure
                date_str = item.get("@time")
                formatted_date = format_estat_date(date_str)
                if formatted_date:
                    date = datetime.strptime(formatted_date, "%Y-%m-%d").date()
                else:
                    continue  # Skip records without valid dates (required by SeriesData)

                # Parse value - it's stored as a string in '$' field
                value_str = item.get("$")
                if value_str is None:
                    continue  # Skip records without values
                try:
                    value = float(value_str)
                except (ValueError, TypeError):
                    continue  # Skip records without valid values

                # Create result using the SeriesData symbol field
                result = EstatStatisticalData(
                    date=date,
                    value=value,
                    symbol=item.get("@tab", ""),  # Required by SeriesData
                    stats_code=item.get("@tab"),
                    category_name=item.get("@cat01"),
                    area_name=item.get("@area"),
                    unit=item.get("@unit"),
                )
                results.append(result)
            except (ValueError, TypeError, KeyError):
                continue  # Skip malformed records

        return sorted(results, key=lambda x: (x.date or datetime.min.date(), x.symbol))
