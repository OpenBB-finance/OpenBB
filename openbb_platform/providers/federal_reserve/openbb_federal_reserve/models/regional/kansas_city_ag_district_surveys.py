"""Federal Reserve Bank of Kansas City District Ag Credit Surveys Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

_DOCUMENT_ID = 7230


class FederalReserveKansasCityAgDistrictSurveysQueryParams(QueryParams):
    """Kansas City Fed District Ag Credit Surveys Query Parameters."""

    district: str | None = Field(
        default=None,
        description="Filter to a single Federal Reserve district by name"
        " (e.g. Chicago, Dallas, Kansas City, Minneapolis, Richmond,"
        " San Francisco).",
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveKansasCityAgDistrictSurveysData(Data):
    """Kansas City Fed District Ag Credit Surveys Data.

    One row per survey quarter-end date, with one column per district-and-indicator
    series carrying that series' value; the series are pivoted to wide.
    """

    date: dateType = Field(description="The survey quarter-end date.")


class FederalReserveKansasCityAgDistrictSurveysFetcher(
    Fetcher[
        FederalReserveKansasCityAgDistrictSurveysQueryParams,
        list[FederalReserveKansasCityAgDistrictSurveysData],
    ]
):
    """Kansas City Fed District Ag Credit Surveys Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveKansasCityAgDistrictSurveysQueryParams:
        """Transform the query params."""
        return FederalReserveKansasCityAgDistrictSurveysQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveKansasCityAgDistrictSurveysQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the district surveys history from the Kansas City Fed."""
        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )
        from openbb_federal_reserve.utils.kansas_city import fetch_kansas_city
        from openbb_federal_reserve.utils.kansas_city_ag import resolve_kc_ag_url

        content = cached(
            "kansas_city_ag_district_surveys",
            lambda: seconds_until_next_release("quarterly"),
            lambda: fetch_kansas_city(resolve_kc_ag_url(_DOCUMENT_ID)),
        )
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReserveKansasCityAgDistrictSurveysQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveKansasCityAgDistrictSurveysData]:
        """Melt the district survey history, then pivot each series to a column."""
        from openbb_federal_reserve.utils.kansas_city_ag import parse_kc_district
        from openbb_federal_reserve.utils.workbook import pivot_wide

        records = parse_kc_district(
            data[0]["_raw"],
            start_date=query.start_date,
            end_date=query.end_date,
        )
        if query.district:
            wanted = query.district.strip().lower()
            records = [r for r in records if wanted in r["series"].lower()]
        rows = pivot_wide(records, index="date", column="series", value="value")
        return [
            FederalReserveKansasCityAgDistrictSurveysData.model_validate(record)
            for record in rows
        ]
