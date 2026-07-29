"""Unit tests for ``openbb_sec.utils.non_xbrl_parser``."""

from bs4 import BeautifulSoup

from openbb_sec.utils.non_xbrl_parser import (
    _build_meta_dataframe,
    _build_statement_dataframe,
    _clean_cell_text,
    _clean_html_entities,
    _clean_paragraph_text,
    _convert_sgml_tables,
    _detect_multiplier,
    _extract_8k_items,
    _extract_block_line_items,
    _extract_bullet_list,
    _extract_items_sgml,
    _extract_period_ending,
    _extract_periods,
    _extract_sgml_periods,
    _extract_simple_table,
    _extract_table_data,
    _extract_table_subtitle,
    _extract_text_blocks_sgml,
    _extract_toc_from_table,
    _extract_toc_sgml,
    _find_best_sgml_table,
    _find_notes_in_section,
    _get_8k_item_name,
    _get_direct_text,
    _get_item_default_name,
    _get_negative_keywords,
    _get_statement_keywords,
    _is_bullet_table,
    _is_financial_table,
    _is_header_row,
    _is_section_header,
    _is_sgml_content,
    _parse_data_row,
    _parse_html_table_for_notes,
    _parse_number,
    _parse_sgml_statement,
    _parse_sgml_value,
    _sgml_to_text,
    _table_to_markdown_notes,
    extract_items,
    extract_plain_text_notes,
    extract_text_blocks,
    extract_toc,
    find_all_statements,
    get_statement_names,
    parse_non_xbrl_statement,
)


def _soup(html: str):
    """Build a BeautifulSoup tree from an HTML fragment."""
    return BeautifulSoup(html, "html.parser")


def _first_table(html: str):
    """Return the first <table> element from an HTML fragment."""
    return _soup(html).find("table")


INCOME_TABLE_HTML = """
<table>
<tr><td>Statements of Operations</td><td></td><td></td></tr>
<tr><td>In millions</td><td></td><td></td></tr>
<tr><td>Year Ended June 30</td><td>2002</td><td>2001</td></tr>
<tr><td>Total revenues</td><td>$1,234</td><td>$1,100</td></tr>
<tr><td>Cost of revenue</td><td>500</td><td>450</td></tr>
<tr><td>Gross profit:</td></tr>
<tr><td>Operating expenses</td><td>200</td><td>180</td></tr>
<tr><td>Net income</td><td>534</td><td>470</td></tr>
<tr><td>Net loss</td><td>(14</td><td>)</td></tr>
<tr><td>Diluted per share</td><td>1.23</td><td>1.10</td></tr>
<tr><td>Shares outstanding</td><td>100,000,001</td><td>99,000,001</td></tr>
</table>
"""


_SGML_FILLER = "Body prose line that pads out the section content.\n" * 12

SGML_FILING = (
    "<PAGE>\n"
    "PART I\n\n"
    "ITEM 1.  FINANCIAL STATEMENTS                                          1\n"
    "ITEM 2.  MANAGEMENT'S DISCUSSION AND ANALYSIS                         10\n"
    "ITEM 3.  QUANTITATIVE DISCLOSURES                                     20\n"
    "ITEM 4.  CONTROLS AND PROCEDURES                                      25\n"
    + "\n" * 4
    + _SGML_FILLER
    + "ITEM 1.  FINANCIAL STATEMENTS\n\n"
    "CONSOLIDATED STATEMENTS OF OPERATIONS\n"
    "(In thousands)\n\n"
    "                                            December 31,    December 31,\n"
    "                                                1993            1992\n"
    "<TABLE>\n"
    "<CAPTION>\n"
    "                                            December 31,    December 31,\n"
    "                                                1993            1992\n"
    "<S>                                         <C>             <C>\n"
    "Total revenues                              $12,340         $11,000\n"
    "Cost of revenue                              5,000           4,500\n"
    "Operating costs:\n"
    "   Selling expense                           2,000           1,800\n"
    "Net income                                   5,340           4,700\n"
    "                                            -------         -------\n"
    "                                            $50,000         $40,000\n"
    "</TABLE>\n\n"
    + _SGML_FILLER
    + "ITEM 2.  MANAGEMENT'S DISCUSSION AND ANALYSIS\n\n"
    + _SGML_FILLER
    + "PART II\n\n"
    "ITEM 1.  LEGAL PROCEEDINGS\n\n" + _SGML_FILLER
)


def test_get_statement_keywords_known_and_default():
    assert "net income" in _get_statement_keywords("income")
    assert "balance sheet" in _get_statement_keywords("balance")
    assert _get_statement_keywords("unknown") == _get_statement_keywords("income")


def test_get_negative_keywords_known_and_default():
    assert "cash flows" in _get_negative_keywords("income")
    # Common negatives (Selected Financial Data / segment tables) apply to all.
    assert "selected financial data" in _get_negative_keywords("income")
    assert _get_negative_keywords("nope") == [
        "selected financial data",
        "selected consolidated financial data",
        "unit sales",
        "unit shipment",
    ]


def test_detect_multiplier_all_scales():
    assert _detect_multiplier(
        _first_table("<table><tr><td>in millions</td></tr></table>")
    ) == (
        1_000_000,
        "millions",
    )
    assert _detect_multiplier(
        _first_table("<table><tr><td>(thousands)</td></tr></table>")
    ) == (1_000, "thousands")
    assert _detect_multiplier(
        _first_table("<table><tr><td>in billions</td></tr></table>")
    ) == (1_000_000_000, "billions")
    assert _detect_multiplier(
        _first_table("<table><tr><td>nothing</td></tr></table>")
    ) == (
        1,
        "units",
    )


def test_clean_cell_text_collapses_whitespace():
    cell = _first_table("<table><tr><td>  a   b  </td></tr></table>").find("td")
    assert _clean_cell_text(cell) == "a b"


def test_parse_number_variants():
    assert _parse_number("1,234") == 1234.0
    assert _parse_number("(50)") == -50.0
    assert _parse_number("3.14") == 3.14
    assert _parse_number("") is None
    assert _parse_number("abc") is None


def test_parse_data_row_basic_and_negatives_and_padding():
    basic = _parse_data_row(["Revenue", "$", "1,000", "2,000"], 2)
    assert basic is not None
    label, values, skip = basic
    assert label == "Revenue"
    assert values == [1000.0, 2000.0]
    assert skip is False

    neg = _parse_data_row(["Net loss", "(14", ")"], 2)
    assert neg is not None
    _, vals, _ = neg
    assert vals[0] == -14.0
    assert vals[1] is None  # padded


def test_parse_data_row_pending_negative_invalid_then_label():
    parsed = _parse_data_row(["(abc", "100"], 1)
    assert parsed is not None
    label, values, _ = parsed
    assert label == "(abc"
    assert values == [100.0]


def test_parse_data_row_per_share_and_share_count_skip_multiplier():
    eps = _parse_data_row(["Diluted EPS", "1.23"], 1)
    assert eps is not None
    assert eps[2] is True
    shares = _parse_data_row(["Shares outstanding", "1,000,000"], 1)
    assert shares is not None
    assert shares[2] is True


def test_parse_data_row_rejections():
    assert _parse_data_row([], 1) is None
    assert _parse_data_row(["$", "—", "-"], 1) is None  # no label, no values
    assert _parse_data_row(["x" * 101, "1"], 1) is None  # label too long
    assert _parse_data_row(["Basic 474,712 shares", "1"], 1) is None  # embedded data
    assert _parse_data_row(["LabelOnly"], 1) is None  # no values


def test_parse_data_row_truncates_extra_values():
    parsed = _parse_data_row(["Revenue", "1", "2", "3"], 2)
    assert parsed is not None
    _, values, _ = parsed
    assert values == [1.0, 2.0]


def test_is_header_row_detection():
    assert _is_header_row("year ended june 30", ["Year Ended June 30"]) is True
    assert _is_header_row("foo 2001 2002", ["2001", "2002"]) is True
    assert _is_header_row("revenue 100 200", ["Revenue", "100", "200"]) is False


def test_is_header_row_multiple_years_not_standalone():
    row_text = "growth from 2001 to 2002 was strong indeed"
    cells = ["growth from 2001 to 2002 was strong indeed"]
    assert _is_header_row(row_text, cells) is False


def test_extract_periods_prefix_and_years():
    html = """
    <table>
    <tr><td>Three Months Ended May</td><td>Six Months Ended May</td></tr>
    <tr><td>1999</td><td>1998</td><td>1999</td><td>1998</td></tr>
    </table>
    """
    rows = _first_table(html).find_all("tr")
    periods = _extract_periods(rows)
    assert any("1999" in p for p in periods)


def test_extract_periods_column_headers():
    html = """
    <table>
    <tr><td>Description</td><td>Gross Carrying Amount</td><td>Net Value</td></tr>
    </table>
    """
    rows = _first_table(html).find_all("tr")
    periods = _extract_periods(rows)
    assert "Gross Carrying Amount" in periods or "Net Value" in periods


def test_extract_periods_years_only():
    html = "<table><tr><td>Label</td><td>2001</td><td>2000</td></tr></table>"
    rows = _first_table(html).find_all("tr")
    assert _extract_periods(rows) == ["2001", "2000"]


def test_extract_periods_empty():
    html = "<table><tr><td></td></tr></table>"
    rows = _first_table(html).find_all("tr")
    assert _extract_periods(rows) == []


def test_extract_periods_skip_huge_row():
    cells = "".join("<td>x</td>" for _ in range(51))
    html = f"<table><tr>{cells}</tr><tr><td>Label</td><td>2001</td><td>2000</td></tr></table>"
    rows = _first_table(html).find_all("tr")
    assert _extract_periods(rows) == ["2001", "2000"]


def test_extract_table_data_too_few_rows():
    html = "<table><tr><td>a</td></tr></table>"
    assert _extract_table_data(_first_table(html)) is None


def test_extract_table_data_full():
    result = _extract_table_data(_first_table(INCOME_TABLE_HTML))
    assert result is not None
    line_items, periods, multiplier, _title = result
    assert multiplier == 1_000_000
    labels = [li["label"] for li in line_items]
    assert "Cost of revenue" in labels
    assert any(li["section"] == "Gross profit" for li in line_items)


def test_extract_table_data_no_periods_fallback_to_cols():
    html = """
    <table>
    <tr><td>Revenue</td><td>100</td><td>200</td></tr>
    <tr><td>Costs</td><td>50</td><td>60</td></tr>
    <tr><td>Income</td><td>50</td><td>140</td></tr>
    <tr><td>Other</td><td>10</td><td>20</td></tr>
    <tr><td>Total</td><td>60</td><td>160</td></tr>
    </table>
    """
    result = _extract_table_data(_first_table(html))
    assert result is not None
    _, periods, _, _ = result
    assert periods == ["Col 1", "Col 2"]


def test_extract_table_data_value_fallback():
    rows = "".join(f"<tr><td>Item {i}</td><td>x</td></tr>" for i in range(6))
    html = f"<table>{rows}</table>"
    result = _extract_table_data(_first_table(html))
    assert result is None  # no values -> no line items


def test_extract_table_data_skip_oversized_row():
    big = "".join("<td>1</td>" for _ in range(60))
    html = (
        "<table>"
        f"<tr>{big}</tr>"
        "<tr><td>Revenue</td><td>100</td><td>200</td></tr>"
        "<tr><td>Costs</td><td>50</td><td>60</td></tr>"
        "<tr><td>Income</td><td>50</td><td>140</td></tr>"
        "<tr><td>Net</td><td>40</td><td>120</td></tr>"
        "<tr><td>Total</td><td>90</td><td>260</td></tr>"
        "</table>"
    )
    result = _extract_table_data(_first_table(html))
    assert result is not None


def test_clean_html_entities():
    text = "Smith&#146;s &amp; Co. &nbsp; &mdash; &bull; &unknown; &#999;"
    out = _clean_html_entities(text)
    assert "&" not in out or out.count("&") == 1
    assert "Smith's" in out


def test_clean_paragraph_text_rejections_and_pass():
    assert _clean_paragraph_text("") is None
    assert _clean_paragraph_text("123") is None
    assert _clean_paragraph_text("abc") is None  # too short
    assert _clean_paragraph_text("(UNAUDITED)") is None
    assert _clean_paragraph_text("Section (Continued)") is None
    assert _clean_paragraph_text("text PAGEBREAK here") is None
    assert _clean_paragraph_text("page 12") is None
    assert _clean_paragraph_text("19991998 garbled") is None
    assert _clean_paragraph_text("$100$200 garbled") is None
    assert _clean_paragraph_text("$1 $2 $3 $4 too many") is None
    assert (
        _clean_paragraph_text("This is a real sentence.") == "This is a real sentence."
    )


def test_get_direct_text():
    html = "<div>Direct <b>bold</b><p>nested ignored</p></div>"
    div = _soup(html).find("div")
    out = _get_direct_text(div)
    assert "Direct" in out
    assert "bold" in out
    assert "nested" not in out


def test_is_section_header():
    header = _soup("<p><b>Significant Policies</b></p>").find("p")
    assert _is_section_header(header) is True

    numbered = _soup("<p><b>1. Former Partner</b></p>").find("p")
    assert _is_section_header(numbered) is False

    multi = _soup("<p><b>a</b><b>b</b></p>").find("p")
    assert _is_section_header(multi) is False

    not_only = _soup("<p>extra<b>Bold Heading Text</b></p>").find("p")
    assert _is_section_header(not_only) is False


def test_is_bullet_table_and_extract():
    html = """
    <table>
    <tr><td>•</td><td>First bullet point here</td></tr>
    <tr><td>•</td><td>Second bullet point here</td></tr>
    </table>
    """
    table = _first_table(html)
    assert _is_bullet_table(table) is True
    out = _extract_bullet_list(table)
    assert out is not None
    assert "First bullet point" in out
    assert out.startswith("- ")


def test_is_bullet_table_false_and_extract_none():
    html = "<table><tr><td>Revenue</td><td>100</td></tr></table>"
    table = _first_table(html)
    assert _is_bullet_table(table) is False
    assert _extract_bullet_list(table) is None


def test_is_financial_table():
    fin = _first_table("<table><tr><td>1,234 5,678 9,012</td></tr></table>")
    assert _is_financial_table(fin) is True
    plain = _first_table("<table><tr><td>no numbers here</td></tr></table>")
    assert _is_financial_table(plain) is False


def test_extract_simple_table():
    html = """
    <table>
    <tr><td>Name</td><td>Value</td></tr>
    <tr><td>Foo</td><td>Bar</td></tr>
    </table>
    """
    out = _extract_simple_table(_first_table(html))
    assert out is not None
    assert "Name | Value" in out
    assert "Foo | Bar" in out


def test_extract_simple_table_no_rows_and_single_row():
    assert _extract_simple_table(_first_table("<table></table>")) is None
    single = "<table><tr><td>only</td></tr></table>"
    assert _extract_simple_table(_first_table(single)) is None


def test_extract_simple_table_skips_nested():
    html = """
    <table>
    <tr><td>A</td><td>B</td></tr>
    <tr><td><table><tr><td>nested</td></tr></table></td><td>visible</td></tr>
    </table>
    """
    out = _extract_simple_table(_first_table(html))
    assert out is not None
    assert "A | B" in out


def test_extract_period_ending_variants():
    assert _extract_period_ending("Year Ended June 30 2003") == "2003-06-30"
    assert _extract_period_ending("2003 fiscal year ending in February") == "2003-02-28"
    assert _extract_period_ending("2003 fiscal year ending in April") == "2003-04-30"
    assert _extract_period_ending("2003 fiscal year ending in March") == "2003-03-31"
    assert _extract_period_ending("Fiscal 2003") == "2003-12-31"
    assert _extract_period_ending("no year here") is None


def test_build_statement_dataframe_units():
    items = [
        {
            "label": "Revenue",
            "section": "Top",
            "values": [100.0, 200.0],
            "skip_multiplier": False,
        },
        {
            "label": "Diluted earnings per share",
            "section": None,
            "values": [1.5],
            "skip_multiplier": True,
        },
        {
            "label": "Shares outstanding",
            "section": None,
            "values": [1000.0],
            "skip_multiplier": True,
        },
    ]
    df = _build_statement_dataframe(items, ["2002", "2001"], 1_000_000)
    assert (df["unit"] == "USD").any()
    assert (df["unit"] == "USD/shares").any()
    assert (df["unit"] == "shares").any()
    rev = df[df["label"] == "Revenue"].iloc[0]
    assert rev["value"] == 100_000_000.0


def test_build_statement_dataframe_none_label():
    items = [
        {"label": None, "section": None, "values": [None], "skip_multiplier": False}
    ]
    df = _build_statement_dataframe(items, ["2002"], 1)
    assert df.iloc[0]["unit"] == "USD"


def test_build_meta_dataframe_scales():
    assert (
        _build_meta_dataframe("T", ["2002"], 1_000_000_000).iloc[0]["scale"]
        == "billions"
    )
    assert (
        _build_meta_dataframe("T", ["2002"], 1_000_000).iloc[0]["scale"] == "millions"
    )
    assert _build_meta_dataframe("T", ["2002"], 1_000).iloc[0]["scale"] == "thousands"
    assert _build_meta_dataframe(None, ["2002"], 1).iloc[0]["scale"] == "units"


def test_parse_non_xbrl_statement_income():
    df, meta = parse_non_xbrl_statement(INCOME_TABLE_HTML, "income")
    assert not df.empty
    assert meta.iloc[0]["scale"] == "millions"


def test_parse_non_xbrl_statement_no_table():
    df, meta = parse_non_xbrl_statement("<html><body>nothing</body></html>", "income")
    assert df.empty
    assert meta.empty


def test_parse_non_xbrl_statement_toc_penalty_skipped():
    html = """
    <table>
    <tr><td>Statements of income page no</td><td>item 1:</td></tr>
    <tr><td>x</td><td>1</td></tr>
    </table>
    """
    df, _ = parse_non_xbrl_statement(html, "income")
    assert df.empty


def test_parse_non_xbrl_statement_too_few_numbers_skipped():
    html = """
    <table>
    <tr><td>Statements of operations net income</td><td>1</td><td>2</td></tr>
    </table>
    """
    df, _ = parse_non_xbrl_statement(html, "income")
    assert df.empty


def test_parse_non_xbrl_statement_bonus_scores():
    rows = "".join(
        f"<tr><td>Line item label {i}</td><td>$</td><td>1,000</td>"
        f"<td>$</td><td>2,000</td></tr>"
        for i in range(20)
    )
    html = (
        "<table>"
        "<tr><td>Statements of operations net income total revenues</td></tr>"
        "<tr><td>in millions</td></tr>"
        f"{rows}"
        "</table>"
    )
    df, meta = parse_non_xbrl_statement(html, "income")
    assert not df.empty


def test_find_all_statements():
    results = find_all_statements(INCOME_TABLE_HTML)
    assert "income" in results


def test_get_statement_names():
    names = get_statement_names()
    assert names["income"].startswith("Consolidated")
    assert set(names) == {"income", "balance", "cash", "equity"}


def test_is_sgml_content():
    assert _is_sgml_content("<PAGE>\nsome text") is True
    assert _is_sgml_content("<S>   <C>") is True
    assert _is_sgml_content("<html><body>x</body></html>") is False
    assert _is_sgml_content("<PAGE><div>x</div>") is False


def test_sgml_to_text_and_convert_tables():
    out = _sgml_to_text(SGML_FILING)
    assert "FINANCIAL STATEMENTS" in out
    assert "<TABLE>" not in out


def test_convert_sgml_tables_no_data_fallback():
    block = "<TABLE>\nSome Caption\n<S>   <C>\n-----\n</TABLE>"
    out = _convert_sgml_tables(block)
    assert "Some Caption" in out


def test_convert_sgml_tables_no_header_no_data():
    block = "<TABLE>\n<S>   <C>\n   \n</TABLE>"
    out = _convert_sgml_tables(block)
    assert out == "" or "Col" not in out


def test_convert_sgml_tables_with_period_headers():
    block = (
        "<TABLE>\n"
        "                          December 31, 1993      December 31, 1992\n"
        "<S>                       <C>                    <C>\n"
        "Revenue:\n"
        "Total revenue             1,234                  1,100\n"
        "</TABLE>"
    )
    out = _convert_sgml_tables(block)
    assert "1993" in out
    assert "Total revenue" in out
    assert "**Revenue:**" in out


def test_convert_sgml_tables_no_format_line():
    block = "<TABLE>\nTotal revenue   1,234   1,100\n</TABLE>"
    out = _convert_sgml_tables(block)
    assert "1,234" in out


def test_extract_items_sgml():
    items = _extract_items_sgml(SGML_FILING)
    assert "item_1" in items
    assert items["item_1"]["part"] == "I"
    assert "item_II_1" in items


def test_extract_items_sgml_no_items():
    assert _extract_items_sgml("<PAGE>\nJust some text with no items.") == {}


def test_extract_items_sgml_toc_filtering():
    gap = "Filler prose line padding out the gap between sections.\n" * 20
    content = (
        "<PAGE>\n"
        "TABLE OF CONTENTS\n"
        "ITEM 1. BUSINESS 1\n"
        "ITEM 2. PROPERTIES 2\n"
        "ITEM 3. LEGAL 3\n"
        "ITEM 4. MINE 4\n"
        "ITEM 5. MARKET 5\n"
        + gap
        + "ITEM 1.  BUSINESS\n"
        + "Real business content goes here and is reasonably long.\n"
        + gap
        + "ITEM 2.  PROPERTIES\n"
        + "Real property content here that is also reasonably long enough.\n"
    )
    items = _extract_items_sgml(content)
    assert items


def test_extract_items_sgml_skips_lowercase_crossref():
    content = (
        "<PAGE>\n"
        "PART I\n"
        "ITEM 1.  BUSINESS\n"
        "The Company makes computers and related products for sale worldwide.\n"
        "Item 1 of this report describes the business in further detail here.\n"
        "ITEM 2.  PROPERTIES\n"
        "The Company leases its facilities under operating leases worldwide.\n"
    )
    items = _extract_items_sgml(content)
    # The cross-reference ("Item 1 of this report...") is not a section header.
    assert items["item_1"]["name"] == "BUSINESS"
    assert "describes the business" in items["item_1"]["text"]


def test_extract_items_sgml_folds_wrapped_title():
    """A short all-caps continuation line is folded into the item title."""
    body = "Real discussion content that is reasonably long. " * 12
    content = (
        "<PAGE>\n"
        "PART I\n"
        "ITEM 7.  MANAGEMENT'S DISCUSSION AND RESULTS\n"
        "OF OPERATIONS\n"
        "\n" + body + "\n"
        "ITEM 8.  FINANCIAL STATEMENTS\n" + body + "\n"
    )
    items = _extract_items_sgml(content)
    assert (
        items["item_7"]["name"] == "MANAGEMENT'S DISCUSSION AND RESULTS OF OPERATIONS"
    )


def test_extract_toc_sgml():
    toc = _extract_toc_sgml(SGML_FILING)
    assert toc


def test_extract_toc_from_table():
    html = """
    <table>
    <tr><td>PART I:</td><td>Business Overview</td></tr>
    <tr><td>Item 1:</td><td>Business</td><td>1</td></tr>
    <tr><td>Item 2:</td><td>Properties</td><td>2</td></tr>
    </table>
    """
    toc = _extract_toc_from_table(_soup(html))
    assert toc.get("1") == "Business"


def test_extract_toc_from_table_part_two():
    html = """
    <table>
    <tr><td>PART II:</td><td>Financial Information</td></tr>
    <tr><td>Item 5:</td><td>Market for Registrant</td><td>15</td></tr>
    </table>
    """
    toc = _extract_toc_from_table(_soup(html))
    assert "II_5" in toc


def test_extract_toc_from_table_skips_non_toc():
    html = "<table><tr><td>Revenue</td><td>100</td></tr></table>"
    assert _extract_toc_from_table(_soup(html)) == {}


def test_extract_toc_link_method():
    html = """
    <a href="#item1">ITEM 1.</a>
    <a href="#item1">Business Overview</a>
    <a href="#item1a">ITEM 1A.</a>
    <a href="#item1a">Risk Factors Disclosure</a>
    """
    toc = extract_toc(html)
    assert toc.get("1") == "Business Overview"
    assert toc.get("1A") == "Risk Factors Disclosure"


def test_extract_toc_text_pattern_fallback():
    html = "<div>ITEM 1. BUSINESS\nITEM 2. PROPERTIES\n</div>"
    toc = extract_toc(html)
    assert toc.get("1") == "BUSINESS"


def test_extract_toc_sgml_path():
    toc = extract_toc(SGML_FILING)
    assert toc


def test_parse_html_table_for_notes_structured():
    headers, rows = _parse_html_table_for_notes(_first_table(INCOME_TABLE_HTML))
    assert headers[0] == ""
    assert rows


def test_parse_html_table_for_notes_fallback():
    html = """
    <table>
    <tr><td>Name</td><td>Detail</td></tr>
    <tr><td>Foo</td><td>Bar</td></tr>
    </table>
    """
    headers, rows = _parse_html_table_for_notes(_first_table(html))
    assert headers == ["Name", "Detail"]
    assert rows == [["Foo", "Bar"]]


def test_parse_html_table_for_notes_too_few_rows():
    headers, rows = _parse_html_table_for_notes(
        _first_table("<table><tr><td>x</td></tr></table>")
    )
    assert headers == []
    assert rows == []


def test_table_to_markdown_notes():
    out = _table_to_markdown_notes(["A", "B"], [["1", "2"], ["3"]])
    assert "| A | B |" in out
    assert "| 3 |  |" in out


def test_table_to_markdown_notes_empty():
    assert _table_to_markdown_notes([], []) == ""


def test_table_to_markdown_notes_zero_cols():
    assert _table_to_markdown_notes([], [[]]) == ""


def test_extract_text_blocks_note_pattern():
    html = (
        "<b>Note 1. Significant Accounting Policies</b>"
        "<p>The company applies these significant policies in its reporting.</p>"
        "<b>Note 2. Inventories</b>"
        "<p>Inventories are stated at the lower of cost or market value here.</p>"
    )
    blocks = extract_text_blocks(html)
    assert "note_1" in blocks
    assert "Significant Accounting Policies" in blocks["note_1"]["name"]


def test_extract_text_blocks_empty():
    assert extract_text_blocks("<p>no notes here</p>") == {}


def test_extract_text_blocks_sgml_route():
    content = (
        "<PAGE>\n"
        "NOTES TO CONSOLIDATED FINANCIAL STATEMENTS\n"
        "1.  Interim information is unaudited and reflects all adjustments necessary.\n"
        "2.  Effective September 25, 1993 the company changed its accounting method here.\n"
        "ITEM 2\n"
    )
    blocks = extract_text_blocks(content)
    assert "note_1" in blocks


def test_extract_text_blocks_sgml_no_notes_section():
    content = "<PAGE>\nThis SGML filing has no notes section at all.\n"
    assert _extract_text_blocks_sgml(content) == {}


def test_extract_text_blocks_sgml_no_numbered_notes():
    content = (
        "<PAGE>\n"
        "NOTES TO FINANCIAL STATEMENTS\n"
        "Prose with no numbered notes whatsoever.\n"
    )
    assert _extract_text_blocks_sgml(content) == {}


def test_extract_text_blocks_sgml_numbered_notes_named_note_n():
    content = (
        "<PAGE>\n"
        "NOTES TO FINANCIAL STATEMENTS\n"
        "1.  Interim results are unaudited in all respects for this period.\n"
        "2.  Effective this year, the accounting policy changed for the company.\n"
    )
    blocks = _extract_text_blocks_sgml(content)
    # Bare numbered notes are named "Note N"; the number prefix is dropped.
    assert blocks["note_1"]["name"] == "Note 1"
    assert blocks["note_1"]["text"].startswith("Interim results are unaudited")
    assert blocks["note_2"]["name"] == "Note 2"


def test_extract_plain_text_notes_named_headings():
    text = (
        "Notes to Consolidated Financial Statements.\n"
        "Income Taxes\n"
        "The Company adopted a new accounting standard that changes the method "
        "of accounting for income taxes on a prospective basis during the year.\n"
        "<PAGE>\n"
        "27\n"
        "This Heading Is Far Too Long To Be Treated As A Real Note Title Line\n"
        "RESERVES\n"
        "Amount      Value\n"
        "FAS 109\n"
        "Income xyz Provision\n"
        "Borrowings\n"
        "Short tail.\n"
        "Inventories\n"
        "Inventories are stated at the lower of cost or market and consist of "
        "purchased parts, work in process, and finished goods held at year end.\n"
        "SIGNATURES\n"
        "Pursuant to the requirements this trailing text must be excluded here.\n"
    )
    notes = extract_plain_text_notes(text)
    assert [n["name"] for n in notes.values()] == ["Income Taxes", "Inventories"]
    assert notes["note_1"]["text"].startswith("The Company adopted")
    assert "must be excluded" not in notes["note_2"]["text"]


def test_extract_plain_text_notes_no_header():
    assert extract_plain_text_notes("Prose without a notes header anywhere.") == {}


def test_extract_plain_text_notes_no_boundary():
    text = (
        "Notes to Financial Statements\n"
        "Commitments\n"
        "The Company leases office and manufacturing facilities under various "
        "operating leases that expire at differing dates over the next decade.\n"
    )
    notes = extract_plain_text_notes(text)
    assert [n["name"] for n in notes.values()] == ["Commitments"]


def test_extract_text_blocks_sgml_named_notes_preferred():
    content = (
        "<PAGE>\n"
        "NOTES TO CONSOLIDATED FINANCIAL STATEMENTS\n"
        "Income Taxes\n"
        "The Company adopted a new standard for accounting for income taxes on "
        "a prospective basis, and prior periods have not been restated here.\n"
        "Inventories\n"
        "Inventories are stated at the lower of cost or market and consist of "
        "purchased parts, work in process, and finished goods at period end.\n"
        "SIGNATURES\n"
    )
    blocks = _extract_text_blocks_sgml(content)
    assert [b["name"] for b in blocks.values()] == ["Income Taxes", "Inventories"]


def test_extract_plain_text_notes_note_n_title():
    text = (
        "Note 1 - Basis of Presentation\n"
        "Interim information is unaudited but reflects all adjustments that are "
        "necessary for a fair statement of the interim results presented here.\n"
        "Note 2 - Contingencies\n"
        "The Company is subject to various legal proceedings and claims that "
        "arise in the ordinary course of business and remain unadjudicated.\n"
        "Item 2. Management's Discussion and Analysis\n"
        "This MD&A text must not be captured as a note body at all here.\n"
    )
    notes = extract_plain_text_notes(text)
    assert [n["name"] for n in notes.values()] == [
        "Basis of Presentation",
        "Contingencies",
    ]
    assert notes["note_1"]["text"].startswith("Interim information")
    assert "MD&A text" not in notes["note_2"]["text"]


def test_extract_text_blocks_sgml_note_n_title_condensed():
    content = (
        "<PAGE>\n"
        "NOTES TO CONDENSED CONSOLIDATED FINANCIAL STATEMENTS (UNAUDITED)\n"
        "Note 1 - Basis of Presentation\n"
        "Interim information is unaudited but reflects all adjustments that are "
        "necessary for a fair statement of the interim results presented here.\n"
        "Note 2 - Contingencies\n"
        "The Company is subject to various legal proceedings and claims that "
        "arise in the ordinary course of business and remain unadjudicated.\n"
        "Item 2. Management's Discussion and Analysis\n"
    )
    blocks = _extract_text_blocks_sgml(content)
    assert [b["name"] for b in blocks.values()] == [
        "Basis of Presentation",
        "Contingencies",
    ]


def test_find_notes_in_section_no_match():
    assert _find_notes_in_section("no financial notes here") == []


def test_find_notes_in_section_no_toc_notes():
    html = "Notes to Financial Statements\nbut no toc table cells present."
    assert _find_notes_in_section(html) == []


def test_find_notes_in_section_with_toc_and_content():
    toc = (
        "Notes to Consolidated Financial Statements"
        "<td><p><font>A</font></p></td>"
        '<td width="85%"><font>Significant Accounting Policies</font>'
    )
    padding_a = " " * 100_000
    content_header = "<b><font>A. Significant Accounting Policies</font></b>"
    html = toc + padding_a + content_header + " body content for note A here."
    matches = _find_notes_in_section(html)
    assert matches
    assert matches[0][1] == "A"


def test_extract_text_blocks_via_find_notes():
    toc = (
        "Notes to Consolidated Financial Statements"
        "<td><p><font>A</font></p></td>"
        '<td width="85%"><font>Significant Accounting Policies</font>'
    )
    padding = " " * 100_000
    content = (
        "<b><font>A. Significant Accounting Policies</font></b>"
        "<p>Policies described here in adequate length for extraction.</p>"
    )
    html = toc + padding + content
    blocks = extract_text_blocks(html)
    assert "note_A" in blocks


def test_extract_items_html_bold():
    html = (
        "<b>Item 2: Management Discussion</b>"
        "<p>This is the discussion content with sufficient length to keep.</p>"
        "<b>Item 3: Market Risk</b>"
        "<p>Market risk disclosures appear here with adequate descriptive length.</p>"
    )
    items = extract_items(html, "10-Q")
    assert "item_2" in items
    assert "Management Discussion" in items["item_2"]["name"]


def test_extract_items_split_pattern():
    html = (
        "<b>Item&nbsp;2:&nbsp;</b></TD><TD><b>Management Discussion And Analysis</b>"
        "<p>Discussion body text here that is sufficiently long to be retained.</p>"
    )
    items = extract_items(html, "10-Q")
    assert "item_2" in items


def test_extract_items_nonbold_pattern():
    html = (
        ">ITEM 7. MANAGEMENT'S DISCUSSION AND ANALYSIS OF OPERATIONS</FONT>"
        "<p>Some MD&A content here that is reasonably long for retention purposes.</p>"
    )
    items = extract_items(html, "10-K")
    assert "item_7" in items


def test_extract_items_part_two_detection():
    html = (
        "<b>Item 1: Business</b>"
        "<p>Business description content that is reasonably long enough to keep here.</p>"
        "<b>Item 2: Properties</b>"
        "<p>Property description content that is reasonably long enough to keep here.</p>"
        "<b>Item 1: Legal Proceedings</b>"
        "<p>Legal proceedings content that is reasonably long enough to keep around.</p>"
    )
    items = extract_items(html)
    assert "item_II_1" in items
    assert items["item_II_1"]["part"] == "II"


def test_extract_items_no_matches_sgml_fallback():
    items = extract_items(SGML_FILING)
    assert "item_1" in items


def test_extract_items_no_matches_html():
    assert extract_items("<p>nothing relevant at all here</p>", "10-K") == {}


def test_extract_items_with_table_and_header_and_bullets():
    html = (
        "<b>Item 2: Discussion</b>"
        "<p><b>A Bold Section Header</b></p>"
        "<table>"
        "<tr><td>•</td><td>A bullet point of reasonable length to keep</td></tr>"
        "<tr><td>•</td><td>Another bullet point of reasonable length</td></tr>"
        "</table>"
        "<table><tr><td>Just a small non-financial table cell value here.</td></tr></table>"
        "<p>Regular paragraph text content that should be retained in the output.</p>"
    )
    items = extract_items(html, "10-Q")
    assert "item_2" in items
    assert "##" in items["item_2"]["text"]


def test_extract_items_financial_table_in_item():
    html = "<b>Item 1: Financial Statements</b>" + INCOME_TABLE_HTML
    items = extract_items(html, "10-Q")
    assert "item_1" in items


def test_extract_8k_items():
    html = (
        "<p>Item 1.01 Entry into a Material Definitive Agreement</p>"
        "<p>The registrant entered into an agreement described in this paragraph.</p>"
        "<p>Item 8.01 Other Events</p>"
        "<p>Other events are described in this paragraph with sufficient length.</p>"
    )
    items = _extract_8k_items(html)
    assert "item_1.01" in items
    assert items["item_1.01"]["section"] == "1"


def test_extract_8k_via_extract_items():
    html = (
        "<p>Item 1.01 Entry into a Material Definitive Agreement here</p>"
        "<p>The registrant entered into an agreement described in this paragraph fully.</p>"
    )
    items = extract_items(html)
    assert "item_1.01" in items


def test_extract_8k_items_empty():
    assert _extract_8k_items("<p>no eight k items present here</p>") == {}


def test_extract_8k_items_short_title_default():
    html = (
        "<p>Item 8.01</p>"
        "<p>Other events described here with sufficient descriptive length retained.</p>"
    )
    items = _extract_8k_items(html)
    assert items["item_8.01"]["name"] == "Other Events"


def test_extract_8k_items_dedup_toc():
    spacer = "x" * 1500
    html = (
        "<p>Item 1.01 Entry into Agreement</p>"
        "<p>TOC short.</p>"
        f"<p>{spacer}</p>"
        "<p>Item 1.01 Entry into a Material Definitive Agreement</p>"
        "<p>The actual section content appears here with proper descriptive length.</p>"
    )
    items = _extract_8k_items(html)
    assert "item_1.01" in items


def test_extract_8k_items_with_table():
    html = "<p>Item 9.01 Financial Statements and Exhibits</p>" + INCOME_TABLE_HTML
    items = _extract_8k_items(html)
    assert "item_9.01" in items


def test_get_8k_item_name():
    assert _get_8k_item_name("1.01") == "Entry into a Material Definitive Agreement"
    assert _get_8k_item_name("99.99") == "Item 99.99"


def test_get_item_default_name():
    assert _get_item_default_name("1", "I") == "Financial Statements"
    assert _get_item_default_name("1A", "II") == "Risk Factors"
    assert _get_item_default_name("99", "I") == "Item 99"


def test_parse_sgml_value():
    assert _parse_sgml_value("$1,234") == 1234.0
    assert _parse_sgml_value("(500)") == -500.0
    assert _parse_sgml_value("--") is None
    assert _parse_sgml_value("") is None
    assert _parse_sgml_value("abc") is None


def test_extract_sgml_periods_multiline():
    lines = [
        "                December 31      December 31",
        "                   1993             1992",
    ]
    periods = _extract_sgml_periods(lines, 2)
    assert periods == ["December 31, 1993", "December 31, 1992"]


def test_extract_sgml_periods_mismatched_counts():
    lines = [
        "          December 31",
        "             1993        1992",
    ]
    periods = _extract_sgml_periods(lines, 2)
    assert "1993" in periods[0]
    assert periods[1] == "1992"


def test_extract_sgml_periods_full_date_single_line():
    lines = ["    January 31, 1993     January 25, 1992"]
    periods = _extract_sgml_periods(lines, 2)
    assert periods[0].startswith("January 31, 1993")


def test_extract_sgml_periods_standalone_years():
    lines = ["    Description    1993    1992"]
    periods = _extract_sgml_periods(lines, 2)
    assert periods == ["1993", "1992"]


def test_extract_sgml_periods_none():
    assert _extract_sgml_periods(["no dates here"], 2) == []


def test_extract_table_subtitle():
    assert _extract_table_subtitle("ASSETS\n", "") == "Assets"
    liab = _extract_table_subtitle("LIABILITIES AND SHAREHOLDERS' EQUITY\n", "")
    assert liab is not None
    assert "Liabilities and" in liab
    assert _extract_table_subtitle("nothing relevant", "") is None


def test_find_best_sgml_table():
    tables = _find_best_sgml_table(SGML_FILING, "income")
    assert tables
    assert tables[0][1] >= 0


def test_find_best_sgml_table_negative_keywords_skip():
    content = (
        "balance sheet financial position\n"
        "<TABLE>\n<S>   <C>\n"
        "statements of income total revenues\n"
        "Revenue   1,234   1,100   2,345   3,456   4,567\n"
        "</TABLE>\n"
    )
    assert _find_best_sgml_table(content, "income") == []


def test_find_best_sgml_table_too_few_numbers():
    content = (
        "<TABLE>\n<S>   <C>\n"
        "statements of operations net income\n"
        "Revenue   100   200\n"
        "</TABLE>\n"
    )
    assert _find_best_sgml_table(content, "income") == []


def test_find_best_sgml_table_no_keyword():
    content = (
        "<TABLE>\n<S>   <C>\n"
        "Generic table with no keywords\n"
        "Row   1,234   2,345   3,456   4,567   5,678\n"
        "</TABLE>\n"
    )
    assert _find_best_sgml_table(content, "income") == []


def test_parse_sgml_statement():
    df, meta = _parse_sgml_statement(SGML_FILING, "income")
    assert not df.empty
    assert meta.iloc[0]["scale"] == "thousands"


def test_parse_sgml_statement_no_tables():
    df, meta = _parse_sgml_statement("<PAGE>\nno tables here", "income")
    assert df.empty
    assert meta.empty


def test_parse_non_xbrl_statement_sgml_route():
    df, _ = parse_non_xbrl_statement(SGML_FILING, "income")
    assert not df.empty


def test_extract_block_line_items_basic():
    block = (
        "<S>                  <C>          <C>\n"
        "Current assets:\n"
        "Cash                 1,234        1,100\n"
        "Receivables          2,345        2,200\n"
        "                     ------       ------\n"
        "                     3,579        3,300\n"
    )
    items, label_end, fmt_idx = _extract_block_line_items(block, 2, "Assets")
    assert fmt_idx == 0
    labels = [i["label"] for i in items]
    assert "Cash" in labels
    assert any(lbl.startswith("Total") for lbl in labels)


def test_extract_block_line_items_no_format_line():
    block = (
        "Revenue              1,234        1,100\n"
        "Costs                  500          450\n"
    )
    items, label_end, fmt_idx = _extract_block_line_items(block, 2)
    assert fmt_idx is None
    assert label_end is None


def test_extract_block_line_items_dashes_and_skips():
    block = (
        "<S>                  <C>          <C>\n"
        "See accompanying notes.\n"
        "=========\n"
        "Multi line label\n"
        "continues here       1,234        1,100\n"
        "Dashes only          --           --\n"
        "Earnings per share   $1,500       $1,400\n"
    )
    items, _, _ = _extract_block_line_items(block, 2, None)
    assert any("Multi line label continues here" in i["label"] for i in items)
    assert any(i["skip_multiplier"] for i in items)


def test_extract_block_line_items_section_in_buffer_then_blank():
    block = (
        "<S>                  <C>          <C>\n"
        "Buffered text\n"
        "Operating activities:\n"
        "\n"
        "Cash flow            1,234        1,100\n"
    )
    items, _, _ = _extract_block_line_items(block, 2, None)
    assert items


def test_extract_block_line_items_empty_label_uses_section():
    block = (
        "<S>                  <C>          <C>\n"
        "Net assets:\n"
        "                     1,234        1,100\n"
    )
    items, _, _ = _extract_block_line_items(block, 2, None)
    assert any(i["label"] == "Total Net assets" for i in items)


def test_extract_block_line_items_empty_label_no_section_no_fallback():
    block = (
        "<S>                  <C>          <C>\n"
        "                     1,234        1,100\n"
    )
    items, _, _ = _extract_block_line_items(block, 2, None)
    assert any(i["label"] == "Total" for i in items)


def test_clean_paragraph_text_year_run():
    assert _clean_paragraph_text("revenue 19981999 was up") is None


def test_extract_periods_skip_dollar_for_at_headers():
    html = (
        "<table><tr>"
        "<td>$</td><td>for the</td><td>at</td>"
        "<td>Gross Carrying Amount</td><td>Net Carrying Value</td>"
        "</tr></table>"
    )
    rows = _first_table(html).find_all("tr")
    periods = _extract_periods(rows)
    assert "Gross Carrying Amount" in periods or "Net Carrying Value" in periods


def test_extract_periods_more_years_than_prefixes():
    html = (
        "<table>"
        "<tr><td>Year Ended December</td></tr>"
        "<tr><td>2003</td><td>2002</td><td>2001</td></tr>"
        "</table>"
    )
    rows = _first_table(html).find_all("tr")
    periods = _extract_periods(rows)
    assert periods[-1] == "2001"


def test_extract_table_data_skips_empty_row():
    html = (
        "<table>"
        "<tr><td>Revenue</td><td>100</td><td>200</td></tr>"
        "<tr><td></td><td></td></tr>"
        "<tr><td>Costs</td><td>50</td><td>60</td></tr>"
        "<tr><td>Income</td><td>50</td><td>140</td></tr>"
        "<tr><td>Net</td><td>40</td><td>120</td></tr>"
        "<tr><td>Total</td><td>90</td><td>260</td></tr>"
        "</table>"
    )
    result = _extract_table_data(_first_table(html))
    assert result is not None


def test_parse_non_xbrl_statement_extract_returns_none():
    html = (
        "<table>"
        "<tr><td>net income total revenues 1,000 2,000 3,000 4,000 5,000 "
        "6,000 7,000 8,000 9,000 10,000 11,000</td></tr>"
        "</table>"
    )
    df, meta = parse_non_xbrl_statement(html, "income")
    assert df.empty
    assert meta.empty


def test_extract_toc_skips_non_hash_and_empty_links():
    html = (
        '<a href="http://example.com">External</a>'
        '<a href="#item1"></a>'
        '<a href="#item1">ITEM 1.</a>'
        '<a href="#item1">Business Description Section</a>'
    )
    toc = extract_toc(html)
    assert toc.get("1") == "Business Description Section"


def test_extract_toc_from_table_all_empty_cells():
    html = "<table><tr><td>PART I</td></tr><tr><td></td><td></td></tr></table>"
    _extract_toc_from_table(_soup(html))


def test_extract_toc_from_table_many_cells():
    inner = "".join(f"<td>x{i}</td>" for i in range(8))
    html = (
        "<table>"
        f"<tr>{inner}<td>Item 1:</td><td>Business</td><td>1</td></tr>"
        "<tr><td>PART I</td><td>placeholder</td></tr>"
        "</table>"
    )
    toc = _extract_toc_from_table(_soup(html))
    assert toc.get("1") == "Business"


def test_extract_toc_from_table_arabic_parts():
    html = (
        "<table>"
        "<tr><td>PART 1:</td><td>Business Section</td></tr>"
        "<tr><td>Item 1:</td><td>Business</td><td>1</td></tr>"
        "<tr><td>PART 2:</td><td>Financial Section</td></tr>"
        "<tr><td>Item 5:</td><td>Market Data</td><td>30</td></tr>"
        "</table>"
    )
    toc = _extract_toc_from_table(_soup(html))
    assert "PART_I" in toc
    assert "PART_II" in toc


def test_extract_toc_from_table_title_with_trailing_page():
    html = (
        "<table>"
        "<tr><td>PART I</td><td>x</td></tr>"
        "<tr><td>Item 1:</td><td>Business 15</td><td>15</td></tr>"
        "</table>"
    )
    toc = _extract_toc_from_table(_soup(html))
    assert toc.get("1") == "Business"


def test_extract_toc_sgml_merge_when_not_larger():
    content = (
        "<PAGE>\n"
        "ITEM 1. BUSINESS\n"
        "ITEM 2. PROPERTIES\n"
        "\n"
        "ITEM 1.  BUSINESS                                    1\n"
        "ITEM 7.  EXTRA ITEM HEADING HERE                     7\n"
    )
    toc = extract_toc(content)
    assert toc


def test_extract_toc_sgml_part_markers_and_partii():
    content = (
        "<PAGE>\n"
        "PART 1\n"
        "ITEM 1.  BUSINESS OVERVIEW                            1\n"
        + "filler text line padding out the gap between the parts.\n"
        * 5
        + "PART 2\n"
        "ITEM 5.  MARKET INFORMATION                           5\n"
    )
    toc = _extract_toc_sgml(content)
    assert "II_5" in toc


def test_extract_items_sgml_arabic_parts():
    gap = "Filler prose padding the gap between document sections here.\n" * 20
    content = (
        "<PAGE>\n"
        "PART 1\n\n"
        + gap
        + "ITEM 1.  BUSINESS\n"
        + "Real business content here that is reasonably long for a section.\n"
        + gap
        + "PART 2\n\n"
        + "ITEM 1.  LEGAL PROCEEDINGS\n"
        + "Real legal content here that is reasonably long for a section body.\n"
        + gap
        + "PART 3\n\n"
        + "ITEM 7.  OTHER MATTERS\n"
        + "Real other content here that is reasonably long for a section body.\n"
    )
    items = _extract_items_sgml(content)
    assert items


def test_extract_items_sgml_all_packed_toc():
    content = (
        "<PAGE>\n"
        "ITEM 1. BUSINESS 1\n"
        "ITEM 2. PROPERTIES 2\n"
        "ITEM 3. LEGAL 3\n"
        "ITEM 4. MINE 4\n"
        "ITEM 5. MARKET 5\n"
    )
    assert _extract_items_sgml(content) == {}


def test_extract_items_nonbold_short_title_skipped():
    html = ">ITEM 7. SHORT.</FONT>"
    assert extract_items(html, "10-K") == {}


def test_extract_items_nested_table_and_nested_p():
    html = (
        "<b>Item 2: Discussion</b>"
        "<table><tr><td>"
        "<p>Paragraph nested inside a financial statement table cell here.</p>"
        "<table><tr><td>1,234 5,678 9,012 nested financial table values</td></tr></table>"
        "</td></tr>"
        "<tr><td>Outer table value 1,234 5,678 9,012 keeps it financial</td></tr>"
        "</table>"
    )
    items = extract_items(html, "10-Q")
    assert "item_2" in items


def test_extract_8k_nested_table_bullet_nonfinancial_and_nested_p():
    html = (
        "<p>Item 8.01 Other Events Disclosure Section</p>"
        "<table>"
        "<tr><td>•</td><td>A bullet point of adequate length to be kept</td></tr>"
        "<tr><td>•</td><td>Another bullet point of adequate length kept</td></tr>"
        "</table>"
        "<table><tr><td>Plain non-financial descriptive table cell content here.</td></tr></table>"
        "<table>"
        "<tr><td><p>Nested paragraph inside outer financial table cell content.</p>"
        "<table><tr><td>nested 1,234 5,678 9,012 financial values here</td></tr></table>"
        "</td></tr>"
        "<tr><td>Outer 1,234 5,678 9,012 financial table values retained</td></tr>"
        "</table>"
    )
    items = _extract_8k_items(html)
    assert "item_8.01" in items


def test_extract_simple_table_row_without_direct_cells():
    html = (
        "<table>"
        "<tr><th>Heading One</th><th>Heading Two</th></tr>"
        "<tbody><tr><td>Row A</td><td>Row B</td></tr></tbody>"
        "</table>"
    )
    _extract_simple_table(_first_table(html))


def test_parse_html_table_for_notes_fallback_empty_row():
    html = (
        "<table>"
        "<tr><td>Name</td><td>Detail</td></tr>"
        "<tr><td></td><td></td></tr>"
        "<tr><td>Foo</td><td>Bar</td></tr>"
        "</table>"
    )
    headers, rows = _parse_html_table_for_notes(_first_table(html))
    assert headers == ["Name", "Detail"]
    assert rows == [["Foo", "Bar"]]


def test_extract_text_blocks_note_with_tables_and_bullets():
    html = (
        "<b>Note 1. Significant Accounting Policies</b>"
        "<p>The company applies significant accounting policies in its reporting here.</p>"
        "<table>"
        "<tr><td>•</td><td>A bullet item of adequate length to be retained</td></tr>"
        "<tr><td>•</td><td>Another bullet item of adequate length retained</td></tr>"
        "</table>"
        + INCOME_TABLE_HTML
        + "<table><tr><td>Single row note table that yields no data rows.</td></tr></table>"
        + "<table><tr><td>"
        "<p>Paragraph nested in a table cell that should be skipped here.</p>"
        "<table><tr><td>nested 1,234 5,678 9,012 financial table values</td></tr>"
        "<tr><td>nested 2,345 6,789 0,123 more financial values here</td></tr></table>"
        "</td>"
        "<td>outer 1,234 5,678 9,012 financial values keep it a table</td></tr></table>"
        "<b>Note 2. Inventories</b>"
        "<p>Inventories are stated at the lower of cost or market value as described.</p>"
        "<b>Item 2: Management Discussion</b>"
    )
    blocks = extract_text_blocks(html)
    assert "note_1" in blocks
    assert "tables" in blocks["note_1"]


def test_extract_sgml_periods_blank_between_month_and_year():
    lines = [
        "                December 31      December 31",
        "",
        "                   1993             1992",
    ]
    periods = _extract_sgml_periods(lines, 2)
    assert periods == ["December 31, 1993", "December 31, 1992"]


def test_extract_block_line_items_no_format_more_values():
    block = "\n".join(
        ["Padding header line"] * 10
        + [
            "Revenue line item value     1,234     5,678     9,012",
            "Costs line item value         500       450       400",
        ]
    )
    items, label_end, fmt_idx = _extract_block_line_items(block, 2)
    assert label_end is None
    assert fmt_idx is None
    assert items
    assert all(len(i["values"]) == 2 for i in items)


def test_extract_block_line_items_fewer_values_padded():
    block = "<S>          <C>      <C>      <C>\nRevenue line     1,234\n"
    items, _, _ = _extract_block_line_items(block, 3)
    assert items
    assert items[0]["values"][0] is None


def test_parse_sgml_statement_millions():
    content = (
        "<PAGE>\n"
        "CONSOLIDATED STATEMENTS OF OPERATIONS\n"
        "(In millions)\n\n"
        "                            1993        1992\n"
        "<TABLE>\n"
        "<S>                         <C>         <C>\n"
        "Total revenues              12,340      11,000\n"
        "Cost of revenue             5,000       4,500\n"
        "Net income                  5,340       4,700\n"
        "</TABLE>\n"
    )
    _, meta = _parse_sgml_statement(content, "income")
    assert meta.iloc[0]["scale"] == "millions"


def test_parse_sgml_statement_billions():
    content = (
        "<PAGE>\n"
        "CONSOLIDATED STATEMENTS OF OPERATIONS\n"
        "(In billions)\n\n"
        "                            1993        1992\n"
        "<TABLE>\n"
        "<S>                         <C>         <C>\n"
        "Total revenues              12,340      11,000\n"
        "Cost of revenue             5,000       4,500\n"
        "Net income                  5,340       4,700\n"
        "</TABLE>\n"
    )
    _, meta = _parse_sgml_statement(content, "income")
    assert meta.iloc[0]["scale"] == "billions"


def test_parse_sgml_statement_units_and_period_fallback():
    content = (
        "<PAGE>\n"
        "CONSOLIDATED STATEMENTS OF OPERATIONS\n\n"
        "<TABLE>\n"
        "<S>                         <C>         <C>\n"
        "Total revenues              12,340      11,000\n"
        "Cost of revenue             5,000       4,500\n"
        "Net income                  5,340       4,700\n"
        "</TABLE>\n"
    )
    _, meta = _parse_sgml_statement(content, "income")
    assert meta.iloc[0]["scale"] == "units"
    assert meta.iloc[0]["periods"][0].startswith("Period_")


def test_extract_items_sgml_gap_break():
    packed = (
        "<PAGE>\n"
        "ITEM 1. A 1\n"
        "ITEM 2. B 2\n"
        "ITEM 3. C 3\n"
        "ITEM 4. D 4\n"
        "ITEM 5. E 5\n"
        "ITEM 6. F 6\n"
    )
    gap = "Real section content padding the document body out fully.\n" * 18
    content = (
        packed
        + gap
        + "ITEM 7.  OTHER MATTERS\n"
        + "Real other content that is reasonably long for a section body here too.\n"
    )
    items = _extract_items_sgml(content)
    assert items


def test_extract_items_sgml_title_all_dots():
    gap = "Filler prose padding the gap between document sections here.\n" * 20
    content = (
        "<PAGE>\n"
        "ITEM 1.  BUSINESS\n"
        + gap
        + "ITEM 2.  .....\n"
        + gap
        + "ITEM 3.  REAL HEADING\n"
        + "Real content of adequate length to serve as a section body here.\n"
    )
    items = _extract_items_sgml(content)
    assert "item_2" not in items


def test_parse_sgml_statement_no_line_items():
    content = (
        "<PAGE>\n"
        "CONSOLIDATED STATEMENTS OF OPERATIONS net income total revenues\n"
        "<TABLE>\n"
        "Reference figures 1,234 5,678 9,012 1,111 2,222 3,333 in caption\n"
        "<S>             <C>        <C>\n"
        "See accompanying notes to the financial statements herein.\n"
        "See notes for further detail on these amounts and balances.\n"
        "</TABLE>\n"
    )
    df, meta = _parse_sgml_statement(content, "income")
    assert df.empty
    assert meta.empty


def test_extract_simple_table_tr_without_direct_cells():
    html = (
        "<table>"
        "<tr><span>orphan row with no direct cells</span></tr>"
        "<tr><td>Name</td><td>Value</td></tr>"
        "<tr><td>Foo</td><td>Bar</td></tr>"
        "</table>"
    )
    out = _extract_simple_table(_first_table(html))
    assert out is not None
    assert "Name | Value" in out


def test_extract_block_line_items_buffer_cleared_on_blank():
    block = (
        "<S>                  <C>          <C>\n"
        "Buffered non colon line\n"
        "\n"
        "Cash flow            1,234        1,100\n"
    )
    items, _, _ = _extract_block_line_items(block, 2, None)
    assert any(i["label"] == "Cash flow" for i in items)


def test_parse_sgml_statement_periods_from_second_table():
    content = (
        "<PAGE>\n"
        "CONSOLIDATED STATEMENTS OF OPERATIONS\n"
        "(In thousands)\n\n"
        "<TABLE>\n"
        "<S>                         <C>         <C>\n"
        "Total revenues              12,340      11,000\n"
        "Cost of revenue             5,000       4,500\n"
        "Net income                  5,340       4,700\n"
        "</TABLE>\n\n"
        "CONSOLIDATED STATEMENTS OF OPERATIONS CONTINUED\n"
        "<TABLE>\n"
        "                            1993        1992\n"
        "<S>                         <C>         <C>\n"
        "Other income                3,000       2,500\n"
        "Total income                8,340       7,200\n"
        "Final total                 5,340       4,700\n"
        "</TABLE>\n"
    )
    _, meta = _parse_sgml_statement(content, "income")
    assert meta.iloc[0]["periods"] == ["1993", "1992"]


def test_extract_sgml_periods_single_date_multi_year():
    lines = ["THREE FISCAL YEARS ENDED SEPTEMBER 25, 1999    1999    1998    1997"]
    assert _extract_sgml_periods(lines, 3) == [
        "SEPTEMBER 25, 1999",
        "SEPTEMBER 25, 1998",
        "SEPTEMBER 25, 1997",
    ]


def test_extract_sgml_periods_single_date_fallback():
    # One full date, three columns requested, but no extra year columns to pair.
    assert _extract_sgml_periods(["AS OF SEPTEMBER 25, 1999"], 3) == [
        "SEPTEMBER 25, 1999"
    ]


def test_convert_sgml_tables_skips_rule_line_in_header():
    content = (
        "<TABLE>\n"
        "Net sales by product (in millions):\n"
        "-----------------------------------\n"
        "                  December 31, 1999\n"
        "<S>               <C>\n"
        "Product A          $ 1,234\n"
        "Product B          $ 5,678\n"
        "</TABLE>"
    )
    md = _convert_sgml_tables(content)
    assert "Net sales by product (in millions):" in md
    assert "-----------------------------------" not in md
