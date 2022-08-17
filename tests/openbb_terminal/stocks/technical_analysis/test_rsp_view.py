# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.technical_analysis import rsp_view

# pylint: disable=E1101


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout()
@pytest.mark.parametrize(
    "ticker",
    [
        ("TSLA"),
        (""),
    ],
)
def test_view(mocker, ticker):
    # MOCK VISUALIZE_OUTPUT
    mocker.patch(target="openbb_terminal.helper_classes.TerminalStyle.visualize_output")
    rsp_view.display_rsp(ticker, tickers_show=True)
