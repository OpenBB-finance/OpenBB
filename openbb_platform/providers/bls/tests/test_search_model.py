"""Tests for the ``BlsSearchFetcher``."""

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_bls.models.search import (
    BlsSearchData,
    BlsSearchFetcher,
    BlsSearchQueryParams,
    _fill_titles,
    _is_blank_title,
    _rank_by_recency,
    _synthesize_title,
)


def test_rank_by_recency_orders_current_first():
    """Series with the most recent ``end_year`` (then period) sort first."""
    from pandas import DataFrame

    df = DataFrame(
        [
            {"series_id": "OLD", "end_year": "2003", "end_period": "M12"},
            {"series_id": "NEW", "end_year": "2026", "end_period": "M04"},
            {"series_id": "MID", "end_year": "2015", "end_period": "M06"},
        ]
    )
    assert list(_rank_by_recency(df)["series_id"]) == ["NEW", "MID", "OLD"]


def test_rank_by_recency_pushes_missing_year_to_bottom():
    """Missing / non-numeric ``end_year`` is treated as oldest."""
    from pandas import DataFrame

    df = DataFrame(
        [
            {"series_id": "A", "end_year": None, "end_period": "M01"},
            {"series_id": "B", "end_year": "2026", "end_period": "M01"},
            {"series_id": "C", "end_year": "bad", "end_period": "M01"},
        ]
    )
    assert _rank_by_recency(df).iloc[0]["series_id"] == "B"


def test_rank_by_recency_without_end_period_column():
    """Ranking still works when only ``end_year`` is present."""
    from pandas import DataFrame

    df = DataFrame(
        [{"series_id": "A", "end_year": "2000"}, {"series_id": "B", "end_year": "2024"}]
    )
    assert list(_rank_by_recency(df)["series_id"]) == ["B", "A"]


def test_rank_by_recency_no_end_year_is_noop():
    """A frame without ``end_year`` is returned unchanged."""
    from pandas import DataFrame

    df = DataFrame([{"series_id": "A"}, {"series_id": "B"}])
    assert list(_rank_by_recency(df)["series_id"]) == ["A", "B"]


def test_is_blank_title_branches():
    """``_is_blank_title`` flags None / placeholder strings, keeps real text."""
    assert _is_blank_title(None)
    assert _is_blank_title("")
    assert _is_blank_title("   ")
    assert _is_blank_title("NaN")
    assert _is_blank_title("-")
    assert not _is_blank_title("All items in U.S. city average")


def test_synthesize_title_combines_resolved_fields():
    """A title is built in reading order with the seasonal-adjustment suffix."""
    row = {
        "sector_code": "Manufacturing, Nondurable Goods",
        "measure_code": "Output per worker",
        "duration_code": "% Change from previous quarter",
        "seasonal": "S",
    }
    assert _synthesize_title(row) == (
        "Manufacturing, Nondurable Goods — Output per worker"
        " — % Change from previous quarter (seasonally adjusted)"
    )


def test_synthesize_title_dedupes_skips_blanks_and_marks_unadjusted():
    """Duplicate / blank parts are dropped; ``U`` yields the unadjusted suffix."""
    row = {
        "industry_code": "Total Nonfarm",
        "region_code": "Total Nonfarm",  # duplicate -> collapsed
        "area_code": "-",  # blank -> skipped
        "dataelement_code": "Hires",
        "seasonal": "U",
    }
    assert _synthesize_title(row) == "Total Nonfarm — Hires (not seasonally adjusted)"


def test_synthesize_title_seasonal_only_and_empty():
    """With no descriptive fields, fall back to the seasonal label or None."""
    assert _synthesize_title({"seasonal": "S"}) == "Seasonally adjusted"
    assert _synthesize_title({"sector_code": "-", "seasonal": ""}) is None


def test_fill_titles_fills_blanks_and_preserves_existing():
    """``_fill_titles`` keeps real titles and synthesizes the missing ones."""
    from pandas import DataFrame

    df = DataFrame(
        [
            {"series_id": "A", "series_title": "Real title", "sector_code": "X"},
            {
                "series_id": "B",
                "series_title": None,
                "sector_code": "Mining",
                "dataelement_code": "Hires",
                "seasonal": "U",
            },
        ]
    )
    out = _fill_titles(df)
    assert out.loc[0, "series_title"] == "Real title"
    assert out.loc[1, "series_title"] == "Mining — Hires (not seasonally adjusted)"


def test_fill_titles_adds_missing_column():
    """A category without a ``series_title`` column gets one synthesized."""
    from pandas import DataFrame

    df = DataFrame(
        [{"series_id": "A", "industry_code": "Total Nonfarm", "seasonal": "S"}]
    )
    out = _fill_titles(df)
    assert out.loc[0, "series_title"] == "Total Nonfarm (seasonally adjusted)"


def test_transform_query_validates_category():
    """``transform_query`` builds the params model with a valid category."""
    params = BlsSearchFetcher.transform_query({"category": "cpi", "query": "Food"})
    assert isinstance(params, BlsSearchQueryParams)
    assert params.category == "cpi"
    assert params.query == "Food"


def test_transform_query_rejects_invalid_category():
    """Pydantic rejects categories outside ``SURVEY_CATEGORIES``."""
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        BlsSearchFetcher.transform_query({"category": "not-a-cat"})


def test_extract_data_no_query_returns_all_rows(stub_cache_path):
    """An empty query string returns every row in the category."""
    query = BlsSearchFetcher.transform_query({"category": "cpi", "query": ""})
    rows = BlsSearchFetcher.extract_data(query, credentials=None)
    assert len(rows) == 2
    assert {r["series_id"] for r in rows} == {"CUUR0000SA0", "CUUR0000SAF1"}


def test_extract_data_applies_and_filter(stub_cache_path):
    """Semicolon-separated terms apply AND across rows."""
    query = BlsSearchFetcher.transform_query({"category": "cpi", "query": "Food;city"})
    rows = BlsSearchFetcher.extract_data(query, credentials=None)
    assert len(rows) == 1
    assert rows[0]["series_id"] == "CUUR0000SAF1"


def test_extract_data_empty_match_raises(stub_cache_path):
    """A non-matching query bubbles up as ``EmptyDataError``."""
    query = BlsSearchFetcher.transform_query(
        {"category": "cpi", "query": "no-such-term"}
    )
    with pytest.raises(EmptyDataError):
        BlsSearchFetcher.extract_data(query, credentials=None)


def test_extract_data_include_extras_keeps_all_columns(stub_cache_path):
    """``include_extras=True`` returns every column from the series table."""
    query = BlsSearchFetcher.transform_query(
        {"category": "cpi", "query": "Food", "include_extras": True}
    )
    rows = BlsSearchFetcher.extract_data(query, credentials=None)
    assert "area_code" in rows[0]


def test_extract_data_default_trims_columns(stub_cache_path):
    """Without extras the result is trimmed to the canonical 3 columns."""
    query = BlsSearchFetcher.transform_query({"category": "cpi", "query": "Food"})
    rows = BlsSearchFetcher.extract_data(query, credentials=None)
    assert set(rows[0]) == {"series_id", "series_title", "survey_name"}


def test_transform_data_attaches_codes_when_requested(stub_cache_path):
    """``include_code_map=True`` populates the AnnotatedResult metadata."""
    query = BlsSearchFetcher.transform_query(
        {"category": "cpi", "query": "Food", "include_code_map": True}
    )
    rows = BlsSearchFetcher.extract_data(query, credentials=None)
    result = BlsSearchFetcher.transform_data(query, rows)
    assert result.metadata == {"cu": {"area_code": {"0000": "U.S. city average"}}}
    assert all(isinstance(r, BlsSearchData) for r in result.result)


def test_transform_data_without_code_map(stub_cache_path):
    """Default ``include_code_map=False`` returns empty metadata."""
    query = BlsSearchFetcher.transform_query({"category": "cpi", "query": "Food"})
    rows = BlsSearchFetcher.extract_data(query, credentials=None)
    result = BlsSearchFetcher.transform_data(query, rows)
    assert result.metadata == {}
    assert len(result.result) == 1
