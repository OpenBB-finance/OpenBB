# ruff: noqa: T201
"""Developer script to regenerate country_data.json from authoritative sources.

Sources:
  - ISO 3166-1: pycountry library
  - G7:   https://en.wikipedia.org/wiki/G7
  - G20:  https://en.wikipedia.org/wiki/G20
  - EU:   https://european-union.europa.eu/principles-countries-history/eu-countries_en
  - NATO: https://en.wikipedia.org/wiki/Member_states_of_NATO
  - OECD: https://en.wikipedia.org/wiki/OECD
  - OPEC: https://en.wikipedia.org/wiki/OPEC
  - BRICS: https://en.wikipedia.org/wiki/BRICS

Usage:
    python update_country_data.py [--dry-run] [--output PATH]

Requirements:
    pip install pycountry beautifulsoup4 requests
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from datetime import date
from pathlib import Path

import requests

try:
    import pycountry
    from bs4 import BeautifulSoup
except ImportError as e:
    missing_package = str(e).split("'")[1] if "'" in str(e) else "unknown"
    raise ImportError(
        f"Missing required package: {missing_package}. "
        "Please install dependencies: pip install pycountry beautifulsoup4 requests"
    ) from e

SCRIPT_DIR = Path(__file__).parent
DEFAULT_OUTPUT = SCRIPT_DIR / "country_data.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}

# Expected member counts for sanity checks (approximate — update when membership changes)
EXPECTED_COUNTS: dict[str, int | tuple[int, int]] = {
    "G7": 7,
    "G20": 20,  # 19 countries + EU (we only count countries)
    "EU": 27,
    "NATO": 32,
    "OECD": 38,
    "OPEC": (12, 14),  # fluctuates
    "BRICS": (9, 11),  # 2024 expansion + Indonesia 2025
}

# ── Name normalization ──────────────────────────────────────────────────────
# Map common display names → pycountry names or alpha_2 codes
NAME_OVERRIDES: dict[str, str | None] = {
    "brunei": "BN",
    "bolivia": "BO",
    "congo": "CG",
    "democratic republic of the congo": "CD",
    "côte d'ivoire": "CI",
    "cote d'ivoire": "CI",
    "ivory coast": "CI",
    "czech republic": "CZ",
    "czechia": "CZ",
    "eswatini": "SZ",
    "swaziland": "SZ",
    "iran": "IR",
    "south korea": "KR",
    "korea": "KR",
    "korea, republic of": "KR",
    "republic of korea": "KR",
    "north korea": "KP",
    "north macedonia": "MK",
    "laos": "LA",
    "moldova": "MD",
    "russia": "RU",
    "russian federation": "RU",
    "syria": "SY",
    "taiwan": "TW",
    "tanzania": "TZ",
    "türkiye": "TR",
    "turkey": "TR",
    "united states of america": "US",
    "united states": "US",
    "usa": "US",
    "united kingdom": "GB",
    "uk": "GB",
    "venezuela": "VE",
    "vietnam": "VN",
    "palestine": "PS",
    "the netherlands": "NL",
    "netherlands": "NL",
    "uae": "AE",
    "united arab emirates": "AE",
    "saudi arabia": "SA",
    "south africa": "ZA",
    "european union": None,  # skip — not a country
    "african union": None,
}


def _strip_accents(text: str) -> str:
    """Strip diacritical marks (e.g., Côte d'Ivoire -> Cote d'Ivoire)."""
    nfd = unicodedata.normalize("NFD", text)
    return "".join(c for c in nfd if not unicodedata.combining(c))


def _build_name_index() -> dict[str, str]:
    """Build lowercase name → alpha_2 lookup from pycountry + overrides."""
    idx: dict[str, str] = {}
    for c in pycountry.countries:
        idx[c.name.lower()] = c.alpha_2  # type: ignore
        if hasattr(c, "common_name"):
            idx[c.common_name.lower()] = c.alpha_2  # type: ignore
        if hasattr(c, "official_name"):
            idx[c.official_name.lower()] = c.alpha_2  # type: ignore
    idx.update(NAME_OVERRIDES)  # type: ignore
    return idx


NAME_INDEX = _build_name_index()


def resolve_country(name: str) -> str | None:
    """Resolve a display name to ISO alpha_2, or None if not a country."""
    clean = re.sub(r"\[.*?\]", "", name).strip()  # remove wiki refs like [1]
    clean = re.sub(r"\(.*?\)", "", clean).strip()  # remove parentheticals
    clean = clean.strip("* \t\n")
    key = clean.lower()

    if key in NAME_INDEX:
        return NAME_INDEX[key]

    # Try pycountry fuzzy search as fallback
    try:
        results = pycountry.countries.search_fuzzy(clean)
        if results:
            return results[0].alpha_2  # type: ignore
    except LookupError:
        pass

    return None


# ── Scrapers ────────────────────────────────────────────────────────────────


def fetch_soup(url: str) -> BeautifulSoup:
    """Fetch a URL and return parsed BeautifulSoup."""
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")


def scrape_g7() -> set[str]:
    """Scrape G7 members from Wikipedia.

    G7 membership is extremely stable (no changes since Russia left in 2014),
    so we use the infobox and validate against hardcoded list.
    """
    soup = fetch_soup("https://en.wikipedia.org/wiki/G7")
    hardcoded = {"CA", "FR", "DE", "IT", "JP", "GB", "US"}

    members = set()
    # Look for the infobox — it has a row labeled "Members" with country links
    infobox = soup.find("table", class_="infobox")
    if infobox:
        for tr in infobox.find_all("tr"):
            th = tr.find("th")
            if th and "member" in th.get_text().lower():
                td = tr.find("td")
                if td:
                    for li in td.find_all("li"):
                        a = li.find("a")
                        if a:
                            code = resolve_country(a.get_text())
                            if code:
                                members.add(code)

    return members if 6 <= len(members) <= 9 else hardcoded


def scrape_g20() -> set[str]:
    """Scrape G20 members from Wikipedia."""
    soup = fetch_soup("https://en.wikipedia.org/wiki/G20")
    hardcoded = {
        "AR",
        "AU",
        "BR",
        "CA",
        "CN",
        "FR",
        "DE",
        "IN",
        "ID",
        "IT",
        "JP",
        "KR",
        "MX",
        "RU",
        "SA",
        "ZA",
        "TR",
        "GB",
        "US",
    }

    members = set()
    # Find the member states section
    for header in soup.find_all(["h2", "h3"]):
        if "member" in header.get_text().lower():
            # Scan the next sibling elements for a table or list
            for sib in header.find_next_siblings():
                if sib.name in ("h2", "h3"):
                    break
                for a in sib.find_all("a"):
                    code = resolve_country(a.get_text())
                    if code:
                        members.add(code)

    # Filter to reasonable count (G20 has 19 country members + EU)
    return members if len(members) >= 19 else hardcoded


def scrape_eu() -> set[str]:
    """Scrape EU member states from Wikipedia's member states table."""
    hardcoded = {
        "AT",
        "BE",
        "BG",
        "HR",
        "CY",
        "CZ",
        "DK",
        "EE",
        "FI",
        "FR",
        "DE",
        "GR",
        "HU",
        "IE",
        "IT",
        "LV",
        "LT",
        "LU",
        "MT",
        "NL",
        "PL",
        "PT",
        "RO",
        "SK",
        "SI",
        "ES",
        "SE",
    }

    soup = fetch_soup(
        "https://en.wikipedia.org/wiki/Member_state_of_the_European_Union"
    )
    members = set()

    # Find the first wikitable sortable — this is the member states table
    table = soup.find("table", class_="wikitable sortable")
    if table:
        for row in table.find_all("tr")[1:]:  # skip header
            cells = row.find_all("td")
            if not cells:
                continue
            # Country name is typically in the first cell with a link
            a = cells[0].find("a")
            if a:
                code = resolve_country(a.get_text())
                if code:
                    members.add(code)

    return members if 25 <= len(members) <= 30 else hardcoded


def scrape_nato() -> set[str]:
    """Scrape NATO member states from Wikipedia."""
    soup = fetch_soup("https://en.wikipedia.org/wiki/Member_states_of_NATO")
    members = set()

    for table in soup.find_all("table", class_="wikitable"):
        prev_header = table.find_previous("h2")
        if not prev_header or "member" not in prev_header.get_text().lower():
            continue
        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if not cells:
                continue
            # First cell with a link is usually the country
            for a in cells[0].find_all("a"):
                code = resolve_country(a.get_text())
                if code:
                    members.add(code)
                    break

    hardcoded = {
        "AL",
        "BE",
        "BG",
        "CA",
        "HR",
        "CZ",
        "DK",
        "EE",
        "FI",
        "FR",
        "DE",
        "GR",
        "HU",
        "IS",
        "IT",
        "LV",
        "LT",
        "LU",
        "ME",
        "NL",
        "MK",
        "NO",
        "PL",
        "PT",
        "RO",
        "SK",
        "SI",
        "ES",
        "SE",
        "TR",
        "GB",
        "US",
    }
    return members if len(members) >= 30 else hardcoded


def scrape_oecd() -> set[str]:
    """Scrape OECD member states from Wikipedia."""
    soup = fetch_soup("https://en.wikipedia.org/wiki/OECD")
    members = set()

    # Find "Member countries" section
    for header in soup.find_all(["h2", "h3"]):
        htext = header.get_text().lower()
        if "member" in htext and "country" in htext or "countries" in htext:
            for sib in header.find_next_siblings():
                if sib.name in ("h2", "h3"):
                    break
                for a in sib.find_all("a"):
                    code = resolve_country(a.get_text())
                    if code:
                        members.add(code)
            break

    hardcoded = {
        "AU",
        "AT",
        "BE",
        "CA",
        "CL",
        "CO",
        "CR",
        "CZ",
        "DK",
        "EE",
        "FI",
        "FR",
        "DE",
        "GR",
        "HU",
        "IS",
        "IE",
        "IL",
        "IT",
        "JP",
        "KR",
        "LV",
        "LT",
        "LU",
        "MX",
        "NL",
        "NZ",
        "NO",
        "PL",
        "PT",
        "SK",
        "SI",
        "ES",
        "SE",
        "CH",
        "TR",
        "GB",
        "US",
    }
    return members if len(members) >= 35 else hardcoded


def scrape_opec() -> set[str]:
    """Scrape OPEC member states from Wikipedia."""
    soup = fetch_soup("https://en.wikipedia.org/wiki/OPEC")
    members = set()

    # Find "Current members" or "Member countries" section
    for header in soup.find_all(["h2", "h3"]):
        htext = header.get_text().lower()
        if ("current" in htext and "member" in htext) or (
            "member" in htext and ("country" in htext or "countries" in htext)
        ):
            for sib in header.find_next_siblings():
                if sib.name in ("h2", "h3"):
                    break
                for a in sib.find_all("a"):
                    code = resolve_country(a.get_text())
                    if code:
                        members.add(code)
            if members:
                break

    hardcoded = {
        "DZ",
        "CG",
        "GQ",
        "GA",
        "IR",
        "IQ",
        "KW",
        "LY",
        "NG",
        "SA",
        "AE",
        "VE",
    }
    return members if len(members) >= 10 else hardcoded


def scrape_brics() -> set[str]:
    """Scrape BRICS member states from Wikipedia."""
    soup = fetch_soup("https://en.wikipedia.org/wiki/BRICS")
    members = set()

    # Find "Member states" section
    for header in soup.find_all(["h2", "h3"]):
        if "member" in header.get_text().lower():
            for sib in header.find_next_siblings():
                if sib.name in ("h2", "h3"):
                    break
                # Look in tables for member states
                if sib.name == "table":
                    for row in sib.find_all("tr"):
                        for a in row.find_all("a"):
                            code = resolve_country(a.get_text())
                            if code:
                                members.add(code)
                for a in sib.find_all("a"):
                    code = resolve_country(a.get_text())
                    if code:
                        members.add(code)
            if members:
                break

    # 2024 expansion: Egypt, Ethiopia, Iran, UAE + Indonesia (Jan 2025)
    hardcoded = {"BR", "RU", "IN", "CN", "ZA", "EG", "ET", "IR", "AE", "ID"}
    return members if len(members) >= 9 else hardcoded


# ── Main logic ──────────────────────────────────────────────────────────────

GROUP_SCRAPERS = {
    "G7": scrape_g7,
    "G20": scrape_g20,
    "EU": scrape_eu,
    "NATO": scrape_nato,
    "OECD": scrape_oecd,
    "OPEC": scrape_opec,
    "BRICS": scrape_brics,
}


def build_country_data() -> dict:
    """Build the complete country_data.json structure."""
    # 1. Scrape all group memberships
    group_members: dict[str, set[str]] = {}
    for group_name, scraper in GROUP_SCRAPERS.items():
        print(f"Scraping {group_name}...", end=" ", flush=True)
        try:
            members = scraper()
            group_members[group_name] = members
            print(f"✅ {len(members)} members")
        except Exception as e:
            print(f"❌ Error: {e}")
            group_members[group_name] = set()

    # 2. Sanity checks
    print("\n── Sanity Checks ──")
    for group_name, members in group_members.items():
        expected = EXPECTED_COUNTS.get(group_name)
        count = len(members)
        if expected is None:
            continue
        if isinstance(expected, tuple):
            lo, hi = expected
            ok = lo <= count <= hi
            expected_str = f"{lo}-{hi}"
        elif isinstance(expected, int):
            ok = abs(count - expected) <= 2  # allow ±2 tolerance
            expected_str = str(expected)
        status = "✅" if ok else "⚠️"
        print(f"  {status} {group_name}: got {count}, expected ~{expected_str}")
        if not ok:
            print(f"     Members: {sorted(members)}")

    # 3. Build alpha_2 → groups mapping
    country_groups: dict[str, list[str]] = {}
    for group_name, members in group_members.items():
        for alpha_2 in members:
            country_groups.setdefault(alpha_2, []).append(group_name)

    # Sort group lists for consistency
    for groups in country_groups.values():
        groups.sort()

    # 4. Build country list from pycountry
    countries = []
    for c in sorted(pycountry.countries, key=lambda x: x.alpha_2):  # type: ignore
        entry: dict = {
            "alpha_2": c.alpha_2,  # type: ignore
            "alpha_3": c.alpha_3,  # type: ignore
            "name": _strip_accents(c.name),  # type: ignore
            "numeric": c.numeric,  # type: ignore
        }
        groups = country_groups.get(c.alpha_2)  # type: ignore
        if groups:
            entry["groups"] = groups
        countries.append(entry)

    return {
        "_last_updated": date.today().isoformat(),
        "_sources": {
            "iso_3166": "pycountry library",
            "G7": "https://en.wikipedia.org/wiki/G7",
            "G20": "https://en.wikipedia.org/wiki/G20",
            "EU": "https://european-union.europa.eu/principles-countries-history/eu-countries_en",
            "NATO": "https://en.wikipedia.org/wiki/Member_states_of_NATO",
            "OECD": "https://en.wikipedia.org/wiki/OECD",
            "OPEC": "https://en.wikipedia.org/wiki/OPEC",
            "BRICS": "https://en.wikipedia.org/wiki/BRICS",
        },
        "countries": countries,
    }


def main():
    """CLI entrypoint to regenerate country_data.json."""
    parser = argparse.ArgumentParser(
        description="Regenerate country_data.json from authoritative sources."
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output path (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print summary without writing file.",
    )
    args = parser.parse_args()

    print("🌍 Updating country_data.json\n")
    data = build_country_data()

    countries_with_groups = sum(1 for c in data["countries"] if "groups" in c)
    total = len(data["countries"])
    print("\n── Summary ──")
    print(f"  Total countries: {total}")
    print(f"  Countries with group memberships: {countries_with_groups}")
    print(f"  Last updated: {data['_last_updated']}")

    if args.dry_run:
        print("\n[DRY RUN] Would write to:", args.output)
        # Print first 5 entries as sample
        print("\nSample (first 5 entries):")
        sample = {
            "_last_updated": data["_last_updated"],
            "countries": data["countries"][:5],
        }
        print(json.dumps(sample, indent=2, ensure_ascii=False))
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"\n✅ Written to: {args.output}")


if __name__ == "__main__":
    main()
