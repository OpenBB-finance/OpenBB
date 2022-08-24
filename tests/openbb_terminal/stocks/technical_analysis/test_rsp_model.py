# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.technical_analysis import rsp_model


@pytest.mark.vcr
def test_get_rsp_image(recorder):
    result = rsp_model.get_rsp()
    for df in result:
        recorder.capture(df)
