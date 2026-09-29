"""Federal Reserve Bank of St. Louis National Index Model."""

from datetime import date as dateType
from typing import Any

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
            "multiple_items_allowed": True,
            "x-widget_config": {
                "options": [
                    {
                        "label": "Financial Stress Index",
                        "value": "financial_stress_index",
                    },
                    {"label": "Price Pressures", "value": "price_pressures"},
                    {"label": "Economic News Index", "value": "economic_news_index"},
                ],
                "multiSelect": True,
            },
        }
    }

    index: str | None = Field(
        default=None,
        description="One or more indexes (columns) to return; the default returns"
        " all three: 'financial_stress_index' (STLFSI4, weekly), 'price_pressures'"
        " (STLPPM, monthly), and 'economic_news_index' (STLENI, quarterly).",
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
    financial_stress_index: float | None = Field(
        default=None,
        description="St. Louis Fed Financial Stress Index (STLFSI4, weekly).",
    )
    price_pressures: float | None = Field(
        default=None,
        description="St. Louis Fed Price Pressures Measure (STLPPM, monthly).",
    )
    economic_news_index: float | None = Field(
        default=None,
        description="St. Louis Fed Economic News Index real-GDP nowcast"
        " (STLENI, quarterly).",
    )


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
        """Download each selected index CSV from FRED."""
        from openbb_federal_reserve.utils.st_louis import fetch_fred_graph_csv

        requested = (
            [name.strip() for name in query.index.split(",") if name.strip()]
            if query.index
            else list(_INDEX_SERIES)
        )
        selected = [name for name in requested if name in _INDEX_SERIES]
        data = [
            {"index": name, "_raw": fetch_fred_graph_csv(_INDEX_SERIES[name])}
            for name in selected
        ]
        if not any(item["_raw"] for item in data):
            raise EmptyDataError("The request was returned empty.")
        return data

    @staticmethod
    def transform_data(
        query: FederalReserveStLouisNationalIndexQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveStLouisNationalIndexData]:
        """Merge each index into wide ``(date, index columns)`` rows."""
        from io import StringIO

        from pandas import isna, read_csv, to_datetime, to_numeric

        frames = []
        for item in data:
            if not item["_raw"]:
                continue
            frame = read_csv(StringIO(item["_raw"]))
            frame.columns = ["date", item["index"]]
            frame["date"] = to_datetime(frame["date"]).dt.date
            frame[item["index"]] = to_numeric(
                frame[item["index"]].replace(".", None), errors="coerce"
            )
            frames.append(frame)
        if not frames:
            raise EmptyDataError("The request was returned empty.")

        merged = frames[0]
        for frame in frames[1:]:
            merged = merged.merge(frame, on="date", how="outer")

        if query.start_date:
            merged = merged[merged["date"] >= query.start_date]
        if query.end_date:
            merged = merged[merged["date"] <= query.end_date]

        columns = [column for column in merged.columns if column != "date"]
        records: list[FederalReserveStLouisNationalIndexData] = []
        for row in merged.sort_values("date").to_dict(orient="records"):
            record = {
                k: (None if isinstance(v, float) and isna(v) else v)
                for k, v in row.items()
            }
            if any(record[column] is not None for column in columns):
                records.append(
                    FederalReserveStLouisNationalIndexData.model_validate(record)
                )
        if not records:
            raise EmptyDataError("The request was returned empty.")
        return records
