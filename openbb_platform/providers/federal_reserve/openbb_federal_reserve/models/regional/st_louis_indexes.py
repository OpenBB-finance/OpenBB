"""Federal Reserve Bank of St. Louis National Index Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

_INDEX_SERIES = {
    "financial_stress_index": "STLFSI4",
    "price_pressures": "STLPPM",
    "economic_news_index": "STLENI",
}


class FederalReserveStLouisNationalIndexQueryParams(QueryParams):
    """St. Louis Fed National Index Query Parameters."""

    __json_schema_extra__ = {
        "index": {
            "x-widget_config": {
                "options": [
                    {
                        "label": "Financial Stress Index",
                        "value": "financial_stress_index",
                    },
                    {"label": "Price Pressures", "value": "price_pressures"},
                    {"label": "Economic News Index", "value": "economic_news_index"},
                ]
            }
        }
    }

    index: Literal[
        "financial_stress_index", "price_pressures", "economic_news_index"
    ] = Field(
        default="financial_stress_index",
        description="The index to return: 'financial_stress_index' (STLFSI4, weekly),"
        + " 'price_pressures' (STLPPM, monthly), or 'economic_news_index'"
        + " (STLENI, quarterly).",
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveStLouisNationalIndexData(Data):
    """St. Louis Fed National Index Data."""

    date: dateType = Field(description="The observation date.")
    index: str = Field(description="The requested index name.")
    value: float | None = Field(default=None, description="The index value.")


class FederalReserveStLouisNationalIndexFetcher(
    Fetcher[
        FederalReserveStLouisNationalIndexQueryParams,
        list[FederalReserveStLouisNationalIndexData],
    ]
):
    """St. Louis Fed National Index Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveStLouisNationalIndexQueryParams:
        """Transform the query params."""
        return FederalReserveStLouisNationalIndexQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveStLouisNationalIndexQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the selected index CSV from FRED."""
        from openbb_federal_reserve.utils.st_louis import fetch_fred_graph_csv

        text = fetch_fred_graph_csv(_INDEX_SERIES[query.index])
        if not text:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": text}]

    @staticmethod
    def transform_data(
        query: FederalReserveStLouisNationalIndexQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveStLouisNationalIndexData]:
        """Parse the two-column CSV and apply the date filters."""
        from io import StringIO

        from pandas import isna, read_csv, to_datetime, to_numeric

        frame = read_csv(StringIO(data[0]["_raw"]))
        frame.columns = ["date", "value"]
        frame["date"] = to_datetime(frame["date"]).dt.date
        frame["value"] = to_numeric(frame["value"].replace(".", None), errors="coerce")
        frame["index"] = query.index

        if query.start_date:
            frame = frame[frame["date"] >= query.start_date]
        if query.end_date:
            frame = frame[frame["date"] <= query.end_date]

        return [
            FederalReserveStLouisNationalIndexData.model_validate(
                {
                    k: (None if isinstance(v, float) and isna(v) else v)
                    for k, v in row.items()
                }
            )
            for row in frame.sort_values("date").to_dict(orient="records")
        ]
