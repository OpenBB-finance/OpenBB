"""LoanScan Model"""
import argparse
import logging
from typing import Any, Dict

import pandas as pd

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import get_user_agent, log_and_raise, request

logger = logging.getLogger(__name__)

api_url = "https://api.loanscan.io"

PLATFORMS = [
    "MakerDao",
    "Compound",
    "Poloniex",
    "Bitfinex",
    "dYdX",
    "CompoundV2",
    "Linen",
    "Hodlonaut",
    "InstaDapp",
    "Zerion",
    "Argent",
    "DeFiSaver",
    "MakerDaoV2",
    "Ddex",
    "AaveStable",
    "AaveVariable",
    "YearnFinance",
    "BlockFi",
    "Nexo",
    "CryptoCom",
    "Soda",
    "Coinbase",
    "SaltLending",
    "Ledn",
    "Bincentive",
    "Inlock",
    "Bitwala",
    "Zipmex",
    "Vauld",
    "Delio",
    "Yield",
    "Vesper",
    "Reflexer",
    "SwissBorg",
    "MushroomsFinance",
    "ElementFi",
    "Maple",
    "CoinRabbit",
    "WirexXAccounts",
    "Youhodler",
    "YieldApp",
    "NotionalFinance",
    "IconFi",
]

CRYPTOS = [
    "ZRX",
    "BAT",
    "REP",
    "ETH",
    "SAI",
    "BTC",
    "XRP",
    "LTC",
    "EOS",
    "BCH",
    "XMR",
    "DOGE",
    "USDC",
    "USDT",
    "BSV",
    "NEO",
    "ETC",
    "OMG",
    "ZEC",
    "BTG",
    "SAN",
    "DAI",
    "UNI",
    "WBTC",
    "COMP",
    "LUNA",
    "UST",
    "BUSD",
    "KNC",
    "LEND",
    "LINK",
    "MANA",
    "MKR",
    "SNX",
    "SUSD",
    "TUSD",
    "eCRV-DAO",
    "HEGIC",
    "YFI",
    "1INCH",
    "CRV-IB",
    "CRV-HBTC",
    "BOOST",
    "CRV-sBTC",
    "CRV-renBTC",
    "CRV-sAave",
    "CRV-oBTC",
    "CRV-pBTC",
    "CRV-LUSD",
    "CRV-BBTC",
    "CRV-tBTC",
    "CRV-FRAX",
    "CRV-yBUSD",
    "CRV-COMP",
    "CRV-GUSD",
    "yUSD",
    "CRV-3pool",
    "CRV-TUSD",
    "CRV-BUSD",
    "CRV-DUSD",
    "CRV-UST",
    "CRV-mUSD",
    "sUSD",
    "CRV-sUSD",
    "CRV-LINK",
    "CRV-USDN",
    "CRV-USDP",
    "CRV-alUSD",
    "CRV-Aave",
    "CRV-HUSD",
    "CRV-EURS",
    "RAI",
    "CRV-triCrypto",
    "CRV-Pax",
    "CRV-USDT",
    "CRV-USDK",
    "CRV-RSV",
    "CRV-3Crypto",
    "GUSD",
    "PAX",
    "USD",
    "ILK",
    "BNB",
    "PAXG",
    "ADA",
    "FTT",
    "SOL",
    "SRM",
    "RAY",
    "XLM",
    "SUSHI",
    "CRV",
    "BAL",
    "AAVE",
    "MATIC",
    "GRT",
    "ENJ",
    "USDP",
    "IOST",
    "AMP",
    "PERP",
    "SHIB",
    "ALICE",
    "ALPHA",
    "ANKR",
    "ATA",
    "AVA",
    "AXS",
    "BAKE",
    "BAND",
    "BNT",
    "BTCST",
    "CELR",
    "CFX",
    "CHR",
    "COS",
    "COTI",
    "CTSI",
    "DUSK",
    "EGLD",
    "ELF",
    "FET",
    "FLOW",
    "FTM",
    "INJ",
    "IOTX",
    "MDX",
    "NEAR",
    "OCEAN",
    "ONT",
    "POLS",
    "REEF",
    "WRX",
    "XEC",
    "XTZ",
    "XVS",
    "ZIL",
    "DOT",
    "FIL",
    "TRX",
    "CAKE",
    "ADX",
    "FIRO",
    "SXP",
    "ATOM",
    "IOTA",
    "AKRO",
    "AUDIO",
    "BADGER",
    "CVC",
    "DENT",
    "DYDX",
    "FORTH",
    "GNO",
    "HOT",
    "LPT",
    "LRC",
    "NKN",
    "NMR",
    "NU",
    "OGN",
    "OXT",
    "POLY",
    "QNT",
    "RLC",
    "RSR",
    "SAND",
    "SKL",
    "STMX",
    "STORJ",
    "TRB",
    "UMA",
    "DPI",
    "VSP",
    "CHSB",
    "EURT",
    "GHST",
    "3CRV",
    "CRVRENWBTC",
    "MIR-UST UNI LP",
    "ALCX",
    "ALUSD",
    "USDP3CRV",
    "RENBTC",
    "YVECRV",
    "CVX",
    "USDTTRC20",
    "AUD",
    "HKD",
    "GBP",
    "EUR",
    "HUSD",
    "HT",
    "DASH",
    "EURS",
    "AVAX",
    "BTT",
    "GALA",
    "ILV",
    "APE",
]


@log_start_end(log=logger)
def get_rates(rate_type: str = "borrow") -> pd.DataFrame:
    """Returns crypto {borrow,supply} interest rates for cryptocurrencies across several platforms
    [Source: https://loanscan.io/]

    Parameters
    ----------
    rate_type : str
        Interest rate type: {borrow, supply}. Default: supply

    Returns
    -------
    pd.DataFrame
        crypto interest rates per platform
    """
    if rate_type not in ("supply", "borrow"):
        raise Exception("Rate type not supported. Supported rates: borrow, supply")

    response = request(
        f"{api_url}/v1/interest-rates",
        headers={"User-Agent": get_user_agent()},
    )
    if response.status_code != 200:
        raise Exception(f"Status code: {response.status_code}. Reason: {response.text}")

    data = response.json()
    cryptos: Dict[Any, Any] = {}
    for provider in data:
        provider_name = provider["provider"].lower()
        for crypto in provider[rate_type]:
            symbol = crypto["symbol"]
            if symbol not in cryptos:
                cryptos[symbol] = {}
            cryptos[symbol][provider_name] = crypto["rate"]
    df = pd.DataFrame(cryptos, columns=sorted(cryptos.keys()))
    for platform in PLATFORMS:
        if platform.lower() not in df.index:
            df = pd.concat(
                [df, pd.Series(name=platform.lower(), dtype="object")],
                axis=0,
                join="outer",
            )
    return df


def check_valid_coin(value) -> str:
    """Argparse type to check valid coins argument"""
    cryptos = value.split(",")
    cryptos_lowered = [x.lower() for x in CRYPTOS]
    for crypto in cryptos:
        if crypto.lower() not in cryptos_lowered:
            log_and_raise(
                argparse.ArgumentTypeError(
                    f"{crypto} is not supported. Options: {','.join(CRYPTOS)}"
                )
            )
    return value


def check_valid_platform(value) -> str:
    """Argparse type to check valid platform argument"""
    platforms = value.split(",")
    platforms_lowered = [x.lower() for x in PLATFORMS]
    for platform in platforms:
        if platform.lower() not in platforms_lowered:
            log_and_raise(
                argparse.ArgumentTypeError(
                    f"{platform} is not supported. Options: {','.join(PLATFORMS)}"
                )
            )
    return value
