# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.cryptocurrency.due_diligence import coinbase_view


@pytest.mark.vcr
@pytest.mark.parametrize(
    "func, kwargs",
    [
        ("display_order_book", dict(symbol="ETH-USDT")),
        ("display_trades", dict(symbol="ETH-USDT")),
        ("display_candles", dict(symbol="ETH-USDT")),
        ("display_stats", dict(symbol="ETH-USDT")),
    ],
)
def test_call_func(func, kwargs, mocker):
    # MOCK EXPORT_DATA
    mocker.patch(
        target="openbb_terminal.cryptocurrency.due_diligence.coinbase_view.plot_order_book"
    )
    # MOCK EXPORT_DATA
    mocker.patch(
        target="openbb_terminal.cryptocurrency.due_diligence.coinbase_view.export_data"
    )

    getattr(coinbase_view, func)(**kwargs)
