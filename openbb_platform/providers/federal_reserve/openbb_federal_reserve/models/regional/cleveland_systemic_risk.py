"""Federal Reserve Bank of Cleveland Systemic Risk Indicator Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

URL = (
    "https://www.clevelandfed.org/-/media/files/webcharts"
    "/systemicrisk/landing_systemicrisk.csv"
)

_LABELS = {
    "sri": "Systemic Risk Indicator (ADD minus PDD)",
    "add": "Average Distance-to-Default (ADD)",
    "pdd": "Portfolio Distance-to-Default (PDD)",
}


class FederalReserveClevelandSystemicRiskQueryParams(QueryParams):
    """Cleveland Fed Systemic Risk Indicator Query Parameters."""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveClevelandSystemicRiskData(Data):
    """Cleveland Fed Systemic Risk Indicator Data.

    One row per observation date, with one column per indicator component
    carrying that component's value, in standard deviations. The indicator and
    its two distance-to-default legs are pivoted to wide.
    """

    date: dateType = Field(description="The observation date.")


class FederalReserveClevelandSystemicRiskFetcher(
    Fetcher[
        FederalReserveClevelandSystemicRiskQueryParams,
        list[FederalReserveClevelandSystemicRiskData],
    ]
):
    """Cleveland Fed Systemic Risk Indicator Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveClevelandSystemicRiskQueryParams:
        """Transform the query params."""
        return FederalReserveClevelandSystemicRiskQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveClevelandSystemicRiskQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the Systemic Risk Indicator CSV from the Cleveland Fed."""
        from openbb_core.provider.utils.helpers import make_request

        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )

        def _producer() -> str:
            """Fetch the indicator CSV text."""
            response = make_request(URL)
            response.raise_for_status()
            return response.text

        text = cached(
            "cleveland_systemic_risk",
            lambda: seconds_until_next_release("daily"),
            _producer,
        )
        if not text:
            raise EmptyDataError("The request was returned empty.")
        return [{"_text": text}]

    @staticmethod
    def transform_data(
        query: FederalReserveClevelandSystemicRiskQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveClevelandSystemicRiskData]:
        """Melt the indicator and its two legs, then pivot to wide records."""
        from io import StringIO

        from pandas import isna, read_csv, to_datetime, to_numeric

        from openbb_federal_reserve.utils.workbook import pivot_wide, round_value

        frame = read_csv(StringIO(data[0]["_text"]))
        frame.columns = [str(column).strip().lower() for column in frame.columns]
        frame["date"] = to_datetime(frame["date"], errors="coerce").dt.date
        frame = frame.dropna(subset=["date"])

        value_columns = [c for c in _LABELS if c in frame.columns]
        for column in value_columns:
            frame[column] = to_numeric(frame[column], errors="coerce")
        melted = frame[["date", *value_columns]].melt(
            id_vars=["date"], var_name="_column", value_name="value"
        )
        melted["series"] = melted["_column"].map(_LABELS)

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
        ]
        rows = pivot_wide(records, index="date", column="series", value="value")
        return [
            FederalReserveClevelandSystemicRiskData.model_validate(record)
            for record in rows
        ]
