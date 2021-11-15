```
usage: active   [-a ASSET]
                [-s INITIAL_DATE]
                [-u END_DATE]
                [-i {1h, 24h, 10m, 1w, 1month}]
                [--export {csv,json,xlsx}] [-h]
```

Display active addresses on a certain blockchain over time [Source: https://glassnode.org]

The number of unique addresses that were active either as a sender or receiver. Only addresses that were active in successful transactions are counted.

Supported assets: BTC, ETH, LTC, AAVE, ABT, AMPL, ANT, ARMOR, BADGER, BAL, BAND, BAT, BIX, BNT, BOND, BRD, BUSD, BZRX, CELR, CHSB, CND, COMP, CREAM, CRO, CRV, CVC, CVP, DAI, DDX, DENT, DGX, DHT, DMG, DODO, DOUGH, DRGN, ELF, ENG, ENJ, EURS, FET, FTT, FUN, GNO, GUSD, HEGIC, HOT, HPT, HT, HUSD, INDEX, KCS, LAMB, LBA, LDO, LEO, LINK, LOOM, LRC, MANA, MATIC, MCB, MCO, MFT, MIR, MKR, MLN, MTA, MTL, MX, NDX, NEXO, NFTX, NMR, Nsure, OCEAN, OKB, OMG, PAX, PAY, PERP, PICKLE, PNK, PNT, POLY, POWR, PPT, QASH, QKC, QNT, RDN, REN, REP, RLC, ROOK, RPL, RSR, SAI, SAN, SNT, SNX, STAKE, STORJ, sUSD, SUSHI, TEL, TOP, UBT, UMA, UNI, USDC, USDK, USDT, UTK, VERI, WaBi, WAX, WBTC, WETH, wNMX, WTC, YAM, YFI, ZRX

```
optional arguments:
  -a ASSET                      Asset to search for active addresses (default: BTC)
  -s DATE --since DATE          Start date (default: 1 year before, e.g., 2020-10-22)
  -u DATE --until DATE          End date (default: current day, e.g., 2021-10-22)
  -i INTERV --interval INTERV   Interval frequency (default: 24h)
  --export {csv,json,xlsx}      Export dataframe data to csv,json,xlsx file (default: )
  -h, --help                    show this help message (default: False)
```
