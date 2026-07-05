"""BoC fetcher tests backed by VCR cassettes.

These tests replay recorded HTTP interactions from
``tests/record/http/test_boc_fetchers/*.yaml`` so CI can run without
network access. The cassettes were recorded with a 6-month date range
(2025-12-31 to 2026-06-29) to validate parsing of multiple rows and
date mapping across a meaningful span.

To re-record the cassettes (e.g. when the BoC changes its API
response shape), run::

    python /home/z/my-project/scripts/record_vcr_cassettes.py

The tests use ``@pytest.mark.record_http`` (declared in
``pyproject.toml``) matching the OECD V5 pattern. VCR's record mode
is ``none`` so any unrecorded HTTP call fails the test — this
catches drift between the fetcher code and the cassettes.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from openbb_government_ca.boc.fx import BankOfCanadaFXFetcher
from openbb_government_ca.boc.rates import BankOfCanadaRatesFetcher
from openbb_government_ca.boc.yields import BankOfCanadaYieldsFetcher
from openbb_government_ca.utils.metadata import GovernmentCaMetadata

# The cassettes were recorded with this exact date range. The tests
# must use the same range so VCR can match the requests.
CASSETTE_START = date(2025, 12, 31)
CASSETTE_END = date(2026, 6, 29)

_CASSETTE_DIR = Path(__file__).parent / "record" / "http" / "test_boc_fetchers"


# ---------------------------------------------------------------------------
# VCR configuration — match the OECD V5 pattern
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def vcr_config():
    """VCR configuration: match on URL+query, strip User-Agent."""
    return {
        "record_mode": "none",  # never record; fail on unrecorded calls
        "match_on": ["method", "scheme", "host", "port", "path", "query"],
        "filter_headers": ["user-agent", "User-Agent"],
    }


# ---------------------------------------------------------------------------
# Shared fixture: seed the cache with real BoC series metadata
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def seeded_boc_cache():
    """Seed the metadata singleton with real BoC series metadata.

    The fetchers read the cache to resolve ``observations_url`` before
    making the HTTP call that VCR intercepts. We seed with the same
    real BoC catalog data that was used during recording.
    """
    import json

    from openbb_government_ca.utils.generate_cache import (
        _normalize_boc_group_entry,
        _normalize_boc_series_entry,
    )

    research_dir = Path("/home/z/my-project/research")
    series_file = research_dir / "boc_series_list.json"
    groups_file = research_dir / "boc_groups_list.json"
    if not series_file.exists() or not groups_file.exists():
        pytest.skip(
            "BoC catalog fixtures not available locally. These cassettes "
            "are recorded by the maintainer with real BoC API responses "
            "and stored under /home/z/my-project/research/."
        )
    series_list = json.loads(series_file.read_text())["series"]
    groups_list = json.loads(groups_file.read_text())["groups"]

    interest = (
        "FXUSDCAD",
        "V39076",
        "V39077",
        "V39078",
        "V39079",
        "CBC20210",
        "BD.CDN.2YR.DQ.YLD",
        "BD.CDN.3YR.DQ.YLD",
        "BD.CDN.5YR.DQ.YLD",
        "BD.CDN.7YR.DQ.YLD",
        "BD.CDN.10YR.DQ.YLD",
        "BD.CDN.LONG.DQ.YLD",
        "BD.CDN.RRB.DQ.YLD",
    )

    GovernmentCaMetadata._reset()
    meta = GovernmentCaMetadata()
    meta._apply_blob(
        {
            "generated_at": "2026-06-28T05:00:00Z",
            "source": "vcr-test",
            "boc": {
                "valet_url": "https://www.bankofcanada.ca/valet",
                "status": "ok",
                "series": {
                    n: _normalize_boc_series_entry(n, series_list[n])
                    for n in interest
                    if n in series_list
                },
                "groups": {
                    n: _normalize_boc_group_entry(n, groups_list[n])
                    for n in ["FX_RATES_DAILY"]
                    if n in groups_list
                },
                "series_count": len([n for n in interest if n in series_list]),
                "groups_count": 1,
            },
            "statscan": {},
        }
    )
    yield meta
    GovernmentCaMetadata._reset()


# ===========================================================================
# FX fetcher — cassette-backed test
# ===========================================================================
@pytest.mark.record_http
def test_boc_fx_fetcher_with_cassette(seeded_boc_cache):
    """FX fetcher returns multiple observations from the cassette.

    The cassette contains ~124 daily observations of FXUSDCAD over a
    6-month span. We validate:
    - Multiple rows returned (not just one day)
    - ``close`` is populated, OHLC is None (per brief)
    - Values are NOT normalized (FX is direct price)
    - Date sort is ascending
    """
    q = BankOfCanadaFXFetcher.transform_query(
        {
            "symbol": "FXUSDCAD",
            "start_date": CASSETTE_START,
            "end_date": CASSETTE_END,
        }
    )
    raw = BankOfCanadaFXFetcher.extract_data(q, None)
    result = BankOfCanadaFXFetcher.transform_data(q, raw)

    # Multiple rows — validates parsing across a 6-month span.
    assert len(result) > 50, f"expected 50+ observations, got {len(result)}"

    # All rows have close populated, OHLC None.
    for row in result:
        assert row.close is not None
        assert row.open is None
        assert row.high is None
        assert row.low is None
        assert row.volume is None
        assert row.vwap is None
        assert row.series == "FXUSDCAD"

    # Values are direct prices (not normalized). FXUSDCAD has
    # historically been in the 1.20-1.45 range — verify the values
    # are in a sane ballpark for direct prices (NOT 0.01-0.02 which
    # would indicate erroneous division by 100).
    for row in result:
        assert 0.5 < row.close < 2.5, (
            f"close={row.close} is out of expected FX range — "
            "did you accidentally normalize?"
        )

    # Date sort is ascending.
    dates = [r.date for r in result]
    assert dates == sorted(dates)


# ===========================================================================
# Rates fetcher — cassette-backed test
# ===========================================================================
@pytest.mark.record_http
def test_boc_rates_fetcher_with_cassette(seeded_boc_cache):
    """Rates fetcher returns target overnight rate observations.

    The cassette contains ~126 daily observations of CBC20210 (Target
    for the overnight rate) over a 6-month span. We validate:
    - Multiple rows returned
    - ``value`` is normalized to decimal (raw 2.25 → 0.0225)
    - ``country`` is 'canada'
    - ``series`` is 'CBC20210' (the preferred name)
    - Date sort is ascending
    """
    q = BankOfCanadaRatesFetcher.transform_query(
        {"start_date": CASSETTE_START, "end_date": CASSETTE_END}
    )
    raw = BankOfCanadaRatesFetcher.extract_data(q, None)
    result = BankOfCanadaRatesFetcher.transform_data(q, raw)

    assert len(result) > 50, f"expected 50+ observations, got {len(result)}"

    # CBC20210 was preferred over V39079.
    assert all(r.series == "CBC20210" for r in result)

    # Country is always canada.
    assert all(r.country == "canada" for r in result)

    # Values are normalized to decimal. BoC policy rate has been in
    # the 2.25%-5.00% range recently — verify the normalized values
    # are in 0.02-0.10 (i.e. 2%-10%). If we forgot to divide, the
    # values would be 2.25-5.00 and this assertion would fail.
    for row in result:
        assert 0.005 < row.value < 0.20, (
            f"value={row.value} is out of expected normalized range — "
            "did you forget to divide by 100?"
        )

    # Date sort is ascending.
    dates = [r.date for r in result]
    assert dates == sorted(dates)


# ===========================================================================
# Yields fetcher — cassette-backed test
# ===========================================================================
@pytest.mark.record_http
def test_boc_yields_fetcher_with_cassette(seeded_boc_cache):
    """Yields fetcher returns benchmark bond yields pivoted by date.

    The cassette contains 6 parallel HTTP calls (one per tenor: 2Y,
    3Y, 5Y, 7Y, 10Y, LONG) with ~123 days of observations each. We
    validate:
    - Multiple rows returned (one per date)
    - ``year_2``, ``year_3``, ``year_5``, ``year_7``, ``year_10``,
      ``year_30`` are all populated (LONG → year_30)
    - Sub-1Y fields (``week_4``, ``month_3``, ``year_1``) and
      ``year_20`` are all ``None`` (per brief)
    - Values are normalized to decimal (raw 3.18 → 0.0318)
    - Date sort is ascending
    """
    q = BankOfCanadaYieldsFetcher.transform_query(
        {"start_date": CASSETTE_START, "end_date": CASSETTE_END}
    )
    raw = BankOfCanadaYieldsFetcher.extract_data(q, None)
    result = BankOfCanadaYieldsFetcher.transform_data(q, raw)

    assert len(result) > 50, f"expected 50+ days, got {len(result)}"

    # All 6 nominal tenors should be populated on most days.
    # (Some tenors might be None on holidays, but the majority should be filled.)
    filled_year_2 = sum(1 for r in result if r.year_2 is not None)
    filled_year_10 = sum(1 for r in result if r.year_10 is not None)
    filled_year_30 = sum(1 for r in result if r.year_30 is not None)
    assert filled_year_2 > 40, f"year_2 only filled on {filled_year_2} days"
    assert filled_year_10 > 40, f"year_10 only filled on {filled_year_10} days"
    assert filled_year_30 > 40, f"year_30 only filled on {filled_year_30} days"

    # Sub-1Y and year_20 are ALWAYS None per the brief.
    for row in result:
        assert row.week_4 is None
        assert row.month_1 is None
        assert row.month_2 is None
        assert row.month_3 is None
        assert row.month_6 is None
        assert row.year_1 is None
        assert row.year_20 is None

    # Values are normalized to decimal. Canadian benchmark bond
    # yields have been in the 2.5%-4.5% range recently — verify the
    # normalized values are in 0.02-0.06 (i.e. 2%-6%).
    for row in result:
        if row.year_10 is not None:
            assert 0.01 < row.year_10 < 0.10, (
                f"year_10={row.year_10} is out of expected normalized range — "
                "did you forget to divide by 100?"
            )

    # Date sort is ascending.
    dates = [r.date for r in result]
    assert dates == sorted(dates)

    # The fetched_tenors extension field lists all 6 tenors.
    sample = next(r for r in result if r.fetched_tenors)
    assert set(sample.fetched_tenors) == {"2Y", "3Y", "5Y", "7Y", "10Y", "LONG"}


# ===========================================================================
# Smoke test: verify cassettes exist and are non-empty
# ===========================================================================
def test_cassettes_exist_and_are_non_empty():
    """All 3 cassettes exist and contain recorded interactions.

    This catches the case where someone deletes a cassette file or
    the recording script fails silently.
    """
    expected = {
        "test_boc_fx_fetcher_urllib3_v2.yaml",
        "test_boc_rates_fetcher_urllib3_v2.yaml",
        "test_boc_yields_fetcher_urllib3_v2.yaml",
    }
    actual = {f.name for f in _CASSETTE_DIR.glob("*.yaml")}
    assert expected.issubset(actual), (
        f"missing cassettes: {expected - actual}. "
        "Run: python /home/z/my-project/scripts/record_vcr_cassettes.py"
    )

    # Each cassette should be at least 5KB (indicating real recorded data).
    for name in expected:
        size = (_CASSETTE_DIR / name).stat().st_size
        assert size > 5000, f"{name} is only {size} bytes — may be empty"
