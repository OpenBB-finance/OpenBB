"""Federal Reserve Bank of New York Empire State Survey Report Index Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field


class FederalReserveNewYorkEmpireReportsQueryParams(QueryParams):
    """New York Fed Empire State Survey Report Index Query Parameters."""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveNewYorkEmpireReportsData(Data):
    """New York Fed Empire State Survey Report Index Data."""

    date: dateType = Field(description="The survey month, as the month-start date.")
    period: str = Field(description="The report period as ``YYYYMM``.")
    url: str = Field(description="The direct URL to the PDF document.")


class FederalReserveNewYorkEmpireReportsFetcher(
    Fetcher[
        FederalReserveNewYorkEmpireReportsQueryParams,
        list[FederalReserveNewYorkEmpireReportsData],
    ]
):
    """New York Fed Empire State Survey Report Index Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveNewYorkEmpireReportsQueryParams:
        """Transform the query params."""
        return FederalReserveNewYorkEmpireReportsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveNewYorkEmpireReportsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Index the Empire State Survey report PDF archive."""
        from openbb_federal_reserve.utils.ny_empire import list_empire_state_reports

        catalog = list_empire_state_reports()
        if not catalog:
            raise EmptyDataError("The request was returned empty.")
        return catalog

    @staticmethod
    def transform_data(
        query: FederalReserveNewYorkEmpireReportsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveNewYorkEmpireReportsData]:
        """Build dated records and apply the date filters."""
        from datetime import date as date_cls

        records = []
        for record in data:
            period = record["period"]
            obs = date_cls(int(period[:4]), int(period[4:6]), 1)
            if query.start_date and obs < query.start_date:
                continue
            if query.end_date and obs > query.end_date:
                continue
            records.append({"date": obs, "period": period, "url": record["url"]})
        return [
            FederalReserveNewYorkEmpireReportsData.model_validate(record)
            for record in records
        ]
