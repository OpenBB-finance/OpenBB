"""Federal Reserve NIC Large Holding Companies Model."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field


class FederalReserveLargeHoldingCompaniesQueryParams(QueryParams):
    """Federal Reserve Large Holding Companies Query Parameters."""

    limit: int | None = Field(
        default=None,
        description="Limit the number of holding companies returned.",
    )


class FederalReserveLargeHoldingCompaniesData(Data):
    """Federal Reserve Large Holding Companies Data."""

    rank: int = Field(description="Rank by total consolidated assets.")
    rssd_id: str = Field(description="The holding company's RSSD identifier.")
    name: str = Field(description="The holding company's legal name.")
    location: str | None = Field(
        default=None, description="The holding company's headquarters location."
    )
    total_assets: float | None = Field(
        default=None,
        description="Total consolidated assets, in USD.",
    )
    date: dateType | None = Field(
        default=None, description="The reporting period-end date."
    )


class FederalReserveLargeHoldingCompaniesFetcher(
    Fetcher[
        FederalReserveLargeHoldingCompaniesQueryParams,
        list[FederalReserveLargeHoldingCompaniesData],
    ]
):
    """Federal Reserve Large Holding Companies Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveLargeHoldingCompaniesQueryParams:
        """Transform the query params."""
        return FederalReserveLargeHoldingCompaniesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveLargeHoldingCompaniesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the ranked list of large holding companies."""
        from openbb_federal_reserve.utils.ffiec import fetch_top_holders

        holders = fetch_top_holders()
        if not holders:
            raise EmptyDataError("The request was returned empty.")
        rows = sorted(holders, key=lambda h: h.get("Rank", 0))
        if query.limit:
            rows = rows[: query.limit]
        return rows

    @staticmethod
    def transform_data(
        query: FederalReserveLargeHoldingCompaniesQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveLargeHoldingCompaniesData]:
        """Map the JSON records to the data model."""
        results: list[FederalReserveLargeHoldingCompaniesData] = []
        for row in data:
            raw_date = str(row.get("Date", ""))
            parsed = (
                datetime.strptime(raw_date, "%Y%m%d").date()
                if len(raw_date) == 8 and raw_date.isdigit()
                else None
            )
            assets = row.get("TotalAssets")
            try:
                total_assets = float(assets) * 1000 if assets is not None else None
            except (TypeError, ValueError):
                total_assets = None
            results.append(
                FederalReserveLargeHoldingCompaniesData.model_validate(
                    {
                        "rank": row.get("Rank"),
                        "rssd_id": str(row.get("RssdId", "")),
                        "name": str(row.get("Name", "")).strip(),
                        "location": (row.get("Location") or "").strip() or None,
                        "total_assets": total_assets,
                        "date": parsed,
                    }
                )
            )
        return results
