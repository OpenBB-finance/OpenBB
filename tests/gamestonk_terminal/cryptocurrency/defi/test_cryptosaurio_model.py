# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.cryptocurrency.defi import cryptosaurio_model


@pytest.mark.vcr
@pytest.mark.parametrize(
    "address",
    [("terra13kc0x8kr3sq8226myf4nmanmn2mrk9s5s9wsnz")],
)
def test_get_anchor_data(address, recorder):
    df, _, _ = cryptosaurio_model.get_anchor_data(
        address=address,
    )
    recorder.capture(df)
