"""Federal Reserve Bank of St. Louis FRED-MD / FRED-QD Panel Models."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

from openbb_federal_reserve.utils.fred_md import series_options


def _apply_transform(series, code: int | None):
    """Apply a FRED-MD/QD stationarity transformation code to a series."""
    from numpy import log

    if code == 7:
        return (series / series.shift(1) - 1).diff()
    if code in (4, 5, 6):
        series = log(series)
        code -= 3
    if code == 2:
        return series.diff()
    if code == 3:
        return series.diff().diff()
    return series


def _parse_panel(
    text: str,
    transform_row: int,
    data_start: int,
    series_filter: set[str] | None,
    apply: bool,
) -> list[dict[str, Any]]:
    """Parse a FRED panel into wide ``(date, series columns)`` rows."""
    from io import StringIO

    from pandas import isna, read_csv, to_datetime, to_numeric

    frame = read_csv(StringIO(text))
    frame = frame.rename(columns={"sasdate": "date"})

    codes: dict[str, int | None] = {}
    code_row = frame.iloc[transform_row]
    for column in frame.columns:
        if column == "date":
            continue
        try:
            codes[column] = int(float(code_row[column]))
        except (TypeError, ValueError):
            codes[column] = None

    frame = frame.iloc[data_start:].copy()
    frame = frame[frame["date"].notna() & (frame["date"].astype(str).str.strip() != "")]
    frame["date"] = to_datetime(frame["date"], format="%m/%d/%Y").dt.date

    value_columns = [c for c in frame.columns if c != "date"]
    if series_filter:
        value_columns = [c for c in value_columns if c in series_filter]

    for column in value_columns:
        frame[column] = to_numeric(frame[column].replace(".", None), errors="coerce")
        if apply:
            frame[column] = _apply_transform(frame[column], codes.get(column))

    wide = frame[["date", *value_columns]]
    records: list[dict[str, Any]] = []
    for row in wide.sort_values("date").to_dict(orient="records"):
        record = {
            k: (None if isinstance(v, float) and isna(v) else v) for k, v in row.items()
        }
        if any(record[column] is not None for column in value_columns):
            records.append(record)
    return records


def _filter_records(
    records: list[dict[str, Any]],
    start_date: dateType | None,
    end_date: dateType | None,
) -> list[dict[str, Any]]:
    """Apply the date-range filters to the parsed panel rows."""
    if start_date:
        records = [r for r in records if r["date"] >= start_date]
    if end_date:
        records = [r for r in records if r["date"] <= end_date]
    return records


class FederalReserveStLouisFredMdQueryParams(QueryParams):
    """St. Louis Fed FRED-MD Monthly Macro Panel Query Parameters."""

    __json_schema_extra__ = {
        "series": {
            "multiple_items_allowed": True,
            "x-widget_config": {
                "options": series_options("monthly"),
                "multiSelect": True,
            },
        }
    }

    series: str | None = Field(
        default=None,
        description="One or more FRED series codes (panel columns) to return;"
        " the default returns every series.",
    )
    transform: bool = Field(
        default=False,
        description="Apply each series' recommended stationarity transformation"
        " (its transform code) instead of returning raw levels.",
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveStLouisFredMdData(Data):
    """St. Louis Fed FRED-MD Monthly Macro Panel Data."""

    date: dateType = Field(description="The observation date.")


class FederalReserveStLouisFredMdFetcher(
    Fetcher[
        FederalReserveStLouisFredMdQueryParams,
        list[FederalReserveStLouisFredMdData],
    ]
):
    """St. Louis Fed FRED-MD Monthly Macro Panel Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveStLouisFredMdQueryParams:
        """Transform the query params."""
        return FederalReserveStLouisFredMdQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveStLouisFredMdQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the FRED-MD panel CSV from the St. Louis Fed."""
        from openbb_federal_reserve.utils.st_louis import fetch_fred_panel

        text = fetch_fred_panel("monthly")
        if not text:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": text}]

    @staticmethod
    def transform_data(
        query: FederalReserveStLouisFredMdQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveStLouisFredMdData]:
        """Pivot the panel wide (optionally transforming) and apply the filters."""
        series_filter = (
            {s.strip() for s in query.series.split(",") if s.strip()}
            if query.series
            else None
        )
        records = _parse_panel(data[0]["_raw"], 0, 1, series_filter, query.transform)
        records = _filter_records(records, query.start_date, query.end_date)
        if not records:
            raise EmptyDataError("The request was returned empty.")
        return [
            FederalReserveStLouisFredMdData.model_validate(record) for record in records
        ]


class FederalReserveStLouisFredQdQueryParams(QueryParams):
    """St. Louis Fed FRED-QD Quarterly Macro Panel Query Parameters."""

    __json_schema_extra__ = {
        "series": {
            "multiple_items_allowed": True,
            "x-widget_config": {
                "options": series_options("quarterly"),
                "multiSelect": True,
            },
        }
    }

    series: str | None = Field(
        default=None,
        description="One or more FRED series codes (panel columns) to return;"
        " the default returns every series.",
    )
    transform: bool = Field(
        default=False,
        description="Apply each series' recommended stationarity transformation"
        " (its transform code) instead of returning raw levels.",
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveStLouisFredQdData(Data):
    """St. Louis Fed FRED-QD Quarterly Macro Panel Data."""

    date: dateType = Field(description="The observation date.")


class FederalReserveStLouisFredQdFetcher(
    Fetcher[
        FederalReserveStLouisFredQdQueryParams,
        list[FederalReserveStLouisFredQdData],
    ]
):
    """St. Louis Fed FRED-QD Quarterly Macro Panel Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveStLouisFredQdQueryParams:
        """Transform the query params."""
        return FederalReserveStLouisFredQdQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveStLouisFredQdQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the FRED-QD panel CSV from the St. Louis Fed."""
        from openbb_federal_reserve.utils.st_louis import fetch_fred_panel

        text = fetch_fred_panel("quarterly")
        if not text:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": text}]

    @staticmethod
    def transform_data(
        query: FederalReserveStLouisFredQdQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveStLouisFredQdData]:
        """Pivot the panel wide (optionally transforming) and apply the filters."""
        series_filter = (
            {s.strip() for s in query.series.split(",") if s.strip()}
            if query.series
            else None
        )
        records = _parse_panel(data[0]["_raw"], 1, 2, series_filter, query.transform)
        records = _filter_records(records, query.start_date, query.end_date)
        if not records:
            raise EmptyDataError("The request was returned empty.")
        return [
            FederalReserveStLouisFredQdData.model_validate(record) for record in records
        ]
