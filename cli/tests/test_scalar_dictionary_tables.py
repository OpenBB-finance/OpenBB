"""Dictionary records should be valid tabular adapter input."""

from pathlib import Path
from unittest.mock import patch
from urllib.parse import unquote, urlparse

import pytest

from openbb_cli.outputs.html import HtmlOutput
from openbb_cli.outputs.tsv import TsvOutput


def test_scalar_record_tsv(capsys):
    TsvOutput().display({"symbol": "AAPL", "price": 42})
    assert capsys.readouterr().out == "symbol\tprice\nAAPL\t42\n"


def test_scalar_record_html_writes_native_table():
    with patch("openbb_cli.outputs.html.webbrowser.open") as browser:
        HtmlOutput().display({"symbol": "AAPL", "price": 42})
    path = Path(unquote(urlparse(browser.call_args.args[0]).path))
    try:
        html = path.read_text()
        assert "<td>AAPL</td>" in html
        assert "<td>42</td>" in html
    finally:
        path.unlink()


def test_column_oriented_control(capsys):
    TsvOutput().display({"symbol": ["A", "B"], "price": [1, 2]})
    assert capsys.readouterr().out == "symbol\tprice\nA\t1\nB\t2\n"


@pytest.mark.parametrize("adapter", [TsvOutput(), HtmlOutput()])
def test_unequal_columns_are_not_silently_reinterpreted(adapter):
    with pytest.raises(ValueError, match="same length"):
        adapter.display({"symbol": ["A"], "price": [1, 2]})
