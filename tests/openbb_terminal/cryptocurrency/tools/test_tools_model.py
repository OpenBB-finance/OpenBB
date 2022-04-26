# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.cryptocurrency.tools import tools_model


@pytest.mark.vcr
@pytest.mark.parametrize(
    "apr,compound_times",
    [(100, 12)],
)
def test_calculate_apy(apr, compound_times, recorder):
    df, _ = tools_model.calculate_apy(apr=apr, compounding_times=compound_times)
    recorder.capture(df)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "price_changeA,price_changeB,proportion,initial_pool_value", [(100, 200, 50, 1000)]
)
def test_calculate_il(
    price_changeA, price_changeB, proportion, initial_pool_value, recorder
):
    df, _ = tools_model.calculate_il(
        price_changeA=price_changeA,
        price_changeB=price_changeB,
        proportion=proportion,
        initial_pool_value=initial_pool_value,
    )
    recorder.capture(df)
