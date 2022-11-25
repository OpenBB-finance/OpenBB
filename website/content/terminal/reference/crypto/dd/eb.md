---
title: eb
description: OpenBB Terminal Function
---

# eb

Display active blockchain addresses over time [Source: https://glassnode.org] Note that free api keys only allow fetching data with a 1y lag

### Usage

```python
eb [-p] [-e {aggregated,binance,bittrex,coinex,gate.io,gemini,huobi,kucoin,poloniex,bibox,bigone,bitfinex,hitbtc,kraken,okex,bithumb,zb.com,cobinhood,bitmex,bitstamp,coinbase,coincheck,luno}] [-s SINCE] [-u UNTIL]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| percentage | Show percentage instead of stacked value. Default: False | False | True | None |
| exchange | Exchange to check change. Default: aggregated | aggregated | True | aggregated, binance, bittrex, coinex, gate.io, gemini, huobi, kucoin, poloniex, bibox, bigone, bitfinex, hitbtc, kraken, okex, bithumb, zb.com, cobinhood, bitmex, bitstamp, coinbase, coincheck, luno |
| since | Initial date. Default: 2 years ago | 2020-11-25 | True | None |
| until | Final date. Default: 1 year ago | 2021-11-23 | True | None |

![eb](https://user-images.githubusercontent.com/46355364/154060160-3102de99-bed7-4e3b-bc98-81c684eefcb0.png)

---
