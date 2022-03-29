# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.cryptocurrency.defi import defirate_model


@pytest.mark.vcr
def test_get_funding_rates(recorder):
    df = defirate_model.get_funding_rates(current=True)
    recorder.capture(df)


@pytest.mark.vcr
def test_get_lending_rates(recorder):
    df = defirate_model.get_lending_rates(current=True)
    recorder.capture(df)


@pytest.mark.vcr
def test_get_borrow_rates(recorder):
    df = defirate_model.get_borrow_rates(current=True)
    recorder.capture(df)
