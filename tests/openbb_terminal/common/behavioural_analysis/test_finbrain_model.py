# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.common.behavioural_analysis import finbrain_model


@pytest.mark.vcr
def test_get_sentiment(recorder):
    df = finbrain_model.get_sentiment(ticker="PM")
    recorder.capture(df)
