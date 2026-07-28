#!/usr/bin/env python
"""Generate the shipped ``bls_cache.zip`` archive.

Run from the bls provider root:

    python openbb_bls/utils/generate_cache.py

For each survey category the script sequentially downloads the
fixed-width ``series`` listing plus every referenced codelist from
https://download.bls.gov/pub/time.series/ and packs the result into a
single ZIP archive at ``openbb_bls/assets/bls_cache.zip`` with this
layout::

    bls_cache.zip
    ├── index.json           ← {categories: {cat: {surveys, series_count, name}}}
    ├── {cat}/series.csv     ← one row per series_id
    ├── {cat}/codes.json     ← {survey: {dim_code: {value: label}}}
    └── ...

BLS rate-limits aggressive scrapers, so surveys are fetched serially
within a category (with a short inter-request sleep) and categories
themselves are processed serially. The whole run takes 2-3 minutes.
"""

from __future__ import annotations

import csv
import io
import json
import sys
import time
import zipfile
from collections import defaultdict
from pathlib import Path

import requests

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
CACHE_FILE = ASSETS_DIR / "bls_cache.zip"
BASE_URL = "https://download.bls.gov/pub/time.series"
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Linux; U; Android 4.0.4; en-us; Glass 1 Build/IMM76L; "
        "XE16.2) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 "
        "Mobile Safari/534.30"
    ),
    "Accept": "text/plain, */*",
}

# Surveys grouped into download categories. Mirrors
# ``openbb_bls.utils.constants.SURVEY_CATEGORY_MAP`` but inlined so the
# generator runs in the PEP 517 build env without importing the package.
SURVEY_CATEGORY_MAP: dict[str, list[str]] = {
    "cpi": ["ap", "cu", "cw", "li", "su"],
    "ixp": ["ei"],
    "pce": ["cx"],
    "ppi": ["wp", "pc"],
    "ip": ["ip", "pr", "mp"],
    "jolts": ["jl", "jt"],
    "nfp": ["ce"],
    "cps": ["le", "lu"],
    "lfs": ["ln", "fm", "in", "ws"],
    "wages": ["ci", "wm"],
    "ec": ["cm", "cc"],
    "sla": ["la", "sm"],
    "bed": ["bd"],
    "tu": ["tu"],
}

CATEGORY_NAMES: dict[str, str] = {
    "cpi": "Consumer Price Index",
    "ixp": "Import/Export Price Indexes",
    "pce": "Consumer Expenditure Survey",
    "ppi": "Producer Price Index",
    "ip": "Productivity (Industry, Major Sector & Total Factor)",
    "jolts": "Job Openings and Labor Turnover Survey",
    "nfp": "Nonfarm Payrolls (Current Employment Statistics)",
    "cps": "Current Population Survey",
    "lfs": "Labor Force Statistics & International Comparisons",
    "wages": "Employment Cost Index & Wage Estimates",
    "ec": "Employer Costs for Employee Compensation",
    "sla": "State & Local Area Employment & Unemployment",
    "bed": "Business Employment Dynamics",
    "tu": "American Time Use Survey",
}

SURVEY_NAMES: dict[str, str] = {
    "AP": "Consumer Price Index - Average Price Data",
    "BD": "Business Employment Dynamics",
    "CC": "Employer Costs for Employee Compensation",
    "CE": "Current Employment Statistics (National)",
    "CI": "Employment Cost Index",
    "CM": "Employer Costs for Employee Compensation",
    "CU": "Consumer Price Index - All Urban Consumers",
    "CW": "Consumer Price Index - Urban Wage Earners and Clerical Workers",
    "CX": "Consumer Expenditure Survey",
    "EI": "Import/Export Price Indexes",
    "FM": "Current Population Survey - Marital and Family Labor Force",
    "IN": "International Labor Comparisons",
    "IP": "Industry Productivity",
    "JL": "Job Openings and Labor Turnover Survey",
    "JT": "Job Openings and Labor Turnover Survey",
    "LA": "Local Area Unemployment Statistics",
    "LE": "Current Population Survey - Weekly and Hourly Earnings",
    "LI": "Consumer Price Index - Department Store Inventory Price Index",
    "LN": "Labor Force Statistics from the Current Population Survey",
    "LU": "Current Population Survey - Union Affiliation",
    "MP": "Major Sector Total Factor Productivity",
    "PC": "Producer Price Index - Industry",
    "PR": "Major Sector Productivity and Costs",
    "SM": "State and Area Employment, Hours, and Earnings",
    "SU": "Consumer Price Index - Chained (C-CPI-U)",
    "TU": "American Time Use Survey",
    "WM": "Modeled Wage Estimates",
    "WP": "Producer Price Index - Commodity",
    "WS": "Work Stoppages",
}

# Surveys flagged as "skip" by the legacy downloader. They have no
# downloadable series listing or are deprecated mirrors of other surveys.
_SKIP_SURVEYS: set[str] = {"ch", "cs", "fw", "is", "nw", "oe", "yy"}


def _get(url: str, retries: int = 4, backoff: float = 2.0) -> requests.Response | None:
    """GET ``url`` returning the Response, or ``None`` on a 404."""
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=_HEADERS, timeout=120)
        except requests.RequestException:
            if attempt == retries - 1:
                raise
            time.sleep(backoff * (attempt + 1))
            continue
        if resp.status_code == 404:
            return None
        if resp.status_code == 429:
            time.sleep(max(10.0, backoff * (attempt + 1) * 5))
            continue
        if resp.status_code != 200:
            if attempt == retries - 1:
                resp.raise_for_status()
            time.sleep(backoff * (attempt + 1))
            continue
        return resp
    raise requests.RequestException(f"failed after {retries} attempts: {url}")


def _parse_tsv(text: str) -> list[dict[str, str | None]]:
    """Parse a BLS fixed-tab TSV blob into a list of stripped-string rows."""
    reader = csv.DictReader(io.StringIO(text), delimiter="\t")
    if reader.fieldnames is None:
        return []
    headers = [name.strip() for name in reader.fieldnames]
    rows: list[dict[str, str | None]] = []
    for raw in reader:
        clean: dict[str, str | None] = {}
        for header, key in zip(headers, reader.fieldnames):
            val = raw.get(key)
            if isinstance(val, str):
                val = val.strip()
            if val in ("", "''", '""', "nan", None):
                clean[header] = None
            else:
                clean[header] = val
        rows.append(clean)
    return rows


def _fetch_survey_asset(survey: str, asset: str) -> list[dict] | None:
    """Fetch ``<survey>.<asset>`` from download.bls.gov, returning parsed rows."""
    url = f"{BASE_URL}/{survey}/{survey}.{asset}"
    resp = _get(url)
    if resp is None or not resp.text.strip():
        return None
    try:
        return _parse_tsv(resp.text)
    except Exception as exc:  # noqa: BLE001
        print(f"      warn: failed to parse {url}: {exc}", file=sys.stderr)
        return None


def _build_code_map(survey: str, code_columns: list[str]) -> dict[str, dict[str, str]]:
    """Resolve the ``{dim}.code`` files referenced by a survey's series listing."""
    code_map: dict[str, dict[str, str]] = {}
    for code_col in code_columns:
        dim = code_col.removesuffix("_code")
        asset = "datatype" if dim == "data" else dim
        rows = _fetch_survey_asset(survey, asset)
        if not rows:
            continue
        resolved_dim = "data_type" if dim == "data" and survey == "ce" else dim
        labels: dict[str, str] = {}
        for row in rows:
            code = row.get(f"{dim}_code")
            label = (
                row.get(f"{dim}_name")
                or row.get(f"{dim}_text")
                or row.get(f"{dim}_title")
            )
            if code is None:
                continue
            labels[str(code)] = str(label) if label is not None else str(code)
        if labels:
            code_map[f"{resolved_dim}_code"] = labels
    return code_map


def _resolve_codes(
    row: dict[str, str | None], code_map: dict[str, dict[str, str]]
) -> dict[str, str | None]:
    """Replace each ``{dim}_code`` value with its human label when known."""
    out: dict[str, str | None] = dict(row)
    for col, labels in code_map.items():
        if col in out and out[col] is not None:
            raw = out[col]
            if isinstance(raw, str) and "," in raw and any(c.isdigit() for c in raw):
                parts = [labels.get(p, p) for p in raw.split(",")]
                out[col] = " ".join(p for p in parts if p)
            else:
                out[col] = labels.get(str(raw), raw)
    return out


def fetch_category(
    category: str, surveys: list[str]
) -> tuple[list[dict], dict[str, dict[str, dict[str, str]]]]:
    """Fetch every series row + code map for one category."""
    rows: list[dict] = []
    codes: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)

    for survey in surveys:
        if survey in _SKIP_SURVEYS:
            continue
        print(f"    {survey}", flush=True)
        series = _fetch_survey_asset(survey, "series")
        if not series:
            continue

        code_columns = sorted(
            {
                c
                for row in series
                for c in row
                if c.endswith("_code") and "periodicity" not in c
            }
        )
        survey_codes = _build_code_map(survey, code_columns)
        if survey_codes:
            codes[survey] = survey_codes

        survey_name = SURVEY_NAMES.get(survey.upper(), survey.upper())
        for raw in series:
            sid = raw.get("series_id")
            if not isinstance(sid, str) or not sid.upper().startswith(survey.upper()):
                continue
            resolved = _resolve_codes(raw, survey_codes)
            resolved["survey_name"] = survey_name
            rows.append(resolved)
        time.sleep(0.25)

    return rows, dict(codes)


def _rows_to_csv_bytes(rows: list[dict]) -> bytes:
    """Serialise a list of series rows to UTF-8 CSV bytes, dropping all-null columns."""
    columns: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row:
            if key not in seen:
                seen.add(key)
                columns.append(key)
    keep = [c for c in columns if any(row.get(c) not in (None, "") for row in rows)]
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=keep, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow({c: ("" if row.get(c) is None else row.get(c)) for c in keep})
    return buf.getvalue().encode("utf-8")


def main() -> None:
    """Materialise ``bls_cache.zip`` from the BLS bulk-download tree."""
    t0 = time.time()
    print("BLS cache: starting...", flush=True)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    index: dict[str, dict] = {}
    entries: dict[str, bytes] = {}

    for category, surveys in SURVEY_CATEGORY_MAP.items():
        print(f"  [{category}] {len(surveys)} surveys", flush=True)
        rows, codes = fetch_category(category, surveys)
        if not rows:
            continue
        entries[f"{category}/series.csv"] = _rows_to_csv_bytes(rows)
        entries[f"{category}/codes.json"] = json.dumps(
            codes, separators=(",", ":")
        ).encode("utf-8")
        index[category] = {
            "name": CATEGORY_NAMES.get(category, category),
            "surveys": surveys,
            "series_count": len(rows),
        }

    entries["index.json"] = json.dumps(
        {"categories": index}, separators=(",", ":")
    ).encode("utf-8")

    print("  writing zip...", flush=True)
    with zipfile.ZipFile(
        CACHE_FILE,
        "w",
        compression=zipfile.ZIP_LZMA,
    ) as zf:
        for name, payload in entries.items():
            zf.writestr(name, payload)

    size_mb = CACHE_FILE.stat().st_size / (1024 * 1024)
    elapsed = time.time() - t0
    total_rows = sum(idx["series_count"] for idx in index.values())
    print(
        f"Wrote {CACHE_FILE} ({size_mb:.1f} MB, "
        f"{len(index)} categories, {total_rows} series) in {elapsed:.0f}s",
        flush=True,
    )


if __name__ == "__main__":
    main()
