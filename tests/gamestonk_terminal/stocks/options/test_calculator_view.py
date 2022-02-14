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
    # MOCK VISUALIZE_OUTPUT
    mocker.patch(
        target="gamestonk_terminal.helper_classes.TerminalStyle.visualize_output"
    )

    calculator_view.view_calculator(
        strike=10,
        premium=2,
        put=True,
        sell=sell,
    )
