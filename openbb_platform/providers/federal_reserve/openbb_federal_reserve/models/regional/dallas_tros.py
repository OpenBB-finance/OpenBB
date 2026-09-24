"""Federal Reserve Bank of Dallas Texas Retail Outlook Survey Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

URL = (
    "https://www.dallasfed.org/-/media/Documents/research"
    "/surveys/tssos/documents/tros_alldata.xls"
)


class FederalReserveDallasRetailQueryParams(QueryParams):
    """Dallas Fed Texas Retail Outlook Survey Query Parameters."""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveDallasRetailData(Data):
    """Dallas Fed Texas Retail Outlook Survey Data."""

    date: dateType = Field(description="The survey month.")


class FederalReserveDallasRetailFetcher(
    Fetcher[
        FederalReserveDallasRetailQueryParams,
        list[FederalReserveDallasRetailData],
    ]
):
    """Dallas Fed Texas Retail Outlook Survey Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveDallasRetailQueryParams:
        """Transform the query params."""
        return FederalReserveDallasRetailQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveDallasRetailQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the Texas Retail Outlook Survey workbook."""
        from openbb_core.provider.utils.helpers import make_request

        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )

        def _producer() -> bytes:
            """Fetch the raw survey workbook bytes."""
            response = make_request(URL)
            response.raise_for_status()
            return response.content

        content = cached(
            "dallas_tros", lambda: seconds_until_next_release("monthly"), _producer
        )
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReserveDallasRetailQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveDallasRetailData]:
        """Transform and pivot survey data to wide rows."""
        from openbb_federal_reserve.utils.dallas_survey import parse_retail_survey
        from openbb_federal_reserve.utils.workbook import pivot_wide

        records = parse_retail_survey(
            data[0]["_raw"],
            "Alldata",
            date_format="%b-%y",
            start_date=query.start_date,
            end_date=query.end_date,
        )
        for record in records:
            record["column"] = (
                f"{record['indicator']} ({record['horizon']}, {record['response']})"
            )
        rows = pivot_wide(records, index="date", column="column", value="value")
        return [
            FederalReserveDallasRetailData.model_validate(record) for record in rows
        ]
