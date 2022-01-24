# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.economy import wsj_model


@pytest.mark.vcr
@pytest.mark.parametrize(
    "func",
    [
        "us_indices",
        "market_overview",
        "top_commodities",
        "us_bonds",
        "global_bonds",
        "global_currencies",
    ],
)
def test_call_func(func, recorder):
    result_df = getattr(wsj_model, func)()

    recorder.capture(result_df)
