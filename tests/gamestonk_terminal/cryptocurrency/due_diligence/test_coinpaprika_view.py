# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.cryptocurrency.due_diligence import coinpaprika_view


@pytest.mark.vcr
@pytest.mark.parametrize(
    "func, kwargs",
    [
        ("display_twitter", dict()),
        ("display_events", dict()),
        ("display_exchanges", dict()),
        ("display_markets", dict()),
        ("display_price_supply", dict()),
        ("display_basic", dict()),
    ],
)
def test_call_func(func, kwargs, mocker):
    # MOCK EXPORT_DATA
    mocker.patch(
        target="gamestonk_terminal.cryptocurrency.due_diligence.coinpaprika_view.export_data"
    )

    getattr(coinpaprika_view, func)(**kwargs)
