# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.options import calculator_view


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "sell",
    [True, False],
)
def test_view_calculator(mocker, sell):
    # MOCK CHARTS
    mocker.patch.object(target=calculator_view.gtff, attribute="USE_ION", new=True)
    mocker.patch(target="gamestonk_terminal.stocks.backtesting.bt_view.plt.ion")
    mocker.patch(target="gamestonk_terminal.stocks.backtesting.bt_view.plt.show")

    calculator_view.view_calculator(
        strike=10,
        premium=2,
        put=True,
        sell=sell,
    )
