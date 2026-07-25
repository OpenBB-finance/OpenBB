"""Unit tests for ``openbb_sec.utils.as_filed_widget``."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pandas as pd

from openbb_sec.utils.as_filed_widget import get_as_filed_widget_rows


def _run(data, url="https://sec.gov/f.htm"):
    fs = SimpleNamespace(get_statement=lambda _: (data, None))
    with (
        patch(
            "openbb_sec.models.sec_financials.resolve_section_url",
            AsyncMock(return_value=url),
        ),
        patch(
            "openbb_sec.models.sec_financials.FinancialStatements.from_url",
            return_value=fs,
        ),
    ):
        return asyncio.run(get_as_filed_widget_rows("ORCL", "balance"))


def test_pivots_periods_newest_first():
    df = pd.DataFrame(
        [
            {
                "order": 1,
                "label": "Cash",
                "unit": "USD",
                "period_ending": "2025-05-31",
                "value": 10,
            },
            {
                "order": 1,
                "label": "Cash",
                "unit": "USD",
                "period_ending": "2024-05-31",
                "value": 9,
            },
            {
                "order": 2,
                "label": "AR",
                "unit": "USD",
                "period_ending": "2025-05-31",
                "value": 8,
            },
            {
                "order": 2,
                "label": "AR",
                "unit": "USD",
                "period_ending": "2024-05-31",
                "value": 7,
            },
        ]
    )
    rows = _run(df)
    assert list(rows[0].keys()) == [
        "order",
        "label",
        "unit",
        "2025-05-31",
        "2024-05-31",
    ]
    assert rows[0] == {
        "order": 1,
        "label": "Cash",
        "unit": "USD",
        "2025-05-31": 10,
        "2024-05-31": 9,
    }
    assert [r["order"] for r in rows] == [1, 2]


def test_equity_statement_passes_through_wide():
    df = pd.DataFrame(
        [
            {
                "label": "Beginning balances",
                "Total": 100,
                "Common stock": 80,
                "tag": "x",
            },
            {"label": "Net income", "Total": 50, "Common stock": 0, "tag": "y"},
        ]
    )
    rows = _run(df)
    assert list(rows[0].keys()) == ["order", "label", "Total", "Common stock"]
    assert rows[0] == {
        "order": 1,
        "label": "Beginning balances",
        "Total": 100,
        "Common stock": 80,
    }
    assert [r["order"] for r in rows] == [1, 2]


def test_no_url_returns_empty():
    with patch(
        "openbb_sec.models.sec_financials.resolve_section_url",
        AsyncMock(return_value=""),
    ):
        assert asyncio.run(get_as_filed_widget_rows("ORCL", "balance")) == []


def test_empty_or_missing_statement_returns_empty():
    assert _run(pd.DataFrame()) == []
    assert _run(None) == []


def test_all_columns_dropped_returns_empty():
    df = pd.DataFrame(
        [
            {
                "tag": "us-gaap_Cash",
                "value": 10,
                "period_ending": "2025-05-31",
                "context_ref": "c1",
            }
        ]
    )
    assert _run(df) == []


def test_pivot_branch_preserves_dash_values():
    df = pd.DataFrame(
        [
            {
                "order": 1,
                "label": "Cash",
                "unit": "USD",
                "period_ending": "2025-05-31",
                "value": 10,
            },
            {
                "order": 2,
                "label": "AR",
                "unit": "USD",
                "period_ending": "2024-05-31",
                "value": 7,
            },
        ]
    )
    rows = _run(df)
    assert rows[0]["2024-05-31"] == "--"
    assert rows[1]["2025-05-31"] == "--"
