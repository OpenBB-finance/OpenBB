---
title: eb
description: The eb page provides information on how to display active blockchain
  addresses over time using different exchanges. It also includes details on parameters
  such as the initial and final dates for fetching data.
keywords:
- blockchain addresses
- data fetching
- api keys
- exchanges
- parameters
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto /dd/eb - Reference | OpenBB Terminal Docs" />

Display active blockchain addresses over time [Source: https://glassnode.org] Note that free api keys only allow fetching data with a 1y lag

### Usage

```python wordwrap
eb [-p] [-e {aggregated,binance,bittrex,coinex,gate.io,gemini,huobi,kucoin,poloniex,bibox,bigone,bitfinex,hitbtc,kraken,okex,bithumb,zb.com,cobinhood,bitmex,bitstamp,coinbase,coincheck,luno}] [-s SINCE] [-u UNTIL]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| percentage | -p  --pct | Show percentage instead of stacked value. Default: False | False | True | None |
| exchange | -e  --exchange | Exchange to check change. Default: aggregated | aggregated | True | aggregated, binance, bittrex, coinex, gate.io, gemini, huobi, kucoin, poloniex, bibox, bigone, bitfinex, hitbtc, kraken, okex, bithumb, zb.com, cobinhood, bitmex, bitstamp, coinbase, coincheck, luno |
| since | -s  --since | Initial date. Default: 2 years ago | 2021-11-21 | True | None |
| until | -u  --until | Final date. Default: 1 year ago | 2022-11-19 | True | None |

![eb](https://user-images.githubusercontent.com/46355364/154060160-3102de99-bed7-4e3b-bc98-81c684eefcb0.png)

---
