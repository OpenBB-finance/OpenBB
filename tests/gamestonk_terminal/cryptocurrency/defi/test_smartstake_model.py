# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.cryptocurrency.defi import smartstake_model

LUNA_CIR_SUPPLY_CHANGE = "lunaSupplyChallengeStats"


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_query_parameters": [
            ("token", "MOCK_TOKEN"),
            ("key", "MOCK_API_KEY"),
        ]
    }


# Skipping as there's no a way to specify the input date
@pytest.mark.skip
@pytest.mark.vcr
@pytest.mark.parametrize(
    "days",
    [30, 60, 90],
)
def test_get_luna_supply_stats(days, recorder):
    df = smartstake_model.get_luna_supply_stats(LUNA_CIR_SUPPLY_CHANGE, days)
    recorder.capture(df)
