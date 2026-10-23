"""Test the BLS fetchers.

Most tests in this module exercise the BLS fetchers through the
``mock_bls_http`` conftest fixture, which monkeypatches every HTTP-touching
helper to return bundled bytes from ``tests/fixtures/``. No cassettes are
recorded for these tests — disk footprint stays under 1 MB regardless of how
the BLS source files grow on bls.gov.

The one exception is ``test_bls_series_fetcher``, which targets the BLS
Public Data API and uses a small recorded cassette (~3 KB).
"""

from datetime import date

import pytest

from openbb_bls.models.ces_analytical_tables import (
    BlsCesConfidenceIntervalsFetcher,
    BlsCesTable1Fetcher,
    BlsCesTable2Fetcher,
    BlsCesTable3AFetcher,
    BlsCesTable3BFetcher,
    BlsCesTable4Fetcher,
    BlsCesTable5Fetcher,
    BlsCesTable6Fetcher,
    BlsCesTable7Fetcher,
)
from openbb_bls.models.cpi_documents import BlsCpiDocumentsFetcher
from openbb_bls.models.cpi_news_release import (
    BlsCpiNrTable1Fetcher,
    BlsCpiNrTable2Fetcher,
    BlsCpiNrTable3Fetcher,
    BlsCpiNrTable4Fetcher,
    BlsCpiNrTable5Fetcher,
    BlsCpiNrTable6Fetcher,
    BlsCpiNrTable7Fetcher,
)
from openbb_bls.models.cpi_relative_importance import BlsCpiRelativeImportanceFetcher
from openbb_bls.models.cpi_seasonal_factors import BlsCpiSeasonalFactorsFetcher
from openbb_bls.models.cpi_supplemental_tables import BlsCpiSupplementalTablesFetcher
from openbb_bls.models.empsit_documents import BlsEmpsitDocumentsFetcher
from openbb_bls.models.jolts_documents import BlsJoltsDocumentsFetcher
from openbb_bls.models.jolts_revisions import BlsJoltsRevisionsFetcher
from openbb_bls.models.jolts_tables import BlsJoltsChangeAnalysisFetcher
from openbb_bls.models.ppi_documents import BlsPpiDocumentsFetcher
from openbb_bls.models.ppi_relative_importance import BlsPpiRelativeImportanceFetcher
from openbb_bls.models.ppi_seasonal_factors import BlsPpiSeasonalFactorsFetcher
from openbb_bls.models.productivity_documents import BlsProductivityDocumentsFetcher
from openbb_bls.models.productivity_tables import BlsProductivityTablesFetcher
from openbb_bls.models.realer_documents import BlsRealerDocumentsFetcher
from openbb_bls.models.search import BlsSearchFetcher
from openbb_bls.models.series import BlsSeriesFetcher
from openbb_bls.models.ximpim_charts import (
    BlsXimpimAirFaresFetcher,
    BlsXimpimExportsByCategoryFetcher,
    BlsXimpimExportsByGrainsFetcher,
    BlsXimpimImportExportFetcher,
    BlsXimpimImportsByCategoryFetcher,
    BlsXimpimImportsByOriginFetcher,
)
from openbb_bls.models.ximpim_documents import BlsXimpimDocumentsFetcher


@pytest.mark.record_http
def test_bls_series_fetcher(test_credentials):
    """Test the BLS Series fetcher (recorded against the BLS Public Data API)."""
    params = {
        "symbol": "APU0000701111",
        "start_date": date(2022, 1, 1),
        "end_date": date(2022, 12, 1),
    }
    result = BlsSeriesFetcher().test(params, test_credentials)
    assert result is None


def test_bls_search_fetcher(test_credentials):
    """Test the BLS Search fetcher — data are local cache, no network needed."""
    params = {"category": "cpi", "query": "average price;flour"}
    result = BlsSearchFetcher().test(params, test_credentials)
    assert result is None


# ---------------------------------------------------------------------------
# Document-listing fetchers — scrape functions return canned in-memory data
# ---------------------------------------------------------------------------

_DOCUMENT_FETCHERS = [
    ("cpi", BlsCpiDocumentsFetcher, {"category": "all"}),
    ("empsit", BlsEmpsitDocumentsFetcher, {"category": "all"}),
    ("realer", BlsRealerDocumentsFetcher, {"category": "all"}),
    ("ximpim", BlsXimpimDocumentsFetcher, {"category": "all"}),
    ("ppi", BlsPpiDocumentsFetcher, {}),
    ("jolts", BlsJoltsDocumentsFetcher, {"category": "all"}),
    ("productivity", BlsProductivityDocumentsFetcher, {"category": "all"}),
]


@pytest.mark.parametrize(
    "label,Fetcher,params",
    _DOCUMENT_FETCHERS,
    ids=[t[0] for t in _DOCUMENT_FETCHERS],
)
def test_document_listing_fetchers(
    label, Fetcher, params, mock_bls_http, test_credentials
):
    """Test BLS *_documents fetchers (canned scrape results, no HTTP)."""
    result = Fetcher().test(params, test_credentials)
    assert result is None


_SINGLE_PROGRAM_DOC_FETCHERS = [
    ("cpi", BlsCpiDocumentsFetcher),
    ("empsit", BlsEmpsitDocumentsFetcher),
    ("realer", BlsRealerDocumentsFetcher),
    ("ximpim", BlsXimpimDocumentsFetcher),
]


@pytest.mark.parametrize(
    "label,Fetcher",
    _SINGLE_PROGRAM_DOC_FETCHERS,
    ids=[t[0] for t in _SINGLE_PROGRAM_DOC_FETCHERS],
)
def test_document_fetcher_category_archived_only(
    label, Fetcher, mock_bls_http, test_credentials
):
    """category=archived excludes the current-release entry."""
    result = Fetcher().test({"category": "archived"}, test_credentials)
    assert result is None


@pytest.mark.parametrize(
    "label,Fetcher",
    _SINGLE_PROGRAM_DOC_FETCHERS,
    ids=[t[0] for t in _SINGLE_PROGRAM_DOC_FETCHERS],
)
def test_document_fetcher_category_current_only(
    label, Fetcher, mock_bls_http, test_credentials
):
    """category=current returns only the always-current PDF."""
    result = Fetcher().test({"category": "current"}, test_credentials)
    assert result is None


@pytest.mark.parametrize(
    "label,Fetcher",
    _SINGLE_PROGRAM_DOC_FETCHERS,
    ids=[t[0] for t in _SINGLE_PROGRAM_DOC_FETCHERS],
)
def test_document_fetcher_date_range_filters(
    label, Fetcher, mock_bls_http, test_credentials
):
    """start_date / end_date filters exclude archived entries outside the window."""
    # Window deliberately excludes the latest mocked archive entry to fire
    # both the start_date and end_date `continue` branches.
    params = {
        "category": "archived",
        "start_date": date(2026, 1, 1),
        "end_date": date(2026, 4, 30),
    }
    result = Fetcher().test(params, test_credentials)
    assert result is None


@pytest.mark.parametrize(
    "label,Fetcher",
    _SINGLE_PROGRAM_DOC_FETCHERS,
    ids=[t[0] for t in _SINGLE_PROGRAM_DOC_FETCHERS],
)
def test_document_fetcher_empty_filter_raises(
    label, Fetcher, mock_bls_http, test_credentials
):
    """A filter that excludes every entry raises EmptyDataError."""
    from openbb_core.provider.utils.errors import EmptyDataError

    params = {
        "category": "archived",
        "start_date": date(2099, 1, 1),
        "end_date": date(2099, 12, 31),
    }
    with pytest.raises(EmptyDataError):
        Fetcher.transform_data(
            Fetcher.transform_query(params),
            Fetcher.extract_data(Fetcher.transform_query(params), test_credentials),
        )


def test_jolts_documents_release_code_filter(mock_bls_http, test_credentials):
    """JOLTS docs honour the release_code filter (jolts vs jltst)."""
    params = {"category": "all", "release_code": "jolts"}
    result = BlsJoltsDocumentsFetcher().test(params, test_credentials)
    assert result is None


def test_jolts_documents_archived_with_filter(mock_bls_http, test_credentials):
    """JOLTS docs category=archived + release_code filter combined."""
    params = {
        "category": "archived",
        "release_code": "jolts",
        "start_date": date(2026, 1, 1),
        "end_date": date(2026, 12, 31),
    }
    result = BlsJoltsDocumentsFetcher().test(params, test_credentials)
    assert result is None


def test_productivity_documents_archived_only(mock_bls_http, test_credentials):
    """Productivity docs with category=archived + release_code + date range."""
    params = {
        "category": "archived",
        "release_code": "prod2",
        "start_date": date(2026, 1, 1),
        "end_date": date(2026, 12, 31),
    }
    result = BlsProductivityDocumentsFetcher().test(params, test_credentials)
    assert result is None


def test_productivity_tables_sector_filter(mock_bls_http, test_credentials):
    """Productivity tables sector filter narrows the row set."""
    params = {
        "dataset": "major-sectors-quarterly",
        "sector": "Nonfarm business sector",
    }
    result = BlsProductivityTablesFetcher().test(params, test_credentials)
    assert result is None


def test_productivity_tables_measure_filter(mock_bls_http, test_credentials):
    """Productivity tables measure filter narrows the row set."""
    params = {
        "dataset": "major-sectors-quarterly",
        "measure": "Labor productivity",
    }
    result = BlsProductivityTablesFetcher().test(params, test_credentials)
    assert result is None


def test_productivity_tables_empty_filter_raises(mock_bls_http, test_credentials):
    """Productivity tables with a filter that excludes everything raises."""
    from openbb_core.provider.utils.errors import EmptyDataError

    params = {
        "dataset": "major-sectors-quarterly",
        "sector": "does-not-exist",
    }
    with pytest.raises(EmptyDataError):
        BlsProductivityTablesFetcher.transform_data(
            BlsProductivityTablesFetcher.transform_query(params),
            BlsProductivityTablesFetcher.extract_data(
                BlsProductivityTablesFetcher.transform_query(params),
                test_credentials,
            ),
        )


def test_productivity_tables_default_scopes_to_headline_series(
    mock_bls_http, test_credentials
):
    """With no overrides the table defaults to a single Nonfarm business series."""
    Fetcher = BlsProductivityTablesFetcher
    rows = Fetcher.extract_data(
        Fetcher.transform_query({"dataset": "major-sectors-quarterly"}),
        test_credentials,
    )
    assert rows
    assert all(r["sector"] == "Nonfarm business sector" for r in rows)
    assert all(r["measure"] == "Labor productivity" for r in rows)
    # Units defaults to the 2017=100 index -> one row per period (no apparent dups).
    assert all(r["units"] == "Index (2017=100)" for r in rows)
    assert len({r["date"] for r in rows}) == len(rows)


def test_productivity_tables_drops_level_not_available(mock_bls_http, test_credentials):
    """The always-blank 'Level - not available' placeholder rows are excluded."""
    Fetcher = BlsProductivityTablesFetcher
    rows = Fetcher.extract_data(
        Fetcher.transform_query({"dataset": "major-sectors-quarterly", "units": None}),
        test_credentials,
    )
    assert rows
    assert all(r["units"] != "Level - not available" for r in rows)


def test_productivity_tables_date_and_units_filters(mock_bls_http, test_credentials):
    """start_date / end_date / units filters each narrow the row set."""
    Fetcher = BlsProductivityTablesFetcher
    # Clear the default sector / measure / units so the whole dataset is in scope.
    base = {
        "dataset": "total-economy-hours-employment",
        "sector": None,
        "measure": None,
        "units": None,
    }

    # start_date drops the earlier (2025 Q4) rows.
    query = Fetcher.transform_query({**base, "start_date": date(2026, 1, 1)})
    rows = Fetcher.extract_data(query, test_credentials)
    assert rows and all(r["date"] >= date(2026, 1, 1) for r in rows)

    # end_date drops the later (2026 Q1) rows.
    query = Fetcher.transform_query({**base, "end_date": date(2025, 12, 31)})
    rows = Fetcher.extract_data(query, test_credentials)
    assert rows and all(r["date"] <= date(2025, 12, 31) for r in rows)

    # units filter keeps only the matching units, dropping the rest.
    query = Fetcher.transform_query({**base, "units": "Billions of hours"})
    rows = Fetcher.extract_data(query, test_credentials)
    assert rows and all(r["units"] == "Billions of hours" for r in rows)


def test_productivity_tables_date_filter_drops_undated_rows(monkeypatch):
    """A date filter drops rows whose parsed date is None (e.g. bad cycle labels)."""
    import openbb_bls.models.productivity_tables as ptm

    monkeypatch.setattr(ptm, "fetch_xlsx", lambda filename: b"ignored")
    monkeypatch.setattr(
        ptm,
        "parse_dataset",
        lambda content, dataset: [
            {
                "date": None,
                "period_kind": "business_cycle",
                "measure": "Labor productivity",
                "units": "Compound annual growth rate",
                "row_index": 1,
                "table_id": "t",
                "table_title": "T",
                "source_file": "f.xlsx",
            },
            {
                "date": date(2026, 1, 1),
                "period_kind": "annual",
                "measure": "Labor productivity",
                "units": "Index",
                "row_index": 2,
                "table_id": "t",
                "table_title": "T",
                "source_file": "f.xlsx",
            },
        ],
    )
    query = ptm.BlsProductivityTablesFetcher.transform_query(
        {
            "dataset": "major-sectors-quarterly",
            "start_date": date(2025, 1, 1),
            "sector": None,
            "measure": None,
            "units": None,
        }
    )
    rows = ptm.BlsProductivityTablesFetcher.extract_data(query, None)
    assert len(rows) == 1 and rows[0]["date"] == date(2026, 1, 1)


_CES_TABLE_FETCHERS = [
    ("t1", BlsCesTable1Fetcher),
    ("t2", BlsCesTable2Fetcher),
    ("t3a", BlsCesTable3AFetcher),
    ("t3b", BlsCesTable3BFetcher),
    ("t4", BlsCesTable4Fetcher),
    ("t5", BlsCesTable5Fetcher),
    ("t6", BlsCesTable6Fetcher),
    ("t7", BlsCesTable7Fetcher),
]


@pytest.mark.parametrize(
    "label,Fetcher", _CES_TABLE_FETCHERS, ids=[t[0] for t in _CES_TABLE_FETCHERS]
)
def test_ces_analytical_table(label, Fetcher, mock_bls_http, test_credentials):
    """Each CES analytical-table fetcher parses its bundled trimmed XLSX."""
    result = Fetcher().test({}, test_credentials)
    assert result is None


def test_ces_confidence_intervals_all(mock_bls_http, test_credentials):
    """CES confidence-interval fetcher returns every sub-table by default."""
    result = BlsCesConfidenceIntervalsFetcher().test({}, test_credentials)
    assert result is None


def test_ces_confidence_intervals_filtered(mock_bls_http, test_credentials):
    """The ci_table filter narrows the confidence-interval rows to one sub-table."""
    Fetcher = BlsCesConfidenceIntervalsFetcher
    query = Fetcher.transform_query({"ci_table": "A"})
    data = Fetcher.extract_data(query, test_credentials)
    assert data["rows"] and all(r["ci_table"] == "A" for r in data["rows"])
    rows = Fetcher.transform_data(query, data)
    assert rows and all(r.ci_table == "A" for r in rows)


def test_ces_confidence_intervals_empty_filter_raises(mock_bls_http, test_credentials):
    """A ci_table value with no matching rows raises EmptyDataError."""
    from openbb_core.provider.utils.errors import EmptyDataError

    Fetcher = BlsCesConfidenceIntervalsFetcher
    query = Fetcher.transform_query({"ci_table": "B1"})
    data = Fetcher.extract_data(query, test_credentials)
    data["rows"] = []
    with pytest.raises(EmptyDataError):
        Fetcher.transform_data(query, data)


_XIMPIM_CHART_FETCHERS = [
    ("import-export", BlsXimpimImportExportFetcher),
    ("imports-by-category", BlsXimpimImportsByCategoryFetcher),
    ("exports-by-category", BlsXimpimExportsByCategoryFetcher),
    ("imports-by-origin", BlsXimpimImportsByOriginFetcher),
    ("exports-by-grains", BlsXimpimExportsByGrainsFetcher),
    ("air-passenger-fares", BlsXimpimAirFaresFetcher),
]


@pytest.mark.parametrize(
    "label,Fetcher", _XIMPIM_CHART_FETCHERS, ids=[t[0] for t in _XIMPIM_CHART_FETCHERS]
)
def test_ximpim_chart(label, Fetcher, mock_bls_http, test_credentials):
    """Each import-export chart table parses its bundled trimmed HTML fixture."""
    result = Fetcher().test({}, test_credentials)
    assert result is None


def test_ximpim_chart_date_filter(mock_bls_http, test_credentials):
    """start_date / end_date bound the chart table's monthly rows."""
    Fetcher = BlsXimpimImportExportFetcher
    query = Fetcher.transform_query(
        {"start_date": date(2006, 5, 1), "end_date": date(2006, 6, 1)}
    )
    rows = Fetcher.extract_data(query, test_credentials)
    assert rows and all(date(2006, 5, 1) <= r["date"] <= date(2006, 6, 1) for r in rows)


def test_ximpim_chart_empty_raises(mock_bls_http, test_credentials):
    """A date window with no data raises EmptyDataError."""
    from openbb_core.provider.utils.errors import EmptyDataError

    Fetcher = BlsXimpimImportExportFetcher
    query = Fetcher.transform_query({"start_date": date(2099, 1, 1)})
    with pytest.raises(EmptyDataError):
        Fetcher.transform_data(query, Fetcher.extract_data(query, test_credentials))


from openbb_bls.models.empsit_charts import (
    EMPSIT_CHART_FETCHERS,
    empsit_model_name,
)
from openbb_bls.utils.empsit_charts import CHART_SPECS as _EMPSIT_SPECS

_EMPSIT_CHART_KEYS = list(_EMPSIT_SPECS)


@pytest.mark.parametrize("chart_key", _EMPSIT_CHART_KEYS)
def test_empsit_chart(chart_key, mock_bls_http, test_credentials):
    """Each Employment Situation chart table parses its bundled HTML fixture."""
    fetcher = EMPSIT_CHART_FETCHERS[empsit_model_name(chart_key)]
    result = fetcher().test({}, test_credentials)
    assert result is None


def test_empsit_chart_timeseries_date_filter(mock_bls_http, test_credentials):
    """A time-series chart honors start_date / end_date bounds."""
    fetcher = EMPSIT_CHART_FETCHERS[empsit_model_name("civilian-unemployment-rate")]
    query = fetcher.transform_query(
        {"start_date": date(2006, 5, 1), "end_date": date(2006, 6, 1)}
    )
    rows = fetcher.extract_data(query, test_credentials)
    assert rows and all(date(2006, 5, 1) <= r["date"] <= date(2006, 6, 1) for r in rows)


from openbb_bls.models.empsit_summary import (
    EMPSIT_SUMMARY_FETCHERS,
    empsit_summary_model_name,
)


@pytest.mark.parametrize("key", ["a", "b"])
def test_empsit_summary_table(key, mock_bls_http, test_credentials):
    """Summary tables A and B parse their bundled HTML fixtures."""
    fetcher = EMPSIT_SUMMARY_FETCHERS[empsit_summary_model_name(key)]
    result = fetcher().test({}, test_credentials)
    assert result is None


def test_empsit_summary_a_has_change_b_does_not(mock_bls_http, test_credentials):
    """Table A rows carry the 1-month change; table B rows do not."""
    a = EMPSIT_SUMMARY_FETCHERS[empsit_summary_model_name("a")]
    rows_a = a.extract_data(a.transform_query({}), test_credentials)
    assert rows_a and any(r.get("change_1_month") is not None for r in rows_a)
    b = EMPSIT_SUMMARY_FETCHERS[empsit_summary_model_name("b")]
    rows_b = b.extract_data(b.transform_query({}), test_credentials)
    assert rows_b and all(r.get("change_1_month") is None for r in rows_b)


def test_empsit_chart_industry_has_no_date(mock_bls_http, test_credentials):
    """An industry cross-section chart keys rows by industry, not date."""
    fetcher = EMPSIT_CHART_FETCHERS[
        empsit_model_name("employment-by-industry-monthly-changes")
    ]
    rows = fetcher.extract_data(fetcher.transform_query({}), test_credentials)
    assert rows and "industry" in rows[0] and "date" not in rows[0]


def test_empsit_chart_empty_raises(mock_bls_http, test_credentials):
    """A time-series chart with no rows in the window raises EmptyDataError."""
    from openbb_core.provider.utils.errors import EmptyDataError

    fetcher = EMPSIT_CHART_FETCHERS[empsit_model_name("civilian-unemployment-rate")]
    query = fetcher.transform_query({"start_date": date(2099, 1, 1)})
    with pytest.raises(EmptyDataError):
        fetcher.transform_data(query, fetcher.extract_data(query, test_credentials))


from openbb_bls.models.productivity_charts import (
    PRODUCTIVITY_CHART_FETCHERS,
    productivity_model_name,
)
from openbb_bls.utils.productivity_charts import CHART_SPECS as _PRODUCTIVITY_SPECS

_PRODUCTIVITY_CHART_KEYS = list(_PRODUCTIVITY_SPECS)


@pytest.mark.parametrize("chart_key", _PRODUCTIVITY_CHART_KEYS)
def test_productivity_chart(chart_key, mock_bls_http, test_credentials):
    """Each Productivity and Costs chart table parses its bundled HTML fixture."""
    fetcher = PRODUCTIVITY_CHART_FETCHERS[productivity_model_name(chart_key)]
    result = fetcher().test({}, test_credentials)
    assert result is None


def test_productivity_chart_timeseries_date_filter(mock_bls_http, test_credentials):
    """A quarterly time-series chart honors start_date / end_date bounds."""
    fetcher = PRODUCTIVITY_CHART_FETCHERS[
        productivity_model_name("nonfarm-business-indexes")
    ]
    query = fetcher.transform_query(
        {"start_date": date(2017, 4, 1), "end_date": date(2017, 7, 1)}
    )
    rows = fetcher.extract_data(query, test_credentials)
    assert rows and all(date(2017, 4, 1) <= r["date"] <= date(2017, 7, 1) for r in rows)


def test_productivity_chart_sector_has_no_date(mock_bls_http, test_credentials):
    """The sector cross-section chart keys rows by measure, not date."""
    fetcher = PRODUCTIVITY_CHART_FETCHERS[productivity_model_name("by-sector")]
    rows = fetcher.extract_data(fetcher.transform_query({}), test_credentials)
    assert rows and "measure" in rows[0] and "date" not in rows[0]


def test_productivity_chart_empty_raises(mock_bls_http, test_credentials):
    """A time-series chart with no rows in the window raises EmptyDataError."""
    from openbb_core.provider.utils.errors import EmptyDataError

    fetcher = PRODUCTIVITY_CHART_FETCHERS[
        productivity_model_name("nonfarm-business-indexes")
    ]
    query = fetcher.transform_query({"start_date": date(2099, 1, 1)})
    with pytest.raises(EmptyDataError):
        fetcher.transform_data(query, fetcher.extract_data(query, test_credentials))


from openbb_bls.models.cpi_charts import (
    CPI_CHART_FETCHERS,
    cpi_model_name,
)
from openbb_bls.utils.cpi_charts import CHART_SPECS as _CPI_SPECS

_CPI_CHART_KEYS = list(_CPI_SPECS)


@pytest.mark.parametrize("chart_key", _CPI_CHART_KEYS)
def test_cpi_chart(chart_key, mock_bls_http, test_credentials):
    """Each Consumer Price Index chart table parses its bundled HTML fixture."""
    fetcher = CPI_CHART_FETCHERS[cpi_model_name(chart_key)]
    result = fetcher().test({}, test_credentials)
    assert result is None


def test_cpi_chart_timeseries_date_filter(mock_bls_http, test_credentials):
    """A monthly time-series chart honors start_date / end_date bounds."""
    fetcher = CPI_CHART_FETCHERS[cpi_model_name("by-category-line")]
    query = fetcher.transform_query(
        {"start_date": date(2006, 5, 1), "end_date": date(2006, 6, 1)}
    )
    rows = fetcher.extract_data(query, test_credentials)
    assert rows and all(date(2006, 5, 1) <= r["date"] <= date(2006, 6, 1) for r in rows)


def test_cpi_chart_category_has_no_date(mock_bls_http, test_credentials):
    """The category cross-section chart keys rows by category, not date."""
    fetcher = CPI_CHART_FETCHERS[cpi_model_name("by-category")]
    rows = fetcher.extract_data(fetcher.transform_query({}), test_credentials)
    assert rows and "category" in rows[0] and "date" not in rows[0]


def test_cpi_chart_empty_raises(mock_bls_http, test_credentials):
    """A time-series chart with no rows in the window raises EmptyDataError."""
    from openbb_core.provider.utils.errors import EmptyDataError

    fetcher = CPI_CHART_FETCHERS[cpi_model_name("by-category-line")]
    query = fetcher.transform_query({"start_date": date(2099, 1, 1)})
    with pytest.raises(EmptyDataError):
        fetcher.transform_data(query, fetcher.extract_data(query, test_credentials))


from openbb_bls.models.ppi_charts import (
    PPI_CHART_FETCHERS,
    ppi_model_name,
)
from openbb_bls.utils.ppi_charts import CHART_SPECS as _PPI_SPECS

_PPI_CHART_KEYS = list(_PPI_SPECS)


@pytest.mark.parametrize("chart_key", _PPI_CHART_KEYS)
def test_ppi_chart(chart_key, mock_bls_http, test_credentials):
    """Each Producer Price Index chart table parses its bundled HTML fixture."""
    fetcher = PPI_CHART_FETCHERS[ppi_model_name(chart_key)]
    result = fetcher().test({}, test_credentials)
    assert result is None


def test_ppi_chart_timeseries_date_filter(mock_bls_http, test_credentials):
    """A monthly time-series chart honors start_date / end_date bounds."""
    fetcher = PPI_CHART_FETCHERS[ppi_model_name("final-demand-1m")]
    query = fetcher.transform_query(
        {"start_date": date(2010, 1, 1), "end_date": date(2010, 2, 1)}
    )
    rows = fetcher.extract_data(query, test_credentials)
    assert rows and all(date(2010, 1, 1) <= r["date"] <= date(2010, 2, 1) for r in rows)


def test_ppi_chart_commodity_has_no_date(mock_bls_http, test_credentials):
    """The commodity cross-section chart keys rows by commodity, not date."""
    fetcher = PPI_CHART_FETCHERS[ppi_model_name("final-demand-components-1m")]
    rows = fetcher.extract_data(fetcher.transform_query({}), test_credentials)
    assert rows and "commodity" in rows[0] and "date" not in rows[0]


def test_ppi_chart_empty_raises(mock_bls_http, test_credentials):
    """A time-series chart with no rows in the window raises EmptyDataError."""
    from openbb_core.provider.utils.errors import EmptyDataError

    fetcher = PPI_CHART_FETCHERS[ppi_model_name("final-demand-1m")]
    query = fetcher.transform_query({"start_date": date(2099, 1, 1)})
    with pytest.raises(EmptyDataError):
        fetcher.transform_data(query, fetcher.extract_data(query, test_credentials))


from openbb_bls.models.mining_manufacturing_charts import (
    MINING_MANUFACTURING_CHART_FETCHERS,
    mining_manufacturing_model_name,
)
from openbb_bls.models.tfp_charts import TFP_CHART_FETCHERS, tfp_model_name
from openbb_bls.models.wholesale_retail_charts import (
    WHOLESALE_RETAIL_CHART_FETCHERS,
    wholesale_retail_model_name,
)
from openbb_bls.utils.mining_manufacturing_charts import CHART_SPECS as _MM_SPECS
from openbb_bls.utils.tfp_charts import CHART_SPECS as _TFP_SPECS
from openbb_bls.utils.wholesale_retail_charts import CHART_SPECS as _WR_SPECS

_NEW_PACK_CHARTS = (
    [(TFP_CHART_FETCHERS, tfp_model_name, k) for k in _TFP_SPECS]
    + [
        (WHOLESALE_RETAIL_CHART_FETCHERS, wholesale_retail_model_name, k)
        for k in _WR_SPECS
    ]
    + [
        (MINING_MANUFACTURING_CHART_FETCHERS, mining_manufacturing_model_name, k)
        for k in _MM_SPECS
    ]
)


@pytest.mark.parametrize(
    "fetchers,name_fn,chart_key",
    _NEW_PACK_CHARTS,
    ids=[k for _, _, k in _NEW_PACK_CHARTS],
)
def test_new_productivity_chart(
    fetchers, name_fn, chart_key, mock_bls_http, test_credentials
):
    """Each TFP / wholesale-retail / mining-mfg chart parses its bundled fixture."""
    fetcher = fetchers[name_fn(chart_key)]
    result = fetcher().test({}, test_credentials)
    assert result is None


def test_tfp_chart_timeseries_date_filter(mock_bls_http, test_credentials):
    """A TFP annual-index trend chart honors start_date / end_date bounds."""
    fetcher = TFP_CHART_FETCHERS[tfp_model_name("tfp-ict-trends")]
    query = fetcher.transform_query(
        {"start_date": date(1987, 1, 1), "end_date": date(1988, 1, 1)}
    )
    rows = fetcher.extract_data(query, test_credentials)
    assert rows and all(date(1987, 1, 1) <= r["date"] <= date(1988, 1, 1) for r in rows)


def test_tfp_chart_industry_cross_section(mock_bls_http, test_credentials):
    """A TFP industry cross-section keys rows by industry, not date."""
    fetcher = TFP_CHART_FETCHERS[tfp_model_name("tfp-combined-inputs-output")]
    rows = fetcher.extract_data(fetcher.transform_query({}), test_credentials)
    assert rows and "industry" in rows[0] and "date" not in rows[0]


def test_wholesale_retail_period_cross_section(mock_bls_http, test_credentials):
    """The wholesale/retail by-period chart keys rows by period, not date."""
    fetcher = WHOLESALE_RETAIL_CHART_FETCHERS[
        wholesale_retail_model_name("wr-productivity-by-period")
    ]
    rows = fetcher.extract_data(fetcher.transform_query({}), test_credentials)
    assert rows and "period" in rows[0] and "date" not in rows[0]


def test_mining_manufacturing_chart_empty_raises(mock_bls_http, test_credentials):
    """A ts chart with no rows in the window raises EmptyDataError."""
    from openbb_core.provider.utils.errors import EmptyDataError

    fetcher = MINING_MANUFACTURING_CHART_FETCHERS[
        mining_manufacturing_model_name("mm-indexes-by-industry")
    ]
    query = fetcher.transform_query({"start_date": date(2099, 1, 1)})
    with pytest.raises(EmptyDataError):
        fetcher.transform_data(query, fetcher.extract_data(query, test_credentials))


from openbb_bls.models.jolts_charts import (
    JOLTS_CHART_FETCHERS,
    jolts_chart_model_name,
)
from openbb_bls.utils.jolts_charts import CHART_SPECS as _JOLTS_SPECS

_JOLTS_CHART_KEYS = list(_JOLTS_SPECS)


@pytest.mark.parametrize("chart_key", _JOLTS_CHART_KEYS)
def test_jolts_chart(chart_key, mock_bls_http, test_credentials):
    """Each JOLTS chart table parses its bundled HTML fixture."""
    fetcher = JOLTS_CHART_FETCHERS[jolts_chart_model_name(chart_key)]
    result = fetcher().test({}, test_credentials)
    assert result is None


def test_jolts_chart_timeseries_date_filter(mock_bls_http, test_credentials):
    """A JOLTS monthly chart honors start_date / end_date bounds."""
    fetcher = JOLTS_CHART_FETCHERS[jolts_chart_model_name("unemp-per-opening")]
    query = fetcher.transform_query(
        {"start_date": date(2011, 3, 1), "end_date": date(2011, 4, 1)}
    )
    rows = fetcher.extract_data(query, test_credentials)
    assert rows and all(date(2011, 3, 1) <= r["date"] <= date(2011, 4, 1) for r in rows)


def test_jolts_chart_empty_raises(mock_bls_http, test_credentials):
    """A JOLTS chart with no rows in the window raises EmptyDataError."""
    from openbb_core.provider.utils.errors import EmptyDataError

    fetcher = JOLTS_CHART_FETCHERS[jolts_chart_model_name("beveridge-curve")]
    query = fetcher.transform_query({"start_date": date(2099, 1, 1)})
    with pytest.raises(EmptyDataError):
        fetcher.transform_data(query, fetcher.extract_data(query, test_credentials))


def test_bls_apps_json_endpoint():
    """The /bls/apps.json endpoint serves a valid dashboard with no legacy widget IDs."""
    import asyncio

    from openbb_bls.bls_router import bls_apps

    apps = asyncio.run(bls_apps())
    assert isinstance(apps, list) and apps
    # The main app is first and carries the release-calendar + search tabs
    # (matched structurally so app renames don't break the test).
    assert "release-calendar" in apps[0]["tabs"]
    assert "search-series" in apps[0]["tabs"]
    import json

    blob = json.dumps(apps)
    for legacy in ("bls_ces_", "bls_empsit", "bls_realer", "bls_ximpim"):
        assert legacy not in blob, f"stale widget token {legacy!r} left in apps.json"


def test_bls_apps_search_series_tab_is_install_aware():
    """The Search & Series tab uses Economy-namespaced or standalone IDs per install."""
    import asyncio

    import openbb_bls.bls_router as br

    def _main(apps):
        return next(a for a in apps if "search-series" in a["tabs"])

    def _ss_ids(apps):
        return [w["i"] for w in _main(apps)["tabs"]["search-series"]["layout"]]

    original = br.ECONOMY_INSTALLED
    try:
        br.ECONOMY_INSTALLED = True
        econ = asyncio.run(br.bls_apps())
        assert _ss_ids(econ) == [
            "economy_survey_bls_search_bls_obb",
            "economy_survey_bls_series_bls_obb",
        ]
        br.ECONOMY_INSTALLED = False
        standalone = asyncio.run(br.bls_apps())
        assert _ss_ids(standalone) == ["bls_search_bls_obb", "bls_series_bls_obb"]
        # paramName-linked groups carry no widgetIds and must survive the
        # standalone rewrite untouched (no empty widgetIds injected).
        for group in _main(standalone)["groups"]:
            assert "widgetIds" not in group
    finally:
        br.ECONOMY_INSTALLED = original


def test_bls_apps_employment_situation_split():
    """Employment Situation is its own app entry with dedicated section tabs."""
    import asyncio

    from openbb_bls.bls_router import bls_apps

    apps = asyncio.run(bls_apps())
    # The crowded tab is no longer part of the main BLS app.
    assert "employment-situation" not in apps[0]["tabs"]
    # A dedicated Employment Situation app entry now exists (matched by its
    # tab signature so app renames don't break the test).
    es = next(a for a in apps if "industry-employment" in a["tabs"])
    assert set(es["tabs"]) == {
        "documents",
        "summary-tables",
        "unemployment",
        "labor-force",
        "industry-employment",
        "analytical-tables",
    }
    # Every widget across its tabs stays in the employment_situation namespace,
    # and the 31 source widgets are preserved with no duplication.
    widget_ids = [w["i"] for tab in es["tabs"].values() for w in tab["layout"]]
    assert len(widget_ids) == len(set(widget_ids)) == 31
    assert all(wid.startswith("bls_employment_situation_") for wid in widget_ids)


def test_bls_apps_cpi_split():
    """CPI is its own app entry with dedicated section tabs incl. the chart pack."""
    import asyncio

    from openbb_bls.bls_router import bls_apps

    apps = asyncio.run(bls_apps())
    # The crowded tab is no longer part of the main BLS app.
    assert "cpi" not in apps[0]["tabs"]
    cpi = next(a for a in apps if "news-release-tables" in a["tabs"])
    assert set(cpi["tabs"]) == {
        "documents",
        "news-release-tables",
        "reference-tables",
        "charts",
    }
    # The chart pack lands on the Charts tab and is chart-active.
    chart_ids = [w["i"] for w in cpi["tabs"]["charts"]["layout"]]
    assert len(chart_ids) == 5
    assert all(
        w["state"]["chartView"]["enabled"] is True
        for w in cpi["tabs"]["charts"]["layout"]
    )
    # All 16 CPI widgets stay in the cpi namespace with no duplication.
    widget_ids = [w["i"] for tab in cpi["tabs"].values() for w in tab["layout"]]
    assert len(widget_ids) == len(set(widget_ids)) == 16
    assert all(wid.startswith("bls_cpi_") for wid in widget_ids)


def test_bls_apps_ppi_split():
    """PPI is its own app entry with dedicated section tabs incl. the chart packs."""
    import asyncio

    from openbb_bls.bls_router import bls_apps

    apps = asyncio.run(bls_apps())
    assert "ppi" not in apps[0]["tabs"]
    ppi = next(a for a in apps if "final-demand" in a["tabs"])
    assert set(ppi["tabs"]) == {
        "documents",
        "detailed-report",
        "reference-tables",
        "final-demand",
        "intermediate-demand",
    }
    # Final- and intermediate-demand chart packs are chart-active.
    chart_widgets = (
        ppi["tabs"]["final-demand"]["layout"]
        + ppi["tabs"]["intermediate-demand"]["layout"]
    )
    assert len(chart_widgets) == 10
    assert all(w["state"]["chartView"]["enabled"] is True for w in chart_widgets)
    # All 14 PPI widgets stay in the ppi namespace with no duplication.
    widget_ids = [w["i"] for tab in ppi["tabs"].values() for w in tab["layout"]]
    assert len(widget_ids) == len(set(widget_ids)) == 14
    assert all(wid.startswith("bls_ppi_") for wid in widget_ids)


def test_bls_apps_productivity_split():
    """Productivity is its own app entry with a section tab per chart package."""
    import asyncio

    from openbb_bls.bls_router import bls_apps

    apps = asyncio.run(bls_apps())
    assert "productivity" not in apps[0]["tabs"]
    prod = next(a for a in apps if "total-factor-productivity" in a["tabs"])
    assert set(prod["tabs"]) == {
        "documents",
        "tables",
        "labor-productivity-costs",
        "total-factor-productivity",
        "wholesale-retail",
        "mining-manufacturing",
    }
    # The four chart packs together contribute 8 + 6 + 7 + 6 = 27 chart widgets.
    chart_tabs = (
        "labor-productivity-costs",
        "total-factor-productivity",
        "wholesale-retail",
        "mining-manufacturing",
    )
    chart_count = sum(len(prod["tabs"][t]["layout"]) for t in chart_tabs)
    assert chart_count == 27
    widget_ids = [w["i"] for tab in prod["tabs"].values() for w in tab["layout"]]
    assert len(widget_ids) == len(set(widget_ids)) == 29
    assert all(wid.startswith("bls_productivity_") for wid in widget_ids)


def test_productivity_documents_choices_filters(mock_bls_http):
    """The file-selector choices endpoint honors release_code / start_date / end_date."""
    import asyncio

    from openbb_bls.routers.productivity import document_choices as choices

    # Both archived releases (prod2 @ 2026-05-07, prod3 @ 2026-03-19).
    all_docs = asyncio.run(choices(category="archived"))
    assert len(all_docs) == 2
    # start_date drops the older prod3 release.
    dated = asyncio.run(choices(category="archived", start_date="2026-04-01"))
    assert len(dated) == 1 and "prod2" in dated[0]["value"]
    # end_date drops the newer prod2 release.
    capped = asyncio.run(choices(category="archived", end_date="2026-04-01"))
    assert len(capped) == 1 and "prod3" in capped[0]["value"]
    # release_code narrows to a single program.
    coded = asyncio.run(choices(category="archived", release_code="prod3"))
    assert len(coded) == 1 and "prod3" in coded[0]["value"]
    # Empty-string params are ignored (treated as unset).
    assert len(asyncio.run(choices(category="archived", start_date=""))) == 2


def test_empsit_documents_choices_date_filter(mock_bls_http):
    """The Employment Situation choices endpoint applies the date bounds."""
    import asyncio

    from openbb_bls.routers.ces import document_choices as choices

    unfiltered = asyncio.run(choices(category="archived"))
    future = asyncio.run(choices(category="archived", start_date="2099-01-01"))
    assert len(future) < len(unfiltered)


def test_jolts_revisions_measure_filter(mock_bls_http, test_credentials):
    """JOLTS revisions measure filter narrows the rows."""
    params = {
        "seasonally_adjusted": True,
        "industry_code": "00",
        "measure": "Hires",
    }
    result = BlsJoltsRevisionsFetcher().test(params, test_credentials)
    assert result is None


def test_jolts_revisions_empty_filter_raises(mock_bls_http, test_credentials):
    """JOLTS revisions with a non-matching industry raises EmptyDataError."""
    from openbb_core.provider.utils.errors import EmptyDataError

    params = {
        "seasonally_adjusted": True,
        "industry_code": "ZZ",
    }
    with pytest.raises(EmptyDataError):
        BlsJoltsRevisionsFetcher.transform_data(
            BlsJoltsRevisionsFetcher.transform_query(params),
            BlsJoltsRevisionsFetcher.extract_data(
                BlsJoltsRevisionsFetcher.transform_query(params),
                test_credentials,
            ),
        )


_CPI_SUPP_TABLES = [
    "c-cpi-u",
    "cpi-u-us",
    "cpi-u-regional",
    "cpi-w",
    "historical-cpi-u-index",
    "historical-cpi-u-averages",
]


@pytest.mark.parametrize("table_key", _CPI_SUPP_TABLES)
def test_cpi_supplemental_tables_explicit_date(
    table_key, mock_bls_http, test_credentials
):
    """CPI Supplemental Tables with an explicit `date` query parameter.

    Each table family resolves through the patched fetch_xlsx to its own
    minimal bundled XLSX fixture, so every one is exercised end-to-end.
    """
    params = {"table": table_key, "date": date(2026, 4, 1)}
    result = BlsCpiSupplementalTablesFetcher().test(params, test_credentials)
    assert result is None


_CPI_NR_TABLES = [
    ("t1", BlsCpiNrTable1Fetcher),
    ("t2", BlsCpiNrTable2Fetcher),
    ("t3", BlsCpiNrTable3Fetcher),
    ("t4", BlsCpiNrTable4Fetcher),
    ("t5", BlsCpiNrTable5Fetcher),
    ("t6", BlsCpiNrTable6Fetcher),
    ("t7", BlsCpiNrTable7Fetcher),
]


@pytest.mark.parametrize(
    "label,Fetcher", _CPI_NR_TABLES, ids=[t[0] for t in _CPI_NR_TABLES]
)
def test_cpi_news_release_table(label, Fetcher, mock_bls_http, test_credentials):
    """Test each of the 7 CPI News Release Table fetchers."""
    result = Fetcher().test({"date": date(2026, 4, 1)}, test_credentials)
    assert result is None


def test_cpi_supplemental_tables_fetcher(mock_bls_http, test_credentials):
    """Test BLS CPI Supplemental Tables (pinned to c-cpi-u fixture)."""
    params = {"table": "c-cpi-u"}
    result = BlsCpiSupplementalTablesFetcher().test(params, test_credentials)
    assert result is None


def test_cpi_relative_importance_fetcher(mock_bls_http, test_credentials):
    """Test BLS CPI Relative Importance fetcher (bundled 2025 XLSX)."""
    result = BlsCpiRelativeImportanceFetcher().test({"table": 1}, test_credentials)
    assert result is None


def test_cpi_seasonal_factors_fetcher(mock_bls_http, test_credentials):
    """Test BLS CPI Seasonal Factors fetcher (bundled 2025 XLSX)."""
    result = BlsCpiSeasonalFactorsFetcher().test({}, test_credentials)
    assert result is None


# ---------------------------------------------------------------------------
# PPI fetchers — bundled XLSX + HTML fixtures
# ---------------------------------------------------------------------------


def test_ppi_relative_importance_fetcher(mock_bls_http, test_credentials):
    """Test BLS PPI Relative Importance fetcher (bundled ppi-fdallrel XLSX)."""
    params = {"category": "final_demand"}
    result = BlsPpiRelativeImportanceFetcher().test(params, test_credentials)
    assert result is None


def test_ppi_seasonal_factors_fetcher(mock_bls_http, test_credentials):
    """Test BLS PPI Seasonal Factors fetcher (bundled ppi-seafac HTML)."""
    params = {"category": "forecast"}
    result = BlsPpiSeasonalFactorsFetcher().test(params, test_credentials)
    assert result is None


_JOLTS_CHANGE_ANALYSIS = [
    ("national_t1", "national", 1),
    ("state_t1", "state", 1),
]


@pytest.mark.parametrize(
    "label,scope,table_number",
    _JOLTS_CHANGE_ANALYSIS,
    ids=[t[0] for t in _JOLTS_CHANGE_ANALYSIS],
)
def test_jolts_change_analysis_fetcher(
    label, scope, table_number, mock_bls_http, test_credentials
):
    """Test BLS JOLTS Change-Analysis fetcher (sampled — national + state)."""
    params = {"scope": scope, "table_number": table_number}
    result = BlsJoltsChangeAnalysisFetcher().test(params, test_credentials)
    assert result is None


@pytest.mark.parametrize("seasonally_adjusted", [True, False])
def test_jolts_revisions_fetcher(seasonally_adjusted, mock_bls_http, test_credentials):
    """Test BLS JOLTS Revisions fetcher (mini SA/NSA XLSX fixtures)."""
    params = {"seasonally_adjusted": seasonally_adjusted, "industry_code": "00"}
    result = BlsJoltsRevisionsFetcher().test(params, test_credentials)
    assert result is None


@pytest.mark.parametrize(
    "dataset",
    [
        "major-sectors-quarterly",
        "major-sectors-annual",
        "major-sectors-business-cycles",
        "total-economy-hours-employment",
    ],
)
def test_productivity_tables_fetcher(dataset, mock_bls_http, test_credentials):
    """Test BLS Productivity Tables fetcher (mini prod2 fixtures)."""
    # Clear the default sector / measure / units so every dataset's raw parse is
    # exercised (the total-economy workbook shares none of those defaults).
    params = {
        "dataset": dataset,
        "sector": None,
        "measure": None,
        "units": None,
    }
    result = BlsProductivityTablesFetcher().test(params, test_credentials)
    assert result is None
