"""Unit tests for ``openbb_sec.utils.filing_sections``."""

from bs4 import BeautifulSoup

from openbb_sec.utils.filing_sections import (
    _fixed_width_table_to_markdown,
    _is_bold_paragraph,
    extract_item_sections,
    extract_section_html,
    extract_via_cross_reference,
    reflow_plain_text,
    split_bold_sections,
    strip_markdown_footers,
)

_TABLE_BLOCK = [
    "                          Opening                   Closing",
    "Account                   Balance     Charges       Balance",
    "Cash on hand                $ 11        $ 2           $ 9",
    "Provisions relating to",
    "  pending matters (a|b)        4           1             3",
    "2019 carryover credits         20          3            17",
    "Total                       $ 15        $ 3          $ 12",
]


def test_fixed_width_table_to_markdown_parses():
    md = _fixed_width_table_to_markdown(_TABLE_BLOCK)
    lines = md.split("\n")
    # Multi-line headers merge per column; the label header is first.
    assert lines[0] == "| Account | Opening Balance | Charges | Closing Balance |"
    assert lines[1] == "|---|---|---|---|"
    assert lines[2] == "| Cash on hand | $ 11 | $ 2 | $ 9 |"
    # A wrapped row label folds into the row carrying its values; pipes escape.
    assert r"| Provisions relating to pending matters (a\|b) | 4 | 1 | 3 |" in lines
    # A label-leading year is kept in the label, not read as a value.
    assert "| 2019 carryover credits | 20 | 3 | 17 |" in lines
    assert lines[-1] == "| Total | $ 15 | $ 3 | $ 12 |"


def test_fixed_width_table_to_markdown_none_cases():
    assert _fixed_width_table_to_markdown(["only one line"]) is None
    # No numeric value tokens at all.
    assert _fixed_width_table_to_markdown(["alpha beta gamma", "delta epsilon"]) is None
    # Two rows cannot form a column cluster (needs three aligned tokens).
    assert _fixed_width_table_to_markdown(["x  1  2  3", "y  4  5  6"]) is None
    # Columns form, but every row keeps words past the label boundary.
    no_tail = [
        "Item one    5    Item two    6    Item three    7",
        "Item aaa    1    Item bbb    2    Item cccc     3",
        "Item xxx    8    Item yyy    9    Item zzzz     4",
    ]
    assert _fixed_width_table_to_markdown(no_tail) is None


def test_reflow_plain_text_converts_embedded_table():
    text = (
        "    The Company reports the following restructuring balances during the\n"
        "year then ended, as detailed in the schedule presented below here:\n"
        "\n" + "\n".join(_TABLE_BLOCK) + "\n"
        "\n"
        "These amounts are unaudited and subject to revision in future periods.\n"
    )
    out = reflow_plain_text(text)
    assert "schedule presented below here:" in out
    assert "| Account | Opening Balance | Charges | Closing Balance |" in out
    assert out.rstrip().endswith("subject to revision in future periods.")


def test_reflow_plain_text_table_fallback_to_prose():
    unparseable = [
        "Item one    5    Item two    6    Item three    7",
        "Item aaa    1    Item bbb    2    Item cccc     3",
        "Item xxx    8    Item yyy    9    Item zzzz     4",
    ]
    text = "\n".join(unparseable) + "\n"
    out = reflow_plain_text(text)
    assert "| " not in out
    assert "Item one 5 Item two 6 Item three 7 Item aaa" in out


def test_reflow_plain_text_rejoins_page_split_sentence():
    text = (
        "    The Company operates in one principal industry segment and the\n"
        "balances are presented across the periods shown below should be\n"
        "\n"
        "read in conjunction with the consolidated financial statements here.\n"
    )
    out = reflow_plain_text(text)
    assert "should be read in conjunction with" in out
    assert "\n\n" not in out


def test_reflow_plain_text_justified_prose_is_not_a_table():
    # Two wide gaps but no digits — heavily justified prose, not a table.
    text = (
        "    These results should be read in conjunction with the audited and\n"
        "consolidated   statements   together  with  the  accompanying  notes.\n"
    )
    out = reflow_plain_text(text)
    assert "| " not in out
    assert "read in conjunction with" in out


def test_reflow_plain_text_preserves_markdown_table():
    text = (
        "    Some intro prose that needs reflow because it is indented here.\n"
        "\n"
        "| Account | 1999 |\n"
        "|---|---|\n"
        "| Cash | $ 11 |\n"
        "\n"
        "    Trailing prose after the table that also exercises the reflow path.\n"
    )
    out = reflow_plain_text(text)
    assert "| Account | 1999 |\n|---|---|\n| Cash | $ 11 |" in out
    assert out.rstrip().endswith("exercises the reflow path.")


def test_reflow_plain_text_single_heading_is_content():
    # A document that is a single heading-like line is content, not a heading.
    assert reflow_plain_text("GENERAL OVERVIEW", force=True) == "GENERAL OVERVIEW"


def test_reflow_plain_text_passthrough_when_not_fixed_width():
    text = "A normal markdown paragraph with no leading indentation at all."
    assert reflow_plain_text(text) == text
    assert reflow_plain_text("") == ""


def test_reflow_plain_text_reflows_fixed_width():
    text = (
        "GENERAL\n"
        " \n"
        "    Apple Computer, Inc. was incorporated under the laws of the State\n"
        "of California on January 3, 1977 and its offices are in Cupertino\n"
        "<PAGE>\n"
        "3\n"
        "and it continued to operate there throughout the period presented.\n"
        " \n"
        "    The Company designs and markets personal computers for sale to\n"
        "education, creative, consumer, business and government customers.\n"
    )
    out = reflow_plain_text(text)
    assert out.startswith("**GENERAL**\n\n")
    assert "    Apple" not in out
    assert "<PAGE>" not in out
    # Wrapped lines and the cross-page break rejoin into one paragraph.
    assert (
        "in Cupertino and it continued to operate there throughout the period"
    ) in out
    assert "designs and markets personal computers" in out


def test_strip_markdown_footers_empty():
    assert strip_markdown_footers("") == ""


def test_strip_markdown_footers_removes_all_footer_forms():
    text = (
        "Apple Inc. | 2025 Form 10-K | 3 The business continues to grow.\n"
        "42\n"
        "Filed on Form 10-K in 2024.\n"
        "Keep this real line."
    )
    out = strip_markdown_footers(text)
    assert "Form 10-K" not in out
    assert "\n42\n" not in f"\n{out}\n"
    assert "Keep this real line." in out


def test_extract_item_sections_empty_and_no_headers():
    assert extract_item_sections("") == {}
    assert extract_item_sections("Prose with no item headers at all.") == {}


def test_extract_item_sections_parts_titles_and_name_fallback():
    markdown = (
        "Part I\n"
        "## Item 1\n"
        "Business\n"
        "The company does things.\n\n"
        "## Item 1A. Risk Factors\n"
        "Risks abound.\n\n"
        "Part II\n"
        "## Item 1. Legal Proceedings\n"
        "Lawsuits."
    )
    items = extract_item_sections(markdown)
    assert items["item_1A"]["name"] == "Risk Factors"
    assert items["item_1"]["name"] == "Business"
    assert items["item_II_1"]["part"] == "II"


def test_extract_section_html_titled_only():
    html = (
        "<p>Item 1A. Risk Factors</p>"
        "<div>Body of the risk factors section.</div>"
        "<p>Item 1B. Unresolved Staff Comments</p>"
    )
    section = extract_section_html(html, "1A")
    assert "Body of the risk factors section." in section
    assert "Item 1B" not in section


def test_extract_section_html_untitled_only():
    html = "<p>Item 1A.</p><div>some body content</div><p>Item 1B.</p>"
    section = extract_section_html(html, "1A")
    assert "some body content" in section


def test_extract_section_html_skips_long_and_crossref_elements():
    html = (
        "<div>This is a long paragraph that clearly exceeds the eighty character"
        " length limit used to skip body text.</div>"
        "<p>Item 1A as described in the section below for more detail</p>"
        "<p>Item 1A. Risk Factors</p>"
        "<div>Real body.</div>"
        "<p>Item 2. Properties</p>"
    )
    section = extract_section_html(html, "1A")
    assert "Real body." in section


def test_extract_section_html_no_match():
    assert extract_section_html("<p>nothing relevant</p>", "1A") == ""


def test_extract_section_html_dedupes_nested_headers():
    html = "<td><p>Item 1A.</p></td><div>section body</div><p>Item 1B.</p>"
    section = extract_section_html(html, "1A")
    assert "section body" in section


def test_is_bold_paragraph_empty_and_span_weight():
    empty = BeautifulSoup("<div></div>", "html.parser").div
    assert _is_bold_paragraph(empty) is False

    span_bold = BeautifulSoup(
        '<div><span style="font-weight:700">Bold Heading</span></div>',
        "html.parser",
    ).div
    assert _is_bold_paragraph(span_bold) is True


def test_split_bold_sections_splits_and_skips_containers():
    html = (
        "<p>Item 1A. Risk Factors</p>"
        "<div><b>The first risk heading.</b></div>"
        "<p>Body of the first risk.</p>"
        "<div><p>nested wrapper skipped</p></div>"
        "<div><b>The second risk heading.</b></div>"
        "<p>Body of the second risk.</p>"
    )
    blocks = split_bold_sections(html, "risk_factor")
    headings = [b["risk_factor"] for b in blocks]
    assert "The first risk heading." in headings
    assert "The second risk heading." in headings


_CROSS_REFERENCE_MARKDOWN = (
    '<a id="bus"></a>About our business operations and strategy.\n\n'
    '<a id="risk"></a>Risk discussion of various market risks.\n\n'
    '<a id="mkt"></a>Market for the common equity.\n\n'
    "| Item | Description | Reference |\n"
    "| Part I |\n"
    "| Item 1 | Business | [1](#bus) |\n"
    "| Item 1A | Risk Factors | [2](#risk) |\n"
    "| Item 2 | Properties | none |\n"
    "| Item 3 | Legal | [3](#missing) |\n"
    "| Part II |\n"
    "| Item 5 | Market | [4](#mkt) |\n"
)


def test_extract_via_cross_reference_walks_anchor_table():
    items = extract_via_cross_reference(_CROSS_REFERENCE_MARKDOWN)
    # Rows whose anchor is missing (#missing) or absent (none) are dropped.
    assert set(items) == {"item_1", "item_1A", "item_II_5"}
    assert items["item_1"]["name"] == "Business"
    assert items["item_1"]["part"] == "I"
    assert "About our business" in items["item_1"]["text"]
    # Anchor tags are stripped from the sliced section content.
    assert "<a id=" not in items["item_1"]["text"]
    assert items["item_II_5"]["part"] == "II"
    assert items["item_II_5"]["item_num"] == "5"


def test_extract_via_cross_reference_empty_markdown():
    assert extract_via_cross_reference("") == {}


def test_extract_via_cross_reference_requires_anchors():
    # An anchor table with no in-document ``<a id>`` targets yields nothing.
    assert extract_via_cross_reference("| Item 1 | Business | [1](#bus) |\n") == {}


def test_extract_via_cross_reference_no_resolvable_rows():
    markdown = (
        '<a id="bus"></a>Business content.\n\n| Item 1 | Business | [1](#nope) |\n'
    )
    assert extract_via_cross_reference(markdown) == {}
