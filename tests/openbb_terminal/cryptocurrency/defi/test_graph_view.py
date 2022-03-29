# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.cryptocurrency.defi import graph_view


@pytest.mark.vcr
@pytest.mark.parametrize(
    "func, kwargs",
    [
        ("display_uni_tokens", dict(skip=0, limit=5)),
        ("display_uni_stats", dict()),
        ("display_uni_pools", dict()),
        ("display_last_uni_swaps", dict(top=5)),
    ],
)
def test_call_func(func, kwargs, mocker):
    # MOCK EXPORT_DATA
    mocker.patch(target="openbb_terminal.cryptocurrency.defi.graph_view.export_data")

    getattr(graph_view, func)(**kwargs)


@pytest.mark.vcr(filter_post_data_parameters=[("query", "MOCK_QUERY")])
def test_display_recently_added(mocker):
    # MOCK EXPORT_DATA
    mocker.patch(target="openbb_terminal.cryptocurrency.defi.graph_view.export_data")

    graph_view.display_recently_added(
        top=10,
        days=7,
        min_volume=20,
        min_liquidity=0,
        min_tx=100,
    )
