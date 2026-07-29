"""SEC Executive Compensation Model."""

from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field, field_validator


class SecExecutiveCompensationQueryParams(QueryParams):
    """SEC Executive Compensation Query.

    Executive compensation is the Summary Compensation Table from the company's
    proxy statement (DEF 14A), not the 10-K.
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


class SecExecutiveCompensationData(Data):
    """SEC Executive Compensation Data."""

    content: str = Field(
        description="The Summary Compensation Table from the proxy (DEF 14A)"
        " as a formatted markdown table."
    )


class SecExecutiveCompensationFetcher(
    Fetcher[SecExecutiveCompensationQueryParams, SecExecutiveCompensationData]
):
    """SEC Executive Compensation Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> SecExecutiveCompensationQueryParams:
        """Transform the query."""
        return SecExecutiveCompensationQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: SecExecutiveCompensationQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the Summary Compensation Table from the proxy (DEF 14A)."""
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_sec.models.sec_filing import Filing
        from openbb_sec.utils.proxy_statement import (
            resolve_proxy_url,
            summary_compensation_table,
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
        content = summary_compensation_table(html or "")
        if not content:
            raise EmptyDataError(
                "No Summary Compensation Table was found in the proxy statement for"
                f" {query.symbol}."
            )

        return {"content": content}

    @staticmethod
    def transform_data(
        query: SecExecutiveCompensationQueryParams, data: dict, **kwargs: Any
    ) -> SecExecutiveCompensationData:
        """Transform the data."""
        return SecExecutiveCompensationData.model_validate(data)
