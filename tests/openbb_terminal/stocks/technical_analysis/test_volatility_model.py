# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.common.technical_analysis import volatility_model

# pylint: disable=W0621
# pylint: disable=W0613

MODELS = volatility_model.VOLATILITY_MODELS
MOCK_DATA = pd.read_csv(
    "tests/openbb_terminal/stocks/technical_analysis/csv/test_volatility_model/test_cones_df.csv",
    index_col=0,
)

model = MODELS[0]
lower_q = 0.05
upper_q = 0.95
is_crypto: bool = False


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "model, lower_q, upper_q, is_crypto",
    [
        (MODELS[0], 0.05, 0.95, False),
        (MODELS[1], 0.05, 0.95, False),
        (MODELS[2], 0.05, 0.95, False),
        (MODELS[3], 0.05, 0.95, False),
        (MODELS[4], 0.05, 0.95, False),
        (MODELS[3], 0.10, 0.90, True),
        (MODELS[2], 15, 85, True),
    ],
)
def test_cones(recorder, model, lower_q, upper_q, is_crypto):
    result = volatility_model.cones(
        data=MOCK_DATA, upper_q=upper_q, lower_q=lower_q, is_crypto=is_crypto
    )
    recorder.capture(result)
