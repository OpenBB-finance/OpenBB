# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.cryptocurrency.defi import graph_model


@pytest.mark.vcr(record_mode="none")
def test_query_graph_status_400(mocker):
    # MOCK GET
    attrs = {
        "status_code": 400,
    }
    mock_response = mocker.Mock(**attrs)
    mocker.patch(target="requests.post", new=mocker.Mock(return_value=mock_response))

    graph_model.query_graph(url="http://MOCK_URL", query="MOCK_QUERY")


@pytest.mark.vcr
@pytest.mark.parametrize(
    "func, kwargs",
    [
        ("get_uni_tokens", dict(skip=0, limit=5)),
        ("get_uniswap_stats", dict()),
        ("get_uni_pools_by_volume", dict()),
        ("get_last_uni_swaps", dict(limit=5)),
    ],
)
def test_call_func(func, kwargs):
    df = getattr(graph_model, func)(**kwargs)

    assert isinstance(df, pd.DataFrame)
    assert not df.empty


@pytest.mark.vcr(filter_post_data_parameters=[("query", "MOCK_QUERY")])
def test_get_uniswap_pool_recently_added():
    df = graph_model.get_uniswap_pool_recently_added(
        last_days=14, min_volume=100, min_liquidity=0, min_tx=100
    )

    assert isinstance(df, pd.DataFrame)
    assert not df.empty


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "func, kwargs",
    [
        ("get_uni_tokens", dict(skip=0, limit=5)),
        ("get_uniswap_stats", dict()),
        (
            "get_uniswap_pool_recently_added",
            dict(last_days=14, min_volume=100, min_liquidity=0, min_tx=100),
        ),
        ("get_uni_pools_by_volume", dict()),
        ("get_last_uni_swaps", dict(limit=5)),
    ],
)
def test_call_func_empty_df(func, kwargs, mocker):
    # MOCK QUERY_GRAPH
    mocker.patch(
        target="openbb_terminal.cryptocurrency.defi.graph_model.query_graph",
        return_value={},
    )

    df = getattr(graph_model, func)(**kwargs)

    assert isinstance(df, pd.DataFrame)
    assert df.empty
