#!/usr/bin/env python3
"""
Update exchange data from ISO 10383 (Market Identifier Codes).

Downloads the official ISO 10383 MIC registry and regenerates exchange_data.json.
Uses only Python standard library (no external dependencies).

Source:
    https://www.iso20022.org/market-identifier-codes

Usage:
    python openbb_platform/core/openbb_core/provider/utils/update_exchange_data.py
    python openbb_platform/core/openbb_core/provider/utils/update_exchange_data.py --operating-only
"""

import argparse
import csv
import io
import json
import logging
import sys
import urllib.request
from datetime import date
from pathlib import Path

logger = logging.getLogger(__name__)

SCRIPT_DIR = Path(__file__).parent
OUTPUT_PATH = SCRIPT_DIR / "exchange_data.json"
MIC_CSV_URL = (
    "https://www.iso20022.org/sites/default/files/ISO10383_MIC/ISO10383_MIC.csv"
)


def download_mic_csv() -> list[dict]:
    """Download and parse the official ISO 10383 MIC CSV."""
    logger.info("Downloading MIC data from %s...", MIC_CSV_URL)

    req = urllib.request.Request(  # noqa: S310
        MIC_CSV_URL, headers={"User-Agent": "OpenBB/1.0"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
        raw = resp.read().decode("utf-8-sig")

    reader = csv.DictReader(io.StringIO(raw))
    rows = list(reader)
    logger.info("Downloaded %d total MIC entries", len(rows))
    return rows


def process_mic_data(rows: list[dict], operating_only: bool = False) -> list[dict]:
    """Filter and transform MIC rows into exchange entries."""
    # Normalize header keys (strip whitespace, uppercase)
    active = [r for r in rows if r.get("STATUS", "").strip().upper() == "ACTIVE"]
    logger.info("Active entries: %d", len(active))

    if operating_only:
        active = [
            r for r in active if r.get("OPRT/SGMT", "").strip().upper() in ("OPRT", "O")
        ]
        logger.info("Operating MICs only: %d", len(active))

    exchanges = []
    for row in active:
        mic = row.get("MIC", "").strip()
        if not mic:
            continue

        name = row.get("MARKET NAME-INSTITUTION DESCRIPTION", "").strip()
        if not name:
            continue

        acronym = row.get("ACRONYM", "").strip() or mic

        entry = {
            "mic": mic,
            "acronym": acronym,
            "name": name,
        }

        city = row.get("CITY", "").strip()
        if city:
            entry["city"] = city.title()

        country_code = row.get("ISO COUNTRY CODE (ISO 3166)", "").strip().upper()
        if country_code:
            entry["country"] = country_code

        website = row.get("WEBSITE", "").strip()
        if website:
            # Normalize: ensure lowercase, add https:// if missing scheme
            website = website.lower()
            if website and not website.startswith(("http://", "https://")):
                website = f"https://{website}"
            entry["website"] = website

        entry["_type"] = row.get("OPRT/SGMT", "").strip().upper()
        exchanges.append(entry)

    # Sort operating MICs before segments so that the lookup in exchange_utils
    # (first-write-wins) gives priority to operating MICs when acronyms collide.
    exchanges.sort(key=lambda x: (0 if x["_type"] in ("OPRT", "O") else 1, x["mic"]))

    # Strip internal sort key before output
    for e in exchanges:
        del e["_type"]
    return exchanges


def build_exchange_data(exchanges: list[dict]) -> dict:
    """Build the final exchange data structure."""
    return {
        "_last_updated": date.today().isoformat(),
        "_source": {
            "url": "https://www.iso20022.org/market-identifier-codes",
            "standard": "ISO 10383",
            "maintainer": "SWIFT (ISO 20022 Registration Authority)",
        },
        "_stats": {
            "total_exchanges": len(exchanges),
        },
        "exchanges": exchanges,
    }


def main():
    """Download ISO 10383 MIC registry and regenerate exchange_data.json."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    parser = argparse.ArgumentParser(description="Update exchange data from ISO 10383")
    parser.add_argument(
        "--operating-only",
        action="store_true",
        help="Exclude segment MICs (only include operating MICs)",
    )
    args = parser.parse_args()

    rows = download_mic_csv()
    exchanges = process_mic_data(rows, operating_only=args.operating_only)

    if not exchanges:
        logger.error("No exchanges found after filtering")
        sys.exit(1)

    data = build_exchange_data(exchanges)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    logger.info("\nWrote %s", OUTPUT_PATH)
    logger.info("   Total exchanges: %d", len(exchanges))


if __name__ == "__main__":
    main()
