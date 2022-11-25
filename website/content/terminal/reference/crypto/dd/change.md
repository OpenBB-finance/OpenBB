---
title: change
description: OpenBB Terminal Function
---

# change

Display active blockchain addresses over time [Source: https://glassnode.org] Note that free api keys only allow fetching data with a 1y lag

### Usage

```python
change [-e {aggregated,binance,bittrex,coinex,gate.io,gemini,huobi,kucoin,poloniex,bibox,bigone,bitfinex,hitbtc,kraken,okex,bithumb,zb.com,cobinhood,bitmex,bitstamp,coinbase,coincheck,luno}] [-s SINCE] [-u UNTIL]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| exchange | Exchange to check change. Default: aggregated | aggregated | True | aggregated, binance, bittrex, coinex, gate.io, gemini, huobi, kucoin, poloniex, bibox, bigone, bitfinex, hitbtc, kraken, okex, bithumb, zb.com, cobinhood, bitmex, bitstamp, coinbase, coincheck, luno |
| since | Initial date. Default: 2 years ago | 2020-11-25 | True | None |
| until | Final date. Default: 1 year ago | 2021-11-23 | True | None |

![change](https://user-images.githubusercontent.com/46355364/154060004-c5367c72-d25b-48da-a316-35d8d6e5208e.png)

---
