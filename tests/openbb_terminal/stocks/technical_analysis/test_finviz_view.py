# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.technical_analysis import finviz_view

# pylint: disable=E1101


@pytest.mark.vcr
def test_view():
    finviz_view.view(symbol="PM")
