{%- set views_class = cookiecutter.router_name.replace('_', ' ').title().replace(' ', '') -%}
"""Tests for the {{ cookiecutter.router_name }} charting views."""

from datetime import date
from types import SimpleNamespace

import pytest

pytest.importorskip("openbb_charting")

from {{ cookiecutter.package_name }}.routers.{{ cookiecutter.router_name }}_views import (
    {{ views_class }}Views,
)


class TestCandlesView:
    """The candles view charts the daily highs."""

    def test_figure(self):
        rows = [
            SimpleNamespace(date=date(2023, 8, 23), high=5.0),
            SimpleNamespace(date=date(2023, 8, 24), high=7.0),
        ]
        fig, content = {{ views_class }}Views.{{ cookiecutter.router_name }}_candles(obbject_item=rows)
        assert list(fig.data[0].y) == [5.0, 7.0]
        assert content["data"][0]["type"] == "bar"
