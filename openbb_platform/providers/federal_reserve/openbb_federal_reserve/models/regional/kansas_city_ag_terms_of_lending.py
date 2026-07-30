"""Federal Reserve Bank of Kansas City Ag Terms of Lending Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

_DOCUMENT_ID = 7225


class FederalReserveKansasCityAgTermsOfLendingQueryParams(QueryParams):
    """Kansas City Fed Ag Terms of Lending Query Parameters."""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveKansasCityAgTermsOfLendingData(Data):
    """Kansas City Fed Ag Terms of Lending Data."""

    date: dateType = Field(description="The survey quarter-end date.")


class FederalReserveKansasCityAgTermsOfLendingFetcher(
    Fetcher[
        FederalReserveKansasCityAgTermsOfLendingQueryParams,
        list[FederalReserveKansasCityAgTermsOfLendingData],
    ]
):
    """Kansas City Fed Ag Terms of Lending Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveKansasCityAgTermsOfLendingQueryParams:
        """Transform the query params."""
        return FederalReserveKansasCityAgTermsOfLendingQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveKansasCityAgTermsOfLendingQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the Terms of Lending history from the Kansas City Fed."""
        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )
        from openbb_federal_reserve.utils.kansas_city import fetch_kansas_city
        from openbb_federal_reserve.utils.kansas_city_ag import resolve_kc_ag_url

        content = cached(
            "kansas_city_ag_terms_of_lending",
            lambda: seconds_until_next_release("quarterly"),
            lambda: fetch_kansas_city(resolve_kc_ag_url(_DOCUMENT_ID)),
        )
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReserveKansasCityAgTermsOfLendingQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveKansasCityAgTermsOfLendingData]:
        """Transform raw survey content into wide-format data records."""
        from openbb_federal_reserve.utils.kansas_city_ag import parse_kc_databook
        from openbb_federal_reserve.utils.workbook import pivot_wide

        records = parse_kc_databook(
            data[0]["_raw"],
            start_date=query.start_date,
            end_date=query.end_date,
        )
        rows = pivot_wide(records, index="date", column="series", value="value")
        return [
            FederalReserveKansasCityAgTermsOfLendingData.model_validate(record)
            for record in rows
        ]
