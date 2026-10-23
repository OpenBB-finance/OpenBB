"""Federal Reserve Bank of San Francisco Proxy Funds Rate Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

URL = "https://www.frbsf.org/wp-content/uploads/proxy-funds-rate-data.xlsx"

_SHEETS = {"weekly": "Weekly", "monthly": "Monthly"}
_COLUMN_MAP = {
    "Effective funds rate": "effective_funds_rate",
    "Proxy funds rate": "proxy_funds_rate",
}


class FederalReserveSanFranciscoProxyFundsRateQueryParams(QueryParams):
    """San Francisco Fed Proxy Funds Rate Query Parameters."""

    __json_schema_extra__ = {
        "frequency": {
            "x-widget_config": {
                "options": [
                    {"label": "Weekly", "value": "weekly"},
                    {"label": "Monthly", "value": "monthly"},
                ]
            }
        }
    }

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )
    frequency: Literal["weekly", "monthly"] = Field(
        default="monthly",
        description="The observation frequency.",
    )


class FederalReserveSanFranciscoProxyFundsRateData(Data):
    """San Francisco Fed Proxy Funds Rate Data."""

    date: dateType = Field(description="The observation date.")
    effective_funds_rate: float | None = Field(
        default=None, description="The effective federal funds rate."
    )
    proxy_funds_rate: float | None = Field(
        default=None, description="The proxy funds rate."
    )


class FederalReserveSanFranciscoProxyFundsRateFetcher(
    Fetcher[
        FederalReserveSanFranciscoProxyFundsRateQueryParams,
        list[FederalReserveSanFranciscoProxyFundsRateData],
    ]
):
    """San Francisco Fed Proxy Funds Rate Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveSanFranciscoProxyFundsRateQueryParams:
        """Transform the query params."""
        return FederalReserveSanFranciscoProxyFundsRateQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveSanFranciscoProxyFundsRateQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the Proxy Funds Rate workbook from the San Francisco Fed."""
        from openbb_core.provider.utils.helpers import make_request

        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )

        cadence = "weekly" if query.frequency == "weekly" else "monthly"

        def _producer() -> bytes:
            """Fetch the raw Proxy Funds Rate workbook bytes."""
            response = make_request(URL)
            response.raise_for_status()
            return response.content

        content = cached(
            "san_francisco_proxy_funds_rate",
            lambda: seconds_until_next_release(cadence),
            _producer,
        )
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReserveSanFranciscoProxyFundsRateQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveSanFranciscoProxyFundsRateData]:
        """Parse the requested-frequency sheet and apply the date filters."""
        from io import BytesIO

        from pandas import isna, read_excel, to_datetime

        frame = read_excel(
            BytesIO(data[0]["_raw"]),
            engine="openpyxl",
            sheet_name=_SHEETS[query.frequency],
        )
        frame = frame.rename(columns={"Date": "date", **_COLUMN_MAP})
        frame = frame[["date", "effective_funds_rate", "proxy_funds_rate"]]
        frame["date"] = to_datetime(frame["date"], errors="coerce")
        frame = frame.dropna(subset=["date"])
        frame["date"] = frame["date"].dt.date

        if query.start_date:
            frame = frame[frame["date"] >= query.start_date]
        if query.end_date:
            frame = frame[frame["date"] <= query.end_date]

        return [
            FederalReserveSanFranciscoProxyFundsRateData.model_validate(
                {
                    k: (None if isinstance(v, float) and isna(v) else v)
                    for k, v in row.items()
                }
            )
            for row in frame.sort_values("date").to_dict(orient="records")
        ]
