"""Bank of Canada — Daily Exchange Rates (FX_RATES_DAILY).

Maps to OpenBB's standard ``currency.historical`` model. The brief
requires ``close`` to be populated and OHLC left as ``None``.
"""

from datetime import date, timedelta
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.currency_historical import (
    CurrencyHistoricalData,
    CurrencyHistoricalQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

from openbb_government_ca.boc.utils import is_degraded, lookup_series
from openbb_government_ca.utils._http import NetworkError, http_get_json
from openbb_government_ca.utils.helpers import normalize_fx_symbol
from openbb_government_ca.utils.metadata import GovernmentCaMetadata


def _default_start_date() -> date:
    """Return 30 days ago as a default start_date."""
    return date.today() - timedelta(days=30)


class BankOfCanadaFXQueryParams(CurrencyHistoricalQueryParams):
    """BoC FX Query."""

    __json_schema_extra__ = {
        "symbol": {
            "description": (
                "Currency pair in BASE/QUOTE format (e.g. 'USDCAD', 'USD/CAD', "
                "'fxusdcad'). The BoC publishes rates as 1 unit of BASE "
                "currency in CAD (the quote)."
            ),
        },
    }

    start_date: date | None = Field(
        default=None,
        description=(
            "Start date (YYYY-MM-DD). Defaults to 30 days ago if not provided."
        ),
    )
    end_date: date | None = Field(
        default=None,
        description="End date (YYYY-MM-DD). Defaults to today if not provided.",
    )


class BankOfCanadaFXData(CurrencyHistoricalData):
    """BoC FX Data."""

    series: str | None = Field(
        default=None,
        description="The BoC Valet series name (e.g. 'FXUSDCAD').",
    )


class BankOfCanadaFXFetcher(
    Fetcher[BankOfCanadaFXQueryParams, list[BankOfCanadaFXData]]
):
    """BoC FX Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> BankOfCanadaFXQueryParams:
        """Transform raw params into a validated query model."""
        transformed = params.copy()
        if transformed.get("symbol"):
            transformed["symbol"] = normalize_fx_symbol(str(transformed["symbol"]))
        if transformed.get("start_date") is None:
            transformed["start_date"] = _default_start_date()
        if transformed.get("end_date") is None:
            transformed["end_date"] = date.today()
        return BankOfCanadaFXQueryParams(**transformed)

    @staticmethod
    def extract_data(
        query: BankOfCanadaFXQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Fetch observations from the BoC Valet API."""
        meta = GovernmentCaMetadata()
        boc_cache = meta.boc

        if is_degraded(boc_cache):
            raise OpenBBError(
                "Bank of Canada metadata cache is in degraded mode — the "
                "package was built when www.bankofcanada.ca was unreachable. "
                "Reinstall openbb-government-ca with "
                "OPENBB_GOVERNMENT_CA_FORCE_CACHE_REBUILD=1 to retry."
            )

        try:
            entry = lookup_series(query.symbol, boc_cache)
        except KeyError as exc:
            raise OpenBBError(str(exc)) from exc

        observations_url = entry.get("observations_url", "")
        if not observations_url:
            raise OpenBBError(
                f"BoC series {query.symbol!r} has no observations_url in the cache. "
                f"The cache may be corrupted — reinstall the package."
            )

        assert query.start_date is not None  # noqa: S101
        assert query.end_date is not None  # noqa: S101
        params: dict[str, str] = {
            "start_date": query.start_date.strftime("%Y-%m-%d"),
            "end_date": query.end_date.strftime("%Y-%m-%d"),
        }

        try:
            payload = http_get_json(observations_url, params=params, timeout=30.0)
        except NetworkError as exc:
            raise OpenBBError(
                f"Failed to fetch BoC observations for {query.symbol!r} "
                f"from {observations_url}: {exc}"
            ) from exc

        observations = (
            payload.get("observations", []) if isinstance(payload, dict) else []
        )
        if not observations:
            raise EmptyDataError(
                f"BoC returned no observations for {query.symbol!r} in the "
                f"date range {query.start_date} to {query.end_date}."
            )

        for obs in observations:
            obs["_series"] = query.symbol

        return observations

    @staticmethod
    def transform_data(
        query: BankOfCanadaFXQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[BankOfCanadaFXData]:
        """Map raw Valet observations to the standard ``CurrencyHistoricalData`` model."""
        output: list[BankOfCanadaFXData] = []
        for obs in data:
            obs_date_str = obs.get("d")
            if not obs_date_str:
                continue
            try:
                obs_date = date.fromisoformat(str(obs_date_str))
            except ValueError:
                continue

            series_name = str(obs.get("_series", ""))
            series_block = obs.get(series_name, {})
            value_str = (
                series_block.get("v") if isinstance(series_block, dict) else None
            )
            if value_str is None or value_str == "":
                continue
            try:
                close = float(value_str)
            except (TypeError, ValueError):
                continue

            output.append(
                BankOfCanadaFXData(
                    date=obs_date,
                    open=None,
                    high=None,
                    low=None,
                    close=close,
                    volume=None,
                    vwap=None,
                    series=series_name or None,
                )
            )

        output.sort(key=lambda x: x.date)
        return output
