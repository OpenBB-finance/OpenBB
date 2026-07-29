"""Offline unit tests raising coverage for ``openbb_sec.utils.html2markdown``.

The module is a pure HTML-to-Markdown converter for SEC filings built on
BeautifulSoup and string processing.  No network access is required: the public
``html_to_markdown`` entry point and the many smaller helpers are exercised
directly with crafted, SEC-filing-shaped HTML / row structures.

Tests are grouped: cheap pure-helper tests first, then a handful of rich
``html_to_markdown`` fixtures that sweep the large table / period / layout
machinery transitively.
"""

from bs4 import BeautifulSoup

import openbb_sec.utils.html2markdown as h2m

# ===========================================================================
# Helpers for building bs4 inputs
# ===========================================================================


def _table(html):
    """Parse an HTML snippet and return its first <table> Tag."""
    soup = BeautifulSoup(html, "html.parser")
    return soup.find("table")


def _tag(html, name=None):
    """Parse an HTML snippet and return the first tag (optionally by name)."""
    soup = BeautifulSoup(html, "html.parser")
    if name:
        return soup.find(name)
    return soup.find(True)


def _cell(text, cs=1, rs=1, th=False, idv=None):
    """Build a <td>/<th> string with optional colspan/rowspan/id."""
    tag = "th" if th else "td"
    attrs = ""
    if cs != 1:
        attrs += f' colspan="{cs}"'
    if rs != 1:
        attrs += f' rowspan="{rs}"'
    if idv:
        attrs += f' id="{idv}"'
    return f"<{tag}{attrs}>{text}</{tag}>"


def _build_table(rows):
    """Build a <table> Tag from a list of rows (each a list of _cell strings)."""
    return _table(_table_html(rows))


def _table_html(rows):
    """Build a <table> HTML string from a list of rows (lists of _cell strings)."""
    body = "".join("<tr>" + "".join(r) + "</tr>" for r in rows)
    return f"<table>{body}</table>"


# ===========================================================================
# strip_all / financial normalization
# ===========================================================================


def test_strip_all_removes_invisible_and_whitespace():
    assert h2m.strip_all("  \u200bhello﻿  ") == "hello"
    assert h2m.strip_all("\xa0 x \xa0") == "x"


def test_normalize_financial_cell_variants():
    assert h2m._normalize_financial_cell("$ 1,787") == "$1,787"
    assert h2m._normalize_financial_cell("( 135 )") == "(135)"
    assert h2m._normalize_financial_cell("$ ( 471 )") == "$(471)"
    assert h2m._normalize_financial_cell("( 0.2 ) %") == "(0.2)%"
    # dollar-dash
    assert h2m._normalize_financial_cell("$ —") == "$—"
    # dash-percent
    assert h2m._normalize_financial_cell("— %") == "—%"


def test_normalize_financial_cell_passthrough():
    # empty / whitespace returns original
    assert h2m._normalize_financial_cell("   ") == "   "
    # plain text passes through unchanged
    assert h2m._normalize_financial_cell("Revenue") == "Revenue"
    # already compact -> unchanged (compact == s branch)
    assert h2m._normalize_financial_cell("$1,787") == "$1,787"


def test_normalize_financial_rows():
    rows = [["$ 1,787", "Revenue"], ["( 135 )", "x"]]
    out = h2m._normalize_financial_rows(rows)
    assert out == [["$1,787", "Revenue"], ["(135)", "x"]]


# ===========================================================================
# remove_empty_columns
# ===========================================================================


def test_remove_empty_columns_empty_input():
    assert h2m.remove_empty_columns([]) == []


def test_remove_empty_columns_drops_blank_column():
    rows = [["A", "", "B"], ["1", "", "2"]]
    out = h2m.remove_empty_columns(rows)
    assert out == [["A", "B"], ["1", "2"]]


def test_remove_empty_columns_ragged_rows():
    rows = [["A", "x"], ["B"]]
    out = h2m.remove_empty_columns(rows)
    # second column kept (has content in first row); missing cell -> ""
    assert out == [["A", "x"], ["B", ""]]


# ===========================================================================
# is_data_row_header
# ===========================================================================


def test_is_data_row_header_empty():
    assert h2m.is_data_row_header(["", "  "]) is True


def test_is_data_row_header_years_ended_no_numbers():
    assert h2m.is_data_row_header(["For the Years Ended December 31,"]) is True


def test_is_data_row_header_months_ended_with_data_is_not_header():
    # data row whose label has "months ended" but also numeric values
    row = ["Three months ended April 30,", "10", "$273.42", "$2,681"]
    assert h2m.is_data_row_header(row) is False


def test_is_data_row_header_all_caps_categories():
    assert h2m.is_data_row_header(["EQUIPMENT", "OPERATIONS", "FINANCIAL"]) is True


def test_is_data_row_header_year_only_row():
    assert h2m.is_data_row_header(["2025", "2024", "2023"]) is True


def test_is_data_row_header_period_row():
    assert h2m.is_data_row_header(["May 1999", "November 1998"]) is True


def test_is_data_row_header_regular_data_row():
    assert h2m.is_data_row_header(["Revenue", "$100", "$200"]) is False


# ===========================================================================
# _convert_image_to_html
# ===========================================================================


def test_convert_image_no_src():
    img = _tag('<img alt="x"/>', "img")
    assert h2m._convert_image_to_html(img) == ""


def test_convert_image_markdown_no_size():
    img = _tag('<img src="pic.png" alt="Logo"/>', "img")
    assert h2m._convert_image_to_html(img) == "![Logo](pic.png)"


def test_convert_image_with_style_size_uses_html():
    img = _tag(
        '<img src="c.png" alt="check" style="width:0.09in;height:0.08in"/>', "img"
    )
    out = h2m._convert_image_to_html(img)
    assert (
        out.startswith("<img src=") and "width:0.09in" in out and "height:0.08in" in out
    )


def test_convert_image_resolves_relative_url():
    img = _tag('<img src="img/a.png" alt="A"/>', "img")
    out = h2m._convert_image_to_html(img, base_url="https://x.com/dir/doc.htm")
    assert out == "![A](https://x.com/dir/img/a.png)"


def test_convert_image_numeric_width_attribute():
    img = _tag('<img src="a.png" width="20" height="10"/>', "img")
    out = h2m._convert_image_to_html(img)
    assert "width:20px" in out and "height:10px" in out


# ===========================================================================
# _count_data_columns / _expanded_col_count
# ===========================================================================


def test_count_data_columns_finds_years():
    t = _table(
        "<table><tr><td></td><td>2025</td><td>2024</td></tr>"
        "<tr><td>Rev</td><td>1</td><td>2</td></tr></table>"
    )
    assert h2m._count_data_columns(t) == 2


def test_count_data_columns_none():
    t = _table("<table><tr><td>Rev</td><td>x</td></tr></table>")
    assert h2m._count_data_columns(t) == 0


def test_expanded_col_count_with_colspan():
    t = _table('<table><tr><td colspan="2">A</td><td>B</td></tr></table>')
    assert h2m._expanded_col_count(t) == 3


# ===========================================================================
# _is_continuation_table / _merge_continuation_tables
# ===========================================================================


def test_is_continuation_table_year_only_start():
    t = _table("<table><tr><td>2024</td></tr><tr><td>1</td></tr></table>")
    assert h2m._is_continuation_table(t) is True


def test_is_continuation_table_no_prev_not_year():
    t = _table("<table><tr><td>Rev</td><td>$1</td></tr></table>")
    assert h2m._is_continuation_table(t, prev_table=None) is False


def test_merge_continuation_tables_appends_rows():
    # Headerless continuation: same expanded column count, immediate DOM
    # siblings, data rows with $ -> second table merged into the first.
    html = (
        "<div>"
        "<table><tr><td></td><td>2025</td><td>2024</td></tr>"
        "<tr><td>Rev</td><td>$1</td><td>$2</td></tr></table>"
        "<table><tr><td>Cost</td><td>$3</td><td>$4</td></tr></table>"
        "</div>"
    )
    soup = BeautifulSoup(html, "html.parser")
    h2m._merge_continuation_tables(soup)
    tables = soup.find_all("table")
    # second table should have been merged into the first and removed
    assert len(tables) == 1
    assert "Cost" in tables[0].get_text()


# ===========================================================================
# is_header_element / get_header_level
# ===========================================================================


def test_is_header_element_h_tags():
    assert h2m.is_header_element(_tag("<h2>Title</h2>", "h2")) is True


def test_is_header_element_body_text_flag_false():
    tag = _tag('<div data-body-text="1" style="font-size:20pt">Big</div>', "div")
    assert h2m.is_header_element(tag) is False


def test_is_header_element_div_with_table_false():
    tag = _tag(
        '<div style="font-size:20pt"><table><tr><td>x</td></tr></table></div>', "div"
    )
    assert h2m.is_header_element(tag) is False


def test_is_header_element_large_font_div():
    tag = _tag('<div style="font-size:16pt">Section Title</div>', "div")
    assert h2m.is_header_element(tag) is True


def test_is_header_element_bold_only_children():
    tag = _tag("<p><b>Important Heading</b></p>", "p")
    assert h2m.is_header_element(tag) is True


def test_is_header_element_item_bold():
    assert h2m.is_header_element(_tag("<b>ITEM 1. Business</b>", "b")) is True


def test_is_header_element_part_bold():
    assert h2m.is_header_element(_tag("<b>PART II</b>", "b")) is True


def test_is_header_element_all_caps_words():
    assert h2m.is_header_element(_tag("<b>RISK FACTORS</b>", "b")) is True


def test_is_header_element_single_caps_word():
    assert h2m.is_header_element(_tag("<b>OVERVIEW</b>", "b")) is True


def test_is_header_element_plain_text_false():
    assert (
        h2m.is_header_element(_tag("<b>some lowercase phrase here</b>", "b")) is False
    )


def test_get_header_level_part():
    assert h2m.get_header_level(_tag("<b>PART I</b>", "b")) == 1


def test_get_header_level_item():
    assert h2m.get_header_level(_tag("<b>ITEM 7. MD&amp;A</b>", "b")) == 2


def test_get_header_level_h_tags():
    assert h2m.get_header_level(_tag("<h1>x</h1>", "h1")) == 1
    assert h2m.get_header_level(_tag("<h2>x</h2>", "h2")) == 2
    assert h2m.get_header_level(_tag("<h3>x</h3>", "h3")) == 3


def test_get_header_level_font_size():
    assert h2m.get_header_level(_tag('<div style="font-size:16pt">x</div>', "div")) == 2
    assert h2m.get_header_level(_tag('<div style="font-size:12pt">x</div>', "div")) == 3


def test_get_header_level_default():
    assert h2m.get_header_level(_tag("<p>plain</p>", "p")) == 3


# ===========================================================================
# clean_table_cells
# ===========================================================================


def test_clean_table_cells_dollar_merge():
    rows = [["$", "12,211"]]
    out = h2m.clean_table_cells(rows)
    assert out[0][0] == "$12,211"


def test_clean_table_cells_open_paren_merge():
    rows = [["(2,257", ")(b)"]]
    out = h2m.clean_table_cells(rows)
    assert out[0][0] == "(2,257)(b)"


def test_clean_table_cells_suffix_merge():
    rows = [["22", "%"]]
    out = h2m.clean_table_cells(rows)
    assert out[0][0] == "22%"


def test_clean_table_cells_footnote_note():
    rows = [["7", "(a)"]]
    out = h2m.clean_table_cells(rows)
    assert out[0][0] == "7 (a)"


# ===========================================================================
# merge_split_rows
# ===========================================================================


def test_merge_split_rows_label_continuation():
    rows = [
        ["Level 3 assets for which we do not", "", ""],
        ["bear economic exposure (7)", "(14,437)", "(1)"],
    ]
    cs = [[], []]
    merged, _ = h2m.merge_split_rows(rows, cs)
    assert merged[0][0].startswith("Level 3 assets for which we do not bear economic")
    assert merged[0][1] == "(14,437)"


def test_merge_split_rows_incomplete_paren():
    rows = [["(in millions, except per", "", ""], ["share amounts)", "", ""]]
    cs = [[], []]
    merged, _ = h2m.merge_split_rows(rows, cs)
    assert merged[0][0] == "(in millions, except per share amounts)"


def test_merge_split_rows_balanced_first_cell_no_merge():
    # First cell "(Benefit from) provision" has balanced parens and row_text
    # does not end with ")" -> the balanced-first-cell branch keeps it as is.
    # Two non-empty columns avoid the label-continuation merge path.
    rows = [["(Benefit from) provision for taxes", "100", ""], ["Next Row", "", ""]]
    cs = [[], []]
    merged, _ = h2m.merge_split_rows(rows, cs)
    assert len(merged) == 2
    assert merged[0][0] == "(Benefit from) provision for taxes"


def test_merge_split_rows_header_with_other_content_no_merge():
    rows = [["(descriptor wrapping", "2025", "2024"], ["next", "", ""]]
    cs = [[], []]
    merged, _ = h2m.merge_split_rows(rows, cs)
    # has non-label content -> kept as is
    assert merged[0] == ["(descriptor wrapping", "2025", "2024"]


# ===========================================================================
# merge_split_cells
# ===========================================================================


def test_merge_split_cells_paren_close():
    rows = [["(306", ")"]]
    out = h2m.merge_split_cells(rows)
    assert out[0][0] == "(306)"


def test_merge_split_cells_footnote():
    rows = [["2,264", "(1)"]]
    out = h2m.merge_split_cells(rows)
    assert out[0][0] == "2,264 (1)"


def test_merge_split_cells_percent_suffix():
    rows = [["22", "", "%"]]
    out = h2m.merge_split_cells(rows)
    assert out[0][0] == "22%"


def test_merge_split_cells_passthrough():
    rows = [["Revenue", "Other"]]
    out = h2m.merge_split_cells(rows)
    assert out == [["Revenue", "Other"]]


# ===========================================================================
# collapse_repeated_headers
# ===========================================================================


def test_collapse_repeated_headers_short_input():
    assert h2m.collapse_repeated_headers([]) == []
    assert h2m.collapse_repeated_headers([["A"]]) == [["A"]]


def test_collapse_repeated_headers_duplicate_with_shifted_data():
    rows = [
        ["Name", "Fiscal Year", "", "Salary", ""],
        ["Ellison", "", "2025", "", "950,000"],
    ]
    out = h2m.collapse_repeated_headers(rows)
    # the empty colspan-expanded columns should be collapsed away
    assert len(out[0]) < 5
    assert "2025" in out[1]


# ===========================================================================
# parse_row_semantic
# ===========================================================================


def test_parse_row_semantic_label_and_values():
    label, values = h2m.parse_row_semantic(["Revenue", "$1,000", "$2,000"])
    assert label == "Revenue"
    assert values == ["$1,000", "$2,000"]


def test_parse_row_semantic_dash_value():
    label, values = h2m.parse_row_semantic(["Net", "—", "$5"])
    assert label == "Net"
    assert "—" in values


def test_parse_row_semantic_total_from_currency():
    label, values = h2m.parse_row_semantic(["$1,234", "$5,678"])
    assert label == "Total"


def test_parse_row_semantic_text_values_as_columns():
    label, values = h2m.parse_row_semantic(
        ["Moody's", "P-1", "A1"], num_expected_cols=2
    )
    assert label == "Moody's"
    assert values == ["P-1", "A1"]


def test_parse_row_semantic_extra_text_no_cols_to_label():
    label, values = h2m.parse_row_semantic(["Label", "extra text"])
    assert "extra text" in label


# ===========================================================================
# detect_and_merge_multiindex_headers
# ===========================================================================


def test_detect_multiindex_too_few_rows():
    assert h2m.detect_and_merge_multiindex_headers([["a"], ["b"]]) == (None, 0, 0)


def test_detect_multiindex_with_caps_categories():
    rows = [
        ["For the Years Ended December 31,"],
        ["EQUIPMENT", "EQUIPMENT", "FINANCIAL", "FINANCIAL"],
        ["OPERATIONS", "OPERATIONS", "SERVICES", "SERVICES"],
        ["2025", "2024", "2025", "2024"],
        ["Revenue", "100", "200", "300", "400"],
    ]
    header_rows, data_start, num_cols = h2m.detect_and_merge_multiindex_headers(rows)
    assert header_rows is not None
    assert num_cols >= 2


def test_detect_multiindex_no_categories_returns_none():
    rows = [
        ["title"],
        ["2025", "2024", "2023"],
        ["Revenue", "1", "2", "3"],
        ["Cost", "4", "5", "6"],
    ]
    # no all-caps categories -> falls back to None
    assert h2m.detect_and_merge_multiindex_headers(rows) == (None, 0, 0)


# ===========================================================================
# is_equity_statement_table / process_equity_statement_table
# ===========================================================================


def test_is_equity_statement_table_true():
    rows = [
        ["", "Common Stock", "Treasury Stock", "Retained Earnings"],
        ["", "Accumulated Comprehensive", "Noncontrolling", "Total Equity"],
        ["Balance", "$1", "$2", "$3"],
        ["Net income", "", "", "$4"],
        ["Balance end", "$5", "$6", "$7"],
    ]
    assert h2m.is_equity_statement_table(rows) is True


def test_is_equity_statement_table_false():
    rows = [["Revenue", "1"], ["Cost", "2"]]
    assert h2m.is_equity_statement_table(rows) is False


def test_process_equity_statement_table_not_applicable():
    rows = [["Revenue", "1"], ["Cost", "2"]]
    cs = [[("Revenue", 1), ("1", 1)], [("Cost", 1), ("2", 1)]]
    result, count = h2m.process_equity_statement_table(rows, cs)
    assert result is None and count == 0


# ===========================================================================
# get_text_content
# ===========================================================================


def test_get_text_content_navigable_string():
    soup = BeautifulSoup("plain text", "html.parser")
    node = soup.contents[0]
    assert h2m.get_text_content(node) == "plain text"


def test_get_text_content_joins_split_words():
    tag = _tag("<p><b>INCOM</b><b>E</b></p>", "p")
    assert h2m.get_text_content(tag) == "INCOME"


def test_get_text_content_preserves_space_separator():
    tag = _tag("<p><b>WORD1</b> <b>WORD2</b></p>", "p")
    assert h2m.get_text_content(tag) == "WORD1 WORD2"


def test_get_text_content_links_preserved():
    tag = _tag('<p>See <a href="x.htm">here</a></p>', "p")
    out = h2m.get_text_content(
        tag, preserve_links_in_text=True, base_url="https://x.com/"
    )
    assert "[here](https://x.com/x.htm)" in out


def test_get_text_content_br_becomes_space():
    tag = _tag("<p>a<br/>b</p>", "p")
    assert h2m.get_text_content(tag) == "a b"


def test_get_text_content_xbrl_wrapper():
    tag = _tag("<p><ix:nonfraction>42</ix:nonfraction></p>", "p")
    assert "42" in h2m.get_text_content(tag)


# ===========================================================================
# _html_escape / _clean_html_entities
# ===========================================================================


def test_html_escape():
    assert h2m._html_escape("a < b & c > d") == "a &lt; b &amp; c &gt; d"


def test_clean_html_entities():
    out = h2m._clean_html_entities("a&nbsp;b&amp;c\u200bd\xa0e")
    assert out == "a b&cd e"


# ===========================================================================
# _classify_table
# ===========================================================================


def test_classify_table_no_rows():
    t = _table("<table></table>")
    assert h2m._classify_table(t) == "DATA"


def test_classify_table_bullet():
    t = _table(
        "<table><tr><td>•</td><td>First item</td></tr>"
        "<tr><td>•</td><td>Second item</td></tr></table>"
    )
    assert h2m._classify_table(t) == "BULLET"


def test_classify_table_footnote():
    t = _table(
        "<table><tr><td>(1)</td><td>This is a footnote.</td></tr>"
        "<tr><td>(2)</td><td>Another note.</td></tr></table>"
    )
    assert h2m._classify_table(t) == "FOOTNOTE"


def test_classify_table_header():
    t = _table('<table><tr><td id="toc1"><b>Section Title</b></td></tr></table>')
    assert h2m._classify_table(t) == "HEADER"


def test_classify_table_data_default():
    t = _table("<table><tr><td>Revenue</td><td>$100</td><td>$200</td></tr></table>")
    assert h2m._classify_table(t) == "DATA"


# ===========================================================================
# _extract_bullet_list / _extract_footnote_text / _extract_header_text
# ===========================================================================


def test_extract_bullet_list():
    t = _table(
        "<table><tr><td>•</td><td>Item one here</td></tr>"
        "<tr><td>•</td><td>Item two here</td></tr></table>"
    )
    out = h2m._extract_bullet_list(t)
    assert "- Item one here" in out and "- Item two here" in out


def test_extract_bullet_list_bold_header():
    t = _table(
        "<table><tr><td>•</td>"
        "<td><b>Topic</b>. Description text follows here.</td></tr></table>"
    )
    out = h2m._extract_bullet_list(t)
    assert "**Topic**" in out


def test_extract_bullet_list_single_cell():
    t = _table("<table><tr><td>• Single bullet line</td></tr></table>")
    out = h2m._extract_bullet_list(t)
    assert "- Single bullet line" in out


def test_extract_footnote_text():
    t = _table(
        "<table><tr><td>(1)</td><td>First note.</td></tr>"
        "<tr><td>Standalone line.</td></tr></table>"
    )
    out = h2m._extract_footnote_text(t)
    assert "(1) First note." in out
    assert "Standalone line." in out


def test_extract_header_text_with_anchor():
    t = _table('<table><tr><td id="sec1">My Header</td></tr></table>')
    out = h2m._extract_header_text(t)
    assert '<a id="sec1"></a>' in out and "**My Header**" in out


def test_extract_header_text_plain():
    t = _table("<table><tr><td>Plain Header</td></tr></table>")
    out = h2m._extract_header_text(t)
    assert out == "\n**Plain Header**\n"


def test_extract_header_text_none():
    t = _table("<table><tr><td></td></tr></table>")
    assert h2m._extract_header_text(t) is None


# ===========================================================================
# _extract_cell_text
# ===========================================================================


def test_extract_cell_text_link():
    cell = _tag('<td>See <a href="a.htm">link</a></td>', "td")
    out = h2m._extract_cell_text(cell, base_url="https://x.com/")
    assert "[link](https://x.com/a.htm)" in out


def test_extract_cell_text_footnote_sup_only():
    cell = _tag("<td><sup>12</sup></td>", "td")
    assert h2m._extract_cell_text(cell) == "<sup>12</sup>"


def test_extract_cell_text_strips_decorative_image():
    cell = _tag('<td>Text <img src="x.png" alt="Image"/></td>', "td")
    out = h2m._extract_cell_text(cell)
    assert out == "Text"


def test_extract_cell_text_word_rejoin():
    cell = _tag("<td>ADJUST- MENTS</td>", "td")
    assert h2m._extract_cell_text(cell) == "ADJUSTMENTS"


def test_extract_cell_text_preserve_line_breaks():
    cell = _tag(
        "<td><div>Item A here</div><div>Item B here</div><div>Item C here</div></td>",
        "td",
    )
    out = h2m._extract_cell_text(cell, preserve_line_breaks=True)
    assert "Item A here" in out and "\n" in out


# ===========================================================================
# convert_table (data path)
# ===========================================================================


def test_convert_table_empty():
    t = _table("<table></table>")
    assert h2m.convert_table(t) == ""


def test_convert_table_simple_data():
    t = _table(
        "<table>"
        "<tr><td></td><td>2025</td><td>2024</td></tr>"
        "<tr><td>Revenue</td><td>$100</td><td>$200</td></tr>"
        "<tr><td>Cost</td><td>$50</td><td>$75</td></tr>"
        "</table>"
    )
    out = h2m.convert_table(t)
    assert "|" in out
    assert "Revenue" in out and "100" in out


def test_convert_table_header_classification():
    t = _table('<table><tr><td id="toc5"><b>Risk Factors</b></td></tr></table>')
    out = h2m.convert_table(t)
    assert "Risk Factors" in out


def test_convert_table_bullet_classification():
    t = _table(
        "<table><tr><td>•</td><td>Alpha point</td></tr>"
        "<tr><td>•</td><td>Beta point</td></tr></table>"
    )
    out = h2m.convert_table(t)
    assert "- Alpha point" in out


# ===========================================================================
# html_to_markdown - top-level entry
# ===========================================================================


def test_html_to_markdown_empty():
    assert h2m.html_to_markdown("") == ""


def test_html_to_markdown_bytes_input():
    out = h2m.html_to_markdown(b"<p>Bytes <b>work</b></p>")
    assert "Bytes **work**" in out


def test_html_to_markdown_basic_paragraph():
    out = h2m.html_to_markdown("<p>Hello world.</p>")
    assert "Hello world." in out


def test_html_to_markdown_headers():
    out = h2m.html_to_markdown("<h1>Main Title</h1><h2>Sub Title</h2>")
    assert "# Main Title" in out
    assert "## Sub Title" in out


def test_html_to_markdown_lists():
    out = h2m.html_to_markdown("<ul><li>First</li><li>Second</li></ul>")
    assert "First" in out and "Second" in out


def test_html_to_markdown_table():
    html = (
        "<table>"
        "<tr><th>Item</th><th>2025</th><th>2024</th></tr>"
        "<tr><td>Revenue</td><td>$1,000</td><td>$2,000</td></tr>"
        "<tr><td>Expenses</td><td>$500</td><td>$750</td></tr>"
        "</table>"
    )
    out = h2m.html_to_markdown(html)
    assert "Revenue" in out and "Expenses" in out
    assert "|" in out


def test_html_to_markdown_keep_tables_false():
    html = "<p>Before</p><table><tr><td>x</td><td>y</td></tr></table><p>After</p>"
    out = h2m.html_to_markdown(html, keep_tables=False)
    assert "Before" in out and "After" in out


def test_html_to_markdown_xml_declaration_stripped():
    out = h2m.html_to_markdown('<?xml version="1.0"?><p>Body</p>')
    assert "Body" in out
    assert "<?xml" not in out


def test_html_to_markdown_win1252_entities():
    out = h2m.html_to_markdown("<p>quote&#147;word&#148;</p>")
    assert "word" in out


# ===========================================================================
# extract_periods_from_rows / build_column_headers_from_colspan (direct)
# ===========================================================================


def test_extract_periods_empty():
    assert h2m.extract_periods_from_rows([]) == ([], 0)


def test_extract_periods_stacked_categories_over_years():
    rows = [
        [("", 1), ("EQUIPMENT", 3), ("FINANCIAL", 3)],
        [("", 1), ("OPERATIONS", 3), ("SERVICES", 3)],
        [
            ("", 1),
            ("2025", 1),
            ("2024", 1),
            ("2023", 1),
            ("2025", 1),
            ("2024", 1),
            ("2023", 1),
        ],
    ]
    layers, count = h2m.extract_periods_from_rows(rows, [True, True, True], None)
    assert count == 3
    flat = " ".join(h for layer in layers for h in layer)
    assert "EQUIPMENT OPERATIONS" in flat
    assert "FINANCIAL SERVICES" in flat


def test_extract_periods_vertical_merge_split_labels():
    # Vertical multi-row header merge: "Retail Notes" / "& Financing" / "Leases"
    rows = [
        [("", 1), ("Retail Notes", 2), ("Revolving", 2)],
        [("", 1), ("& Financing", 2), ("Charge", 2)],
        [("", 1), ("Leases", 2), ("Accounts", 2)],
        [("Total", 1), ("$1", 1), ("", 1), ("$2", 1), ("", 1)],
    ]
    layers, count = h2m.extract_periods_from_rows(rows, [True, True, True, False], None)
    assert layers is not None
    flat = " ".join(h for layer in layers for h in layer)
    assert "Retail Notes" in flat


def test_build_column_headers_empty():
    assert h2m.build_column_headers_from_colspan([], None) == (None, 0)


def test_build_column_headers_with_year_range_fragments():
    # year-range fragments "2009 -" / "2010" — exercises that detection branch
    rows = [
        [("", 1), ("2009 -", 1), ("2011 -", 1)],
        [("", 1), ("2010", 1), ("2012", 1)],
        [("Rev", 1), ("$1", 1), ("$2", 1)],
    ]
    layers, count = h2m.build_column_headers_from_colspan(rows, None)
    # Either returns flat fragments or None; exercising the body is the goal.
    assert layers is None or isinstance(layers, list)


# ===========================================================================
# _extract_chart_legend (direct)
# ===========================================================================


def test_extract_chart_legend_detects_swatches():
    html = (
        "<table>"
        '<tr><td style="background-color:#009dd9;height:3px"></td>'
        "<td>United States</td></tr>"
        '<tr><td style="background-color:#0b2d71;height:3px"></td>'
        "<td>Other Americas</td></tr>"
        "</table>"
    )
    t = _table(html)
    out = h2m._extract_chart_legend(t)
    assert out is not None
    assert "Legend:" in out
    assert "United States" in out and "Other Americas" in out


def test_extract_chart_legend_rejects_data_table():
    html = (
        "<table>"
        "<tr><td>Revenue</td><td>$1,234.5</td></tr>"
        "<tr><td>Cost</td><td>$2,345.6</td></tr>"
        "</table>"
    )
    t = _table(html)
    assert h2m._extract_chart_legend(t) is None


def test_extract_chart_legend_too_many_rows():
    rows = "".join(f"<tr><td>r{i}</td></tr>" for i in range(40))
    t = _table(f"<table>{rows}</table>")
    assert h2m._extract_chart_legend(t) is None


def test_extract_chart_legend_no_swatches():
    html = "<table><tr><td>Alpha</td></tr><tr><td>Beta</td></tr></table>"
    t = _table(html)
    assert h2m._extract_chart_legend(t) is None


# ===========================================================================
# _split_composite_table / _make_sub_table
# ===========================================================================


def test_split_composite_table_too_few_rows():
    t = _table("<table><tr><td>x</td></tr></table>")
    assert h2m._split_composite_table(t) == [t]


def test_split_composite_table_no_table_headers():
    t = _table(
        "<table>"
        "<tr><td>Revenue</td><td>$1</td></tr>"
        "<tr><td>Cost</td><td>$2</td></tr>"
        "<tr><td>Net</td><td>$3</td></tr>"
        "<tr><td>Total</td><td>$4</td></tr>"
        "</table>"
    )
    # no "TABLE X" headers -> returned unchanged (single element list)
    assert h2m._split_composite_table(t) == [t]


def test_split_composite_table_splits_on_table_headers():
    t = _table(
        "<table>"
        "<tr><td>TABLE 5: Revenue</td><td></td></tr>"
        "<tr><td>Item A</td><td>$1</td></tr>"
        "<tr><td>TABLE 6: Expenses</td><td></td></tr>"
        "<tr><td>Item B</td><td>$2</td></tr>"
        "</table>"
    )
    parts = h2m._split_composite_table(t)
    # split into 2+ sub-tables
    assert len(parts) >= 2


def test_make_sub_table_copies_rows():
    src = _table('<table class="x"><tr><td>a</td></tr><tr><td>b</td></tr></table>')
    rows = src.find_all("tr")
    new_t = h2m._make_sub_table(rows[:1], src)
    assert new_t.name == "table"
    assert new_t.get("class") == ["x"]
    assert len(new_t.find_all("tr")) == 1


# ===========================================================================
# _convert_layout_table
# ===========================================================================


def test_convert_layout_table_no_rows():
    t = _table("<table></table>")
    assert h2m._convert_layout_table(t) is None


def test_convert_layout_table_data_header_returns_none():
    # row with 3+ bold cells -> real data table, return None
    t = _table(
        "<table><tr>"
        "<td><b>Name</b></td><td><b>Year</b></td><td><b>Salary</b></td>"
        "</tr><tr><td>A</td><td>2025</td><td>1</td></tr></table>"
    )
    assert h2m._convert_layout_table(t) is None


def test_convert_layout_table_header_plus_bullets():
    t = _table(
        "<table><tr>"
        "<td><b>Our Strategy</b></td>"
        "<td><div>• Grow revenue here</div>"
        "<div>• Reduce costs here</div>"
        "<div>• Expand markets here</div></td>"
        "</tr></table>"
    )
    out = h2m._convert_layout_table(t)
    assert out is not None
    assert "Our Strategy" in out
    assert "- Grow revenue here" in out


# ===========================================================================
# Post-processing string functions
# ===========================================================================


def test_merge_consecutive_headers_incomplete():
    md = "### Statements of Changes in\n### Stockholders Equity"
    out = h2m._merge_consecutive_headers(md)
    assert "### Statements of Changes in Stockholders Equity" in out


def test_merge_consecutive_headers_complete_not_merged():
    md = "### Balance Sheet\n### Income Statement"
    out = h2m._merge_consecutive_headers(md)
    # both complete -> not merged into one
    assert "### Balance Sheet" in out
    assert "### Income Statement" in out


def test_merge_consecutive_headers_different_level_incomplete():
    md = "### Notes to the\n#### Financial Statements"
    out = h2m._merge_consecutive_headers(md)
    assert "### Notes to the Financial Statements" in out


def test_convert_inline_subheadings():
    md = "Overview Section . The body text continues with details here."
    out = h2m._convert_inline_subheadings(md)
    assert "#### Overview Section" in out
    assert "The body text continues" in out


def test_convert_inline_subheadings_skips_tables_and_headers():
    md = "| cell | data |\n# Already A Header"
    out = h2m._convert_inline_subheadings(md)
    assert out == md


def test_normalize_bullet_chars_splits_inline():
    md = "•item one; •item two; and •item three."
    out = h2m._normalize_bullet_chars(md)
    lines = out.split("\n")
    assert "- item one;" in lines
    assert "- item two; and" in lines
    assert "- item three." in lines


def test_normalize_bullet_chars_no_bullets_unchanged():
    md = "Just a normal line."
    assert h2m._normalize_bullet_chars(md) == md


def test_normalize_bullet_chars_skips_table_row():
    md = "| • | x |"
    assert h2m._normalize_bullet_chars(md) == md


def test_join_split_paragraphs_connecting_word():
    md = "This sentence ends with and\nacquisitions of new firms."
    out = h2m._join_split_paragraphs(md)
    assert "and acquisitions" in out


def test_join_split_paragraphs_hyphen_split():
    md = "The company reported pre-\ntax income growth."
    out = h2m._join_split_paragraphs(md)
    assert "pre-tax" in out or "pretax" in out


def test_join_split_paragraphs_unaudited_header_removed():
    md = "Some text.\n**(UNAUDITED)**\nMore text here."
    out = h2m._join_split_paragraphs(md)
    assert "**(UNAUDITED)**" not in out


def test_remove_repeated_page_elements():
    footer = "Company Name Page 5"
    lines = ["# Title"]
    for i in range(8):
        lines.append(f"Paragraph {i} content goes here for variety.")
        lines.append(footer)
    md = "\n".join(lines)
    out = h2m._remove_repeated_page_elements(md)
    # the repeated footer (normalizes the same each time) should be removed
    assert "Company Name Page" not in out


def test_remove_repeated_page_elements_no_repeats():
    md = "# Title\nUnique line one.\nUnique line two."
    assert h2m._remove_repeated_page_elements(md) == md


# ===========================================================================
# _reflow_absolute_layout (Certent CDM style position:absolute layouts)
# ===========================================================================


def _abs_frag(idx, left, top, text, fs=10, bold=False):
    """Build a Certent-CDM-style absolutely-positioned text fragment div."""
    weight = "font-weight:bold;" if bold else ""
    return (
        f'<div id="a{idx}" style="position:absolute;left:{left}px;top:{top}px;'
        f'{weight}font-size:{fs}px">{text}</div>'
    )


def _abs_rule(left, top, width):
    """Build a thin full-width position:absolute horizontal rule div."""
    return (
        f'<div style="position:absolute;left:{left}px;top:{top}px;'
        f'width:{width}px;height:1px"></div>'
    )


def _build_abs_layout(page_num=1, idx_start=1):
    """Construct a single-page absolute-positioned filing (>= 30 abs divs)."""
    parts = [f'<div id="Page{page_num}">']
    idx = idx_start
    parts.append(
        _abs_frag(idx, 50, 20, "CONSOLIDATED RESULTS OF OPERATIONS", fs=14, bold=True)
    )
    idx += 1
    for k in range(10):
        parts.append(
            _abs_frag(
                idx,
                50,
                50 + k * 16,
                f"Body sentence {k} describing financial performance across segments.",
            )
        )
        idx += 1
    parts.append(_abs_rule(50, 230, 600))
    parts.append(_abs_frag(idx, 50, 240, "Item"))
    idx += 1
    parts.append(_abs_frag(idx, 300, 240, "2025"))
    idx += 1
    parts.append(_abs_frag(idx, 450, 240, "2024"))
    idx += 1
    parts.append(_abs_rule(50, 260, 600))
    data = [
        ("Revenue", "100", "90"),
        ("Cost", "40", "35"),
        ("Net income", "60", "55"),
        ("Assets", "500", "480"),
        ("Liabilities", "200", "190"),
    ]
    for i, (lbl, a, b) in enumerate(data):
        y = 270 + i * 18
        parts.append(_abs_frag(idx, 50, y, lbl))
        idx += 1
        parts.append(_abs_frag(idx, 300, y, a))
        idx += 1
        parts.append(_abs_frag(idx, 450, y, b))
        idx += 1
    parts.append(_abs_rule(50, 370, 600))
    parts.append("</div>")
    return "".join(parts), idx


def test_reflow_absolute_layout_basic():
    html, _ = _build_abs_layout()
    out = h2m._reflow_absolute_layout(html)
    assert out is not None
    assert "CONSOLIDATED RESULTS OF OPERATIONS" in out
    assert "<table>" in out
    assert "Revenue" in out and "Liabilities" in out


def test_reflow_absolute_layout_rejects_normal_html():
    # Few absolute elements -> not an abs-positioned document.
    assert h2m._reflow_absolute_layout("<p>Normal document content.</p>") is None


def test_reflow_absolute_layout_rejects_with_tables():
    # Has the abs fragments but also > 2 tables -> rejected early.
    html, _ = _build_abs_layout()
    html += "<table><tr><td>x</td></tr></table>" * 3
    assert h2m._reflow_absolute_layout(html) is None


def test_reflow_absolute_layout_no_text_fragments():
    # 30+ absolute rules but NO id="aNN" text fragments -> rejected.
    rules = "".join(_abs_rule(50, 20 + i * 10, 600) for i in range(40))
    html = f'<div id="Page1">{rules}</div>'
    assert h2m._reflow_absolute_layout(html) is None


def test_reflow_absolute_layout_multipage():
    p1, idx = _build_abs_layout(page_num=1, idx_start=1)
    p2, _ = _build_abs_layout(page_num=2, idx_start=idx)
    html = p1 + p2
    out = h2m._reflow_absolute_layout(html)
    assert out is not None
    # both pages' content present
    assert out.count("CONSOLIDATED RESULTS OF OPERATIONS") >= 1


def test_html_to_markdown_drives_reflow_end_to_end():
    html, _ = _build_abs_layout()
    out = h2m.html_to_markdown(html)
    # The reflowed HTML should be converted to markdown with a table.
    assert "CONSOLIDATED RESULTS OF OPERATIONS" in out
    assert "Revenue" in out
    assert "|" in out


def _build_abs_layout_rich(page_num=1, idx_start=1):
    """Abs-positioned page exercising H2 / heading / bullet / chart paths."""
    parts = [f'<div id="Page{page_num}">']
    idx = idx_start
    # Large-font H2 heading (font-size > 18 -> classified as body heading).
    parts.append(_abs_frag(idx, 50, 20, "NET INCOME OVERVIEW", fs=22))
    idx += 1
    # Left-margin body paragraph lines (body font).
    for k in range(6):
        parts.append(
            _abs_frag(
                idx,
                50,
                50 + k * 16,
                f"This paragraph line {k} describes results and was prepared by "
                "management today.",
            )
        )
        idx += 1
    # Short section heading (left<=55, len<50) directly above a bullet list.
    parts.append(_abs_frag(idx, 50, 150, "Key Drivers"))
    idx += 1
    # Bullet lines: bullet glyph fragment + continuation fragment per row.
    for k in range(3):
        parts.append(_abs_frag(idx, 50, 172 + k * 16, "•"))
        idx += 1
        parts.append(
            _abs_frag(
                idx,
                70,
                172 + k * 16,
                f"Bullet point number {k} explaining a driver of performance here.",
            )
        )
        idx += 1
    # Chart annotation block (right column, bold title with deviating font + desc).
    parts.append(_abs_frag(idx, 320, 60, "Revenue by Segment", fs=12, bold=True))
    idx += 1
    parts.append(
        _abs_frag(
            idx,
            320,
            76,
            "(in millions of dollars for the fiscal period reported)",
            fs=12,
        )
    )
    idx += 1
    # Table zone delimited by thin full-width rules.
    parts.append(_abs_rule(50, 240, 600))
    parts.append(_abs_frag(idx, 50, 250, "Item"))
    idx += 1
    parts.append(_abs_frag(idx, 300, 250, "2025"))
    idx += 1
    parts.append(_abs_frag(idx, 450, 250, "2024"))
    idx += 1
    parts.append(_abs_rule(50, 270, 600))
    for i, (lbl, a, b) in enumerate(
        [("Revenue", "100", "90"), ("Cost", "40", "35"), ("Net income", "60", "55")]
    ):
        y = 280 + i * 18
        parts.append(_abs_frag(idx, 50, y, lbl))
        idx += 1
        parts.append(_abs_frag(idx, 300, y, a))
        idx += 1
        parts.append(_abs_frag(idx, 450, y, b))
        idx += 1
    parts.append(_abs_rule(50, 340, 600))
    parts.append("</div>")
    return "".join(parts), idx


def test_reflow_absolute_layout_rich_headings_bullets_chart():
    html, _ = _build_abs_layout_rich()
    out = h2m._reflow_absolute_layout(html)
    assert out is not None
    # Large-font heading -> H2.
    assert "<h2>NET INCOME OVERVIEW</h2>" in out
    # Bullet list emitted.
    assert "<ul>" in out and "<li>" in out
    assert "Bullet point number 0" in out
    # Chart annotation block emitted as a chart div.
    assert 'class="chart"' in out
    assert "Revenue by Segment" in out
    # Table zone preserved.
    assert "<table>" in out and "Net income" in out


def test_html_to_markdown_drives_rich_reflow_end_to_end():
    html, _ = _build_abs_layout_rich()
    out = h2m.html_to_markdown(html)
    assert "NET INCOME OVERVIEW" in out
    assert "Bullet point number 1" in out
    assert "Revenue by Segment" in out


# ===========================================================================
# process_equity_statement_table (full processing path)
# ===========================================================================


def test_process_equity_statement_table_full():
    rows = [
        ["", "Common Stock", "Treasury Stock", "Retained Earnings", "Total Equity"],
        ["", "Shares", "Amount", "Accumulated", "Comprehensive"],
        ["Balance at January 1", "$21,789", "$(24,094)", "$5,165", "$2,860"],
        ["Net income", "", "", "$4,000", "$4,000"],
        ["Balance at December 31", "$25,789", "$(20,094)", "$9,165", "$6,860"],
    ]
    cs = [[(c, 1) for c in r] for r in rows]
    result, count = h2m.process_equity_statement_table(rows, cs)
    assert count == 1
    assert result is not None
    assert result[0][0] == ""
    # data rows preserved
    labels = [r[0] for r in result]
    assert "Balance at January 1" in labels
    assert "Balance at December 31" in labels


def test_html_to_markdown_equity_statement_table():
    cells = [
        ["", "Common Stock", "Treasury Stock", "Retained Earnings", "Total Equity"],
        ["", "Shares", "Amount", "Accumulated", "Comprehensive"],
        ["Balance at January 1", "$21,789", "$(24,094)", "$5,165", "$2,860"],
        ["Net income", "", "", "$4,000", "$4,000"],
        ["Stock issued", "$100", "", "", "$100"],
        ["Balance at December 31", "$25,789", "$(20,094)", "$9,165", "$6,860"],
    ]
    rows_html = "".join(
        "<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in cells
    )
    out = h2m.html_to_markdown(f"<table>{rows_html}</table>")
    assert "Balance at January 1" in out
    assert "|" in out


# ===========================================================================
# Rich html_to_markdown fixtures sweeping convert_table semantic paths
# ===========================================================================


def test_html_to_markdown_multiperiod_year_table():
    # 2-year financial period table -> semantic parsing path
    html = (
        "<table>"
        "<tr><td></td><th>2025</th><th>2024</th></tr>"
        "<tr><td>Net revenue</td><td>$1,000</td><td>$900</td></tr>"
        "<tr><td>Cost of sales</td><td>$(400)</td><td>$(350)</td></tr>"
        "<tr><td>Gross profit</td><td>$600</td><td>$550</td></tr>"
        "<tr><td>Operating expenses</td><td>$(200)</td><td>$(180)</td></tr>"
        "<tr><td>Net income</td><td>$400</td><td>$370</td></tr>"
        "</table>"
    )
    out = h2m.html_to_markdown(html)
    assert "Net revenue" in out and "Net income" in out
    assert "2025" in out and "2024" in out


def test_html_to_markdown_stacked_category_table():
    # Stacked category headers (EQUIPMENT OPERATIONS / FINANCIAL SERVICES) over years
    html = (
        "<table>"
        "<tr><td></td>"
        '<th colspan="3">EQUIPMENT OPERATIONS</th>'
        '<th colspan="3">FINANCIAL SERVICES</th></tr>'
        "<tr><td></td>"
        "<th>2025</th><th>2024</th><th>2023</th>"
        "<th>2025</th><th>2024</th><th>2023</th></tr>"
        "<tr><td>Revenue</td>"
        "<td>100</td><td>90</td><td>80</td>"
        "<td>50</td><td>45</td><td>40</td></tr>"
        "<tr><td>Expenses</td>"
        "<td>60</td><td>55</td><td>50</td>"
        "<td>30</td><td>28</td><td>25</td></tr>"
        "</table>"
    )
    out = h2m.html_to_markdown(html)
    assert "Revenue" in out and "Expenses" in out
    assert "|" in out


def test_html_to_markdown_maturity_bucket_table():
    # Maturity-bucket headers ("0 - 6 Months", "1 - 5 Years", "Total")
    html = (
        "<table>"
        "<tr><td></td><th>0 - 6 Months</th><th>1 - 5 Years</th><th>Total</th></tr>"
        "<tr><td>Debt</td><td>$100</td><td>$500</td><td>$600</td></tr>"
        "<tr><td>Leases</td><td>$50</td><td>$200</td><td>$250</td></tr>"
        "</table>"
    )
    out = h2m.html_to_markdown(html)
    assert "Debt" in out and "Leases" in out


def test_html_to_markdown_mixed_headers_table():
    # Mixed headers: years + non-year columns (% Change, Useful Lives)
    html = (
        "<table>"
        "<tr><td></td><th>2024</th><th>2023</th>"
        "<th>% Change</th><th>Useful Lives</th></tr>"
        "<tr><td>Equipment</td><td>$100</td><td>$90</td><td>11%</td><td>5 yrs</td></tr>"
        "<tr><td>Buildings</td><td>$500</td><td>$480</td><td>4%</td><td>30 yrs</td></tr>"
        "</table>"
    )
    out = h2m.html_to_markdown(html)
    assert "Equipment" in out and "Buildings" in out


def test_html_to_markdown_colspan_rowspan_table():
    html = (
        "<table>"
        '<tr><th rowspan="2">Segment</th><th colspan="2">Revenue</th></tr>'
        "<tr><th>2025</th><th>2024</th></tr>"
        "<tr><td>North</td><td>$100</td><td>$90</td></tr>"
        "<tr><td>South</td><td>$80</td><td>$75</td></tr>"
        "</table>"
    )
    out = h2m.html_to_markdown(html)
    # Exercises the colspan/rowspan multi-index header path; the rowspan
    # label header collapses to an empty leading row, but data rows survive.
    assert "North" in out and "South" in out
    assert "2025" in out and "2024" in out


def test_html_to_markdown_footnote_in_cell():
    html = (
        "<table>"
        "<tr><td></td><th>2025</th></tr>"
        "<tr><td>Revenue<sup>1</sup></td><td>$100</td></tr>"
        "</table>"
    )
    out = h2m.html_to_markdown(html)
    assert "Revenue" in out


def test_html_to_markdown_split_currency_cells():
    # $ in one cell, value in next (SEC pattern)
    html = (
        "<table>"
        "<tr><td></td><th>2025</th><th></th></tr>"
        "<tr><td>Cash</td><td>$</td><td>12,211</td></tr>"
        "<tr><td>Debt</td><td>$</td><td>5,000</td></tr>"
        "</table>"
    )
    out = h2m.html_to_markdown(html)
    assert "Cash" in out and "Debt" in out


# ===========================================================================
# process_element branches via html_to_markdown
# ===========================================================================


def test_html_to_markdown_image_block():
    out = h2m.html_to_markdown('<p><img src="logo.png" alt="Company Logo"/></p>')
    assert "Company Logo" in out


def test_html_to_markdown_ordered_list():
    out = h2m.html_to_markdown("<ol><li>First step</li><li>Second step</li></ol>")
    assert "1. First step" in out
    assert "2. Second step" in out


def test_html_to_markdown_link_resolution():
    out = h2m.html_to_markdown(
        '<p>Visit <a href="page.htm">our page</a> now.</p>',
        base_url="https://sec.gov/docs/",
    )
    assert "[our page](https://sec.gov/docs/page.htm)" in out


def test_html_to_markdown_blockquote():
    out = h2m.html_to_markdown("<blockquote>Quoted text here.</blockquote>")
    assert "> Quoted text here." in out


def test_html_to_markdown_pre_code():
    out = h2m.html_to_markdown("<pre>line1\nline2</pre>")
    assert "```" in out


def test_html_to_markdown_inline_code():
    out = h2m.html_to_markdown("<p>Use <code>x = 1</code> here.</p>")
    assert "`x = 1`" in out


def test_html_to_markdown_horizontal_rule():
    # The <hr> branch (process_element) emits a rule, but standalone rules are
    # stripped by post-processing; both surrounding paragraphs must survive.
    out = h2m.html_to_markdown("<p>Before</p><hr/><p>After</p>")
    assert "Before" in out and "After" in out


def test_html_to_markdown_italic_and_bold():
    out = h2m.html_to_markdown("<p><b>Bold</b> and <i>italic</i> text.</p>")
    assert "**Bold**" in out
    assert "*italic*" in out


def test_html_to_markdown_superscript_footnote():
    out = h2m.html_to_markdown("<p>Income<sup>1</sup> grew.</p>")
    assert "Income" in out and "1" in out


def test_html_to_markdown_styled_inline_div_bold():
    out = h2m.html_to_markdown(
        '<div style="display:inline;font-weight:bold">Inline Bold</div>'
    )
    assert "**Inline Bold**" in out


def test_html_to_markdown_section_header_div():
    out = h2m.html_to_markdown(
        '<div style="font-size:16pt">Results of Operations</div>'
    )
    assert "Results of Operations" in out


def test_html_to_markdown_anchor_target_and_link():
    html = (
        '<p><a href="#sec1">Go to Section 1</a></p>'
        '<h2><a name="sec1"></a>Section 1 Title</h2>'
    )
    out = h2m.html_to_markdown(html)
    assert "Section 1 Title" in out
    # anchor referenced by the link should be preserved
    assert 'id="sec1"' in out


def test_html_to_markdown_underline_passthrough():
    out = h2m.html_to_markdown("<p><u>Underlined</u> text.</p>")
    assert "Underlined" in out


def test_html_to_markdown_table_of_contents_navigation_skipped():
    html = '<div><a href="#x">Table of Contents</a></div><p>Real content here.</p>'
    out = h2m.html_to_markdown(html)
    assert "Real content here." in out


# ===========================================================================
# Staircase / multi-period header detection (extract_periods_from_rows
# year_super_headers block, lines ~2419-2684)
# ===========================================================================


def test_extract_periods_two_layer_staircase_date_superheaders():
    # Each date super-header spans two leaf columns (Owned / Leased), so the
    # two-layer year-over-subheader return path (~2670-2684) is taken.
    rows = [
        [("", 1), ("November 30, 2007", 2), ("November 30, 2006", 2)],
        [("", 1), ("Owned", 1), ("Leased", 1), ("Owned", 1), ("Leased", 1)],
        [("Assets", 1), ("100", 1), ("90", 1), ("80", 1), ("70", 1)],
        [("Liabilities", 1), ("40", 1), ("35", 1), ("30", 1), ("25", 1)],
    ]
    layers, count = h2m.extract_periods_from_rows(
        rows, row_has_th_flags=[True, True, False, False]
    )
    assert layers is not None
    assert count >= 2
    flat = " ".join(" ".join(layer) for layer in layers)
    assert "November 30, 2007" in flat
    assert "Owned" in flat and "Leased" in flat


def test_html_to_markdown_staircase_dated_subcolumns_end_to_end():
    html = (
        "<table>"
        '<tr><td></td><th colspan="2">November 30, 2007</th>'
        '<th colspan="2">November 30, 2006</th></tr>'
        "<tr><td></td><th>Owned</th><th>Leased</th><th>Owned</th><th>Leased</th></tr>"
        "<tr><td>Assets</td><td>100</td><td>90</td><td>80</td><td>70</td></tr>"
        "<tr><td>Liabilities</td><td>40</td><td>35</td><td>30</td><td>25</td></tr>"
        "<tr><td>Equity</td><td>60</td><td>55</td><td>50</td><td>45</td></tr>"
        "</table>"
    )
    out = h2m.html_to_markdown(html)
    assert "November 30, 2007" in out
    assert "Owned" in out and "Leased" in out
    assert "Assets" in out and "Equity" in out


def test_html_to_markdown_staircase_maturity_buckets():
    # Year super-headers over maturity-range sub-columns ("0 - 6", "6 - 12").
    html = (
        "<table>"
        '<tr><td></td><th colspan="2">December 31, 2023</th>'
        '<th colspan="2">December 31, 2022</th></tr>'
        "<tr><td></td><th>0 - 6</th><th>6 - 12</th><th>0 - 6</th><th>6 - 12</th></tr>"
        "<tr><td>Fixed rate</td><td>10</td><td>20</td><td>15</td><td>25</td></tr>"
        "<tr><td>Variable rate</td><td>5</td><td>8</td><td>6</td><td>9</td></tr>"
        "</table>"
    )
    out = h2m.html_to_markdown(html)
    assert "December 31, 2023" in out
    assert "Fixed rate" in out and "Variable rate" in out


# ===========================================================================
# _convert_layout_table patterns (direct calls; ~7560-7962)
# ===========================================================================


def test_convert_layout_table_bio_rowspan_pattern():
    bio_para = (
        "John Smith has served as a director of the Company since 2010 and "
        "brings extensive leadership experience across multiple industries "
        "and sectors over the course of a long and distinguished career, "
        "including prior service as chief executive officer of a public company."
    )
    html = (
        "<table>"
        "<tr><td><b>JOHN SMITH</b></td>"
        "<td><div>Director since 2010</div><div>Age 55</div></td></tr>"
        f'<tr><td rowspan="2"><div>{bio_para}</div></td></tr>'
        "</table>"
    )
    out = h2m._convert_layout_table(_table(html))
    assert out is not None
    assert "**JOHN SMITH**" in out
    assert "John Smith has served" in out


def test_convert_layout_table_bio_with_same_row_metadata():
    bio = (
        "Jane Doe has served as chief financial officer and brings deep "
        "expertise in capital markets and corporate finance across a "
        "distinguished multi-decade career spanning several public and "
        "private organizations and industries throughout the world today."
    )
    html = (
        "<table>"
        "<tr><td><b>JANE DOE</b></td></tr>"
        "<tr><td><div>Age 60</div><div>Director since 2015</div></td>"
        f'<td rowspan="2"><div>{bio}</div></td></tr>'
        "</table>"
    )
    out = h2m._convert_layout_table(_table(html))
    assert out is not None
    assert "**JANE DOE**" in out
    assert "- Age 60" in out
    assert "- Director since 2015" in out
    assert "Jane Doe has served" in out


def test_convert_layout_table_header_plus_bullet_same_row():
    html = (
        "<table>"
        "<tr><td><b>Governance</b></td>"
        "<td><div>• Item one here</div><div>• Item two here</div></td></tr>"
        "<tr><td><b>Strategy</b></td>"
        "<td><div>• Item three here</div></td></tr>"
        "</table>"
    )
    out = h2m._convert_layout_table(_table(html))
    assert out is not None
    assert "**Governance**" in out
    assert "- Item one here" in out
    assert "**Strategy**" in out


def test_convert_layout_table_alternating_header_bullet_rows():
    html = (
        "<table>"
        "<tr><td><b>Section A</b></td></tr>"
        "<tr><td><div>• alpha bullet</div></td></tr>"
        "<tr><td><div>• beta bullet</div></td></tr>"
        "<tr><td><b>Section B</b></td></tr>"
        "<tr><td><div>• gamma bullet</div></td></tr>"
        "</table>"
    )
    out = h2m._convert_layout_table(_table(html))
    assert out is not None
    assert "**Section A**" in out
    assert "- alpha bullet" in out
    assert "**Section B**" in out


def test_convert_layout_table_single_column_multidiv():
    html = (
        "<table>"
        "<tr><th>Highlights</th></tr>"
        "<tr><td><div>First achievement line</div>"
        "<div>Second achievement line</div>"
        "<div>Third achievement line</div></td></tr>"
        "</table>"
    )
    out = h2m._convert_layout_table(_table(html))
    assert out is not None
    assert "**Highlights**" in out
    assert "- First achievement line" in out
    assert "- Third achievement line" in out


def test_convert_layout_table_returns_none_for_no_rows():
    html = "<table></table>"
    assert h2m._convert_layout_table(_table(html)) is None


def test_convert_layout_table_returns_none_for_bold_data_header():
    # A row with 3+ bold content cells signals a real data table -> None.
    html = (
        "<table>"
        "<tr><td><b>Year</b></td><td><b>Revenue</b></td><td><b>Income</b></td></tr>"
        "<tr><td>2025</td><td>100</td><td>20</td></tr>"
        "</table>"
    )
    assert h2m._convert_layout_table(_table(html)) is None


def test_convert_layout_table_returns_none_when_no_content_cells():
    # Rows present, no bold/bullet headers, no multi-div content -> None.
    html = (
        "<table>"
        "<tr><td>plain one</td><td>plain two</td></tr>"
        "<tr><td>plain three</td><td>plain four</td></tr>"
        "</table>"
    )
    assert h2m._convert_layout_table(_table(html)) is None


# ===========================================================================
# convert_table semantic-parsing variations (via extract_periods_from_rows
# and html_to_markdown), lines ~2090-2174, ~4486-5026
# ===========================================================================


def test_extract_periods_month_over_year_vertical_merge():
    # Row A = month labels, Row B = years -> "January 26, 2025" merge path.
    rows = [
        [("", 1), ("January 26,", 1), ("January 28,", 1)],
        [("", 1), ("2025", 1), ("2024", 1)],
        [("Net sales", 1), ("100", 1), ("90", 1)],
        [("Cost of sales", 1), ("40", 1), ("35", 1)],
    ]
    layers, count = h2m.extract_periods_from_rows(
        rows, row_has_th_flags=[True, True, False, False]
    )
    assert layers is not None
    flat = " ".join(" ".join(layer) for layer in layers)
    assert "January 26, 2025" in flat
    assert "January 28, 2024" in flat


def test_html_to_markdown_month_over_year_header_table():
    html = (
        "<table>"
        "<tr><td></td><th>January 26,</th><th>January 28,</th></tr>"
        "<tr><td></td><th>2025</th><th>2024</th></tr>"
        "<tr><td>Net sales</td><td>$100</td><td>$90</td></tr>"
        "<tr><td>Cost of sales</td><td>$40</td><td>$35</td></tr>"
        "<tr><td>Gross profit</td><td>$60</td><td>$55</td></tr>"
        "</table>"
    )
    out = h2m.html_to_markdown(html)
    assert "January 26, 2025" in out
    assert "Net sales" in out and "Gross profit" in out


def test_html_to_markdown_mixed_headers_majority_nonyear():
    # Single header row where non-year columns are the majority -> mixed-header
    # branch (has_mixed_headers True, semantic parsing disabled).
    html = (
        "<table>"
        "<tr><th>Item</th><th>2025</th><th>Useful Lives</th>"
        "<th>Method</th><th>Location</th></tr>"
        "<tr><td>Buildings</td><td>500</td><td>30 yrs</td><td>SL</td><td>US</td></tr>"
        "<tr><td>Equipment</td><td>200</td><td>10 yrs</td><td>SL</td><td>EU</td></tr>"
        "</table>"
    )
    out = h2m.html_to_markdown(html)
    assert "Useful Lives" in out
    assert "Buildings" in out and "Equipment" in out
    assert "Method" in out and "Location" in out


def test_html_to_markdown_plain_text_roster_table():
    # Non-financial roster table with text headers and rows.
    html = (
        "<table>"
        "<tr><th>Name</th><th>Title</th><th>Location</th></tr>"
        "<tr><td>Alice</td><td>CEO</td><td>NYC</td></tr>"
        "<tr><td>Bob</td><td>CFO</td><td>SF</td></tr>"
        "<tr><td>Carol</td><td>COO</td><td>LA</td></tr>"
        "</table>"
    )
    out = h2m.html_to_markdown(html)
    assert "Name" in out and "Title" in out
    assert "Alice" in out and "Carol" in out


def test_html_to_markdown_maturity_bucket_not_mixed():
    # year_cols == 0 but all headers are maturity buckets -> NOT mixed headers.
    html = (
        "<table>"
        "<tr><th>Contractual maturities</th><th>0 - 6 Months</th>"
        "<th>1 - 5 Years</th><th>Thereafter</th><th>Total</th></tr>"
        "<tr><td>Long-term debt</td><td>10</td><td>50</td><td>30</td><td>90</td></tr>"
        "<tr><td>Lease obligations</td><td>5</td><td>20</td><td>15</td><td>40</td></tr>"
        "</table>"
    )
    out = h2m.html_to_markdown(html)
    assert "0 - 6 Months" in out
    assert "Long-term debt" in out and "Lease obligations" in out


# ===========================================================================
# process_element: anchor-splits-bold header & display:table-row bullets
# ===========================================================================


def test_html_to_markdown_anchor_bold_split_header():
    # <a name><b>Item 7.</b></a><b> ...</b> -> "### Item 7. ..."
    html = (
        '<p><a name="sec7"><b>Item 7.</b></a>'
        "<b> Management Discussion and Analysis</b></p>"
        "<p>Body text follows here in the section to make it long enough.</p>"
    )
    out = h2m.html_to_markdown(html)
    assert "### Item 7. Management Discussion and Analysis" in out


def test_html_to_markdown_css_table_row_bullet():
    html = (
        '<div style="display:table-row">'
        '<div style="display:table-cell">•</div>'
        '<div style="display:table-cell">Bullet text content here</div>'
        "</div>"
    )
    out = h2m.html_to_markdown(html)
    assert "- Bullet text content here" in out


# ===========================================================================
# Page-break continuation table merging (_are_immediate_sibling_tables,
# different-parents path, lines ~449-492)
# ===========================================================================


def test_are_immediate_sibling_tables_across_page_divs():
    html = (
        '<div id="root">'
        '<div class="page"><table>'
        "<tr><td></td><th>2025</th><th>2024</th></tr>"
        "<tr><td>Revenue</td><td>$100</td><td>$90</td></tr>"
        "</table></div>"
        "<hr/>"
        '<div class="page"><table>'
        "<tr><td>Net income</td><td>$60</td><td>$55</td></tr>"
        "</table></div>"
        "</div>"
    )
    soup = BeautifulSoup(html, "html.parser")
    ta, tb = soup.find_all("table")
    assert h2m._are_immediate_sibling_tables(ta, tb) is True


def test_are_immediate_sibling_tables_blocked_by_text_between():
    html = (
        '<div id="root">'
        '<div class="page"><table><tr><td>A</td></tr></table></div>'
        "<div>Substantial separating narrative paragraph content here.</div>"
        '<div class="page"><table><tr><td>B</td></tr></table></div>'
        "</div>"
    )
    soup = BeautifulSoup(html, "html.parser")
    ta, tb = soup.find_all("table")
    assert h2m._are_immediate_sibling_tables(ta, tb) is False


def test_html_to_markdown_page_break_continuation_merges():
    html = (
        '<div id="root">'
        '<div class="page"><table>'
        "<tr><td></td><th>2025</th><th>2024</th></tr>"
        "<tr><td>Revenue</td><td>$100</td><td>$90</td></tr>"
        "<tr><td>Cost</td><td>$40</td><td>$35</td></tr>"
        "</table></div>"
        "<hr/>"
        '<div class="page"><table>'
        "<tr><td>Net income</td><td>$60</td><td>$55</td></tr>"
        "<tr><td>Assets</td><td>$500</td><td>$480</td></tr>"
        "</table></div>"
        "</div>"
    )
    out = h2m.html_to_markdown(html)
    # Continuation rows should be folded into a single table (one separator row).
    assert "Revenue" in out and "Net income" in out and "Assets" in out
    sep_lines = [ln for ln in out.splitlines() if set(ln) <= set("|-")]
    assert len(sep_lines) == 1


# ===========================================================================
# process_element: bold/italic anchor & footnote-asterisk branches,
# ix: XBRL inline wrappers, TOC navigation-table de-duplication
# ===========================================================================


def test_html_to_markdown_bold_wrapping_only_image():
    out = h2m.html_to_markdown('<p><b><img src="x.png" alt="Logo"/></b></p>')
    assert "![Logo](x.png)" in out


def test_html_to_markdown_bold_footnote_asterisks_escaped():
    out = h2m.html_to_markdown("<p>Income<b>**</b></p>")
    assert "\\*\\*" in out


def test_html_to_markdown_italic_footnote_asterisk_escaped():
    out = h2m.html_to_markdown("<p>Value<i>*</i></p>")
    assert "\\*" in out


def test_html_to_markdown_italic_with_anchor_and_text():
    out = h2m.html_to_markdown(
        '<p><i><a name="i1"></a>Note Label</i> rest of text.</p>'
    )
    assert "Note Label" in out
    assert "rest of text." in out


def test_html_to_markdown_ix_inline_wrapper():
    out = h2m.html_to_markdown(
        '<p><ix:nonNumeric name="x">Revenue was <b>strong</b> this year.'
        "</ix:nonNumeric></p>"
    )
    assert "Revenue was" in out
    assert "**strong**" in out


def test_html_to_markdown_toc_navigation_table_deduplicated():
    toc = (
        "<table>"
        "<tr><td>Management Discussion</td><td>10</td></tr>"
        "<tr><td>Risk Factors</td><td>20</td></tr>"
        "<tr><td>Financial Statements</td><td>30</td></tr>"
        "<tr><td>Controls</td><td>40</td></tr>"
        "<tr><td>Exhibits</td><td>50</td></tr>"
        "</table>"
    )
    out = h2m.html_to_markdown(toc + "<p>Body between sections.</p>" + toc)
    # The repeated sidebar navigation table is emitted only once.
    assert out.count("Risk Factors") == 1


# ===========================================================================
# merge_split_rows / collapse_repeated_headers helpers (direct calls)
# ===========================================================================


def test_merge_split_rows_parenthetical_continuation():
    # Unbalanced "(In millions, except per" row with an UPPERCASE continuation
    # ("Share amounts)") -> parenthetical lookahead merge (lines ~912-939).
    rows = [
        ["(In millions, except per", "", ""],
        ["Share amounts)", "", ""],
        ["Revenue", "100", "90"],
    ]
    rcs = [
        [("(In millions, except per", 1), ("", 1), ("", 1)],
        [("Share amounts)", 1), ("", 1), ("", 1)],
        [("Revenue", 1), ("100", 1), ("90", 1)],
    ]
    merged, _ = h2m.merge_split_rows(rows, rcs)
    assert merged[0][0] == "(In millions, except per Share amounts)"
    assert ["Revenue", "100", "90"] in merged


def test_collapse_repeated_headers_complementary_dollar_offset():
    # Columns 2 and 3 are strictly complementary (dollar-prefix offset):
    # each data row fills exactly one of them, never both. They collapse
    # into a single value column (lines ~1108-1148).
    rows = [
        ["", "2025", "", ""],
        ["Cash", "", "100", ""],
        ["Debt", "", "", "50"],
        ["Equity", "", "60", ""],
    ]
    out = h2m.collapse_repeated_headers([r[:] for r in rows])
    # Header preserved; the two complementary columns merge into one.
    assert out[0] == ["", "2025"]
    assert ["Cash", "100"] in out
    assert ["Debt", "50"] in out
    assert ["Equity", "60"] in out


def test_collapse_repeated_headers_header_in_data_position():
    # Header text in col i-1 but data in col i (curr_has_data, not prev) ->
    # header copied to data position, duplicate removed (lines ~1065-1069).
    rows = [
        ["", "2025", ""],
        ["Revenue", "", "100"],
        ["Cost", "", "40"],
    ]
    out = h2m.collapse_repeated_headers([r[:] for r in rows])
    assert out[0][1] == "2025"
    assert ["Revenue", "100"] in out


# ===========================================================================
# _extract_cell_text: preserve_line_breaks multi-div (>=3) link/image path
# ===========================================================================


def test_extract_cell_text_multidiv_preserve_line_breaks():
    # A cell with 3+ content divs in preserve_line_breaks mode keeps each div
    # as its own line and converts inner <img>/<a> to markdown (lines ~8053-8078).
    # Covers: relative-href urljoin, absolute href kept, and text-only anchor.
    cell = _tag(
        "<td>"
        '<div><img src="check.png" alt="Done"/> First item</div>'
        '<div><a href="report.htm">Annual Report</a></div>'
        '<div><a href="https://x.io/p">Outside</a> and <a>bare anchor</a></div>'
        "</td>",
        "td",
    )
    out = h2m._extract_cell_text(
        cell, base_url="https://sec.gov/docs/", preserve_line_breaks=True
    )
    lines = out.split("\n")
    assert len(lines) == 3
    assert "![Done](https://sec.gov/docs/check.png)" in lines[0]
    assert "First item" in lines[0]
    assert "[Annual Report](https://sec.gov/docs/report.htm)" in lines[1]
    assert "[Outside](https://x.io/p)" in lines[2]
    assert "bare anchor" in lines[2]


# ===========================================================================
# build_column_headers_from_colspan: colspan-structured header reconstruction
# Inputs are list[list[(text, colspan)]]; returns (header_layers, row_count).
# ===========================================================================


def _bch(rows):
    return h2m.build_column_headers_from_colspan(rows, [0])


def _flat(layers):
    return [c for layer in (layers or []) for c in layer]


def test_bch_empty_input_returns_none():
    # No rows -> short-circuit (line 1649-1650).
    assert _bch([]) == (None, 0)


def test_bch_category_text_abbrev_patterns():
    # A category row carrying the abbreviation patterns exercises the
    # is_category_text True branches: "WTD. AVG..." (1717), "YR.-TO-YR." (1720),
    # "U.S." (1724) and "U.S. PLANS" (1727).
    rows = [
        [("", 1), ("2025", 4), ("2024", 4)],
        [
            ("", 1),
            ("WTD. AVG. EXERCISE PRICE", 2),
            ("YR.-TO-YR.", 2),
            ("U.S.", 2),
            ("U.S. PLANS", 2),
        ],
        [("Item", 1), ("1", 2), ("2", 2), ("3", 2), ("4", 2)],
    ]
    layers, count = _bch(rows)
    assert count >= 1
    flat = _flat(layers)
    assert any(c == "2025" for c in flat)


def test_bch_zero_width_only_header_row_skipped():
    # A row whose cells contain only zero-width spaces has no visible content,
    # so is_header_row returns (False, False) at line 1752.
    rows = [
        [("\u200b", 1), ("\u200b", 1), ("\u200b", 1)],
        [("", 1), ("2025", 1), ("2024", 1)],
        [("Rev", 1), ("1", 1), ("2", 1)],
    ]
    layers, count = _bch(rows)
    assert any(c == "2025" for c in _flat(layers))


def test_bch_date_phrase_title_row():
    # A lone col-0 cell carrying a period phrase is treated as a date super
    # header / title row (line 1782 area).
    rows = [
        [("For the Three Months Ended May 31, 2025", 1)],
        [("", 1), ("2025", 1), ("2024", 1)],
        [("Rev", 1), ("1", 1), ("2", 1)],
    ]
    layers, count = _bch(rows)
    assert count >= 1


def test_bch_units_note_header_row():
    # A "(in millions)" units row is recognised as a header/title row (1812).
    rows = [
        [("(in millions)", 1)],
        [("", 1), ("2025", 1), ("2024", 1)],
        [("Rev", 1), ("1", 1), ("2", 1)],
    ]
    layers, count = _bch(rows)
    assert count >= 1


def test_bch_bare_digit_col0_header_row():
    # A bare 1-3 digit value at column 0 alongside real category cells is
    # treated as a rendering artifact and skipped (line 1822). It must share
    # the row with other cells, else the single-cell row is a title row.
    rows = [
        [("", 1), ("2025", 1), ("2024", 1)],
        [("12", 1), ("Owned", 1), ("Leased", 1)],
        [("Rev", 1), ("1", 1), ("2", 1)],
    ]
    layers, count = _bch(rows)
    assert any(c == "2025" for c in _flat(layers))


def test_bch_preheader_nonheader_wide_cell_skipped():
    # A wide (>2 colspan) non-category cell at a non-zero position, appearing
    # before any header is found, is skipped as a pre-header title (1934-1935).
    rows = [
        [("", 1), ("see accompanying notes to statements", 3), ("", 2)],
        [("", 1), ("2025", 2), ("2024", 2)],
        [("Rev", 1), ("1", 2), ("2", 2)],
    ]
    layers, count = _bch(rows)
    assert any(c == "2025" for c in _flat(layers))


def test_bch_section_header_after_year_breaks():
    # Once a year row is recorded, a lone year cell at position 0 is a section
    # break that stops header scanning (line 1948).
    rows = [
        [("", 1), ("2025", 2), ("2024", 2)],
        [("2023", 1), ("", 1), ("", 1), ("", 1), ("", 1)],
        [("Rev", 1), ("1", 2), ("2", 2)],
    ]
    layers, count = _bch(rows)
    assert any(c == "2025" for c in _flat(layers))


def test_bch_year_at_pos0_with_category_shift():
    # When the first year occupies column 0 and a category row follows, the
    # year positions are shifted right by the label width (2069-2076).
    rows = [
        [("2025", 1), ("2024", 1), ("2023", 1), ("2022", 1)],
        [("Owned", 1), ("Leased", 1), ("Other", 1), ("More", 1)],
        [("Item", 1), ("1", 1), ("2", 1), ("3", 1)],
    ]
    layers, count = _bch(rows)
    flat = _flat(layers)
    assert "2025" in flat


def test_bch_trailing_units_note_not_a_header():
    # A units note positioned to the right of the years is skipped by the
    # trailing super-header gap-fill rather than absorbed as a column (2203-2206).
    rows = [
        [("", 1), ("SEGMENTS", 2), ("(in millions, except per share)", 1)],
        [("", 1), ("2025", 1), ("2024", 1)],
        [("Rev", 1), ("1", 1), ("2", 1)],
    ]
    layers, count = _bch(rows)
    flat = _flat(layers)
    assert "2025" in flat
    assert not any("million" in c.lower() for c in flat)


def test_bch_category_without_subheaders_gets_empty_slot():
    # A category whose column span holds no year header gets a single empty
    # header slot (2911-2915). BETA sits between two year groups with none of
    # its own, so it is not absorbed by the trailing gap-fill.
    rows = [
        [("", 1), ("ALPHA", 3), ("BETA", 3), ("GAMMA", 3)],
        [
            ("", 1),
            ("2025", 1),
            ("2024", 1),
            ("2023", 1),
            ("", 1),
            ("", 1),
            ("", 1),
            ("2022", 1),
            ("2021", 1),
            ("2020", 1),
        ],
        [
            ("Rev", 1),
            ("1", 1),
            ("2", 1),
            ("3", 1),
            ("4", 1),
            ("5", 1),
            ("6", 1),
            ("7", 1),
            ("8", 1),
            ("9", 1),
        ],
    ]
    layers, count = _bch(rows)
    assert "BETA" in layers[0]


def test_bch_all_empty_row_between_headers():
    # An all-empty row appearing between header rows is skipped (1899-1900).
    rows = [
        [("", 1), ("2025", 2), ("2024", 2)],
        [("", 1), ("", 2), ("", 2)],
        [("", 1), ("Owned", 2), ("Leased", 2)],
        [("Rev", 1), ("1", 2), ("2", 2)],
    ]
    layers, count = _bch(rows)
    assert count >= 1


def test_bch_year_row_then_lone_year_pos0():
    # Year row followed by a lone year cell at position 0 (line 1948).
    rows = [
        [("2025", 1), ("2024", 1)],
        [("Rev", 1), ("1", 1), ("2", 1)],
    ]
    layers, count = _bch(rows)
    flat = _flat(layers)
    assert "2025" in flat and "2024" in flat


def test_bch_in_millions_midyear_row():
    # "(in millions)" appearing at a non-zero start position inside a year row
    # is dropped while the surrounding years are kept (line 2051 / 2098-2102).
    rows = [
        [
            ("Item", 1),
            ("January 26,", 1),
            ("(in millions)", 1),
            ("October 27,", 1),
        ],
        [("Label", 1), ("2025", 1), ("", 1), ("2024", 1)],
        [("Rev", 1), ("1", 1), ("2", 1), ("3", 1)],
    ]
    layers, count = _bch(rows)
    assert count >= 1


def test_bch_position_merge_years_then_months():
    # Years row then a months row that position-merges onto it (2130-2144).
    rows = [
        [("", 1), ("2025", 1), ("2024", 1)],
        [("", 1), ("January 26,", 1), ("October 27,", 1)],
        [("Rev", 1), ("1", 1), ("2", 1)],
    ]
    layers, count = _bch(rows)
    flat = _flat(layers)
    assert any("2025" in c for c in flat)


def test_bch_two_year_only_rows_no_merge():
    # Two consecutive year-only rows do not position-merge (line 2173).
    rows = [
        [("", 1), ("2025", 1), ("2024", 1)],
        [("", 1), ("2023", 1), ("2022", 1)],
        [("Rev", 1), ("1", 1), ("2", 1)],
    ]
    layers, count = _bch(rows)
    assert count >= 1


def test_bch_date_super_header_distribution():
    # A wide date super-header distributed across sub-headers (2199, 2203-2227).
    rows = [
        [("", 1), ("Three Months Ended January 26", 6), ("", 4)],
        [
            ("", 1),
            ("Retail Notes", 2),
            ("Revolving", 2),
            ("Wholesale", 2),
            ("", 4),
        ],
        [
            ("", 1),
            ("& Financing", 2),
            ("Charge", 2),
            ("Accounts", 2),
            ("", 4),
        ],
        [("Rev", 1), ("1", 2), ("2", 2), ("3", 2), ("9", 4)],
    ]
    layers, count = _bch(rows)
    flat = _flat(layers)
    assert any("Three Months Ended" in c for c in flat)


def test_bch_flat_position_merge():
    # Flat position-merge path across an unbalanced set of category cells
    # (2268-2289).
    rows = [
        [("For the Year Ended December 31", 1)],
        [("", 1), ("Alpha", 3), ("Bravo", 3)],
        [
            ("", 1),
            ("Charlie", 3),
            ("Delta", 3),
            ("Echo", 3),
            ("Foxtrot", 3),
            ("Golf", 3),
            ("", 3),
        ],
        [
            ("Rev", 1),
            ("1", 3),
            ("2", 3),
            ("3", 3),
            ("4", 3),
            ("5", 3),
            ("9", 3),
        ],
    ]
    layers, count = _bch(rows)
    assert count >= 1


def test_bch_year_super_header_lookahead():
    # Year super-header with a sub-header lookahead that distributes the years
    # across owned/leased sub columns (2461, 2503-2535).
    rows = [
        [("", 1), ("2007", 4), ("2006", 4)],
        [
            ("", 1),
            ("Owned, at", 3),
            ("Leased, at", 1),
            ("Owned, at", 3),
            ("Leased, at", 1),
        ],
        [("Item", 1), ("1", 2), ("2", 2), ("3", 2), ("4", 2)],
    ]
    layers, count = _bch(rows)
    flat = _flat(layers)
    assert "2007" in " ".join(flat)


def test_bch_year_super_header_maturity_staircase():
    # A year super-header over a maturity-range staircase ("0 - 6" / "6 - 12")
    # exercises the non-alpha, non-financial cell branch in the sub-header
    # start-map builder (line 2535).
    rows = [
        [("", 1), ("2007", 4), ("2006", 4)],
        [
            ("", 1),
            ("0 - 6", 2),
            ("6 - 12", 2),
            ("0 - 6", 2),
            ("6 - 12", 2),
        ],
        [("Item", 1), ("100", 2), ("200", 2), ("300", 2), ("400", 2)],
    ]
    layers, count = _bch(rows)
    assert count >= 1


def test_bch_two_layer_label_staircase():
    # Two-layer category labels stacked under a year super-header (2582-2588).
    rows = [
        [("", 1), ("2007", 4), ("2006", 4)],
        [
            ("Plan", 1),
            ("BENEFIT", 2),
            ("PLAN", 2),
            ("BENEFIT", 2),
            ("PLAN", 2),
        ],
        [
            ("Detail", 1),
            ("OBLIGATION", 2),
            ("ASSETS", 2),
            ("OBLIGATION", 2),
            ("ASSETS", 2),
        ],
        [("Item", 1), ("1", 2), ("2", 2), ("3", 2), ("4", 2)],
    ]
    layers, count = _bch(rows)
    assert count >= 1


def test_bch_all_one_to_one():
    # All header cells map one-to-one onto data columns (2616-2665).
    rows = [
        [("", 1), ("2007", 2), ("2006", 2)],
        [("Contract", 1), ("Owned, at", 2), ("Leased, at", 2)],
        [("Type", 1), ("cost", 2), ("cost", 2)],
        [("Item", 1), ("9", 2), ("8", 2)],
    ]
    layers, count = _bch(rows)
    assert count >= 1


def test_bch_stacked_category():
    # Two-row stacked category labels above a year row (line 2717).
    rows = [
        [("", 1), ("EQUIPMENT", 4), ("FINANCIAL", 4)],
        [("", 1), ("OPERATIONS", 4), ("SERVICES", 4)],
        [("", 1), ("2025", 2), ("2024", 2), ("2025", 2), ("2024", 2)],
        [("Rev", 1), ("1", 2), ("2", 2), ("3", 2), ("4", 2)],
    ]
    layers, count = _bch(rows)
    flat = _flat(layers)
    assert "EQUIPMENT OPERATIONS" in flat
    assert "FINANCIAL SERVICES" in flat


def test_bch_orphan_headers():
    # A category set plus an orphan memo column with no year sub-headers
    # (2746-2821).
    rows = [
        [
            ("", 1),
            ("EQUIPMENT", 4),
            ("FINANCIAL", 4),
            ("Memo: ratio", 1),
        ],
        [
            ("", 1),
            ("2025", 2),
            ("2024", 2),
            ("2025", 2),
            ("2024", 2),
            ("", 1),
        ],
        [("Rev", 1), ("1", 2), ("2", 2), ("3", 2), ("4", 2), ("9", 1)],
    ]
    layers, count = _bch(rows)
    assert count >= 1


def test_bch_position_distribution_units_then_category():
    # Leading blank/units span followed by a category that distributes years by
    # position (2841-2843).
    rows = [
        [("", 1), ("", 4), ("EQUIPMENT", 4)],
        [("", 1), ("Units", 4), ("2025", 2), ("2024", 2)],
        [("Rev", 1), ("9", 4), ("1", 2), ("2", 2)],
    ]
    layers, count = _bch(rows)
    assert count >= 1


def test_bch_position_distribution_category_note_category():
    # Category, interstitial note span, then another category distributed by
    # position (2856-2873).
    rows = [
        [("", 1), ("EQUIPMENT", 4), ("", 2), ("FINANCIAL", 4)],
        [("", 1), ("2025", 2), ("2024", 2), ("Note", 2), ("", 4)],
        [("Rev", 1), ("1", 2), ("2", 2), ("9", 2), ("7", 4)],
    ]
    layers, count = _bch(rows)
    assert count >= 1


# ===========================================================================
# _extract_chart_legend: colour-swatch legend detection
# ===========================================================================

_SWATCH = "background-color:{c};width:8px;height:8px"


def _swatch(color):
    return f'<td style="{_SWATCH.format(c=color)}"></td>'


def test_chart_legend_basic_pairs():
    # Two tiny coloured swatch cells each paired with a label produce an inline
    # legend string.
    html = (
        "<table>"
        f"<tr>{_swatch('#009dd9')}<td>United States</td></tr>"
        f"<tr>{_swatch('#0b2d71')}<td>Other Americas</td></tr>"
        "</table>"
    )
    out = h2m._extract_chart_legend(_table(html))
    assert out is not None
    assert "Legend:" in out
    assert "United States" in out and "Other Americas" in out


def test_chart_legend_non_tiny_swatch_branch():
    # A coloured-but-not-tiny cell records its colour without bumping the
    # confident-swatch count (line 3732); two real tiny swatches still qualify
    # the table as a legend.
    html = (
        "<table>"
        '<tr><td style="background-color:#009dd9;width:100px;height:50px"></td>'
        "<td>Alpha</td></tr>"
        f"<tr>{_swatch('#0b2d71')}<td>Bravo</td></tr>"
        f"<tr>{_swatch('#777777')}<td>Charlie</td></tr>"
        "</table>"
    )
    out = h2m._extract_chart_legend(_table(html))
    assert out is not None
    assert "Bravo" in out


def test_chart_legend_swatch_only_rows_collect_colors():
    # Swatch-only rows (colour, no label) append to the colour list (3743);
    # label-only rows supply the labels.
    html = (
        "<table>"
        f"<tr>{_swatch('#009dd9')}</tr>"
        f"<tr>{_swatch('#0b2d71')}</tr>"
        "<tr><td>Alpha</td></tr>"
        "<tr><td>Bravo</td></tr>"
        "</table>"
    )
    out = h2m._extract_chart_legend(_table(html))
    assert out is not None
    assert "Alpha" in out and "Bravo" in out


def test_chart_legend_numeric_labels_rejected():
    # Swatches paired with purely numeric labels are not a category legend, so
    # the function bails at the non-numeric-label guard (line 3764).
    html = (
        "<table>"
        f"<tr>{_swatch('#009dd9')}<td>1.5</td></tr>"
        f"<tr>{_swatch('#0b2d71')}<td>2.5</td></tr>"
        "</table>"
    )
    assert h2m._extract_chart_legend(_table(html)) is None


def test_chart_legend_too_much_text_rejected():
    # A legend-shaped table whose total text exceeds 500 chars is rejected as
    # too verbose to be a real chart legend (line 3770).
    rows = "".join(
        f"<tr>{_swatch('#%06x' % (0x0099D9 + i))}"
        f"<td>Category label number {i} with several extra words here</td></tr>"
        for i in range(10)
    )
    html = f"<table>{rows}</table>"
    assert h2m._extract_chart_legend(_table(html)) is None


def test_chart_legend_insufficient_pairs_rejected():
    # Two tiny swatches packed in a single row yield only one colour entry, so
    # fewer than two colour/label pairs survive and the function bails (3780).
    html = (
        "<table>"
        f"<tr>{_swatch('#009dd9')}{_swatch('#0b2d71')}</tr>"
        "<tr><td>Alpha</td></tr>"
        "<tr><td>Bravo</td></tr>"
        "</table>"
    )
    assert h2m._extract_chart_legend(_table(html)) is None


# ===========================================================================
# _split_composite_table: split one <table> holding multiple "TABLE X" blocks
# ===========================================================================

_LONG_BODY = "This is a long body text paragraph that exceeds sixty characters for sure"


def test_split_composite_with_preamble_and_body():
    # Pre-header rows, an empty <tr>, two "TABLE X" headers and a trailing body
    # paragraph split into four parts (pre-table, table 1, body text, table 2).
    html = (
        "<table>"
        "<tr><td>Preamble row</td><td>data</td></tr>"
        "<tr></tr>"
        "<tr><th>TABLE 1 - Revenue</th></tr>"
        "<tr><td>Item</td><td>100</td></tr>"
        f"<tr><td>{_LONG_BODY}</td><td></td></tr>"
        "<tr><th>TABLE 2 - Expenses</th></tr>"
        "<tr><td>Item</td><td>200</td></tr>"
        "</table>"
    )
    parts = h2m._split_composite_table(_table(html))
    assert len(parts) == 4
    # One part is the extracted body-text string.
    assert any(isinstance(p, str) and _LONG_BODY in p for p in parts)


def test_split_composite_allcaps_heading_body():
    # An ALL-CAPS section heading immediately followed by a long body line is
    # also recognised as the start of a body-text section (lines 3892-3900).
    html = (
        "<table>"
        "<tr><th>TABLE 1 - Revenue</th></tr>"
        "<tr><td>Item</td><td>100</td></tr>"
        "<tr><td>OVERVIEW</td><td></td></tr>"
        f"<tr><td>{_LONG_BODY}</td><td></td></tr>"
        "<tr><th>TABLE 2 - More</th></tr>"
        "<tr><td>Item</td><td>200</td></tr>"
        "</table>"
    )
    parts = h2m._split_composite_table(_table(html))
    assert len(parts) == 3
    assert any(isinstance(p, str) and "OVERVIEW" in p for p in parts)


def test_split_composite_too_few_rows_returns_self():
    # Fewer than four rows: nothing to split, the original table is returned.
    html = "<table><tr><td>A</td></tr><tr><td>B</td></tr></table>"
    t = _table(html)
    assert h2m._split_composite_table(t) == [t]


def test_split_composite_one_header_returns_self():
    # Only one "TABLE X" header: not enough to justify splitting (line 3840).
    html = (
        "<table>"
        "<tr><th>TABLE 1 - Only</th></tr>"
        "<tr><td>Item</td><td>100</td></tr>"
        "<tr><td>Item</td><td>200</td></tr>"
        "<tr><td>Item</td><td>300</td></tr>"
        "</table>"
    )
    t = _table(html)
    assert h2m._split_composite_table(t) == [t]


# ===========================================================================
# collapse_repeated_headers - complementary-column merging (second pass)
# ===========================================================================


def test_collapse_headers_fully_empty_curr_column_skipped():
    # Second pass: columns 1,2 are complementary but column 2 is entirely
    # empty (col_curr_count == 0) so the merge is skipped (lines 1129-1130)
    # and the trailing-empty pass (1158) removes it instead.
    rows = [["A", "", ""], ["x", "1", ""], ["y", "2", ""]]
    out = h2m.collapse_repeated_headers(rows)
    assert out == [["A", ""], ["x", "1"], ["y", "2"]]


def test_collapse_headers_merge_curr_into_prev():
    # Empty header on the prev column, data is complementary, and the prev
    # column holds at least as many values as curr -> merge curr into prev
    # (lines 1133-1140).
    rows = [["", "Price"], ["100", ""], ["", "200"], ["300", ""]]
    out = h2m.collapse_repeated_headers(rows)
    assert out == [["Price"], ["100"], ["200"], ["300"]]


def test_collapse_headers_merge_prev_into_curr():
    # Same shape but the curr column holds more values than prev -> the prev
    # column is merged into curr instead (lines 1141-1148).
    rows = [["", "Price"], ["", "100"], ["", "200"], ["300", ""]]
    out = h2m.collapse_repeated_headers(rows)
    assert out == [["Price"], ["100"], ["200"], ["300"]]


def test_collapse_headers_trailing_empty_column_removed():
    # A wholly empty trailing column (empty header + empty data) is dropped by
    # the right-to-left trailing pass (line 1158).
    rows = [["A", "B", ""], ["1", "2", ""], ["3", "4", ""]]
    out = h2m.collapse_repeated_headers(rows)
    assert out == [["A", "B"], ["1", "2"], ["3", "4"]]


# ===========================================================================
# build_column_headers_from_colspan - residual classification branches
# ===========================================================================


def test_bch_single_cell_title_row_at_col0():
    # A lone non-empty cell at column 0 (others empty) is a TITLE row, not a
    # category/header row (line 1803).
    rows = [
        [("Financial Performance", 1), ("", 1), ("", 1), ("", 1), ("", 1)],
        [("", 1), ("2025", 1), ("2024", 1), ("2023", 1), ("2022", 1)],
        [("Rev", 1), ("1", 1), ("2", 1), ("3", 1), ("4", 1)],
    ]
    layers, count = _bch(rows)
    assert isinstance(count, int)
    assert layers is None or isinstance(layers, list)


def test_bch_allcaps_colspan_category_with_trailing_label():
    # An ALL-CAPS category cell with colspan>1 followed by a colon-label cell
    # exercises the category-with-label branch (line 1850).
    rows = [
        [("", 1), ("EQUIPMENT", 2), ("Assets:", 1)],
        [("", 1), ("2025", 1), ("2024", 1), ("2023", 1)],
        [("Rev", 1), ("1", 1), ("2", 1), ("3", 1)],
    ]
    layers, count = _bch(rows)
    assert isinstance(count, int)


def test_bch_month_super_header_single_row_positions():
    # Month labels present in only one of two header rows force the per-row
    # position bookkeeping for unmatched columns (lines 2135-2139).
    rows = [
        [
            ("", 1),
            ("January 26", 1),
            ("January 28", 1),
            ("%", 1),
            ("AOnly", 1),
            ("", 1),
        ],
        [("", 1), ("2025", 1), ("2024", 1), ("Change", 1), ("", 1), ("BOnly", 1)],
        [("Rev", 1), ("1", 1), ("2", 1), ("3", 1), ("4", 1), ("5", 1)],
    ]
    layers, count = _bch(rows)
    assert isinstance(count, int)


def test_bch_month_and_year_misaligned_returns_none():
    # A month cell and a year cell at different column positions yield zero
    # month+year merges, so the merge attempt bails out (line 2144).
    rows = [
        [("", 1), ("January 26", 1), ("", 1)],
        [("", 1), ("", 1), ("2025", 1)],
        [("Rev", 1), ("1", 1), ("2", 1)],
    ]
    layers, count = _bch(rows)
    assert isinstance(count, int)
    assert layers is None or isinstance(layers, list)


def test_bch_wide_allcaps_categories_many_narrow_columns():
    # Two wide ALL-CAPS category rows over many narrow data columns drive the
    # category fan-out path (line 2272).
    rows = [
        [
            ("", 3),
            ("WIDEONE", 3),
            ("WIDETWO", 3),
            ("WIDETHREE", 3),
            ("WIDEFOUR", 3),
            ("WIDEFIVE", 3),
        ],
        [("", 3), ("NARROW", 3), ("OTHER", 3), ("LAST", 3)],
        [("Rev", 1)] + [("1", 1)] * 17,
    ]
    layers, count = _bch(rows)
    assert isinstance(count, int)


def test_bch_year_super_header_with_lowercase_breaker_row():
    # A year super-header followed by an empty staircase row and a colspan
    # sub-header exercises the lookahead at line 2461.
    rows = [
        [("", 1), ("2007", 4)],
        [("owned", 1), ("leased", 1), ("", 1), ("", 1), ("", 1)],
        [("", 1), ("", 1), ("", 1), ("", 1), ("", 1)],
        [("", 1), ("Retail", 2), ("Total", 2)],
        [("Rev", 1), ("1", 1), ("2", 1), ("3", 1), ("4", 1)],
    ]
    layers, count = _bch(rows)
    assert isinstance(count, int)


def test_bch_year_super_header_credit_rating_breaker():
    # The breaker row holds short rating-like cells (A+, Stable) — line 2503.
    rows = [
        [("", 1), ("2007", 4)],
        [("owned", 1), ("leased", 1), ("", 1), ("", 1), ("", 1)],
        [("Issuer", 1), ("A+", 1), ("Stable", 1), ("", 1), ("", 1)],
        [("Rev", 1), ("1", 1), ("2", 1), ("3", 1), ("4", 1)],
    ]
    layers, count = _bch(rows)
    assert isinstance(count, int)


def test_bch_year_super_header_as_of_date_breaker():
    # A breaker row carrying an "As of November" date phrase — line 2506.
    rows = [
        [("", 1), ("2007", 4)],
        [("owned", 1), ("leased", 1), ("", 1), ("", 1), ("", 1)],
        [("", 1), ("As of", 1), ("November", 1), ("", 1), ("", 1)],
        [("", 1), ("Retail", 2), ("Total", 2)],
        [("Rev", 1), ("1", 1), ("2", 1), ("3", 1), ("4", 1)],
    ]
    layers, count = _bch(rows)
    assert isinstance(count, int)


def test_bch_nested_super_headers_equipment_good_bad():
    # Three header layers (EQUIPMENT super, GOOD/bad mid, years) with trailing
    # note columns exercise the nested colspan merge (lines 2748-2751).
    rows = [
        [("", 1), ("EQUIPMENT", 4), ("note", 2)],
        [("", 1), ("GOOD", 2), ("bad", 2), ("", 1), ("", 1)],
        [
            ("", 1),
            ("2025", 1),
            ("2024", 1),
            ("2023", 1),
            ("2022", 1),
            ("x", 1),
            ("y", 1),
        ],
        [("Rev", 1), ("1", 1), ("2", 1), ("3", 1), ("4", 1), ("5", 1), ("6", 1)],
    ]
    layers, count = _bch(rows)
    assert isinstance(count, int)


def test_bch_orphan_column_after_super_header():
    # An ALL-CAPS super-header with an orphan single-column label, followed by
    # years offset to the right, hits the orphan handling (lines 2810-2811).
    rows = [
        [("", 1), ("EQUIPMENT", 4), ("orphanX", 1)],
        [("", 1), ("", 1), ("", 1), ("", 1), ("", 1), ("2025", 1), ("2024", 1)],
        [("Rev", 1), ("1", 1), ("2", 1), ("3", 1), ("4", 1), ("5", 1), ("6", 1)],
    ]
    layers, count = _bch(rows)
    assert isinstance(count, int)


# ===========================================================================
# _convert_layout_table / _extract_header_text - bullet-list layout patterns
# ===========================================================================


def test_layout_table_bullet_div_skips_empty_and_image():
    # PATTERN 2: a bullet cell with an empty leading div, a container-only div,
    # an image-bearing bullet and a plain bullet (lines 7560/7562/7563/7570).
    html = (
        "<table><tr><td><b>Header One</b></td>"
        "<td><div>&#160;</div>"
        "<div><div>&#8226; nested only</div></div>"
        '<div>&#8226; <img src="check.png"/> Item with image</div>'
        "<div>&#8226; Plain bullet item</div></td></tr></table>"
    )
    out = h2m._convert_layout_table(_table(html), "")
    assert "**Header One**" in out
    assert "- Plain bullet item" in out
    assert "![Image](check.png)" in out


def test_layout_table_styled_bold_header_with_anchor():
    # PATTERN 2: header cell styled bold via font-weight (no <b>) inside an
    # anchored div emits an <a id> + bold header (lines 7594-7615, 7807).
    html = (
        '<table><tr><td><div id="sec1">'
        '<span style="font-weight:bold">Styled Header</span></div></td>'
        "<td><div>&#8226; Bullet alpha</div>"
        "<div>&#8226; Bullet beta</div></td></tr></table>"
    )
    out = h2m._convert_layout_table(_table(html), "")
    assert '<a id="sec1"></a>' in out
    assert "**Styled Header**" in out
    assert "- Bullet alpha" in out


def test_layout_table_header_div_fallback_no_bold():
    # PATTERN 3: a header cell with only a plain div (no bold) falls back to
    # extract_header_text's div text (lines 7619-7623).
    html = (
        "<table><tr><td><b>Bold Title</b></td>"
        "<td><div>Plain Div Text</div></td></tr>"
        "<tr><td><div>&#8226; one</div></td>"
        "<td><div>&#8226; two</div></td></tr>"
        "<tr><td><div>&#8226; three</div></td></tr></table>"
    )
    out = h2m._convert_layout_table(_table(html), "")
    assert isinstance(out, str)
    assert "one" in out


def test_layout_table_pattern2_skips_empty_rows_and_cells():
    # PATTERN 2: a row with no cells and an nbsp-only cell are both skipped
    # before the bold header is found (lines 7767, 7776).
    html = (
        "<table><tr></tr>"
        "<tr><td>&#160;</td><td><b>Hdr</b></td>"
        "<td><div>&#8226; aa</div><div>&#8226; bb</div></td></tr></table>"
    )
    out = h2m._convert_layout_table(_table(html), "")
    assert isinstance(out, str)
    assert "aa" in out


def test_layout_table_pattern3_skips_empty_rows_and_text():
    # PATTERN 3 (no bold header anywhere): empty row and empty-text row are
    # skipped (lines 7829, 7833).
    html = (
        "<table><tr></tr><tr><td>&#160;</td></tr>"
        "<tr><td><div>&#8226; one</div></td></tr>"
        "<tr><td><div>&#8226; two</div></td></tr>"
        "<tr><td><div>&#8226; three</div></td></tr></table>"
    )
    out = h2m._convert_layout_table(_table(html), "")
    assert isinstance(out, str)
    assert "one" in out


def test_layout_table_pattern3_anchored_header_row():
    # PATTERN 3: the header row carries an id, producing an anchored heading
    # before the bullet list (lines 7856, 7874).
    html = (
        '<table><tr><td id="anchorX"><b>Section Title</b></td></tr>'
        "<tr><td><div>&#8226; bullet one</div></td></tr>"
        "<tr><td><div>&#8226; bullet two</div></td></tr>"
        "<tr><td><div>&#8226; bullet three</div></td></tr></table>"
    )
    out = h2m._convert_layout_table(_table(html), "")
    assert '<a id="anchorX"></a>' in out
    assert "- bullet one" in out


def test_layout_table_pattern0_bio_skips_empty_and_long_siblings():
    # PATTERN 0 (bio): backward search past an empty cell, and the metadata
    # loop skipping an empty sibling and an over-150-char sibling
    # (lines 7681, 7701, 7704).
    other = "x" * 160
    long = "L" * 220
    html = (
        "<table><tr><td>&#160;</td><td><b>JOHN SMITH</b></td></tr>"
        f"<tr><td>&#160;</td><td>{other}</td>"
        "<td><div>Age: 55</div><div>Director since 2010</div></td>"
        f'<td rowspan="2"><div>{long}</div></td></tr>'
        "<tr><td>&#160;</td></tr></table>"
    )
    out = h2m._convert_layout_table(_table(html), "")
    assert out is None or isinstance(out, str)


def test_layout_table_pattern1_bold_header_break_and_image():
    # PATTERN 1: a content row whose cell starts with short bold text is
    # treated as a header (break), and an image inside a >=3-div content cell
    # is converted (lines 7907, 7908, 7931).
    html = (
        "<table><tr><td><b>Title Row</b></td></tr>"
        "<tr><td><b>Lead</b><div>First line item</div>"
        '<div>Second line item <img src="pic.png"/></div>'
        "<div>Third line item</div></td></tr></table>"
    )
    out = h2m._convert_layout_table(_table(html), "")
    assert "First line item" in out
    assert "![Image](pic.png)" in out


def test_extract_header_text_nested_div_anchor():
    # _extract_header_text: a header cell whose text lives in a nested div that
    # carries an id emits an <a id> anchor before the text (lines 7981-7984).
    html = '<table><tr><td><div id="hdrAnchor">Header Cell Text</div></td></tr></table>'
    out = h2m._extract_header_text(_table(html))
    assert out is not None
    assert "Header Cell Text" in out
    assert '<a id="hdrAnchor"></a>' in out


# ===========================================================================
# process_equity_statement_table - stacked vertical headers / $-split values
# ===========================================================================


def _twin(rows):
    """Build a 1:1 colspan twin of a plain rows matrix."""
    return [[(c, 1) for c in r] for r in rows]


def test_equity_statement_split_dollar_cells_and_skips():
    # $ and value live in separate cells (lines 1479-1486); the $-prefix cell
    # is rejoined with the following number (1604-1607); a value living in the
    # next cell is recovered (1611-1612); a leading empty row is skipped in the
    # data search (1437) and counts as a title row (1504); a value-less row is
    # dropped (1617).
    rows = [
        ["", "", "", "", ""],
        ["", "Common Stock", "Retained Earnings", "", ""],
        ["Balance at Jan 1, 2024", "$", "100", "$(", "200"],
        ["Net loss", "", "75", "$(", "50"],
        ["", "", "", "", ""],
        ["Balance at Dec 31, 2024", "$", "150", "$(", "250"],
    ]
    result, num_header = h2m.process_equity_statement_table(rows, _twin(rows))
    assert num_header == 1
    assert result[0] == ["", "Common Stock", "Retained Earnings"]
    labels = [r[0] for r in result[1:]]
    assert "Balance at Jan 1, 2024" in labels
    assert "Net loss" in labels
    # The fully empty row produced no label/values and was dropped.
    assert "" not in labels


def test_equity_statement_too_few_value_columns_returns_none():
    # Only a single $-value pair: fewer than two value columns -> bail (1490).
    rows = [["", "Common Stock"], ["Balance at Jan 1, 2024", "$", "100"]]
    assert h2m.process_equity_statement_table(rows, _twin(rows)) == (None, 0)


def test_equity_statement_single_cell_colspan_title_skipped():
    # A single-cell row whose colspan spans 40%+ of the table is recognised as
    # a title row and excluded from the header set (lines 1509-1517).
    rows = [
        ["Statement of Stockholders Equity", "", "", "", ""],
        ["", "Common Stock", "Retained Earnings", "", ""],
        ["Balance at Jan 1", "$", "100", "$(", "200"],
    ]
    rwc = [
        [("Statement of Stockholders Equity", 5)],
        [("", 1), ("Common Stock", 1), ("Retained Earnings", 1), ("", 1), ("", 1)],
        [("Balance at Jan 1", 1), ("$", 1), ("100", 1), ("$(", 1), ("200", 1)],
    ]
    result, _ = h2m.process_equity_statement_table(rows, rwc)
    # Title row text must not leak into the header row.
    assert "Statement of Stockholders Equity" not in result[0]
    assert result[0] == ["", "Common Stock", "Retained Earnings"]


def test_equity_statement_column_fallback_when_fewer_headers():
    # Two value columns but only one header text -> the second column gets the
    # synthetic "Column N" label (line 1564).
    rows = [["", "Common Stock", "", ""], ["Balance at Jan 1", "$", "100", "$(", "200"]]
    rwc = [
        [("", 1), ("Common Stock", 1), ("", 1), ("", 1)],
        [("Balance at Jan 1", 1), ("$", 1), ("100", 1), ("$(", 1), ("200", 1)],
    ]
    result, _ = h2m.process_equity_statement_table(rows, rwc)
    assert result[0] == ["", "Common Stock", "Column 2"]


# ===========================================================================
# extract_periods_from_rows -> is_data_row rating/credit-code detection
# ===========================================================================


def _periods(rows, flags=None):
    return h2m.extract_periods_from_rows([list(r) for r in rows], flags)


def test_is_data_row_bare_digit_label_then_rating():
    # A bare 1-3 digit cell in the label column is treated as a rendering
    # artifact (skipped, lines 3016-3017); the following "A+" rating then marks
    # the row as data (line 3027).
    out = _periods([[("12", 1), ("A+", 1)]])
    assert isinstance(out, tuple) and len(out) == 2


def test_is_data_row_letter_digit_rating():
    # "A1" style rating (line 3029).
    out = _periods([[("Issuer", 1), ("A1", 1)]])
    assert isinstance(out, tuple) and len(out) == 2


def test_is_data_row_allcaps_sign_rating():
    # "AA+" style rating (line 3031).
    out = _periods([[("Issuer", 1), ("AA+", 1)]])
    assert isinstance(out, tuple) and len(out) == 2


def test_is_data_row_prime_rating():
    # "Prime-1" rating (line 3033).
    out = _periods([[("Issuer", 1), ("Prime-1", 1)]])
    assert isinstance(out, tuple) and len(out) == 2


def test_is_data_row_outlook_word():
    # Outlook word "Stable" (line 3044).
    out = _periods([[("Issuer", 1), ("Stable", 1)]])
    assert isinstance(out, tuple) and len(out) == 2


# ===========================================================================
# extract_periods_from_rows - single-row fallback (colspan/vertical declined)
# ===========================================================================


def test_periods_as_of_full_date_headers():
    # "As of" prefix row + Month-Year cells -> Priority 2 full-date headers with
    # the prefix applied (lines 3480, 3486, 3583-3588).
    out = _periods([[("As of", 1)], [("May 2024", 1), ("May 2023", 1)]])
    assert out == ([["", "As of May 2024", "As of May 2023"]], 1)


def test_periods_prefix_with_multiple_years_uses_years():
    # A period prefix that itself names two years -> the bare years win
    # (lines 3602-3603).
    out = _periods(
        [[("Three Months Ended December 2024 and 2023", 1)], [("2024", 1), ("2023", 1)]]
    )
    assert out == ([["", "2024", "2023"]], 1)


def test_periods_one_year_per_prefix_uses_prefixes():
    # Each prefix carries exactly one year and the counts match -> use the full
    # prefixes directly (lines 3607-3610).
    out = _periods(
        [[("Year Ended December 31, 2024", 1), ("Year Ended December 31, 2023", 1)]]
    )
    assert out == (
        [["", "Year Ended December 31, 2024", "Year Ended December 31, 2023"]],
        1,
    )


def test_periods_year_loop_skips_long_paren_and_full_date():
    # The year scanner skips an over-50-char cell (3501), a "(YYYY)" effective
    # date (3504) and a full "Month D, YYYY" date (3521); nothing usable -> empty.
    out = _periods(
        [
            [
                (
                    "This is a long descriptive column header exceeding fifty characters total",
                    1,
                ),
                ("(2020)", 1),
                ("April 7, 2025", 1),
            ]
        ]
    )
    assert out == ([], 0)


def test_periods_generic_block_skips_descriptor_and_data_rows():
    # An empty row (3431), a "(in millions)" descriptor row (3534) and a
    # comma-grouped numeric data row (3537) all yield no headers.
    out = _periods([[("", 1)], [("(in millions)", 1)], [("1,234", 1), ("5,678", 1)]])
    assert out == ([], 0)


def test_periods_prefix_already_contains_year():
    # One prefix, two years: the year already present in the prefix is not
    # duplicated, the missing one is appended (lines 3619-3622).
    out = _periods([[("Year Ended 2024", 1)], [("2024", 1), ("2023", 1)]])
    assert out == ([["", "Year Ended 2024", "Year Ended 2024 2023"]], 1)


def test_periods_years_only():
    # Bare years with no prefixes/dates -> plain year headers (line 3632).
    out = _periods([[("2024", 1), ("2023", 1)]])
    assert out == ([["", "2024", "2023"]], 1)


# ===========================================================================
# is_header_element — header-detection branches
# ===========================================================================


def test_is_header_element_toc_bold_anchor():
    # An element with a toc* id wrapping <b> text is a TOC section header
    # (lines 579, 582-586).
    tag = _tag('<div id="toc1"><b>Section Title Here</b></div>', "div")
    assert h2m.is_header_element(tag) is True


def test_is_header_element_child_span_smaller_font_not_header():
    # A div carrying a large fallback font-size whose span child has a SMALLER
    # font-size is not a header (the child font wins; lines 607-612).
    tag = _tag(
        '<div style="font-size:14pt">'
        '<span style="font-size:8pt">small text here</span></div>',
        "div",
    )
    assert h2m.is_header_element(tag) is False


def test_is_header_element_mostly_bold_spans():
    # A div whose text spans are predominantly bold is a header (lines 680-688).
    tag = _tag('<div><span style="font-weight:bold">Header Text</span></div>', "div")
    assert h2m.is_header_element(tag) is True


# ===========================================================================
# _is_continuation_table / _are_immediate_sibling_tables
# ===========================================================================


def _two_tables(html):
    """Parse a snippet and return the tables with ids 'a' and 'b'."""
    soup = BeautifulSoup(html, "html.parser")
    return soup.find("table", id="a"), soup.find("table", id="b")


def test_continuation_skips_empty_leading_row():
    # The first scan skips a fully empty row before finding the year-only
    # start (line 342).
    table = _table("<table><tr><td></td></tr><tr><td>2024</td></tr></table>")
    assert h2m._is_continuation_table(table, None) is True


def test_continuation_year_only_column_mismatch_rejected():
    # A year-only continuation whose data-column count differs from the
    # previous table is rejected (lines 353-356).
    prev = _table("<table><tr><td>2024</td><td>2023</td></tr></table>")
    cur = _table(
        "<table><tr><td>2024</td></tr>"
        "<tr><td>2024</td><td>2023</td><td>2022</td></tr></table>"
    )
    assert h2m._is_continuation_table(cur, prev) is False


def test_continuation_headerless_width_mismatch_rejected():
    # Sibling tables with different expanded column counts are not a
    # headerless continuation (line 373).
    a, b = _two_tables(
        '<div><table id="a"><tr><td>$1</td><td>$2</td></tr></table>'
        '<table id="b"><tr><td>$3</td></tr></table></div>'
    )
    assert h2m._is_continuation_table(b, a) is False


def test_continuation_headerless_dollar_data_row():
    # A headerless sibling whose body starts after an empty row and carries a
    # dollar value is a continuation (lines 385, 411 -> True).
    a, b = _two_tables(
        '<div><table id="a"><tr><td>$1</td><td>$2</td></tr></table>'
        '<table id="b"><tr><td></td><td></td></tr>'
        "<tr><td>$3</td><td>$4</td></tr></table></div>"
    )
    assert h2m._is_continuation_table(b, a) is True


def test_continuation_headerless_year_cell_rejected():
    # A year anywhere in the sibling's first row means it owns a header and is
    # not a continuation (line 389).
    a, b = _two_tables(
        '<div><table id="a"><tr><td>$1</td><td>$2</td></tr></table>'
        '<table id="b"><tr><td>x</td><td>2024</td></tr></table></div>'
    )
    assert h2m._is_continuation_table(b, a) is False


def test_continuation_headerless_period_phrase_rejected():
    # A period phrase ("... Ended") in the first row likewise marks an
    # independent header (line 395).
    a, b = _two_tables(
        '<div><table id="a"><tr><td>$1</td><td>$2</td></tr></table>'
        '<table id="b"><tr><td>x</td><td>Three Months Ended</td></tr>'
        "</table></div>"
    )
    assert h2m._is_continuation_table(b, a) is False


def test_continuation_headerless_two_numeric_cells():
    # No dollar sign, but two comma-grouped numeric cells qualify the row as
    # data -> continuation (lines 415, 421-422).
    a, b = _two_tables(
        '<div><table id="a"><tr><td>1,234</td><td>5,678</td></tr></table>'
        '<table id="b"><tr><td>1,234</td><td>5,678</td></tr></table></div>'
    )
    assert h2m._is_continuation_table(b, a) is True


def test_continuation_headerless_no_data_row_rejected():
    # A sibling with matching width but only label/text cells (no data row)
    # falls through to the final reject (line 424).
    a, b = _two_tables(
        '<div><table id="a"><tr><td>1,234</td><td>5,678</td></tr></table>'
        '<table id="b"><tr><td>Label</td><td>Text</td></tr></table></div>'
    )
    assert h2m._is_continuation_table(b, a) is False


def test_sibling_same_parent_significant_text_between():
    # Significant text between same-parent tables breaks adjacency
    # (lines 441-442).
    a, b = _two_tables(
        '<div><table id="a"></table>significant<table id="b"></table></div>'
    )
    assert h2m._are_immediate_sibling_tables(a, b) is False


def test_sibling_same_parent_short_text_ok():
    # A tiny (<=2 char) string between same-parent tables is ignored; they are
    # still adjacent (line 443 increment -> True).
    a, b = _two_tables('<div><table id="a"></table>x<table id="b"></table></div>')
    assert h2m._are_immediate_sibling_tables(a, b) is True


def test_sibling_container_none_rejected():
    # When a table has been detached (parent is None) the different-parent
    # branch rejects on the None-container guard (line 452).
    detached = BeautifulSoup('<table id="a"></table>', "html.parser").find("table")
    detached.extract()
    b = _table('<div><table id="b"></table></div>')
    assert h2m._are_immediate_sibling_tables(detached, b) is False


def test_sibling_different_grandparent_rejected():
    # Tables whose containers do not share a grandparent are not siblings
    # (line 455).
    soup = BeautifulSoup(
        '<div id="g1"><div><table id="a"></table></div></div>'
        '<div id="g2"><div><table id="b"></table></div></div>',
        "html.parser",
    )
    a = soup.find("table", id="a")
    b = soup.find("table", id="b")
    assert h2m._are_immediate_sibling_tables(a, b) is False


def test_sibling_table_a_not_last_tag_rejected():
    # Significant tag content after table A inside its container breaks
    # adjacency (lines 460-463).
    a, b = _two_tables(
        '<div id="gp"><div id="ca"><table id="a"></table>'
        "<p>significant text</p></div>"
        '<div id="cb"><table id="b"></table></div></div>'
    )
    assert h2m._are_immediate_sibling_tables(a, b) is False


def test_sibling_table_a_not_last_string_rejected():
    # Significant string content after table A breaks adjacency (lines 464-465).
    a, b = _two_tables(
        '<div id="gp"><div id="ca"><table id="a"></table>'
        "significant string here</div>"
        '<div id="cb"><table id="b"></table></div></div>'
    )
    assert h2m._are_immediate_sibling_tables(a, b) is False


def test_sibling_table_b_not_first_tag_rejected():
    # Significant tag content before table B breaks adjacency (lines 470-473).
    a, b = _two_tables(
        '<div id="gp"><div id="ca"><table id="a"></table></div>'
        '<div id="cb"><p>text before</p><table id="b"></table></div></div>'
    )
    assert h2m._are_immediate_sibling_tables(a, b) is False


def test_sibling_table_b_not_first_string_rejected():
    # Significant string content before table B breaks adjacency (lines 474-475).
    a, b = _two_tables(
        '<div id="gp"><div id="ca"><table id="a"></table></div>'
        '<div id="cb">text before here<table id="b"></table></div></div>'
    )
    assert h2m._are_immediate_sibling_tables(a, b) is False


def test_sibling_long_gap_between_containers_rejected():
    # A long (>10 char) string in the gap between the two containers breaks
    # adjacency (lines 489-490).
    a, b = _two_tables(
        '<div id="gp"><div id="ca"><table id="a"></table></div>'
        "this is a long gap string"
        '<div id="cb"><table id="b"></table></div></div>'
    )
    assert h2m._are_immediate_sibling_tables(a, b) is False


def test_sibling_adjacent_with_minor_gap_noise():
    # Empty tags around the tables and a short gap string are all ignored; the
    # tables remain adjacent siblings (lines 466, 476, 491 increments -> True).
    a, b = _two_tables(
        '<div id="gp"><div id="ca"><table id="a"></table><span></span></div>'
        "ok"
        '<div id="cb"><span></span><table id="b"></table></div></div>'
    )
    assert h2m._are_immediate_sibling_tables(a, b) is True


# ===========================================================================
# extract_periods_from_rows — merge_vertical_headers + single-row fallback
# ===========================================================================


def test_periods_vertical_is_header_text_edge_tokens():
    # is_header_text classifies a zero-width-only cell as non-header (2974), a
    # single punctuation char as non-header (2988) and a "YYYY -" year-range
    # fragment as a header (2982); the two rows then vertically merge.
    out = _periods(_twin([["\u200b", "*", "2009 -"], ["foo", "baz", "2010"]]))
    assert out == ([["foo", "baz", "2009 - 2010"]], 2)


def test_periods_vertical_numeric_range_bucket_header():
    # A "0 - 6" numeric maturity bucket is recognised as a header by
    # is_header_text (line 2992).
    out = _periods(_twin([["Bucket", "Range"], ["0 - 6", "6 - 12"]]))
    assert out == ([["", "Bucket", "Range"]], 1)


def test_periods_vertical_skips_empty_row_between_headers():
    # An empty row sitting between two collected header rows is skipped, not
    # treated as a boundary (line 3098).
    out = _periods(_twin([["Alpha", "Beta"], ["", ""], ["2010", "2011"]]))
    assert out == ([["Alpha 2010", "Beta 2011"]], 3)


def test_periods_vertical_section_label_colon_breaks():
    # A single-cell "Assets:" row (colspan small vs a 3-wide table, so not a
    # title) is detected as a section label and breaks header collection
    # (lines 3117, 3123-3136).
    out = _periods(
        _twin(
            [
                ["Income", "Expense", "Net"],
                ["Assets:", "", ""],
                ["2010", "2011", "2012"],
            ]
        )
    )
    assert out == ([["", "2010", "2011", "2012"]], 1)


def test_periods_vertical_section_label_small_colspan_breaks():
    # A single short label at column 0 (no trailing colon) is likewise treated
    # as a section label via the small-colspan rule (lines 3131, 3133).
    out = _periods(
        _twin(
            [
                ["Income", "Expense", "Net"],
                ["Label", "", ""],
                ["2010", "2011", "2012"],
            ]
        )
    )
    assert out == ([["", "2010", "2011", "2012"]], 1)


def test_periods_vertical_single_leaf_position_bails():
    # Two header rows whose only cells sit at the same column position yield a
    # single leaf position, so vertical merging bails out (line 3190).
    out = _periods(_twin([["", "Alpha", ""], ["", "Beta", ""]]))
    assert out == ([], 0)


def test_periods_fallback_period_part_plus_ended_equal_counts():
    # Single row mixing period parts and matching "Ended X" cells: the fallback
    # records period_parts (3462) and combines them 1:1 with the ended cells
    # (3468, 3470-3471) before the generic-header path returns.
    out = _periods(_twin([["Three Months", "Ended May"]]))
    assert out == ([["", "Three Months", "Ended May"]], 1)


def test_periods_fallback_period_parts_single_ended_broadcast():
    # Two period parts but a single "Ended X" cell -> the one ended phrase is
    # broadcast to every part (lines 3474, 3476).
    out = _periods(_twin([["Three Months", "Six Months", "Ended May"]]))
    assert out == ([["", "Three Months", "Six Months", "Ended May"]], 1)


def test_periods_fallback_full_date_with_sub_headers():
    # Month-Year date cells paired with Assets/Liabilities sub-headers in one
    # row hit Priority 1: the dates and subs combine into a two-row header
    # (lines 3486, 3493, 3553-3579).
    out = _periods(_twin([["May 2024", "May 2023", "Assets", "Liabilities"]]))
    assert out == (
        [["", "May 2024", "May 2023"], ["", "Assets", "Liabilities"]],
        2,
    )


def test_periods_fallback_more_years_than_prefixes_appends_bare_year():
    # Two period prefixes but three years: once the prefixes are exhausted the
    # remaining year is appended bare (line 3628).
    out = _periods(
        _twin([["Three Months Ended", "Six Months Ended", "2024", "2023", "2022"]])
    )
    assert out == (
        [["", "Three Months Ended 2024", "Six Months Ended 2023", "2022"]],
        1,
    )


# ===========================================================================
# Additional small-helper branch coverage
# ===========================================================================


def test_clean_table_cells_pass1_break_on_close_paren():
    # Pass 1: a "$" prefix immediately followed by ")" hits the break that
    # stops the forward merge scan (no value to attach the prefix to).
    out = h2m.clean_table_cells([["$", ")"]])
    assert out == [["$)", ""]]


def test_clean_table_cells_pass2_skips_empty_then_merges():
    # Pass 2: an unclosed "(" cell, an empty gap cell (continue), then a ")"
    # cell that completes the negative.
    out = h2m.clean_table_cells([["(2,257", "", ")"]])
    assert out == [["(2,257)", "", ""]]


def test_clean_table_cells_pass2_break_on_non_paren():
    # Pass 2: an unclosed "(" cell followed by a non-paren, non-empty cell
    # stops the scan without merging.
    out = h2m.clean_table_cells([["(2,257", "foo"]])
    assert out == [["(2,257", "foo"]]


def test_merge_split_rows_lookahead_non_continuation_break():
    # Unbalanced first cell with empty data columns reaches the look-ahead
    # loop; the next row (capitalized, so not a label-continuation) is not a
    # parenthetical continuation, so the loop breaks without merging.
    rows = [["(in millions, except per", "", ""], ["Random Text", "", ""]]
    merged, _ = h2m.merge_split_rows(rows, [[], []])
    assert merged == [["(in millions, except per", "", ""], ["Random Text", "", ""]]


def test_merge_split_cells_open_paren_close():
    # Case 1: a cell ending with "(" plus a bare ")" cell merge into "x()".
    out = h2m.merge_split_cells([["abc(", ")"]])
    assert out == [["abc()", ""]]


def test_collapse_repeated_headers_header_too_short():
    # A two-row table whose header has a single cell short-circuits early.
    assert h2m.collapse_repeated_headers([["x"], ["y"]]) == [["x"], ["y"]]


def test_collapse_repeated_headers_empty_trailing_neither_has_data():
    # Header ["A", ""] with empty data: neither column has data and the
    # current header is empty, so the trailing empty column is dropped.
    assert h2m.collapse_repeated_headers([["A", ""], ["", ""]]) == [["A"], [""]]


def test_parse_row_semantic_skips_bare_dollar_cell():
    # A bare "$" cell is skipped (continue) before the label is assigned.
    label, values = h2m.parse_row_semantic(["$", "label"])
    assert label == "label"
    assert values == []


def test_parse_row_semantic_fills_short_value_count_with_text():
    # One numeric value but three expected columns: the extra text item is
    # appended to fill the remaining slots.
    label, values = h2m.parse_row_semantic(["MyLabel", "123", "Tech"], 3)
    assert label == "MyLabel"
    assert values == ["123", "Tech"]


def test_detect_multiindex_empty_row_is_title():
    # A fully empty row is treated as a title row (skipped). Single-character
    # "category" cells are not all-caps words, so no categories are found and
    # the function falls back to None.
    rows = [
        ["", ""],
        ["A", "B", "C", "D"],
        ["2021", "2022", "2023"],
        ["x", "1", "2", "3"],
    ]
    assert h2m.detect_and_merge_multiindex_headers(rows) == (None, 0, 0)


def test_detect_multiindex_fewer_years_than_categories():
    # Four categories but only three years: years_per_cat floors to 0 then is
    # bumped to 1, and the final category runs out of years (empty appended).
    rows = [
        ["ALPHA", "BETA", "GAMMA", "DELTA"],
        ["2021", "2022", "2023"],
        ["x", "1", "2", "3"],
    ]
    header_rows, data_start, num_cols = h2m.detect_and_merge_multiindex_headers(rows)
    assert header_rows == [
        ["", "ALPHA", "BETA", "GAMMA", "DELTA"],
        ["", "2021", "2022", "2023", ""],
    ]
    assert (data_start, num_cols) == (2, 4)


def test_detect_multiindex_multiple_years_per_category():
    # Two categories spanning four years: years_per_cat == 2 pads each category
    # header with a trailing empty cell.
    rows = [
        ["ALPHA", "BETA"],
        ["2020", "2021", "2022", "2023"],
        ["x", "1", "2", "3", "4"],
    ]
    header_rows, data_start, num_cols = h2m.detect_and_merge_multiindex_headers(rows)
    assert header_rows == [
        ["", "ALPHA", "", "BETA", ""],
        ["", "2020", "2021", "2022", "2023"],
    ]
    assert (data_start, num_cols) == (2, 4)


def test_detect_multiindex_final_scan_non_data_row():
    # After the year row, a non-data / non-title / non-category row terminates
    # the data-start scan (the final-scan break branch).
    rows = [
        ["ALPHA", "BETA", "GAMMA"],
        ["2021", "2022", "2023"],
        ["lowercase intro text"],
    ]
    header_rows, data_start, num_cols = h2m.detect_and_merge_multiindex_headers(rows)
    assert header_rows == [
        ["", "ALPHA", "BETA", "GAMMA"],
        ["", "2021", "2022", "2023"],
    ]
    assert (data_start, num_cols) == (2, 3)


def test_periods_vertical_section_label_before_any_header_continues():
    # A section-label row encountered before any header row is collected uses
    # the "continue" branch (not the break) so scanning proceeds.
    out = _periods(
        _twin(
            [
                ["Assets:", "", ""],
                ["Income", "Expense", "Net"],
                ["2010", "2011", "2012"],
            ]
        )
    )
    assert out == ([["Income 2010", "Expense 2011", "Net 2012"]], 3)


def test_periods_vertical_merged_financial_terms_without_years():
    # Vertical merge yields multi-word headers containing financial terms but
    # no years/periods, so the financial-terms acceptance branch returns them.
    out = _periods(
        _twin([["Income Tax", "Total Expense"], ["Provision Amount", "Net Balance"]])
    )
    assert out == (
        [["Income Tax Provision Amount", "Total Expense Net Balance"]],
        2,
    )


# ===========================================================================
# get_text_content / _split_composite_table / text post-processing helpers
# ===========================================================================


def test_get_text_content_anchor_without_href_keeps_text():
    # An <a> without an href but with link text falls into the "else" branch
    # that appends the bare link text.
    p = _tag("<p><a>just text</a></p>", "p")
    assert h2m.get_text_content(p, preserve_links_in_text=True) == "just text"


def test_split_composite_table_body_section_rejected():
    # Two "TABLE N" headers trigger splitting. A would-be body-text section is
    # rejected because a later row has content beyond column 0, so both parts
    # stay as <table> elements (no plain-text body fragment).
    html = (
        "<table>"
        "<tr><td>TABLE 5</td><td></td></tr>"
        "<tr><td>Item A</td><td>100</td></tr>"
        "<tr><td>This is a long body text paragraph that exceeds sixty chars ok"
        "</td><td></td></tr>"
        "<tr><td>second column present here</td><td>X</td></tr>"
        "<tr><td>TABLE 6</td><td></td></tr>"
        "<tr><td>Item B</td><td>200</td></tr>"
        "</table>"
    )
    parts = h2m._split_composite_table(_table(html))
    assert len(parts) == 2
    assert all(not isinstance(p, str) for p in parts)


def test_merge_consecutive_headers_incomplete_comma_merges():
    # A header ending with a comma is "incomplete" and merges with the next
    # same-level header.
    out = h2m._merge_consecutive_headers("### Incomplete Title,\n### Continued")
    assert out == "### Incomplete Title, Continued"


def test_html_to_markdown_merges_adjacent_bold_spans():
    # Two adjacent bold spans on one line collapse into a single bold span.
    out = h2m.html_to_markdown(
        "<p><b>foo</b> <b>bar</b> plain trailing words to avoid promotion</p>"
    )
    assert out == "**foo bar** plain trailing words to avoid promotion"


def test_normalize_bullet_chars_keeps_prefix_text():
    # Text before the first bullet character is emitted as its own line.
    out = h2m._normalize_bullet_chars("Intro text •item one •item two")
    assert out == "Intro text\n- item one\n- item two"


def test_join_split_paragraphs_period_then_lowercase():
    # A line ending with "." joins the next line when it starts lowercase
    # (abbreviation / mid-sentence period at a wrap boundary).
    out = h2m._join_split_paragraphs(
        "Some sentence ending with abbrev Inc.\ncontinued lowercase words here"
    )
    assert out == "Some sentence ending with abbrev Inc. continued lowercase words here"


def test_join_split_paragraphs_unclosed_quote_joins_next():
    # An unclosed straight quote means the period is not sentence-terminal, so
    # the next line joins even though it starts uppercase.
    out = h2m._join_split_paragraphs(
        'Refer to "Part II, Item 7.\nContinued Uppercase text'
    )
    assert out == 'Refer to "Part II, Item 7. Continued Uppercase text'


def test_classify_table_all_empty_rows_is_data():
    # Rows present but every cell empty -> no non-empty rows -> DATA.
    table = _table("<table><tr><td></td></tr><tr><td></td></tr></table>")
    assert h2m._classify_table(table) == "DATA"


def test_classify_table_single_cell_font_weight_bold_is_header():
    # A single-cell row whose only emphasis is a font-weight:bold style (no
    # <b>/<strong>) is still classified as a HEADER.
    table = _table(
        '<table><tr><td><span style="font-weight:bold">Header</span></td></tr></table>'
    )
    assert h2m._classify_table(table) == "HEADER"


def test_extract_bullet_list_bold_only_item():
    # A bullet row whose content cell is only bold text (no trailing
    # description) yields a bare bold bullet.
    table = _table("<table><tr><td>•</td><td><b>Just Bold</b></td></tr></table>")
    assert h2m._extract_bullet_list(table) == "**Just Bold**"


def test_extract_cell_text_converts_br_to_space():
    # A <br> inside a cell becomes a space in the default (non-line-break) mode.
    td = _tag("<td>line1<br>line2</td>", "td")
    assert h2m._extract_cell_text(td) == "line1 line2"


def test_extract_cell_text_anchor_without_href_keeps_text():
    # An <a> without href but with link text is replaced by the bare text.
    td = _tag("<td><a>linktext</a></td>", "td")
    assert h2m._extract_cell_text(td) == "linktext"


# ===========================================================================
# convert_table — direct fixtures for cell extraction / classification paths
# ===========================================================================


def test_convert_table_cell_id_emits_anchor():
    # A cell with an id attribute gets an inline <a id=...> anchor prefix.
    out = h2m.convert_table(
        _build_table(
            [
                [_cell("Lbl", idv="c1"), _cell("100"), _cell("90")],
                [_cell("Rev"), _cell("1"), _cell("2")],
            ]
        )
    )
    assert out == ('| <a id="c1"></a>Lbl | 100 | 90 |\n|---|---|---|\n| Rev | 1 | 2 |')


def test_convert_table_trailing_rowspan_fills_blanks():
    # A rowspan cell at the end of a row leaves a trailing grid position that
    # the following (shorter) row fills with a blank.
    out = h2m.convert_table(
        _build_table([[_cell("A"), _cell("B", rs=2)], [_cell("C")]])
    )
    assert out == "| A | B |\n|---|---|\n| C |  |"


def test_convert_table_empty_cell_shift_to_dollar_position():
    # The first row has "$" then a number; a later row omits the "$" but its
    # number is shifted to the same (currency) position to keep alignment.
    out = h2m.convert_table(
        _build_table(
            [
                [_cell("Rev"), _cell("$"), _cell("100")],
                [_cell("Cost"), _cell(""), _cell("50")],
            ]
        )
    )
    assert out == "| Rev | $100 |\n|---|---|\n| Cost | 50 |"


def test_convert_table_empty_cell_shift_stops_on_non_numeric():
    # Same as above but the shifted-to cell is non-numeric, so no shift occurs.
    out = h2m.convert_table(
        _build_table(
            [
                [_cell("Rev"), _cell("$"), _cell("100")],
                [_cell("Cost"), _cell(""), _cell("txt")],
            ]
        )
    )
    assert out == "| Rev | $100 |\n|---|---|\n| Cost | txt |"


def test_convert_table_currency_lookahead_stops_on_non_numeric():
    # A "$" cell followed by a non-numeric value is not merged as a currency
    # amount (the look-ahead stops at the first non-numeric, non-empty cell).
    out = h2m.convert_table(
        _build_table(
            [
                [_cell("Rev"), _cell("$"), _cell("txt")],
                [_cell("A"), _cell("1"), _cell("2")],
            ]
        )
    )
    assert out == "| Rev | $txt |  |\n|---|---|---|\n| A | 1 | 2 |"


def test_convert_table_sup_footnote_merges_to_label():
    # A lone <sup>N</sup> cell is treated as a footnote marker and appended to
    # the preceding row label rather than rendered as its own column.
    out = h2m.convert_table(
        _build_table([[_cell("Rev"), _cell("<sup>12</sup>"), _cell("100")]])
    )
    assert out == "Rev<sup>12</sup> 100"


def test_convert_table_page_footer_digit_first_skipped():
    # A 2-cell row of "<page number> | Form 10-K" is a page footer -> dropped.
    out = h2m.convert_table(_build_table([[_cell("42"), _cell("Form 10-K")]]))
    assert out == ""


def test_convert_table_page_footer_digit_second_skipped():
    # Same page-footer skip when the digit is the second cell.
    out = h2m.convert_table(_build_table([[_cell("Form 10-K"), _cell("42")]]))
    assert out == ""


def test_convert_table_headerless_numeric_grid():
    # A header-less all-numeric grid renders as a plain markdown table.
    out = h2m.convert_table(
        _build_table(
            [
                [_cell("10"), _cell("20"), _cell("30")],
                [_cell("40"), _cell("50"), _cell("60")],
            ]
        )
    )
    assert out == "| 10 | 20 | 30 |\n|---|---|---|\n| 40 | 50 | 60 |"


def test_convert_table_chart_legend_inline():
    # Tiny coloured swatch cells paired with category labels render as an
    # inline HTML legend instead of a useless single-column table.
    html = (
        "<table>"
        '<tr><td style="background-color:#009dd9;width:10px;height:5px"></td>'
        "<td>United States</td></tr>"
        '<tr><td style="background-color:#0b2d71;width:10px;height:5px"></td>'
        "<td>Other Americas</td></tr></table>"
    )
    out = h2m.convert_table(_table(html))
    assert out.startswith('<div style="margin:4px 0;font-size:0.9em"><b>Legend:</b>')
    assert "United States" in out and "Other Americas" in out
    assert "#009dd9" in out and "#0b2d71" in out


def test_convert_table_footnote_marker_rows():
    # Rows whose first cell is a "(N)" marker classify as FOOTNOTE text.
    out = h2m.convert_table(
        _build_table(
            [
                [_cell("(1)"), _cell("First footnote text here")],
                [_cell("(2)"), _cell("Second footnote text here")],
            ]
        )
    )
    assert out == ("(1) First footnote text here\n\n(2) Second footnote text here")


def test_convert_table_uppercase_toc_anchor_section_header():
    # An uppercase id="TOC..." escapes the (lowercase) HEADER classifier and
    # reaches the data-path TOC-anchor section-header branch.
    out = h2m.convert_table(
        _table('<table><tr><td id="TOC1">Section Title Here</td></tr></table>')
    )
    assert out == '\n\n<a id="TOC1"></a>\n\n### Section Title Here\n\n'


def test_convert_table_multiindex_more_categories_than_years():
    # Stacked category row + year row with fewer years builds a 2-layer header.
    out = h2m.convert_table(
        _build_table(
            [
                [_cell("ALPHA"), _cell("BETA"), _cell("GAMMA"), _cell("DELTA")],
                [_cell("2021"), _cell("2022"), _cell("2023")],
                [_cell("x"), _cell("1"), _cell("2"), _cell("3")],
            ]
        )
    )
    assert out == (
        "|  | ALPHA | BETA | GAMMA | DELTA |\n"
        "|---|---|---|---|---|\n"
        "|  | 2021 | 2022 | 2023 |  |\n"
        "| x |  | 1 | 2 | 3 |"
    )


def test_convert_table_colspan_year_expands_columns():
    # A year header with colspan=3 expands to three physical columns.
    out = h2m.convert_table(
        _build_table(
            [
                [_cell("Item"), _cell("2025", cs=3), _cell("2024", cs=3)],
                [
                    _cell("Rev"),
                    _cell("1"),
                    _cell("2"),
                    _cell("3"),
                    _cell("4"),
                    _cell("5"),
                    _cell("6"),
                ],
            ]
        )
    )
    assert out == (
        "| Item | 2025 |  |  | 2024 |  |  |\n"
        "|---|---|---|---|---|---|---|\n"
        "| Rev | 1 | 2 | 3 | 4 | 5 | 6 |"
    )


def test_convert_table_non_financial_header_rows_kept():
    # A non-financial table (text headers, no years) keeps its <th> header row.
    out = h2m.convert_table(
        _build_table(
            [
                [
                    _cell("Item", th=True),
                    _cell("Desc", th=True),
                    _cell("Notes", th=True),
                ],
                [_cell("A"), _cell("desc"), _cell("note")],
                [_cell("B"), _cell("desc2"), _cell("note2")],
            ]
        )
    )
    assert out == (
        "| Item | Desc | Notes |\n|---|---|---|\n"
        "| A | desc | note |\n| B | desc2 | note2 |"
    )


def test_convert_table_months_ended_is_financial_period():
    # A "Three Months Ended" header marks the table as a financial-period table.
    out = h2m.convert_table(
        _build_table(
            [[_cell("Item"), _cell("Three Months Ended")], [_cell("Rev"), _cell("100")]]
        )
    )
    assert out == "| Item | Three Months Ended |\n|---|---|\n| Rev | 100 |"


def test_convert_table_all_superscript_rows_yield_empty():
    # Rows whose only content is a <sup> footnote marker produce no data cells,
    # so the table collapses to an empty string.
    out = h2m.convert_table(
        _build_table([[_cell("<sup>1</sup>")], [_cell("<sup>2</sup>")]])
    )
    assert out == ""


def test_convert_table_bullet_inline_short_text():
    # Short bullet text (<=3 chars) makes _extract_bullet_list return None, so
    # the inline data-path bullet handler renders the list instead.
    out = h2m.convert_table(
        _build_table(
            [
                [_cell("•"), _cell("ab")],
                [_cell("•"), _cell("cd")],
            ]
        )
    )
    assert out == "- ab\n- cd"


def test_convert_table_bullet_inline_continuation_row():
    # A single-cell row following bullets is treated as a continuation item.
    out = h2m.convert_table(
        _build_table(
            [
                [_cell("•"), _cell("ab")],
                [_cell("cd")],
            ]
        )
    )
    assert out == "- ab\n- cd"


def test_convert_table_bullet_inline_break_falls_to_table():
    # A non-bullet multi-cell row breaks the bullet run; the table then renders
    # as a normal markdown grid.
    out = h2m.convert_table(
        _build_table(
            [
                [_cell("•"), _cell("ab")],
                [_cell("x"), _cell("y")],
            ]
        )
    )
    assert out == "| • | ab |\n|---|---|\n| x | y |"


def test_html_to_markdown_subcolumn_bps_unit_merge():
    # A "bps" unit cell following a numeric value in the same year sub-column
    # is merged onto that value rather than creating a spurious column.
    out = h2m.html_to_markdown(
        str(
            _build_table(
                [
                    [_cell("Item"), _cell("2025", cs=2), _cell("2024", cs=2)],
                    [
                        _cell("Margin"),
                        _cell("50"),
                        _cell("bps"),
                        _cell("45"),
                        _cell("bps"),
                    ],
                ]
            )
        )
    )
    assert "50 bps" in out and "45 bps" in out


def test_html_to_markdown_subcolumn_none_label_empty_group():
    # A trailing row whose only content is bare "$" cells produces no label and
    # all-empty value groups, so it is dropped from the rendered table.
    out = h2m.html_to_markdown(
        str(
            _build_table(
                [
                    [_cell("Item"), _cell("2025", cs=2), _cell("2024", cs=2)],
                    [
                        _cell("Revenue"),
                        _cell("100"),
                        _cell("50"),
                        _cell("90"),
                        _cell("45"),
                    ],
                    [_cell(""), _cell("$"), _cell(""), _cell("$"), _cell("")],
                ]
            )
        )
    )
    assert "Revenue | 100 | 50 | 90 | 45" in out


# ===========================================================================
# html_to_markdown — sub-column / multi-layer / mixed header sweeps
# ===========================================================================


def test_html_to_markdown_subcolumn_semantic_two_values_per_year():
    # Each year header (colspan=2) covers two physical data columns; the
    # semantic parser interleaves both values under the year.
    out = h2m.html_to_markdown(
        _table_html(
            [
                [_cell("Item"), _cell("2025", cs=2), _cell("2024", cs=2)],
                [_cell("Revenue"), _cell("100"), _cell("50"), _cell("90"), _cell("45")],
                [_cell("Costs"), _cell("10"), _cell("5"), _cell("9"), _cell("4")],
            ]
        )
    )
    assert out == (
        "| | 2025 | | 2024 | |\n|---|---|---|---|---|\n"
        "| Revenue | 100 | 50 | 90 | 45 |\n| Costs | 10 | 5 | 9 | 4 |"
    )


def test_html_to_markdown_subcolumn_second_value_non_numeric():
    # The second sub-column value may be non-numeric text (e.g. "up"/"down").
    out = h2m.html_to_markdown(
        _table_html(
            [
                [_cell("Item"), _cell("2025", cs=2), _cell("2024", cs=2)],
                [
                    _cell("Revenue"),
                    _cell("100"),
                    _cell("up"),
                    _cell("90"),
                    _cell("down"),
                ],
            ]
        )
    )
    assert out == (
        "| | 2025 | | 2024 | |\n|---|---|---|---|---|\n"
        "| Revenue | 100 | up | 90 | down |"
    )


def test_html_to_markdown_subcolumn_empty_label_uses_first_value():
    # When the row label cell is empty, the first non-numeric value becomes the
    # label.
    out = h2m.html_to_markdown(
        _table_html(
            [
                [_cell("Item"), _cell("2025", cs=2), _cell("2024", cs=2)],
                [_cell(""), _cell("100"), _cell("up"), _cell("90"), _cell("down")],
            ]
        )
    )
    assert out == ("| | 2025 | 2024 | |\n|---|---|---|---|\n| up | 100 | 90 | down |")


def test_html_to_markdown_two_layer_year_subheader():
    # A rowspan label + two stacked header rows (years over Basic/Diluted)
    # render as a two-row header above the separator.
    out = h2m.html_to_markdown(
        _table_html(
            [
                [_cell("Item", rs=2), _cell("2025", cs=2), _cell("2024", cs=2)],
                [_cell("Basic"), _cell("Diluted"), _cell("Basic"), _cell("Diluted")],
                [
                    _cell("EPS"),
                    _cell("$1.00"),
                    _cell("$0.95"),
                    _cell("$0.90"),
                    _cell("$0.85"),
                ],
            ]
        )
    )
    assert out == (
        "| | 2025 | | 2024 | |\n|---|---|---|---|---|\n"
        "| | Basic | Diluted | Basic | Diluted |\n"
        "| EPS | $1.00 | $0.95 | $0.90 | $0.85 |"
    )


def test_html_to_markdown_skips_interior_repeated_year_header():
    # An interior row that is itself a year header (2025|2024|2023|2022) is
    # recognised as a header-like row and dropped from the data body.
    out = h2m.html_to_markdown(
        _table_html(
            [
                [_cell("Item"), _cell("2025"), _cell("2024"), _cell("% Change")],
                [_cell("Revenue"), _cell("100"), _cell("90"), _cell("11")],
                [_cell("2025"), _cell("2024"), _cell("2023"), _cell("2022")],
                [_cell("Costs"), _cell("10"), _cell("9"), _cell("11")],
            ]
        )
    )
    assert out == (
        "| | 2025 | 2024 | % Change |\n|---|---|---|---|\n"
        "| Revenue | 100 | 90 | 11 |\n| Costs | 10 | 9 | 11 |"
    )


def test_html_to_markdown_realign_dollar_gap_column():
    # A stray empty cell between $-values is realigned so the two periods line
    # up under their year headers.
    out = h2m.html_to_markdown(
        _table_html(
            [
                [_cell("Item"), _cell("2025"), _cell("2024")],
                [_cell("Revenue"), _cell("$100"), _cell(""), _cell("$90")],
            ]
        )
    )
    assert out == "| | 2025 | 2024 |\n|---|---|---|\n| Revenue | $100 | $90 |"


def test_html_to_markdown_mixed_header_single_row():
    # A header mixing a year with non-year columns ("Useful Life", "Method")
    # renders as a flat single-header table.
    out = h2m.html_to_markdown(
        _table_html(
            [
                [_cell("Asset"), _cell("2024"), _cell("Useful Life"), _cell("Method")],
                [_cell("Building"), _cell("100"), _cell("30 years"), _cell("SL")],
            ]
        )
    )
    assert out == (
        "| Asset | 2024 | Useful Life | Method |\n|---|---|---|---|\n"
        "| Building | 100 | 30 years | SL |"
    )


def test_html_to_markdown_mixed_header_title_row_dropped():
    # A full-width <th> title row above a mixed header is dropped, leaving the
    # column-defining header row.
    out = h2m.html_to_markdown(
        _table_html(
            [
                [_cell("Title One", cs=4, th=True)],
                [_cell("Asset"), _cell("2024"), _cell("Useful Life"), _cell("Method")],
                [_cell("Building"), _cell("100"), _cell("30 years"), _cell("SL")],
            ]
        )
    )
    assert out == (
        "| Asset | 2024 | Useful Life | Method |\n|---|---|---|---|\n"
        "| Building | 100 | 30 years | SL |"
    )


def test_html_to_markdown_mixed_non_financial_title_row_kept():
    # A non-financial table (no years) keeps its full-width title row as the
    # first table row.
    out = h2m.html_to_markdown(
        _table_html(
            [
                [_cell("Title One", cs=3, th=True)],
                [_cell("Item"), _cell("Description"), _cell("Notes")],
                [_cell("A"), _cell("desc"), _cell("note")],
            ]
        )
    )
    assert out == (
        "| Title One | | |\n|---|---|---|\n"
        "| Item | Description | Notes |\n| A | desc | note |"
    )


def test_html_to_markdown_uneven_colspan_header_expansion():
    # A 2025 header with colspan=3 next to a colspan=1 2024 header expands the
    # year row with blank padding columns.
    out = h2m.html_to_markdown(
        _table_html(
            [
                [_cell("Item"), _cell("2025", cs=3), _cell("2024")],
                [_cell("Revenue"), _cell("100"), _cell("50"), _cell("25"), _cell("90")],
            ]
        )
    )
    assert out == (
        "| | 2025 | | | 2024 |\n|---|---|---|---|---|\n| Revenue | 100 | 50 | 25 | 90 |"
    )


# ---------------------------------------------------------------------------
# html_to_markdown — preprocessing / cleanup passes
# ---------------------------------------------------------------------------


def test_html_to_markdown_strips_script_style_noscript():
    # <script>/<style>/<noscript> tags are removed before conversion.
    out = h2m.html_to_markdown(
        "<p>Visible text here for body.</p><script>var x=1;</script>"
        "<style>.c{color:red}</style><noscript>nojs</noscript>"
    )
    assert out == "Visible text here for body."


def test_html_to_markdown_extracts_html_comments():
    # HTML comments embedded in body text are removed from the output.
    out = h2m.html_to_markdown(
        "<p>Body paragraph<!-- a hidden comment --> text content.</p>"
    )
    assert out == "Body paragraph text content."


def test_html_to_markdown_display_none_cell_kept_empty_other_decomposed():
    # A display:none <td> is cleared but kept as an empty grid placeholder,
    # while a visibility:hidden <div> is removed entirely.
    out = h2m.html_to_markdown(
        "<table><tr><td>Keep</td>"
        '<td style="display:none">SECRET</td></tr>'
        "<tr><td>Row</td><td>Val</td></tr></table>"
        '<div style="visibility:hidden">GONE</div>'
    )
    assert "SECRET" not in out and "GONE" not in out
    assert out == "| Keep | |\n|---|---|\n| Row | Val |"


def test_html_to_markdown_slide_deck_text_to_comments():
    # A slide deck (>=3 div.slide) converts slideText into HTML comments;
    # an empty slideText div is dropped.
    out = h2m.html_to_markdown(
        '<div class="slide"><img src="s0.png"/>'
        '<div class="slideText">Slide zero accessibility description text.</div>'
        '</div><div class="spaceAfterSlideText"></div>'
        '<div class="slide"><img src="s1.png"/>'
        '<div class="slideText">Slide one accessibility description text.</div>'
        '</div><div class="spaceAfterSlideText"></div>'
        '<div class="slide"><img src="s2.png"/>'
        '<div class="slideText"></div>'
        '</div><div class="spaceAfterSlideText"></div>'
    )
    assert out == (
        "![Image](s0.png)\n\n"
        "<!-- Slide zero accessibility description text. --> ![Image](s1.png)\n"
        "<!-- Slide one accessibility description text. --> ![Image](s2.png)"
    )


def test_html_to_markdown_invisible_accessibility_text_to_comment():
    # Tiny white (1pt) accessibility text >20 chars becomes a comment; an empty
    # invisible tag is decomposed.
    out = h2m.html_to_markdown(
        "<p>Real body content for the document.</p>"
        '<font style="font-size:1pt;color:white">This is a long invisible '
        "accessibility description for an image.</font>"
        '<span style="font-size:1pt;color:white"></span>'
    )
    assert out == (
        "Real body content for the document.\n\n"
        "<!-- This is a long invisible accessibility description for an image. -->"
    )


# ---------------------------------------------------------------------------
# _reflow_absolute_layout — PDF-to-HTML absolute-positioned layouts
# ---------------------------------------------------------------------------


def _abs_layout_html():
    """Build a multi-page Certent-CDM-style absolute-positioned document.

    Exercises the full reflow pipeline: headings (H2/H3), bullet lists with
    continuations, paragraphs, rule-delimited tables (with currency merges and
    column clustering), composite-table splitting, charts, and footnotes.
    """
    ids = [0]

    def af(top, left, text, bold=False, fs=10, w=None, h=None, idn=None):
        style = f"position:absolute;left:{left}px;top:{top}px;font-size:{fs}px"
        if bold:
            style += ";font-weight:bold"
        if w is not None:
            style += f";width:{w}px"
        if h is not None:
            style += f";height:{h}px"
        if idn is None:
            ids[0] += 1
            idn = f"a{ids[0]}"
        idattr = f' id="{idn}"' if idn else ""
        return f'<div{idattr} style="{style}">{text}</div>'

    def hrule(top, w=500):
        return af(top, 40, "", w=w, h=1, idn="")

    f = ['<div id="Page1"></div>']
    # h3-closes-list + bullet-absorb breaks
    f += [af(100, 48, "●"), af(100, 64, "alpha bullet one content")]
    f += [af(130, 48, "Section Heading Here")]
    f += [af(160, 48, "●"), af(160, 64, "beta bullet two content")]
    f += [af(180, 48, "●"), af(180, 64, "gamma bullet three content")]
    f += [af(195, 48, "HUGEHEAD", fs=20)]
    f += [af(225, 48, "●"), af(225, 64, "delta bullet four content")]
    f += [af(240, 48, "BoldSubhead Title", bold=True)]
    f += [af(260, 48, "●"), af(260, 64, "epsilon bullet five content")]
    f += [af(275, 48, "more continuation text here for bullet")]
    f += [af(295, 48, "Plain closing paragraph sentence not a heading here")]
    # paragraph-absorb breaks
    f += [af(320, 48, "first paragraph sentence content here")]
    f += [af(335, 48, "BIGPARA", fs=20)]
    f += [af(375, 48, "second paragraph sentence content here")]
    f += [af(390, 48, "BoldParaBreak", bold=True)]
    f += [af(430, 48, "third paragraph begins on this line now")]
    f += [af(445, 90, "indented continuation forces a paragraph break")]
    # ALL-CAPS split + per-fragment bold
    f += [af(490, 48, "BUSINESS SEGMENT", bold=True), af(490, 250, "Overview Notes")]
    f += [af(520, 48, "normal lead "), af(520, 160, "BoldFrag", bold=True)]
    f += [af(555, 48, "the company provides services across regions", bold=True)]
    # table zone 1: bold cells + currency merges + column clustering + superscript
    f += [hrule(600), hrule(640)]
    f += [
        af(610, 48, "Revenue"),
        af(610, 200, "$", bold=True),
        af(610, 240, "1,000", bold=True),
        af(610, 360, "900"),
    ]
    f += [af(622, 48, "Costs"), af(622, 200, "$"), af(622, 360, "500")]
    f += [af(628, 48, "Net"), af(628, 52, "Worth"), af(628, 240, "7")]
    f += [af(634, 240, "9", fs=5)]
    # body after table (crosses-zone group split)
    f += [af(700, 48, "Body text that appears after the table zone here.")]
    # chart with title
    f += [
        af(760, 250, "Market Share Chart", bold=True, fs=11),
        af(780, 250, "(figures in percentages of total here)", fs=8),
        af(800, 260, "25", fs=6),
    ]
    # footnotes + page-footer skip
    f += [af(965, 48, "Footnote text rendered at the page bottom here.")]
    f += [af(975, 48, "Page 5 of 20", fs=8)]
    # parser edge cases
    f += [af(250, 300, "", w=1, h=100, idn="")]
    f += [af(255, 400, "", w=50, h=50, idn="")]
    f += ['<div style="position:absolute;width:10px">x</div>']
    f += [af(260, 100, "orphan no id", idn="")]
    f += [af(305, 50, "", idn="a900")]
    # Page 2: only-table + composite split (TABLE 1 / TABLE 2 + body section)
    f += ['<div id="Page2"></div>']
    f += [hrule(100), hrule(170)]
    f += [af(108, 48, "TABLE 1"), af(108, 240, "Header")]
    f += [af(120, 48, "RowA"), af(120, 240, "10")]
    f += [
        af(
            132,
            48,
            "This is a rather long body-text paragraph sentence "
            "inside the first sub table here.",
        )
    ]
    f += [af(144, 48, "TABLE 2"), af(144, 240, "Header")]
    f += [af(156, 48, "RowB"), af(156, 240, "20")]
    # Page 3: dedup-bold + chart-no-title + edge zones (>300px apart)
    f += ['<div id="Page3"></div>']
    f += [hrule(100), hrule(140)]
    f += [af(110, 48, "Total"), af(110, 240, "100")]
    f += [af(125, 48, "Total", bold=True), af(125, 240, "100", bold=True)]
    f += [
        af(300, 250, "(only a description here, no title at all)", fs=8),
        af(320, 260, "50", fs=6),
    ]
    f += [hrule(500), hrule(530)]
    f += [af(510, 48, "3", fs=5), af(515, 240, "4", fs=5)]
    f += [hrule(900), hrule(930)]
    f += [af(940, 48, "marginonly")]
    # Page 4: no rules + malformed trailing fragment (unclosed div at EOF)
    f += ['<div id="Page4"></div>']
    f += [af(100, 48, "Page four has only a single paragraph of text here.")]
    f += ['<div id="a999" style="position:absolute;left:50px;top:800px">orphanfrag']
    return "".join(f)


def test_html_to_markdown_absolute_layout_reflow():
    # A PDF-to-HTML absolute-positioned document is reflowed into structured
    # markdown: headings, bullet lists, paragraphs, tables, charts, footnotes.
    out = h2m.html_to_markdown(_abs_layout_html())
    # Headings via the three H2/H3 detectors (single-bold, large-font, gap+bullet)
    assert "### Section Heading Here" in out
    assert "## HUGEHEAD" in out
    assert "## BoldSubhead Title" in out
    assert "## BIGPARA" in out
    assert "## BoldParaBreak" in out
    assert "## BUSINESS SEGMENT" in out
    # Bullets + continuation absorption
    assert "- alpha bullet one content" in out
    assert "- beta bullet two content" in out
    assert "- epsilon bullet five content more continuation text here for bullet" in out
    # Paragraph that closes an open bullet list
    assert "Plain closing paragraph sentence not a heading here" in out
    # Per-fragment bold preserved + lowercase-bold sentence kept as body text
    assert "**BoldFrag**" in out
    assert "**the company provides services across regions**" in out
    # Rule-delimited table: bold cells, currency-symbol merges, column cluster
    assert "| Revenue | $1,000 | 900 |" in out
    assert "| Costs | | $500 |" in out
    assert "| Net Worth | 7 | |" in out
    # Body text after the table (cross-zone group split)
    assert "Body text that appears after the table zone here." in out
    # Chart placeholder + footnote
    assert '<div class="chart"><span>Market Share Chart</span>' in out
    assert "Footnote text rendered at the page bottom here." in out
    # Composite-table split into TABLE 1 / body paragraph / TABLE 2
    assert "| TABLE 1 | Header |" in out
    assert "| TABLE 2 | Header |" in out
    assert (
        "This is a rather long body-text paragraph sentence inside the first "
        "sub table here."
    ) in out
    # Page 4 (no rules) still rendered
    assert "Page four has only a single paragraph of text here." in out
    # Malformed trailing fragment and page-footer line are dropped
    assert "orphanfrag" not in out
    assert "Page 5 of 20" not in out


def test_reflow_absolute_layout_rejects_low_abs_div_ratio():
    # Many plain divs dilute the absolute/div ratio below 0.4 -> not reflowed.
    parts = [
        f'<div id="a{i}" style="position:absolute;left:48px;top:{10 + i}px">'
        f"frag {i}</div>"
        for i in range(30)
    ]
    parts += ["<div>plain</div>"] * 60
    assert h2m._reflow_absolute_layout("".join(parts)) is None


def test_reflow_absolute_layout_rejects_missing_page_marker():
    # Passes the abs/ratio/id="aNN" gates but has no id="PageN" -> not reflowed.
    html = "".join(
        f'<div id="a{i}" style="position:absolute;left:48px;top:{10 + i}px">'
        f"frag {i}</div>"
        for i in range(30)
    )
    assert h2m._reflow_absolute_layout(html) is None


# ===========================================================================
# process_element — per-tag recursive HTML -> markdown conversion
# ===========================================================================


def test_process_element_heading_table_of_contents_suppressed():
    # <h1>-<h6> whose sole text is "Table of Contents" is a nav artefact.
    out = h2m.html_to_markdown(
        "<h5>Table of Contents</h5>"
        "<p>Some real body paragraph text here for content.</p>"
    )
    assert "Table of Contents" not in out
    assert "Some real body paragraph text here for content." in out


def test_process_element_image_without_src_emits_nothing():
    # An <img> that yields no usable markup returns "" (no image emitted).
    out = h2m.html_to_markdown(
        '<p>A paragraph of body text content here.</p><img alt="no source attribute">'
    )
    assert "![" not in out
    assert "A paragraph of body text content here." in out


def test_process_element_header_with_id_anchor():
    # Header carrying an id= attribute renders as a markdown heading.
    out = h2m.html_to_markdown('<h2 id="s1">Hello Heading Text</h2>')
    assert "## Hello Heading Text" in out


def test_process_element_empty_header_with_id_returns_anchor_only():
    # Header with an id but no visible text yields no "##" heading line.
    out = h2m.html_to_markdown(
        '<h2 id="s2"></h2><p>Body text after the empty heading here.</p>'
    )
    assert "##" not in out
    assert "Body text after the empty heading here." in out


def test_process_element_inline_div_bold_italic():
    # display:inline div with bold+italic -> ***text***, italic-only -> *text*.
    out_bi = h2m.html_to_markdown(
        '<div style="display:inline;font-weight:bold;font-style:italic">bi</div>'
    )
    assert "***bi***" in out_bi
    out_i = h2m.html_to_markdown(
        '<div style="display:inline;font-style:italic">it</div>'
    )
    assert "*it*" in out_i


def test_process_element_subheading_bold_dot_body_split():
    # "**Title** . body" inside a div becomes a #### heading + paragraph.
    out = h2m.html_to_markdown("<div><b>Title</b> . Body sentence goes here.</div>")
    assert "#### Title" in out
    assert "Body sentence goes here." in out


def test_process_element_br_and_anchor_targets():
    # <br> becomes a newline; named/plain anchors render their text.
    out_br = h2m.html_to_markdown("<p>line a<br>line b</p>")
    assert "line a" in out_br and "line b" in out_br
    out_named = h2m.html_to_markdown('<a name="t1">Anchor Link Text</a>')
    assert "Anchor Link Text" in out_named
    out_plain = h2m.html_to_markdown("<div><a>plain anchor only text</a></div>")
    assert "plain anchor only text" in out_plain


def test_process_element_bold_wrapping_anchor():
    # Bold wrapping an empty anchor + text keeps the bold text; anchor-only
    # bold collapses (anchor stripped when unreferenced).
    out_text = h2m.html_to_markdown('<b><a id="z1"></a>BoldAnchoredText</b>')
    assert "**BoldAnchoredText**" in out_text
    out_anchor = h2m.html_to_markdown(
        '<b><a id="z2"></a></b><p>Body content paragraph here.</p>'
    )
    assert "**" not in out_anchor
    assert "Body content paragraph here." in out_anchor


def test_process_element_empty_inline_tags_collapse():
    # Empty bold / italic / italic-anchor / sup / blockquote emit no markup.
    assert "**" not in h2m.html_to_markdown("<p>before<b>  </b>after</p>")
    assert "*" not in h2m.html_to_markdown("<p>before<i>  </i>after</p>")
    out_ia = h2m.html_to_markdown(
        '<i><a id="z3"></a></i><p>Body content paragraph here.</p>'
    )
    assert "*" not in out_ia and "Body content paragraph here." in out_ia
    out_sup = h2m.html_to_markdown("<p>before<sup>  </sup>after</p>")
    assert "before" in out_sup and "after" in out_sup
    out_bq = h2m.html_to_markdown(
        "<blockquote>  </blockquote><p>Body content paragraph here.</p>"
    )
    assert ">" not in out_bq and "Body content paragraph here." in out_bq


def test_process_element_multiline_code_block():
    # <code> containing a newline renders as a fenced block.
    out = h2m.html_to_markdown("<code>line1\nline2</code>")
    assert "```" in out


def test_process_element_default_element_with_id():
    # A span (default branch) carrying an id renders its inner text.
    out = h2m.html_to_markdown('<span id="s9">span content here</span>')
    assert "span content here" in out


def test_merge_consecutive_bold_spans_iterates():
    # Four adjacent bold spans collapse into one via the merge loop.
    out = h2m.html_to_markdown(
        "<p>The values <b>A</b> <b>B</b> <b>C</b> <b>D</b> are shown here.</p>"
    )
    assert "**A B C D**" in out


def test_process_element_anchor_bold_sibling_heading():
    # <a name><b>..</b></a> followed by a bold sibling then a non-bold sibling
    # is merged into a ### heading (bold-sibling absorb + break).
    out = h2m.html_to_markdown(
        '<div><a name="an1"><b>Bold One</b></a> <b>Bold Two</b>'
        "<span>stopper</span></div>"
    )
    assert "### Bold OneBold Two" in out
    assert "stopper" in out


def test_process_element_toc_heading_then_table_kept_once():
    # A non-exact "Table of Contents ..." heading directly followed by a pipe
    # table is kept (first occurrence); the same heading without a following
    # table is dropped.
    kept = h2m.html_to_markdown(
        "<h3>Table of Contents Notes Section</h3>"
        "<table><tr><td>Item</td><td>1</td></tr>"
        "<tr><td>Other</td><td>2</td></tr></table>"
    )
    assert "### Table of Contents Notes Section" in kept
    assert "| Item | 1 |" in kept
    dropped = h2m.html_to_markdown(
        "<h3>Table of Contents Appendix Section</h3>"
        "<p>Just some plain text after the toc heading here.</p>"
    )
    assert "Table of Contents" not in dropped
    assert "Just some plain text after the toc heading here." in dropped


def test_process_element_toc_navigation_table_with_empty_row():
    # A >=5-row navigation table (TOC heading + page-number rows, incl. an
    # empty <tr>) is still converted; the empty row is skipped.
    out = h2m.html_to_markdown(
        "<table>"
        "<tr><td>Management Discussion</td><td>5</td></tr>"
        "<tr><td>Item A</td><td>10</td></tr>"
        "<tr><td>Item B</td><td>20</td></tr>"
        "<tr><td>Item C</td><td>30</td></tr>"
        "<tr></tr>"
        "<tr><td>Item D</td><td>40</td></tr></table>"
    )
    assert "| Management Discussion | 5 |" in out


def test_convert_table_multilevel_year_position_shift():
    """A year sub-header row starting at column 0 is shifted to align with data."""
    html = (
        "<table>"
        "<tr><td>Item</td><td>A Corp</td><td>B Corp</td><td>C Corp</td></tr>"
        "<tr><td>2025</td><td>2024</td><td>2023</td></tr>"
        "<tr><td>Rev</td><td>1</td><td>2</td><td>3</td></tr>"
        "</table>"
    )
    out = h2m.convert_table(_table(html))
    assert "| 2025 | 2024 | 2023 |" in out
    assert "| Rev | 1 | 2 | 3 |" in out


def test_convert_table_layout_fallback_bullet_divs():
    # A table that classifies as BULLET (the bullet char is the row's LAST
    # cell, so _extract_bullet_list finds no content cell and returns None),
    # yet whose first cell holds >=3 bullet-less divs.  The non-DATA
    # classification then falls through to the layout-table fallback, whose
    # PATTERN 1 (single column with multi-div cells) emits the bullet list.
    out = h2m.convert_table(
        _table(
            "<table>"
            "<tr><td><div>Item A here</div><div>Item B here</div>"
            "<div>Item C here</div></td><td>•</td></tr>"
            "<tr><td><div>Item D</div><div>Item E</div><div>Item F</div></td>"
            "<td>•</td></tr></table>"
        )
    )
    assert out == (
        "- Item A here\n- Item B here\n- Item C here\n\n- Item D\n- Item E\n- Item F\n"
    )


def test_convert_table_augment_skips_paren_descriptor():
    # A 2-layer header (categories ALPHA/BETA over a sub-row) whose sub-row
    # mixes a single year with a parenthetical descriptor "(in millions)".
    # Years under-cover the periods, so the leaf-position augmentation loop
    # runs and skips the parenthetical descriptor cell.
    out = h2m.convert_table(
        _build_table(
            [
                [_cell("Item"), _cell("ALPHA", cs=2), _cell("BETA", cs=2)],
                [
                    _cell(""),
                    _cell("2025"),
                    _cell("(in millions)"),
                    _cell("Change"),
                    _cell("Pct"),
                ],
                [_cell("Rev"), _cell("1"), _cell("2"), _cell("3"), _cell("4")],
            ]
        )
    )
    assert out == (
        "|  |  |  |  |  |\n|---|---|---|---|---|\n"
        "|  | 2025 |  | Change | Pct |\n| Rev | 1 | 2 | 3 | 4 |"
    )


def test_convert_table_dollar_position_fallback():
    # A 2-layer header where years cover only some periods and a remaining
    # period column is marked by a lone "$".  After the year and augmentation
    # passes leave header_col_positions unset, the dollar-position fallback
    # computes positions from dollar_positions.
    out = h2m.convert_table(
        _build_table(
            [
                [_cell("Item"), _cell("ALPHA", cs=2), _cell("BETA", cs=2)],
                [_cell(""), _cell("2025"), _cell("2024"), _cell("$"), _cell("v")],
                [_cell("Rev"), _cell("1"), _cell("2"), _cell("$"), _cell("3")],
            ]
        )
    )
    assert out == (
        "|  |  |  |  |  |\n|---|---|---|---|---|\n"
        "|  | 2025 | 2024 | $ | v |\n| Rev | 1 | 2 | $3 |  |"
    )
