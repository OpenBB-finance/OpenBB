# IMPORTATION STANDARD
import os

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.cryptocurrency.overview import overview_controller

# pylint: disable=E1101
# pylint: disable=W0603
# pylint: disable=E1111

GET_ALL_CONTRACT_PLATFORMS_DF = pd.DataFrame(
    data={
        "index": {
            0: 1,
            1: 2,
            2: 3,
            3: 4,
            4: 5,
            5: 6,
            6: 7,
            7: 8,
            8: 9,
            9: 10,
            10: 11,
            11: 12,
            12: 13,
            13: 14,
            14: 15,
            15: 16,
            16: 17,
            17: 18,
            18: 19,
            19: 20,
            20: 21,
            21: 22,
            22: 23,
            23: 24,
            24: 25,
            25: 26,
            26: 27,
            27: 28,
            28: 29,
            29: 30,
            30: 31,
            31: 32,
            32: 33,
            33: 34,
            34: 35,
            35: 36,
            36: 37,
        },
        "platform_id": {
            0: "btc-bitcoin",
            1: "eos-eos",
            2: "eth-ethereum",
            3: "xrp-xrp",
            4: "bch-bitcoin-cash",
            5: "xem-nem",
            6: "neo-neo",
            7: "xlm-stellar",
            8: "etc-ethereum-classic",
            9: "qtum-qtum",
            10: "zec-zcash",
            11: "vet-vechain",
            12: "bts-bitshares",
            13: "waves-waves",
            14: "nxt-nxt",
            15: "act-achain",
            16: "ubq-ubiq",
            17: "xcp-counterparty",
            18: "html-htmlcoin",
            19: "etp-metaverse-etp",
            20: "signa-signa",
            21: "omni-omni",
            22: "trx-tron",
            23: "bnb-binance-coin",
            24: "ardr-ardor",
            25: "ht-huobi-token",
            26: "blvr-believer",
            27: "cake-pancakeswap",
            28: "fsxu-flashx-ultra",
            29: "chik-chickenkebab-finance",
            30: "jgn-juggernaut7492",
            31: "crx-cryptex",
            32: "whirl-whirl-finance",
            33: "eubi-eubi-token",
            34: "swam-swapmatic-token",
            35: "shells-shells",
            36: "slx-solex-finance",
        },
    }
)


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "queue, expected",
    [
        (["load", "help"], ["help"]),
        (["quit", "help"], ["help"]),
    ],
)
def test_menu_with_queue(expected, mocker, queue):
    path_controller = "openbb_terminal.cryptocurrency.overview.overview_controller"

    # MOCK SWITCH
    mocker.patch(
        target=f"{path_controller}.OverviewController.switch",
        return_value=["quit"],
    )
    result_menu = overview_controller.OverviewController(queue=queue).menu()

    assert result_menu == expected


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "mock_input",
    ["help", "homee help", "home help", "mock"],
)
def test_menu_without_queue_sys_exit(mock_input, mocker):
    path_controller = "openbb_terminal.cryptocurrency.overview.overview_controller"

    # DISABLE AUTO-COMPLETION
    mocker.patch.object(
        target=overview_controller.obbff,
        attribute="USE_PROMPT_TOOLKIT",
        new=False,
    )
    mocker.patch(
        target=f"{path_controller}.session",
        return_value=None,
    )

    # MOCK USER INPUT
    mocker.patch("builtins.input", return_value=mock_input)

    # MOCK SWITCH
    class SystemExitSideEffect:
        def __init__(self):
            self.first_call = True

        def __call__(self, *args, **kwargs):
            if self.first_call:
                self.first_call = False
                raise SystemExit()
            return ["quit"]

    mock_switch = mocker.Mock(side_effect=SystemExitSideEffect())
    mocker.patch(
        target=f"{path_controller}.OverviewController.switch",
        new=mock_switch,
    )

    result_menu = overview_controller.OverviewController(queue=None).menu()

    assert result_menu == ["help"]


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_print_help():
    controller = overview_controller.OverviewController(queue=None)
    controller.print_help()


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "an_input, expected_queue",
    [
        ("", []),
        ("/help", ["home", "help"]),
        ("help/help", ["help", "help"]),
        ("q", ["quit"]),
        ("h", []),
        (
            "r",
            ["quit", "quit", "reset", "crypto", "ov"],
        ),
    ],
)
def test_switch(an_input, expected_queue):
    controller = overview_controller.OverviewController(queue=None)
    queue = controller.switch(an_input=an_input)

    assert queue == expected_queue


@pytest.mark.vcr(record_mode="none")
def test_call_cls(mocker):
    mocker.patch("os.system")

    controller = overview_controller.OverviewController(queue=None)
    controller.call_cls([])

    assert controller.queue == []
    os.system.assert_called_once_with("cls||clear")


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "func, queue, expected_queue",
    [
        (
            "call_exit",
            [],
            ["quit", "quit", "quit"],
        ),
        ("call_exit", ["help"], ["quit", "quit", "quit", "help"]),
        ("call_home", [], ["quit", "quit"]),
        ("call_help", [], []),
        ("call_quit", [], ["quit"]),
        ("call_quit", ["help"], ["quit", "help"]),
        (
            "call_reset",
            [],
            ["quit", "quit", "reset", "crypto", "ov"],
        ),
        (
            "call_reset",
            ["help"],
            ["quit", "quit", "reset", "crypto", "ov", "help"],
        ),
    ],
)
def test_call_func_expect_queue(expected_queue, func, queue):
    controller = overview_controller.OverviewController(queue=queue)
    result = getattr(controller, func)([])

    assert result is None
    assert controller.queue == expected_queue


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "tested_func, other_args, mocked_func, called_args, called_kwargs",
    [
        (
            "call_cgglobal",
            [],
            "pycoingecko_view.display_global_market_info",
            [],
            dict(),
        ),
        (
            "call_cgdefi",
            [],
            "pycoingecko_view.display_global_defi_info",
            [],
            dict(),
        ),
        (
            "call_cgstables",
            [],
            "pycoingecko_view.display_stablecoins",
            [],
            dict(),
        ),
        (
            "call_cgexchanges",
            [],
            "pycoingecko_view.display_exchanges",
            [],
            dict(),
        ),
        (
            "call_cgexrates",
            [],
            "pycoingecko_view.display_exchange_rates",
            [],
            dict(),
        ),
        (
            "call_cr",
            [],
            "loanscan_view.display_crypto_rates",
            [],
            dict(),
        ),
        (
            "call_cgindexes",
            [],
            "pycoingecko_view.display_indexes",
            [],
            dict(),
        ),
        (
            "call_cgderivatives",
            [],
            "pycoingecko_view.display_derivatives",
            [],
            dict(),
        ),
        (
            "call_cgcategories",
            [],
            "pycoingecko_view.display_categories",
            [],
            dict(),
        ),
        (
            "call_cghold",
            [],
            "pycoingecko_view.display_holdings_overview",
            [],
            dict(),
        ),
        (
            "call_cpglobal",
            [],
            "coinpaprika_view.display_global_market",
            [],
            dict(),
        ),
        (
            "call_cpmarkets",
            [],
            "coinpaprika_view.display_all_coins_market_info",
            [],
            dict(),
        ),
        (
            "call_cpexmarkets",
            ["binance"],
            "coinpaprika_view.display_exchange_markets",
            [],
            dict(),
        ),
        (
            "call_cpinfo",
            [],
            "coinpaprika_view.display_all_coins_info",
            [],
            dict(),
        ),
        (
            "call_cpexchanges",
            [],
            "coinpaprika_view.display_all_exchanges",
            [],
            dict(),
        ),
        (
            "call_cpplatforms",
            [],
            "coinpaprika_view.display_all_platforms",
            [],
            dict(),
        ),
        (
            "call_cpcontracts",
            ["eth-ethereum"],
            "coinpaprika_view.display_contracts",
            [],
            dict(),
        ),
        (
            "call_cbpairs",
            [],
            "coinbase_view.display_trading_pairs",
            [],
            dict(),
        ),
        (
            "call_news",
            [],
            "cryptopanic_view.display_news",
            [],
            dict(),
        ),
        (
            "call_wf",
            [],
            "withdrawalfees_view.display_overall_withdrawal_fees",
            [],
            dict(),
        ),
        (
            "call_ewf",
            [],
            "withdrawalfees_view.display_overall_exchange_withdrawal_fees",
            [],
            dict(),
        ),
        (
            "call_btcrb",
            [],
            "display_btc_rainbow",
            [],
            dict(),
        ),
        (
            "call_altindex",
            [],
            "blockchaincenter_view.display_altcoin_index",
            [],
            dict(),
        ),
        (
            "call_ch",
            [],
            "rekt_view.display_crypto_hacks",
            [],
            dict(),
        ),
    ],
)
def test_call_func(
    tested_func, mocked_func, other_args, called_args, called_kwargs, mocker
):
    path_controller = "openbb_terminal.cryptocurrency.overview.overview_controller"

    # MOCK GET_ALL_CONTRACT_PLATFORMS
    mocker.patch(
        target=f"{path_controller}.get_all_contract_platforms",
        return_value=GET_ALL_CONTRACT_PLATFORMS_DF,
    )

    if mocked_func:
        mock = mocker.Mock()
        mocker.patch(
            target=f"{path_controller}.{mocked_func}",
            new=mock,
        )

        controller = overview_controller.OverviewController(queue=None)
        controller.address = "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984"
        controller.address_type = "token"

        getattr(controller, tested_func)(other_args)

        if called_args or called_kwargs:
            mock.assert_called_once_with(*called_args, **called_kwargs)
        else:
            mock.assert_called_once()
    else:
        controller = overview_controller.OverviewController(queue=None)
        controller.address = "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984"
        controller.address_type = "token"

        getattr(controller, tested_func)(other_args)
