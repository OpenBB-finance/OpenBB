"""Market data loading with local parquet cache."""

from __future__ import annotations

import logging
import os
import re
import shutil
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd
import yfinance as yf

from openbb_quant_ml.service.cache_registry import update_data_version
from openbb_quant_ml.service.constants import (
    ARTIFACT_ROOT,
    CACHE_DIR,
    CACHE_TTL_DAYS,
    RAW_STORE_DIR,
)
from openbb_quant_ml.service.storage import save_parquet_atomic

LOGGER = logging.getLogger(__name__)


def _safe_symbol(symbol: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]+", "_", symbol)


def _cache_path(symbol: str) -> Path:
    # Keep backward compatibility with legacy cache location.
    legacy_path = CACHE_DIR / f"{_safe_symbol(symbol)}.parquet"
    new_path = RAW_STORE_DIR / f"{_safe_symbol(symbol)}.parquet"
    if new_path.exists() or not legacy_path.exists():
        return new_path
    return legacy_path


def _contains_non_ascii(text: str) -> bool:
    try:
        text.encode("ascii")
        return False
    except UnicodeEncodeError:
        return True


def _ensure_ssl_bundle_path() -> None:
    """Force SSL bundle path to an ASCII-only location for curl-based yfinance backends."""
    try:
        import certifi
    except Exception:
        return

    source_path = Path(certifi.where())
    if not source_path.exists():
        return

    # In some Windows environments, curl_cffi fails when CA path includes non-ASCII characters.
    needs_copy = _contains_non_ascii(str(source_path))
    if needs_copy:
        target_path = ARTIFACT_ROOT / "certs" / "cacert.pem"
        target_path.parent.mkdir(parents=True, exist_ok=True)
        if (
            not target_path.exists()
            or target_path.stat().st_size != source_path.stat().st_size
        ):
            shutil.copy2(source_path, target_path)
        bundle_path = str(target_path)
    else:
        bundle_path = str(source_path)

    os.environ["SSL_CERT_FILE"] = bundle_path
    os.environ["REQUESTS_CA_BUNDLE"] = bundle_path
    os.environ["CURL_CA_BUNDLE"] = bundle_path


def _is_cache_fresh(path: Path, ttl_days: int) -> bool:
    if not path.exists():
        return False
    modified_at = datetime.fromtimestamp(path.stat().st_mtime)
    return datetime.now() - modified_at <= timedelta(days=ttl_days)


def _normalize_frame(frame: pd.DataFrame, symbol: str) -> pd.DataFrame:
    if frame.empty:
        return frame
    df = frame.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [str(col[0]).lower() for col in df.columns]
    else:
        df.columns = [str(col).lower() for col in df.columns]
    df = df.reset_index()
    df.columns = [str(col).lower() for col in df.columns]
    if "date" not in df.columns:
        first_col = df.columns[0]
        df = df.rename(columns={first_col: "date"})
    keep_columns = ["date", "open", "high", "low", "close", "volume"]
    for column in keep_columns:
        if column not in df.columns:
            df[column] = float("nan")
    df = df[keep_columns]
    df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)
    df["symbol"] = symbol
    return (
        df.dropna(subset=["date", "close"]).sort_values("date").reset_index(drop=True)
    )


def _extract_result_frame(result: Any) -> pd.DataFrame:
    if isinstance(result, pd.DataFrame):
        return result
    for method_name in ("to_df", "to_dataframe"):
        method = getattr(result, method_name, None)
        if callable(method):
            candidate = method()
            if isinstance(candidate, pd.DataFrame):
                return candidate
    return pd.DataFrame()


from tenacity import retry, stop_after_attempt, wait_exponential


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10), reraise=True)
def _fetch_obb_prices(
    symbol: str,
    start_date: date,
    end_date: date,
    provider: str,
) -> pd.DataFrame:
    provider_norm = str(provider or "").strip().lower()
    if not provider_norm:
        return pd.DataFrame()
    try:
        from openbb import obb  # type: ignore[import-not-found]
    except Exception as exc:  # noqa: BLE001
        LOGGER.warning(
            "OpenBB Core import failed for symbol %s/provider %s: %s",
            symbol,
            provider_norm,
            exc,
        )
        return pd.DataFrame()

    try:
        result = obb.equity.price.historical(
            symbol=symbol,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            provider=provider_norm,
        )
    except Exception as exc:  # noqa: BLE001
        LOGGER.warning(
            "OpenBB Core fetch failed for symbol %s/provider %s: %s",
            symbol,
            provider_norm,
            exc,
        )
        return pd.DataFrame()

    extracted = _extract_result_frame(result)
    return _normalize_frame(extracted, symbol)


@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=5), reraise=True)
def _fetch_yfinance_prices(
    symbol: str,
    start_date: date,
    end_date: date,
    timeout_sec: int,
    retry: int,  # kept for signature compatibility
    backoff_base: float, # kept for signature compatibility
) -> tuple[pd.DataFrame, Exception | None]:
    _ensure_ssl_bundle_path()
    try:
        fresh = yf.download(
            tickers=symbol,
            start=start_date.isoformat(),
            end=end_date.isoformat(),
            auto_adjust=False,
            progress=False,
            timeout=max(1, int(timeout_sec)),
            threads=False,
        )
    except Exception as exc:
        raise ValueError(f"yfinance download failed for {symbol}: {exc}") from exc

    # Some yfinance versions return empty download frames while ticker history works.
    if fresh is None or fresh.empty:
        try:
            fresh = yf.Ticker(symbol).history(
                start=start_date.isoformat(),
                end=end_date.isoformat(),
                auto_adjust=False,
                timeout=max(1, int(timeout_sec)),
            )
        except Exception as exc:
            raise ValueError(
                f"yfinance returned empty download and history failed for {symbol}: {exc}"
            ) from exc
        if fresh is None or fresh.empty:
            raise ValueError(f"yfinance returned empty dataframe for {symbol}")
    return _normalize_frame(fresh, symbol), None


def _load_cached(symbol: str) -> pd.DataFrame:
    cache_path = _cache_path(symbol)
    if not cache_path.exists():
        return pd.DataFrame()
    df = pd.read_parquet(cache_path)
    if df.empty:
        return df
    df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)
    return df.sort_values("date").reset_index(drop=True)


def _save_cache(symbol: str, frame: pd.DataFrame, source: str = "yfinance") -> None:
    cache_path = _cache_path(symbol)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    save_parquet_atomic(cache_path, frame, index=False)
    update_data_version(symbol=symbol, frame=frame, source=source)


def load_symbol_prices(
    symbol: str,
    start_date: date,
    end_date: date,
    provider: str = "yfinance",
    ttl_days: int = CACHE_TTL_DAYS,
    timeout_sec: int = 8,
    retry: int = 2,
    backoff_base: float = 2.0,
) -> pd.DataFrame:
    """Load OHLCV series from cache, OpenBB Core provider, or yfinance fallback."""

    cached = _load_cached(symbol)
    has_coverage = False
    if not cached.empty:
        min_date = cached["date"].min().date()
        max_date = cached["date"].max().date()
        has_coverage = min_date <= start_date and max_date >= end_date

    if not cached.empty and has_coverage:
        return cached[
            (cached["date"].dt.date >= start_date)
            & (cached["date"].dt.date <= end_date)
        ].copy()

    download_start = start_date - timedelta(days=400)
    if not cached.empty:
        cached_max = cached["date"].max().date()
        download_start = max(start_date, cached_max - timedelta(days=7))

    download_end = end_date + timedelta(days=5)
    provider_norm = str(provider or "").strip().lower()
    normalized = pd.DataFrame()
    source_used = provider_norm or "yfinance"
    if provider_norm and provider_norm != "yfinance":
        try:
            normalized = _fetch_obb_prices(
                symbol=symbol,
                start_date=download_start,
                end_date=download_end,
                provider=provider_norm,
            )
            source_used = provider_norm
        except Exception as exc:
            LOGGER.warning("OpenBB fetch exception: %s", exc)
    last_exc: Exception | None = None
    if normalized.empty:
        try:
            normalized, last_exc = _fetch_yfinance_prices(
                symbol=symbol,
                start_date=download_start,
                end_date=download_end,
                timeout_sec=timeout_sec,
                retry=retry,
                backoff_base=backoff_base,
            )
            source_used = "yfinance"
            if not normalized.empty and provider_norm and provider_norm != "yfinance":
                LOGGER.warning(
                    "Provider fallback to yfinance for symbol %s (requested provider: %s).",
                    symbol,
                    provider,
                )
        except Exception as exc:
            last_exc = exc

    if normalized.empty:
        if not cached.empty:
            return cached[
                (cached["date"].dt.date >= start_date)
                & (cached["date"].dt.date <= end_date)
            ].copy()
        if last_exc is not None:
            raise ValueError(
                f"Failed to load market data for symbol: {symbol} ({last_exc})"
            ) from last_exc
        raise ValueError(f"Failed to load market data for symbol: {symbol}")

    # Keep the most complete frame in cache by unioning old+new and dropping duplicates.
    merged = (
        pd.concat([cached, normalized], ignore_index=True)
        if not cached.empty
        else normalized
    )
    merged = merged.sort_values("date").drop_duplicates(subset=["date"], keep="last")
    _save_cache(symbol, merged, source=source_used)
    return merged[
        (merged["date"].dt.date >= start_date) & (merged["date"].dt.date <= end_date)
    ].copy()


def load_market_data(
    symbols: list[str],
    start_date: date,
    end_date: date,
    provider: str = "yfinance",
    ttl_days: int = CACHE_TTL_DAYS,
    progress_callback: Callable[[int, int, str, bool], None] | None = None,
    timeout_sec: int = 20,
    retry: int = 2,
    backoff_base: float = 2.0,
    max_workers: int = 6,
) -> tuple[dict[str, pd.DataFrame], list[str]]:
    """Load market data for a symbol universe."""
    datasets: dict[str, pd.DataFrame] = {}
    skipped: list[str] = []
    total = max(len(symbols), 1)

    def _load_one(symbol: str) -> tuple[str, pd.DataFrame | None]:
        series = load_symbol_prices(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            provider=provider,
            ttl_days=ttl_days,
            timeout_sec=timeout_sec,
            retry=retry,
            backoff_base=backoff_base,
        )
        return symbol, series

    worker_count = max(1, min(int(max_workers), max(len(symbols), 1)))
    if worker_count <= 1:
        for idx, symbol in enumerate(symbols, start=1):
            loaded = False
            try:
                _, series = _load_one(symbol)
                if series is None or len(series) < 120:
                    skipped.append(symbol)
                else:
                    datasets[symbol] = series
                    loaded = True
            except Exception:
                skipped.append(symbol)
            finally:
                if progress_callback is not None:
                    progress_callback(idx, total, symbol, loaded)
        return datasets, skipped

    completed = 0
    with ThreadPoolExecutor(max_workers=worker_count, thread_name_prefix="quant-data") as pool:
        futures: dict[Future[tuple[str, pd.DataFrame | None]], str] = {
            pool.submit(_load_one, symbol): symbol for symbol in symbols
        }
        for future in as_completed(futures):
            symbol = futures[future]
            completed += 1
            loaded = False
            try:
                _, series = future.result()
                if series is None or len(series) < 120:
                    skipped.append(symbol)
                else:
                    datasets[symbol] = series
                    loaded = True
            except Exception:
                skipped.append(symbol)
            finally:
                if progress_callback is not None:
                    progress_callback(completed, total, symbol, loaded)
    return datasets, skipped


def build_close_panel(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Build wide close-price dataframe indexed by date."""
    if not data:
        return pd.DataFrame()
    pivot_source = pd.concat(
        [df[["date", "symbol", "close"]] for df in data.values()], ignore_index=True
    )
    panel = pivot_source.pivot(
        index="date", columns="symbol", values="close"
    ).sort_index()
    return panel


def build_price_panel(data: dict[str, pd.DataFrame], price_field: str) -> pd.DataFrame:
    """Build wide panel for one price field indexed by date."""
    if not data:
        return pd.DataFrame()
    field = str(price_field).lower()
    rows: list[pd.DataFrame] = []
    for frame in data.values():
        if field not in frame.columns:
            continue
        rows.append(frame[["date", "symbol", field]])
    if not rows:
        return pd.DataFrame()
    pivot_source = pd.concat(rows, ignore_index=True)
    panel = pivot_source.pivot(
        index="date", columns="symbol", values=field
    ).sort_index()
    return panel
