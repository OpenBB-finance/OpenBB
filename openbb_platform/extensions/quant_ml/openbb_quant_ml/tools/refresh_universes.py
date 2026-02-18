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
from urllib.request import Request, urlopen

import pandas as pd

from openbb_quant_ml.service.universe import get_universe_minimum_required
from openbb_quant_ml.service.universe_builder import UNIVERSE_INPUT_DIR

UNIVERSE_IDS_ALL = ("kospi200", "kosdaq100", "sp500", "nasdaq100", "sox", "dow30")


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


def _atomic_write_csv(path: Path, symbols: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=str(path.parent)
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["symbol"])
            for symbol in symbols:
                writer.writerow([symbol])
            file.flush()
            os.fsync(file.fileno())
        os.replace(tmp_name, path)
    finally:
        try:
            if os.path.exists(tmp_name):
                os.remove(tmp_name)
        except OSError:
            pass


def _sanitize_token(value: str) -> str:
    value = value.strip().upper()
    value = re.sub(r"\s+", "", value)
    value = re.sub(r"[^A-Z0-9.\-_]", "", value)
    return value


def _normalize_us_ticker(raw: str) -> str:
    token = _sanitize_token(raw)
    if re.fullmatch(r"[A-Z]{1,6}\.[A-Z]{1,2}", token):
        token = token.replace(".", "-")
    return token


def _normalize_kr_code(raw: str, suffix: str) -> str:
    code = re.sub(r"[^0-9]", "", str(raw).strip())
    if len(code) != 6:
        return ""
    return f"{code}{suffix}"


def _dedupe_sort(items: Iterable[str]) -> list[str]:
    return sorted({item for item in items if item})


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


def _fetch_kr_with_pykrx(universe_id: str) -> list[str]:
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
        tickers = [str(item) for item in stock.get_index_portfolio_deposit_file(target_code)]
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
    return out


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
    raise RuntimeError(
        f"market-cap fallback failed: market={market}, top_n={top_n}"
    )


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
            fetched = _fetch_us_from_wikipedia(universe_id)
        elif universe_id in ("kospi200", "kosdaq100"):
            fetched = _fetch_kr_with_pykrx(universe_id)
        else:
            return RefreshResult(
                universe_id, False, 0, 0, 0, 0, "unknown universe id"
            )

        normalized = _dedupe_sort(fetched)
        valid_symbols = normalized
        invalid_symbols: list[str] = []
        validate_msg = "skipped"
        if validate and normalized:
            valid_symbols, invalid_symbols, validate_msg = _validate_with_yfinance(
                normalized, max_workers=max_workers
            )

        minimum_required = int(get_universe_minimum_required(universe_id))
        actual_count = len(valid_symbols)
        if minimum_required > 0 and actual_count < minimum_required:
            return RefreshResult(
                universe_id,
                False,
                len(fetched),
                len(normalized),
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
                len(fetched),
                len(normalized),
                len(valid_symbols),
                len(invalid_symbols),
                f"dry-run; validate={validate_msg}",
            )

        target = outdir / f"{universe_id}.csv"
        invalid_path = outdir / f"_invalid_{universe_id}.csv"
        _atomic_write_csv(target, valid_symbols)
        if invalid_symbols:
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
            len(fetched),
            len(normalized),
            len(valid_symbols),
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
