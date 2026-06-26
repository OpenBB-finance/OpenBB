"""SEC institutional reporting periods from Form 13F structured data."""

from __future__ import annotations

from datetime import date
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field

from openbb_sec.utils.definitions import HEADERS
from openbb_sec.utils.form_13f_datasets import (
    SEC_13F_DATA_SETS_URL,
    filter_13f_data_sets,
    parse_13f_data_set_page,
)
from openbb_sec.utils.ratelimit import sec_make_request


class SecInstitutionalReportingPeriodsQueryParams(QueryParams):
    """SEC institutional reporting periods query."""

    years: int = Field(
        default=5,
        description="Number of years of published periods to return.",
        ge=1,
    )
    all_history: bool = Field(
        default=False,
        description="Whether to return all published periods.",
    )
    limit: int | None = Field(
        default=None,
        description="Maximum number of periods to return.",
        ge=1,
    )
    use_cache: bool = Field(
        default=True,
        description="Whether or not to use cache.",
    )


class SecInstitutionalReportingPeriodsData(Data):
    """SEC institutional reporting period row."""

    period: date | None = Field(
        default=None,
        description="Published SEC structured 13F reporting period end date.",
    )
    label: str | None = Field(
        default=None,
        description="SEC label for the published structured 13F period.",
    )


class SecInstitutionalReportingPeriodsFetcher(
    Fetcher[
        SecInstitutionalReportingPeriodsQueryParams,
        list[SecInstitutionalReportingPeriodsData],
    ]
):
    """SEC institutional reporting periods fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> SecInstitutionalReportingPeriodsQueryParams:
        """Transform query parameters."""
        return SecInstitutionalReportingPeriodsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: SecInstitutionalReportingPeriodsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return published structured 13F reporting periods."""
        page_url = kwargs.get("page_url", SEC_13F_DATA_SETS_URL)
        session = kwargs.get("session")
        request_kwargs: dict[str, Any] = {"headers": HEADERS}
        if session is not None:
            request_kwargs["session"] = session
        response = sec_make_request(page_url, **request_kwargs)
        response.raise_for_status()
        data_sets = filter_13f_data_sets(
            parse_13f_data_set_page(response.text, base_url=page_url),
            years=query.years,
            all_history=query.all_history,
        )
        records = [
            {"period": data_set.period_date, "label": data_set.period_label}
            for data_set in data_sets
            if data_set.period_date is not None
        ]
        records = sorted(records, key=lambda row: row["period"], reverse=True)
        return records[: query.limit] if query.limit is not None else records

    @staticmethod
    def transform_data(
        query: SecInstitutionalReportingPeriodsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[SecInstitutionalReportingPeriodsData]:
        """Transform raw data to the model format."""
        return [SecInstitutionalReportingPeriodsData.model_validate(d) for d in data]
