# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.options import calculator_model


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "kwargs",
    [
        dict(
            strike=10,
            premium=2,
            put=True,
            sell=True,
        ),
        dict(
            strike=10,
            premium=2,
            put=False,
            sell=True,
            x_min=1,
            x_max=20,
        ),
    ],
)
def test_pnl_calculator(kwargs, recorder):
    result_tuple = calculator_model.pnl_calculator(**kwargs)
    result_tuple = (
        pd.DataFrame(result_tuple[0]),
        pd.DataFrame(result_tuple[1]),
        result_tuple[2],
    )

    recorder.capture_list(result_tuple)
