# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.options import chartexchange_view
from gamestonk_terminal import helper_funcs


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


@pytest.mark.default_cassette("test_display_raw")
@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "tab",
    [True, False],
)
def test_display_raw(mocker, tab):
    # MOCK CHARTS
    mocker.patch.object(
        target=helper_funcs.gtff,
        attribute="USE_TABULATE_DF",
        new=tab,
    )

    # MOCK VISUALIZE_OUTPUT
    mocker.patch(
        target="gamestonk_terminal.helper_classes.TerminalStyle.visualize_output"
    )

    chartexchange_view.display_raw(
        export="",
        ticker="GME",
        date="2021-02-05",
        call=True,
        price="90",
    )
