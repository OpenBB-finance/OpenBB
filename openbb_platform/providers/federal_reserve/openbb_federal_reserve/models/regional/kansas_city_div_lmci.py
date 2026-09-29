"""Federal Reserve Bank of Kansas City Divisional LMCI Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

URL = "https://www.kansascityfed.org/documents/16577/DIV-LMCI.xlsx"
_SHEETS = {"level_of_activity": "Level of Activity", "momentum": "Momentum"}


class FederalReserveKansasCityDivisionalLmciQueryParams(QueryParams):
    """Kansas City Fed Divisional LMCI Query Parameters."""

    __json_schema_extra__ = {
        "indicator": {
            "x-widget_config": {
                "options": [
                    {"label": "Level of Activity", "value": "level_of_activity"},
                    {"label": "Momentum", "value": "momentum"},
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
    indicator: Literal["level_of_activity", "momentum"] = Field(
        default="level_of_activity",
        description="The LMCI indicator to return.",
    )


class FederalReserveKansasCityDivisionalLmciData(Data):
    """Kansas City Fed Divisional LMCI Data."""

    date: dateType = Field(description="The observation month.")


class FederalReserveKansasCityDivisionalLmciFetcher(
    Fetcher[
        FederalReserveKansasCityDivisionalLmciQueryParams,
        list[FederalReserveKansasCityDivisionalLmciData],
    ]
):
    """Kansas City Fed Divisional LMCI Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveKansasCityDivisionalLmciQueryParams:
        """Transform the query params."""
        return FederalReserveKansasCityDivisionalLmciQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveKansasCityDivisionalLmciQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the Divisional LMCI workbook from the Kansas City Fed."""
        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )
        from openbb_federal_reserve.utils.kansas_city import fetch_kansas_city

        content = cached(
            "kansas_city_div_lmci",
            lambda: seconds_until_next_release("monthly"),
            lambda: fetch_kansas_city(URL),
        )
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReserveKansasCityDivisionalLmciQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveKansasCityDivisionalLmciData]:
        """Pivot the divisional sheet to one wide row per month, division columns."""
        from openbb_federal_reserve.utils.workbook import melt_sheet, pivot_wide

        records = pivot_wide(
            melt_sheet(
                data[0]["_raw"],
                _SHEETS[query.indicator],
                start_date=query.start_date,
                end_date=query.end_date,
            )
        )
        return [
            FederalReserveKansasCityDivisionalLmciData.model_validate(record)
            for record in records
        ]
