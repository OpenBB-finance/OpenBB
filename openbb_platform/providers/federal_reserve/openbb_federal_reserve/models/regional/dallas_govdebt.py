"""Federal Reserve Bank of Dallas Government Debt Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

URL = "https://www.dallasfed.org/~/media/documents/research/govdebt.xlsx"


class FederalReserveDallasGovernmentDebtQueryParams(QueryParams):
    """Dallas Fed Government Debt Query Parameters."""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveDallasGovernmentDebtData(Data):
    """Dallas Fed Government Debt Data."""

    date: dateType = Field(description="The observation month.")


class FederalReserveDallasGovernmentDebtFetcher(
    Fetcher[
        FederalReserveDallasGovernmentDebtQueryParams,
        list[FederalReserveDallasGovernmentDebtData],
    ]
):
    """Dallas Fed Government Debt Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveDallasGovernmentDebtQueryParams:
        """Transform the query params."""
        return FederalReserveDallasGovernmentDebtQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveDallasGovernmentDebtQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the government debt workbook from the Dallas Fed."""
        from openbb_core.provider.utils.helpers import make_request

        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )

        def _producer() -> bytes:
            """Fetch the raw government debt workbook bytes."""
            response = make_request(URL)
            response.raise_for_status()
            return response.content

        content = cached(
            "dallas_govdebt",
            lambda: seconds_until_next_release("monthly"),
            _producer,
        )
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReserveDallasGovernmentDebtQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveDallasGovernmentDebtData]:
        """Melt the par/market two-level header, then pivot series to wide rows."""
        from openbb_federal_reserve.utils.dallas import melt_two_level
        from openbb_federal_reserve.utils.workbook import pivot_wide

        records = melt_two_level(
            data[0]["_raw"],
            "data",
            label_row=2,
            date_kind="datetime",
            start_date=query.start_date,
            end_date=query.end_date,
        )
        rows = pivot_wide(records, index="date", column="series", value="value")
        return [
            FederalReserveDallasGovernmentDebtData.model_validate(record)
            for record in rows
        ]
