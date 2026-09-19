"""Unit tests for ``openbb_sec.utils.xml_render``."""

from lxml import etree

from openbb_sec.utils import xml_render
from openbb_sec.utils.xml_render import (
    _humanize,
    _is_leaf,
    _is_record,
    _kv_table,
    _local,
    _records_table,
    _text,
    is_asset_data_root,
    render_xml_as_html,
)


def _elem(xml: str):
    """Parse an XML fragment into a single element."""
    return etree.fromstring(xml.encode("utf-8"))


def _render(xml: str, **kwargs):
    """Render an XML string fragment as HTML."""
    return render_xml_as_html(xml.encode("utf-8"), **kwargs)


class TestLocalAndHumanize:
    """The local-name and label-humanizing helpers."""

    def test_local_strips_namespace(self):
        assert _local("{http://ns}AssetData") == "AssetData"
        assert _local("plain") == "plain"

    def test_local_non_string_is_none(self):
        assert _local(123) is None
        assert _local(etree.Comment) is None

    def test_humanize_camel_and_snake(self):
        assert _humanize("assetNumber") == "Asset Number"
        assert _humanize("reporting_period") == "Reporting period"
        assert _humanize("") == ""


class TestStructurePredicates:
    """Leaf / record / asset-data-root predicates."""

    def test_is_leaf_and_record(self):
        record = _elem("<asset><num>1</num><bal>2</bal></asset>")
        assert _is_record(record) is True
        assert _is_leaf(record) is False
        leaf = record[0]
        assert _is_leaf(leaf) is True
        assert _is_record(leaf) is False

    def test_record_requires_all_children_leaves(self):
        nested = _elem("<a><b><c>1</c></b></a>")
        assert _is_record(nested) is False

    def test_is_asset_data_root(self):
        assert is_asset_data_root("assetData") is True
        assert is_asset_data_root("{http://www.sec.gov/edgar/absee}foo") is True
        assert is_asset_data_root("xbrl") is False
        assert is_asset_data_root(123) is False

    def test_text_trims_and_handles_empty(self):
        assert _text(_elem("<x>  hi  </x>")) == "hi"
        assert _text(_elem("<x/>")) == ""


class TestTableHelpers:
    """Direct rendering of record and key/value tables."""

    def test_records_table_empty_members(self):
        assert _records_table([]) == ""

    def test_records_table_fills_missing_columns(self):
        members = [
            _elem("<asset><a>1</a><b>2</b></asset>"),
            _elem("<asset><a>3</a><c>4</c></asset>"),
        ]
        html = _records_table(members)
        assert "<th>A</th>" in html
        assert "<th>B</th>" in html
        assert "<th>C</th>" in html
        # The first record has no ``c`` and the second no ``b`` -> blank cells.
        assert html.count("<td></td>") == 2

    def test_kv_table(self):
        html = _kv_table([("assetNumber", "1"), ("balance", "2")])
        assert "<th>Asset Number</th>" in html
        assert "<td>1</td>" in html


class TestRenderAssetData:
    """Rendering ABS-EE asset-data documents as record tables."""

    def test_renders_records_as_table(self):
        html = _render(
            "<assetData>"
            "<asset><assetNumber>1</assetNumber><balance>100</balance></asset>"
            "<asset><assetNumber>2</assetNumber><balance>200</balance></asset>"
            "</assetData>"
        )
        assert html is not None
        assert "<h1>Asset Data</h1>" in html
        assert "ob-tbl" in html
        assert "Asset Number" in html
        assert "<td>100</td>" in html

    def test_simple_table_for_repeated_leaves(self):
        html = _render("<assetData><note>a</note><note>b</note></assetData>")
        assert "<h2>Note</h2>" in html
        assert "<td>a</td>" in html
        assert "<td>b</td>" in html

    def test_single_leaf_renders_key_value(self):
        html = _render("<assetData><assetType>auto</assetType></assetData>")
        assert "ob-kv" in html
        assert "<td>auto</td>" in html

    def test_nested_elements_recurse(self):
        html = _render(
            "<assetData><wrapper><inner><leaf>v</leaf></inner></wrapper></assetData>"
        )
        assert "<h2>Wrapper</h2>" in html
        assert "<h2>Inner</h2>" in html
        assert "<td>v</td>" in html

    def test_leaf_tail_text_renders_as_mapped_text_item(self):
        html = _render(
            "<assetData><assets>"
            "<newEx103tag1>assetTypeNumber</newEx103tag1>"
            "<![CDATA[Asset Number Type - HCA indicates Hyundai Capital America.]]>"
            "</assets></assetData>"
        )
        assert "ob-kv" in html
        assert "<th>Asset Type Number</th>" in html
        assert "Asset Number Type - HCA indicates Hyundai Capital America." in html

    def test_leaf_tail_only_uses_element_name_as_key(self):
        html = _render(
            "<assetData><assets>"
            "<newEx103tag1/>"
            "<![CDATA[Asset Number Type - HCA indicates Hyundai Capital America.]]>"
            "</assets></assetData>"
        )
        assert "ob-kv" in html
        assert "<th>New Ex103tag1</th>" in html
        assert "Asset Number Type - HCA indicates Hyundai Capital America." in html

    def test_mixed_group_recurses_each_member(self):
        html = _render("<assetData><m><a>1</a></m><m>plain</m></assetData>")
        assert html.count("<h2>M</h2>") == 2

    def test_truncates_records_over_max_rows(self, monkeypatch):
        monkeypatch.setattr(xml_render, "MAX_ROWS", 1)
        html = _render(
            "<assetData><asset><n>1</n></asset><asset><n>2</n></asset></assetData>"
        )
        assert "Showing the first 1 of 2 records." in html


class TestRenderComments:
    """Rendering document-level comment legends."""

    def test_comments_legend_open_when_no_table(self):
        html = _render(
            "<comments><!--First note--><!--Second note--><item>value</item></comments>"
        )
        assert "Document notes (2)" in html
        assert "ob-note open" in html
        assert "First note" in html
        assert "Second note" in html

    def test_comments_legend_collapsed_when_table_present(self):
        html = _render(
            "<assetData><!--Legend note-->"
            "<asset><x>1</x></asset><asset><x>2</x></asset></assetData>"
        )
        assert "Document notes (1)" in html
        assert "ob-note open" not in html

    def test_nested_comment_is_rendered(self):
        html = _render(
            "<assetData><assets><!--inline note--><item>value</item></assets></assetData>"
        )
        assert "inline note" in html


class TestRenderPreviewAndGuards:
    """Truncation previews and the not-renderable guard paths."""

    def test_truncated_with_source_url_links_full_document(self):
        html = _render(
            "<assetData><asset><x>1</x></asset><asset><x>2</x></asset></assetData>",
            source_url="https://www.sec.gov/a.xml",
            truncated=True,
        )
        assert "open the full document" in html
        assert "https://www.sec.gov/a.xml" in html

    def test_truncated_without_source_url(self):
        html = _render(
            "<assetData><asset><x>1</x></asset><asset><x>2</x></asset></assetData>",
            truncated=True,
        )
        assert "Showing a preview of a large file." in html
        assert "<a href" not in html

    def test_unparseable_bytes_return_none(self):
        assert render_xml_as_html(b"") is None
        assert render_xml_as_html(b"\xff\xfe not xml") is None

    def test_non_asset_or_comments_root_returns_none(self):
        assert _render("<foo><bar>1</bar></foo>") is None

    def test_empty_document_returns_none(self):
        assert _render("<comments></comments>") is None
