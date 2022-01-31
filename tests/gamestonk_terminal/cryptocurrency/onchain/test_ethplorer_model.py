# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.cryptocurrency.onchain import ethplorer_model


@pytest.mark.vcr
@pytest.mark.parametrize(
    "func, kwargs",
    [
        (
            "get_token_decimals",
            dict(address="0x1f9840a85d5af5bf1d1762f925bdaddc4201f984"),
        ),
        (
            "get_address_info",
            dict(address="0x1f9840a85d5af5bf1d1762f925bdaddc4201f984"),
        ),
        ("get_top_tokens", dict()),
        (
            "get_top_token_holders",
            dict(address="0x1f9840a85d5af5bf1d1762f925bdaddc4201f984"),
        ),
        (
            "get_address_history",
            dict(address="0x1f9840a85d5af5bf1d1762f925bdaddc4201f984"),
        ),
        ("get_token_info", dict(address="0x1f9840a85d5af5bf1d1762f925bdaddc4201f984")),
        (
            "get_token_history",
            dict(address="0x1f9840a85d5af5bf1d1762f925bdaddc4201f984"),
        ),
        (
            "get_token_historical_price",
            dict(address="0x1f9840a85d5af5bf1d1762f925bdaddc4201f984"),
        ),
    ],
)
def test_call_func(func, kwargs, recorder):
    result = getattr(ethplorer_model, func)(**kwargs)

    if isinstance(result, pd.DataFrame) and "timestamp" in result.columns:
        result.drop(columns=["timestamp"], inplace=True)

    if isinstance(result, tuple):
        recorder.capture_list(result)
    else:
        recorder.capture(result)


@pytest.mark.vcr
def test_get_tx_info():
    df = ethplorer_model.get_tx_info(
        tx_hash="0x9dc7b43ad4288c624fdd236b2ecb9f2b81c93e706b2ffd1d19b112c1df7849e6",
    )

    assert isinstance(df, pd.DataFrame)
    assert not df.empty
