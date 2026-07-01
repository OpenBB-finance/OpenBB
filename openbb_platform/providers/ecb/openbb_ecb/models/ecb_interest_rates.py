"""ECB Key Interest Rates Model."""

# pylint: disable=unused-argument

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

from openbb_ecb.utils.series_keys import FM_RATE_CODES

_KEY_RATES = {
    "DFR": "deposit_facility",
    "MRR_FR": "main_refinancing",
    "MLFR": "marginal_lending",
}
_KEY_RATES_KEY = "B.U2.EUR.4F.KR." + "+".join(FM_RATE_CODES.values()) + ".LEV"


def _rate(label: str):
    """Build a percent-valued policy-rate column."""
    return Field(
        default=None,
        description=f"{label}, in percent.",
        json_schema_extra={
            "x-widget_config": {"headerName": label},
            "x-unit_measurement": "percent",
        },
    )


class ECBInterestRatesQueryParams(QueryParams):
    """ECB Key Interest Rates Query."""

    start_date: dateType | None = Field(
        default=None, description="Start date of the data window."
    )
    end_date: dateType | None = Field(
        default=None, description="End date of the data window."
    )
    use_cache: bool = Field(
        default=True,
        description="If true, cache parsed results on disk for the dataset TTL.",
    )


class ECBInterestRatesData(Data):
    """ECB Key Interest Rates Data."""

    date: dateType = Field(description="The date of the rates.")
    deposit_facility: float | None = _rate("Deposit facility")
    main_refinancing: float | None = _rate("Main refinancing operations")
    marginal_lending: float | None = _rate("Marginal lending facility")


class ECBInterestRatesFetcher(
    Fetcher[ECBInterestRatesQueryParams, list[ECBInterestRatesData]]
):
    """Fetch the key ECB interest rates from the FM dataflow."""

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
        """Fetch the change-point series for the key rates."""
        # pylint: disable=import-outside-toplevel
        from openbb_ecb.utils.data_cache import cached_records, make_key
        from openbb_ecb.utils.query_builder import fetch_sdmx_data

        async def loader() -> list[dict]:
            return await fetch_sdmx_data("FM", _KEY_RATES_KEY, raise_empty=False)

        records = await cached_records(
            "fm",
            make_key("fm", key=_KEY_RATES_KEY),
            loader,
            use_cache=query.use_cache,
        )
        if not records:
            raise OpenBBError(EmptyDataError("No data found for the ECB key rates."))
        return records

    @staticmethod
    def transform_data(
        query: ECBInterestRatesQueryParams, data: list[dict], **kwargs: Any
    ) -> list[ECBInterestRatesData]:
        """Pivot the rates and forward-fill to a daily series."""
        # pylint: disable=import-outside-toplevel
        from pandas import DataFrame, Timestamp, date_range, isna, to_datetime

        rows = [
            {
                "date": record["date"],
                "field": _KEY_RATES.get(record.get("PROVIDER_FM_ID") or ""),
                "rate": record["OBS_VALUE"],
            }
            for record in data
            if record.get("OBS_VALUE") is not None
        ]
        frame = DataFrame([row for row in rows if row["field"]])
        if frame.empty:
            raise EmptyDataError("No data found for the ECB key rates.")
        frame["date"] = to_datetime(frame["date"])
        pivot = frame.pivot_table(
            index="date", columns="field", values="rate", aggfunc="last"
        ).sort_index()

        start = Timestamp(query.start_date) if query.start_date else pivot.index.min()
        end = (
            Timestamp(query.end_date)
            if query.end_date
            else Timestamp(datetime.now().date())
        )
        daily = date_range(start=start, end=end, freq="D")
        pivot = pivot.reindex(pivot.index.union(daily)).ffill().reindex(daily)

        records: list[dict] = []
        for idx in daily:
            row = pivot.loc[idx]
            record: dict = {"date": idx.strftime("%Y-%m-%d")}
            for field in _KEY_RATES.values():
                value = row.get(field)
                record[field] = None if value is None or isna(value) else float(value)
            records.append(record)
        return [ECBInterestRatesData.model_validate(r) for r in records]
