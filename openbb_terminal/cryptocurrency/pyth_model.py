import logging
from typing import Tuple

from pythclient.pythaccounts import PythPriceAccount, PythPriceStatus
from pythclient.solana import (
    SOLANA_DEVNET_HTTP_ENDPOINT,
    SOLANA_DEVNET_WS_ENDPOINT,
    SolanaClient,
    SolanaPublicKey,
)

logger = logging.getLogger(__name__)

ASSETS = {
    "AAVE-USD": {"feedID": "FT7Cup6ZiFDF14uhFD3kYS3URMCf2RZ4iwfNEVUgndHW"},
    "ADA-USD": {"feedID": "8oGTURNmSQkrBS1AQ5NjB2p8qY34UVmMA9ojrw8vnHus"},
    "ALGO-USD": {"feedID": "c1A946dY5NHuVda77C8XXtXytyR3wK1SCP3eA9VRfC3"},
    "ANC-USD": {"feedID": "5Si2Pdm7B87ojYvkegg7ct8Y446RHJyEjeREAyZEZcAV"},
    "APE-USD": {"feedID": "EfnLcrwxCgwALc5vXr4cwPZMVcmotZAuqmHa8afG8zJe"},
    "ATLAS-USD": {"feedID": "Dzs6SE1cssUqBpWCKzE4jeS5PrmRK1Fp2Kw1WMaDCiVR"},
    "ATOM-USD": {"feedID": "7YAze8qFUMkBnyLVdKT4TFUUFui99EwS5gfRArMcrvFk"},
    "AVAX-USD": {"feedID": "FVb5h1VmHPfVb1RfqZckchq18GxRv4iKt8T4eVTQAqdz"},
    "BCH-USD": {"feedID": "4EQrNZYk5KR1RnjyzbaaRbHsv8VqZWzSUtvx58wLsZbj"},
    "BETH-USD": {"feedID": "HyShqBUTtwAaCas9Dnib3ut6GmEDk9hTdKsrNfRffX8E"},
    "BNB-USD": {"feedID": "GwzBgrXb4PG59zjce24SF2b9JXbLEjJJTBkmytuEZj1b"},
    "BRZ-USD": {"feedID": "5g4XtpqLynP6YUSQwncw6CrdAEoy5a7QNDevgAgLsfyC"},
    "BTC-USD": {"feedID": "HovQMDrbAgAYPCmHVSrezcSmkMtXSSUsLDFANExrZh2J"},
    "BUSD-USD": {"feedID": "TRrB75VTpiojCy99S5BHmYkjARgtfBqZKk5JbeouUkV"},
    "C98-USD": {"feedID": "Dxp7vob2NTGhmodyWyeEkqtNEpSfvSMoGKMYjmaY6pg1"},
    "COPE-USD": {"feedID": "BAXDJUXtz6P5ARhHH1aPwgv4WENzHwzyhmLYK4daFwiM"},
    "CUSD-USD": {"feedID": "DDwzo3aAjgYk8Vn8D3Zbxo62rTmBVdJv1WjaKQseiHKk"},
    "DOGE-USD": {"feedID": "4L6YhY8VvUgmqG5MvJkUJATtzB2rFqdrJwQCmFLv4Jzy"},
    "DOT-USD": {"feedID": "4dqq5VBpN4EwYb7wyywjjfknvMKu7m78j9mKZRXTj462"},
    "ETH-USD": {"feedID": "EdVCmQ9FSPcVe5YySXDPCRmc8aDQLKJ9xvYBMZPie1Vw"},
    "FIDA-USD": {"feedID": "7teETxN9Y8VK6uJxsctHEwST75mKLLwPH1jaFdvTQCpD"},
    "FTM-USD": {"feedID": "BTwrLU4so1oJMViWA3BTzh8YmFwiLZ6CL4U3JryG7Q5S"},
    "FTT-USD": {"feedID": "6vivTRs5ZPeeXbjo7dfburfaYDWoXjBtdtuYgQRuGfu"},
    "GMT-USD": {"feedID": "EZy99wkoqohyyNxT1QCwW3epQtMQ1Dfqx4sXKqkHiSox"},
    "GOFX-USD": {"feedID": "A9r7BHsXJQ2w9B7cdJV8BkfRoBWkxRichVGm72vVS1s5"},
    "HXRO-USD": {"feedID": "6VrSw4Vxg5zs9shfdCxLqfUy2qSD3NCS9AsdBQUgbjnt"},
    "INJ-USD": {"feedID": "44uRsNnT35kjkscSu59MxRr9CfkLZWf6gny8bWqUbVxE"},
    "JET-USD": {"feedID": "3JnVPNY878pRH6TQ9f4wuwfNqGh6okyshmqmKsyvewMs"},
    "LTC-USD": {"feedID": "BLArYBCUYhdWiY8PCUTpvFE21iaJq85dvxLk9bYMobcU"},
    "LUNA-USD": {"feedID": "7xzCBiE2d9UwV9CYLV9vrbJPipJzMEaycPBoZg2LjhUf"},
    "LUNC-USD": {"feedID": "8PugCXTAHLM9kfLSQWe2njE5pzAgUdpPk3Nx5zSm7BD3"},
    "MATIC-USD": {"feedID": "FBirwuDFuRAu4iSGc7RGxN5koHB7EJM1wbCmyPuQoGur"},
    "MER-USD": {"feedID": "6Z3ejn8DCWQFBuAcw29d3A5jgahEpmycn7YDMX7yRNrn"},
    "MIR-USD": {"feedID": "4BDvhA5emySfqyyTHPHofTJqRw1cwDabK1yiEshetPv9"},
    "MNGO-USD": {"feedID": "DCNw5mwZgjfTcoNsSZWUiXqU61ushNvr3JRQJRi1Nf95"},
    "MSOL-USD": {"feedID": "9a6RNx3tCu1TSs6TBSfV2XRXEPEZXQ6WB7jRojZRvyeZ"},
    "NEAR-USD": {"feedID": "3gnSbT7bhoTdGkFVZc1dW1PvjreWzpUNUD5ppXwv1N59"},
    "ONE-USD": {"feedID": "BScN1mER6QJ2nFKpnP4PcqffQp97NXAvzAbVPjLKyRaF"},
    "ORCA-USD": {"feedID": "A1WttWF7X3Rg6ZRpB2YQUFHCRh1kiXV8sKKLV3S9neJV"},
    "PAI-USD": {"feedID": "8EjmYPrH9oHxLqk2oFG1qwY6ert7M9cv5WpXyWHxKiMb"},
    "PORT-USD": {"feedID": "33ugpDWbC2mLrYSQvu1BHfykR8bt3MVc4S3YuuXMVRH3"},
    "RAY-USD": {"feedID": "EhgAdTrgxi4ZoVZLQx1n93vULucPpiFi2BQtz9RJr1y6"},
    "SBR-USD": {"feedID": "4WSN3XDSTfBX9A1YXGg8HJ7n2GtWMDNbtz1ab6aGGXfG"},
    "SCNSOL-USD": {"feedID": "HoDAYYYhFvCNQNFPui51H8qvpcdz6KuVtq77ZGtHND2T"},
    "SLND-USD": {"feedID": "FtwKARNAnZK2Nx1W4KVXzbyDzuRJqmApHRBtQpZ49HDv"},
    "SNY-USD": {"feedID": "DEmEX28EgrdQEBwNXdfMsDoJWZXCHRS5pbgmJiTkjCRH"},
    "SOL-USD": {"feedID": "J83w4HKfqxwcq3BEMMkPFSppX3gqekLyLJBexebFVkix"},
    "SRM-USD": {"feedID": "992moaMQKs32GKZ9dxi8keyM2bUmbrwBZpK4p2K6X5Vs"},
    "STEP-USD": {"feedID": "DKjdYzkPEZLBsfRzUaCjze5jjgCYu5kFCB19wVa9sy6j"},
    "STSOL-USD": {"feedID": "2LwhbcswZekofMNRtDRMukZJNSRUiKYMFbqtBwqjDfke"},
    "TUSD-USD": {"feedID": "2sbXow64dSbktGM6gG9FpszwVu7GNhr6Qi2WHRCP9ULn"},
    "USDC-USD": {"feedID": "5SSkXsEKQepHHAewytPVwdej4epN1nxgLVM84L4KXgy7"},
    "USDT-USD": {"feedID": "38xoQ4oeJCBrcVvca2cGk7iV1dAfrmTR1kmhSCJQ8Jto"},
    "USTC-USD": {"feedID": "AUKjh1oVPZyudi3nzYSsdZxSjq42afUCvsdbKFc5CbD"},
    "VAI-USD": {"feedID": "Gvm85Pbjq4Tv7qyaS4y9ZMqCdY3nynGDBFYAu7mjPoGM"},
    "XVS-USD": {"feedID": "8Y4jhVcQvQZWjMarM855NMkVuua78FS8Uwy58TjcnUWs"},
    "ZBC-USD": {"feedID": "7myonvBWD5zfh6qfScRP5E4anEue4Bqnu8XS8cdtJTQx"},
}


async def get_price(symbol: str) -> Tuple[float, float, float]:
    """Returns price and confidence interval from pyth live feed. [Source: Pyth]

    Parameters
    ----------
    symbol : str
        Symbol of the asset to get price and confidence interval from

    Returns
    -------
    Tuple[float, float, float]
        Price of the asset,
        Confidence level,
        Previous price of the asset
    """

    account_key = SolanaPublicKey(ASSETS[symbol]["feedID"])
    solana_client = SolanaClient(
        endpoint=SOLANA_DEVNET_HTTP_ENDPOINT, ws_endpoint=SOLANA_DEVNET_WS_ENDPOINT
    )
    price: PythPriceAccount = PythPriceAccount(account_key, solana_client)

    await price.update()

    price_status = price.aggregate_price_status
    aggregate_price = -1
    confidence = -1
    if price_status == PythPriceStatus.TRADING:
        aggregate_price = price.aggregate_price
        previous_price = price.prev_price
        confidence = price.aggregate_price_confidence_interval

    await solana_client.close()
    return aggregate_price, confidence, previous_price
