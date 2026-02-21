"""Security master helpers for staged universe filtering."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pandas as pd

from openbb_quant_ml.service.constants import ARTIFACT_ROOT
from openbb_quant_ml.service.universe import get_symbol_metadata_map

SECURITY_MASTER_COLUMNS: tuple[str, ...] = (
    "symbol",
    "company_id",
    "security_type",
    "exchange",
    "country",
    "sector_l1",
    "free_float_ratio",
    "float_mcap_usd",
    "ipo_trading_days",
    "trading_halt_days",
    "management_flag",
    "delisting_pending_flag",
    "special_status_flag",
    "hard_to_borrow_flag",
)

REFERENCE_DIR = ARTIFACT_ROOT / "reference"
REFERENCE_SECURITY_MASTER_PATH = REFERENCE_DIR / "security_master.parquet"
REFERENCE_TRADING_STATUS_PATH = REFERENCE_DIR / "trading_status.parquet"
REFERENCE_BORROW_STATUS_PATH = REFERENCE_DIR / "borrow_status.parquet"


def _normalize_symbol(symbol: Any) -> str:
    return str(symbol or "").strip().upper()


def _infer_exchange(symbol: str, market: str | None) -> str:
    token = _normalize_symbol(symbol)
    market_key = str(market or "").strip().upper()
    if token.endswith(".KS") or market_key == "KOSPI":
        return "KOSPI"
    if token.endswith(".KQ") or market_key == "KOSDAQ":
        return "KOSDAQ"
    return "NYSE"


def _infer_country(symbol: str, market: str | None) -> str:
    token = _normalize_symbol(symbol)
    market_key = str(market or "").strip().upper()
    if token.endswith(".KS") or token.endswith(".KQ") or market_key in {"KOSPI", "KOSDAQ"}:
        return "KR"
    return "US"


def _infer_security_type(symbol: str, category: str | None) -> str:
    token = _normalize_symbol(symbol)
    category_key = str(category or "").strip().lower()
    if "etf" in category_key:
        return "etf"
    if token.startswith("^"):
        return "index"
    return "common_stock"


def _company_id(symbol: str) -> str:
    token = _normalize_symbol(symbol)
    token = token.split(".")[0]
    token = re.sub(r"[-.][A-Z]$", "", token)
    return token or _normalize_symbol(symbol)


def _coerce_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value or "").strip().lower()
    if text in {"1", "true", "y", "yes"}:
        return True
    if text in {"0", "false", "n", "no"}:
        return False
    return default


def _read_reference_table(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        frame = pd.read_parquet(path)
    except Exception:  # noqa: BLE001
        return pd.DataFrame()
    if frame.empty:
        return frame
    if "symbol" not in frame.columns:
        return pd.DataFrame()
    frame["symbol"] = frame["symbol"].map(_normalize_symbol)
    return frame


def _apply_status_overrides(frame: pd.DataFrame, run_dir: Path | None) -> pd.DataFrame:
    trading_candidates = [
        run_dir / "trading_status.parquet" if run_dir is not None else None,
        REFERENCE_TRADING_STATUS_PATH,
    ]
    borrow_candidates = [
        run_dir / "borrow_status.parquet" if run_dir is not None else None,
        REFERENCE_BORROW_STATUS_PATH,
    ]

    out = frame.copy()
    for candidate in trading_candidates:
        if candidate is None:
            continue
        status = _read_reference_table(candidate)
        if status.empty:
            continue
        keep = [
            col
            for col in (
                "symbol",
                "trading_halt_days",
                "management_flag",
                "delisting_pending_flag",
                "special_status_flag",
            )
            if col in status.columns
        ]
        out = out.merge(status[keep], on="symbol", how="left", suffixes=("", "_st"))
        for col in (
            "trading_halt_days",
            "management_flag",
            "delisting_pending_flag",
            "special_status_flag",
        ):
            st_col = f"{col}_st"
            if st_col in out.columns:
                out[col] = out[st_col].combine_first(out[col])
                out = out.drop(columns=[st_col])
        break

    for candidate in borrow_candidates:
        if candidate is None:
            continue
        borrow = _read_reference_table(candidate)
        if borrow.empty:
            continue
        keep = [col for col in ("symbol", "hard_to_borrow_flag") if col in borrow.columns]
        out = out.merge(borrow[keep], on="symbol", how="left", suffixes=("", "_br"))
        if "hard_to_borrow_flag_br" in out.columns:
            out["hard_to_borrow_flag"] = out["hard_to_borrow_flag_br"].combine_first(
                out["hard_to_borrow_flag"]
            )
            out = out.drop(columns=["hard_to_borrow_flag_br"])
        break
    return out


def load_security_master(symbols: list[str], run_dir: Path | None = None) -> pd.DataFrame:
    """Load or infer security master rows for provided symbols."""
    normalized = sorted({_normalize_symbol(symbol) for symbol in symbols if _normalize_symbol(symbol)})
    metadata = get_symbol_metadata_map()
    fallback_rows: list[dict[str, Any]] = []
    for symbol in normalized:
        meta = metadata.get(symbol, {})
        category = str(meta.get("category_l2") or meta.get("category") or "").strip()
        market = str(meta.get("market", "")).strip()
        fallback_rows.append(
            {
                "symbol": symbol,
                "company_id": str(meta.get("company_id") or _company_id(symbol)),
                "security_type": _infer_security_type(symbol, category),
                "exchange": _infer_exchange(symbol, market),
                "country": _infer_country(symbol, market),
                "sector_l1": str(meta.get("sector_l1") or "other"),
                "free_float_ratio": float(meta.get("free_float_ratio") or 1.0),
                "float_mcap_usd": float(meta.get("float_mcap_usd") or 2_000_000_000.0),
                "ipo_trading_days": int(meta.get("ipo_trading_days") or 3650),
                "trading_halt_days": int(meta.get("trading_halt_days") or 0),
                "management_flag": _coerce_bool(meta.get("management_flag"), default=False),
                "delisting_pending_flag": _coerce_bool(
                    meta.get("delisting_pending_flag"), default=False
                ),
                "special_status_flag": _coerce_bool(meta.get("special_status_flag"), default=False),
                "hard_to_borrow_flag": _coerce_bool(meta.get("hard_to_borrow_flag"), default=False),
            }
        )
    master = pd.DataFrame(fallback_rows)

    candidates: list[Path] = []
    if run_dir is not None:
        candidates.append(run_dir / "security_master.parquet")
    candidates.append(REFERENCE_SECURITY_MASTER_PATH)
    for candidate in candidates:
        ref = _read_reference_table(candidate)
        if ref.empty:
            continue
        ref = ref.copy()
        ref = ref[ref["symbol"].isin(normalized)]
        if ref.empty:
            continue
        merged = master.merge(ref, on="symbol", how="left", suffixes=("", "_ref"))
        for col in SECURITY_MASTER_COLUMNS:
            if col == "symbol":
                continue
            ref_col = f"{col}_ref"
            if ref_col in merged.columns:
                merged[col] = merged[ref_col].combine_first(merged[col])
                merged = merged.drop(columns=[ref_col])
        master = merged
        break

    master = _apply_status_overrides(master, run_dir=run_dir)

    # Final normalize.
    master["symbol"] = master["symbol"].map(_normalize_symbol)
    master["company_id"] = master["company_id"].fillna(master["symbol"]).astype(str)
    master["security_type"] = master["security_type"].fillna("common_stock").astype(str).str.lower()
    master["exchange"] = master["exchange"].fillna("NYSE").astype(str).str.upper()
    master["country"] = master["country"].fillna("US").astype(str).str.upper()
    master["sector_l1"] = master["sector_l1"].fillna("other").astype(str)

    for col, default in (
        ("free_float_ratio", 1.0),
        ("float_mcap_usd", 2_000_000_000.0),
        ("ipo_trading_days", 3650),
        ("trading_halt_days", 0),
    ):
        master[col] = pd.to_numeric(master[col], errors="coerce").fillna(default)
    for col in (
        "management_flag",
        "delisting_pending_flag",
        "special_status_flag",
        "hard_to_borrow_flag",
    ):
        master[col] = master[col].map(_coerce_bool)

    return master[list(SECURITY_MASTER_COLUMNS)].drop_duplicates(subset=["symbol"], keep="last")
