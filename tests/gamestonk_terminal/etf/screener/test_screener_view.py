# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.etf.screener import screener_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


@pytest.mark.vcr()
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "preset,num_to_show,sortby,ascend",
    [
        ("etf_config", 5, "Assets", True),
        ("etf_config", 10, "Expense", False),
        ("etf_config", 7, "Volume", True),
    ],
)
def test_view_screener(preset, num_to_show, sortby, ascend, mocker):
    mocker.patch.object(
        target=screener_view.gtff, attribute="USE_TABULATE_DF", new=False
    )
    screener_view.view_screener(
        preset, num_to_show=num_to_show, sortby=sortby, ascend=ascend, export=""
    )
