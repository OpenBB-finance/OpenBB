"""Federal Reserve Bank of Kansas City Risk-On/Risk-Off Index Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

_URLS = {
    "daily": "https://kcresearch-share.kansascityfed.org/kc-roro/roro_daily.csv",
    "weekly": "https://kcresearch-share.kansascityfed.org/kc-roro/roro_weekly.csv",
}
_COLUMN_MAP = {
    "z_spreads": "spreads",
    "z_equities": "equities",
    "z_liquidity": "liquidity",
    "z_goldcurrency": "gold_currency",
    "z_roro": "roro",
}


class FederalReserveKansasCityRiskIndexQueryParams(QueryParams):
    """Kansas City Fed Risk-On/Risk-Off Index Query Parameters."""

    __json_schema_extra__ = {
        "frequency": {
            "x-widget_config": {
                "options": [
                    {"label": "Daily", "value": "daily"},
                    {"label": "Weekly", "value": "weekly"},
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
    frequency: Literal["daily", "weekly"] = Field(
        default="daily",
        description="The observation frequency.",
    )


class FederalReserveKansasCityRiskIndexData(Data):
    """Kansas City Fed Risk-On/Risk-Off Index Data."""

    date: dateType = Field(description="The observation date.")
    roro: float | None = Field(
        default=None, description="The composite Risk-On/Risk-Off index."
    )
    spreads: float | None = Field(
        default=None, description="The standardized credit-spreads component."
    )
    equities: float | None = Field(
        default=None, description="The standardized equities component."
    )
    liquidity: float | None = Field(
        default=None, description="The standardized liquidity component."
    )
    gold_currency: float | None = Field(
        default=None, description="The standardized gold and currency component."
    )


class FederalReserveKansasCityRiskIndexFetcher(
    Fetcher[
        FederalReserveKansasCityRiskIndexQueryParams,
        list[FederalReserveKansasCityRiskIndexData],
    ]
):
    """Kansas City Fed Risk-On/Risk-Off Index Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveKansasCityRiskIndexQueryParams:
        """Transform the query params."""
        return FederalReserveKansasCityRiskIndexQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveKansasCityRiskIndexQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the RORO CSV for the requested frequency."""
        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )
        from openbb_federal_reserve.utils.kansas_city import fetch_kansas_city

        url = _URLS[query.frequency]
        cadence = "weekly" if query.frequency == "weekly" else "daily"
        content = cached(
            ("kansas_city_roro", query.frequency),
            lambda: seconds_until_next_release(cadence),
            lambda: fetch_kansas_city(url),
        )
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReserveKansasCityRiskIndexQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveKansasCityRiskIndexData]:
        """Parse the RORO CSV, drop empty rows, and apply the date filters."""
        from io import BytesIO

        from pandas import isna, read_csv, to_datetime

        frame = read_csv(BytesIO(data[0]["_raw"]))
        frame = frame.rename(columns={"t": "date", **_COLUMN_MAP})
        frame["date"] = to_datetime(frame["date"].str.lower(), format="%d%b%Y").dt.date
        frame = frame.dropna(subset=list(_COLUMN_MAP.values()), how="all")

        if query.start_date:
            frame = frame[frame["date"] >= query.start_date]
        if query.end_date:
            frame = frame[frame["date"] <= query.end_date]

        return [
            FederalReserveKansasCityRiskIndexData.model_validate(
                {
                    k: (None if isinstance(v, float) and isna(v) else v)
                    for k, v in row.items()
                }
            )
            for row in frame.sort_values("date").to_dict(orient="records")
        ]
