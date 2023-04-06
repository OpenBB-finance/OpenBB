# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.options import calculator_view


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "sell",
    [True, False],
)
def test_view_calculator(sell):
    calculator_view.view_calculator(
        strike=10,
        premium=2,
        put=True,
        sell=sell,
    )
