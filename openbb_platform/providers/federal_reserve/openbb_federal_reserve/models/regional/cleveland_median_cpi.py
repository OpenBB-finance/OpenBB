"""Federal Reserve Bank of Cleveland Median CPI Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

BASE_URL = "https://www.clevelandfed.org/-/media/files/webcharts/mediancpi"

# table key -> (csv filename, {raw column: readable series label}).
_TABLES = {
    "summary": (
        "mediancpi_chartdata.csv",
        {
            "mediancpi": "Median CPI",
            "trimmedmeancpi": "16% Trimmed-Mean CPI",
            "cpi": "CPI",
            "corecpi": "Core CPI",
        },
    ),
    "median_cpi": (
        "mcpi_revised.csv",
        {
            "mcpi_monthly_chg": "Median CPI, 1-Month Change",
            "mcpi_ann_monthly_chg": "Median CPI, 1-Month Annualized",
        },
    ),
    "trimmed_mean": (
        "trim_revised.csv",
        {
            "trim_monthly_chg": "16% Trimmed-Mean CPI, 1-Month Change",
            "trim_ann_monthly_chg": "16% Trimmed-Mean CPI, 1-Month Annualized",
        },
    ),
    "cpi": (
        "cpi.csv",
        {
            "cpi_index": "CPI Index",
            "ann_monthly_chg": "CPI, 1-Month Annualized",
        },
    ),
    "core_cpi": (
        "core.csv",
        {
            "core_index": "Core CPI Index",
            "ann_monthly_chg": "Core CPI, 1-Month Annualized",
        },
    ),
}


class FederalReserveClevelandMedianCpiQueryParams(QueryParams):
    """Cleveland Fed Median CPI Query Parameters."""

    __json_schema_extra__ = {
        "table": {
            "x-widget_config": {
                "options": [
                    {"label": "Summary", "value": "summary"},
                    {"label": "Median CPI (Revised History)", "value": "median_cpi"},
                    {
                        "label": "16% Trimmed-Mean CPI (Revised History)",
                        "value": "trimmed_mean",
                    },
                    {"label": "CPI", "value": "cpi"},
                    {"label": "Core CPI", "value": "core_cpi"},
                ]
            }
        },
    }

    table: Literal["summary", "median_cpi", "trimmed_mean", "cpi", "core_cpi"] = Field(
        default="summary",
        description="The headline summary (Median, Trimmed-Mean, CPI, Core, 12-month),"
        " or the full revised history of the median CPI, the 16% trimmed-mean CPI,"
        " the CPI, or the core CPI.",
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveClevelandMedianCpiData(Data):
    """Cleveland Fed Median CPI Data.

    One row per observation month, with one column per inflation series carrying
    that series' reported value. The selected table's series are pivoted to wide,
    so the columns vary with the requested table.
    """

    date: dateType = Field(description="The observation month.")


class FederalReserveClevelandMedianCpiFetcher(
    Fetcher[
        FederalReserveClevelandMedianCpiQueryParams,
        list[FederalReserveClevelandMedianCpiData],
    ]
):
    """Cleveland Fed Median CPI Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveClevelandMedianCpiQueryParams:
        """Transform the query params."""
        return FederalReserveClevelandMedianCpiQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveClevelandMedianCpiQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the requested Median CPI series CSV from the Cleveland Fed."""
        from openbb_core.provider.utils.helpers import make_request

        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )

        filename = _TABLES[query.table][0]

        def _producer() -> str:
            """Fetch the table's CSV text."""
            response = make_request(f"{BASE_URL}/{filename}")
            response.raise_for_status()
            return response.text

        text = cached(
            ("cleveland_median_cpi", query.table),
            lambda: seconds_until_next_release("monthly"),
            _producer,
        )
        if not text:
            raise EmptyDataError("The request was returned empty.")
        return [{"_text": text}]

    @staticmethod
    def transform_data(
        query: FederalReserveClevelandMedianCpiQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveClevelandMedianCpiData]:
        """Melt the selected series CSV, then pivot the series to wide rows."""
        from io import StringIO

        from pandas import isna, notna, read_csv, to_datetime, to_numeric

        from openbb_federal_reserve.utils.workbook import pivot_wide, round_value

        labels = _TABLES[query.table][1]
        frame = read_csv(StringIO(data[0]["_text"]))
        frame.columns = [str(column).strip() for column in frame.columns]
        frame = frame.rename(columns={frame.columns[0]: "date"})
        frame["date"] = to_datetime(frame["date"], errors="coerce").dt.date
        frame = frame.dropna(subset=["date"])

        value_columns = [c for c in labels if c in frame.columns]
        for column in value_columns:
            frame[column] = to_numeric(frame[column], errors="coerce")
        melted = frame[["date", *value_columns]].melt(
            id_vars=["date"], var_name="_column", value_name="value"
        )
        melted["series"] = melted["_column"].map(labels)

        if query.start_date:
            melted = melted[melted["date"] >= query.start_date]
        if query.end_date:
            melted = melted[melted["date"] <= query.end_date]

        records = [
            {
                "date": row["date"],
                "series": row["series"],
                "value": (
                    None
                    if isinstance(row["value"], float) and isna(row["value"])
                    else round_value(row["value"])
                ),
            }
            for row in melted.sort_values(["date", "series"]).to_dict(orient="records")
            if notna(row["date"])
        ]
        rows = pivot_wide(records, index="date", column="series", value="value")
        return [
            FederalReserveClevelandMedianCpiData.model_validate(record)
            for record in rows
        ]
