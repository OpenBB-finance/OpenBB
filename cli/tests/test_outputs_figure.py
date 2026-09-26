"""Tests for Plotly figure JSON display."""

import builtins
import json
from unittest.mock import MagicMock, patch

import pytest

from openbb_cli.outputs import figure as figure_module
from openbb_cli.outputs.figure import (
    is_plotly_figure,
    render_figure_html,
    show_figure,
    strip_theme_colors,
)

FIGURE = {
    "data": [{"type": "scatter", "x": [1, 2], "y": [3, 4], "name": "</script>"}],
    "layout": {"title": {"text": "Term Structure"}, "font": {"color": "white"}},
    "config": {"displaylogo": False},
}


@pytest.fixture()
def mock_session():
    with patch("openbb_cli.outputs.figure.session") as ms:
        ms.console.print = MagicMock()
        yield ms


class TestIsPlotlyFigure:
    """Recognizing Plotly figure JSON."""

    def test_figure_dict(self):
        assert is_plotly_figure(FIGURE)

    @pytest.mark.parametrize(
        "data",
        [
            {"data": [1], "rows": 2},
            {"data": {"x": 1}, "layout": {}},
            {"data": [], "layout": "wide"},
            [FIGURE],
            None,
        ],
    )
    def test_other_values(self, data):
        assert not is_plotly_figure(data)


class TestRenderFigureHtml:
    """Rendering figure JSON as a standalone page."""

    def test_embeds_escaped_title_and_figure(self):
        page = render_figure_html(FIGURE, "/cboe/<options>")
        assert "<title>/cboe/&lt;options&gt;</title>" in page
        assert "<\\/script>" in page
        assert "__FIGURE__" not in page and "__TITLE__" not in page
        start = page.index("const figure = ") + len("const figure = ")
        end = page.index(";\n", start)
        assert json.loads(page[start:end].replace("<\\/", "</")) == FIGURE

    def test_inlines_local_plotly(self):
        from plotly.offline import get_plotlyjs

        assert get_plotlyjs()[:200] in render_figure_html(FIGURE, "t")
        assert figure_module.PLOTLYJS_CDN not in render_figure_html(FIGURE, "t")

    def test_uses_cdn_without_plotly(self, monkeypatch):
        real_import = builtins.__import__

        def blocked_import(name, *args, **kwargs):
            if name == "plotly.offline":
                raise ImportError(name)
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", blocked_import)
        page = render_figure_html(FIGURE, "t")
        assert f'<script src="{figure_module.PLOTLYJS_CDN}"></script>' in page

    def test_title_token_in_title_is_not_substituted(self):
        page = render_figure_html(FIGURE, "__FIGURE__")
        assert "<title>__FIGURE__</title>" in page


class TestShowFigure:
    """Showing figure JSON in the chart window or the browser."""

    def test_sends_to_backend(self, mock_session):
        show_figure(FIGURE, "/cboe/options/term_structure")
        mock_session.backend.send_figure.assert_called_once()
        fig = mock_session.backend.send_figure.call_args[0][0]
        assert fig.layout.title.text == "Term Structure"
        assert len(fig.data) == 1
        assert (
            mock_session.backend.send_figure.call_args[1]["command_location"]
            == "/cboe/options/term_structure"
        )

    def test_backend_figure_drops_server_theme_colors(self, mock_session):
        themed = {
            "data": [{"type": "scatter", "y": [1, 2], "line": {"color": "red"}}],
            "layout": {
                "template": {"layout": {"font": {"color": "#2a3f5f"}}},
                "font": {"color": "white", "size": 12},
                "paper_bgcolor": "rgba(0,0,0,0)",
                "xaxis": {"linecolor": "white", "title": {"text": "Date"}},
            },
        }
        show_figure(themed, "t")
        fig = mock_session.backend.send_figure.call_args[0][0]
        assert fig.layout.font.color is None
        assert fig.layout.font.size == 12
        assert fig.layout.paper_bgcolor is None
        assert fig.layout.xaxis.linecolor is None
        assert fig.layout.xaxis.title.text == "Date"
        assert fig.data[0].line.color == "red"

    def test_backend_failure_opens_browser(self, mock_session):
        mock_session.backend.send_figure.side_effect = RuntimeError("no window")
        with patch("openbb_cli.outputs.figure.webbrowser.open") as open_browser:
            show_figure(FIGURE, "t")
        open_browser.assert_called_once()
        msgs = [str(c) for c in mock_session.console.print.call_args_list]
        assert any("no window" in m for m in msgs)

    def test_without_backend_opens_browser(self, mock_session, tmp_path):
        mock_session.backend = None
        with (
            patch("openbb_cli.outputs.figure.webbrowser.open") as open_browser,
            patch(
                "openbb_cli.outputs.figure.tempfile.NamedTemporaryFile",
                lambda **kwargs: open(tmp_path / "chart.html", "w", encoding="utf-8"),
            ),
        ):
            show_figure(FIGURE, "t")
        open_browser.assert_called_once_with((tmp_path / "chart.html").as_uri())
        assert "Plotly.newPlot" in (tmp_path / "chart.html").read_text(encoding="utf-8")


class TestStripThemeColors:
    """Removing server-side theme styling from a layout."""

    def test_removes_template_and_color_keys_recursively(self):
        layout = {
            "template": {"layout": {}},
            "paper_bgcolor": "black",
            "colorway": ["#111", "#222"],
            "annotations": [{"text": "a", "font": {"color": "white", "size": 9}}],
            "legend": {"bgcolor": "black", "orientation": "h"},
        }
        assert strip_theme_colors(layout) == {
            "colorway": ["#111", "#222"],
            "annotations": [{"text": "a", "font": {"size": 9}}],
            "legend": {"orientation": "h"},
        }

    def test_leaves_the_input_unchanged(self):
        layout = {"font": {"color": "white"}}
        strip_theme_colors(layout)
        assert layout == {"font": {"color": "white"}}
