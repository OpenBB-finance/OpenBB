#!/usr/bin/env python3
"""
CLI entry point for updating OpenBB taxonomy reference data.

Refreshes exchange_data.json (ISO 10383) and/or country_data.json
(membership groups) from authoritative sources.

Usage:
    openbb-update              # update all taxonomy data
    openbb-update exchanges    # update exchange data only
    openbb-update countries    # update country data only
    openbb-update --dry-run    # show what would change without writing

This ships as a console_script so it works both locally and in CI.
No external dependencies — uses only the Python standard library.
"""

import argparse
import csv
import io
import json
import sys
import urllib.request
from datetime import date
from pathlib import Path

UTILS_DIR = Path(__file__).parent
EXCHANGE_OUTPUT = UTILS_DIR / "exchange_data.json"
COUNTRY_OUTPUT = UTILS_DIR / "country_data.json"

MIC_CSV_URL = (
    "https://www.iso20022.org/sites/default/files/ISO10383_MIC/ISO10383_MIC.csv"
)

# ---------------------------------------------------------------------------
# Country membership data (authoritative sources)
# Last verified: 2025-02-13
#
# To update: edit the member lists below, update ``last_updated``, then run
# ``openbb-update countries`` to regenerate country_data.json.
# ---------------------------------------------------------------------------

MEMBERSHIPS = {
    "G7": {
        "source": "https://en.wikipedia.org/wiki/G7",
        "last_updated": "2025-02-13",
        "members": [
            "CA",  # Canada
            "FR",  # France
            "DE",  # Germany
            "IT",  # Italy
            "JP",  # Japan
            "GB",  # United Kingdom
            "US",  # United States
        ],
    },
    "G20": {
        "source": "https://en.wikipedia.org/wiki/G20",
        "last_updated": "2025-02-13",
        "notes": "EU is a member but not a country; African Union joined 2023",
        "members": [
            "AR",  # Argentina
            "AU",  # Australia
            "BR",  # Brazil
            "CA",  # Canada
            "CN",  # China
            "FR",  # France
            "DE",  # Germany
            "IN",  # India
            "ID",  # Indonesia
            "IT",  # Italy
            "JP",  # Japan
            "MX",  # Mexico
            "RU",  # Russia
            "SA",  # Saudi Arabia
            "ZA",  # South Africa
            "KR",  # South Korea
            "TR",  # Turkey (Turkiye)
            "GB",  # United Kingdom
            "US",  # United States
        ],
    },
    "EU": {
        "source": "https://en.wikipedia.org/wiki/Member_state_of_the_European_Union",
        "last_updated": "2025-02-13",
        "members": [
            "AT",  # Austria
            "BE",  # Belgium
            "BG",  # Bulgaria
            "HR",  # Croatia
            "CY",  # Cyprus
            "CZ",  # Czechia
            "DK",  # Denmark
            "EE",  # Estonia
            "FI",  # Finland
            "FR",  # France
            "DE",  # Germany
            "GR",  # Greece
            "HU",  # Hungary
            "IE",  # Ireland
            "IT",  # Italy
            "LV",  # Latvia
            "LT",  # Lithuania
            "LU",  # Luxembourg
            "MT",  # Malta
            "NL",  # Netherlands
            "PL",  # Poland
            "PT",  # Portugal
            "RO",  # Romania
            "SK",  # Slovakia
            "SI",  # Slovenia
            "ES",  # Spain
            "SE",  # Sweden
        ],
    },
    "NATO": {
        "source": "https://www.nato.int/cps/en/natohq/nato_countries.htm",
        "last_updated": "2025-02-13",
        "notes": "Sweden joined March 7, 2024; Finland joined April 4, 2023",
        "members": [
            "AL",  # Albania
            "BE",  # Belgium
            "BG",  # Bulgaria
            "CA",  # Canada
            "HR",  # Croatia
            "CZ",  # Czechia
            "DK",  # Denmark
            "EE",  # Estonia
            "FI",  # Finland (2023)
            "FR",  # France
            "DE",  # Germany
            "GR",  # Greece
            "HU",  # Hungary
            "IS",  # Iceland
            "IT",  # Italy
            "LV",  # Latvia
            "LT",  # Lithuania
            "LU",  # Luxembourg
            "ME",  # Montenegro
            "NL",  # Netherlands
            "MK",  # North Macedonia
            "NO",  # Norway
            "PL",  # Poland
            "PT",  # Portugal
            "RO",  # Romania
            "SK",  # Slovakia
            "SI",  # Slovenia
            "ES",  # Spain
            "SE",  # Sweden (2024)
            "TR",  # Turkey (Turkiye)
            "GB",  # United Kingdom
            "US",  # United States
        ],
    },
    "OECD": {
        "source": "https://www.oecd.org/about/document/ratification-oecd-convention.htm",
        "last_updated": "2025-02-13",
        "members": [
            "AU",  # Australia
            "AT",  # Austria
            "BE",  # Belgium
            "CA",  # Canada
            "CL",  # Chile
            "CO",  # Colombia
            "CR",  # Costa Rica
            "CZ",  # Czechia
            "DK",  # Denmark
            "EE",  # Estonia
            "FI",  # Finland
            "FR",  # France
            "DE",  # Germany
            "GR",  # Greece
            "HU",  # Hungary
            "IS",  # Iceland
            "IE",  # Ireland
            "IL",  # Israel
            "IT",  # Italy
            "JP",  # Japan
            "KR",  # South Korea
            "LV",  # Latvia
            "LT",  # Lithuania
            "LU",  # Luxembourg
            "MX",  # Mexico
            "NL",  # Netherlands
            "NZ",  # New Zealand
            "NO",  # Norway
            "PL",  # Poland
            "PT",  # Portugal
            "SK",  # Slovakia
            "SI",  # Slovenia
            "ES",  # Spain
            "SE",  # Sweden
            "CH",  # Switzerland
            "TR",  # Turkey (Turkiye)
            "GB",  # United Kingdom
            "US",  # United States
        ],
    },
    "OPEC": {
        "source": "https://www.opec.org/opec_web/en/about_us/25.htm",
        "last_updated": "2025-02-13",
        "members": [
            "DZ",  # Algeria
            "AO",  # Angola
            "CG",  # Congo
            "GQ",  # Equatorial Guinea
            "GA",  # Gabon
            "IR",  # Iran
            "IQ",  # Iraq
            "KW",  # Kuwait
            "LY",  # Libya
            "NG",  # Nigeria
            "SA",  # Saudi Arabia
            "AE",  # United Arab Emirates
            "VE",  # Venezuela
        ],
    },
    "BRICS": {
        "source": "https://en.wikipedia.org/wiki/BRICS",
        "last_updated": "2025-02-13",
        "notes": (
            "Expanded Jan 1, 2024 (Egypt, Ethiopia, Iran, UAE); Indonesia joined Jan 6, 2025"
        ),
        "members": [
            "BR",  # Brazil
            "RU",  # Russia
            "IN",  # India
            "CN",  # China
            "ZA",  # South Africa
            "EG",  # Egypt (2024)
            "ET",  # Ethiopia (2024)
            "IR",  # Iran (2024)
            "AE",  # UAE (2024)
            "ID",  # Indonesia (2025)
        ],
    },
}


# ---------------------------------------------------------------------------
# Exchange data (ISO 10383)
# ---------------------------------------------------------------------------


def _download_mic_csv() -> list[dict]:
    """Download and parse the official ISO 10383 MIC CSV."""
    print(f"Downloading MIC data from {MIC_CSV_URL}...")
    req = urllib.request.Request(MIC_CSV_URL, headers={"User-Agent": "OpenBB/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
        raw = resp.read().decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(raw))
    rows = list(reader)
    print(f"  Downloaded {len(rows)} total MIC entries")
    return rows


def _process_mic_data(rows: list[dict]) -> list[dict]:
    """Filter and transform MIC rows into exchange entries."""
    active = [r for r in rows if r.get("STATUS", "").strip().upper() == "ACTIVE"]
    print(f"  Active entries: {len(active)}")

    exchanges = []
    for row in active:
        mic = row.get("MIC", "").strip()
        name = row.get("MARKET NAME-INSTITUTION DESCRIPTION", "").strip()
        if not mic or not name:
            continue

        acronym = row.get("ACRONYM", "").strip() or mic
        entry: dict = {"mic": mic, "acronym": acronym, "name": name}

        city = row.get("CITY", "").strip()
        if city:
            entry["city"] = city.title()

        country_code = row.get("ISO COUNTRY CODE (ISO 3166)", "").strip().upper()
        if country_code:
            entry["country"] = country_code

        website = row.get("WEBSITE", "").strip()
        if website:
            website = website.lower()
            if not website.startswith(("http://", "https://")):
                website = f"https://{website}"
            entry["website"] = website

        entry["_type"] = row.get("OPRT/SGMT", "").strip().upper()
        exchanges.append(entry)

    # Operating MICs first (lookup priority), then alphabetical by MIC
    exchanges.sort(key=lambda x: (0 if x["_type"] in ("OPRT", "O") else 1, x["mic"]))
    for e in exchanges:
        del e["_type"]
    return exchanges


def update_exchanges(*, dry_run: bool = False) -> bool | None:
    """Update exchange_data.json from ISO 10383.

    Returns True if data changed, False if up-to-date, None on error.
    """
    print("\n--- Updating exchange data (ISO 10383) ---")
    rows = _download_mic_csv()
    exchanges = _process_mic_data(rows)

    if not exchanges:
        print("Error: No exchanges found after filtering")
        return None

    data = {
        "_last_updated": date.today().isoformat(),
        "_source": {
            "url": "https://www.iso20022.org/market-identifier-codes",
            "standard": "ISO 10383",
            "maintainer": "SWIFT (ISO 20022 Registration Authority)",
        },
        "_stats": {"total_exchanges": len(exchanges)},
        "exchanges": exchanges,
    }

    new_json = json.dumps(data, indent=2, ensure_ascii=False) + "\n"

    changed = True
    if EXCHANGE_OUTPUT.exists():
        old_json = EXCHANGE_OUTPUT.read_text(encoding="utf-8")
        changed = old_json != new_json

    if dry_run:
        status = "CHANGED" if changed else "unchanged"
        print(f"  [{status}] {EXCHANGE_OUTPUT} ({len(exchanges)} exchanges)")
    elif changed:
        EXCHANGE_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        EXCHANGE_OUTPUT.write_text(new_json, encoding="utf-8")
        print(f"  Wrote {EXCHANGE_OUTPUT} ({len(exchanges)} exchanges)")
    else:
        print(f"  No changes to {EXCHANGE_OUTPUT}")

    return changed


# ---------------------------------------------------------------------------
# Country data (membership groups overlay on existing country_data.json)
# ---------------------------------------------------------------------------


def _load_existing_countries() -> list[dict]:
    """Load the base country list from the existing country_data.json.

    The file ships with openbb-core and contains all 249 ISO 3166 countries.
    We use it as the base rather than requiring an external package.
    """
    if not COUNTRY_OUTPUT.exists():
        print(f"Error: {COUNTRY_OUTPUT} not found.")
        print("The base country_data.json must exist (ships with openbb-core).")
        return []

    try:
        with open(COUNTRY_OUTPUT, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"Error: {COUNTRY_OUTPUT} contains invalid JSON: {exc}")
        return []

    countries = data.get("countries", [])
    if not countries:
        print(f"Error: No countries found in {COUNTRY_OUTPUT}")
        return []

    return countries


def _validate_memberships(valid_codes: set[str]) -> list[str]:
    """Validate that all membership country codes exist in the base data."""
    errors = []
    for group_name, group_data in MEMBERSHIPS.items():
        for code in group_data["members"]:
            if code not in valid_codes:
                errors.append(f"{group_name}: Unknown country code '{code}'")
    return errors


def update_countries(*, dry_run: bool = False) -> bool | None:
    """Update country_data.json with current membership groups.

    Reads the existing country_data.json as the base (all 249 ISO 3166
    countries), strips old group assignments, and reapplies from the
    MEMBERSHIPS dict. No external dependencies required.

    Returns True if data changed, False if up-to-date, None on error.
    """
    print("\n--- Updating country data (membership groups) ---")

    base_countries = _load_existing_countries()
    if not base_countries:
        return None

    valid_codes = {c["alpha_2"] for c in base_countries}

    errors = _validate_memberships(valid_codes)
    if errors:
        print("Validation errors:")
        for error in errors:
            print(f"  - {error}")
        return None

    # Strip existing groups and reapply from MEMBERSHIPS
    countries = []
    for country in base_countries:
        entry = {
            "alpha_2": country["alpha_2"],
            "alpha_3": country["alpha_3"],
            "name": country["name"],
            "numeric": country["numeric"],
        }
        groups = sorted(
            g for g, d in MEMBERSHIPS.items() if country["alpha_2"] in d["members"]
        )
        if groups:
            entry["groups"] = groups
        countries.append(entry)

    countries.sort(key=lambda x: x["alpha_2"])

    data = {
        "_last_updated": date.today().isoformat(),
        "_sources": {
            group: {
                "url": gdata["source"],
                "last_verified": gdata["last_updated"],
                **({"notes": gdata["notes"]} if "notes" in gdata else {}),
            }
            for group, gdata in MEMBERSHIPS.items()
        },
        "countries": countries,
    }

    new_json = json.dumps(data, indent=2, ensure_ascii=False) + "\n"

    changed = True
    old_json = COUNTRY_OUTPUT.read_text(encoding="utf-8")
    changed = old_json != new_json

    countries_with_groups = sum(1 for c in countries if "groups" in c)

    if dry_run:
        status = "CHANGED" if changed else "unchanged"
        print(f"  [{status}] {COUNTRY_OUTPUT}")
        print(f"  {len(countries)} countries, {countries_with_groups} with memberships")
    elif changed:
        COUNTRY_OUTPUT.write_text(new_json, encoding="utf-8")
        print(f"  Wrote {COUNTRY_OUTPUT}")
        print(f"  {len(countries)} countries, {countries_with_groups} with memberships")
    else:
        print(f"  No changes to {COUNTRY_OUTPUT}")

    print("\n  Membership counts:")
    for group_name, group_data in MEMBERSHIPS.items():
        print(f"    {group_name}: {len(group_data['members'])} members")

    return changed


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    """Update OpenBB taxonomy reference data from authoritative sources.

    Registered as the ``openbb-update`` console_script in openbb-core.
    Can also be invoked directly::

        python -m openbb_core.provider.utils.update_taxonomy [target] [--dry-run]
    """
    parser = argparse.ArgumentParser(
        prog="openbb-update",
        description=(
            "Refresh OpenBB taxonomy reference data (exchange MICs and country "
            "membership groups) from authoritative upstream sources."
        ),
        epilog=(
            "examples:\n"
            "  openbb-update                 update all taxonomy data\n"
            "  openbb-update exchanges       update ISO 10383 exchange data only\n"
            "  openbb-update countries       update country memberships only\n"
            "  openbb-update --dry-run       preview changes without writing\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "target",
        nargs="?",
        choices=["exchanges", "countries", "all"],
        default="all",
        help="which data to update (default: all)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="show what would change without writing files",
    )
    args = parser.parse_args()

    if args.dry_run:
        print("[DRY RUN] No files will be modified.\n")

    changed = False
    failed = False

    if args.target in ("all", "exchanges"):
        result = update_exchanges(dry_run=args.dry_run)
        if result is None:
            failed = True
        else:
            changed |= result

    if args.target in ("all", "countries"):
        result = update_countries(dry_run=args.dry_run)
        if result is None:
            failed = True
        else:
            changed |= result

    if failed:
        sys.exit(1)
    elif args.dry_run:
        print("\n[DRY RUN] Complete. Re-run without --dry-run to apply changes.")
    elif changed:
        print("\nDone. Review changes with: git diff")
    else:
        print("\nNo changes detected. Data is up to date.")


if __name__ == "__main__":
    main()
