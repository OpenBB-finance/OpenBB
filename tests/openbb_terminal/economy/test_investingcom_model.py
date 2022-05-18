# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.economy import investingcom_model


# @pytest.mark.vcr
@pytest.mark.parametrize(
    "country",
    [
        "united states",
        "portugal",
        "spain",
        "germany",
    ],
)
def test_get_yieldcurve(country):
    result_df = investingcom_model.get_yieldcurve(country)

    assert isinstance(result_df, pd.DataFrame)
