# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.technical_analysis import finviz_view

# pylint: disable=E1101


@pytest.mark.vcr
def test_view(mocker):
    # MOCK VISUALIZE_OUTPUT
    mocker.patch(target="openbb_terminal.helper_classes.TerminalStyle.visualize_output")

    finviz_view.view(ticker="PM")
