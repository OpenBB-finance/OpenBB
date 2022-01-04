# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.options import chartexchange_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


@pytest.mark.vcr
def test_get_option_history(recorder):
    result_df = chartexchange_model.get_option_history(
        ticker="GME",
        date="2021-02-05",
        call=True,
        price="90",
    )

    recorder.capture(result_df)
