"""ECB Balance of Payments Model."""

# pylint: disable=unused-argument,too-many-ancestors

from datetime import date as dateType
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.balance_of_payments import (
    BalanceOfPaymentsQueryParams,
    ECBCountry,
    ECBDirectInvestment,
    ECBInvestmentIncome,
    ECBMain,
    ECBOtherInvestment,
    ECBPortfolioInvestment,
    ECBServices,
    ECBSummary,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

from openbb_ecb.utils.bps_series import (
    BPS_COUNTRIES,
    BPS_FREQUENCIES,
    BPS_REPORT_TYPES,
    generate_bps_series_ids,
)


class ECBBalanceOfPaymentsQueryParams(BalanceOfPaymentsQueryParams):
    """ECB Balance of Payments Query."""

    report_type: BPS_REPORT_TYPES = Field(
        default="main",
        description="The report type, the level of detail in the data.",
    )
    frequency: BPS_FREQUENCIES = Field(
        default="monthly",
        description="The frequency of the data.  Monthly is valid only for ['main', 'summary'].",
    )
    country: BPS_COUNTRIES | None = Field(
        default=None,
        description="The country/region of the data.  This parameter will override the 'report_type' parameter.",
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )
    use_cache: bool = Field(
        default=True,
        description="If true, cache parsed results on disk for the dataset TTL.",
    )


class ECBBalanceOfPaymentsData(
    ECBMain,
    ECBSummary,
    ECBServices,
    ECBInvestmentIncome,
    ECBDirectInvestment,
    ECBPortfolioInvestment,
    ECBOtherInvestment,
    ECBCountry,
):
    """ECB Balance of Payments Data."""


class ECBBalanceOfPaymentsFetcher(
    Fetcher[ECBBalanceOfPaymentsQueryParams, list[ECBBalanceOfPaymentsData]]
):
    """Transform the query, extract and transform the data from the ECB endpoints."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> ECBBalanceOfPaymentsQueryParams:
        """Transform query."""
        return ECBBalanceOfPaymentsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: ECBBalanceOfPaymentsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Fetch the raw component series for each balance-of-payments item."""
        # pylint: disable=import-outside-toplevel
        import asyncio

        from openbb_ecb.utils.data_cache import cached_records, make_key
        from openbb_ecb.utils.query_builder import fetch_sdmx_data

        series_ids = generate_bps_series_ids(
            query.frequency, query.report_type, country=query.country
        )
        start = query.start_date.isoformat() if query.start_date else None
        end = query.end_date.isoformat() if query.end_date else None

        async def get_one(name: str, key: str) -> list[dict]:
            async def loader() -> list[dict]:
                return await fetch_sdmx_data(
                    "BPS", key, start_date=start, end_date=end, raise_empty=False
                )

            cache_key = make_key("balance_of_payments", key=key, start=start, end=end)
            records = await cached_records(
                "balance_of_payments", cache_key, loader, use_cache=query.use_cache
            )
            for record in records:
                record["_item"] = name
            return records

        batches = await asyncio.gather(*[get_one(n, k) for n, k in series_ids.items()])
        return [record for batch in batches for record in batch]

    @staticmethod
    def transform_data(
        query: ECBBalanceOfPaymentsQueryParams, data: list[dict], **kwargs: Any
    ) -> list[ECBBalanceOfPaymentsData]:
        """Sum component series, pivot to one row per period, and validate."""
        # pylint: disable=import-outside-toplevel
        from math import isnan

        from pandas import DataFrame

        if not data:
            raise OpenBBError(EmptyDataError("No balance of payments data found."))

        items: dict[str, dict[str, float]] = {}
        for record in data:
            value = record.get("OBS_VALUE")
            if value is None:
                continue
            by_period = items.setdefault(record["_item"], {})
            by_period[record["date"]] = by_period.get(record["date"], 0.0) + value

        if not items:
            raise OpenBBError(EmptyDataError("No balance of payments data found."))

        frame = (
            DataFrame(items)
            .sort_index()
            .reset_index()
            .rename(columns={"index": "period"})
        )
        records = [
            {
                k: (None if (isinstance(v, float) and isnan(v)) else v)
                for k, v in row.items()
            }
            for row in frame.to_dict("records")
        ]
        return [ECBBalanceOfPaymentsData.model_validate(d) for d in records]
