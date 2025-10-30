"""FMP Equity Most Active Model."""

# pylint: disable=unused-argument

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_performance import (
    EquityPerformanceData,
    EquityPerformanceQueryParams,
)
from pydantic import Field, field_validator


class FMPEquityActiveQueryParams(EquityPerformanceQueryParams):
    """FMP Most Active Query.

    Source: https://site.financialmodelingprep.com/developer/docs#most-active
    """


class FMPEquityActiveData(EquityPerformanceData):
    """FMP Most Active Data."""

    __alias_dict__ = {
        "percent_change": "changesPercentage",
    }

    exchange: str = Field(
        description="Stock exchange where the security is listed.",
    )

    @field_validator("percent_change", mode="before", check_fields=False)
    @classmethod
    def _normalize_percent(cls, v):
        """Normalize percent change by removing % sign and converting to float."""
        return v / 100 if v else None


class FMPEquityActiveFetcher(
    Fetcher[FMPEquityActiveQueryParams, list[FMPEquityActiveData]]
):
    """FMP EquityActive Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FMPEquityActiveQueryParams:
        """Transform query params."""
        return FMPEquityActiveQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPEquityActiveQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list:
        """Get the raw data from the FMP API."""
        # pylint: disable=import-outside-toplevel
        from openbb_fmp.utils.helpers import get_data_many

        api_key = credentials.get("fmp_api_key") if credentials else ""
        url = f"https://financialmodelingprep.com/stable/most-actives?apikey={api_key}"

        return await get_data_many(url)

    @staticmethod
    def transform_data(
        query: EquityPerformanceQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FMPEquityActiveData]:
        """Transform data."""
        return [
            FMPEquityActiveData.model_validate(d)
            for d in sorted(
                data,
                key=lambda x: x["changesPercentage"],
                reverse=query.sort == "desc",
            )
        ]
