"""Warm up raw market data cache without running model training."""

from __future__ import annotations

import argparse
import csv
from datetime import date
from pathlib import Path

from openbb_quant_ml.service.constants import ARTIFACT_ROOT
from openbb_quant_ml.service.data_loader import load_market_data
from openbb_quant_ml.service.macro_catalog import parse_date_input
from openbb_quant_ml.service.storage import save_json, utc_now_iso


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Warm up symbol market-data cache.")
    parser.add_argument("--symbols-file", required=True, help="Path to txt/csv file with symbols")
    parser.add_argument("--start", required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", default="today", help="End date (YYYY-MM-DD or today)")
    return parser.parse_args()


def _load_symbols(path: Path) -> list[str]:
    if not path.exists():
        return []
    suffix = path.suffix.lower()
    symbols: list[str] = []
    seen: set[str] = set()

    if suffix == ".csv":
        with path.open(encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                for item in row:
                    symbol = str(item or "").strip().upper()
                    if symbol and symbol not in seen:
                        seen.add(symbol)
                        symbols.append(symbol)
    else:
        text = path.read_text(encoding="utf-8")
        for item in text.replace(",", "\n").splitlines():
            symbol = str(item or "").strip().upper()
            if symbol and symbol not in seen:
                seen.add(symbol)
                symbols.append(symbol)
    return symbols


def main() -> int:
    args = _parse_args()
    symbols_path = Path(args.symbols_file)
    symbols = _load_symbols(symbols_path)
    if not symbols:
        print("No symbols found.")
        return 1

    start = parse_date_input(args.start)
    end = parse_date_input(args.end) or date.today()
    if start is None:
        print("Invalid start date.")
        return 1

    data, skipped = load_market_data(symbols=symbols, start_date=start, end_date=end)

    report = {
        "timestamp": utc_now_iso(),
        "symbols_file": str(symbols_path),
        "start": start.isoformat(),
        "end": end.isoformat(),
        "symbols_requested": len(symbols),
        "symbols_loaded": len(data),
        "symbols_skipped": skipped,
    }
    report_dir = ARTIFACT_ROOT / "jobs" / "reports"
    report_path = report_dir / f"cache_warmup_{utc_now_iso().replace(':', '').replace('-', '')}.json"
    save_json(report_path, report)
    print(f"Loaded {len(data)} / {len(symbols)} symbols.")
    print(f"Report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

