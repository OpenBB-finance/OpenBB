"""SEC Pay Versus Performance Model."""

from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field, field_validator


class SecPayVersusPerformanceQueryParams(QueryParams):
    """SEC Pay Versus Performance Query.

    The Pay Versus Performance disclosure (Reg S-K Item 402(v)) from the proxy
    statement (DEF 14A), read from the filing's inline XBRL (``ecd:``) facts.
    """

    symbol: str = Field(description="Symbol to get data for.")
    calendar_year: int | None = Field(
        default=None,
        description="Calendar year the proxy was filed. Defaults to the most recent.",
    )
    use_cache: bool = Field(
        default=True,
        description="Use the cache for downloaded filings. Default is True.",
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def _to_upper(cls, v):
        """Upper-case the symbol."""
        return v.upper() if isinstance(v, str) else v

    @field_validator("calendar_year", mode="before", check_fields=False)
    @classmethod
    def _empty_to_none(cls, v):
        """Treat an empty string as None (most recent filing)."""
        return None if v == "" else v


class SecPayVersusPerformanceData(Data):
    """SEC Pay Versus Performance Data."""

    year: int = Field(
        description="Fiscal year.",
        json_schema_extra={"x-widget_config": {"formatterFn": "none"}},
    )
    peo_total_compensation: float | None = Field(
        default=None,
        description="Principal executive officer total compensation (Summary"
        " Compensation Table total).",
        title="PEO Total Compensation",
    )
    peo_compensation_actually_paid: float | None = Field(
        default=None,
        description="Principal executive officer compensation actually paid.",
        title="PEO Compensation Actually Paid",
    )
    average_neo_total_compensation: float | None = Field(
        default=None,
        description="Average total compensation of the non-PEO named executive"
        " officers.",
        title="Average Non-PEO Total Compensation",
    )
    average_neo_compensation_actually_paid: float | None = Field(
        default=None,
        description="Average compensation actually paid to the non-PEO named"
        " executive officers.",
        title="Average Non-PEO Compensation Actually Paid",
    )
    total_shareholder_return: float | None = Field(
        default=None,
        description="Cumulative total shareholder return on a $100 investment.",
    )
    peer_group_total_shareholder_return: float | None = Field(
        default=None,
        description="Peer-group cumulative total shareholder return on a $100"
        " investment.",
    )
    net_income: float | None = Field(default=None, description="Net income.")
    company_selected_measure: float | None = Field(
        default=None,
        description="The company-selected financial performance measure value.",
    )
    company_selected_measure_name: str | None = Field(
        default=None,
        description="Name of the company-selected financial performance measure.",
    )


class SecPayVersusPerformanceFetcher(
    Fetcher[SecPayVersusPerformanceQueryParams, list[SecPayVersusPerformanceData]]
):
    """SEC Pay Versus Performance Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> SecPayVersusPerformanceQueryParams:
        """Transform the query."""
        return SecPayVersusPerformanceQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: SecPayVersusPerformanceQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the Pay Versus Performance XBRL facts from the proxy (DEF 14A)."""
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_sec.models.sec_filing import Filing
        from openbb_sec.utils.proxy_statement import (
            pay_versus_performance,
            resolve_proxy_url,
        )

        url = await resolve_proxy_url(
            query.symbol, query.calendar_year, query.use_cache
        )
        if not url and query.calendar_year is not None:
            url = await resolve_proxy_url(query.symbol, None, query.use_cache)
        if not url:
            raise EmptyDataError(
                f"No proxy statement (DEF 14A) was found for {query.symbol}."
            )

        html = await Filing._adownload_file(url, query.use_cache)
        rows = pay_versus_performance(html or "")
        if not rows:
            raise EmptyDataError(
                "No Pay Versus Performance disclosure was found in the proxy"
                f" statement for {query.symbol}."
            )

        return rows

    @staticmethod
    def transform_data(
        query: SecPayVersusPerformanceQueryParams, data: list[dict], **kwargs: Any
    ) -> list[SecPayVersusPerformanceData]:
        """Transform the data."""
        return [SecPayVersusPerformanceData.model_validate(d) for d in data]
