# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.technical_analysis import finviz_model


@pytest.mark.vcr
def test_get_finviz_image():
    result = finviz_model.get_finviz_image(ticker="PM")
    assert isinstance(result, bytes)
