import pytest

from gamestonk_terminal.cryptocurrency.overview import blockchaincenter_model

pytest.skip("skipping broken tests", allow_module_level=True)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "days,since,until",
    [
        (365, 1_601_596_800, 1_641_573_787),
        (90, 1_601_596_800, 1_641_573_787),
        (30, 1_601_596_800, 1_641_573_787),
    ],
)
def test_get_altcoin_index(days, since, until, recorder):
    df = blockchaincenter_model.get_altcoin_index(days, since, until)
    recorder.capture(df)
