"""Refresh local universe CSV files for quant_ml.

This tool keeps existing files safe by using atomic replacement and by
returning per-universe failures without crashing the whole run.
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import sys
import tempfile
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from io import StringIO
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

import pandas as pd
import yaml

from openbb_quant_ml.service.universe import get_universe_minimum_required
from openbb_quant_ml.service.universe_builder import UNIVERSE_INPUT_DIR

UNIVERSE_IDS_ALL = (
    "kospi200",
    "kosdaq100",
    "sp500",
    "nasdaq100",
    "sox",
    "dow30",
    "russell1000",
    "all_in_one",
)
KR_TAXONOMY_PATH = (
    Path(__file__).resolve().parent.parent / "config" / "kr_sector_taxonomy.yaml"
)
UNIVERSE_CONFIG_PATH = (
    Path(__file__).resolve().parent.parent / "config" / "universe.yaml"
)
RUSSELL1000_ISHARES_CSV_URL = (
    "https://www.ishares.com/us/products/239707/"
    "ishares-russell-1000-etf/1467271812596.ajax?"
    "fileType=csv&fileName=IWB_holdings&dataType=fund"
)
ALL_IN_ONE_SOURCE_UNIVERSES: tuple[str, ...] = (
    "kospi200",
    "kosdaq100",
    "sp500",
    "nasdaq100",
    "dow30",
    "sox",
    "russell1000",
)
ETF_CATEGORIES_FOR_ALL_IN_ONE: set[str] = {
    "bond_etf",
    "commodity_etf",
    "currency_etf",
}
UNIVERSE_CSV_BASE_FIELDS: tuple[str, ...] = (
    "symbol",
    "name",
    "market",
    "sector_l1",
    "category_l2",
    "data_asof",
    "source",
)


@dataclass(frozen=True)
class RefreshResult:
    """Result for one universe refresh job."""

    universe_id: str
    ok: bool
    fetched: int
    normalized: int
    valid: int
    invalid: int
    message: str


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _log(msg: str) -> None:
    print(msg, file=sys.stderr)


def _atomic_write_rows_csv(
    path: Path, rows: list[dict[str, str]], fieldnames: list[str]
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=str(path.parent)
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for row in rows:
                writer.writerow({name: row.get(name, "") for name in fieldnames})
            file.flush()
            os.fsync(file.fileno())
        os.replace(tmp_name, path)
    finally:
        try:
            if os.path.exists(tmp_name):
                os.remove(tmp_name)
        except OSError:
            pass


def _atomic_write_csv(path: Path, symbols: list[str]) -> None:
    rows = [{"symbol": str(symbol)} for symbol in symbols if str(symbol).strip()]
    _atomic_write_rows_csv(path, rows, fieldnames=["symbol"])


def _sanitize_token(value: str) -> str:
    value = value.strip().upper()
    value = re.sub(r"\s+", "", value)
    value = re.sub(r"[^A-Z0-9.\-_]", "", value)
    return value


def _normalize_us_ticker(raw: str) -> str:
    token = _sanitize_token(raw)
    token = token.replace("/", "-")
    if re.fullmatch(r"[A-Z]{1,6}\.[A-Z]{1,2}", token):
        token = token.replace(".", "-")
    class_share_aliases = {
        "BFA": "BF-A",
        "BRKB": "BRK-B",
        "BFB": "BF-B",
        "CWENA": "CWEN-A",
        "HEIA": "HEI-A",
        "LENB": "LEN-B",
        "UHALB": "UHAL-B",
    }
    token = class_share_aliases.get(token, token)
    return token


def _normalize_kr_code(raw: str, suffix: str) -> str:
    code = re.sub(r"[^0-9]", "", str(raw).strip())
    if len(code) != 6:
        return ""
    return f"{code}{suffix}"


def _dedupe_sort(items: Iterable[str]) -> list[str]:
    return sorted({item for item in items if item})


def _normalize_symbol(value: str) -> str:
    return str(value or "").strip().upper()


def _symbol_only_rows(symbols: list[str]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    seen: set[str] = set()
    for symbol in symbols:
        normalized = _normalize_symbol(symbol)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        out.append({"symbol": normalized})
    return out


def _read_rows_from_csv(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    if not path.exists():
        return rows
    with path.open(encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        columns = [column for column in (reader.fieldnames or []) if column]
        symbol_col = (
            "symbol" if "symbol" in columns else columns[0] if columns else None
        )
        if symbol_col is None:
            return rows
        for source_row in reader:
            symbol = _normalize_symbol(source_row.get(symbol_col, ""))
            if not symbol:
                continue
            row: dict[str, str] = {"symbol": symbol}
            for column in UNIVERSE_CSV_BASE_FIELDS[1:]:
                value = str(source_row.get(column, "")).strip()
                if value:
                    row[column] = value
            rows.append(row)
    return _dedupe_rows_by_symbol(rows)


def _infer_market(symbol: str) -> str:
    token = _normalize_symbol(symbol)
    if token.endswith(".KS"):
        return "KOSPI"
    if token.endswith(".KQ"):
        return "KOSDAQ"
    return "US"


def _load_allowed_etf_rows() -> list[dict[str, str]]:
    if not UNIVERSE_CONFIG_PATH.exists():
        return []
    try:
        with UNIVERSE_CONFIG_PATH.open(encoding="utf-8") as file:
            payload = yaml.safe_load(file) or {}
    except Exception:  # noqa: BLE001
        return []
    assets = payload.get("assets", [])
    if not isinstance(assets, list):
        return []

    rows: list[dict[str, str]] = []
    for asset in assets:
        if not isinstance(asset, dict):
            continue
        symbol = _normalize_symbol(asset.get("symbol", ""))
        category = str(asset.get("category", "")).strip()
        if not symbol or category not in ETF_CATEGORIES_FOR_ALL_IN_ONE:
            continue
        rows.append(
            {
                "symbol": symbol,
                "market": "US",
                "category_l2": category,
                "source": "universe.yaml",
            }
        )
    return _dedupe_rows_by_symbol(rows)


def _resolve_source_universe_path(universe_id: str, outdir: Path) -> Path | None:
    candidates = [
        outdir / f"{universe_id}.csv",
        Path(UNIVERSE_INPUT_DIR) / f"{universe_id}.csv",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def _build_all_in_one_rows(outdir: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    missing_sources: list[str] = []
    for universe_id in ALL_IN_ONE_SOURCE_UNIVERSES:
        source_path = _resolve_source_universe_path(universe_id, outdir)
        if source_path is None:
            missing_sources.append(universe_id)
            continue
        for source_row in _read_rows_from_csv(source_path):
            symbol = _normalize_symbol(source_row.get("symbol", ""))
            if not symbol:
                continue
            normalized: dict[str, str] = {
                "symbol": symbol,
                "market": str(source_row.get("market", "")).strip()
                or _infer_market(symbol),
                "source": str(source_row.get("source", "")).strip() or universe_id,
            }
            for column in ("name", "sector_l1", "data_asof"):
                value = str(source_row.get(column, "")).strip()
                if value:
                    normalized[column] = value
            category_l2 = (
                str(source_row.get("category_l2", "")).strip()
                or str(source_row.get("category", "")).strip()
                or "equity_stock"
            )
            normalized["category_l2"] = category_l2
            rows.append(normalized)

    if missing_sources:
        raise RuntimeError(
            "missing source universe csv(s) for all_in_one: "
            + ", ".join(sorted(missing_sources))
        )

    rows.extend(_load_allowed_etf_rows())
    deduped = _dedupe_rows_by_symbol(rows)
    if not deduped:
        raise RuntimeError("all_in_one produced no symbols")
    return deduped


def _dedupe_rows_by_symbol(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    merged: dict[str, dict[str, str]] = {}
    for row in rows:
        symbol = _normalize_symbol(row.get("symbol", ""))
        if not symbol:
            continue
        existing = merged.get(symbol, {"symbol": symbol})
        for key, value in row.items():
            if key == "symbol":
                continue
            value_clean = str(value).strip()
            if value_clean:
                existing[key] = value_clean
        merged[symbol] = existing
    return sorted(merged.values(), key=lambda item: item["symbol"])


def _universe_rows_fieldnames(rows: list[dict[str, str]]) -> list[str]:
    extra: list[str] = []
    for key in UNIVERSE_CSV_BASE_FIELDS[1:]:
        if any(str(row.get(key, "")).strip() for row in rows):
            extra.append(key)
    return ["symbol", *extra]


def _load_kr_taxonomy() -> dict[str, Any]:
    if not KR_TAXONOMY_PATH.exists():
        return {
            "symbol_overrides": {},
            "name_keywords": [],
            "sector_defaults": {},
            "default_category_l2": "other",
        }
    try:
        with KR_TAXONOMY_PATH.open(encoding="utf-8") as file:
            payload = yaml.safe_load(file) or {}
    except Exception:  # noqa: BLE001
        payload = {}
    payload.setdefault("symbol_overrides", {})
    payload.setdefault("name_keywords", [])
    payload.setdefault("sector_defaults", {})
    payload.setdefault("default_category_l2", "other")
    return payload


def _classify_kr_category_l2(
    symbol: str, name: str, sector_l1: str, taxonomy: dict[str, Any]
) -> str:
    symbol_key = _normalize_symbol(symbol)
    overrides = (
        taxonomy.get("symbol_overrides", {}) if isinstance(taxonomy, dict) else {}
    )
    if isinstance(overrides, dict):
        mapped = str(overrides.get(symbol_key, "")).strip()
        if mapped:
            return mapped

    name_text = str(name or "").strip()
    for rule in taxonomy.get("name_keywords", []) if isinstance(taxonomy, dict) else []:
        if not isinstance(rule, dict):
            continue
        keyword = str(rule.get("keyword", "")).strip()
        category_l2 = str(rule.get("category_l2", "")).strip()
        if keyword and category_l2 and keyword in name_text:
            return category_l2

    sector_key = str(sector_l1 or "").strip()
    sector_defaults = (
        taxonomy.get("sector_defaults", {}) if isinstance(taxonomy, dict) else {}
    )
    if isinstance(sector_defaults, dict):
        mapped = str(sector_defaults.get(sector_key, "")).strip()
        if mapped:
            return mapped

    fallback = (
        taxonomy.get("default_category_l2", "other")
        if isinstance(taxonomy, dict)
        else "other"
    )
    fallback_clean = str(fallback).strip()
    return fallback_clean or "other"


def _fetch_html(url: str, timeout_sec: int = 20) -> str:
    req = Request(url, headers={"User-Agent": "Mozilla/5.0 (universe-refresh)"})
    with urlopen(req, timeout=timeout_sec) as resp:
        data = resp.read()
    return data.decode("utf-8", errors="replace")


def _pick_table_with_column(
    tables: list[pd.DataFrame], col_candidates: list[str]
) -> tuple[pd.DataFrame, str]:
    lowered = [candidate.lower() for candidate in col_candidates]
    for table in tables:
        cols = [str(col) for col in table.columns]
        cols_lower = [col.lower() for col in cols]
        for wanted in lowered:
            if wanted in cols_lower:
                idx = cols_lower.index(wanted)
                return table, cols[idx]
    raise ValueError(f"could not find columns {col_candidates}")


def _extract_col_values(df: pd.DataFrame, col_name: str) -> list[str]:
    series = df[col_name]
    return [str(item) for item in series.dropna().tolist()]


def _extract_sox_from_html_list(html: str) -> list[str]:
    """Fallback parser for SOX page variants that expose symbols as list items."""
    raw = re.findall(
        r"<li>.*?,\s*([A-Z]{1,6}(?:\.[A-Z]{1,2})?)\s*</li>",
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    out: list[str] = []
    for value in raw:
        token = _normalize_us_ticker(value)
        if token and re.search(r"[A-Z]", token):
            out.append(token)
    out = _dedupe_sort(out)
    if not out:
        raise ValueError("no SOX tickers parsed from html list fallback")
    return out


def _fetch_us_from_wikipedia(universe_id: str) -> list[str]:
    urls = {
        "sp500": "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
        "nasdaq100": "https://en.wikipedia.org/wiki/Nasdaq-100",
        "dow30": "https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average",
        "sox": "https://en.wikipedia.org/wiki/PHLX_Semiconductor_Sector",
    }
    html = _fetch_html(urls[universe_id])
    raw: list[str] = []
    try:
        tables = pd.read_html(StringIO(html))
        table, symbol_col = _pick_table_with_column(
            tables, ["Symbol", "Ticker", "Ticker symbol"]
        )
        raw = _extract_col_values(table, symbol_col)
    except ValueError:
        if universe_id == "sox":
            return _extract_sox_from_html_list(html)
        raise

    out: list[str] = []
    for value in raw:
        token = _normalize_us_ticker(value)
        if not token:
            continue
        if len(token) > 8:
            continue
        if not re.search(r"[A-Z]", token):
            continue
        out.append(token)

    out = _dedupe_sort(out)
    if not out:
        raise ValueError(f"no tickers parsed for {universe_id}")
    return out


def _fetch_russell1000_from_ishares() -> list[dict[str, str]]:
    content = _fetch_html(RUSSELL1000_ISHARES_CSV_URL, timeout_sec=30)
    lines = content.splitlines()
    header_index = -1
    for idx, line in enumerate(lines):
        normalized = line.lstrip("\ufeff").strip().lower()
        if normalized.startswith("ticker,"):
            header_index = idx
            break
    if header_index < 0:
        raise ValueError("could not find ticker header in iShares Russell 1000 csv")

    csv_text = "\n".join(lines[header_index:])
    reader = csv.DictReader(StringIO(csv_text))
    today = date.today().isoformat()
    rows: list[dict[str, str]] = []
    for row in reader:
        raw_ticker = str(row.get("Ticker", "")).strip().strip('"')
        if not raw_ticker:
            continue
        asset_class = str(row.get("Asset Class", "")).strip().strip('"').lower()
        if asset_class and "equity" not in asset_class:
            continue
        symbol = _normalize_us_ticker(raw_ticker)
        if not symbol:
            continue
        name = str(row.get("Name", "")).strip().strip('"')
        sector = str(row.get("Sector", "")).strip().strip('"')
        rows.append(
            {
                "symbol": symbol,
                "name": name,
                "market": "US",
                "sector_l1": sector,
                "category_l2": "us_large_mid_equity",
                "data_asof": today,
                "source": "ishares_iwb",
            }
        )

    deduped = _dedupe_rows_by_symbol(rows)
    if len(deduped) < 900:
        raise ValueError(
            f"unexpected Russell 1000 parse size: {len(deduped)} (expected >= 900)"
        )
    return deduped


def _latest_kr_sector_snapshot(
    stock_module,
    *,
    market: str,
    max_lookback_days: int = 14,
) -> tuple[str | None, pd.DataFrame]:
    for offset in range(max(1, int(max_lookback_days))):
        day = (date.today() - timedelta(days=offset)).strftime("%Y%m%d")
        try:
            frame = stock_module.get_market_sector_classifications(day, market=market)
        except Exception:  # noqa: BLE001
            continue
        if frame is None or getattr(frame, "empty", True):
            continue
        return day, frame.copy()
    return None, pd.DataFrame()


def _fetch_kr_with_pykrx(universe_id: str) -> list[dict[str, str]]:
    try:
        from pykrx import stock  # type: ignore
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(
            "pykrx not installed; install with `pip install pykrx`"
        ) from exc

    if universe_id == "kospi200":
        market = "KOSPI"
        target_names = {"코스피200", "KOSPI200"}
        suffix = ".KS"
        desired_size = 200
        fallback_top_n = 300
    elif universe_id == "kosdaq100":
        market = "KOSDAQ"
        target_names = {"코스닥100", "KOSDAQ100"}
        suffix = ".KQ"
        desired_size = 100
        fallback_top_n = 300
    else:
        raise ValueError(universe_id)

    index_codes = stock.get_index_ticker_list(market=market)
    target_code = None
    for code in index_codes:
        name = str(stock.get_index_ticker_name(code)).strip()
        key = re.sub(r"\s+", "", name).upper()
        if key in target_names:
            target_code = code
            break

    tickers: list[str] = []
    used_fallback = False
    if target_code:
        tickers = [
            str(item) for item in stock.get_index_portfolio_deposit_file(target_code)
        ]
    if not tickers:
        _log(
            f"WARN universe_id: {universe_id} index constituents unavailable; "
            f"using {market} market-cap top {fallback_top_n} fallback"
        )
        used_fallback = True
        tickers = _fallback_kr_market_cap_tickers(
            stock_module=stock,
            market=market,
            top_n=fallback_top_n,
        )

    out: list[str] = []
    seen: set[str] = set()
    for item in tickers:
        symbol = _normalize_kr_code(item, suffix)
        if not symbol or symbol in seen:
            continue
        seen.add(symbol)
        out.append(symbol)
    if used_fallback and len(out) >= desired_size:
        out = out[:desired_size]
    out = sorted(out)
    if used_fallback and len(out) < desired_size:
        raise RuntimeError(
            f"fallback produced insufficient symbols for {universe_id}: {len(out)} < {desired_size}"
        )
    if not out:
        raise RuntimeError(f"empty constituents for {universe_id}")

    taxonomy = _load_kr_taxonomy()
    sector_day, sector_frame = _latest_kr_sector_snapshot(stock, market=market)
    name_col = ""
    sector_col = ""
    sector_lookup: dict[str, Any] = {}
    if not sector_frame.empty:
        columns = [str(column) for column in sector_frame.columns]
        if "종목명" in columns:
            name_col = "종목명"
        elif columns:
            name_col = columns[0]
        if "업종명" in columns:
            sector_col = "업종명"
        elif len(columns) >= 2:
            sector_col = columns[1]
        for ticker, row in sector_frame.iterrows():
            ticker_key = re.sub(r"[^0-9]", "", str(ticker)).zfill(6)
            if ticker_key:
                sector_lookup[ticker_key] = row

    if sector_day:
        data_asof = f"{sector_day[0:4]}-{sector_day[4:6]}-{sector_day[6:8]}"
    else:
        data_asof = date.today().isoformat()

    rows: list[dict[str, str]] = []
    for symbol in out:
        code = re.sub(r"[^0-9]", "", symbol.split(".", 1)[0]).zfill(6)
        name = ""
        sector_l1 = ""
        row = sector_lookup.get(code)
        if row is not None:
            if name_col:
                name = str(row.get(name_col, "")).strip()
            if sector_col:
                sector_l1 = str(row.get(sector_col, "")).strip()
        category_l2 = _classify_kr_category_l2(
            symbol=symbol,
            name=name,
            sector_l1=sector_l1,
            taxonomy=taxonomy,
        )
        rows.append(
            {
                "symbol": symbol,
                "name": name,
                "market": market,
                "sector_l1": sector_l1,
                "category_l2": category_l2,
                "data_asof": data_asof,
                "source": "pykrx",
            }
        )
    return _dedupe_rows_by_symbol(rows)


def _fallback_kr_market_cap_tickers(
    stock_module,
    *,
    market: str,
    top_n: int,
    max_lookback_days: int = 14,
) -> list[str]:
    for offset in range(max(1, int(max_lookback_days))):
        day = (date.today() - timedelta(days=offset)).strftime("%Y%m%d")
        try:
            frame = stock_module.get_market_cap_by_ticker(day, market=market)
        except Exception:  # noqa: BLE001
            continue
        if frame is None or getattr(frame, "empty", True):
            continue
        cap_col = "시가총액" if "시가총액" in frame.columns else str(frame.columns[0])
        ordered = frame.sort_values(by=cap_col, ascending=False)
        tickers = [str(item) for item in ordered.index.tolist()]
        if tickers:
            return tickers[: max(1, int(top_n))]
    raise RuntimeError(f"market-cap fallback failed: market={market}, top_n={top_n}")


def _validate_with_yfinance(
    symbols: list[str], *, max_workers: int = 6
) -> tuple[list[str], list[str], str]:
    try:
        import yfinance as yf  # type: ignore
    except Exception:
        return symbols, [], "yfinance not installed; validation skipped"

    def _check(symbol: str) -> tuple[str, bool]:
        try:
            frame = yf.download(
                symbol,
                period="7d",
                interval="1d",
                progress=False,
                auto_adjust=False,
                threads=False,
            )
            ok = frame is not None and getattr(frame, "empty", True) is False
            return symbol, bool(ok)
        except Exception:
            return symbol, False

    valid: list[str] = []
    invalid: list[str] = []
    with ThreadPoolExecutor(max_workers=max(1, int(max_workers))) as pool:
        futures = [pool.submit(_check, symbol) for symbol in symbols]
        for future in as_completed(futures):
            symbol, ok = future.result()
            if ok:
                valid.append(symbol)
            else:
                invalid.append(symbol)

    return _dedupe_sort(valid), _dedupe_sort(invalid), "ok"


def _refresh_one(
    universe_id: str,
    outdir: Path,
    *,
    validate: bool,
    max_workers: int,
    dry_run: bool,
) -> RefreshResult:
    try:
        if universe_id in ("sp500", "nasdaq100", "sox", "dow30"):
            fetched_rows = _symbol_only_rows(_fetch_us_from_wikipedia(universe_id))
        elif universe_id in ("kospi200", "kosdaq100"):
            fetched_rows = _fetch_kr_with_pykrx(universe_id)
        elif universe_id == "russell1000":
            fetched_rows = _fetch_russell1000_from_ishares()
        elif universe_id == "all_in_one":
            fetched_rows = _build_all_in_one_rows(outdir)
        else:
            return RefreshResult(universe_id, False, 0, 0, 0, 0, "unknown universe id")

        normalized_rows = _dedupe_rows_by_symbol(fetched_rows)
        valid_rows = list(normalized_rows)
        invalid_symbols: list[str] = []
        invalid_rows: list[dict[str, str]] = []
        validate_msg = "skipped"
        effective_validate = bool(validate) and universe_id != "all_in_one"
        if effective_validate and normalized_rows:
            symbols_to_validate = [
                row["symbol"] for row in normalized_rows if row.get("symbol")
            ]
            valid_symbols, invalid_symbols, validate_msg = _validate_with_yfinance(
                symbols_to_validate, max_workers=max_workers
            )
            valid_set = set(valid_symbols)
            invalid_set = set(invalid_symbols)
            valid_rows = [
                row for row in normalized_rows if row.get("symbol") in valid_set
            ]
            invalid_rows = [
                row for row in normalized_rows if row.get("symbol") in invalid_set
            ]

        if validate and universe_id == "all_in_one":
            validate_msg = "skipped (aggregate universe)"

        minimum_required = int(get_universe_minimum_required(universe_id))
        actual_count = len(valid_rows)
        if minimum_required > 0 and actual_count < minimum_required:
            return RefreshResult(
                universe_id,
                False,
                len(fetched_rows),
                len(normalized_rows),
                actual_count,
                len(invalid_symbols),
                (
                    f"undersized_refresh_result: actual_count={actual_count}; "
                    f"minimum_required={minimum_required}; "
                    "existing_file_preserved; "
                    f"validate={validate_msg}"
                ),
            )

        if dry_run:
            return RefreshResult(
                universe_id,
                True,
                len(fetched_rows),
                len(normalized_rows),
                len(valid_rows),
                len(invalid_symbols),
                f"dry-run; validate={validate_msg}",
            )

        target = outdir / f"{universe_id}.csv"
        invalid_path = outdir / f"_invalid_{universe_id}.csv"
        _atomic_write_rows_csv(
            target,
            valid_rows,
            fieldnames=_universe_rows_fieldnames(valid_rows),
        )
        if invalid_symbols:
            if invalid_rows:
                _atomic_write_rows_csv(
                    invalid_path,
                    invalid_rows,
                    fieldnames=_universe_rows_fieldnames(invalid_rows),
                )
            else:
                _atomic_write_csv(invalid_path, invalid_symbols)
        else:
            try:
                if invalid_path.exists():
                    invalid_path.unlink()
            except OSError:
                pass

        return RefreshResult(
            universe_id,
            True,
            len(fetched_rows),
            len(normalized_rows),
            len(valid_rows),
            len(invalid_symbols),
            f"ok; validate={validate_msg}",
        )
    except Exception as exc:  # noqa: BLE001
        return RefreshResult(universe_id, False, 0, 0, 0, 0, f"failed: {exc}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Refresh universe constituent CSVs (atomic, local-first)."
    )
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--only", nargs="*", default=None)
    parser.add_argument("--outdir", type=str, default="")
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--no-validate", action="store_true")
    parser.add_argument("--max-workers", type=int, default=6)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    validate = bool(args.validate)
    if args.no_validate:
        validate = False

    if args.all:
        targets = list(UNIVERSE_IDS_ALL)
    elif args.only:
        targets = [str(item).strip() for item in args.only if str(item).strip()]
    else:
        _log("no target specified: use --all or --only <ids...>")
        return 2

    outdir = (
        Path(args.outdir).expanduser().resolve()
        if args.outdir
        else Path(UNIVERSE_INPUT_DIR)
    )
    outdir.mkdir(parents=True, exist_ok=True)

    _log(f"time: {_utc_now()}")
    _log(f"outdir: {outdir}")
    _log(f"validate: {validate}")
    _log(f"dry_run: {bool(args.dry_run)}")

    results: list[RefreshResult] = []
    for universe_id in targets:
        result = _refresh_one(
            universe_id,
            outdir,
            validate=validate,
            max_workers=int(args.max_workers),
            dry_run=bool(args.dry_run),
        )
        results.append(result)
        status = "OK" if result.ok else "FAIL"
        _log(
            f"{status} universe_id: {universe_id} fetched: {result.fetched} "
            f"normalized: {result.normalized} valid: {result.valid} "
            f"invalid: {result.invalid} message: {result.message}"
        )

    failed = [result.universe_id for result in results if not result.ok]
    if failed:
        _log(f"failed_universes: {', '.join(failed)}")
        return 1

    _log("all requested universes refreshed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
