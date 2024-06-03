import pytest

from openbb_cramer.models.cramer import get_cramer_picks

def test_get_cramer_picks_with_valid_loopback():

    lookback = 10
    result = get_cramer_picks(lookback)
    assert bool(result)

def test_get_cramer_picks_with_invalid_loopback():

    lookback = 0
    result = get_cramer_picks(lookback)
    assert bool(result) is False


