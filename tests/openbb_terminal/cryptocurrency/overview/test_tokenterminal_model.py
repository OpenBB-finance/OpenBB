import pytest
from pandas import Series

from openbb_terminal.cryptocurrency.overview import tokenterminal_model

TIMELINES = ["24h", "7d", "30d", "90d", "180d", "365d"]

CATEGORIES = [
    "Asset Management",
    "Blockchain",
    "DeFi",
    "Exchange",
    "Gaming",
    "Insurance",
    "Interoperability",
    "Lending",
    "NFT",
    "Other",
    "Prediction Market",
    "Stablecoin",
]

METRICS = [
    "twitter_followers",
    "gmv_annualized",
    "market_cap",
    "take_rate",
    "revenue",
    "revenue_protocol",
    "tvl",
    "pe",
    "pe_circulating",
    "ps",
    "ps_circulating",
]


def test_get_possible_timelines():
    timelines = tokenterminal_model.get_possible_timelines()

    assert isinstance(timelines, list)
    assert timelines == TIMELINES


def test_get_possible_categories():
    categories = tokenterminal_model.get_possible_categories()

    assert isinstance(categories, list)
    assert categories == CATEGORIES


def test_get_possible_metrics():
    metrics = tokenterminal_model.get_possible_metrics()

    assert isinstance(metrics, list)
    assert metrics == METRICS


@pytest.mark.skip(reason="Fix the function")
@pytest.mark.record_http
@pytest.mark.parametrize(
    "metric, category, timeline",
    [
        ("revenue", "", "24h"),
    ],
)
def test_get_fundamental_metrics(metric, category, timeline):
    series = tokenterminal_model.get_fundamental_metrics(
        metric=metric, category=category, timeline=timeline
    )

    assert isinstance(series, Series)
    assert not series.empty
