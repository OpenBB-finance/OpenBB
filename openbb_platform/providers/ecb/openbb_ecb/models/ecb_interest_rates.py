"""ECB Key Interest Rates Model (FM dataflow).

The three key ECB policy rates: the deposit facility, the marginal lending
facility, and the main refinancing operations (fixed) rate. ECB stores these
as sparse step-functions (one observation per rate change), so the full
change-point series is fetched and forward-filled to a daily series over the
requested window.
"""

# pylint: disable=unused-argument

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.ecb_interest_rates import (
    EuropeanCentralBankInterestRatesData,
    EuropeanCentralBankInterestRatesParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field


class ECBInterestRatesQueryParams(EuropeanCentralBankInterestRatesParams):
    """ECB Key Interest Rates Query."""

    use_cache: bool = Field(
        default=True,
        description="If true, cache parsed results on disk for the dataset TTL.",
    )


class ECBInterestRatesData(EuropeanCentralBankInterestRatesData):
    """ECB Key Interest Rates Data."""


class ECBInterestRatesFetcher(
    Fetcher[ECBInterestRatesQueryParams, list[ECBInterestRatesData]]
):
    """Fetch a key ECB interest rate from the FM dataflow."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> ECBInterestRatesQueryParams:
        """Transform query."""
        return ECBInterestRatesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: ECBInterestRatesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Fetch the full change-point series for the requested key rate."""
        # pylint: disable=import-outside-toplevel
        from openbb_ecb.utils.data_cache import cached_records, make_key
        from openbb_ecb.utils.query_builder import fetch_sdmx_data
        from openbb_ecb.utils.series_keys import FM_RATE_CODES, fm_key

        code = FM_RATE_CODES[query.interest_rate_type]

        async def loader() -> list[dict]:
            # No date filter — the series is sparse; fetch every change point.
            return await fetch_sdmx_data("FM", fm_key(code), raise_empty=False)

        cache_key = make_key("fm", code=code)
        records = await cached_records(
            "fm", cache_key, loader, use_cache=query.use_cache
        )
        if not records:
            raise OpenBBError(
                EmptyDataError("No data found for the requested ECB key rate.")
            )
        return records

    @staticmethod
    def transform_data(
        query: ECBInterestRatesQueryParams, data: list[dict], **kwargs: Any
    ) -> list[ECBInterestRatesData]:
        """Forward-fill the step changes to a daily series over the window."""
        # pylint: disable=import-outside-toplevel
        from datetime import date as dateType

        from pandas import DataFrame, Timestamp, date_range, to_datetime

        frame = DataFrame(
            [
                {"date": r["date"], "rate": r["OBS_VALUE"]}
                for r in data
                if r.get("OBS_VALUE") is not None
            ]
        )
        if frame.empty:
            raise EmptyDataError("No data found for the requested ECB key rate.")
        frame["date"] = to_datetime(frame["date"])
        frame = frame.drop_duplicates("date").set_index("date").sort_index()

        start = Timestamp(query.start_date) if query.start_date else frame.index.min()
        end = (
            Timestamp(query.end_date) if query.end_date else Timestamp(dateType.today())
        )
        daily = date_range(start=start, end=end, freq="D")
        series = (
            frame["rate"]
            .reindex(frame.index.union(daily))
            .ffill()
            .reindex(daily)
            .dropna()
        )
        records = [
            {"date": idx.strftime("%Y-%m-%d"), "rate": float(value)}
            for idx, value in series.items()
        ]
        return [ECBInterestRatesData.model_validate(r) for r in records]
