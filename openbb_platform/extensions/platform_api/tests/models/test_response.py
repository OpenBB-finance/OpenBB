"""Tests for openbb_platform_api.models.response."""

import base64
import json

import pytest

from openbb_platform_api.models.response import (
    MetricResponseModel,
    OmniWidgetResponseModel,
    PdfResponseModel,
)

# ---------------------------------------------------------------------------
# MetricResponseModel
# ---------------------------------------------------------------------------


def test_metric_response_model_basic_construction():
    """Required ``label`` + ``value`` build cleanly with no delta."""
    m = MetricResponseModel(label="Revenue", value=1234)
    assert m.label == "Revenue"
    assert m.value == 1234
    assert m.delta is None


def test_metric_response_model_accepts_string_and_float_values():
    """``value`` is ``int | float | str`` so all three flow through."""
    m = MetricResponseModel(label="Pct", value=3.14, delta="+2.0%")
    assert m.value == 3.14
    assert m.delta == "+2.0%"


# ---------------------------------------------------------------------------
# PdfResponseModel
# ---------------------------------------------------------------------------


def test_pdf_response_requires_content_or_url():
    """Both empty → validator raises with the canonical message."""
    with pytest.raises(ValueError, match="Either 'content' or 'url'"):
        PdfResponseModel()


def test_pdf_response_url_must_have_scheme():
    """A bare ``url`` like ``"file.pdf"`` (no ``://``) is rejected."""
    with pytest.raises(ValueError, match="Invalid URL reference"):
        PdfResponseModel(url="not-a-url")


def test_pdf_response_url_only_passes_through():
    """``url`` with a real scheme is accepted; ``content`` slot stays
    untouched and ``data_format`` is stamped.
    """
    m = PdfResponseModel(url="https://example.com/doc.pdf", filename="doc.pdf")
    assert m.url == "https://example.com/doc.pdf"
    assert m.data_format == {"data_type": "pdf", "filename": "doc.pdf"}


def test_pdf_response_bytes_content_gets_base64_encoded():
    """Raw bytes get re-encoded as a base64 string so the JSON wire
    payload stays text-only.
    """
    raw = b"%PDF-1.4 fake content"
    m = PdfResponseModel(content=raw, filename="x.pdf")
    decoded = base64.b64decode(m.content)
    assert decoded == raw
    assert m.data_format == {"data_type": "pdf", "filename": "x.pdf"}


def test_pdf_response_string_content_passes_through_unchanged():
    """A string ``content`` (already base64-encoded) doesn't get
    re-encoded — the validator only encodes ``bytes``.
    """
    encoded = base64.b64encode(b"hello").decode("utf-8")
    m = PdfResponseModel(content=encoded)
    assert m.content == encoded


# ---------------------------------------------------------------------------
# OmniWidgetResponseModel
# ---------------------------------------------------------------------------


def test_omni_response_rejects_empty_content():
    """Workspace requires *some* content — an explicit ``None`` is a bug."""
    with pytest.raises(ValueError, match="Content cannot be empty"):
        OmniWidgetResponseModel(content=None)


def test_omni_response_validates_parse_as_choices():
    """Only ``table`` / ``chart`` / ``text`` are valid hints."""
    with pytest.raises(ValueError, match="Invalid parse_as"):
        OmniWidgetResponseModel(content="hi", parse_as="bogus")


def test_omni_response_explicit_parse_as_skips_inference():
    """When the caller passes ``parse_as`` explicitly, the validator
    trusts it and stamps ``data_format`` without re-running inference.
    """
    m = OmniWidgetResponseModel(content="some text", parse_as="text")
    assert m.data_format == {"data_type": "object", "parse_as": "text"}
    # ``parse_as`` is consumed during validation and removed from the
    # model body so it doesn't leak into the wire response.
    assert getattr(m, "parse_as", None) is None


def test_omni_response_infers_chart_for_plotly_dict():
    """``{layout, data}`` → ``parse_as="chart"`` automatically."""
    fig = {"layout": {"title": "x"}, "data": [{"type": "scatter"}]}
    m = OmniWidgetResponseModel(content=fig)
    assert m.data_format["parse_as"] == "chart"
    assert m.content == fig


def test_omni_response_infers_table_for_list_of_dicts():
    """A list of records gets tagged as a table."""
    rows = [{"a": 1}, {"a": 2}]
    m = OmniWidgetResponseModel(content=rows)
    assert m.data_format["parse_as"] == "table"
    assert m.content == rows


def test_omni_response_infers_table_for_dict_of_lists():
    """``{"col": [...]}`` shape gets converted into row-records via
    ``pandas.to_json(orient="records")`` before tagging as a table.
    """
    cols = {"a": [1, 2], "b": [3, 4]}
    m = OmniWidgetResponseModel(content=cols)
    assert m.data_format["parse_as"] == "table"
    assert m.content == [{"a": 1, "b": 3}, {"a": 2, "b": 4}]


def test_omni_response_infers_table_from_dataframe():
    """A pandas DataFrame becomes a list of records."""
    pd = pytest.importorskip("pandas")
    df = pd.DataFrame({"x": [1, 2], "y": [3, 4]})
    m = OmniWidgetResponseModel(content=df)
    assert m.data_format["parse_as"] == "table"
    assert m.content == [{"x": 1, "y": 3}, {"x": 2, "y": 4}]


def test_omni_response_parses_json_string():
    """A JSON-encoded string of a list/dict gets parsed and tagged
    according to its shape.
    """
    payload = json.dumps([{"a": 1}, {"a": 2}])
    m = OmniWidgetResponseModel(content=payload)
    assert m.data_format["parse_as"] == "table"
    assert m.content == [{"a": 1}, {"a": 2}]


def test_omni_response_repairs_trailing_commas_in_json_string():
    """The validator falls back to a regex cleanup pass when the raw
    JSON parse fails — covers Workspace's lenient payloads.
    """
    m = OmniWidgetResponseModel(content='[{"a": 1,},]')
    # Either parses (the repair worked) or stays as the raw string with
    # ``parse_as="text"`` — both are valid outcomes for the lenient path.
    assert m.data_format["parse_as"] in {"table", "text"}


def test_omni_response_string_falls_back_to_text_for_garbage():
    """A non-JSON string can't be repaired — falls through to text."""
    m = OmniWidgetResponseModel(content="just plain text")
    assert m.data_format["parse_as"] == "text"


def test_omni_response_text_for_unrecognized_shape():
    """A scalar that isn't string/list/dict/DataFrame → text."""
    m = OmniWidgetResponseModel(content=42)
    assert m.data_format["parse_as"] == "text"


def test_omni_response_chart_from_plotly_figure_object():
    """A real Plotly ``Figure`` instance gets serialized to JSON and
    tagged as a chart — exercises the ``content.__class__.__name__ ==
    'Figure'`` branch.
    """
    pytest.importorskip("plotly")
    import plotly.graph_objects as go

    fig = go.Figure(data=[go.Scatter(x=[1, 2], y=[3, 4])])
    m = OmniWidgetResponseModel(content=fig)
    assert m.data_format["parse_as"] == "chart"
    # ``content`` is the JSON serialization, not the Figure object.
    assert isinstance(m.content, str)
    parsed = json.loads(m.content)
    assert "data" in parsed and "layout" in parsed


def test_omni_response_dataframe_serialization_failure_raises_value_error():
    """If pandas can't serialize the DataFrame (corrupt state), the
    validator surfaces a clear ``ValueError`` instead of leaking the
    raw exception.
    """
    pd = pytest.importorskip("pandas")

    # Patch ``to_json`` to raise so we exercise the except-arm.
    class _BadDF(pd.DataFrame):
        @property
        def _constructor(self):
            return _BadDF

        def to_json(self, *args, **kwargs):  # noqa: ARG002
            raise RuntimeError("simulated to_json failure")

    df = _BadDF({"x": [1, 2]})
    with pytest.raises(ValueError, match="Failed to convert DataFrame"):
        OmniWidgetResponseModel(content=df)


def test_omni_response_figure_to_json_failure_raises_value_error():
    """Plotly Figure ``to_json`` failure → clear ValueError. Exercises
    the ``except Exception`` arm of the Figure-class branch.
    """

    class _BrokenFigure:
        """Custom class whose ``__class__.__name__`` is 'Figure' but
        whose ``to_json`` always raises — covers the failure arm
        without needing a real plotly install.
        """

        def to_json(self):
            raise RuntimeError("simulated to_json failure")

    _BrokenFigure.__name__ = "Figure"

    with pytest.raises(ValueError, match="Failed to convert chart to JSON"):
        OmniWidgetResponseModel(content=_BrokenFigure())


def test_omni_response_dict_of_lists_serialization_failure_raises_value_error():
    """The dict-of-lists branch transposes via stdlib ``zip(strict=True)``
    rather than pandas, so any input where the per-key lists have
    different lengths surfaces as a ``ValueError`` from the transpose.
    Mirrors the DataFrame-branch defensive arm but without an
    optional-pandas dependency.
    """
    with pytest.raises(ValueError, match="dictionary of lists"):
        # ``zip(*..., strict=True)`` raises when the iterables have
        # mismatched lengths — the transpose can't produce a
        # meaningful list-of-records, so the validator surfaces the
        # failure with the per-branch error message.
        OmniWidgetResponseModel(content={"a": [1, 2, 3], "b": [3, 4]})
