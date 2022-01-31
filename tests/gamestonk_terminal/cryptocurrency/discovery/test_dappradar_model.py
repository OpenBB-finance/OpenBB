# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.cryptocurrency.discovery import dappradar_model

# pylint: disable=protected-access


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


@pytest.mark.vcr
@pytest.mark.parametrize(
    "func, kwargs",
    [
        ("get_top_nfts", dict()),
        ("get_top_dexes", dict()),
        ("get_top_games", dict()),
        ("get_top_dapps", dict()),
    ],
)
def test_call_func(func, kwargs, recorder):
    result = getattr(dappradar_model, func)(**kwargs)

    recorder.capture(result)
