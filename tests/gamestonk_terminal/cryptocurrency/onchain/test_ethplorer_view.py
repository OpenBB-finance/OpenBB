# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.cryptocurrency.onchain import ethplorer_view


@pytest.mark.vcr
@pytest.mark.parametrize(
    "func, kwargs",
    [
        (
            "display_address_info",
            dict(address="0x1f9840a85d5af5bf1d1762f925bdaddc4201f984"),
        ),
        ("display_top_tokens", dict()),
        (
            "display_top_token_holders",
            dict(address="0x1f9840a85d5af5bf1d1762f925bdaddc4201f984"),
        ),
        (
            "display_address_history",
            dict(address="0x1f9840a85d5af5bf1d1762f925bdaddc4201f984"),
        ),
        (
            "display_token_info",
            dict(address="0x1f9840a85d5af5bf1d1762f925bdaddc4201f984"),
        ),
        (
            "display_tx_info",
            dict(
                tx_hash="0x9dc7b43ad4288c624fdd236b2ecb9f2b81c93e706b2ffd1d19b112c1df7849e6"
            ),
        ),
        (
            "display_token_history",
            dict(address="0x1f9840a85d5af5bf1d1762f925bdaddc4201f984"),
        ),
        (
            "display_token_historical_prices",
            dict(address="0x1f9840a85d5af5bf1d1762f925bdaddc4201f984"),
        ),
    ],
)
def test_call_func(func, kwargs, mocker):
    # MOCK EXPORT_DATA
    mocker.patch(
        target="gamestonk_terminal.cryptocurrency.onchain.ethplorer_view.export_data"
    )

    getattr(ethplorer_view, func)(**kwargs)
