"""Tests for the BLS PPI Detailed Report fetcher and XLSX parser."""

from __future__ import annotations

from datetime import date as _date
from pathlib import Path

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

import openbb_bls.models.ppi_detailed_report as ppi_dr_mod
from openbb_bls.models.ppi_detailed_report import (
    BlsPpiDetailedReportData,
    BlsPpiDetailedReportFetcher,
    BlsPpiDetailedReportQueryParams,
    _build_code,
    _classify_header_pair,
    _clean_header,
    _coerce_number,
    _detect_columns,
    _discover_latest,
    _fetch_month_xlsx,
    _inherit_from_stack,
    _month_from_token,
    _month_url,
    _parse_table,
    _parse_table_footnotes,
    _period_label_to_date,
    _resolve_label_footnotes,
    _row_to_records,
    _strip_footnote_marker,
)

_FIXTURES = Path(__file__).parent / "fixtures"
_TRIMMED_FIXTURE = _FIXTURES / "ppi_detailed_report_trimmed.xlsx"
_FIXTURE_BYTES = _TRIMMED_FIXTURE.read_bytes()


class _FakeResponse:
    """Minimal ``requests.Response`` stand-in for unit tests."""

    def __init__(self, content: bytes, status_code: int = 200):
        self.content = content
        self.status_code = status_code

    def raise_for_status(self) -> None:
        """No-op."""


def _patch_fetch_xlsx(monkeypatch, payload: bytes | None) -> None:
    """Replace ``_fetch_month_xlsx`` at the model binding to return ``payload``."""
    monkeypatch.setattr(ppi_dr_mod, "_fetch_month_xlsx", lambda year, month: payload)


@pytest.mark.parametrize("table_number", list(range(1, 15)))
def test_fetcher_all_tables(monkeypatch, table_number, test_credentials):
    """Every one of the 14 PPI Detailed Report tables parses end-to-end."""
    _patch_fetch_xlsx(monkeypatch, _FIXTURE_BYTES)
    params = {"date": _date(2026, 4, 1), "table": table_number}
    out = BlsPpiDetailedReportFetcher().test(params, test_credentials)
    assert out is None


def test_fetcher_returns_validated_rows(monkeypatch, test_credentials):
    """The full pipeline yields ``BlsPpiDetailedReportData`` rows."""
    _patch_fetch_xlsx(monkeypatch, _FIXTURE_BYTES)
    params = {"date": _date(2026, 4, 1), "table": 1}
    q = BlsPpiDetailedReportFetcher.transform_query(params)
    raw = BlsPpiDetailedReportFetcher.extract_data(q, test_credentials)
    out = BlsPpiDetailedReportFetcher.transform_data(q, raw)
    assert out
    assert all(isinstance(r, BlsPpiDetailedReportData) for r in out)
    assert all(r.table_number == 1 for r in out)
    assert all(r.release_period == "April 2026" for r in out)


def test_query_params_defaults():
    """``date`` defaults to ``None``, ``table`` defaults to 1."""
    q = BlsPpiDetailedReportQueryParams()
    assert q.date is None
    assert q.table == 1


def test_query_params_date_too_early_raises_via_extract(monkeypatch, test_credentials):
    """Requesting a pre-2022 month surfaces as ``OpenBBError``."""
    _patch_fetch_xlsx(monkeypatch, _FIXTURE_BYTES)
    q = BlsPpiDetailedReportFetcher.transform_query(
        {"date": _date(2021, 12, 1), "table": 1}
    )
    with pytest.raises(OpenBBError, match="January 2022 onward"):
        BlsPpiDetailedReportFetcher.extract_data(q, test_credentials)


def test_extract_data_explicit_date_missing_xlsx_raises(monkeypatch, test_credentials):
    """An explicit date with no published XLSX raises ``OpenBBError``."""
    _patch_fetch_xlsx(monkeypatch, None)
    q = BlsPpiDetailedReportFetcher.transform_query(
        {"date": _date(2026, 4, 1), "table": 1}
    )
    with pytest.raises(OpenBBError, match="no PPI Detailed Report XLSX"):
        BlsPpiDetailedReportFetcher.extract_data(q, test_credentials)


def test_extract_data_no_date_uses_discover_latest(monkeypatch, test_credentials):
    """``date=None`` routes through ``_discover_latest``."""

    def _fake_discover():
        return 2026, 4, _FIXTURE_BYTES

    monkeypatch.setattr(ppi_dr_mod, "_discover_latest", _fake_discover)
    q = BlsPpiDetailedReportFetcher.transform_query({"table": 2})
    raw = BlsPpiDetailedReportFetcher.extract_data(q, test_credentials)
    assert raw["table_id"] == "ppi-dr-2026-04-t2"


def test_transform_data_empty_raises():
    """An empty ``rows`` list raises ``EmptyDataError`` with the table id."""
    q = BlsPpiDetailedReportFetcher.transform_query(
        {"date": _date(2026, 4, 1), "table": 1}
    )
    with pytest.raises(EmptyDataError, match="some-table-id"):
        BlsPpiDetailedReportFetcher.transform_data(
            q, {"rows": [], "table_id": "some-table-id"}
        )


def test_transform_data_missing_table_id_uses_placeholder():
    """An empty ``rows`` with no ``table_id`` falls back to ``'?'``."""
    q = BlsPpiDetailedReportFetcher.transform_query(
        {"date": _date(2026, 4, 1), "table": 1}
    )
    with pytest.raises(EmptyDataError, match=r"'\?'"):
        BlsPpiDetailedReportFetcher.transform_data(q, {})


def test_parse_table_unknown_sheet_raises():
    """``_parse_table`` raises when the sheet name is missing from the workbook."""
    with pytest.raises(OpenBBError, match="does not contain sheet 'Table 99'"):
        _parse_table(_FIXTURE_BYTES, 99, 2026, 4)


def test_month_url_format():
    """``_month_url`` emits the canonical BLS XLSX URL."""
    url = _month_url(2026, 4)
    assert (
        url == "https://www.bls.gov/ppi/detailed-report/"
        "ppi-detailed-report-april-2026.xlsx"
    )


@pytest.mark.parametrize("status_code", [301, 302, 303, 307, 308, 404])
def test_fetch_month_xlsx_redirect_or_404_returns_none(monkeypatch, status_code):
    """3xx redirects and 404s collapse to ``None`` (file isn't published)."""
    monkeypatch.setattr(
        "requests.get",
        lambda *a, **k: _FakeResponse(b"<html>", status_code=status_code),
    )
    assert _fetch_month_xlsx(2026, 4) is None


def test_fetch_month_xlsx_non_200_raises(monkeypatch):
    """A surprise non-redirect non-200 raises ``OpenBBError``."""
    monkeypatch.setattr(
        "requests.get",
        lambda *a, **k: _FakeResponse(b"server error", status_code=500),
    )
    with pytest.raises(OpenBBError, match="HTTP 500"):
        _fetch_month_xlsx(2026, 4)


def test_fetch_month_xlsx_non_xlsx_magic_returns_none(monkeypatch):
    """A 200 response that isn't a real XLSX (no PK magic) collapses to ``None``."""
    monkeypatch.setattr(
        "requests.get",
        lambda *a, **k: _FakeResponse(b"<html>not xlsx</html>"),
    )
    assert _fetch_month_xlsx(2026, 4) is None


def test_fetch_month_xlsx_xlsx_magic_returns_content(monkeypatch):
    """A 200 response that starts with the PK magic returns its content."""
    body = b"PK\x03\x04" + b"\x00" * 32
    monkeypatch.setattr("requests.get", lambda *a, **k: _FakeResponse(body))
    assert _fetch_month_xlsx(2026, 4) == body


def test_discover_latest_walks_back_on_misses(monkeypatch):
    """``_discover_latest`` tolerates 2 missing months before the hit."""
    calls: list[tuple[int, int]] = []

    def _fake_fetch(year, month):
        calls.append((year, month))
        if len(calls) <= 2:
            return None
        return _FIXTURE_BYTES

    monkeypatch.setattr(ppi_dr_mod, "_fetch_month_xlsx", _fake_fetch)
    year, month, content = _discover_latest()
    assert content == _FIXTURE_BYTES
    assert len(calls) == 3


def test_discover_latest_year_rollover(monkeypatch):
    """``_discover_latest`` rolls the year back when month decrements past January."""

    class _Today:
        @staticmethod
        def today():
            return _date(2026, 1, 15)

    monkeypatch.setattr(ppi_dr_mod, "dateType", _Today)

    calls: list[tuple[int, int]] = []

    def _fake_fetch(year, month):
        calls.append((year, month))
        if (year, month) == (2025, 12):
            return _FIXTURE_BYTES
        return None

    monkeypatch.setattr(ppi_dr_mod, "_fetch_month_xlsx", _fake_fetch)
    year, month, _content = _discover_latest()
    assert (year, month) == (2025, 12)
    assert calls[0] == (2026, 1)
    assert calls[1] == (2025, 12)


def test_discover_latest_exhausts_window_raises(monkeypatch):
    """Six consecutive misses raise ``OpenBBError``."""
    monkeypatch.setattr(ppi_dr_mod, "_fetch_month_xlsx", lambda y, m: None)
    with pytest.raises(OpenBBError, match="Could not locate"):
        _discover_latest()


# --- Helper-level coverage ------------------------------------------------


def test_inherit_from_stack_walks_shallower_levels():
    """``_inherit_from_stack`` returns the nearest shallower non-None value."""
    stack = {
        0: {"industry_code": "1133", "group_code": None},
        1: {"industry_code": None, "group_code": None},
        2: {"industry_code": "113310", "group_code": None},
    }
    assert _inherit_from_stack(stack, 3, "industry_code") == "113310"
    assert _inherit_from_stack(stack, 2, "industry_code") == "1133"
    assert _inherit_from_stack(stack, 1, "industry_code") == "1133"
    assert _inherit_from_stack(stack, 0, "industry_code") is None
    assert _inherit_from_stack(stack, 3, "group_code") is None


def test_inherit_from_stack_empty_entry():
    """Missing levels in the stack are skipped silently."""
    assert _inherit_from_stack({}, 5, "industry_code") is None
    assert _inherit_from_stack({2: None}, 5, "industry_code") is None  # type: ignore[dict-item]


def test_parse_table_footnotes_skips_until_header():
    """Footnote definitions before the ``Footnotes:`` header are ignored."""
    rows = [
        ("", "(1) Stray pre-header text", None),
        ("", "Footnotes:", None),
        ("", "(1) Real first footnote.", None),
        ("", "(2) Real second footnote.", None),
        ("", "(p) Preliminary", None),
        ("", "non-matching free text", None),
        ("", None, None),
        (None,),
    ]
    out = _parse_table_footnotes(rows)
    assert out == {
        "(1)": "Real first footnote.",
        "(2)": "Real second footnote.",
        "(p)": "Preliminary",
    }


def test_parse_table_footnotes_empty_body_keeps_full_text():
    """A footnote definition with an empty body falls back to the full cell text."""
    rows = [
        ("", "Footnotes:", None),
        ("", "(1)  ", None),
    ]
    out = _parse_table_footnotes(rows)
    assert out == {"(1)": "(1)"}


def test_parse_table_footnotes_ignores_non_string_and_short_rows():
    """Non-string cells, short rows, and empty rows are skipped."""
    out = _parse_table_footnotes(
        [
            (),
            ("only-one",),
            ("", 12345, None),
            ("", "   ", None),
            ("", "Footnotes:", None),
            ("", "no-paren-prefix", None),
            ("", "(7) Valid footnote.", None),
        ]
    )
    assert out == {"(7)": "Valid footnote."}


def test_resolve_label_footnotes_picks_unique_matches():
    """``_resolve_label_footnotes`` resolves markers, dedupes, and joins them."""
    fn = {"(1)": "First note.", "(3)": "Third note."}
    assert _resolve_label_footnotes("Total finished(3)", fn) == "Third note."
    assert _resolve_label_footnotes("Foo(1)(3)(1)", fn) == "First note.\n\nThird note."


def test_resolve_label_footnotes_returns_none_when_no_match():
    """Markers absent from the legend produce ``None``."""
    fn = {"(1)": "x"}
    assert _resolve_label_footnotes("Foo(99)", fn) is None
    assert _resolve_label_footnotes("Foo (plain)", fn) is None


def test_resolve_label_footnotes_empty_inputs():
    """An empty label or empty footnote dict short-circuits to ``None``."""
    assert _resolve_label_footnotes(None, {"(1)": "x"}) is None
    assert _resolve_label_footnotes("", {"(1)": "x"}) is None
    assert _resolve_label_footnotes("Foo(1)", {}) is None


def test_build_code_precedence_product_first():
    """``product_code`` outranks every other field."""
    assert (
        _build_code(
            {
                "product_code": "PROD",
                "industry_code": "IND",
                "group_code": "G",
                "item_code": "I",
            }
        )
        == "PROD"
    )


def test_build_code_group_plus_item_concatenated():
    """``group_code + item_code`` produces a concatenated key when both present."""
    assert _build_code({"group_code": "FD", "item_code": "4111"}) == "FD4111"


def test_build_code_industry_fallback():
    """``industry_code`` alone is returned when product/group+item are absent."""
    assert _build_code({"industry_code": "1133"}) == "1133"


def test_build_code_group_alone():
    """``group_code`` alone is returned when neither item nor industry is present."""
    assert _build_code({"group_code": "FD"}) == "FD"


def test_build_code_item_alone():
    """``item_code`` alone is returned as a last resort."""
    assert _build_code({"item_code": "999"}) == "999"


def test_build_code_returns_none_for_empty_record():
    """An empty record yields ``None``."""
    assert _build_code({}) is None


def test_clean_header_collapses_whitespace_and_newlines():
    """``_clean_header`` collapses newlines and runs of whitespace."""
    assert _clean_header("Relative\nImportance   Dec.\n2025(1)") == (
        "Relative Importance Dec. 2025(1)"
    )
    assert _clean_header(None) == ""
    assert _clean_header(123) == "123"


def test_strip_footnote_marker_removes_trailing_paren_token():
    """Trailing ``(N)`` or ``(p)`` markers are stripped from header labels."""
    assert _strip_footnote_marker("Apr. 2026(p)") == "Apr. 2026"
    assert _strip_footnote_marker("Index Value(1)") == "Index Value"
    assert _strip_footnote_marker("Nothing here") == "Nothing here"


def test_month_from_token_handles_abbr_full_and_sept():
    """``_month_from_token`` recognises ``Apr``, ``April``, ``Sept`` and trailing dots."""
    assert _month_from_token("Apr") == 4
    assert _month_from_token("Apr.") == 4
    assert _month_from_token("April") == 4
    assert _month_from_token("Sept") == 9
    assert _month_from_token("september") == 9
    assert _month_from_token("???") is None


def test_period_label_to_date_single_form():
    """A single-month label like ``Apr. 2026(p)`` parses to that calendar month."""
    assert _period_label_to_date("Apr.\n2026(p)", 2026, 4, is_range=False) == _date(
        2026, 4, 1
    )


def test_period_label_to_date_single_form_no_match():
    """A label that doesn't match the single-form regex returns ``None``."""
    assert _period_label_to_date("garbage", 2026, 4, is_range=False) is None


def test_period_label_to_date_single_form_unknown_month():
    """A single-form label with a bogus month token returns ``None``."""
    assert _period_label_to_date("Xyz 2026", 2026, 4, is_range=False) is None


def test_period_label_to_date_range_form_with_year():
    """A range label that includes the trailing year parses that year."""
    assert _period_label_to_date(
        "Apr. 2025\nto\nApr. 2026(p)", 2026, 4, is_range=True
    ) == _date(2026, 4, 1)


def test_period_label_to_date_range_form_without_year_current_year():
    """A range label without an explicit year and month <= report_month -> report year."""
    assert _period_label_to_date("Feb. to\nMar.(p)", 2026, 4, is_range=True) == _date(
        2026, 3, 1
    )


def test_period_label_to_date_range_form_without_year_prior_year():
    """A range label without an explicit year and month > report_month -> prior year."""
    assert _period_label_to_date("Nov. to\nDec.", 2026, 4, is_range=True) == _date(
        2025, 12, 1
    )


def test_period_label_to_date_range_form_no_match():
    """A range label that doesn't match the regex returns ``None``."""
    assert _period_label_to_date("noop", 2026, 4, is_range=True) is None


def test_period_label_to_date_range_form_unknown_month():
    """A range label with an unrecognised month token returns ``None``."""
    assert _period_label_to_date("to\nXyz 2026", 2026, 4, is_range=True) is None


def test_period_label_to_date_none_input():
    """A ``None`` label produces ``None``."""
    assert _period_label_to_date(None, 2026, 4, is_range=False) is None


def test_coerce_number_passthrough_and_sentinels():
    """``_coerce_number`` returns float for numerics, ``None`` for BLS sentinels."""
    assert _coerce_number(None) is None
    assert _coerce_number(5) == 5.0
    assert _coerce_number(2.5) == 2.5
    assert _coerce_number("3.14") == 3.14
    for sentinel in ("", "-", "(NA)", "–"):
        assert _coerce_number(sentinel) is None
    assert _coerce_number("not-a-number") is None


def test_detect_columns_no_header_returns_empty():
    """No ``Indent Level`` cell in any row yields an empty classification list."""
    classifications, idx = _detect_columns(
        [(), (None, None), ("Not the header", "Group code")]
    )
    assert classifications == []
    assert idx == 0


def test_detect_columns_sub_row_missing_at_end_of_rows():
    """``_detect_columns`` tolerates a header on the final row (empty sub-row)."""
    rows = [("Indent Level", "Grouping", "Group code")]
    classifications, idx = _detect_columns(rows)
    assert idx == 2
    assert classifications[0] == ("indent", None)
    assert classifications[1] == ("label", None)
    assert classifications[2] == ("group_code", None)


def test_classify_header_pair_covers_every_branch():
    """``_classify_header_pair`` recognises every kind of column the parser uses."""
    super_row = (
        "Indent Level",
        "Grouping",
        "Commodity code",
        None,
        "Other index base",
        "Relative Importance Dec. 2025(1)",
        "Unadjusted 12-month percent change(2)",
        "Seasonally adjusted 1-month percent change(2)",
        "Unadjusted 1-month percent change(2)",
        "Seasonally adjusted index(1)",
        "Unadjusted index(1)",
        "Industry code",
        "Product code",
        "Title(1)",
        "completely unknown column",
    )
    sub_row = (
        None,
        None,
        "Group code",
        "Item code",
        None,
        None,
        "Apr. 2025\nto\nApr. 2026(p)",
        "Mar. to\nApr.(p)",
        "Mar. to\nApr.(p)",
        "Apr.\n2026(p)",
        "Apr.\n2026(p)",
        None,
        None,
        None,
        None,
    )
    out = _classify_header_pair(super_row, sub_row)
    kinds = [o[0] for o in out]
    assert kinds == [
        "indent",
        "label",
        "group_code",
        "item_code",
        "other_index_base",
        "relative_importance",
        "pct_change_12m",
        "pct_change_1m_sa",
        "pct_change_1m_nsa",
        "index_sa",
        "index_nsa",
        "industry_code",
        "product_code",
        "label",
        "skip",
    ]
    rel_importance = next(o for o in out if o[0] == "relative_importance")
    assert rel_importance[1] == "Dec. 2025"
    pct_12m = next(o for o in out if o[0] == "pct_change_12m")
    assert pct_12m[1] == "Apr. 2025 to Apr. 2026"


def test_classify_header_pair_sub_row_only_codes():
    """Sub-row ``industry code``/``product code`` tokens classify when the super-row text doesn't claim them."""
    super_row = (
        "Indent Level",
        "Title",
        "Other Index Base",
        "Codes",
        "Codes",
    )
    sub_row = (None, None, None, "industry code", "product code")
    out = _classify_header_pair(super_row, sub_row)
    kinds = [o[0] for o in out]
    assert kinds == [
        "indent",
        "label",
        "other_index_base",
        "industry_code",
        "product_code",
    ]


def test_row_to_records_skips_empty_and_unparseable_indent():
    """A blank row or non-integer indent returns no records."""
    classifications = [("indent", None), ("label", None)]
    assert _row_to_records((), classifications, 2026, 4) == []
    assert _row_to_records((None, "x"), classifications, 2026, 4) == []
    assert _row_to_records(("not-int", "x"), classifications, 2026, 4) == []


def test_row_to_records_no_periods_no_label_returns_empty():
    """A row with no parseable periods and no label/code yields nothing."""
    classifications = [
        ("indent", None),
        ("label", None),
        ("index_nsa", "Apr. 2026"),
    ]
    out = _row_to_records((0, None, None), classifications, 2026, 4)
    assert out == []


def test_row_to_records_label_only_no_periods_returns_empty():
    """A label-only row with no numeric periods yields no records."""
    classifications = [("indent", None), ("label", None)]
    out = _row_to_records((0, "Header label"), classifications, 2026, 4)
    assert out == []


def test_row_to_records_skip_kind_passes_through():
    """Columns classified as ``skip`` never contribute to the output record."""
    classifications = [
        ("indent", None),
        ("label", None),
        ("skip", None),
        ("index_nsa", "Apr. 2026"),
    ]
    out = _row_to_records((0, "Foo", "DROP-ME", 99.5), classifications, 2026, 4)
    assert len(out) == 1
    assert out[0]["index_value"] == 99.5
    assert out[0]["label"] == "Foo"


def test_row_to_records_value_with_bad_period_label_dropped():
    """Numeric cells whose period header is unparseable get silently dropped."""
    classifications = [
        ("indent", None),
        ("label", None),
        ("index_nsa", "not-a-month"),
    ]
    out = _row_to_records((0, "Foo", 1.0), classifications, 2026, 4)
    assert out == []


def test_row_to_records_blank_string_in_cell_treated_as_missing():
    """Whitespace-only strings are skipped during classification."""
    classifications = [
        ("indent", None),
        ("label", None),
        ("index_nsa", "Apr. 2026"),
    ]
    out = _row_to_records((0, "Foo", "   "), classifications, 2026, 4)
    assert out == []


def test_row_to_records_label_takes_only_first_value():
    """A second label column doesn't overwrite an already-captured label."""
    classifications = [
        ("indent", None),
        ("label", None),
        ("label", None),
        ("index_nsa", "Apr. 2026"),
    ]
    out = _row_to_records((0, "First", "Second", 12.5), classifications, 2026, 4)
    assert out[0]["label"] == "First"


def test_row_to_records_non_string_codes_ignored():
    """Numeric values in code columns are ignored — those slots expect strings."""
    classifications = [
        ("indent", None),
        ("group_code", None),
        ("item_code", None),
        ("industry_code", None),
        ("product_code", None),
        ("label", None),
        ("index_nsa", "Apr. 2026"),
    ]
    out = _row_to_records((0, 999, 999, 999, 999, "Foo", 1.5), classifications, 2026, 4)
    assert out[0]["group_code"] is None
    assert out[0]["item_code"] is None
    assert out[0]["industry_code"] is None
    assert out[0]["product_code"] is None
    assert out[0]["code"] is None
    assert out[0]["label"] == "Foo"


def test_row_to_records_truncates_classifications_to_row_length():
    """``classifications`` longer than the row are silently truncated."""
    classifications = [
        ("indent", None),
        ("label", None),
        ("index_nsa", "Apr. 2026"),
        ("index_nsa", "Mar. 2026"),
    ]
    out = _row_to_records((0, "Foo", 1.0), classifications, 2026, 4)
    assert len(out) == 1
    assert out[0]["index_value"] == 1.0


def test_row_to_records_relative_importance_and_other_base():
    """``relative_importance`` and ``other_index_base`` flow into the record."""
    classifications = [
        ("indent", None),
        ("label", None),
        ("other_index_base", None),
        ("relative_importance", "Dec. 2025"),
    ]
    out = _row_to_records((0, "Foo", "12/14", 25.5), classifications, 2026, 4)
    assert out[0]["other_index_base"] == "12/14"
    assert out[0]["relative_importance"] == 25.5


def test_row_to_records_unrecognised_value_kind_is_dropped():
    """A classification kind outside ``_VALUE_KINDS`` doesn't produce a value slot."""
    classifications = [
        ("indent", None),
        ("label", None),
        ("mystery", "Apr. 2026"),
        ("index_nsa", "Apr. 2026"),
    ]
    out = _row_to_records((0, "Foo", 999, 1.5), classifications, 2026, 4)
    assert len(out) == 1
    assert out[0]["index_value"] == 1.5


def test_row_to_records_values_without_label_or_code_dropped():
    """A row with numeric periods but neither label nor any code is dropped."""
    classifications = [
        ("indent", None),
        ("skip", None),
        ("index_nsa", "Apr. 2026"),
    ]
    out = _row_to_records((0, "ignored", 12.5), classifications, 2026, 4)
    assert out == []


def test_row_to_records_unparseable_number_dropped():
    """Numeric cells that can't be coerced to float are dropped silently."""
    classifications = [
        ("indent", None),
        ("label", None),
        ("index_nsa", "Apr. 2026"),
        ("index_nsa", "Mar. 2026"),
    ]
    out = _row_to_records((0, "Foo", "not-a-number", 1.0), classifications, 2026, 4)
    assert len(out) == 1
    assert out[0]["date"] == _date(2026, 3, 1)


# --- Data serialiser ------------------------------------------------------


def test_data_label_hovercard_serializer_with_footnote():
    """``label`` JSON-serialises as a hover-card when ``footnote`` is set."""
    row = BlsPpiDetailedReportData(
        date=_date(2026, 4, 1),
        label="Finished consumer foods",
        footnote="Footnote text.",
        table_id="ppi-dr-2026-04-t1",
        table_name="t",
        table_number=1,
        release_period="April 2026",
    )
    dumped = row.model_dump(mode="json")
    assert dumped["label"] == {
        "value": "Finished consumer foods",
        "footnote": "Footnote text.",
    }


def test_data_label_passes_through_without_footnote():
    """Without a footnote, ``label`` JSON-serialises as a bare string."""
    row = BlsPpiDetailedReportData(
        date=_date(2026, 4, 1),
        label="Goods",
        table_id="ppi-dr-2026-04-t1",
        table_name="t",
        table_number=1,
        release_period="April 2026",
    )
    dumped = row.model_dump(mode="json")
    assert dumped["label"] == "Goods"


def test_data_label_none_with_footnote_returns_none():
    """A null label short-circuits the hover-card wrapper."""
    row = BlsPpiDetailedReportData(
        date=_date(2026, 4, 1),
        label=None,
        footnote="x",
        table_id="ppi-dr-2026-04-t1",
        table_name="t",
        table_number=1,
        release_period="April 2026",
    )
    dumped = row.model_dump(mode="json")
    assert dumped["label"] is None
