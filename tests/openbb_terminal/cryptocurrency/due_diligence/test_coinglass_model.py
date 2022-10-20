# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.cryptocurrency.due_diligence import coinglass_model


@pytest.fixture(scope="module")
def vcr_config():
    return {"filter_headers": [("coinglassSecret", "TOKEN")]}


@pytest.mark.vcr
@pytest.mark.parametrize(
    "func, kwargs",
    [
        ("get_liquidations", dict(symbol="ETH")),
        ("get_funding_rate", dict(symbol="ETH")),
        ("get_open_interest_per_exchange", dict(symbol="ETH")),
    ],
)
def test_call_func(func, kwargs, recorder):
    result = getattr(coinglass_model, func)(**kwargs)

    if isinstance(result, tuple):
        recorder.capture_list(result)
    else:
        recorder.capture(result)
