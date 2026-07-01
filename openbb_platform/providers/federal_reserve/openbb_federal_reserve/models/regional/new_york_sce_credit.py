"""Federal Reserve Bank of New York SCE Credit Access Survey Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

URL = (
    "https://www.newyorkfed.org/medialibrary/interactives/sce/sce"
    "/downloads/data/frbny-sce-credit-access-data.xlsx?sc_lang=en"
)

# Readable labels for the headline metrics; other columns keep their source name.
_LABELS = {
    "Observations": "Observations",
    "Applied_Accepted": "Applied and Accepted",
    "Applied_Rejected": "Applied and Rejected",
    "Discouraged": "Discouraged from Applying",
}

_ID_COLUMNS = {"date", "group", "category"}


class FederalReserveNewYorkConsumerCreditAccessQueryParams(QueryParams):
    """New York Fed SCE Credit Access Survey Query Parameters."""

    __json_schema_extra__ = {
        "breakdown": {
            "x-widget_config": {
                "options": [
                    {"label": "Overall", "value": "overall"},
                    {"label": "Demographics", "value": "demographics"},
                ]
            }
        }
    }

    breakdown: Literal["overall", "demographics"] = Field(
        default="overall",
        description="The overall (all respondents) series, or the breakdown by"
        " respondent age and credit-score group.",
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveNewYorkConsumerCreditAccessData(Data):
    """New York Fed SCE Credit Access Survey Data.

    One row per ``(date, group, category)`` combination, with one column per
    credit-access series carrying its value. The series are pivoted to wide; the
    group and category dimensions stay as row-group columns.
    """

    date: dateType = Field(description="The survey month.")
    group: str | None = Field(default=None, description="The respondent grouping.")
    category: str | None = Field(default=None, description="The respondent category.")


class FederalReserveNewYorkConsumerCreditAccessFetcher(
    Fetcher[
        FederalReserveNewYorkConsumerCreditAccessQueryParams,
        list[FederalReserveNewYorkConsumerCreditAccessData],
    ]
):
    """New York Fed SCE Credit Access Survey Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveNewYorkConsumerCreditAccessQueryParams:
        """Transform the query params."""
        return FederalReserveNewYorkConsumerCreditAccessQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveNewYorkConsumerCreditAccessQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the SCE Credit Access workbook from the New York Fed."""
        from openbb_core.provider.utils.helpers import make_request

        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )

        def _producer() -> bytes:
            """Fetch the raw SCE Credit Access workbook bytes."""
            response = make_request(URL)
            response.raise_for_status()
            return response.content

        content = cached(
            "new_york_sce_credit",
            lambda: seconds_until_next_release("monthly"),
            _producer,
        )
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReserveNewYorkConsumerCreditAccessQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveNewYorkConsumerCreditAccessData]:
        """Pivot the selected sheet to wide ``(date, group, category)`` + series."""
        from io import BytesIO

        from pandas import isna, notna, read_excel, to_datetime, to_numeric

        from openbb_federal_reserve.utils.workbook import pivot_wide

        frame = read_excel(
            BytesIO(data[0]["_raw"]),
            engine="openpyxl",
            sheet_name=query.breakdown,
            header=1,
        )
        frame["date"] = to_datetime(
            frame["date"].astype("Int64").astype("string"),
            format="%Y%m",
            errors="coerce",
        )
        frame = frame.dropna(subset=["date"])
        frame["date"] = frame["date"].dt.date

        value_columns = [c for c in frame.columns if c not in _ID_COLUMNS]
        for column in value_columns:
            frame[column] = to_numeric(frame[column], errors="coerce")
        melted = frame.melt(
            id_vars=["date", "group", "category"],
            value_vars=value_columns,
            var_name="_column",
            value_name="value",
        )
        melted["series"] = melted["_column"].map(lambda c: _LABELS.get(c, c))

        if query.start_date:
            melted = melted[melted["date"] >= query.start_date]
        if query.end_date:
            melted = melted[melted["date"] <= query.end_date]

        records = [
            {
                "date": row["date"],
                "group": (
                    None if not notna(row["group"]) else str(row["group"]).strip()
                ),
                "category": (
                    None if not notna(row["category"]) else str(row["category"]).strip()
                ),
                "series": row["series"],
                "value": (
                    None
                    if isinstance(row["value"], float) and isna(row["value"])
                    else float(row["value"])
                ),
            }
            for row in melted.sort_values(
                ["date", "group", "category", "series"]
            ).to_dict(orient="records")
        ]
        return [
            FederalReserveNewYorkConsumerCreditAccessData.model_validate(record)
            for record in pivot_wide(
                records,
                index=("date", "group", "category"),
                column="series",
                value="value",
            )
        ]
