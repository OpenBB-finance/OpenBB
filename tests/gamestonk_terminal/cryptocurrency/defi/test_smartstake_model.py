# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.cryptocurrency.defi import smartstake_model

LUNA_CIR_SUPPLY_CHANGE = "lunaSupplyChallengeStats"


@pytest.mark.vcr
@pytest.mark.parametrize(
    "days",
    [30, 60, 90],
)
def test_get_luna_supply_stats(days, recorder):
    df = smartstake_model.get_luna_supply_stats(LUNA_CIR_SUPPLY_CHANGE, days)
    recorder.capture(df)
