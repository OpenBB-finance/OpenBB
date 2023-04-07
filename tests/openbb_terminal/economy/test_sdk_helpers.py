"""Test economy SDK helpers."""

# IMPORTATION STANDARD
# IMPORTATION THIRDPARTY
import pytest
from pandas import DataFrame

# IMPORTATION INTERNAL
from openbb_terminal.economy.sdk_helpers import futures


@pytest.mark.record_http
@pytest.mark.parametrize(
    "source, future_type", [("WSJ", "Indices"), ("Finviz", "Metals")]
)
def test_futures(source, future_type):
    df = futures(source, future_type)

    assert isinstance(df, DataFrame)
    assert not df.empty
