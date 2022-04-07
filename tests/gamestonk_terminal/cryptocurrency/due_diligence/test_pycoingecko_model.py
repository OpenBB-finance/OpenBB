import pytest

from openbb_terminal.cryptocurrency.due_diligence import pycoingecko_model


@pytest.mark.skip
@pytest.mark.parametrize(
    "main_coin,vs",
    [("algorand", "bitcoin"), ("solana", "ethereum")],
)
def test_get_coin_potential_returns(main_coin, vs, recorder):
    df = pycoingecko_model.get_coin_potential_returns(main_coin=main_coin, vs=vs)
    recorder.capture(df)
