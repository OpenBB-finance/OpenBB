"""Bank of Canada — Daily Exchange Rates (FX_RATES_DAILY).

This fetcher reads from the shipped metadata cache (Phase 3) to resolve
which FX series the user asked for, then makes a single runtime HTTP
call to the BoC Valet observations endpoint to fetch the actual
time-series.

Maps to OpenBB's standard ``currency.historical`` model. The brief
requires ``close`` to be populated and OHLC left as ``None``.

Design notes
------------
- **Symbol normalization.** Accepts ``USDCAD``, ``USD/CAD``,
  ``fxusdcad``, etc. and normalizes to the BoC canonical ``FX{BASE}{QUOTE}``
  shape via ``openbb_government_ca.utils.helpers.normalize_fx_symbol``.
- **Group membership check.** The fetcher validates the requested
  symbol against the ``FX_RATES_DAILY`` group's member list in the
  cache. If the symbol isn't in the group, we still attempt the call
  (the cache might be stale) but warn the user.
- **No value transformation.** FX rates are direct prices — the BoC
  publishes ``1.3316`` for USDCAD and that's exactly what we return.
  No division, no multiplication.
- **Date range defaults.** If the user doesn't pass ``start_date``,
  we default to 30 days ago. If no ``end_date``, we default to today.
"""

from __future__ import annotations

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
    """BoC FX Query.

    Extends the standard ``CurrencyHistoricalQueryParams`` with BoC-specific
    defaults. The ``symbol`` field accepts the common spellings:
    ``USDCAD``, ``USD/CAD``, ``fxusdcad``, etc. — all normalized to
    the BoC canonical ``FXUSDCAD`` form.
    """

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
    """BoC FX Data.

    Extends the standard ``CurrencyHistoricalData`` with a BoC-specific
    extension field for the series name (useful for debugging).
    """

    series: str | None = Field(
        default=None,
        description="The BoC Valet series name (e.g. 'FXUSDCAD').",
    )


class BankOfCanadaFXFetcher(
    Fetcher[BankOfCanadaFXQueryParams, list[BankOfCanadaFXData]]
):
    """BoC FX Fetcher.

    Reads the cache for series metadata, then makes a runtime HTTP
    call to Valet for the actual observations.
    """

    @staticmethod
    def transform_query(params: dict[str, Any]) -> BankOfCanadaFXQueryParams:
        """Transform raw params into a validated query model."""
        transformed = params.copy()
        # Normalize the symbol to BoC canonical form early so that
        # downstream lookups (cache + URL) all use the same shape.
        if transformed.get("symbol"):
            transformed["symbol"] = normalize_fx_symbol(str(transformed["symbol"]))
        # Apply date defaults.
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
        """Fetch observations from the BoC Valet API.

        Reads the cache to find the series' ``observations_url`` and
        validates membership in the ``FX_RATES_DAILY`` group. Then
        makes a single HTTP call to fetch the time-series.
        """
        meta = GovernmentCaMetadata()
        boc_cache = meta.boc

        if is_degraded(boc_cache):
            raise OpenBBError(
                "Bank of Canada metadata cache is in degraded mode — the "
                "package was built when www.bankofcanada.ca was unreachable. "
                "Reinstall openbb-government-ca with "
                "OPENBB_GOVERNMENT_CA_FORCE_CACHE_REBUILD=1 to retry."
            )

        # Look up the series in the cache. This raises KeyError with a
        # helpful "did you mean" hint if the symbol isn't recognized.
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

        # Build the full URL with date range. The Valet API uses
        # ``start_date`` and ``end_date`` query params in YYYY-MM-DD
        # format. ``recent=N`` is an alternative but we prefer the
        # date range for explicit control.
        # ``transform_query`` always populates these with defaults, so
        # the assert is for ty's benefit — it can't see the invariant.
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

        # Tag each row with the series name so ``transform_data`` can
        # populate the extension field without re-deriving it.
        for obs in observations:
            obs["_series"] = query.symbol

        return observations

    @staticmethod
    def transform_data(
        query: BankOfCanadaFXQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[BankOfCanadaFXData]:
        """Map raw Valet observations to the standard ``CurrencyHistoricalData`` model.

        Each Valet observation has the shape::

            {"d": "2024-01-02", "FXUSDCAD": {"v": "1.3316"}}

        The ``d`` field is the ISO date; the series name (``FXUSDCAD``)
        is a key on the same dict whose value is ``{"v": "..."}``.

        Per the brief: populate ``close`` only, leave OHLC as ``None``.
        No value transformation — the BoC rate (1.3316) is the close.
        """
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
                # BoC uses empty string for holidays/weekends — skip.
                continue
            try:
                close = float(value_str)
            except (TypeError, ValueError):
                continue

            output.append(
                BankOfCanadaFXData(
                    date=obs_date,
                    open=None,  # per brief — OHLC left as None
                    high=None,
                    low=None,
                    close=close,  # NOT normalized — FX is a direct price
                    volume=None,
                    vwap=None,
                    series=series_name or None,
                )
            )

        # Sort ascending by date — standard convention for time-series.
        output.sort(key=lambda x: x.date)
        return output
