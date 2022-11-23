```
usage: eb       [-e EXCHANGE]
                [-p {True, False}]
                [-s INITIAL_DATE]
                [-u END_DATE]
                [-i {1h, 24h, 10m, 1w, 1month}]
                [--export {csv,json,xlsx}] [-h]
```

Display total amount of coins held on exchange addresses in units and percentage. [Source: https://glassnode.org]

Supported assets: BTC, ETH, LTC, AAVE, ABT, AMPL, ANT, ARMOR, BADGER, BAL, BAND, BAT, BIX, BNT, BOND, BRD, BUSD, BZRX, CELR, CHSB, CND, COMP, CREAM, CRO, CRV, CVC, CVP, DAI, DDX, DENT, DGX, DHT, DMG, DODO, DOUGH, DRGN, ELF, ENG, ENJ, EURS, FET, FTT, FUN, GNO, GUSD, HEGIC, HOT, HPT, HT, HUSD, INDEX, KCS, LAMB, LBA, LDO, LEO, LINK, LOOM, LRC, MANA, MATIC, MCB, MCO, MFT, MIR, MKR, MLN, MTA, MTL, MX, NDX, NEXO, NFTX, NMR, Nsure, OCEAN, OKB, OMG, PAX, PAY, PERP, PICKLE, PNK, PNT, POLY, POWR, PPT, QASH, QKC, QNT, RDN, REN, REP, RLC, ROOK, RPL, RSR, SAI, SAN, SNT, SNX, STAKE, STORJ, sUSD, SUSHI, TEL, TOP, UBT, UMA, UNI, USDC, USDK, USDT, UTK, VERI, WaBi, WAX, WBTC, WETH, wNMX, WTC, YAM, YFI, ZRX

Supported exchanges: aggregated, binance, bittrex, coinex, gate.io, gemini, huobi, kucoin, poloniex, bibox, bigone, bitfinex, hitbtc, kraken, okex, bithumb, zb.com, cobinhood, bitmex, bitstamp, coinbase, coincheck, luno

```
arguments:
  -e EXCHANGE                   Exchange to check (default: aggregated)
  -p {True, False}              Show percentage instead of stacked value (default: False)
  -s DATE --since DATE          Start date (default: 3 years before, e.g., 2018-10-22)
  -u DATE --until DATE          End date (default: 2 years before, e.g., 2019-10-22)
  -i INTERV --interval INTERV   Interval frequency (default: 24h)
  --export {csv,json,xlsx}      Export dataframe data to csv,json,xlsx file (default: )
  -h, --help                    show this help message (default: False)
```

![eb](https://user-images.githubusercontent.com/46355364/154060160-3102de99-bed7-4e3b-bc98-81c684eefcb0.png)
